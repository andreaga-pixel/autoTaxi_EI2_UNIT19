#DEMOSTRACIÓN INTEGRADA DE LA EI3
#Se ejecuta con: python demo_ei3.py
#Registra un lote desordenado, lo ordena por prioridad y llegada,
#y atiende cada solicitud buscando su ruta en el mapa_09.

from autotaxi.request_queue import RequestQueue
from autotaxi.mapa import cargar_mapa
from autotaxi.gestor import procesar_lote

MAPA = "autotaxi/mapas/mapa_09.csv"

LOTE = [
    {"request_id": "R-0001", "user": "Ana",   "pickup": (1, 1), "destination": (5, 14), "priority": 2},
    {"request_id": "R-0002", "user": "Luis",  "pickup": (2, 2), "destination": (8, 2),  "priority": 1},
    {"request_id": "R-0003", "user": "Marta", "pickup": (8, 1), "destination": (8, 14), "priority": 2},
    {"request_id": "R-0004", "user": "Dani",  "pickup": (4, 4), "destination": (4, 4),  "priority": 1},
    {"request_id": "R-0005", "user": "Eva",   "pickup": (2, 7), "destination": (1, 1),  "priority": 3},
    {"request_id": "R-0006", "user": "Hugo",  "pickup": (1, 1), "destination": (15, 3), "priority": 3},
]


def main() -> None:
    mapa = cargar_mapa(MAPA)
    manager = RequestQueue()
    for data in LOTE:
        manager.enqueue(data)

    print("=== PROCESAMIENTO DEL LOTE ===\n")
    procesar_lote(manager, mapa)

    print("=== REGISTRO FINAL (se conservan todas las solicitudes) ===")
    for r in manager.list_all():
        print(f"   {r.request_id}  {r.status.value:<11} longitud: {r.route_length}")
    print(f"Pendientes: {len(manager.list_pending())} | ¿Vacía? {manager.is_empty()}")


if __name__ == "__main__":
    main()

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#El lote tiene a propósito un caso de cada tipo (mapa_09: dos zonas separadas
#por la fila 6):
#   R-0001: ruta normal que rodea el obstáculo de arriba.
#   R-0002: origen arriba y destino abajo -> no hay ruta (NO RESUELTA).
#   R-0003: ruta en la zona de abajo que rodea la pared de la columna 10.
#   R-0004: origen = destino -> longitud 0.
#   R-0005: origen sobre un obstáculo -> INVÁLIDA.
#   R-0006: destino fuera del mapa -> INVÁLIDA.
#Llegan desordenadas por prioridad, así que también se ve la ordenación.

##---------------------------------------------------------------------