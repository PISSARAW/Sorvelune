"""Comparer trois plans de revue à budget égal sur une population simulée."""
import argparse
import json
import random
import re
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


def review(packet, budget, seed):
    if packet["schema"] != "review-input.v1":
        raise ValueError("version du rapport incompatible")
    weights = {"clear": 0, "unknown": 3, "missing_document": 2, "digest_mismatch": 2,
               "extra_access": 2, "missing_access": 2, "longer_access": 2, "shorter_access": 2}
    outcomes = {}
    for row in packet["observations"]:
        key = row["id"]
        if not re.fullmatch(r"(revaskel|mandoryve)-[1-9][0-9]*", key) or key in outcomes:
            raise ValueError("identifiant invalide ou dupliqué")
        if row["result"] not in weights:
            raise ValueError("résultat inconnu")
        outcomes[key] = row["result"]
    scores = {key: weights[value] for key, value in outcomes.items()}
    picks, coverage = select(scores, budget, "mixed", random.Random(seed))
    context = {key: [] for key in outcomes}
    seen = set()
    for pair in packet["relations"]:
        if "undetermined" in pair:
            a, b = pair["undetermined"]
            labels = ("undetermined", "undetermined")
        else:
            a, b = pair["before"], pair["after"]
            labels = ("before", "after")
        ids = frozenset((a, b))
        if len(ids) != 2 or a not in context or b not in context or ids in seen:
            raise ValueError("relation inconnue ou dupliquée")
        seen.add(ids)
        context[a].append({"relation": labels[0], "other": b})
        context[b].append({"relation": labels[1], "other": a})
    if len(seen) != len(outcomes) * (len(outcomes) - 1) // 2:
        raise ValueError("chronologie incomplète")
    return {"schema": "review-queue.v1", "strategy": "mixed", "population": len(scores),
            "budget": budget, "seed": seed, "full_sampling_coverage": coverage,
            "queue": [{"id": key, "result": outcomes[key], "inclusion_probability": probability,
                       "context": context[key]} for key, probability in picks]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--review", action="store_true", help="échantillonner les constats Calquory")
    parser.add_argument("--budget", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    try:
        data = json.loads(args.config.read_text())
        result = review(data, args.budget, args.seed) if args.review else simulate(data)
        print(json.dumps(result, indent=2))
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.exit(2, f"Configuration invalide ({exc})\n")
