import random
import unittest
from itertools import combinations
from statistics import mean

from sorvelune import Plan, select, simulate


class SamplingTests(unittest.TestCase):
    def test_equal_budget_and_inclusion(self):
        for strategy in ("top", "mixed", "random"):
            picks, _ = select(dict(enumerate(range(10))), Plan(4, strategy), random.Random(1))
            self.assertEqual(len({i for i, _ in picks}), 4)
        self.assertEqual([p for _, p in picks], [0.4] * 4)

    def test_population_estimate_refused_for_top_only(self):
        result = simulate(dict(size=20, budget=3, repeats=10, seed=1))
        self.assertIsNone(result["strategies"]["top"]["estimated_total_mean"])

    def test_census(self):
        for row in simulate(dict(size=6, budget=6, repeats=3, seed=33))["strategies"].values():
            self.assertEqual(row["mean_absolute_error"], 0)

    def test_exact_expectation_of_mixed_estimator(self):
        scores = {i: -i for i in range(5)}
        truth = {i: i in {0, 2, 4} for i in scores}
        estimates = []
        # Énumérer tous les tirages possibles de la strate aléatoire.
        class Draw:
            def sample(self, population, k):
                return self.draw
        sampler = Draw()
        for draw in combinations([1, 2, 3, 4], 2):
            sampler.draw = draw
            picks, covered = select(scores, Plan(3, "mixed"), sampler)
            self.assertTrue(covered)
            estimates.append(sum(truth[i] / p for i, p in picks))
        self.assertEqual(mean(estimates), sum(truth.values()))

    def test_invalid_budget_and_repeatability(self):
        config = dict(size=20, budget=3, repeats=8, seed=5)
        self.assertEqual(simulate(config), simulate(config))
        with self.assertRaises(ValueError):
            simulate(dict(config, budget=21))
