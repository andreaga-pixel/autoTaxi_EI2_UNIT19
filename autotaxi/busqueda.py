#BÚSQUEDA DE RUTAS (EI3) · ADAPTACIÓN DEL ALGORITMO DEL PROFESOR

##Parte del código original (original/main.py): búsqueda en anchura (BFS)
#que expande los nodos en el orden en que se descubren.
#Cambios respecto al original:
#   - Recibe el mapa, el origen y el destino como PARÁMETROS (antes estaban fijos).
#   - DEVUELVE la ruta completa, del origen al destino (antes solo la imprimía, al revés).
#   - TERMINA si no hay ruta (antes: bucle infinito).
#   - Origen = destino devuelve una ruta de longitud 0 (antes: ida y vuelta de 2).
#   - Comprueba que origen y destino están dentro del mapa y libres (antes: IndexError
#     o escribía encima de la pared).
#   - Apunta las casillas visitadas en un conjunto aparte, sin modificar el mapa.
#   - Cuenta los nodos explorados, para medir el trabajo.

from .errors import InvalidPositionError
from .mapa import dentro_del_mapa, es_libre
from .models import position

MOVIMIENTOS = (
    ("arriba", -1, 0),
    ("abajo", 1, 0),
    ("derecha", 0, 1),
    ("izquierda", 0, -1),
)


#EL NODO (igual que en el original, sin el método de imprimir)

class Nodo:
    def __init__(self, fila, columna, identificador, predecesor):
        self.fila = fila
        self.columna = columna
        self.identificador = identificador  #posición del nodo en la lista "nodos"
        self.predecesor = predecesor        #identificador del nodo del que viene (-2 = origen)


#COMPROBAR UNA POSICIÓN ANTES DE BUSCAR

def validar_posicion(mapa: list[list[int]], pos: position, nombre: str) -> None:
    if not dentro_del_mapa(mapa, pos):                                   #(1)
        raise InvalidPositionError(f"El {nombre} {pos} está fuera del mapa")
    if not es_libre(mapa, pos):                                          #(2)
        raise InvalidPositionError(f"El {nombre} {pos} está sobre un obstáculo")

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#   1. Si la posición no existe en el mapa -> error (arregla la prueba 4 del original).
#   2. Si existe pero es pared -> error (arregla la prueba 5 del original).
#"nombre" es "origen" o "destino", para que el mensaje diga cuál está mal.

##---------------------------------------------------------------------


#RECONSTRUIR LA RUTA SIGUIENDO LOS PREDECESORES

def reconstruir_ruta(nodos: list[Nodo], identificador: int) -> list[position]:
    ruta = []
    while identificador != -2:                                           #(1)
        nodo = nodos[identificador]                                      #(2)
        ruta.append((nodo.fila, nodo.columna))
        identificador = nodo.predecesor                                  #(3)
    ruta.reverse()                                                       #(4)
    return ruta

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Empieza en el destino y va "hacia atrás" siguiendo las migas de pan.
#   1. Sigue hasta llegar al origen, que tiene como predecesor -2.
#   2. El identificador de cada nodo es su posición en la lista, así que se
#      accede DIRECTAMENTE con nodos[identificador], sin recorrer la lista.
#      (El original recorría toda la lista buscando cada predecesor.)
#   3. Pasa al nodo anterior.
#   4. La ruta se ha construido del destino al origen: se le da la vuelta.
#Coste: O(L), con L = número de casillas de la ruta.

##---------------------------------------------------------------------


#BUSCAR LA RUTA

def buscar_ruta(mapa: list[list[int]], origen: position, destino: position) -> tuple[list[position], int]:
    validar_posicion(mapa, origen, "origen")                             #(1)
    validar_posicion(mapa, destino, "destino")

    if origen == destino:                                                #(2)
        return [origen], 0

    nodos = [Nodo(origen[0], origen[1], 0, -2)]                          #(3)
    visitados = {origen}                                                 #(4)
    siguiente = 0                                                        #(5)

    while siguiente < len(nodos):                                        #(6)
        actual = nodos[siguiente]
        for direccion, cambio_fila, cambio_columna in MOVIMIENTOS:       #(7)
            vecina = (actual.fila + cambio_fila, actual.columna + cambio_columna)
            if not dentro_del_mapa(mapa, vecina) or not es_libre(mapa, vecina):
                continue                                                 #pared o fuera del mapa
            if vecina in visitados:
                continue                                                 #ya descubierta
            nuevo = Nodo(vecina[0], vecina[1], len(nodos), actual.identificador)
            nodos.append(nuevo)
            visitados.add(vecina)
            if vecina == destino:                                        #(8)
                return reconstruir_ruta(nodos, nuevo.identificador), siguiente + 1
        siguiente += 1

    return [], siguiente                                                 #(9)

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Devuelve dos cosas: (ruta, nodos_explorados).
#   1. Antes de buscar, comprueba origen y destino. Si alguno está mal,
#      lanza InvalidPositionError y NO se busca.
#   2. Si origen y destino son la misma casilla, la ruta es solo esa casilla
#      (longitud 0) y no hace falta explorar nada. Arregla la prueba 3.
#   3. La lista de nodos empieza con el origen (identificador 0, predecesor -2),
#      igual que en el original.
#   4. "visitados" es un conjunto (set) con las casillas ya descubiertas.
#      El original las marcaba escribiendo un 2 en el mapa; aquí el mapa
#      NO se modifica, así que se puede usar para la siguiente solicitud.
#   5. "siguiente" es el número del próximo nodo a expandir. La lista "nodos"
#      funciona como una COLA: los nodos se añaden al final y se expanden
#      en orden desde el principio (FIFO). Eso es lo que hace que sea BFS.
#   6. Sigue mientras queden nodos por expandir. Cuando "siguiente" llega al
#      final de la lista, ya se han mirado todas las casillas alcanzables:
#      el bucle TERMINA. Arregla el bucle infinito de las pruebas 2 y 5.
#   7. Mira las 4 vecinas en el mismo orden que el original. Si es pared,
#      está fuera del mapa o ya se ha visitado, la salta.
#   8. En cuanto descubre el destino, reconstruye la ruta y la devuelve.
#      Como BFS avanza "por ondas", la primera vez que llega es por el camino
#      con MENOS movimientos (Rodriguez, 2026, Sesión 9).
#   9. Si sale del bucle sin encontrarlo, devuelve una ruta vacía: ahora SÍ
#      se puede afirmar que NO existe ninguna ruta, porque se ha explorado
#      todo lo alcanzable desde el origen.
#nodos_explorados = cuántos nodos se han expandido (sacado de la cola). Sirve
#para medir el trabajo realizado.

##---------------------------------------------------------------------