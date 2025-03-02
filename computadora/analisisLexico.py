import src.ply.lex as lex
from utils.programas import programa_minimo  # Importa string de un programa prueba

# ------------------------------------------------------------
# DEFINICIONES REGULARES Y EXTENSIONES REGULARES
# ------------------------------------------------------------

# Números
digito = r"[0-9]"
digito_parte_flotante = r"\." + digito + r"+"
digito_parte_exponente = r"[eE][+-]?" + digito + r"+"

# Letras
letra = r"[a-zA-ZáéíóúÁÉÍÓÚ_]"
string = r"\'.*?\'"

# Extensiones compuestas
identificador = letra + r"(" + letra + r"|" + digito + r")*"

# Números con flotante y notación científica opcionales
numero_flotante_opcional = (
    digito
    + r"+("
    + digito_parte_flotante
    + r")?"
    + r"("
    + digito_parte_exponente
    + r")?"
)

# Declaracion de constantes
constante = (
    r"const\s*"
    + identificador
    + r"\s*"
    + r"("
    + numero_flotante_opcional
    + r"|"
    + string
    + r"+)"
)

# ------------------------------------------------------------
# DEFINICIÓN DE TOKENS
# ------------------------------------------------------------

# Palabras reservadas
palabrasReservadas = {
    # Estructuras de control
    "si": "SI",
    "sino": "SINO",
    "mientras": "MIENTRAS",
    "funcion": "FUNCION",
    "para": "PARA",
    # Valores de verdad
    "verdadero": "VERDADERO",
    "falso": "FALSO",
    # Operadores lógicos
    "y": "Y",
    "o": "O",
    "no": "NO",
    # Otros
    "const": "CONST",
    "retornar": "RETORNAR",
    "importar": "IMPORTAR",
}

# Lista de nombres de tokens
tokens = (
    # Palabras reservadas
    *palabrasReservadas.values(),
    # # Ejecutar librerias precompiladas
    # "EJECUTAR_POSICION",
    # Operadores relacionales
    "IGUALDAD",
    "DIFERENTE",
    "MAYOR",
    "MENOR",
    "MAYOR_IGUAL",
    "MENOR_IGUAL",
    # Operadores aritméticos
    "SUMA",
    "RESTA",
    "MULTIPLICACION",
    "DIVISION",
    "DIVISION_ENTERA",
    # Operador de asignación
    "ASIGNACION",
    # Delimitadores
    "PARENTESIS_IZQUIERDO",
    "PARENTESIS_DERECHO",
    # Literales e identificadores
    "NUMERO",
    "STRING",
    "BOOLEANO",
    "ID",
    # Comentarios
    "COMENTARIO",
    # Espacios y tabulaciones
    "NUEVA_LINEA",
    "INDENTACION",
    "ESPACIO",
)

# ------------------------------------------------------------
# ESTADO GLOBAL
# ------------------------------------------------------------

# Diccionario de constantes
constantes = {}

# ------------------------------------------------------------
# REGLAS PARA RECONOCER TOKENS
# ------------------------------------------------------------


# Palabras reservadas
# Regla para importar librerías
def t_IMPORTAR(t):
    r"importar\s*\'.*?\'"
    return t


# # Regla para ejecutar librerías precompiladas
# def t_EJECUTAR_POSICION(t):
#     r"!EJECUTAR_POSICION:[0-9]+"
#     t.value = int(t.value.split(":")[1])
#     return t


# Regla para las constantes
@lex.TOKEN(constante)
def t_CONST(t):
    # Separar el nombre de la constante y su valor
    parts = t.value.split(maxsplit=2)
    const, nombre, valor = parts[0], parts[1], parts[2]
    # Eliminar espacios en blanco
    nombre = nombre.strip()
    valor = valor.strip()
    # Agregar la constante al diccionario
    global constantes
    # Verificar si la constante ya existe
    if nombre in constantes:
        print(f"Error: la constante '{nombre}' ya ha sido declarada")
        t.lexer.skip(1)
        return
    constantes[nombre] = valor
    return t


# Operadores relacionales
t_IGUALDAD = r"=="
t_DIFERENTE = r"!="
t_MAYOR = r">"
t_MENOR = r"<"
t_MAYOR_IGUAL = r">="
t_MENOR_IGUAL = r"<="

# Operadores aritméticos
t_SUMA = r"\+"
t_RESTA = r"-"
t_MULTIPLICACION = r"\*"
t_DIVISION = r"/"
t_DIVISION_ENTERA = r"//"

# Asignación
t_ASIGNACION = r"="

# Delimitadores
t_PARENTESIS_IZQUIERDO = r"\("
t_PARENTESIS_DERECHO = r"\)"

# Literales e identificadores


# Regla para números con flotante y notacion científica opcionales
@lex.TOKEN(numero_flotante_opcional)
def t_NUMERO(t):
    return t


t_STRING = string
t_BOOLEANO = r"verdadero|falso"


# Regla para identificadores y palabras reservadas
@lex.TOKEN(identificador)
def t_ID(t):
    t.type = palabrasReservadas.get(
        t.value, "ID"
    )  # Verificar si es una palabra reservada
    # verificar si esta en el diccionario de constantes y reemplazar
    if t.value in constantes:
        t.value = constantes[t.value]
    return t


# Comentarios
t_ignore_COMENTARIO = r"\#.*"

# Espacios y tabulaciones
t_ignore = "\t"  # Ignorar tabulaciones


# Regla para indentación (4 espacios en blanco)
def t_INDENTACION(t):
    r"[ ]{4}"
    return t


# Regla para nuevas líneas
def t_NUEVA_LINEA(t):
    r"\n+"
    t.lexer.lineno += len(t.value)
    t.value = "\n"
    return t


# Regla para espacios
def t_ESPACIO(t):
    r"\s+"
    t.value = " "
    return t


# Regla para manejar errores
def t_error(t):
    print(f"Caracter no reconocido '{t.value[0]}'")
    t.lexer.skip(1)


# ------------------------------------------------------------
# CONSTRUCCIÓN Y EJECUCIÓN DEL LEXER
# ------------------------------------------------------------

# Construir el lexer
lexer = lex.lex()

# Ejecutar el lexer
lexer.input(programa_minimo)

# # Separar tokens
# while True:
#     token = lexer.token()
#     if not token:
#         break
#     print(token.lexpos)
