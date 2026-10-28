#DEMOSTRACIÓN DEL GESTOR DE SOLICITUDES
#Se ejecuta con: python demo.py
#Hace 5 registros, 1 consulta y 3 extracciones,
#y muestra el contenido del gestor después de cada paso.


#Importaciones
#El gestor y la "madre" de los errores (para capturar cualquier fallo).
from autotaxi.request_queue import RequestQueue
from autotaxi.errors import AutoTaxiError


#LOS DATOS DE PRUEBA
#Cada solicitud es un dict con sus 4 campos obligatorios.

SOLICITUDES = [
    {"request_id": "R-0001", "user": "Ana",   "pickup": (0, 1), "destination": (2, 3)},
    {"request_id": "R-0002", "user": "Luis",  "pickup": (1, 1), "destination": (3, 0)},
    {"request_id": "R-0003", "user": "Marta", "pickup": (2, 2), "destination": (0, 0)},
    {"request_id": "R-0004", "user": "Dani",  "pickup": (3, 4), "destination": (1, 2)},
    {"request_id": "R-0005", "user": "Eva",   "pickup": (4, 0), "destination": (0, 4)},
]


#MOSTRAR EL CONTENIDO DEL GESTOR

def show_state(manager: RequestQueue) -> None:
    #(1) La fila de pendientes
    print("  PENDIENTES (deque, de la primera a la última):")
    pending = manager.list_pending()
    if pending:
        line = ""
        for r in pending:
            line += f"{r.request_id} (nº{r.arrival_order})   "
        print("    " + line)
    else:
        print("    (vacía)")

    #(2) La libreta con todas las solicitudes
    print("  REGISTRO (diccionario, todas las solicitudes):")
    print(f"    {'ID':<8}{'Nº':<4}{'Usuario':<8}{'Origen':<9}{'Destino':<9}{'Estado':<10}Atendida")
    for r in manager.list_all():
        if r.handled_at is None:
            handled = "-"
        else:
            handled = r.handled_at.strftime("%H:%M:%S")
        print(f"    {r.request_id:<8}{r.arrival_order:<4}{r.user:<8}{str(r.pickup):<9}"
              f"{str(r.destination):<9}{r.status.value:<10}{handled}")
    print()

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Esta función solo MUESTRA, no cambia nada del gestor.
#   1. Pide la copia de la fila (list_pending) y escribe los IDs en una línea,
#      con su número de llegada. Si no hay ninguno, escribe "(vacía)".
#   2. Pide la copia de la libreta (list_all) y escribe una fila por solicitud.
#      Si todavía no se ha atendido, en "handled" pone "-".
#      Si ya se atendió, pone la hora (strftime la escribe como 13:45:02).
#Los :<8, :<4... dejan un ancho fijo para cada columna, así sale como una tabla.

##---------------------------------------------------------------------


#LA DEMOSTRACIÓN

def main() -> None:
    manager = RequestQueue()
    step = 1

    #(1) Registrar las 5 solicitudes
    print("=== 1) REGISTRO DE 5 SOLICITUDES ===\n")
    for data in SOLICITUDES:
        request = manager.enqueue(data)
        print(f"Paso {step}: registrar {request.request_id} ({request.user})"
              f" -> nº de llegada {request.arrival_order}")
        show_state(manager)
        step += 1

    #(2) Consultar una solicitud por su ID
    print("=== 2) CONSULTA POR IDENTIFICADOR ===\n")
    print(f"Paso {step}: consultar R-0003")
    found = manager.find("R-0003")
    if found is None:
        print("  No existe ninguna solicitud con ese ID")
    else:
        print(f"  Encontrada: usuario {found.user}, origen {found.pickup},"
              f" destino {found.destination}, estado {found.status.value}")
    show_state(manager)
    step += 1

    #(3) Extraer las 3 primeras pendientes
    print("=== 3) TRES EXTRACCIONES (FIFO) ===\n")
    for _ in range(3):
        request = manager.dequeue()
        print(f"Paso {step}: extraer siguiente -> {request.request_id}"
              f" (nº{request.arrival_order}, {request.user})")
        show_state(manager)
        step += 1

    #(4) Resumen final
    print("=== RESUMEN ===")
    print(f"Quedan {len(manager.list_pending())} pendientes. ¿Está vacía? {manager.is_empty()}")

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#   1. Registra las 5 solicitudes una a una. Después de cada una enseña
#      su número de llegada y el contenido del gestor.
#   2. Consulta R-0003. Si find devuelve None, avisa de que no existe.
#      Si la encuentra, enseña sus datos. La consulta no cambia nada.
#   3. Extrae 3 veces. Deben salir R-0001, R-0002 y R-0003, en el orden
#      en que llegaron (FIFO). En el registro se verá que pasan a HANDLED
#      con su hora, y que NO desaparecen: los datos se conservan.
#   4. Al final quedan 2 pendientes (R-0004 y R-0005).
#"step" es un contador que numera los pasos en pantalla.

##---------------------------------------------------------------------


#ARRANCAR EL PROGRAMA

if __name__ == "__main__":
    try:
        main()
    except AutoTaxiError as error:
        print("Error:", error)

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#if __name__ == "__main__" significa: "ejecuta main() solo si se arranca
#este archivo directamente" (con python demo.py).
#El try/except captura cualquier error de AutoTaxi y muestra un mensaje
#en lugar de que el programa se rompa.

##---------------------------------------------------------------------