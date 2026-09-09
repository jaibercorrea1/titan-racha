import math


def poisson_pmf(k: int, lam: float) -> float:
    return math.exp(-lam) * (lam ** k) / math.factorial(k)


def poisson_matrix(lambda_home: float, lambda_away: float, max_goals: int = 5):
    return [[poisson_pmf(i, lambda_home) * poisson_pmf(j, lambda_away) for j in range(max_goals + 1)] for i in range(max_goals + 1)]


def market_probs(matrix):
    n = len(matrix)
    home = sum(matrix[i][j] for i in range(n) for j in range(n) if i > j)
    draw = sum(matrix[i][j] for i in range(n) for j in range(n) if i == j)
    away = sum(matrix[i][j] for i in range(n) for j in range(n) if i < j)
    over25 = sum(matrix[i][j] for i in range(n) for j in range(n) if i + j >= 3)
    btts = sum(matrix[i][j] for i in range(n) for j in range(n) if i > 0 and j > 0)
    return {"home": home, "draw": draw, "away": away, "over25": over25, "under25": 1-over25, "btts": btts, "no_btts": 1-btts}


def outcome_probs(prediction, home=None, away=None):
    try:
        percent = prediction[0].get("predictions", {}).get("percent", {})
        vals = [float(str(percent.get(k, "0")).replace("%", "")) for k in ("home", "draw", "away")]
        s = sum(vals)
        if s > 0: return tuple(100*x/s for x in vals)
    except Exception:
        pass
    return 33.3, 33.4, 33.3
