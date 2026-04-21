import numpy as np

BASELINE_USERS = 4_300_000
BASELINE_SERVERS = 9200
BASELINE_UTIL = 0.30

def compute_adjustment(throttling, latency, loss):
    lat_norm = max(0, (latency - 100) / 100)
    return 1 + throttling * 2 + lat_norm * 1.5 + loss * 2


def compute_util(users, servers, adj, load_multiplier):
    return (
        (users / BASELINE_USERS)
        * (BASELINE_SERVERS / servers)
        * BASELINE_UTIL
        * adj
        * load_multiplier
    )


def compute_ci(p, n, z=1.96):
    if n == 0:
        return (p, p)
    margin = z * np.sqrt((p * (1 - p)) / n)
    return max(0, p - margin), min(1, p + margin)


def simulate(server_count, state, sla_target, load_multiplier, iterations=100):
    violations = 0
    total = 0

    TARGET_UTIL = 0.65

    adj = compute_adjustment(
        state["throttled_users_pct"],
        state["latency_p95_ms"],
        state["packet_loss_pct"] / 100,
    )

    for _ in range(iterations):
        users = state["active_users"]

        for _ in range(60):
            users_step = int(users + np.random.normal(0, users * 0.02))

            if np.random.rand() < 0.01:
                users_step *= np.random.uniform(1.2, 2.0)

            util = compute_util(users_step, server_count, adj, load_multiplier)

            if util > TARGET_UTIL:
                violations += 1

            total += 1

    p = violations / total
    ci_low, ci_high = compute_ci(p, total)

    return {
        "violation": p,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "samples": total
    }


def find_optimal(state, sla_target, load_multiplier):
    results = []

    allowed_violation = 1 - sla_target

    for servers in range(3000, 10000, 250):
        res = simulate(servers, state, sla_target, load_multiplier)

        results.append({
            "servers": servers,
            **res
        })

    valid = [r for r in results if r["violation"] <= allowed_violation]

    optimal = min(valid, key=lambda x: x["servers"]) if valid else None

    return optimal, results
