"""Behavioral Baseline Calculation.

Computes and updates CustomerBehaviorProfile from historical transaction records.
Provides robust defaults for cold-start customers with limited or no prior transactions.
"""

from __future__ import annotations

import math
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Optional, Sequence, Union

from .schemas import CustomerBehaviorProfile


class BehaviorBaselineCalculator:
    """Calculates customer behavioral baseline profiles from historical transaction data."""

    DEFAULT_USUAL_HOURS = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    DEFAULT_AVG_AMOUNT = 1500.0
    DEFAULT_STD_AMOUNT = 800.0

    @classmethod
    def parse_datetime(cls, dt_val: Any) -> Optional[datetime]:
        """Safely parse various datetime representations."""
        if dt_val is None:
            return None
        if isinstance(dt_val, datetime):
            return dt_val
        if isinstance(dt_val, str):
            try:
                # Handle ISO format strings (with or without Z / offsets)
                clean_str = dt_val.replace("Z", "+00:00")
                return datetime.fromisoformat(clean_str)
            except Exception:
                return None
        return None

    @classmethod
    def calculate_profile(
        cls,
        user_id: str,
        transactions: Optional[Sequence[dict[str, Any]]] = None,
        reference_time: Optional[Union[datetime, str]] = None,
    ) -> CustomerBehaviorProfile:
        """Build a CustomerBehaviorProfile from a list of historical transaction dictionaries."""
        if not transactions:
            return cls.get_default_profile(user_id)

        amounts: list[float] = []
        hours: list[int] = []
        recipients: list[str] = []
        devices: list[str] = []
        locations: list[str] = []
        parsed_timestamps: list[datetime] = []

        ref_dt = cls.parse_datetime(reference_time) or datetime.now(timezone.utc)

        for tx in transactions:
            if not isinstance(tx, dict):
                continue

            # Amount
            try:
                amt = float(tx.get("amount", 0.0))
                if amt >= 0:
                    amounts.append(amt)
            except (ValueError, TypeError):
                pass

            # Timestamp & Hours
            tx_dt = cls.parse_datetime(tx.get("timestamp") or tx.get("created_at"))
            if tx_dt:
                hours.append(tx_dt.hour)
                parsed_timestamps.append(tx_dt)

            # Recipient
            rcp = tx.get("recipient_id")
            if rcp and isinstance(rcp, str):
                recipients.append(rcp)

            # Device
            dev = tx.get("device_id")
            if dev and isinstance(dev, str):
                devices.append(dev)

            # Location
            loc = tx.get("location")
            if isinstance(loc, dict):
                reg = loc.get("region") or loc.get("country")
                if reg and isinstance(reg, str):
                    locations.append(reg)
            elif isinstance(loc, str) and loc:
                locations.append(loc)

        if not amounts:
            return cls.get_default_profile(user_id)

        # Statistics
        n = len(amounts)
        avg_amt = sum(amounts) / n
        min_amt = min(amounts)
        max_amt = max(amounts)

        if n > 1:
            variance = sum((x - avg_amt) ** 2 for x in amounts) / (n - 1)
            std_amt = math.sqrt(variance)
        else:
            std_amt = max(avg_amt * 0.3, 100.0)

        # Ensure std is strictly non-zero
        std_amt = max(std_amt, max(avg_amt * 0.1, 10.0))

        # Usual Hours
        if hours:
            hour_counts = Counter(hours)
            # Hours with at least 10% occurrence or all distinct hours if few transactions
            threshold = max(1, n * 0.05)
            usual_hours = sorted([h for h, c in hour_counts.items() if c >= threshold])
            if not usual_hours:
                usual_hours = sorted(list(set(hours)))
        else:
            usual_hours = cls.DEFAULT_USUAL_HOURS.copy()

        # Frequent Recipients (sent to at least once in history)
        frequent_recipients = [rcp for rcp, _ in Counter(recipients).most_common(20)]

        # Known Devices and Locations
        known_devices = list(dict.fromkeys(devices))
        known_locations = list(dict.fromkeys(locations))

        # Velocity in last 1h and 24h
        count_1h = 0
        count_24h = 0
        if ref_dt.tzinfo is None:
            ref_dt = ref_dt.replace(tzinfo=timezone.utc)

        for ts in parsed_timestamps:
            curr_ts = ts if ts.tzinfo is not None else ts.replace(tzinfo=timezone.utc)
            delta_seconds = (ref_dt - curr_ts).total_seconds()
            if 0 <= delta_seconds <= 3600:
                count_1h += 1
            if 0 <= delta_seconds <= 86400:
                count_24h += 1

        # Daily transactions rate
        avg_daily = max(1.0, float(n) / 30.0)

        return CustomerBehaviorProfile(
            user_id=user_id,
            avg_amount=round(avg_amt, 2),
            std_amount=round(std_amt, 2),
            min_amount=round(min_amt, 2),
            max_amount=round(max_amt, 2),
            usual_hours=usual_hours,
            frequent_recipients=frequent_recipients,
            known_devices=known_devices,
            known_locations=known_locations,
            avg_daily_transactions=round(avg_daily, 2),
            recent_transaction_count_1h=count_1h,
            recent_transaction_count_24h=count_24h,
            historical_transactions=list(transactions) if transactions else None,
        )

    @classmethod
    def get_default_profile(cls, user_id: str) -> CustomerBehaviorProfile:
        """Cold-start baseline profile for a new user."""
        return CustomerBehaviorProfile(
            user_id=user_id,
            avg_amount=cls.DEFAULT_AVG_AMOUNT,
            std_amount=cls.DEFAULT_STD_AMOUNT,
            min_amount=100.0,
            max_amount=5000.0,
            usual_hours=cls.DEFAULT_USUAL_HOURS.copy(),
            frequent_recipients=[],
            known_devices=[],
            known_locations=[],
            avg_daily_transactions=1.0,
            recent_transaction_count_1h=0,
            recent_transaction_count_24h=0,
            historical_transactions=None,
        )
