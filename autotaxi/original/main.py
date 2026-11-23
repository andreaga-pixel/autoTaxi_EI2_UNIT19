"""Búsqueda de un recorrido mediante la expansión de nodos.

Mapa de entrada: 0 = libre; 1 = obstáculo.
Marcas utilizadas durante la ejecución: 2 = visitado; 3 = inicio; 4 = destino.
Las posiciones se expresan como (fila, columna), con índices desde 0.
El nodo inicial tiene como predecesor el identificador -2.
"""


ARCHIVO_MAPA = "mapas/mapa_01.csv"
FILA_INICIO = 2
COLUMNA_INICIO = 2
FILA_DESTINO = 0
COLUMNA_DESTINO = 0

MOVIMIENTOS = (
    ("arriba", -1, 0),
    ("abajo", 1, 0),
    ("derecha", 0, 1),
    ("izquierda", 0, -1),
)


class Nodo:
    def __init__(self, fila, columna, identificador, predecesor):
        self.fila = fila
        self.columna = columna
        self.identificador = identificador
        self.predecesor = predecesor

    def mostrar(self):
        print(
            f"Posición: ({self.fila}, {self.columna}) | "
            f"Nodo: {self.identificador} | Anterior: {self.predecesor}"
        )


def mostrar_mapa():
    for fila in mapa:
        print(fila)


# Preparación del mapa y de los puntos de partida y llegada.
mapa = []
with open(ARCHIVO_MAPA) as archivo:
    for linea in archivo:
        mapa.append(linea.strip().split(","))

mapa[FILA_INICIO][COLUMNA_INICIO] = "3"
mapa[FILA_DESTINO][COLUMNA_DESTINO] = "4"
mostrar_mapa()

nodos = [Nodo(FILA_INICIO, COLUMNA_INICIO, 0, -2)]
destino_encontrado = False
predecesor_destino = -1


# Expansión de los nodos almacenados.
while not destino_encontrado: 
    print(f"\nNodos descubiertos: {len(nodos)}")

    for actual in nodos:
        actual.mostrar()

        for direccion, cambio_fila, cambio_columna in MOVIMIENTOS:
            fila_vecina = actual.fila + cambio_fila
            columna_vecina = actual.columna + cambio_columna
            contenido = mapa[fila_vecina][columna_vecina]

            if contenido == "4":
                print(f"Destino localizado hacia {direccion}.")
                predecesor_destino = actual.identificador
                destino_encontrado = True
                break

            elif contenido == "0":
                print(f"Explorando hacia {direccion}.")
                siguiente = Nodo(
                    fila_vecina,
                    columna_vecina,
                    len(nodos),
                    actual.identificador,
                )
                mapa[fila_vecina][columna_vecina] = "2"
                nodos.append(siguiente)

        if destino_encontrado:
            break

        mostrar_mapa()


# Consulta de los predecesores de la solución encontrada.
print("\nNodos del recorrido:")
recorrido_mostrado = False

while not recorrido_mostrado:
    for actual in nodos:
        if actual.identificador == predecesor_destino:
            actual.mostrar()
            predecesor_destino = actual.predecesor

            if predecesor_destino == -2:
                print("Fin del recorrido.")
                recorrido_mostrado = True
