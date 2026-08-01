#!/usr/bin/env python3
"""Genera un cronograma de clases a partir de un Excel de entrada.

Uso:
    python main.py entrada.xlsx salida.xlsx
"""

import sys

from scheduler import ScheduleError, build_schedule
from scheduler.io_excel import load_input, write_output


def main() -> int:
    if len(sys.argv) != 3:
        print("Uso: python main.py <entrada.xlsx> <salida.xlsx>")
        return 1

    entrada, salida = sys.argv[1], sys.argv[2]

    try:
        config, assignments, unavailability = load_input(entrada)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error al leer '{entrada}': {e}")
        return 1

    total_horas = sum(a.hours_per_week for a in assignments)
    print(f"Leídas {len(assignments)} asignaciones ({total_horas} horas/semana en total).")
    print(f"Días: {', '.join(config.days)}")
    print(f"Periodos: {', '.join(config.periods)}")

    try:
        schedule = build_schedule(config, assignments, unavailability)
    except ScheduleError as e:
        print(f"No se pudo generar el cronograma: {e}")
        return 1

    write_output(salida, config, assignments, schedule)
    print(f"Cronograma generado en '{salida}'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
