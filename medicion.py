#MEDICIONES DE EFICIENCIA (EI3)
#Se ejecuta con: python medicion.py
#   Parte A (M2 y P7): inserción frente a MergeSort con los mismos lotes.
#   Parte B (P7): tiempo y memoria de la búsqueda en mapas de distinto tamaño.
#Se mide SOLO el algoritmo: crear los datos, copiarlos y mostrar resultados
#queda fuera del tiempo medido.

import platform
import random
import statistics
import time
import tracemalloc

from autotaxi.models import Request
from autotaxi.ordenacion import insercion, clave_prioridad
from autotaxi.mapa import cargar_mapa
from autotaxi.busqueda import buscar_ruta

REPETICIONES = 5
TAMANOS = [10, 100, 1000]
random.seed(19)   #semilla fija: cada ejecución genera los mismos lotes (reproducible)


#MERGESORT DE LA SESIÓN 8 (REFERENCIA PARA COMPARAR, NO SE USA EN EL GESTOR)

def merge_sort(A, clave, contador):
    if len(A) <= 1:
        return A[:]
    mitad = len(A) // 2
    izquierda = merge_sort(A[:mitad], clave, contador)
    derecha = merge_sort(A[mitad:], clave, contador)
    return mezclar(izquierda, derecha, clave, contador)


def mezclar(L, R, clave, contador):
    salida = []
    i = j = 0
    while i < len(L) and j < len(R):
        contador[0] += 1                      #una comparación de claves
        if clave(L[i]) <= clave(R[j]):
            salida.append(L[i])
            i += 1
        else:
            salida.append(R[j])
            j += 1
    salida.extend(L[i:])
    salida.extend(R[j:])
    return salida

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Es el código de MergeSort de la Sesión 8 (Rodriguez, 2026) con un único
#cambio: "contador" es una lista de un elemento donde se suman las
#comparaciones, para poder compararlas con las de la inserción.
#Se usa una lista y no un número porque así todas las llamadas recursivas
#suman en el mismo sitio.

##---------------------------------------------------------------------


#CREAR UN LOTE DE PRUEBA

