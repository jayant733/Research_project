"""Run one live RATC session and print the measured rounds."""

from packages.ratc.orchestrator import RunConfig, run_session


def main() -> None:
    events = run_session(RunConfig(mode="ratc", seed=7, num_rounds=3, epochs=1))
    for event in events:
        if event.get("type") != "ROUND_COMPLETED":
            continue
        metrics = event["metrics"]
        print(
            f"round={metrics['round']} accuracy={metrics['accuracy']:.4f} "
            f"loss={metrics['loss']:.4f} bytes={metrics['payload_bytes']} "
            f"epsilon={metrics['privacy_budget']:.3f}"
        )
        for client_id, client in sorted(metrics["clients"].items()):
            print(f"  {client_id}: {client['tier']} score={client['score']:.3f}")


if __name__ == "__main__":
    main()
