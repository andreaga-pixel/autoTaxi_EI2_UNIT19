#GESTOR INTEGRADO DE AutoTaxi

##Une todas las piezas para procesar un lote completo de solicitudes:
#   1. Ordenar el lote pendiente con MI algoritmo (inserción).
#   2. Sacar la siguiente solicitud de la cola (FIFO sobre el lote ya ordenado).
#   3. Validar origen y destino contra el mapa y buscar la ruta.
#   4. Guardar el resultado en la solicitud: HANDLED, UNRESOLVED o INVALID.
#   5. Seguir con la siguiente, aunque una falle, hasta vaciar la cola.

from .errors import InvalidPositionError
from .busqueda import buscar_ruta
from .models import Request, RequestStatus
from .ordenacion import insercion
from .request_queue import RequestQueue


#ATENDER UNA SOLICITUD

def atender(request: Request, mapa: list[list[int]]) -> int:
    try:
        ruta, explorados = buscar_ruta(mapa, request.pickup, request.destination)  #(1)
    except InvalidPositionError as error:                                          #(2)
        request.status = RequestStatus.INVALID
        request.result_note = str(error)
        return 0
    if ruta:                                                                       #(3)
        request.status = RequestStatus.HANDLED
        request.route = ruta
        request.route_length = len(ruta) - 1
    else:                                                                          #(4)
        request.status = RequestStatus.UNRESOLVED
        request.result_note = "No existe ninguna ruta entre el origen y el destino"
    return explorados

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Recibe una solicitud ya sacada de la cola y el mapa. Devuelve los nodos explorados.
#   1. Busca la ruta. buscar_ruta valida antes el origen y el destino.
#   2. Si el origen o el destino están fuera del mapa o en una pared, buscar_ruta
#      lanza InvalidPositionError. Se CAPTURA aquí: la solicitud queda INVALID con
#      el motivo y el programa NO se detiene.
#   3. Si hay ruta: HANDLED, y se guarda la ruta y su longitud (casillas - 1).
#   4. Si la ruta está vacía: se exploró todo lo alcanzable y no hay camino,
#      así que queda UNRESOLVED (no_resuelta) con el motivo.

##---------------------------------------------------------------------


#PROCESAR EL LOTE COMPLETO

def procesar_lote(manager: RequestQueue, mapa: list[list[int]]) -> list[Request]:
    if manager.is_empty():                                                         #(1)
        print("No hay solicitudes pendientes. No hay nada que procesar.")
        return []

    lote = manager.list_pending()                                                  #(2)
    print("LOTE PENDIENTE (orden de llegada):", ", ".join(r.request_id for r in lote))
    comparaciones = insercion(lote)
    manager.reorder_pending(lote)
    print("LOTE ORDENADO (prioridad, llegada):", ", ".join(r.request_id for r in lote))
    print(f"Comparaciones de la inserción: {comparaciones}\n")

    atendidas = []
    while not manager.is_empty():                                                  #(3)
        request = manager.dequeue()                                                #(4)
        explorados = atender(request, mapa)                                        #(5)
        mostrar_resultado(request, explorados)
        atendidas.append(request)
    return atendidas                                                               #(6)

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#   1. Lote vacío: lo dice y termina de forma controlada (sin errores).
#   2. Ordena una COPIA de las pendientes con la inserción y se la da al gestor
#      con reorder_pending, que comprueba que no se pierde ni se repite ninguna.
#   3. Repite mientras queden solicitudes pendientes.
#   4. dequeue saca la primera de la cola (la más prioritaria, porque ya está
#      ordenada). Al sacarla deja de estar pendiente, pero sigue en el registro.
#   5. La atiende y muestra el resultado. Como atender captura los errores,
#      una solicitud que falla NO detiene el lote: se pasa a la siguiente.
#   6. Devuelve la lista de solicitudes atendidas, en el orden en que se procesaron.

##---------------------------------------------------------------------


#MOSTRAR EL RESULTADO DE UNA SOLICITUD

def mostrar_resultado(request: Request, explorados: int) -> None:
    print(f"{request.request_id} ({request.user}) | prioridad {request.priority} | "
          f"{request.pickup} -> {request.destination}")
    if request.status == RequestStatus.HANDLED:
        print(f"   ATENDIDA. Ruta: {request.route}")
        print(f"   Longitud: {request.route_length} movimientos | Nodos explorados: {explorados}")
    elif request.status == RequestStatus.UNRESOLVED:
        print(f"   NO RESUELTA. {request.result_note} | Nodos explorados: {explorados}")
    else:
        print(f"   INVÁLIDA. {request.result_note}")
    print()