#PRUEBAS DEL SISTEMA INTEGRADO (EI3)

#Las 6 pruebas que pide el enunciado (apartado 5) y una prueba extra con los 10 mapas.
#Mismo formato que pruebas.py de la EI2: entrada, esperado, obtenido y resultado.

import io
from contextlib import redirect_stdout

from autotaxi.request_queue import RequestQueue
from autotaxi.mapa import cargar_mapa, dentro_del_mapa, es_libre
from autotaxi.busqueda import buscar_ruta
from autotaxi.gestor import procesar_lote
from autotaxi.models import RequestStatus

MAPA_01 = cargar_mapa("autotaxi/mapas/mapa_01.csv")   #una pared con un hueco en (4, 3)
MAPA_09 = cargar_mapa("autotaxi/mapas/mapa_09.csv")   #dos zonas separadas por la fila 6

results = []


def show_result(number, name, entrada, expected, obtained, ok) -> None:
    print(f"PRUEBA {number}: {name}")
    print(f"  Entrada:   {entrada}")
    print(f"  Esperado:  {expected}")
    print(f"  Obtenido:  {obtained}")
    print(f"  Resultado: {'CORRECTO' if ok else 'FALLO'}")
    print()
    results.append(ok)


#CREAR UN GESTOR CON UN LOTE Y PROCESARLO SIN LLENAR LA PANTALLA

def procesar(lote: list[dict], mapa) -> tuple[RequestQueue, list, str]:
    manager = RequestQueue()                          #(1)
    for data in lote:
        manager.enqueue(data)
    salida = io.StringIO()                            #(2)
    with redirect_stdout(salida):                     #(3)
        atendidas = procesar_lote(manager, mapa)
    return manager, atendidas, salida.getvalue()     #(4)

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#   1. Crea un gestor nuevo y registra las solicitudes del lote. Cada prueba
#      usa un gestor nuevo, así ninguna depende de otra (igual que en la EI2).
#   2. Crea una "libreta" de texto vacía.
#   3. procesar_lote escribe en pantalla cada resultado. Con redirect_stdout,
#      ese texto se guarda en la libreta en lugar de mostrarse, para que las
#      pruebas se lean bien.
#   4. Devuelve el gestor, las solicitudes atendidas y el texto de la libreta
#      (así la prueba 6 puede comprobar el mensaje de "no hay solicitudes").

##---------------------------------------------------------------------


#COMPROBAR QUE UNA RUTA ES VÁLIDA

def comprobar_ruta(mapa, ruta, origen, destino) -> list[str]:
    problemas = []
    if not ruta:
        return ["la ruta está vacía"]
    if ruta[0] != origen:                                                    #(1)
        problemas.append("no empieza en el origen")
    if ruta[-1] != destino:
        problemas.append("no termina en el destino")
    for casilla in ruta:                                                     #(2)
        if not dentro_del_mapa(mapa, casilla) or not es_libre(mapa, casilla):
            problemas.append(f"{casilla} no es una casilla libre")
    for a, b in zip(ruta, ruta[1:]):                                         #(3)
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
            problemas.append(f"{a} -> {b} no es un movimiento entre vecinas")
    return problemas                                                         #(4)

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#El enunciado pide comprobar en cada ruta: los extremos, que las casillas son
#libres, que los movimientos son entre vecinas y la longitud.
#   1. Extremos: la primera casilla es el origen y la última el destino.
#   2. Todas las casillas están dentro del mapa y valen 0.
#   3. zip(ruta, ruta[1:]) forma parejas de casillas seguidas: (1ª,2ª), (2ª,3ª)...
#      En cada paso solo puede cambiar la fila o la columna, y en 1. Si la suma
#      de las diferencias no es 1, hay un salto o un movimiento en diagonal.
#   4. Devuelve la lista de problemas. Si está vacía, la ruta es válida.
#   (La longitud se comprueba en cada prueba: len(ruta) - 1.)

##---------------------------------------------------------------------


#PRUEBA 1: ORDENACIÓN CON LOTE DESORDENADO Y EMPATES

