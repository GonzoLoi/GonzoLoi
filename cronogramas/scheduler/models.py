from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Slot:
    """A single (day, period) cell in the weekly grid."""

    day: str
    period: str

    def __str__(self) -> str:
        return f"{self.day} {self.period}"


@dataclass(frozen=True)
class Assignment:
    """A group/subject/teacher combo that needs `hours_per_week` sessions placed."""

    group: str
    subject: str
    teacher: str
    hours_per_week: int
    room: Optional[str] = None


@dataclass
class Config:
    days: list[str]
    periods: list[str]

    @property
    def slots(self) -> list[Slot]:
        return [Slot(day, period) for day in self.days for period in self.periods]
