from app.services.friction.service import FrictionService


def test_low_to_allow():
    result = FrictionService().decide("LOW")

    assert result.action == "ALLOW"


def test_medium_to_verify():
    result = FrictionService().decide("MEDIUM")

    assert result.action == "VERIFY"


def test_high_to_strong_verify():
    result = FrictionService().decide("HIGH")

    assert result.action == "STRONG_VERIFY"


def test_critical_to_hold():
    result = FrictionService().decide("CRITICAL")

    assert result.action == "HOLD"