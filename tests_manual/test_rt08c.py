import unittest


def decision_source(rules, ml, confidence, guarded, threshold=80.0):
    if guarded:
        return "rules", "disposal"

    if rules == "review" or not rules:
        return "human", None

    if not ml:
        return "rules", rules

    if rules == ml:
        return "agreement", rules

    if confidence >= threshold:
        return "ml", ml

    return "rules", rules


class TestRT08C(unittest.TestCase):

    def test_ml_above_threshold(self):
        source, treatment = decision_source(
            rules="recycle",
            ml="reuse",
            confidence=92.0,
            guarded=False,
        )
        self.assertEqual(source, "ml")
        self.assertEqual(treatment, "reuse")

    def test_rules_below_threshold(self):
        source, treatment = decision_source(
            rules="recycle",
            ml="reuse",
            confidence=65.0,
            guarded=False,
        )
        self.assertEqual(source, "rules")
        self.assertEqual(treatment, "recycle")

    def test_safety_guard(self):
        source, treatment = decision_source(
            rules="disposal",
            ml="reuse",
            confidence=99.0,
            guarded=True,
        )
        self.assertEqual(source, "rules")
        self.assertEqual(treatment, "disposal")


if __name__ == "__main__":
    unittest.main(verbosity=2)
