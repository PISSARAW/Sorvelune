"""Comparer trois plans de revue à budget égal sur une population simulée."""
import argparse
import json
import random
from pathlib import Path
from statistics import fmean


def generate(size, seed):
    rng = random.Random(seed)
    scores = {i: rng.random() for i in range(size)}
    truth = {i: rng.random() < 0.04 + 0.7 * score ** 3 for i, score in scores.items()}
    return scores, truth


def select(scores, budget, strategy, rng):
    """Renvoie (id, probabilité d'inclusion) et la couverture du plan."""
    if not 1 <= budget <= len(scores):
        raise ValueError("budget hors population")
    ranked = sorted(scores, key=lambda i: (-scores[i], i))
    if strategy == "top":
        fixed = budget
    elif strategy == "random":
        fixed = 0
    elif strategy == "mixed":
        fixed = budget // 2
    else:
        raise ValueError("stratégie inconnue")
    tail = ranked[fixed:]
    k = budget - fixed
    picks = [(i, 1.0) for i in ranked[:fixed]]
    if k:
        inclusion = k / len(tail)
        picks.extend((i, inclusion) for i in rng.sample(tail, k))
    return picks, bool(k or not tail)


def evaluate(scores, truth, budget, repeats, seed):
    if not 1 <= repeats <= 10000:
        raise ValueError("nombre de répétitions hors limites")
    result = {}
    for strategy in ("top", "random", "mixed"):
        rng = random.Random(seed)
        found, estimates = [], []
        for _ in range(repeats):
            picks, covers_all = select(scores, budget, strategy, rng)
            found.append(sum(truth[i] for i, _ in picks))
            if covers_all:
                estimates.append(sum(truth[i] / inclusion for i, inclusion in picks))
        # La vérité complète intervient seulement pour évaluer le simulateur.
        total = sum(truth.values())
        result[strategy] = {
            "found_mean": fmean(found),
            "estimated_total_mean": fmean(estimates) if estimates else None,
            "mean_absolute_error": fmean(abs(x - total) for x in estimates) if estimates else None,
        }
    return {"population_size": len(scores), "review_budget": budget, "repeats": repeats,
            "simulated_true_total": sum(truth.values()), "strategies": result}


def simulate(config):
    for name in ("size", "budget", "repeats", "seed"):
        if type(config[name]) is not int:
            raise ValueError(f"{name} doit être entier")
    if not 1 <= config["size"] <= 100000:
        raise ValueError("taille hors limites")
    scores, truth = generate(config["size"], config["seed"])
    return evaluate(scores, truth, config["budget"], config["repeats"], config["seed"] + 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(simulate(json.loads(args.config.read_text())), indent=2))
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.exit(2, f"Configuration invalide ({exc})\n")
