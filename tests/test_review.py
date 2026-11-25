import unittest

from sorvelune import review


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.packet = {"schema": "review-input.v1", "observations": [
            {"id": "revaskel-1", "result": "clear"}, {"id": "mandoryve-1", "result": "unknown"}],
            "relations": [{"undetermined": ["revaskel-1", "mandoryve-1"]}]}

    def test_review_keeps_unknown_and_temporal_context(self):
        queue = review(self.packet, 2, 5)["queue"]
        self.assertEqual(queue[0]["result"], "unknown")
        self.assertEqual(queue[0]["context"][0]["relation"], "undetermined")
        self.assertTrue(all(row["inclusion_probability"] == 1 for row in queue))

    def test_invalid_budget_and_unknown_ref(self):
        with self.assertRaises(ValueError):
            review(self.packet, 3, 5)
        self.packet["relations"] = [{"before": "other", "after": "revaskel-1"}]
        with self.assertRaises(ValueError):
            review(self.packet, 1, 5)
