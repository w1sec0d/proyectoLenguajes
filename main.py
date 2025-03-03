from antlr4 import *
from antlr_output.DreamchaserLexer import DreamchaserLexer
from antlr_output.DreamchaserParser import DreamchaserParser
from dreamchaser_interpreter import DreamchaserInterpreter
from ejemplosProgramas.programas import programas
from gui import DreamchaserGUI
import tkinter as tk


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

    print("\nBigrafos:", end="\n")
    for id_bigrafo, bigrafo in interprete.bigrafos.items():
        print(f"  {id_bigrafo}:")
        for id_nodo, nodo in bigrafo.nodos.items():
            print(f"    Nodo {id_nodo} (tipo: {nodo.tipo}, valor: {nodo.valor})")
            if nodo.lugares:
                print(f"      Lugares: {[lugar.id for lugar in nodo.lugares]}")
            if nodo.enlaces:
                print(f"      Enlaces: {[enlace.id for enlace in nodo.enlaces]}")

    print("==============================\n")


def main():
    root = tk.Tk()
    app = DreamchaserGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
