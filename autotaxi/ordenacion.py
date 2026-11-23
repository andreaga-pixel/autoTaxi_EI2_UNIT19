#ORDENACIÓN DEL LOTE DE SOLICITUDES 

#Algoritmo de ordenación implementado a mano: INSERCIÓN.
#No se usa sorted() ni .sort() para ordenar. Solo se usan en las pruebas para COMPROBAR que el resultado es correcto.
#Basado en el algoritmo de inserción de la Sesión 8 (Rodriguez, 2026),
#adaptado a las solicitudes de AutoTaxi y con un contador de comparaciones.

from .models import Request


#LA CLAVE DE ORDENACIÓN (la política de servicio)

def clave_prioridad(request: Request) -> tuple[int, int]:
    return (request.priority, request.arrival_order)

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#La clave dice QUÉ se compara de cada solicitud. Devuelve una pareja: (prioridad, número de llegada)

#Python compara las parejas como un diccionario compara palabras:
#   - primero mira la prioridad: la más BAJA va antes.
#   - solo si las prioridades empatan, mira la llegada: la que llegó ANTES va antes.

#Ejemplos:
#   (1, 4) va antes que (2, 1) -> gana la prioridad 1, la llegada ni se mira.
#   (2, 1) va antes que (2, 3) -> empatan en prioridad 2, decide la llegada.

#Como dos solicitudes nunca tienen el mismo número de llegada, nunca hay
#un empate completo: el resultado es siempre el mismo (reproducible).

##---------------------------------------------------------------------


#ORDENACIÓN POR INSERCIÓN

def insercion(lista: list, clave=clave_prioridad) -> int:
    comparaciones = 0                                       #(1)
    for i in range(1, len(lista)):                          #(2)
        actual = lista[i]                                   #(3)
        clave_actual = clave(actual)
        j = i - 1
        while j >= 0:                                       #(4)
            comparaciones += 1
            if clave(lista[j]) > clave_actual:              #(5)
                lista[j + 1] = lista[j]
                j -= 1
            else:
                break                                       #(6)
        lista[j + 1] = actual                               #(7)
    return comparaciones                                    #(8)

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Funciona como ordenar cartas en la mano: la parte de la izquierda ya está ordenada 
# y cada carta nueva se mete en su sitio dentro de esa parte.

#   1. Contador de comparaciones. No hace falta para ordenar, pero sirve
#      para medir cuánto trabajo hace el algoritmo.
#   2. Empieza en la posición 1: un solo elemento ya está ordenado.
#   3. "actual" es la carta que vamos a colocar. Se guarda porque su hueco
#      se va a pisar al desplazar las demás. j empieza justo a su izquierda.
#   4. Recorre hacia atrás la parte ya ordenada.
#   5. Si la de la izquierda tiene una clave MAYOR, debe ir detrás:
#      se desplaza un sitio a la derecha y seguimos mirando a la izquierda.
#   6. Si NO es mayor, paramos: hemos encontrado el sitio.
#      Usar ">" (y no ">=") hace que la inserción sea ESTABLE: si dos
#      claves empatan, no se adelantan y se conserva su orden.
#   7. Se coloca "actual" en el hueco que ha quedado.
#   8. Devuelve cuántas comparaciones ha hecho. La lista se ordena "en el
#      sitio" (no se crea otra lista), por eso la memoria extra es O(1).
#
#Diferencia con la Sesión 8: allí la condición es
#"while j >= 0 and clave(A[j]) > clave(actual)". Aquí está separada en
#if/else solo para poder contar cada comparación.
#
#COSTE (n = número de solicitudes del lote):
#   Mejor caso (ya ordenado): 1 comparación por solicitud -> n-1 -> O(n)
#   Peor caso (al revés): 1+2+...+(n-1) = n(n-1)/2 comparaciones -> O(n²)
#   Memoria extra: solo actual, clave_actual, i, j -> O(1)

##---------------------------------------------------------------------