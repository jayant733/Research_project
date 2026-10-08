"""Run a real Flower session with heterogeneous privacy tiers."""

import socket
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import flwr as fl
import torch

from packages.common.real_model import RealModel
from packages.flower.client_adapter import FlowerClientAdapter
from packages.flower.strategy_adapter import FlowerStrategyAdapter
from packages.privacy.fhe_engine import FHESession
from packages.ratc.data import make_loaders
from packages.ratc.fleet import ClientSpec, default_fleet
from packages.ratc.model import CompactMLP
from packages.ratc.participant import RATCClient
from packages.ratc.strategy import RATCStrategy

EventCallback = Callable[[Dict[str, Any]], None]


@dataclass
class RunConfig:
    """Controls one reproducible federated demonstration."""

    mode: str = "ratc"
    seed: int = 7
    num_rounds: int = 5
    epochs: int = 2
    learning_rate: float = 0.15
    clients: List[ClientSpec] = field(default_factory=default_fleet)
    secagg_secret: str = "ratc-demonstrator-client-secret"
    objective: str = "topsis"
    scenario: str = "none"
    budget_epsilon: Optional[float] = None
    latency_cap: Optional[float] = None
    forbid_iot_fhe: bool = False
    secagg_recovery: bool = False


def run_session(
    config: Optional[RunConfig] = None, on_event: Optional[EventCallback] = None
) -> List[Dict[str, Any]]:
    """Train the compact model and return the emitted round events."""
    selected = config or RunConfig()
    events: List[Dict[str, Any]] = []

    def emit(event: Dict[str, Any]) -> None:
        events.append(event)
        if on_event is not None:
            on_event(event)

    _validate_mode(selected.mode)
    _validate_choice("objective", selected.objective, _OBJECTIVES)
    _validate_choice("scenario", selected.scenario, _SCENARIOS)
    emit(
        {
            "type": "RUN_STARTED",
            "mode": selected.mode,
            "objective": selected.objective,
            "scenario": selected.scenario,
            "seed": selected.seed,
            "rounds": selected.num_rounds,
            "clients": [client.client_id for client in selected.clients],
            "source": "live",
        }
    )
    try:
        _execute(selected, emit)
    except Exception as exc:
        emit({"type": "RUN_FAILED", "error": str(exc), "source": "live"})
        raise
    emit(
        {
            "type": "RUN_FINISHED",
            "mode": selected.mode,
            "seed": selected.seed,
            "source": "live",
        }
    )
    return events


def _execute(config: RunConfig, emit: EventCallback) -> None:
    _allow_embedded_flower_server()
    torch.manual_seed(config.seed)
    initial = RealModel(CompactMLP()).get_weights()
    session = None if config.mode == "plain" else FHESession()
    strategy = RATCStrategy(
        initial_parameters=initial,
        clients=config.clients,
        mode=config.mode,
        seed=config.seed,
        epochs=config.epochs,
        learning_rate=config.learning_rate,
        fhe_session=session,
        on_event=emit,
        objective=config.objective,
        scenario=config.scenario,
        budget_epsilon=config.budget_epsilon,
        latency_cap=config.latency_cap,
        forbid_iot_fhe=config.forbid_iot_fhe,
        secagg_recovery=config.secagg_recovery,
    )
    port = _free_port()
    address = f"127.0.0.1:{port}"
    client_count = len(config.clients)
    flower_strategy = FlowerStrategyAdapter(
        generic_strategy=strategy,
        fraction_fit=1.0,
        fraction_evaluate=1.0,
        min_fit_clients=client_count,
        min_evaluate_clients=client_count,
        min_available_clients=client_count,
        accept_failures=False,
        on_fit_config_fn=strategy.config_for_round,
    )
    server_error: List[BaseException] = []
    server = threading.Thread(
        target=_serve,
        args=(address, config.num_rounds, flower_strategy, server_error),
        daemon=True,
    )
    server.start()
    _wait_for_port(port)
    public_bytes = None if session is None else session.public_bytes
    client_errors: List[BaseException] = []
    threads = [
        threading.Thread(
            target=_client_loop,
            args=(address, spec, config, public_bytes, client_errors),
            daemon=True,
        )
        for spec in config.clients
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=max(60, config.num_rounds * 90))
    server.join(timeout=30)
    if server_error:
        raise RuntimeError(str(server_error[0]))
    if client_errors:
        raise RuntimeError(str(client_errors[0]))
    if any(thread.is_alive() for thread in threads):
        raise TimeoutError("A federated client did not finish.")


def _allow_embedded_flower_server() -> None:
    """Flower registers process signals, which Python only allows on the main thread."""
    import flwr.compat.server.app as flower_server_app

    flower_server_app.register_signal_handlers = lambda *_args, **_kwargs: None


def _serve(
    address: str,
    num_rounds: int,
    strategy: FlowerStrategyAdapter,
    errors: List[BaseException],
) -> None:
    try:
        fl.server.start_server(
            server_address=address,
            config=fl.server.ServerConfig(num_rounds=num_rounds),
            strategy=strategy,
        )
    except BaseException as exc:
        errors.append(exc)


def _client_loop(
    address: str,
    spec: ClientSpec,
    config: RunConfig,
    public_fhe: bytes | None,
    errors: List[BaseException],
) -> None:
    try:
        torch.manual_seed(config.seed)
        train_data, test_data = make_loaders(spec, config.seed)
        model = RealModel(CompactMLP())
        client = RATCClient(
            model=model,
            spec=spec,
            train_data=train_data,
            test_data=test_data,
            seed=config.seed,
            secagg_secret=config.secagg_secret,
            public_fhe=public_fhe,
        )
        fl.client.start_numpy_client(
            server_address=address, client=FlowerClientAdapter(client)
        )
    except BaseException as exc:
        errors.append(exc)


_MODES = {"ratc", "plain", "random", "static", "reactive", "predictive", "bandit"}
_OBJECTIVES = {"topsis", "privacy", "latency", "upload"}
_SCENARIOS = {"none", "poison", "freerider", "telemetry", "dropout"}


def _validate_mode(mode: str) -> None:
    _validate_choice("run mode", mode, _MODES)


def _validate_choice(name: str, value: str, allowed: set[str]) -> None:
    if value not in allowed:
        choices = ", ".join(sorted(allowed))
        raise ValueError(f"Unknown {name} '{value}'. Expected one of: {choices}.")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
        handle.bind(("127.0.0.1", 0))
        return int(handle.getsockname()[1])


def _wait_for_port(port: int, timeout: float = 20.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
            handle.settimeout(0.2)
            if handle.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.1)
    raise TimeoutError(f"Flower server did not open port {port}.")
