import unittest

from runtime.environment_builder import generate_environment_specs


class StoryEnvironmentBuilderTests(unittest.TestCase):
    def test_same_story_and_shot_is_deterministic(self):
        env = {"procedural": {"profile": "market", "seed": "story-a", "dressing_count": 12}}
        first = generate_environment_specs(env, "story-a", "shot-1")
        second = generate_environment_specs(env, "story-a", "shot-1")
        self.assertEqual(first, second)

    def test_different_stories_get_different_dressing(self):
        env = {"procedural": {"profile": "market", "dressing_count": 12}}
        first = generate_environment_specs(env, "story-a", "shot-1")
        second = generate_environment_specs(env, "story-b", "shot-1")
        self.assertNotEqual(first, second)
        self.assertNotEqual(
            [item["location"] for item in first],
            [item["location"] for item in second],
        )

    def test_profiles_have_distinct_material_palettes(self):
        market = generate_environment_specs({"profile": "market"}, "a", "1")
        snow = generate_environment_specs({"profile": "snow"}, "b", "1")
        self.assertNotEqual(market[0]["material"], snow[0]["material"])

    def test_no_profile_preserves_authored_environment_only(self):
        self.assertEqual(generate_environment_specs({}, "a", "1"), [])

    def test_unknown_profile_fails_loudly(self):
        with self.assertRaisesRegex(ValueError, "Unknown procedural environment"):
            generate_environment_specs({"profile": "underwater_city"}, "a", "1")


if __name__ == "__main__":
    unittest.main()