def test_1_ordenacion() -> None:
    lote = [
        {"request_id": "R-0001", "user": "Ana",  "pickup": (1, 1), "destination": (8, 6), "priority": 2},
        {"request_id": "R-0002", "user": "Luis", "pickup": (2, 2), "destination": (7, 2), "priority": 1},
        {"request_id": "R-0003", "user": "Eva",  "pickup": (3, 4), "destination": (6, 1), "priority": 2},
        {"request_id": "R-0004", "user": "Dani", "pickup": (1, 6), "destination": (5, 3), "priority": 1},
    ]
    manager, atendidas, _ = procesar(lote, MAPA_01)
    orden = [r.request_id for r in atendidas]
    registradas = len(manager.list_all())
    esperado = ["R-0002", "R-0004", "R-0001", "R-0003"]
    show_result(1, "Ordenación de un lote desordenado con empates",
                "R-0001(p2), R-0002(p1), R-0003(p2), R-0004(p1)",
                "Se atienden R-0002, R-0004, R-0001, R-0003 y se conservan las 4",
                f"Se atienden {', '.join(orden)} | registradas: {registradas}",
                orden == esperado and registradas == 4)

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Hay dos empates: R-0002 y R-0004 (prioridad 1) y R-0001 y R-0003 (prioridad 2).
#Se comprueba el orden en que el gestor ATIENDE las solicitudes (no solo la
#función de ordenar) y que las 4 siguen en el registro.

##---------------------------------------------------------------------


#PRUEBA 2: RUTA QUE RODEA UN OBSTÁCULO

def test_2_ruta_obstaculo() -> None:
    origen, destino = (2, 2), (7, 2)
    ruta, explorados = buscar_ruta(MAPA_01, origen, destino)
    problemas = comprobar_ruta(MAPA_01, ruta, origen, destino)
    longitud = len(ruta) - 1
    pasa_por_hueco = (4, 3) in ruta
    show_result(2, "Ruta que rodea un obstáculo",
                "mapa_01, origen (2, 2), destino (7, 2). Pared en la fila 4 con hueco en (4, 3)",
                "Ruta válida (extremos, casillas libres, vecinas) que pasa por (4, 3), longitud 7",
                f"Ruta: {ruta} | longitud: {longitud} | pasa por (4, 3): {pasa_por_hueco}"
                f" | problemas: {problemas if problemas else 'ninguno'}",
                not problemas and longitud == 7 and pasa_por_hueco)

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#La fila 4 del mapa_01 es una pared con un único hueco en la columna 3.
#Para ir de arriba abajo la ruta TIENE que pasar por (4, 3).
#La longitud mínima es 7: bajar 5 filas, más 1 columna para ir al hueco
#y otra para volver (5 + 1 + 1 = 7).

##---------------------------------------------------------------------


#PRUEBA 3: ORIGEN IGUAL A DESTINO

def test_3_origen_igual_destino() -> None:
    ruta, explorados = buscar_ruta(MAPA_01, (2, 2), (2, 2))
    show_result(3, "Origen igual a destino",
                "mapa_01, origen (2, 2), destino (2, 2)",
                "Una sola casilla libre, [(2, 2)], y longitud 0",
                f"Ruta: {ruta} | longitud: {len(ruta) - 1}",
                ruta == [(2, 2)] and len(ruta) - 1 == 0)


#PRUEBA 4: BÚSQUEDA SIN ÉXITO Y EL PROGRAMA CONTINÚA

def test_4_sin_exito_continua() -> None:
    lote = [
        {"request_id": "R-0001", "user": "Luis", "pickup": (2, 2), "destination": (8, 2)},   #sin ruta
        {"request_id": "R-0002", "user": "Ana",  "pickup": (8, 1), "destination": (8, 14)},  #con ruta
    ]
    manager, atendidas, _ = procesar(lote, MAPA_09)
    r1, r2 = manager.find("R-0001"), manager.find("R-0002")
    show_result(4, "Búsqueda sin éxito y el programa continúa",
                "mapa_09: R-0001 (2, 2)->(8, 2) en zonas separadas, después R-0002 (8, 1)->(8, 14)",
                "R-0001 UNRESOLVED con motivo; R-0002 se atiende igualmente (HANDLED)",
                f"R-0001: {r1.status.value} ({r1.result_note}) | R-0002: {r2.status.value},"
                f" longitud {r2.route_length} | pendientes: {len(manager.list_pending())}",
                r1.status == RequestStatus.UNRESOLVED and r2.status == RequestStatus.HANDLED
                and manager.is_empty())

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#No basta con ver que detecta que no hay ruta: se pone DETRÁS una solicitud
#válida para demostrar que el programa sigue y la atiende.

##---------------------------------------------------------------------


#PRUEBA 5: COORDENADA INVÁLIDA (FUERA DEL MAPA Y SOBRE UN OBSTÁCULO)

