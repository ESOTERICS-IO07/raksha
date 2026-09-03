"""Unit and Integration Tests for Behavior Intelligence Engine.

Validates contract conformance, score bounds, signal generation, feature extraction,
baseline calculations, and deterministic demo scenarios according to CONTRACTS.md.
"""

from __future__ import annotations

import os
import sys
import unittest
from datetime import datetime, timezone

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from apps.api.app.services.behavior import (
    BehaviorAnomalyModel,
    BehaviorBaselineCalculator,
    BehaviorEngine,
    BehaviorFeatureExtractor,
    BehaviorFeatures,
    BehaviorResult,
    BehaviorRuleEngine,
    BehaviorSignal,
    CustomerBehaviorProfile,
    TransactionContext,
    analyze_behavior,
)


class TestBehaviorEngine(unittest.TestCase):
    """Test suite for the Behavior Intelligence Engine."""

    def setUp(self) -> None:
        self.engine = BehaviorEngine()

        # Standard baseline profile for testing
        self.standard_profile = CustomerBehaviorProfile(
            user_id="U001",
            avg_amount=1500.0,
            std_amount=400.0,
            min_amount=100.0,
            max_amount=4000.0,
            usual_hours=[9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            frequent_recipients=["R001", "R002", "R003"],
            known_devices=["D001"],
            known_locations=["TN"],
            avg_daily_transactions=2.0,
            recent_transaction_count_1h=0,
            recent_transaction_count_24h=1,
        )

    def test_scenario_a_normal_transaction(self) -> None:
        """Scenario A: ₹850 to frequent merchant during daytime -> LOW score, no anomaly signals."""
        context = TransactionContext(
            transaction_id="TX001",
            user_id="U001",
            recipient_id="R001",
            amount=850.0,
            currency="INR",
            timestamp="2026-09-03T14:30:00+05:30",
            device_id="D001",
            location={"country": "IN", "region": "TN"},
            reason="Grocery purchase",
        )

        result = self.engine.analyze(context, self.standard_profile)

        self.assertIsInstance(result, BehaviorResult)
        self.assertIsInstance(result.score, int)
        self.assertLess(result.score, 30, f"Normal transaction score should be < 30, got {result.score}")
        self.assertEqual(result.signals, [])
        self.assertEqual(result.model_version, "behavior-v1")
        self.assertEqual(result.features["is_new_recipient"], False)
        self.assertGreaterEqual(result.features["recipient_frequency"], 1)

    def test_scenario_b_suspicious_payment(self) -> None:
        """Scenario B: ₹25,000 to new recipient at unusual hour -> MEDIUM/HIGH score, proper signals."""
        context = TransactionContext(
            transaction_id="TX002",
            user_id="U001",
            recipient_id="R999",
            amount=25000.0,
            currency="INR",
            timestamp="2026-09-03T23:45:00+05:30",
            device_id="D001",
            location={"country": "IN", "region": "TN"},
            reason="Personal transfer",
        )

        result = self.engine.analyze(context, self.standard_profile)

        self.assertIsInstance(result, BehaviorResult)
        self.assertGreaterEqual(result.score, 40, f"Suspicious transaction score should be >= 40, got {result.score}")
        self.assertIn(BehaviorSignal.AMOUNT_ABOVE_NORMAL.value, result.signals)
        self.assertIn(BehaviorSignal.UNUSUAL_TIME.value, result.signals)
        self.assertTrue(result.features["is_new_recipient"])
        self.assertGreater(result.features["amount_deviation"], 2.0)

    def test_scenario_c_social_engineering_coercion(self) -> None:
        """Scenario C: ₹50,000 at 3:30 AM to new recipient from new device -> HIGH/CRITICAL score (>= 80)."""
        context = {
            "transaction_id": "TX1001",
            "user_id": "U001",
            "recipient_id": "R014",
            "amount": 50000.0,
            "currency": "INR",
            "timestamp": "2026-09-03T03:30:00+05:30",
            "device_id": "D999",
            "location": {"country": "IN", "region": "MH"},
            "reason": "Bank officer told me to verify my account",
        }

        output = analyze_behavior(context, self.standard_profile)

        self.assertIsInstance(output, dict)
        self.assertIsInstance(output["score"], int)
        self.assertGreaterEqual(output["score"], 80, f"Social engineering score should be >= 80, got {output['score']}")
        self.assertLessEqual(output["score"], 100)

        signals = output["signals"]
        self.assertTrue(
            BehaviorSignal.AMOUNT_ABOVE_NORMAL.value in signals or BehaviorSignal.SPIKE_AMOUNT.value in signals,
            "Should detect amount anomaly",
        )
        self.assertIn(BehaviorSignal.UNUSUAL_TIME.value, signals)
        self.assertIn(BehaviorSignal.NEW_BEHAVIOR_PATTERN.value, signals)
        self.assertEqual(output["model_version"], "behavior-v1")

    def test_score_bounds_and_types(self) -> None:
        """Verify score is strictly an integer between 0 and 100 for extreme inputs."""
        extreme_cases = [
            {"amount": 0.0, "timestamp": "2026-09-03T12:00:00"},
            {"amount": 99999999.0, "timestamp": "2026-09-03T02:00:00"},
            {"amount": -500.0, "timestamp": None},
        ]

        for case in extreme_cases:
            ctx = TransactionContext(
                user_id="U001",
                recipient_id="R001",
                amount=case["amount"],
                timestamp=case["timestamp"],
            )
            result = self.engine.analyze(ctx, self.standard_profile)
            self.assertIsInstance(result.score, int)
            self.assertGreaterEqual(result.score, 0)
            self.assertLessEqual(result.score, 100)

    def test_cold_start_profile_fallback(self) -> None:
        """Verify graceful handling when customer profile is empty or None."""
        ctx = {
            "user_id": "NEW_USER_99",
            "recipient_id": "R001",
            "amount": 1200.0,
            "timestamp": "2026-09-03T12:00:00+05:30",
        }

        # None profile
        result_none = analyze_behavior(ctx, None)
        self.assertIsInstance(result_none["score"], int)
        self.assertIn("score", result_none)
        self.assertIn("signals", result_none)
        self.assertIn("features", result_none)
        self.assertEqual(result_none["model_version"], "behavior-v1")

        # Empty dict profile
        result_empty = analyze_behavior(ctx, {})
        self.assertIsInstance(result_empty["score"], int)
        self.assertEqual(result_empty["model_version"], "behavior-v1")

    def test_baseline_calculator_statistics(self) -> None:
        """Verify baseline calculator accurately computes statistics from historical transactions."""
        history = [
            {"amount": 1000.0, "timestamp": "2026-09-01T10:00:00+00:00", "recipient_id": "R1", "device_id": "D1"},
            {"amount": 2000.0, "timestamp": "2026-09-01T11:00:00+00:00", "recipient_id": "R1", "device_id": "D1"},
            {"amount": 3000.0, "timestamp": "2026-09-02T10:00:00+00:00", "recipient_id": "R2", "device_id": "D1"},
            {"amount": 2000.0, "timestamp": "2026-09-02T12:00:00+00:00", "recipient_id": "R1", "device_id": "D2"},
        ]

        profile = BehaviorBaselineCalculator.calculate_profile(
            user_id="U_TEST",
            transactions=history,
            reference_time="2026-09-02T12:30:00+00:00",
        )

        self.assertEqual(profile.user_id, "U_TEST")
        self.assertEqual(profile.avg_amount, 2000.0)
        self.assertAlmostEqual(profile.min_amount, 1000.0)
        self.assertAlmostEqual(profile.max_amount, 3000.0)
        self.assertIn(10, profile.usual_hours)
        self.assertIn(11, profile.usual_hours)
        self.assertIn("R1", profile.frequent_recipients)
        self.assertIn("D1", profile.known_devices)
        self.assertIn("D2", profile.known_devices)
        self.assertEqual(profile.recent_transaction_count_1h, 1)

    def test_unusual_location_and_device(self) -> None:
        """Verify new location and new device fire appropriate signals."""
        context = TransactionContext(
            user_id="U001",
            recipient_id="R001",
            amount=1200.0,
            timestamp="2026-09-03T12:00:00+05:30",
            device_id="D_UNKNOWN",
            location={"country": "IN", "region": "UNKNOWN_REGION"},
        )
        result = self.engine.analyze(context, self.standard_profile)
        self.assertIn(BehaviorSignal.NEW_DEVICE.value, result.signals)
        self.assertIn(BehaviorSignal.UNUSUAL_LOCATION.value, result.signals)
        self.assertTrue(result.features["is_new_device"])
        self.assertTrue(result.features["is_new_location"])

    def test_high_velocity_burst(self) -> None:
        """Verify rapid transaction velocity generates HIGH_TRANSACTION_VELOCITY signal."""
        burst_profile = self.standard_profile.model_copy(
            update={"recent_transaction_count_1h": 4, "recent_transaction_count_24h": 6}
        )
        context = TransactionContext(
            user_id="U001",
            recipient_id="R001",
            amount=1000.0,
            timestamp="2026-09-03T12:00:00+05:30",
            device_id="D001",
        )
        result = self.engine.analyze(context, burst_profile)
        self.assertIn(BehaviorSignal.HIGH_TRANSACTION_VELOCITY.value, result.signals)
        self.assertEqual(result.features["velocity_1h"], 4)

    def test_isolation_forest_determinism(self) -> None:
        """Verify that Isolation Forest with random_state=42 produces deterministic outputs."""
        model_1 = BehaviorAnomalyModel(random_state=42)
        model_2 = BehaviorAnomalyModel(random_state=42)

        test_vector = BehaviorFeatureExtractor.features_to_vector(
            BehaviorFeatures(amount_deviation=4.8, hour_deviation=2.1, recipient_frequency=0)
        )

        score_1, df_1 = model_1.predict_anomaly_score(test_vector)
        score_2, df_2 = model_2.predict_anomaly_score(test_vector)

        self.assertEqual(score_1, score_2)
        self.assertAlmostEqual(df_1, df_2, places=6)

    def test_pydantic_score_clamping(self) -> None:
        """Verify BehaviorResult clamps score within 0 to 100."""
        r1 = BehaviorResult(score=-10, signals=[], features={})
        self.assertEqual(r1.score, 0)

        r2 = BehaviorResult(score=150, signals=[], features={})
        self.assertEqual(r2.score, 100)

        r3 = BehaviorResult(score=87.6, signals=[], features={})
        self.assertEqual(r3.score, 88)

    def test_contract_keys_and_no_decisions(self) -> None:
        """Verify contract schema exact keys and verify NO friction decisions are present."""
        ctx = {
            "user_id": "U001",
            "recipient_id": "R001",
            "amount": 500.0,
            "timestamp": "2026-09-03T12:00:00+05:30",
        }
        res = analyze_behavior(ctx, self.standard_profile)

        # Must have exact 4 contract keys
        self.assertEqual(set(res.keys()), {"score", "signals", "features", "model_version"})

        # Forbidden decision keywords
        forbidden_keys = {"action", "decision", "allow", "hold", "verify", "strong_verify", "verdict"}
        for k in res.keys():
            self.assertNotIn(k.lower(), forbidden_keys)


if __name__ == "__main__":
    unittest.main()
