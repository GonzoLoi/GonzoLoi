"""Backtracking solver that places weekly class sessions into a day/period grid
without double-booking a teacher, a group, or (if given) a room."""

import random
from dataclasses import dataclass
from typing import Optional

from .models import Assignment, Config, Slot


class ScheduleError(Exception):
    """Raised when no valid schedule could be found."""


@dataclass
class _Session:
    assignment_index: int
    occurrence: int  # 0-based index within the assignment's required weekly hours


def _expand_sessions(assignments: list[Assignment]) -> list[_Session]:
    sessions = []
    for i, a in enumerate(assignments):
        for occ in range(a.hours_per_week):
            sessions.append(_Session(i, occ))
    return sessions


def build_schedule(
    config: Config,
    assignments: list[Assignment],
    unavailability: Optional[dict[str, set[Slot]]] = None,
    max_attempts: int = 8,
    max_steps: int = 200_000,
) -> dict[tuple[int, int], Slot]:
    """Try to place every required session of every assignment into a slot.

    Constraints enforced:
      - a teacher is never double-booked at the same slot
      - a group is never double-booked at the same slot
      - a room (if set on the assignment) is never double-booked at the same slot
      - an assignment's weekly sessions land on distinct days, whenever there
        are at least as many available days as sessions requested

    Returns ``{(assignment_index, occurrence): Slot}``.
    Raises ``ScheduleError`` if no valid arrangement is found after
    ``max_attempts`` randomized tries.
    """
    unavailability = unavailability or {}
    all_slots = config.slots
    if not all_slots:
        raise ScheduleError("No hay días/periodos configurados en la hoja Config.")

    sessions = _expand_sessions(assignments)
    if not sessions:
        return {}

    for attempt in range(max_attempts):
        rng = random.Random(attempt)
        result = _attempt(config, assignments, sessions, unavailability, all_slots, rng, max_steps)
        if result is not None:
            return result

    raise ScheduleError(
        "No fue posible generar un cronograma sin choques con los datos actuales. "
        "Probá agregar más días/periodos disponibles, revisar la disponibilidad de "
        "los profesores, o reducir las horas semanales de alguna materia."
    )


def _attempt(config, assignments, sessions, unavailability, all_slots, rng, max_steps):
    n = len(sessions)
    order = list(range(n))

    domains: list[set] = []
    for s in sessions:
        a = assignments[s.assignment_index]
        forbidden = unavailability.get(a.teacher, set())
        domains.append({slot for slot in all_slots if slot not in forbidden})

    assigned: dict[int, Slot] = {}
    steps = 0

    def days_used(assignment_index: int) -> set:
        return {
            assigned[i].day
            for i, sess in enumerate(sessions)
            if i in assigned and sess.assignment_index == assignment_index
        }

    def legal_candidates(idx: int) -> list:
        s = sessions[idx]
        a = assignments[s.assignment_index]
        limit_days = a.hours_per_week <= len(config.days)
        used_days = days_used(s.assignment_index) if limit_days else set()
        candidates = []
        for slot in domains[idx]:
            if limit_days and slot.day in used_days:
                continue
            ok = True
            for j, other_slot in assigned.items():
                if other_slot != slot:
                    continue
                other_a = assignments[sessions[j].assignment_index]
                if other_a.group == a.group or other_a.teacher == a.teacher:
                    ok = False
                    break
                if a.room and other_a.room == a.room:
                    ok = False
                    break
            if ok:
                candidates.append(slot)
        return candidates

    def backtrack() -> bool:
        nonlocal steps
        if len(assigned) == n:
            return True

        remaining = [i for i in order if i not in assigned]
        rng.shuffle(remaining)

        best_idx, best_candidates = None, None
        for idx in remaining:
            candidates = legal_candidates(idx)
            if best_candidates is None or len(candidates) < len(best_candidates):
                best_idx, best_candidates = idx, candidates
            if best_candidates is not None and len(best_candidates) == 0:
                break

        if best_idx is None or not best_candidates:
            return False

        rng.shuffle(best_candidates)
        for slot in best_candidates:
            steps += 1
            if steps > max_steps:
                return False
            assigned[best_idx] = slot
            if backtrack():
                return True
            del assigned[best_idx]
        return False

    if backtrack():
        return {
            (sessions[i].assignment_index, sessions[i].occurrence): slot
            for i, slot in assigned.items()
        }
    return None
