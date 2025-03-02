import re
from analisisLexico import lexer
from utils.programas import programaPrueba
from utils.funcionesPrecompiladas import funcionesPrecompiladas


# Función para preprocesar el código fuente
def preprocesar_codigo(codigoFuente):
    resultado = []
    lexer.input(codigoFuente)
    while True:
        token = lexer.token()
        if not token:
            break
        if token.type == "IMPORTAR":
            nombreLibreria = token.value.split("'")[1]
            if nombreLibreria in funcionesPrecompiladas:
                posicionMemoria = funcionesPrecompiladas.get(nombreLibreria)
                # Leer el contenido del archivo importado
                resultado.append(
                    f"!EJECUTAR_POSICION:{posicionMemoria}\n",
                )

            else:
                print(f"Error: la función '{nombreLibreria}' no está precompilada")
        else:
            resultado.append(token.value)

    codigo_preprocesado = "".join(resultado)
    # Reemplazar múltiples saltos de línea consecutivos con un solo salto de línea
    codigo_preprocesado = re.sub(r"\n\s*\n", "\n", codigo_preprocesado)
    # Eliminar espacios en blanco al inicio y al final del archivo
    codigo_preprocesado = codigo_preprocesado.strip()

    return codigo_preprocesado
