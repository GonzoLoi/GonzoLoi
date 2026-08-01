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

Por defecto arma módulos de 45 minutos con recreos después del 2do y 4to
módulo, pero se puede ajustar todo por línea de comandos:

```bash
python generar_plantilla.py plantilla.xlsx \
    --duracion 60 \      # minutos por módulo (45, 60, lo que uses)
    --modulos 5 \        # cantidad de módulos por día
    --inicio 08:00 \     # hora del primer módulo
    --recreo 2:20        # recreo de 20' después del 2do módulo (repetible)
```

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

| Dias   | Periodos     | Recreos      |
|--------|--------------|--------------|
| Lunes  | 08:00-08:45  | 09:30-09:45  |
| Martes | 08:45-09:30  |              |
| ...    | 09:45-10:30  |              |

Las tres columnas son independientes: no hace falta que tengan la misma
cantidad de filas. `Periodos` puede ser cualquier franja horaria — módulos de
45', de 60', o lo que uses en tu centro — vos elegís el texto.

`Recreos` (opcional) son franjas que se muestran en el cronograma final como
una fila "RECREO" pero **nunca reciben clases**: no forman parte de los
horarios disponibles para el armado. Se pueden cargar a mano o generar
automáticamente con `generar_plantilla.py --recreo` (ver arriba).

### Hoja `Asignaciones`

| Grupo  | Materia    | Profesor    | HorasSemana | Aula   |
|--------|-----------|-------------|-------------|--------|
| 1ro A  | Matemática | Juana Pérez | 4           | Aula 1 |

Una fila por cada combinación Grupo + Materia + Profesor. `HorasSemana` es la
cantidad de módulos semanales que necesita esa materia (no necesariamente
"horas reloj" — depende de la duración del módulo que definas en `Config`).
`Aula` es opcional; si se completa, el programa evita que dos clases usen la
misma aula al mismo tiempo.

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
python -m unittest discover -s tests -v
```
