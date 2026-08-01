from __future__ import annotations

import unittest

import pandas as pd

from modules.feature_engineering import engineer_features


class FeatureEngineeringTests(unittest.TestCase):
    def test_scenario_time_index_continues_from_historical_origin(self) -> None:
        historical_origin = pd.Timestamp("2024-01-01")
        scenario = pd.DataFrame(
            {"temperature": [10.0, 11.0]},
            index=pd.date_range("2024-01-11", periods=2, freq="D"),
        )

        features, _ = engineer_features(
            scenario,
            seasonal=False,
            rolling_windows=(),
            time_origin=historical_origin,
        )

        self.assertEqual(features["time_idx_days"].tolist(), [10.0, 11.0])

    def test_selected_rolling_windows_control_generated_features(self) -> None:
        frame = pd.DataFrame(
            {"temperature": [10.0, 12.0, 14.0]},
            index=pd.date_range("2024-01-01", periods=3, freq="D"),
        )

        features, _ = engineer_features(
            frame,
            seasonal=False,
            rolling_windows=(2, 3),
        )

        self.assertIn("temperature_rolling_2", features)
        self.assertIn("temperature_rolling_3", features)
        self.assertNotIn("temperature_rolling_7", features)
        self.assertEqual(
            features["temperature_rolling_2"].tolist(),
            [10.0, 11.0, 13.0],
        )


if __name__ == "__main__":
    unittest.main()