def crear_lote(n: int, tipo: str) -> list[Request]:
    lote = []
    for i in range(n):
        if tipo == "ordenado":
            prioridad = 0                      #todas iguales -> ya está en orden de llegada
        elif tipo == "inverso":
            prioridad = n - i                  #cada una más urgente que la anterior -> al revés
        else:
            prioridad = random.randint(0, 3)   #prioridades al azar
        lote.append(Request(f"R-{i:04d}", "Usuario", (1, 1), (2, 2),
                            priority=prioridad, arrival_order=i + 1))
    return lote

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Crea n solicitudes directamente (sin pasar por la cola, porque aquí solo se
#mide la ordenación). El número de llegada va de 1 a n. Tres tipos de lote:
#   ordenado: todas con prioridad 0 -> ya están en su orden (mejor caso de la inserción).
#   inverso:  la prioridad baja en cada solicitud -> el lote está al revés (peor caso).
#   aleatorio: prioridades entre 0 y 3 al azar, como en un caso real con empates.

##---------------------------------------------------------------------


#MEDIR UN ALGORITMO DE ORDENACIÓN

def medir_ordenacion(algoritmo: str, lote: list) -> tuple[float, int, int, list]:
    tiempos = []
    for _ in range(REPETICIONES):                                   #(1)
        copia = lote[:]                                             #(2)
        contador = [0]
        inicio = time.perf_counter()                                #(3)
        if algoritmo == "insercion":
            comparaciones = insercion(copia, clave_prioridad)
            resultado = copia
        else:
            resultado = merge_sort(copia, clave_prioridad, contador)
            comparaciones = contador[0]
        tiempos.append(time.perf_counter() - inicio)

    copia = lote[:]                                                 #(4)
    tracemalloc.start()
    if algoritmo == "insercion":
        insercion(copia, clave_prioridad)
    else:
        merge_sort(copia, clave_prioridad, [0])
    memoria = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return statistics.median(tiempos) * 1000, comparaciones, memoria, resultado   #(5)

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#   1. Repite la medición varias veces (REPETICIONES), porque un solo tiempo
#      puede salir alterado por otras tareas del ordenador.
#   2. Cada repetición ordena una COPIA nueva del mismo lote: así los dos
#      algoritmos reciben exactamente los mismos datos, y la copia no cuenta
#      en el tiempo porque se hace antes de empezar a medir.
#   3. perf_counter mide el tiempo justo antes y justo después de ordenar.
#   4. La memoria se mide aparte (medirla a la vez haría el tiempo más lento):
#      tracemalloc dice el máximo de memoria EXTRA que ha usado el algoritmo.
#   5. Devuelve la MEDIANA de los tiempos en milisegundos (el valor del medio,
#      que no se deja engañar por una repetición rara), las comparaciones,
#      la memoria en bytes y el resultado para comprobar que es correcto.

##---------------------------------------------------------------------


#PARTE A: INSERCIÓN FRENTE A MERGESORT

def parte_a() -> None:
    print("PARTE A · INSERCIÓN FRENTE A MERGESORT (mismos lotes, misma clave)")
    print(f"{'n':>5} {'Lote':<10} {'Algoritmo':<10} {'Tiempo (ms)':>12} {'Comparac.':>10}"
          f" {'Memoria extra':>14} {'Correcto':>9}")
    for n in TAMANOS:
        for tipo in ["ordenado", "aleatorio", "inverso"]:
            lote = crear_lote(n, tipo)
            referencia = sorted(lote, key=clave_prioridad)            #solo para COMPROBAR
            for algoritmo in ["insercion", "mergesort"]:
                ms, comp, mem, resultado = medir_ordenacion(algoritmo, lote)
                correcto = [r.request_id for r in resultado] == [r.request_id for r in referencia]
                print(f"{n:>5} {tipo:<10} {algoritmo:<10} {ms:>12.3f} {comp:>10}"
                      f" {mem:>11} B {'Sí' if correcto else 'NO':>9}")
        print()


#PARTE B: TIEMPO Y MEMORIA DE LA BÚSQUEDA

def parte_b() -> None:
    print("PARTE B · BÚSQUEDA DE ESQUINA A ESQUINA EN MAPAS DE DISTINTO TAMAÑO")
    print(f"{'Mapa':<8} {'Tamaño':>8} {'Libres (V)':>10} {'Explorados':>11} {'Longitud':>9}"
          f" {'Tiempo (ms)':>12} {'Memoria extra':>14}")
    for numero in [1, 4, 7, 8]:
        mapa = cargar_mapa(f"autotaxi/mapas/mapa_{numero:02d}.csv")
        libres = [(f, c) for f in range(len(mapa)) for c in range(len(mapa[0])) if mapa[f][c] == 0]
        origen, destino = libres[0], libres[-1]
        tiempos = []
        for _ in range(REPETICIONES):
            inicio = time.perf_counter()
            ruta, explorados = buscar_ruta(mapa, origen, destino)
            tiempos.append(time.perf_counter() - inicio)
        tracemalloc.start()
        buscar_ruta(mapa, origen, destino)
        memoria = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        print(f"{'mapa_' + format(numero, '02d'):<8} {len(mapa)}x{len(mapa[0]):<5} {len(libres):>10}"
              f" {explorados:>11} {len(ruta) - 1:>9} {statistics.median(tiempos) * 1000:>12.3f}"
              f" {memoria:>11} B")
    print()

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Busca la ruta de la primera a la última casilla libre (como en la prueba 7)
#en 4 mapas cada vez más grandes. Mide el tiempo (mediana de 5 repeticiones)
#y la memoria extra (con tracemalloc), y muestra las casillas libres (V) y los
#nodos explorados para relacionar el tiempo con el análisis O(V).

##---------------------------------------------------------------------


if __name__ == "__main__":
    print("=== MEDICIONES DE EFICIENCIA (EI3) ===")
    print(f"Entorno: Python {platform.python_version()} · {platform.system()} {platform.release()}"
          f" · {platform.processor() or platform.machine()}")
    print(f"Repeticiones por caso: {REPETICIONES} (se muestra la mediana)\n")
    parte_a()
    parte_b()