def test_5_coordenada_invalida() -> None:
    lote = [
        {"request_id": "R-0001", "user": "Hugo", "pickup": (2, 2), "destination": (20, 2)},  #fuera
        {"request_id": "R-0002", "user": "Eva",  "pickup": (0, 0), "destination": (7, 2)},   #pared
        {"request_id": "R-0003", "user": "Ana",  "pickup": (2, 2), "destination": (7, 2)},   #válida
    ]
    manager, atendidas, _ = procesar(lote, MAPA_01)
    r1, r2, r3 = manager.find("R-0001"), manager.find("R-0002"), manager.find("R-0003")
    show_result(5, "Coordenada inválida",
                "mapa_01: R-0001 destino (20, 2) fuera; R-0002 origen (0, 0) en pared; R-0003 válida",
                "R-0001 y R-0002 INVALID con su motivo; R-0003 se atiende (HANDLED)",
                f"R-0001: {r1.status.value} ({r1.result_note}) | R-0002: {r2.status.value}"
                f" ({r2.result_note}) | R-0003: {r3.status.value}",
                r1.status == RequestStatus.INVALID and "fuera del mapa" in r1.result_note
                and r2.status == RequestStatus.INVALID and "obstáculo" in r2.result_note
                and r3.status == RequestStatus.HANDLED)

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Cubre los dos tipos de posición inválida (fuera del mapa y sobre una pared)
#y, otra vez, una solicitud válida detrás para ver que el programa continúa.

##---------------------------------------------------------------------


#PRUEBA 6: LOTE VACÍO

def test_6_lote_vacio() -> None:
    manager, atendidas, salida = procesar([], MAPA_01)
    show_result(6, "Lote vacío",
                "gestor sin solicitudes",
                "Informa de que no hay solicitudes y termina sin errores",
                f"Mensaje: '{salida.strip()}' | atendidas: {len(atendidas)}",
                atendidas == [] and "No hay solicitudes" in salida)


#PRUEBA 7: LOS 10 MAPAS, DE UNA ESQUINA A LA OTRA

SIN_RUTA_ESPERADA = {"mapa_09", "mapa_10"}   #mapas con sectores separados (ver la imagen de los mapas)

def test_7_todos_los_mapas() -> None:
    for numero in range(1, 11):
        nombre = f"mapa_{numero:02d}"
        mapa = cargar_mapa(f"autotaxi/mapas/{nombre}.csv")
        libres = [(f, c) for f in range(len(mapa)) for c in range(len(mapa[0])) if mapa[f][c] == 0]   #(1)
        origen, destino = libres[0], libres[-1]                                                        #(2)
        ruta, explorados = buscar_ruta(mapa, origen, destino)
        if nombre in SIN_RUTA_ESPERADA:                                                                #(3)
            esperado = "Sin ruta: termina e informa, explorando solo su sector"
            obtenido = f"{'sin ruta' if not ruta else 'HAY RUTA'} | explorados {explorados} de {len(libres)} libres"
            ok = ruta == [] and explorados < len(libres)
        else:                                                                                          #(4)
            problemas = comprobar_ruta(mapa, ruta, origen, destino)
            esperado = "Ruta válida (extremos, casillas libres, vecinas)"
            obtenido = (f"longitud {len(ruta) - 1} | explorados {explorados} de {len(libres)} libres"
                        f" | problemas: {problemas if problemas else 'ninguno'}")
            ok = bool(ruta) and not problemas
        show_result(f"7-{numero:02d}", f"{nombre} ({len(mapa)} x {len(mapa[0])})",
                    f"origen {origen}, destino {destino}", esperado, obtenido, ok)

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Prueba la búsqueda en los 10 mapas del profesor, no solo en los de las otras pruebas.
#   1. Hace una lista con todas las casillas libres, recorriendo el mapa fila a
#      fila, de arriba abajo y de izquierda a derecha.
#   2. El origen es la PRIMERA casilla libre (arriba a la izquierda) y el destino
#      la ÚLTIMA (abajo a la derecha). Así la ruta cruza todo el mapa.
#   3. En mapa_09 y mapa_10 (sectores separados) se espera que NO haya ruta:
#      debe terminar y haber explorado menos casillas que las libres del mapa,
#      porque solo puede recorrer el sector del origen.
#   4. En el resto se espera una ruta válida, comprobada con comprobar_ruta.

##---------------------------------------------------------------------


#EJECUTAR TODAS LAS PRUEBAS

if __name__ == "__main__":
    print("=== PRUEBAS DEL SISTEMA INTEGRADO (EI3) ===\n")
    test_1_ordenacion()
    test_2_ruta_obstaculo()
    test_3_origen_igual_destino()
    test_4_sin_exito_continua()
    test_5_coordenada_invalida()
    test_6_lote_vacio()
    test_7_todos_los_mapas()
    print(f"=== RESUMEN: {sum(results)} de {len(results)} pruebas correctas ===")