from antlr4 import *
from antlr_output.DreamchaserLexer import DreamchaserLexer
from antlr_output.DreamchaserParser import DreamchaserParser
from dreamchaser_interpreter import DreamchaserInterpreter


def run_program(program_text):
    # Create lexer and parser
    input_stream = InputStream(program_text)
    lexer = DreamchaserLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = DreamchaserParser(token_stream)

    # Parse the input
    tree = parser.program()

    # Create listener and walk the parse tree
    interpreter = DreamchaserInterpreter()
    walker = ParseTreeWalker()
    walker.walk(interpreter, tree)

    print("\n======= Resultado ejecucion =======")
    print("Variables:", end="\n")
    for var, value in interpreter.variables.items():
        print(f"  {var} = {value}")

    print("\nConstantes:", end="\n")
    for const, value in interpreter.constants.items():
        print(f"  {const} = {value}")

    print("\nFunciones:", end="\n")
    for func_name in interpreter.functions:
        print(f"  {func_name}({', '.join(interpreter.functions[func_name]['params'])})")

    print("==============================\n")


def main():
    # Your example programs
    programaPrueba = """
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

    programaPrueba2 = """
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

    programaPrueba3 = """
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

    programaPrint = """
a = 42
b = 2
c = a + b
"""

    # Run each program
    run_program(programa_minimo)


if __name__ == "__main__":
    main()
