#PRUEBAS DEL GESTOR DE SOLICITUDES
#Se ejecuta con: python pruebas.py
#Comprueba los 6 casos del enunciado. Para cada uno muestra
#la entrada, el resultado esperado, el obtenido y si es correcto.


#Importaciones

from autotaxi.request_queue import RequestQueue
from autotaxi.errors import (DuplicateIdError, EmptyQueueError, InvalidDataError, InvalidPositionError)


#DATOS DE PRUEBA

ANA   = {"request_id": "R-0001", "user": "Ana",   "pickup": (0, 1), "destination": (2, 3)}
LUIS  = {"request_id": "R-0002", "user": "Luis",  "pickup": (1, 1), "destination": (3, 0)}
MARTA = {"request_id": "R-0003", "user": "Marta", "pickup": (2, 2), "destination": (0, 0)}

results = []   #aquí se apunta si cada prueba es correcta (True) o no (False)


#MOSTRAR EL RESULTADO DE UNA PRUEBA

def show_result(number, name, entrada, expected, obtained, ok) -> None:
    print(f"PRUEBA {number}: {name}")
    print(f"  Entrada:   {entrada}")
    print(f"  Esperado:  {expected}")
    print(f"  Obtenido:  {obtained}")
    print(f"  Resultado: {'CORRECTO' if ok else 'FALLO'}")
    print()
    results.append(ok)

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Escribe los datos de la prueba en un formato fijo y apunta en la lista
#"results" si ha salido bien. Al final se cuentan las correctas.
#'CORRECTO' if ok else 'FALLO' -> escribe CORRECTO si ok es True, y FALLO si no.

##---------------------------------------------------------------------


#PRUEBA 1: REGISTRO Y CONSULTA

def test_1_registro_y_consulta() -> None:
    manager = RequestQueue()
    manager.enqueue(ANA)
    found = manager.find("R-0001")
    if found is None:
        obtained = "No se encuentra"
    else:
        obtained = f"Se encuentra {found.request_id} con usuario {found.user}"
    show_result(1, "Registro y consulta",
                "registrar R-0001 (Ana) y consultar R-0001",
                "Se encuentra R-0001 con usuario Ana",
                obtained,
                found is not None and found.user == "Ana")


#PRUEBA 2: ID DUPLICADO

def test_2_id_duplicado() -> None:
    manager = RequestQueue()
    manager.enqueue(ANA)
    duplicate = {"request_id": "R-0001", "user": "Luis", "pickup": (1, 1), "destination": (3, 0)}
    try:
        manager.enqueue(duplicate)
        obtained = "Se ha aceptado el duplicado"
        ok = False
    except DuplicateIdError as error:
        total = len(manager.list_all())
        obtained = f"DuplicateIdError ({error}). Solicitudes registradas: {total}"
        ok = (total == 1)
    show_result(2, "Identificador duplicado",
                "registrar R-0001 (Ana) y después otra vez R-0001 (Luis)",
                "Se rechaza con DuplicateIdError y sigue habiendo 1 solicitud",
                obtained, ok)

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Intenta registrar el mismo ID dos veces.
#try: si el segundo registro se acepta, la prueba FALLA.
#except: si salta DuplicateIdError, comprueba además que el gestor
#sigue teniendo 1 sola solicitud (no se ha duplicado).

##---------------------------------------------------------------------


#PRUEBA 3: CONSULTA DE UN ID QUE NO EXISTE

def test_3_consulta_inexistente() -> None:
    manager = RequestQueue()
    manager.enqueue(ANA)
    found = manager.find("R-9999")
    if found is None:
        obtained = "None -> 'El identificador R-9999 no está registrado'"
    else:
        obtained = f"Ha devuelto {found.request_id}"
    show_result(3, "Consulta de un registro inexistente",
                "registrar R-0001 y consultar R-9999",
                "Devuelve None y se informa de que no está registrado",
                obtained, found is None)


