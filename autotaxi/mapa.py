#EL MAPA DE AutoTaxi

##Carga un mapa desde un archivo CSV y responde a dos preguntas:
#   ¿esta posición está dentro del mapa?  -> dentro_del_mapa
#   ¿esta casilla está libre (vale 0)?    -> es_libre
#Son las operaciones in_bounds e is_traversable que especifiqué en la EI1.

from .errors import InvalidDataError, InvalidPositionError
from .models import position


#CARGAR UN MAPA DESDE UN CSV

def cargar_mapa(ruta_archivo: str) -> list[list[int]]:
    mapa = []
    with open(ruta_archivo) as archivo:                          #(1)
        for linea in archivo:
            linea = linea.strip()
            if linea == "":                                      #(2)
                continue
            fila = []
            for valor in linea.split(","):                       #(3)
                if valor not in ("0", "1"):
                    raise InvalidDataError(f"El mapa solo puede tener 0 y 1: {valor!r}")
                fila.append(int(valor))
            mapa.append(fila)
    if not mapa:                                                 #(4)
        raise InvalidDataError("El mapa está vacío")
    for fila in mapa:                                            #(5)
        if len(fila) != len(mapa[0]):
            raise InvalidDataError("El mapa no es rectangular")
    return mapa

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#   1. Abre el archivo y lo lee línea a línea (igual que el código del profesor).
#   2. Se salta las líneas vacías (por ejemplo, la última línea del CSV).
#   3. Separa cada línea por comas y convierte cada valor en un número entero.
#      Si aparece algo que no sea 0 o 1 -> InvalidDataError.
#      Diferencia con el original: allí las casillas se guardaban como TEXTO
#      ('0', '1'). Aquí se guardan como NÚMEROS (0, 1), como dice el enunciado.
#   4. Si el archivo no tenía ninguna fila -> InvalidDataError.
#   5. Todas las filas deben tener la misma longitud (el mapa es rectangular).

##---------------------------------------------------------------------


#¿ESTÁ DENTRO DEL MAPA? (in_bounds de la EI1)

def dentro_del_mapa(mapa: list[list[int]], pos: position) -> bool:
    fila, columna = pos
    return 0 <= fila < len(mapa) and 0 <= columna < len(mapa[0])


#¿ESTÁ LIBRE LA CASILLA? (is_traversable de la EI1)

def es_libre(mapa: list[list[int]], pos: position) -> bool:
    if not dentro_del_mapa(mapa, pos):                           #(1)
        raise InvalidPositionError(f"La posición {pos} está fuera del mapa")
    fila, columna = pos
    return mapa[fila][columna] == 0                              #(2)

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#dentro_del_mapa: la fila tiene que estar entre 0 y el número de filas - 1,
#y la columna entre 0 y el número de columnas - 1. Devuelve True o False.
#
#es_libre:
#   1. PRIMERO comprueba que la posición está dentro del mapa. Si no lo está,
#      mirar la casilla daría IndexError (el fallo de la prueba 4 del original).
#   2. Solo después mira la casilla: True si vale 0 (libre), False si vale 1.
#Es el orden que fijé en la EI1: primero límites, después contenido.
#Coste de las dos: O(1), solo hacen comparaciones y un acceso por índice.

##---------------------------------------------------------------------