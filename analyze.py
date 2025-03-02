import sys
from antlr4 import *
from antlr_output.DreamchaserLexer import DreamchaserLexer
from antlr_output.DreamchaserParser import DreamchaserParser
from antlr_output.DreamchaserListener import DreamchaserListener


class AnalizadorSemantico(DreamchaserListener):
    def __init__(self):
        self.variables = {}

    def exitConstStmt(self, ctx):
        # Maneja la declaración de constantes
        nombre_var = ctx.ID().getText()
        valor = ctx.expr().getText()
        self.variables[nombre_var] = valor
        print(f"Constante declarada: {nombre_var} = {valor}")

    def exitVarDecl(self, ctx):
        # Maneja la declaración de variables
        nombre_var = ctx.ID().getText()
        valor = ctx.expr().getText()
        self.variables[nombre_var] = valor
        print(f"Variable declarada: {nombre_var} = {valor}")

    def exitAssignment(self, ctx):
        # Maneja la asignación de variables
        nombre_var = ctx.ID().getText()
        valor = ctx.expr().getText()
        if nombre_var in self.variables:
            self.variables[nombre_var] = valor
            print(f"Variable asignada: {nombre_var} = {valor}")
        else:
            print(f"Error: Variable '{nombre_var}' no declarada")

    def exitArithmeticExpr(self, ctx):
        # Maneja las expresiones aritméticas
        if ctx.getChildCount() == 3:
            izquierda = ctx.expr(0).getText()
            derecha = ctx.expr(1).getText()
            operador = ctx.getChild(1).getText()
            if izquierda in self.variables and derecha in self.variables:
                izquierda_valor = float(self.variables[izquierda])
                derecha_valor = float(self.variables[derecha])
                if operador == "+":
                    resultado = izquierda_valor + derecha_valor
                elif operador == "-":
                    resultado = izquierda_valor - derecha_valor
                elif operador == "*":
                    resultado = izquierda_valor * derecha_valor
                elif operador == "/":
                    resultado = izquierda_valor / derecha_valor
                self.variables[ctx.getText()] = resultado
                print(f"Resultado de {izquierda} {operador} {derecha} = {resultado}")
            else:
                print(
                    f"Error: Una o ambas variables '{izquierda}' o '{derecha}' no están declaradas"
                )

    def exitPrintStmt(self, ctx):
        # Maneja la impresión de resultados
        expr = ctx.expr().getText()
        if expr in self.variables:
            print(f"Imprimir: {self.variables[expr]}")
        else:
            print(f"Error: Variable '{expr}' no declarada")


def main(argv):
    # Lee el archivo de entrada
    flujo_entrada = FileStream(argv[1])
    lexer = DreamchaserLexer(flujo_entrada)
    flujo_tokens = CommonTokenStream(lexer)
    parser = DreamchaserParser(flujo_tokens)
    arbol = parser.prog()

    # Realiza el análisis semántico
    analizador = AnalizadorSemantico()
    caminante = ParseTreeWalker()
    caminante.walk(analizador, arbol)


if __name__ == "__main__":
    main(sys.argv)
