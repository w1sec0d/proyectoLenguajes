# Define opcode segun tipo de operacion
especiales = {"PARAR": "00000000000000000000000000000000"}

carga_memoria = {
    "CARGAR": "000000000000000100",  # Operación CARGAR (18 bits)
    "ALMACENAR": "000000000000000110",  # Operación ALMACENAR (18 bits) }]
}

carga_operacion_valor = {
    "CARGARVALOR": "000000000000000101",  # Operación CARGARVALOR (20 bits)
    "LSL": "000000000000000001",
    "LSR": "000000000000000010",
    "ASR": "000000000000000011",
    "ROTACIONL": "000000000000000111",
    "ROTACIONR": "000000000000001000",
}

# Diccionario de operaciones de salto (21 bits)
saltos = {
    "SALTAR": "000000000000000000111",  # SALTAR (21 bits)
    "SALTARSICERO": "000000000000000000001",  # SALTAR SI CERO
    "SALTARSIPOS": "000000000000000000010",  # SALTAR SI POSITIVO
    "SALTARSINEG": "000000000000000000011",  # SALTAR SI NEGATIVO
    "SALTARSIPAR": "000000000000000000100",  # SALTAR SI PAR
    "SALTARSICARRY": "000000000000000000101",  # SALTAR SI CARRY
    "SALTARSIDES": "000000000000000000110",  # SALTAR SI DESBORDAMIENTO
    "SALTARSINODES": "000000000000000001000",  # SALTAR SI DESBORDAMIENTO
}

operaciones_registros = {
    "OR": "00000000000000000000000001",
    "AND": "00000000000000000000000010",
    "XOR": "00000000000000000000000011",
    "NOT": "00000000000000000000000100",
    "SUMAR": "00000000000000000000000101",
    "RESTAR": "00000000000000000000000110",
    "MULT": "00000000000000000000000111",
    "DIV": "00000000000000000000001000",
    "COPIAR": "00000000000000000000001001",
    "COMP": "00000000000000000000001010",
    "INTERCAMBIAR": "00000000000000000000001011",
    "MOD": "00000000000000000000001101",
}

# Diccionario de operaciones (18 bits para la operación)
codigo_operaciones = (
    especiales | carga_memoria | carga_operacion_valor | saltos | operaciones_registros
)

# Registro de selección (3 bits)
registros = {
    "R0": "000",  # Registro 0 (3 bits)
    "R1": "001",  # Registro 1 (3 bits)
    "R2": "010",  # Registro 2 (3 bits)
    "R3": "011",  # Registro 3 (3 bits)
    "R4": "100",  # Registro 4 (3 bits)
    "R5": "101",  # Registro 5 (3 bits)
    "R6": "110",  # Registro 6 (3 bits)
    "R7": "111",  # Registro 7 (3 bits)
}


# Recibe una instrucción y devuelve su representación en binario
def traducir_instruccion(instruccion):
    if instruccion == "PARAR":
        return codigo_operaciones["PARAR"]

    partes = instruccion.split()
    nombre_instruccion = partes[0]
    if nombre_instruccion not in codigo_operaciones:  # verificar si existe opcode
        raise ValueError(f"Operación desconocida: {nombre_instruccion}")
    opcode = codigo_operaciones[nombre_instruccion]

    # Determinar el resto de la instrucción
    if (
        nombre_instruccion in carga_memoria
        or nombre_instruccion in carga_operacion_valor
    ):
        if partes[1] not in registros:
            raise ValueError(f"Registro desconocido: {partes[1]}")
        registro = registros[partes[1]]

        direccion_binaria = format(
            int(partes[2]), "011b"
        )  # Determinar la dirección de memoria de 11 bits (últimos 11 bits)

        return opcode + registro + direccion_binaria

    elif nombre_instruccion.startswith("SALTAR"):
        direccion_binaria = format(
            int(partes[1]), "011b"
        )  # Determinar la dirección de memoria de 11 bits (últimos 11 bits)
        return opcode + direccion_binaria

    elif nombre_instruccion in operaciones_registros:
        registro1 = registros[partes[1]]
        registro2 = registros[partes[2]]
        return opcode + registro1 + registro2

    else:
        raise ValueError(f"Operación desconocida: {partes[0]}")


def ensamblador(lista_instrucciones):
    instrucciones_binarias = []

    for instruccion in lista_instrucciones:
        instruccion_binaria = traducir_instruccion(instruccion)
        instrucciones_binarias.append(instruccion_binaria)
    return instrucciones_binarias


# Prueba del ensamblador
# codigo_entrada = [
#     "SALTAR 0",
#     "CARGAR R4 2",
#     "CARGAR R5 4",
#     "ALMACENAR R6 32",
#     "ALMACENAR R7 40",
#     "ALMACENAR R2 1",
#     "SALTARSICERO 7",
#     "SALTARSICARRY 72",
#     "SALTARSIPAR 130",
#     "SALTAR 3",
#     "ALMACENAR R5 9",
#     "SALTAR 0",
# ]
