import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scheduler.models import Config
from scheduler.periods import fila_orden_clave, generar_periodos


class PeriodsTests(unittest.TestCase):
    def test_modules_of_45_minutes_with_two_recesses(self):
        periodos, recreos = generar_periodos(
            hora_inicio="08:00",
            duracion_modulo=45,
            cantidad_modulos=4,
            recreos=[(2, 15), (4, 15)],
        )
        self.assertEqual(
            periodos,
            ["08:00-08:45", "08:45-09:30", "09:45-10:30", "10:30-11:15"],
        )
        self.assertEqual(recreos, ["09:30-09:45", "11:15-11:30"])

    def test_modules_of_60_minutes_no_recess(self):
        periodos, recreos = generar_periodos(
            hora_inicio="08:00", duracion_modulo=60, cantidad_modulos=3, recreos=None
        )
        self.assertEqual(periodos, ["08:00-09:00", "09:00-10:00", "10:00-11:00"])
        self.assertEqual(recreos, [])

    def test_recesses_are_not_schedulable_slots(self):
        periodos, recreos = generar_periodos("08:00", 45, 4, [(2, 15)])
        config = Config(days=["Lunes"], periods=periodos, recesses=recreos)
        slot_periods = {slot.period for slot in config.slots}
        for recreo in recreos:
            self.assertNotIn(recreo, slot_periods)

    def test_sort_key_orders_chronologically(self):
        franjas = ["09:30-09:45", "08:00-08:45", "10:45-11:30"]
        self.assertEqual(
            sorted(franjas, key=fila_orden_clave),
            ["08:00-08:45", "09:30-09:45", "10:45-11:30"],
        )


if __name__ == "__main__":
    unittest.main()
