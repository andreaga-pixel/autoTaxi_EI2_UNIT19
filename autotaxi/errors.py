## Errores propios del gestor de solicitudes de AutoTaxi.

#NINGUNA de estas clases hace calculos, solo sirve para cuando algo va mal, 
# el programa diga que ha ido mal. 

#La madre de todos los errores
#Todas las demas clases heredan de ella, Exception en Python es el error general
class AutoTaxiError(Exception):
    """Clase base: permite capturar cualquier error de AutoTaxi con un solo except."""

#Detecta duplicados
#Los identificadores deben ser únicos.
#Si se permitiera, habría dos solicitudes con el mismo ID y ya no se sabría cual es cual. 
class DuplicateIdError(AutoTaxiError):
    """El identificador de la solicitud ya está registrado."""

#Detecta que hay campos obligatorios sin rellenar o un dato está mal
#Una solicitud sin destino no se puede atender. es mejor rechazarla al registrarla que descubriri el problema despues.
class InvalidDataError(AutoTaxiError):
    """Falta un dato obligatorio o tiene un tipo incorrecto."""

#Detecta errores en la posicion
#Las coordenadas deben tener dos componentes enteros. 
class InvalidPositionError(AutoTaxiError):
    """La coordenada no tiene la forma (fila, columna) con dos enteros."""

#Cola vacía
#Extraer de una estructura vacía debe termianr de forma controlada
class EmptyQueueError(AutoTaxiError):
    """Se intenta extraer de una cola sin solicitudes pendientes."""