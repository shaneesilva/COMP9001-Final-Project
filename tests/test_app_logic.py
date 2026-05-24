import unittest

import main


class PixelPetLogicTests(unittest.TestCase):
    def test_recursive_count_completed(self):
        tasks = [
            {"completed": True},
            {"completed": False},
            {"completed": True},
        ]
        self.assertEqual(main.recursive_count_completed(tasks), 2)

    def test_recursive_tasks_for_day(self):
        tasks = [
            {"text": "A", "date": "2026-05-21"},
            {"text": "B", "date": "2026-05-20"},
            {"text": "C", "date": "2026-05-21"},
        ]
        todays_tasks = main.recursive_tasks_for_day(tasks, "2026-05-21")
        self.assertEqual([task["text"] for task in todays_tasks], ["A", "C"])

    def test_cat_is_full_after_goal(self):
        tasks = [{"completed": True, "completed_at": None} for _ in range(main.DAILY_GOAL)]
        cat = main.build_cat_state(tasks)
        self.assertEqual(cat["name"], "Full")
        self.assertEqual(cat["bowl_percent"], 100)


if __name__ == "__main__":
    unittest.main()
