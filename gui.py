import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from antlr4 import *
from antlr_output.DreamchaserLexer import DreamchaserLexer
from antlr_output.DreamchaserParser import DreamchaserParser
from dreamchaser_interpreter import DreamchaserInterpreter


class DreamchaserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Lenguaje Dreamchaser - Edición Bigrafos")

        # Establecer tamaño mínimo y máximo de la ventana
        self.root.minsize(800, 600)

        self.create_widgets()

    def create_widgets(self):
        # Columna 1: Área de escritura y botones
        self.text_area = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, width=60, height=20
        )
        self.text_area.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky="nsew")

        # Cambia la disposición de los botones para que estén en la misma fila
        self.load_button = tk.Button(
            self.root, text="Cargar Programa (.txt)", command=self.load_program
        )
        self.load_button.grid(row=3, column=0)

        self.run_button = tk.Button(
            self.root, text="Ejecutar Programa", command=self.run_program
        )
        self.run_button.grid(row=4, column=0)

        # Columna 2: Áreas de salida
        tk.Label(self.root, text="Salida de ejecución:").grid(
            row=0, column=1, sticky="ew"
        )
        self.output_area = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, width=60, height=10, state="disabled"
        )
        self.output_area.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        tk.Label(self.root, text="Estado final:").grid(row=2, column=1, sticky="ew")
        self.final_state_area = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, state="disabled"
        )
        self.final_state_area.grid(
            row=3, column=1, rowspan=2, padx=10, pady=10, sticky="nsew"
        )

        # Configurar la expansión de filas y columnas
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def load_program(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            with open(file_path, "r") as file:
                program = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, program)

    def run_program(self):
        program = self.text_area.get(1.0, tk.END)
        self.output_area.config(state="normal")
        self.output_area.delete(1.0, tk.END)
        self.final_state_area.config(state="normal")
        self.final_state_area.delete(1.0, tk.END)

        try:
            # Redirect print to output_area
            import sys
            from io import StringIO

            old_stdout = sys.stdout
            sys.stdout = mystdout = StringIO()

            # Execute the program
            self.ejecutar_programa(program)

            # Get the output from print statements
            output = mystdout.getvalue()
            self.output_area.insert(tk.END, output)

            # Restore stdout
            sys.stdout = old_stdout
        except Exception as e:
            messagebox.showerror("Error", str(e))

        self.output_area.config(state="disabled")
        self.final_state_area.config(state="disabled")

    def ejecutar_programa(self, texto_programa):
        # Crear lexer y parser
        flujo_entrada = InputStream(texto_programa)
        lexer = DreamchaserLexer(flujo_entrada)
        flujo_tokens = CommonTokenStream(lexer)
        parser = DreamchaserParser(flujo_tokens)
        arbol = parser.program()
        interprete = DreamchaserInterpreter()
        caminante = ParseTreeWalker()
        caminante.walk(interprete, arbol)

        # Display final state in final_state_area
        self.final_state_area.config(state="normal")
        self.final_state_area.insert(tk.END, "Variables:\n")
        for var, valor in interprete.variables.items():
            self.final_state_area.insert(tk.END, f"  {var} = {valor}\n")

        self.final_state_area.insert(tk.END, "==============================\n")

        self.final_state_area.insert(tk.END, "\nConstantes:\n")
        for const, valor in interprete.constants.items():
            self.final_state_area.insert(tk.END, f"  {const} = {valor}\n")

        self.final_state_area.insert(tk.END, "==============================\n")

        self.final_state_area.insert(tk.END, "\nFunciones:\n")
        for nombre_funcion in interprete.functions:
            self.final_state_area.insert(
                tk.END,
                f"  {nombre_funcion}({', '.join(interprete.functions[nombre_funcion]['params'])})\n",
            )

        self.final_state_area.insert(tk.END, "==============================\n")

        self.final_state_area.insert(tk.END, "\nBigrafos:\n")
        for id_bigrafo, bigrafo in interprete.bigrafos.items():
            self.final_state_area.insert(tk.END, f"  {id_bigrafo}:\n")
            for id_nodo, nodo in bigrafo.nodos.items():
                self.final_state_area.insert(
                    tk.END,
                    f"    Nodo {id_nodo} (tipo: {nodo.tipo}, valor: {nodo.valor})\n",
                )
                if nodo.lugares:
                    self.final_state_area.insert(
                        tk.END,
                        f"      Lugares: {[lugar.id for lugar in nodo.lugares]}\n",
                    )
                if nodo.enlaces:
                    self.final_state_area.insert(
                        tk.END,
                        f"      Enlaces: {[enlace.id for enlace in nodo.enlaces]}\n",
                    )

        self.final_state_area.insert(tk.END, "==============================\n")
        self.final_state_area.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = DreamchaserGUI(root)
    root.mainloop()
