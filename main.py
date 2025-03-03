from antlr4 import *
from antlr_output.DreamchaserLexer import DreamchaserLexer
from antlr_output.DreamchaserParser import DreamchaserParser
from dreamchaser_interpreter import DreamchaserInterpreter


def ejecutar_programa(texto_programa):
    # Crear lexer y parser
    flujo_entrada = InputStream(texto_programa)
    lexer = DreamchaserLexer(flujo_entrada)
    flujo_tokens = CommonTokenStream(lexer)
    parser = DreamchaserParser(flujo_tokens)

    # Parsear la entrada
    arbol = parser.program()

    # Crear el intérprete y recorrer el árbol de análisis
    interprete = DreamchaserInterpreter()
    caminante = ParseTreeWalker()
    caminante.walk(interprete, arbol)

    print("\n======= Estado final =======")
    print("Variables:", end="\n")
    for var, valor in interprete.variables.items():
        print(f"  {var} = {valor}")

    print("\nConstantes:", end="\n")
    for const, valor in interprete.constants.items():
        print(f"  {const} = {valor}")

    print("\nFunciones:", end="\n")
    for nombre_funcion in interprete.functions:
        print(
            f"  {nombre_funcion}({', '.join(interprete.functions[nombre_funcion]['params'])})"
        )

    print("==============================\n")


def main():
    # Tus programas de ejemplo
    programa_prueba = """
# Importando librerías precompiladas
importar 'raizCuadrada'
importar 'potencia'
const PI 3.141592654
const E 2.718281828
const MATERIA 'LENGUAJES DE PROGRAMACIÓN'
# Definición de variables
a = 10
b = 20.5
c = 1e-3
d = verdadero
e = falso
# Operaciones aritméticas
suma = a + b
resta = a - b
multiplicacion = a * b
division = a / b
divisionEntera = a // b
# Operadores relacionales
igual = a == b
diferente = a != b
mayor = a > b
menor = a < b
mayorIgual = a >= b
menorIgual = a <= b
# Estructuras de control
si a > b
 retornar a
sino
 retornar b
mientras a < 100
 a = a + 1
funcion calcularArea(radio)
 retornar PI * radio * radio
# Llamada a la función
area = calcularArea(5)
materia2 = MATERIA
# Comentario de prueba
# Este es un comentario que debe ser ignorado por el lexer
"""

    programa_prueba2 = """
importar 'libreria.txt'
const PI 3.141592654
const E = 2.718281828
a_2 = 2.41e-2
calcular = verdadero
si calcular # Esto es un comentario
 a = PI * a_2 # Se va a eliminar
sino a == 3
 a = E
funcion suma(a, b)
 retornar a + b
"""

    programa_prueba3 = """
const PI 3.141592654
const MATERIA 'LENGUAJES DE PROGRAMACIÓN'
a = 10
b = 20
suma = a + b
"""

    programa_minimo = """
const NOTA 4
a = 10
b = NOTA + 1
imprimir(a)
"""

    programa_print = """
a = 42
b = 2
c = a + b
"""

    bucle_minimo = """
a = 0
mientras a < 10
    a = a + 1
"""

    programa2 = """
a = verdadero
si a
    imprimir('verdadero')
c = potencia(2,2)
"""
    ejecutar_programa(programa2)


if __name__ == "__main__":
    main()
