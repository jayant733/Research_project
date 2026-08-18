import asyncio
import random
import time
from packages.scheduler.scheduler import ResourceAwareScheduler
from packages.telemetry.vectors import TelemetryVector
from packages.scheduler.types import ConstraintVector
from backend.services.state import state
from backend.websocket.manager import manager

scheduler = ResourceAwareScheduler()

async def simulate_round():
    # Only allow 50 rounds
    if state.current_round >= state.total_rounds:
        return
        
    state.current_round += 1
    
    # 1. Gather mock telemetry based on profiles for registered clients
    telemetry_map = {}
    constraint_map = {}
    for cid, cdata in state.clients.items():
        profile = cdata.get('profile', 'Desktop')
        if profile == 'Desktop':
            cpu = random.uniform(0.1, 0.4)
            mem = random.uniform(0.2, 0.5)
            bat = 1.0
        elif profile == 'Mobile':
            cpu = random.uniform(0.3, 0.8)
            mem = random.uniform(0.4, 0.8)
            bat = random.uniform(0.2, 0.9)
        else: # IoT
            cpu = random.uniform(0.6, 1.0)
            mem = random.uniform(0.7, 1.0)
            bat = random.uniform(0.1, 0.5)
            
        t_vec = TelemetryVector(cpu, mem, random.uniform(0.1, 1.0), bat, random.uniform(0.1, 0.5))
        telemetry_map[cid] = t_vec
        cdata['telemetry'] = t_vec.to_dict()
        constraint_map[cid] = ConstraintVector(data_sensitivity_score=random.uniform(0.2, 0.8))
        
    # 2. Evaluate Scheduler
    if telemetry_map:
        assignments = scheduler.evaluate(telemetry_map, constraint_map)
        for cid, tier in assignments.items():
            state.clients[cid]['tier'] = tier.name
            
    # Simulate processing time
    await asyncio.sleep(1.0)
            
    # 3. Mock training results
    accuracy = min(0.95, 0.5 + (state.current_round * 0.01) + random.uniform(-0.02, 0.02))
    loss = max(0.1, 1.5 - (state.current_round * 0.03) + random.uniform(-0.05, 0.05))
    latency = random.uniform(1.2, 2.5)
    
    round_metrics = {
        'round': state.current_round,
        'accuracy': accuracy,
        'loss': loss,
        'latency': latency,
        'privacy_budget': min(10.0, state.current_round * 0.15)
    }
    state.metrics_history.append(round_metrics)
    
    # 4. Broadcast
    await manager.broadcast({
        'type': 'ROUND_COMPLETED',
        'metrics': round_metrics,
        'clients': state.clients
    })
