from antlr4 import *
from antlr_output.DreamchaserParser import DreamchaserParser
from antlr_output.DreamchaserListener import DreamchaserListener
import math


class DreamchaserInterpreter(DreamchaserListener):
    def __init__(self):
        self.variables = {}
        self.constants = {}
        self.functions = {}
        self.imported_libraries = set()
        self.current_value = None
        self.block_results = {}

        # Pre-defined libraries
        self.libraries = {
            "raizCuadrada": math.sqrt,
            "potencia": pow,
            "imprimir": print,
        }  # The print function will be added in main.p

    # Helper method to evaluate expressions
    def evaluate(self, ctx):
        # Check the type of ctx and handle accordingly
        if ctx is None:
            return None

        # Handle literal expressions directly by checking their type
        if isinstance(ctx, DreamchaserParser.NumberLiteralContext):
            text = ctx.NUMBER().getText()
            if "e" in text.lower():
                return float(text)
            elif "." in text:
                return float(text)
            else:
                return int(text)
        elif isinstance(ctx, DreamchaserParser.StringLiteralContext):
            text = ctx.STRING().getText()
            return text[1:-1]  # Remove quotes
        elif isinstance(ctx, DreamchaserParser.BooleanLiteralContext):
            text = ctx.BOOLEAN().getText()
            return text == "verdadero"

        # Handle different expression types
        elif isinstance(ctx, DreamchaserParser.LiteralExprContext):
            # For LiteralExpr, correctly delegate to the literal child
            return self.evaluate(ctx.literal())

        elif isinstance(ctx, DreamchaserParser.IdentifierExprContext):
            var_name = ctx.ID().getText()
            if var_name in self.variables:
                return self.variables[var_name]
            elif var_name in self.constants:
                return self.constants[var_name]
            else:
                print(f"Error: Variable or constant '{var_name}' is not defined")
                return None

        elif isinstance(ctx, DreamchaserParser.ParenExprContext):
            return self.evaluate(ctx.expression())

        elif isinstance(ctx, DreamchaserParser.MulDivExprContext):
            left = self.evaluate(ctx.expression(0))
            right = self.evaluate(ctx.expression(1))
            op = ctx.op.text

            if left is None or right is None:
                return None

            if op == "*":
                return left * right
            elif op == "/":
                if right == 0:
                    print("Error: Division by zero")
                    return None
                return left / right
            elif op == "//":
                if right == 0:
                    print("Error: Division by zero")
                    return None
                return left // right
            elif op == "%":
                if right == 0:
                    print("Error: Modulo by zero")
                    return None
                return left % right

        elif isinstance(ctx, DreamchaserParser.AddSubExprContext):
            left = self.evaluate(ctx.expression(0))
            right = self.evaluate(ctx.expression(1))
            op = ctx.op.text

            if left is None or right is None:
                return None

            if op == "+":
                return left + right
            elif op == "-":
                return left - right

        elif isinstance(ctx, DreamchaserParser.RelationalExprContext):
            left = self.evaluate(ctx.expression(0))
            right = self.evaluate(ctx.expression(1))
            op = ctx.op.text

            if left is None or right is None:
                return None

            if op == "==":
                return left == right
            elif op == "!=":
                return left != right
            elif op == ">":
                return left > right
            elif op == "<":
                return left < right
            elif op == ">=":
                return left >= right
            elif op == "<=":
                return left <= right

        elif isinstance(ctx, DreamchaserParser.FunctionCallExprContext):
            return self.evaluate_function_call(ctx.functionCall())

        return None

    def evaluate_function_call(self, ctx):
        function_name = ctx.ID().getText()
        args = []
        if ctx.argList():
            for expr in ctx.argList().expression():
                arg_value = self.evaluate(expr)
                if arg_value is None:
                    print(
                        f"Error: Argument evaluation failed in function call '{function_name}'"
                    )
                    return None
                args.append(arg_value)

        # Check if it's a built-in library function (including print)
        if function_name in self.imported_libraries or function_name in self.libraries:
            if function_name in self.libraries:
                try:
                    result = self.libraries[function_name](*args)
                    # For print function, return None since print doesn't return a value in Python
                    if function_name == "imprimir":
                        return None
                    return result
                except Exception as e:
                    print(
                        f"Error executing library function '{function_name}': {str(e)}"
                    )
                    return None
            else:
                print(
                    f"Error: Library function '{function_name}' is imported but not defined"
                )
                return None

        # Check if it's a user-defined function
        if function_name in self.functions:
            function_def = self.functions[function_name]

            if len(args) != len(function_def["params"]):
                print(
                    f"Error: Function '{function_name}' expects {len(function_def['params'])} arguments, but got {len(args)}"
                )
                return None

            # Save current variable state
            old_vars = self.variables.copy()

            # Set parameters
            for i, param in enumerate(function_def["params"]):
                self.variables[param] = args[i]

            # Execute function body
            old_value = self.current_value
            self.current_value = None
            self.execute_block(function_def["block"])
            result = self.current_value
            if result is None:
                result = old_value  # If no return statement, preserve previous value

            # Restore variable state
            self.variables = old_vars

            return result

        # Check if it's a built-in function
        print(f"Error: Function '{function_name}' is not defined")
        return None

    # Listener methods
    def enterProgram(self, ctx):
        self.current_value = None

    def exitProgram(self, ctx):
        pass

    def enterImportStatement(self, ctx):
        if ctx.STRING() is None:
            print("Error: Import statement missing library name")
            return

        library_text = ctx.STRING().getText()
        library_name = library_text[1:-1]  # Remove quotes

        if library_name in self.libraries:
            self.imported_libraries.add(library_name)
        else:
            print(f"Warning: Library '{library_name}' not found")

    def enterConstStatement(self, ctx):
        id_name = ctx.ID().getText()

        if ctx.literal() is None:
            print(f"Error: Missing value for constant '{id_name}'")
            return

        value = self.evaluate(ctx.literal())

        if id_name in self.constants:
            print(
                f"Warning: Constant '{id_name}' is already defined and will be overwritten"
            )

        self.constants[id_name] = value

    def enterAssignmentStatement(self, ctx):
        id_name = ctx.ID().getText()

        if ctx.expression() is None:
            print(f"Error: Missing expression in assignment to '{id_name}'")
            return

        value = self.evaluate(ctx.expression())

        if id_name in self.constants:
            print(f"Error: Cannot assign to constant '{id_name}'")
            return

        self.variables[id_name] = value

    def enterConditionalStatement(self, ctx):
        if ctx.expression() is None:
            print("Error: Missing condition in 'si' statement")
            return

        condition = self.evaluate(ctx.expression())

        if condition:
            if ctx.block(0) is not None:
                self.execute_block(ctx.block(0))
        elif len(ctx.block()) > 1:
            self.execute_block(ctx.block(1))

    def enterWhileStatement(self, ctx):
        if ctx.expression() is None:
            print("Error: Missing condition in 'mientras' statement")
            return

        # Add a safety limit to prevent infinite loops during development
        max_iterations = 10000
        iteration_count = 0

        while self.evaluate(ctx.expression()) and iteration_count < max_iterations:
            self.execute_block(ctx.block())
            iteration_count += 1

        if iteration_count >= max_iterations:
            print("Warning: Maximum loop iterations reached, possible infinite loop")

    def enterFunctionDefinition(self, ctx):
        function_name = ctx.ID().getText()
        params = []

        if ctx.paramList():
            for param in ctx.paramList().ID():
                params.append(param.getText())

        # Store function definition
        self.functions[function_name] = {"params": params, "block": ctx.block()}

    def enterReturnStatement(self, ctx):
        if ctx.expression() is None:
            print("Error: Missing expression in 'retornar' statement")
            self.current_value = None
            return

        self.current_value = self.evaluate(ctx.expression())

    def enterFunctionCall(self, ctx):
        self.current_value = self.evaluate_function_call(ctx)

    # Helper method to execute a block of statements
    def execute_block(self, block_ctx):
        if block_ctx is None:
            print("Error: Missing block")
            return

        old_value = self.current_value
        for statement in block_ctx.statement():
            try:
                walker = ParseTreeWalker()
                walker.walk(self, statement)
                # If we hit a return statement, break out
                if self.current_value is not None and self.current_value != old_value:
                    break
            except Exception as e:
                print(f"Error executing statement: {str(e)}")
                # Continue execution with next statement
