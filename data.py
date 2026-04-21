import random
import time
import math


# basic
BASE_USERS = 4_300_000
BASE_LATENCY = 120
BASE_PACKET_LOSS = 0.5
BASE_THROTTLING = 0.08
BASE_SERVERS = 7000


def generate_users(t):
    """
    Simulate regular + noise + spike
    """
    # dienos pattern (sin banga)
    daily_cycle = 1 + 0.2 * math.sin(2 * math.pi * t / 1440)

    # random triukšmas
    noise = random.uniform(-0.05, 0.05)

    users = BASE_USERS * daily_cycle * (1 + noise)

    # spike event
    if random.random() < 0.02:
        users *= random.uniform(1.2, 1.8)

    return int(users)


def generate_latency(load_factor):
    noise = random.uniform(-10, 10)
    return BASE_LATENCY * load_factor + noise


def generate_packet_loss(load_factor):
    noise = random.uniform(0, 0.2)
    return max(0, BASE_PACKET_LOSS * load_factor + noise)


def generate_throttling(load_factor):
    noise = random.uniform(0, 0.02)
    return max(0, BASE_THROTTLING * load_factor + noise)


def get_current_state():
    """
    Simuliuoja "live" sistemą
    """
    # laikas minutėmis (naudojam ciklams)
    t = int(time.time() / 60)

    users = generate_users(t)

    # load proxy (kuo daugiau userių → tuo didesnis load)
    load_factor = users / BASE_USERS

    latency = generate_latency(load_factor)
    packet_loss = generate_packet_loss(load_factor)
    throttling = generate_throttling(load_factor)

    new_connections = int(users * random.uniform(0.01, 0.02))

    return {
        "active_users": users,
        "new_connections_per_min": new_connections,
        "latency_p95_ms": round(latency, 2),
        "packet_loss_pct": round(packet_loss, 3),
        "throttled_users_pct": round(throttling, 4),
        "current_servers": BASE_SERVERS,
    }
