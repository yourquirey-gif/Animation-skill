import unittest

from runtime.semantic_actions import compile_performance


class SemanticPerformanceTests(unittest.TestCase):
    def test_wave_generates_arm_and_forearm_tracks(self):
        tracks = compile_performance(
            [{"time_seconds": 0.2, "duration_seconds": 0.8, "action": "wave", "side": "right"}],
            fps=30,
            total_frames=90,
        )
        self.assertIn("upper_arm_right", tracks)
        self.assertIn("forearm_right", tracks)
        self.assertEqual(len(tracks["upper_arm_right"]), 3)
        self.assertEqual(tracks["upper_arm_right"][0]["time_seconds"], 0.2)
        self.assertEqual(tracks["upper_arm_right"][-1]["time_seconds"], 1.0)

    def test_sequential_actions_are_sorted_and_return_to_neutral(self):
        tracks = compile_performance(
            [
                {"time_seconds": 0.2, "duration_seconds": 0.5, "action": "nod"},
                {"time_seconds": 1.0, "duration_seconds": 0.5, "action": "look_left"},
            ],
            fps=30,
            total_frames=90,
        )
        self.assertEqual([x["time_seconds"] for x in tracks["head"]], [0.2, 0.425, 0.7, 1.0, 1.225, 1.5])
        self.assertEqual(tracks["head"][2]["rotation"], [0.0, 0.0, 0.0])

    def test_overlapping_actions_on_same_part_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Overlapping procedural actions"):
            compile_performance(
                [
                    {"time_seconds": 0.2, "duration_seconds": 0.8, "action": "nod"},
                    {"time_seconds": 0.5, "duration_seconds": 0.5, "action": "look_left"},
                ],
                fps=30,
                total_frames=90,
            )

    def test_unknown_action_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported procedural action"):
            compile_performance(
                [{"time_seconds": 0.2, "duration_seconds": 0.5, "action": "teleport"}],
                fps=30,
                total_frames=90,
            )

    def test_action_cannot_extend_past_shot(self):
        with self.assertRaisesRegex(ValueError, "outside the shot"):
            compile_performance(
                [{"time_seconds": 2.8, "duration_seconds": 0.5, "action": "wave"}],
                fps=30,
                total_frames=90,
            )


if __name__ == "__main__":
    unittest.main()
