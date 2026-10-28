##FICHA DE UNA SOLICITUD DE AutoTaxi Y SUS ESTADOS

#Traigo las herramientas de Python
from dataclasses import dataclass, field #para crear la ficha de forma sencilla
from datetime import datetime #trabajar con fechas y horas
from enum import Enum #crear una lista cerrada de opciones (los estados)

#Asociar un "apodo" a la tupla para agilizar la escritura
position = tuple[int, int] #fila, columna

#Los estados
#Define los únicos tres estados que puede tener una solicitud
#Al ser Enum nadie puede inventarse un estado, es una lista cerrada.
#Si intentan escribir otro estado Python da error.
class RequestStatus(Enum):
    PENDING = "PENDING"         #registrada, esperando en la cola
    HANDLED = "HANDLED"         #estraída de la cola y atendida
    UNRESOLVED = "UNRESOLVED"   #no se pudo resolver (para la versión final)


#El model de la ficha
@dataclass
class Request:
    request_id: str         #identificador(texto) "R-0001"
    user: str               #usuario(texto) "Ana"
    pickup: position        #origen(posicion)(0,1)
    destination: position   #destino(posicion)(2,3)
    arrival_order: int=0    #empieza valiendo 0 
    time_received: datetime = field(default_factory=datetime.now)
    #El field(----) significa: cada vez que se cree una solicitud mira el reloj. 
    status: RequestStatus = RequestStatus.PENDING
    handled_at: datetime | None = None
    #EL datetime |None significa: puede ser una hora o nada, empieza en nada porque todavía no se ha atendido. 

##--------------------------------------------------------------------
## LÓGICA COMPLETA
##---------------------------------------------------------------------

#1. Se crea la ficha 
#   Request("R-0001", "Ana", (0, 1), (2, 3))
#   ->  arrival_order=0, status=PENDING, handled_at=None

#2. El gestor la registra (el gestor es el request_queue.py)
#   -> arrival_order=1  (es la primera en llegar)

#3. El gestor la extrae de la cola
#   -> status=HANDLED, handled_at=12:45
#   -> sigue guardada en el diccionario, con todos sus datos

##----------------------------------------------------------------------