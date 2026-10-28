#LA RECEPCIONISTA QUE REVISA LOS DATOS ANTES DE ACEPTAR LA SOLICITUD

##Comprobaciones de los datos antes de registrar una solicitud.

#Solo se comprueba el FORMATO de las coordenadas. La comprobación
#contra el mapa se añadirá cuando se integre la búsqueda de rutas.


#Importaciones
#traigo los dos errores que va a lanzar este archivo y el apodo position


from .errors import InvalidDataError, InvalidPositionError
from .models import position

#lista de campos obligatorios
#Estos son los 4 datos que SIEMPRE deben tener una solicitud
#Va en MAYUSCULAS porque es una constante
REQUIRED_FIELDS = ("request_id", "user", "pickup", "destination")

#REVISAR CAMPOS OBLIGATORIOS

def check_required_fields(data) -> None:
    if not isinstance(data, dict):#primera comprobación (1)
        raise InvalidDataError("Los datos de la solicitud deben ser un diccionario")
    for name in REQUIRED_FIELDS: #mira si no estan los campos obli. (2.1)
        if name not in data or data[name] is None: #(2.2)
            raise InvalidDataError(f"Falta el campo obligatorio '{name}'") #(2.3)

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Las solicitudes llegarán como un dict con sus datos

#{"request_id": "R-0001", "user": "Ana", "pickup": (0, 1), "destination": (2, 3)}

#Esta función hace dos comprobaciones:
#   1. ¿es un dict? si no, error
#   2. ¿estan todos los campos obligatorios?
#       2.1 Recorre la lista con un for y para cada campo mira si no esta.
#       2.2 Mira si está vacio
#       2.3 Si pasa alguna de estas dos cosas -> ERROR

##---------------------------------------------------------------------


#VALIDAR LOS IDENTIFICADORES
#El ID debe ser R- seguido de números (por ejemplo, R-0001).

def validate_id(value) -> str:
    if not isinstance(value, str):#(1)
        raise InvalidDataError("El identificador debe ser un texto")
    value = value.strip().upper() #(2)
    number = value[2:] #(3)
    if not value.startswith("R-") or not (number.isascii() and number.isdigit()):
        raise InvalidDataError(f"Identificador '{value}' no válido: formato esperado R-0001")
    return value

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Esta función hace tres comprobaciones:
#   1. ¿es un texto? si no, error (se comprueba con una funcion de Python isinstance)
#   2. Lo limpia: quita los espacios (strip) y lo pasa a mayusculas (upper). 
#      Así "r-0001" -> "R-0001".
#   3. ¿Empieza por r- y lo demás son solo num?
#       Con value[2:] coge todo lo que va despues de las dos primeras letras ("0001")

##---------------------------------------------------------------------

##VALIDACIÓN DEL USUARIO
#El usuario debe ser texto no vacio

def validate_user(value) -> str:
    
    if not isinstance(value, str) or not value.strip():
        raise InvalidDataError("El usuario no puede estar vacío")
    return value.strip()

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Error si no es texto, o si al quitar los espacios queda vacío. 
#Se recharan "" y " ". 
# Si está bien, devuelve el nombre sin espacios sobrantes

##---------------------------------------------------------------------

#VALIDAR LA POSICION
#La posición debe ser (fila, columna) con dos enteros mayores o iguales que 0.

def validate_position(value) -> position:
    
    if not isinstance(value, (tuple, list)) or len(value) != 2: #(1)
        raise InvalidPositionError(f"La posición debe tener la forma (fila, columna): {value!r}")
    for coord in value: 
        if type(coord) is not int: #(2)
            raise InvalidPositionError(f"Las coordenadas deben ser enteros: {value!r}")
        if coord < 0: #(3)
            raise InvalidPositionError(f"Las coordenadas no pueden ser negativas: {value!r}")
    return (value[0], value[1])

##----------------------------------------------------
##              EXPLICACIÓN LÓGICA
##------------------------------------------------------
#Esta función hace tres comprobaciones:
#   1. ¿es una pareja? Tiene que se una tupla o una lista con exactamente 2 elem. 
#   2. ¿Cada num es entero? Type(coord)..... rechaza decimales como 1.5, textos xomo "a" y tambien True. 
#   3. ¿Es mayor o igual que 0? Las filas y columnas empiezan en 0

##---------------------------------------------------------------------

##TODAS LAS FUNCIONES SIGUEN UNA LÓGICA COMÚN
##¿Está mal?  -> raise (lanzar el error) y PARAR
##¿Está bien? -> return (devolver el dato limpio)