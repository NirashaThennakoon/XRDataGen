from __future__ import annotations
from datetime import timedelta, timezone
import numpy as np
from dateutil import parser
from ..utils.time import local_now, to_utc_iso

class PredictionService:
    def __init__(self, client, store, seq_len: int, horizon: int, local_tz: str):
        self.client = client
        self.store = store
        self.seq_len = seq_len
        self.horizon = horizon
        self.local_tz = local_tz

    def _fetch_series(self, hours: int = 6) -> list[dict]:
        now_local = local_now(self.local_tz)
        from_local = now_local - timedelta(hours=hours)
        events = self.client.events(
            from_iso=to_utc_iso(from_local),
            to_iso=to_utc_iso(now_local),
            metrics="co2",
        )
        return events

    def latest_series_for(self, deviceui: str, hours: int = 6):
        events = self._fetch_series(hours)
        filtered = [
            e for e in events
            if e.get("deveui") == deviceui and e.get("co2") is not None
        ]
        filtered.sort(key=lambda x: x["time"])
        return filtered

    def predict_next(self, sensor_id: str):
        # get time series
        series = self.latest_series_for(sensor_id, hours=6)
        co2 = np.array([float(e["co2"]) for e in series if "co2" in e], dtype=float)
        if len(co2) < self.seq_len:
            raise ValueError(f"Insufficient CO₂ data (need ≥{self.seq_len}, got {len(co2)})")

        # scale & window
        scaled = self.store.scale(co2.reshape(-1, 1))
        X = scaled[-self.seq_len:].reshape(1, self.seq_len, 1)

        model = self.store.model_for(sensor_id)
        preds_scaled = []
        t0 = local_now(self.local_tz)

        for _ in range(self.horizon):
            y = model.predict(X, verbose=0)    # shape (1,1)
            y_scalar = float(y[0][0])
            preds_scaled.append(y_scalar)
            X = np.roll(X, shift=-1, axis=1)
            X[0, -1, 0] = y_scalar

        preds = self.store.inverse_scale(np.array(preds_scaled).reshape(-1,1)).flatten()
        timestamps = [(t0 + timedelta(minutes=i+1)).isoformat() for i in range(self.horizon)]
        return [{"timestamp": t, "predicted_co2": int(round(v))} for t, v in zip(timestamps, preds)]
