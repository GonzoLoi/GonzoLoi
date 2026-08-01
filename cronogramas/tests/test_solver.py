import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scheduler import Assignment, Config, ScheduleError, build_schedule
from scheduler.models import Slot


class SolverTests(unittest.TestCase):
    def setUp(self):
        self.config = Config(
            days=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"],
            periods=["08:00-09:00", "09:00-10:00", "10:00-11:00"],
        )

    def test_simple_schedule_has_no_conflicts(self):
        assignments = [
            Assignment("1ro A", "Matemática", "Juana", 3),
            Assignment("1ro A", "Lengua", "Marcos", 2),
            Assignment("1ro B", "Matemática", "Juana", 3),
            Assignment("1ro B", "Lengua", "Marcos", 2),
        ]
        schedule = build_schedule(self.config, assignments)

        self.assertEqual(sum(a.hours_per_week for a in assignments), len(schedule))

        # A given group (or teacher) must not have two sessions in the same slot.
        group_slot_counts = {}
        teacher_slot_counts = {}
        for (a_idx, _occ), slot in schedule.items():
            a = assignments[a_idx]
            group_slot_counts[(slot, a.group)] = group_slot_counts.get((slot, a.group), 0) + 1
            teacher_slot_counts[(slot, a.teacher)] = teacher_slot_counts.get((slot, a.teacher), 0) + 1
        for count in group_slot_counts.values():
            self.assertEqual(count, 1)
        for count in teacher_slot_counts.values():
            self.assertEqual(count, 1)

        # Same-assignment sessions land on distinct days (enough days available).
        by_assignment_days = {}
        for (a_idx, _occ), slot in schedule.items():
            by_assignment_days.setdefault(a_idx, []).append(slot.day)
        for a_idx, days in by_assignment_days.items():
            self.assertEqual(len(days), len(set(days)))

    def test_respects_teacher_unavailability(self):
        assignments = [Assignment("1ro A", "Matemática", "Juana", 1)]
        unavailable = {"Juana": {Slot("Lunes", "08:00-09:00")}}
        schedule = build_schedule(self.config, assignments, unavailable)
        slot = next(iter(schedule.values()))
        self.assertNotEqual(slot, Slot("Lunes", "08:00-09:00"))

    def test_infeasible_raises(self):
        # Two groups, same teacher, more weekly hours than available slots.
        config = Config(days=["Lunes"], periods=["08:00-09:00"])
        assignments = [
            Assignment("1ro A", "Matemática", "Juana", 1),
            Assignment("1ro B", "Física", "Juana", 1),
        ]
        with self.assertRaises(ScheduleError):
            build_schedule(config, assignments, max_attempts=2)


if __name__ == "__main__":
    unittest.main()
