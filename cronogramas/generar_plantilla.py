#!/usr/bin/env python3
"""Genera un Excel de plantilla (con datos de ejemplo) para completar y luego
pasarle a main.py.

Uso:
    python generar_plantilla.py plantilla.xlsx
"""

import sys

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

HEADER_FILL = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
HEADER_FONT = Font(color="FFFFFF", bold=True)


def _header_row(ws, headers: list[str]) -> None:
    for col_i, h in enumerate(headers, start=1):
        c = ws.cell(row=1, column=col_i, value=h)
        c.font = HEADER_FONT
        c.fill = HEADER_FILL
        ws.column_dimensions[get_column_letter(col_i)].width = max(14, len(h) + 4)


def build_template(path: str) -> None:
    wb = Workbook()

    ws = wb.active
    ws.title = "Config"
    _header_row(ws, ["Dias", "Periodos"])
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    periodos = ["08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00"]
    for i in range(max(len(dias), len(periodos))):
        ws.cell(row=2 + i, column=1, value=dias[i] if i < len(dias) else None)
        ws.cell(row=2 + i, column=2, value=periodos[i] if i < len(periodos) else None)

    ws = wb.create_sheet("Asignaciones")
    _header_row(ws, ["Grupo", "Materia", "Profesor", "HorasSemana", "Aula"])
    ejemplo = [
        ("1ro A", "Matemática", "Juana Pérez", 4, "Aula 1"),
        ("1ro A", "Lengua", "Marcos Ruiz", 4, "Aula 1"),
        ("1ro A", "Inglés", "Laura Gómez", 2, "Aula 1"),
        ("1ro B", "Matemática", "Juana Pérez", 4, "Aula 2"),
        ("1ro B", "Lengua", "Marcos Ruiz", 4, "Aula 2"),
        ("1ro B", "Inglés", "Laura Gómez", 2, "Aula 2"),
    ]
    for row_i, (grupo, materia, profesor, horas, aula) in enumerate(ejemplo, start=2):
        ws.cell(row=row_i, column=1, value=grupo)
        ws.cell(row=row_i, column=2, value=materia)
        ws.cell(row=row_i, column=3, value=profesor)
        ws.cell(row=row_i, column=4, value=horas)
        ws.cell(row=row_i, column=5, value=aula)

    ws = wb.create_sheet("NoDisponibilidad")
    _header_row(ws, ["Profesor", "Dia", "Periodo"])
    ws.cell(row=2, column=1, value="Marcos Ruiz")
    ws.cell(row=2, column=2, value="Viernes")
    ws.cell(row=2, column=3, value="08:00-09:00")

    notas = wb.create_sheet("Instrucciones")
    notas.sheet_view.showGridLines = False
    lines = [
        "Cómo completar este archivo:",
        "",
        "Hoja 'Config': listá los días de la semana (columna Dias) y los",
        "  bloques horarios del día (columna Periodos). No hace falta que",
        "  tengan la misma cantidad de filas.",
        "",
        "Hoja 'Asignaciones': una fila por cada combinación Grupo+Materia+",
        "  Profesor, con las horas semanales que necesita esa materia y,",
        "  opcionalmente, el aula donde se dicta. Borrá las filas de ejemplo",
        "  y cargá las tuyas.",
        "",
        "Hoja 'NoDisponibilidad' (opcional): si un profesor NO puede dar",
        "  clase en un Día+Periodo puntual, agregalo acá. Se puede dejar",
        "  vacía o borrar la hoja si no aplica.",
        "",
        "Una vez completado, generá el cronograma con:",
        "  python main.py plantilla.xlsx cronograma.xlsx",
    ]
    for i, line in enumerate(lines, start=1):
        notas.cell(row=i, column=1, value=line)
    notas.column_dimensions["A"].width = 70

    wb.save(path)


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else "plantilla.xlsx"
    build_template(path)
    print(f"Plantilla generada en '{path}'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