#PRUEBA 4: EXTRACCIONES FIFO

def test_4_extracciones_fifo() -> None:
    manager = RequestQueue()
    manager.enqueue(ANA)
    manager.enqueue(LUIS)
    manager.enqueue(MARTA)
    order = []
    for _ in range(3):
        order.append(manager.dequeue().request_id)
    show_result(4, "Extracciones FIFO",
                "registrar R-0001, R-0002, R-0003 y extraer 3 veces",
                "Salen R-0001, R-0002, R-0003 (orden de llegada)",
                "Salen " + ", ".join(order),
                order == ["R-0001", "R-0002", "R-0003"])

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Registra 3 solicitudes y las extrae una a una, apuntando el ID de
#cada una en la lista "order". La prueba es correcta si salen en el
#mismo orden en que entraron.
#", ".join(order) une los IDs en un solo texto separado por comas.

##---------------------------------------------------------------------


#PRUEBA 5: ESTRUCTURA VACÍA

def test_5_estructura_vacia() -> None:
    manager = RequestQueue()
    try:
        manager.dequeue()
        obtained = "Ha devuelto una solicitud"
        ok = False
    except EmptyQueueError as error:
        obtained = f"EmptyQueueError ({error}). ¿Vacía? {manager.is_empty()}"
        ok = manager.is_empty()
    show_result(5, "Estructura vacía",
                "extraer de un gestor sin solicitudes",
                "Termina de forma controlada con EmptyQueueError",
                obtained, ok)


#PRUEBA 6: DATOS INCOMPLETOS O COORDENADAS MAL FORMADAS

def test_6_datos_incorrectos() -> None:
    cases = [
        ("6a", "Falta un campo obligatorio",
         {"request_id": "R-0006", "user": "Eva", "pickup": (4, 0)},
         InvalidDataError),
        ("6b", "Coordenada con un decimal",
         {"request_id": "R-0007", "user": "Eva", "pickup": (1.5, 2), "destination": (0, 4)},
         InvalidPositionError),
        ("6c", "Coordenada con un solo componente",
         {"request_id": "R-0008", "user": "Eva", "pickup": (2,), "destination": (0, 4)},
         InvalidPositionError),
    ]
    for number, name, data, expected_error in cases:
        manager = RequestQueue()
        try:
            manager.enqueue(data)
            obtained = "Se ha aceptado la solicitud"
            ok = False
        except (InvalidDataError, InvalidPositionError) as error:
            total = len(manager.list_all())
            obtained = f"{type(error).__name__} ({error}). Registradas: {total}"
            ok = isinstance(error, expected_error) and total == 0
        show_result(number, name, str(data),
                    f"Se rechaza con {expected_error.__name__} y no se registra",
                    obtained, ok)

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Tres casos en una lista. Cada caso tiene: número, nombre, los datos
#y el error que esperamos. El for los prueba uno a uno:
#   - Si la solicitud se acepta, la prueba FALLA.
#   - Si salta un error, comprueba que es el ESPERADO y que no se
#     ha registrado nada (0 solicitudes).
#type(error).__name__ escribe el nombre del error (p. ej. InvalidDataError).

##---------------------------------------------------------------------


#EJECUTAR TODAS LAS PRUEBAS

if __name__ == "__main__":
    print("=== PRUEBAS DEL GESTOR DE SOLICITUDES ===\n")
    test_1_registro_y_consulta()
    test_2_id_duplicado()
    test_3_consulta_inexistente()
    test_4_extracciones_fifo()
    test_5_estructura_vacia()
    test_6_datos_incorrectos()
    print(f"=== RESUMEN: {sum(results)} de {len(results)} pruebas correctas ===")

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Ejecuta las pruebas una tras otra. Cada prueba usa un gestor NUEVO,
#así ninguna depende de lo que hizo la anterior.
#sum(results) cuenta los True (las correctas) y len(results) el total.

##---------------------------------------------------------------------