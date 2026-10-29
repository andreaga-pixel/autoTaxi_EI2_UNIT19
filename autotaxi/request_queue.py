#EL GESTOR DE SOLICITUDES (el GestorSolicitudes del enunciado)

##Funciona como la fila de una panadería que, además, tiene una libreta:
#   - LA LIBRETA (_registry, un dict): apunta TODAS las solicitudes registradas,
#     también las ya atendidas. Sirve para consultar por ID y para no repetir IDs.
#   - LA FILA (_pending, un deque): guarda solo las PENDIENTES, en orden de llegada.
#     Se entra por el final y se sale por el principio (FIFO).
#   - EL CONTADOR (_next_order): da a cada solicitud su número de llegada (1, 2, 3...).

#Recordatorio en los metodos cuando pondo ->None: esto indica lo que me devuelve
#Importaciones
#deque para la fila y datetime para apuntar la hora de extracción.

from collections import deque
from datetime import datetime

#De mis archivos: los errores, la ficha de solicitud y las comprobaciones.
from .errors import DuplicateIdError, EmptyQueueError
from .models import Request, RequestStatus
from .validation import check_required_fields, validate_id, validate_position, validate_user


class RequestQueue:

    #PREPARAR EL GESTOR VACÍO (constructor)

    def __init__(self) -> None:
        self._registry: dict[str, Request] = {}    #(1) libreta vacía
        self._pending: deque[Request] = deque()    #(2) fila vacía
        self._next_order = 1                       #(3) la primera será la nº1

    ##----------------------------------------------------
    ##              EXPLICACIÓN LÓGICA
    ##------------------------------------------------------
    #Se ejecuta solo al crear el gestor con RequestQueue().
    #   1. La libreta empieza vacía: todavía no hay ninguna solicitud.
    #   2. La fila empieza vacía: no hay nadie esperando.
    #   3. El contador empieza en 1: la primera solicitud que llegue será la nº1.
    #El guion bajo (_) indica que son PRIVADOS: desde fuera solo se usan las operaciones.

    ##---------------------------------------------------------------------


    #REGISTRAR UNA SOLICITUD
    #Coste: O(1) en el caso esperado.

    def enqueue(self, data: dict) -> Request:
        #FASE 1: comprobar todo, sin modificar nada
        check_required_fields(data) #4*c1                             #(1)
        request_id = validate_id(data["request_id"])  #c2             #(2)
        user = validate_user(data["user"]) #c3
        pickup = validate_position(data["pickup"]) #c4
        destination = validate_position(data["destination"]) #c4
        if request_id in self._registry: #c5(búsqueda en el dic.)     #(3)
            raise DuplicateIdError(f"Ya existe una solicitud con ID {request_id}")

        #FASE 2: crear la solicitud y guardarla
        request = Request(request_id, user, pickup, destination,arrival_order=self._next_order) #c6 #(4)
        self._next_order += 1 #c7                                    #(5)
        self._registry[request_id] = request #c8(insercion en el dic)#(6)
        self._pending.append(request) #c9(añadir al final del deque) #(7)
        return request                                               #(8)

    ##----------------------------------------------------
    ##              EXPLICACIÓN LÓGICA
    ##------------------------------------------------------
    #Recibe los datos como un dict:
    #{"request_id": "R-0001", "user": "Ana", "pickup": (0, 1), "destination": (2, 3)}
    #
    #FASE 1: comprobar sin tocar nada
    #   1. ¿Están los 4 campos obligatorios? Si falta alguno -> InvalidDataError
    #   2. ¿El ID, el usuario y las posiciones son correctos? (funciones de validation.py)
    #      Cada función devuelve el dato limpio, que guardamos en una variable.
    #   3. ¿El ID ya está en la libreta? Si está -> DuplicateIdError
    #   Si CUALQUIER comprobación falla, se lanza el error y NO se guarda nada.
    #
    #FASE 2: guardar
    #   4. Crea la ficha con su número de llegada.
    #   5. Suma 1 al contador, para que la siguiente tenga el número siguiente.
    #   6. La apunta en la LIBRETA.
    #   7. La pone al FINAL de la FILA.
    #   8. Devuelve la solicitud creada.
    #
    #¿Por qué en dos fases? Si guardara primero y comprobara después, un fallo
    #podría dejar un ID apuntado en la libreta sin solicitud en la fila.
    #Así la operación se hace entera o no se hace.

    ##---------------------------------------------------------------------


    #CONSULTAR UNA SOLICITUD POR ID (consultar)
    #Coste: O(1) en el caso esperado.

    def find(self, request_id: str) -> Request | None:
        if not isinstance(request_id, str): #c1(¿texto?)                              #(1)
            return None #c2
        return self._registry.get(request_id.strip().upper()) #c3(limpiar)+c4(buscar) #(2)

    ##----------------------------------------------------
    ##              EXPLICACIÓN LÓGICA
    ##------------------------------------------------------
    #   1. Si el ID no es un texto, no puede existir -> devuelve None.
    #   2. Lo limpia igual que al registrar (sin espacios y en mayúsculas)
    #      y lo busca en la LIBRETA con .get():
    #         - si existe, devuelve la solicitud.
    #         - si no existe, devuelve None ("nada"), SIN dar error.
    #Devolver None es el "valor de retorno controlado" que permite el enunciado.
    #Busca en la libreta, así que encuentra también las solicitudes ya atendidas.

    ##---------------------------------------------------------------------


    #LISTAR LAS PENDIENTES (listar_pendientes)
    #Coste: O(n), porque copia todas las pendientes.

    def list_pending(self) -> list[Request]:
        return list(self._pending)

    ##----------------------------------------------------
    ##              EXPLICACIÓN LÓGICA
    ##------------------------------------------------------
    #Devuelve una COPIA de la fila, en orden de llegada.
    #Si alguien modifica la copia, la fila real no cambia.

    ##---------------------------------------------------------------------


    #LISTAR TODAS LAS REGISTRADAS
    #Coste: O(n).

    def list_all(self) -> list[Request]:
        return list(self._registry.values())

    ##----------------------------------------------------
    ##              EXPLICACIÓN LÓGICA
    ##------------------------------------------------------
    #Devuelve una COPIA de todo lo que hay en la LIBRETA: pendientes y atendidas.
    #La usaremos en la demo para enseñar que los datos se conservan al extraer.
    #El dict recuerda el orden en que se añadieron, así que salen por orden de llegada.

    ##---------------------------------------------------------------------


    #EXTRAER LA SIGUIENTE SOLICITUD (extraer_siguiente)
    #Coste: O(1).

    def dequeue(self) -> Request:
        if self.is_empty(): #c1(¿hay alguien?)                       #(1)
            raise EmptyQueueError("No hay solicitudes pendientes")#c2
        request = self._pending.popleft()  #c3(sacar el primero)     #(2)
        request.status = RequestStatus.HANDLED #c4(marcar atendida)  #(3)
        request.handled_at = datetime.now() #c5(apuntar la hora)     #(4)
        return request  #c6                                          #(5)

    ##----------------------------------------------------
    ##              EXPLICACIÓN LÓGICA
    ##------------------------------------------------------
    #   1. Si la fila está vacía -> EmptyQueueError (termina de forma controlada).
    #   2. popleft() saca la PRIMERA de la fila. Eso es el FIFO.
    #   3. Cambia su estado a HANDLED (atendida).
    #   4. Apunta la hora en que se ha atendido.
    #   5. Devuelve la solicitud extraída.
    #
    #DETALLE CLAVE: la ficha de la fila y la de la libreta son LA MISMA ficha,
    #no dos copias. Al sacarla de la fila sigue en la libreta, y como hemos
    #cambiado su estado y su hora, la libreta ya tiene los datos actualizados.
    #Así se conservan los datos que se registran al extraer.

    ##---------------------------------------------------------------------


    #¿ESTÁ VACÍA? (esta_vacio)
    #Coste: O(1).

    def is_empty(self) -> bool:
        return len(self._pending) == 0

    ##----------------------------------------------------
    ##              EXPLICACIÓN LÓGICA
    ##------------------------------------------------------
    #Devuelve True si no queda ninguna solicitud PENDIENTE en la fila.
    #Las atendidas no cuentan: están en la libreta, pero ya no en la fila.

    ##---------------------------------------------------------------------


##RESUMEN: OPERACIONES DEL ENUNCIADO Y SU EQUIVALENTE EN MI CÓDIGO
##   registrar          -> enqueue
##   consultar          -> find
##   listar_pendientes  -> list_pending
##   extraer_siguiente  -> dequeue
##   esta_vacio         -> is_empty
