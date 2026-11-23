#PRUEBAS DE LA ORDENACIÓN DEL LOTE 23/11/2026
#Se ejecuta con: python prueba_ordenacion.py


from autotaxi.request_queue import RequestQueue
from autotaxi.ordenacion import insercion, clave_prioridad
from autotaxi.errors import BatchMismatchError


#LOTE DEL ENUNCIADO (llegan en este orden: R-0001 primero, R-0005 último)
LOTE_ENUNCIADO = [
    {"request_id": "R-0001", "user": "Ana",   "pickup": (1, 1), "destination": (7, 2), "priority": 2},
    {"request_id": "R-0002", "user": "Luis",  "pickup": (2, 2), "destination": (8, 5), "priority": 1},
    {"request_id": "R-0003", "user": "Marta", "pickup": (3, 4), "destination": (6, 1), "priority": 2},
    {"request_id": "R-0004", "user": "Dani",  "pickup": (1, 6), "destination": (5, 3), "priority": 1},
    {"request_id": "R-0005", "user": "Eva",   "pickup": (2, 5), "destination": (8, 6), "priority": 3},
]

results = []


def show_result(number, name, entrada, expected, obtained, ok) -> None:
    print(f"PRUEBA {number}: {name}")
    print(f"  Entrada:   {entrada}")
    print(f"  Esperado:  {expected}")
    print(f"  Obtenido:  {obtained}")
    print(f"  Resultado: {'CORRECTO' if ok else 'FALLO'}")
    print()
    results.append(ok)


#MOSTRAR UN LOTE COMO TABLA

def show_batch(title, batch) -> None:
    print(f"  {title}")
    print(f"    {'ID':<8}{'Prioridad':<11}{'Llegada':<9}Clave")
    for r in batch:
        print(f"    {r.request_id:<8}{r.priority:<11}{r.arrival_order:<9}{clave_prioridad(r)}")


def ids(batch) -> list[str]:
    return [r.request_id for r in batch]


#ORDENAR LAS PENDIENTES DE UN GESTOR

def ordenar_pendientes(manager: RequestQueue) -> tuple[list, list, int]:
    antes = manager.list_pending()          #(1)
    despues = manager.list_pending()        #(2)
    comparaciones = insercion(despues)      #(3)
    manager.reorder_pending(despues)        #(4)
    return antes, despues, comparaciones

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#   1. Guarda cómo estaba el lote ANTES, para enseñarlo.
#   2. Pide otra copia y ordena esa. La fila real no se toca todavía.
#   3. Ordena con MI inserción y apunta cuántas comparaciones hace.
#   4. Le da el lote ordenado al gestor, que comprueba que es el mismo lote.

##---------------------------------------------------------------------


#PRUEBA O1: LOTE DESORDENADO CON EMPATES (ejemplo del enunciado)

def test_o1_lote_enunciado() -> None:
    manager = RequestQueue()
    for data in LOTE_ENUNCIADO:
        manager.enqueue(data)
    antes, despues, comparaciones = ordenar_pendientes(manager)

    show_batch("ANTES de ordenar (orden de llegada):", antes)
    show_batch("DESPUÉS de ordenar (prioridad, llegada):", despues)
    print(f"  Comparaciones realizadas: {comparaciones}\n")

    esperado = ["R-0002", "R-0004", "R-0001", "R-0003", "R-0005"]
    referencia = ids(sorted(antes, key=clave_prioridad))  #solo para COMPROBAR
    mismas = sorted(ids(antes)) == sorted(ids(despues))   #ni perdidas ni duplicadas
    fila = ids(manager.list_pending())
    show_result("O1", "Lote desordenado con empates de prioridad",
                "R-0001(p2), R-0002(p1), R-0003(p2), R-0004(p1), R-0005(p3)",
                "R-0002, R-0004, R-0001, R-0003, R-0005 y las 5 solicitudes se conservan",
                f"{', '.join(ids(despues))} | igual que sorted(): {ids(despues) == referencia}"
                f" | mismas solicitudes: {mismas} | fila del gestor: {', '.join(fila)}",
                ids(despues) == esperado and ids(despues) == referencia and mismas and fila == esperado)

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Es el caso del enunciado. Hay dos empates: R-0002 y R-0004 (prioridad 1)
#y R-0001 y R-0003 (prioridad 2). En los dos va antes la que llegó antes.
#Se comprueban 4 cosas:
#   - el orden es el esperado,
#   - coincide con sorted() de Python (que se usa SOLO para comprobar),
#   - están las 5 solicitudes, sin perder ni repetir ninguna,
#   - la fila del gestor ha quedado en ese orden.

