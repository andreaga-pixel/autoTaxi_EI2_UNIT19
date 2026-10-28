# AutoTaxi – Gestor de solicitudes (Unit 19 · Entrega 2)

Primera versión ejecutable del sistema de despacho de **AutoTaxi**.
Registra, guarda, consulta y extrae solicitudes de taxi en orden de llegada (FIFO).

**Autora:** Andrea Gutiérrez Arcas
**Asignatura:** Unit 19 – Data Structures and Algorithms

## Cómo funciona

El gestor (`RequestQueue`) usa dos estructuras de Python:

| Estructura | Para qué sirve |
|---|---|
| **Diccionario** (`dict`) | Guarda **todas** las solicitudes registradas por su ID, también las ya atendidas. Permite consultar por ID y evita IDs repetidos. |
| **Deque** (`collections.deque`) | Guarda las solicitudes **pendientes** en orden de llegada. Se añade por el final y se extrae por el principio (FIFO). |

Cada solicitud recibe un **número de llegada** (1, 2, 3…) que deja claro el orden FIFO.
Al extraerla, pasa a estado **HANDLED** y se guarda la hora de atención, sin borrarla del registro.

## Operaciones

| Operación del enunciado | Método | Coste |
|---|---|---|
| registrar | `enqueue(datos)` | O(1) esperado |
| consultar | `find(id)` | O(1) esperado |
| listar_pendientes | `list_pending()` | O(n) |
| extraer_siguiente | `dequeue()` | O(1) |
| esta_vacio | `is_empty()` | O(1) |

## Estructura del proyecto

```
autoTaxi_EI2_UNIT19/
├── autotaxi/
│   ├── models.py          Ficha de la solicitud y sus estados
│   ├── errors.py          Errores del sistema
│   ├── validation.py      Comprobaciones de los datos
│   └── request_queue.py   Gestor de solicitudes (dict + deque)
├── demo.py                Demostración: 5 registros, 1 consulta y 3 extracciones
├── pruebas.py             Pruebas de los 6 casos del enunciado
└── README.md
```

## Cómo ejecutarlo

Requisitos: **Python 3.10 o superior**. No necesita instalar ninguna librería.

Desde la carpeta del proyecto:

```
python demo.py
```

```
python pruebas.py
```

## Uso de herramientas de IA

Este proyecto se ha desarrollado con la ayuda de GitHub Copilot como apoyo
para escribir el código de manera más efectiva y Claude para entender conceptos que me han permitido detallar la lógica y funcionamiento del programa, funciones de Python y proponer la estructura del código cuando no me estaba funcionando el que inicialmente se me ocurria a mi.

Las decisiones de diseño, las pruebas y su documentación se explican en el informe de la entrega.