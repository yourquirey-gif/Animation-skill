import unittest
from runtime.align_visemes import cues_to_keyframes


class RhubarbCueTests(unittest.TestCase):
    def test_converts_cues_and_final_rest(self):
        events = cues_to_keyframes({"mouthCues": [
            {"start": 0.0, "end": 0.2, "value": "A"},
            {"start": 0.2, "end": 0.5, "value": "C"},
        ]})
        self.assertEqual([e["viseme"] for e in events], ["A", "C", "X"])
        self.assertEqual(events[-1]["time_seconds"], 0.5)

    def test_rejects_unknown_shape(self):
        with self.assertRaises(ValueError):
            cues_to_keyframes({"mouthCues": [{"start": 0, "end": 1, "value": "Z"}]})

    def test_rejects_overlapping_cues(self):
        with self.assertRaises(ValueError):
            cues_to_keyframes({"mouthCues": [
                {"start": 0, "end": 0.4, "value": "A"},
                {"start": 0.3, "end": 0.6, "value": "B"},
            ]})


if __name__ == "__main__":
    unittest.main()
