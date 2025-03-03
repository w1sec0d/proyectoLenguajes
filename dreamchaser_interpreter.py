from antlr4 import *
from antlr_output.DreamchaserParser import DreamchaserParser
from antlr_output.DreamchaserListener import DreamchaserListener
import math
from bigrafo import Bigrafo, Nodo


class DreamchaserInterpreter(DreamchaserListener):
    def __init__(self):
        self.variables = {}
        self.constants = {}
        self.functions = {}
        self.librerias_importadas = set()
        self.valor_actual = None
        self.resultados_bloque = {}
        self.bigrafos = {}  # Diccionario para almacenar múltiples bigrafos
        self.bigrafo_actual = None  # Identificador del bigrafo actual

        # Librerías predefinidas
        self.librerias = {
            "raizCuadrada": math.sqrt,
            "potencia": pow,
            "imprimir": print,
        }

    def crear_bigrafo(self, id):
        if id not in self.bigrafos:
            self.bigrafos[id] = Bigrafo()
            self.bigrafo_actual = id
            print(f"Bigrafo creado: {id}")
        else:
            print(f"Error: Bigrafo '{id}' ya existe")

    def seleccionar_bigrafo(self, id):
        if id in self.bigrafos:
            self.bigrafo_actual = id
            print(f"Bigrafo seleccionado: {id}")
        else:
            print(f"Error: Bigrafo '{id}' no existe")

    # Método auxiliar para evaluar expresiones
    def evaluar(self, ctx):
        # Verificar el tipo de ctx y manejarlo en consecuencia
        if ctx is None:
            return None

        # Manejar expresiones literales directamente verificando su tipo
        if isinstance(ctx, DreamchaserParser.NumberLiteralContext):
            texto = ctx.NUMBER().getText()
            if "e" in texto.lower():
                return float(texto)
            elif "." in texto:
                return float(texto)
            else:
                return int(texto)
        elif isinstance(ctx, DreamchaserParser.StringLiteralContext):
            texto = ctx.STRING().getText()
            return texto[1:-1]  # Eliminar comillas
        elif isinstance(ctx, DreamchaserParser.BooleanLiteralContext):
            texto = ctx.BOOLEAN().getText()
            return texto == "verdadero"

        # Manejar diferentes tipos de expresiones
        elif isinstance(ctx, DreamchaserParser.LiteralExprContext):
            # Para LiteralExpr, delegar correctamente al hijo literal
            return self.evaluar(ctx.literal())

        elif isinstance(ctx, DreamchaserParser.IdentifierExprContext):
            nombre_var = ctx.ID().getText()
            if nombre_var in self.variables:
                return self.variables[nombre_var]
            elif nombre_var in self.constants:
                return self.constants[nombre_var]
            else:
                print(f"Error: Variable o constante '{nombre_var}' no está definida")
                return None

        elif isinstance(ctx, DreamchaserParser.ParenExprContext):
            return self.evaluar(ctx.expression())

        elif isinstance(ctx, DreamchaserParser.MulDivExprContext):
            izquierda = self.evaluar(ctx.expression(0))
            derecha = self.evaluar(ctx.expression(1))
            op = ctx.op.text

            if izquierda is None or derecha is None:
                return None

            if op == "*":
                return izquierda * derecha
            elif op == "/":
                if derecha == 0:
                    print("Error: División por cero")
                    return None
                return izquierda / derecha
            elif op == "//":
                if derecha == 0:
                    print("Error: División por cero")
                    return None
                return izquierda // derecha
            elif op == "%":
                if derecha == 0:
                    print("Error: Módulo por cero")
                    return None
                return izquierda % derecha

        elif isinstance(ctx, DreamchaserParser.AddSubExprContext):
            izquierda = self.evaluar(ctx.expression(0))
            derecha = self.evaluar(ctx.expression(1))
            op = ctx.op.text

            if izquierda is None or derecha is None:
                return None

            if op == "+":
                return izquierda + derecha
            elif op == "-":
                return izquierda - derecha

        elif isinstance(ctx, DreamchaserParser.RelationalExprContext):
            izquierda = self.evaluar(ctx.expression(0))
            derecha = self.evaluar(ctx.expression(1))
            op = ctx.op.text

            if izquierda is None or derecha is None:
                return None

            if op == "==":
                return izquierda == derecha
            elif op == "!=":
                return izquierda != derecha
            elif op == ">":
                return izquierda > derecha
            elif op == "<":
                return izquierda < derecha
            elif op == ">=":
                return izquierda >= derecha
            elif op == "<=":
                return izquierda <= derecha

        elif isinstance(ctx, DreamchaserParser.FunctionCallExprContext):
            return self.evaluar_llamada_funcion(ctx.functionCall())

        return None

    def evaluar_llamada_funcion(self, ctx):
        nombre_funcion = ctx.ID().getText()
        args = []
        if ctx.argList():
            for expr in ctx.argList().expression():
                valor_arg = self.evaluar(expr)
                if valor_arg is None:
                    print(
                        f"Error: Fallo en la evaluación del argumento en la llamada a la función '{nombre_funcion}'"
                    )
                    return None
                args.append(valor_arg)

        # Verificar si es una función de librería incorporada (incluyendo imprimir)
        if (
            nombre_funcion in self.librerias_importadas
            or nombre_funcion in self.librerias
        ):
            if nombre_funcion in self.librerias:
                try:
                    resultado = self.librerias[nombre_funcion](*args)
                    # Para la función imprimir, devolver None ya que imprimir no devuelve un valor en Python
                    if nombre_funcion == "imprimir":
                        return None
                    return resultado
                except Exception as e:
                    print(
                        f"Error al ejecutar la función de librería '{nombre_funcion}': {str(e)}"
                    )
                    return None
            else:
                print(
                    f"Error: La función de librería '{nombre_funcion}' está importada pero no definida"
                )
                return None

        # Verificar si es una función definida por el usuario
        if nombre_funcion in self.functions:
            definicion_funcion = self.functions[nombre_funcion]

            if len(args) != len(definicion_funcion["params"]):
                print(
                    f"Error: La función '{nombre_funcion}' espera {len(definicion_funcion['params'])} argumentos, pero recibió {len(args)}"
                )
                return None

            # Guardar el estado actual de las variables
            vars_anteriores = self.variables.copy()

            # Establecer parámetros
            for i, param in enumerate(definicion_funcion["params"]):
                self.variables[param] = args[i]

            # Ejecutar el cuerpo de la función
            valor_anterior = self.valor_actual
            self.valor_actual = None
            self.ejecutar_bloque(definicion_funcion["block"])
            resultado = self.valor_actual
            if resultado is None:
                resultado = valor_anterior  # Si no hay declaración de retorno, preservar el valor anterior

            # Restaurar el estado de las variables
            self.variables = vars_anteriores

            return resultado

        # Verificar si es una función incorporada
        print(f"Error: La función '{nombre_funcion}' no está definida")
        return None

    # Métodos del listener
    def enterProgram(self, ctx):
        self.valor_actual = None

    def exitProgram(self, ctx):
        pass

    def enterImportStatement(self, ctx):
        if ctx.STRING() is None:
            print(
                "Error: Falta el nombre de la librería en la declaración de importación"
            )
            return

        texto_libreria = ctx.STRING().getText()
        nombre_libreria = texto_libreria[1:-1]  # Eliminar comillas

        if nombre_libreria in self.librerias:
            self.librerias_importadas.add(nombre_libreria)
        else:
            print(f"Advertencia: Librería '{nombre_libreria}' no encontrada")

    def enterConstStatement(self, ctx):
        nombre_id = ctx.ID().getText()

        if ctx.literal() is None:
            print(f"Error: Falta el valor para la constante '{nombre_id}'")
            return

        valor = self.evaluar(ctx.literal())

        if nombre_id in self.constants:
            print(
                f"Advertencia: La constante '{nombre_id}' ya está definida y será sobrescrita"
            )

        self.constants[nombre_id] = valor

    def enterAssignmentStatement(self, ctx):
        nombre_id = ctx.ID().getText()

        if ctx.expression() is None:
            print(f"Error: Falta la expresión en la asignación a '{nombre_id}'")
            return

        valor = self.evaluar(ctx.expression())

        if nombre_id in self.constants:
            print(f"Error: No se puede asignar a la constante '{nombre_id}'")
            return

        self.variables[nombre_id] = valor

    def enterConditionalStatement(self, ctx):
        if ctx.expression() is None:
            print("Error: Falta la condición en la declaración 'si'")
            return

        condicion = self.evaluar(ctx.expression())

        if condicion:
            if ctx.block(0) is not None:
                self.ejecutar_bloque(ctx.block(0))
        elif len(ctx.block()) > 1:
            self.ejecutar_bloque(ctx.block(1))

    def enterWhileStatement(self, ctx):
        if ctx.expression() is None:
            print("Error: Falta la condición en la declaración 'mientras'")
            return

        # Agregar un límite de seguridad para evitar bucles infinitos durante el desarrollo
        max_iteraciones = 10000
        contador_iteraciones = 0

        while self.evaluar(ctx.expression()) and contador_iteraciones < max_iteraciones:
            self.ejecutar_bloque(ctx.block())
            contador_iteraciones += 1

        if contador_iteraciones >= max_iteraciones:
            print(
                "Advertencia: Se alcanzó el máximo de iteraciones del bucle, posible bucle infinito"
            )

    def enterFunctionDefinition(self, ctx):
        nombre_funcion = ctx.ID().getText()
        params = []

        if ctx.paramList():
            for param in ctx.paramList().ID():
                params.append(param.getText())

        # Almacenar la definición de la función
        self.functions[nombre_funcion] = {"params": params, "block": ctx.block()}

    def enterReturnStatement(self, ctx):
        if ctx.expression() is None:
            print("Error: Falta la expresión en la declaración 'retornar'")
            self.valor_actual = None
            return

        self.valor_actual = self.evaluar(ctx.expression())

    def enterFunctionCall(self, ctx):
        self.valor_actual = self.evaluar_llamada_funcion(ctx)

    def enterCrearBigrafoStatement(self, ctx):
        id_bigrafo = ctx.ID().getText()
        if id_bigrafo not in self.bigrafos:
            self.bigrafos[id_bigrafo] = Bigrafo()
            self.bigrafo_actual = id_bigrafo
            print(f"Bigrafo creado: {id_bigrafo}")
        else:
            print(f"Error: Bigrafo '{id_bigrafo}' ya existe")

    def enterSeleccionarBigrafoStatement(self, ctx):
        id_bigrafo = ctx.ID().getText()
        if id_bigrafo in self.bigrafos:
            self.bigrafo_actual = id_bigrafo
            print(f"Bigrafo seleccionado: {id_bigrafo}")
        else:
            print(f"Error: Bigrafo '{id_bigrafo}' no existe")

    def enterCrearNodoStatement(self, ctx):
        if self.bigrafo_actual is None:
            print("Error: No hay un bigrafo seleccionado")
            return

        id_nodo = ctx.ID().getText()
        tipo = ctx.STRING(0).getText()[1:-1]  # Eliminar comillas
        valor = ctx.STRING(1).getText()[1:-1]  # Eliminar comillas
        self.bigrafos[self.bigrafo_actual].agregar_nodo(id_nodo, tipo, valor)
        print(
            f"Nodo creado en {self.bigrafo_actual}: {id_nodo} (tipo: {tipo}, valor: {valor})"
        )

    def enterUnirBigrafosStatement(self, ctx):
        id1 = ctx.ID(0).getText()
        id2 = ctx.ID(1).getText()
        id_nuevo = ctx.ID(2).getText()
        self.unir_bigrafos(id1, id2, id_nuevo)

    def enterInterseccionBigrafosStatement(self, ctx):
        id1 = ctx.ID(0).getText()
        id2 = ctx.ID(1).getText()
        id_nuevo = ctx.ID(2).getText()
        self.interseccion_bigrafos(id1, id2, id_nuevo)

    def interseccion_bigrafos(self, id1, id2, id_nuevo):
        if id1 in self.bigrafos and id2 in self.bigrafos:
            bigrafo1 = self.bigrafos[id1]
            bigrafo2 = self.bigrafos[id2]
            nuevo_bigrafo = bigrafo1.interseccion(bigrafo2)
            self.bigrafos[id_nuevo] = nuevo_bigrafo
            print(
                f"Bigrafo '{id_nuevo}' creado por la intersección de '{id1}' y '{id2}'"
            )
        else:
            print(f"Error: Uno o ambos bigrafos '{id1}' y '{id2}' no existen")

    def enterDiferenciaBigrafosStatement(self, ctx):
        id1 = ctx.ID(0).getText()
        id2 = ctx.ID(1).getText()
        id_nuevo = ctx.ID(2).getText()
        self.diferencia_bigrafos(id1, id2, id_nuevo)

    def diferencia_bigrafos(self, id1, id2, id_nuevo):
        if id1 in self.bigrafos and id2 in self.bigrafos:
            bigrafo1 = self.bigrafos[id1]
            bigrafo2 = self.bigrafos[id2]
            nuevo_bigrafo = bigrafo1.diferencia(bigrafo2)
            self.bigrafos[id_nuevo] = nuevo_bigrafo
            print(f"Bigrafo '{id_nuevo}' creado por la diferencia de '{id1}' y '{id2}'")
        else:
            print(f"Error: Uno o ambos bigrafos '{id1}' y '{id2}' no existen")

    def enterClonarBigrafoStatement(self, ctx):
        id_original = ctx.ID(0).getText()
        id_clon = ctx.ID(1).getText()
        self.clonar_bigrafo(id_original, id_clon)

    def clonar_bigrafo(self, id_original, id_clon):
        if id_original in self.bigrafos:
            bigrafo_original = self.bigrafos[id_original]
            bigrafo_clon = bigrafo_original.clonar()
            self.bigrafos[id_clon] = bigrafo_clon
            print(f"Bigrafo '{id_clon}' creado como clon de '{id_original}'")
        else:
            print(f"Error: Bigrafo '{id_original}' no existe")

    def unir_bigrafos(self, id1, id2, id_nuevo):
        if id1 in self.bigrafos and id2 in self.bigrafos:
            bigrafo1 = self.bigrafos[id1]
            bigrafo2 = self.bigrafos[id2]
            nuevo_bigrafo = bigrafo1.union(bigrafo2)
            self.bigrafos[id_nuevo] = nuevo_bigrafo
            print(f"Bigrafo '{id_nuevo}' creado por la unión de '{id1}' y '{id2}'")
        else:
            print(f"Error: Uno o ambos bigrafos '{id1}' y '{id2}' no existen")

    def enterContarLugaresStatement(self, ctx):
        id_nodo = ctx.ID().getText()
        self.contar_lugares(id_nodo)

    def contar_lugares(self, id_nodo):
        if self.bigrafo_actual is None:
            print("Error: No hay un bigrafo seleccionado")
            return

        if id_nodo in self.bigrafos[self.bigrafo_actual].nodos:
            count = self.bigrafos[self.bigrafo_actual].contar_lugares(id_nodo)
            print(f"Nodo '{id_nodo}' tiene {count} lugares")
        else:
            print(f"Error: Nodo '{id_nodo}' no existe")

    def enterContarEnlacesStatement(self, ctx):
        id_nodo = ctx.ID().getText()
        self.contar_enlaces(id_nodo)

    def contar_enlaces(self, id_nodo):
        if self.bigrafo_actual is None:
            print("Error: No hay un bigrafo seleccionado")
            return

        if id_nodo in self.bigrafos[self.bigrafo_actual].nodos:
            count = self.bigrafos[self.bigrafo_actual].contar_enlaces(id_nodo)
            print(f"Nodo '{id_nodo}' tiene {count} enlaces")
        else:
            print(f"Error: Nodo '{id_nodo}' no existe")

    # Método auxiliar para ejecutar un bloque de declaraciones
    def ejecutar_bloque(self, ctx_bloque):
        if ctx_bloque is None:
            print("Error: Falta el bloque")
            return

        valor_anterior = self.valor_actual
        for declaracion in ctx_bloque.statement():
            try:
                caminante = ParseTreeWalker()
                caminante.walk(self, declaracion)
                # Si encontramos una declaración de retorno, salir
                if (
                    self.valor_actual is not None
                    and self.valor_actual != valor_anterior
                ):
                    break
            except Exception as e:
                print(f"Error al ejecutar la declaración: {str(e)}")
                # Continuar la ejecución con la siguiente declaración
