# Cronogramas

Programa en Python para armar el horario de clases de un centro de enseñanza
a partir de un Excel con las asignaciones (grupo, materia, profesor, horas
semanales) y generar un cronograma sin choques de profesores, grupos ni aulas.

## Instalación

```bash
cd cronogramas
pip install -r requirements.txt
```

## Uso

### 1. Generar una plantilla de entrada

```bash
python generar_plantilla.py plantilla.xlsx
```

Esto crea `plantilla.xlsx` con datos de ejemplo y una hoja de instrucciones.
Completala con tus propios datos (o editá el ejemplo) antes de seguir.

### 2. Generar el cronograma

```bash
python main.py plantilla.xlsx cronograma.xlsx
```

`cronograma.xlsx` va a tener:

- **Resumen**: una fila por cada materia/grupo/profesor con sus horarios asignados.
- **Grupo XXX**: una grilla día × periodo por cada grupo/curso.
- **Prof XXX**: una grilla día × periodo por cada profesor, para que cada uno
  vea su propia carga horaria.

## Formato del Excel de entrada

### Hoja `Config`

| Dias   | Periodos     |
|--------|--------------|
| Lunes  | 08:00-09:00  |
| Martes | 09:00-10:00  |
| ...    | ...          |

Las dos columnas son independientes: no hace falta que tengan la misma
cantidad de filas.

### Hoja `Asignaciones`

| Grupo  | Materia    | Profesor    | HorasSemana | Aula   |
|--------|-----------|-------------|-------------|--------|
| 1ro A  | Matemática | Juana Pérez | 4           | Aula 1 |

Una fila por cada combinación Grupo + Materia + Profesor. `Aula` es opcional;
si se completa, el programa evita que dos clases usen la misma aula al mismo
tiempo.

### Hoja `NoDisponibilidad` (opcional)

| Profesor    | Dia     | Periodo     |
|-------------|---------|-------------|
| Marcos Ruiz | Viernes | 08:00-09:00 |

Franjas en las que un profesor puntual NO puede dar clase. Se puede omitir
esta hoja si no aplica.

## Cómo arma el cronograma

El motor (`scheduler/solver.py`) usa backtracking con la heurística de
"variable más restringida" (MRV): en cada paso elige la clase que tiene menos
horarios posibles y prueba asignarla, retrocediendo si se traba. Garantiza:

- un profesor nunca da dos clases a la vez,
- un grupo nunca tiene dos clases a la vez,
- un aula (si se especifica) nunca se usa por dos clases a la vez,
- las horas semanales de una misma materia se reparten en días distintos,
  siempre que haya al menos tantos días como horas pedidas.

Si los datos son imposibles de cumplir (por ejemplo, un profesor con más
horas que huecos disponibles), el programa lo informa por consola en vez de
generar un cronograma con choques.

## Tests

```bash
python -m unittest tests/test_solver.py -v
```
