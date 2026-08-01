"""Helpers to turn "módulos de 45/60 minutos + recreos" into the plain
Periodos/Recreos labels the rest of the program works with."""


def _to_minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _to_hhmm(minutes: int) -> str:
    return f"{(minutes // 60) % 24:02d}:{minutes % 60:02d}"


def generar_periodos(
    hora_inicio: str,
    duracion_modulo: int,
    cantidad_modulos: int,
    recreos: list[tuple[int, int]] | None = None,
) -> tuple[list[str], list[str]]:
    """Genera las franjas horarias de los módulos de clase y de los recreos.

    - hora_inicio: hora de comienzo del primer módulo, formato "HH:MM".
    - duracion_modulo: minutos que dura cada módulo (típico: 45 o 60).
    - cantidad_modulos: cantidad de módulos de clase por día.
    - recreos: lista de (después_de_módulo, duración_minutos), donde
      "después_de_módulo" es el número de módulo (1-based) tras el cual hay
      un recreo. Ej: [(2, 15), (4, 15)] = recreo de 15' después del 2do y
      4to módulo.

    Devuelve (periodos, recreos_franjas), ambos como listas de strings
    "HH:MM-HH:MM" en orden cronológico.
    """
    recreo_map: dict[int, list[int]] = {}
    for despues_de, duracion in recreos or []:
        recreo_map.setdefault(despues_de, []).append(duracion)

    t = _to_minutes(hora_inicio)
    periodos: list[str] = []
    recreos_franjas: list[str] = []
    for modulo in range(1, cantidad_modulos + 1):
        inicio, fin = t, t + duracion_modulo
        periodos.append(f"{_to_hhmm(inicio)}-{_to_hhmm(fin)}")
        t = fin
        for duracion in recreo_map.get(modulo, []):
            inicio_r, fin_r = t, t + duracion
            recreos_franjas.append(f"{_to_hhmm(inicio_r)}-{_to_hhmm(fin_r)}")
            t = fin_r

    return periodos, recreos_franjas


def fila_orden_clave(franja: str) -> int:
    """Clave de orden cronológico para una franja "HH:MM-HH:MM"."""
    inicio = franja.split("-")[0].strip()
    try:
        return _to_minutes(inicio)
    except (ValueError, IndexError):
        return 0
