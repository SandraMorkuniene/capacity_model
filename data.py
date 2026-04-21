def get_mock_state():
    return {
        "active_users": 4_300_000,
        "new_connections_per_min": 50000,
        "latency_p95_ms": 120,
        "packet_loss_pct": 0.5,
        "throttled_users_pct": 0.08,
        "current_servers": 9200,
    }
