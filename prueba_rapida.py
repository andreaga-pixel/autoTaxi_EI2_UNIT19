from autotaxi.mapa import cargar_mapa
from autotaxi.busqueda import buscar_ruta
from autotaxi.errors import InvalidPositionError

mapa01 = cargar_mapa("autotaxi/mapas/mapa_01.csv")
mapa09 = cargar_mapa("autotaxi/mapas/mapa_09.csv")

casos = [
    ("1. Ruta normal",        mapa01, (2, 2), (7, 2)),
    ("2. Sin ruta",           mapa09, (2, 2), (8, 2)),
    ("3. Origen = destino",   mapa01, (2, 2), (2, 2)),
    ("4. Fuera del mapa",     mapa01, (2, 2), (20, 2)),
    ("5. Destino en pared",   mapa01, (2, 2), (0, 0)),
]

for nombre, mapa, origen, destino in casos:
    print(nombre, "->", origen, "a", destino)
    try:
        ruta, explorados = buscar_ruta(mapa, origen, destino)
        if ruta:
            print("   Ruta:", ruta)
            print("   Longitud:", len(ruta) - 1, "| Nodos explorados:", explorados)
        else:
            print("   No existe ninguna ruta | Nodos explorados:", explorados)
    except InvalidPositionError as error:
        print("   Posición inválida:", error)
    print()