##---------------------------------------------------------------------


#PRUEBA O2: SIN PRIORIDADES (todas valen 0) -> se mantiene el FIFO de la EI2

def test_o2_sin_prioridad() -> None:
    manager = RequestQueue()
    for data in LOTE_ENUNCIADO:
        sin_prioridad = {k: v for k, v in data.items() if k != "priority"}
        manager.enqueue(sin_prioridad)
    antes, despues, comparaciones = ordenar_pendientes(manager)
    show_result("O2", "Lote sin prioridad (todas empatan)",
                "R-0001 ... R-0005 sin campo priority",
                "Mismo orden de llegada: R-0001 ... R-0005 (4 comparaciones, mejor caso)",
                f"{', '.join(ids(despues))} ({comparaciones} comparaciones)",
                ids(despues) == ids(antes) and comparaciones == 4)


#PRUEBA O3: LOTE VACÍO

def test_o3_lote_vacio() -> None:
    manager = RequestQueue()
    antes, despues, comparaciones = ordenar_pendientes(manager)
    show_result("O3", "Lote vacío",
                "gestor sin solicitudes",
                "No da error, lote vacío y 0 comparaciones",
                f"lote: {ids(despues)}, comparaciones: {comparaciones}",
                despues == [] and comparaciones == 0)


#PRUEBA O4: UN SOLO ELEMENTO

def test_o4_un_elemento() -> None:
    manager = RequestQueue()
    manager.enqueue(LOTE_ENUNCIADO[0])
    antes, despues, comparaciones = ordenar_pendientes(manager)
    show_result("O4", "Lote de una solicitud",
                "R-0001",
                "Queda igual y 0 comparaciones",
                f"lote: {ids(despues)}, comparaciones: {comparaciones}",
                ids(despues) == ["R-0001"] and comparaciones == 0)


#PRUEBA O5: EL GESTOR RECHAZA UN LOTE QUE PIERDE O REPITE SOLICITUDES

def test_o5_lote_incorrecto() -> None:
    manager = RequestQueue()
    for data in LOTE_ENUNCIADO:
        manager.enqueue(data)
    pendientes = manager.list_pending()
    casos = [("perdida", pendientes[:4]),                      #falta R-0005
             ("duplicada", pendientes[:4] + [pendientes[0]])]  #R-0001 dos veces
    for nombre, lote_malo in casos:
        try:
            manager.reorder_pending(lote_malo)
            obtained, ok = "Se ha aceptado el lote", False
        except BatchMismatchError as error:
            fila = ids(manager.list_pending())
            obtained = f"BatchMismatchError ({error}). Fila sin cambios: {fila == ids(pendientes)}"
            ok = fila == ids(pendientes)
        show_result(f"O5-{nombre}", f"Lote con una solicitud {nombre}",
                    ", ".join(ids(lote_malo)),
                    "Se rechaza con BatchMismatchError y la fila no cambia",
                    obtained, ok)

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Se fabrican a propósito dos lotes malos: uno al que le falta una solicitud
#y otro con una repetida. El gestor debe rechazar los dos y dejar la fila
#exactamente como estaba. Si los acepta, la prueba FALLA.

##---------------------------------------------------------------------


if __name__ == "__main__":
    print("=== PRUEBAS DE LA ORDENACIÓN DEL LOTE ===\n")
    test_o1_lote_enunciado()
    test_o2_sin_prioridad()
    test_o3_lote_vacio()
    test_o4_un_elemento()
    test_o5_lote_incorrecto()
    print(f"=== RESUMEN: {sum(results)} de {len(results)} pruebas correctas ===")