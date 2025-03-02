"""
Función que carga el código máquina retornado
por el ensamblador en memoria para ser ejecutado
resolviendo las direcciones en los casos en que 
sea necesario
"""


# Enlazador-Cargador
def enlazador_cargador(codigo_entrada, direccion_base=0x00000):
    operaciones_memoria = {
        "000000000000000100",  # CARGAR R,M
        "000000000000000110",  # ALMACENAR R,M
        "000000000000000000001",  # SALTARSICERO M
        "000000000000000000010",  # SALTARSIPOS M
        "000000000000000000011",  # SALTARSINEG M
        "000000000000000000100",  # SALTARSIPAR M
        "000000000000000000101",  # SALTARSICARRY M
        "000000000000000000110",  # SALTARSIDES M
        "000000000000000000111",  # SALTAR M
    }  # opcodes de operaciones de memoria

    TAMANO_MEMORIA = 2048  # Tamaño de la memoria en celdas
    mapa_memoria = {}
    direccion = direccion_base
    if len(codigo_entrada) == 0:
        raise ValueError("El código de entrada no puede tener una longitud de 0.")

    for instr in codigo_entrada:
        if direccion >= TAMANO_MEMORIA:
            raise MemoryError(
                "Se ha excedido el tamaño de la memoria para la siguiente instrucción",
                instr,
            )
        instruccion_corta = instr[:18]
        instruccion_salto = instr[:21]
        #  !!! Asumiendo que las direcciones empiezan desde 0, debe ser ASI PARA UN
        # CORRECTO FUNCIONAMIENTO
        if (
            instruccion_corta in operaciones_memoria
            or instruccion_salto in operaciones_memoria
        ):
            # Últimos 10 bits como dirección relativa, es la parte de memoria de la operacion
            direccion_relativa_binaria = int(instr[-10:], 2)
            direccion_absoluta = (
                direccion_base + direccion_relativa_binaria
            )  # Sumar la dirección relativa
            direccion_absoluta_binaria = format(direccion_absoluta, "010b")
            direccion_resuelta = instr[:-10] + direccion_absoluta_binaria
            mapa_memoria[direccion] = direccion_resuelta
        else:
            mapa_memoria[direccion] = instr

        direccion += 1

    return mapa_memoria


enlazador_cargador(
    codigo_entrada=[
        "00000000000000010000001000000000",  # Cargar      A,a CARGO 512
        "00000000000000010000101000000001",  # Cargar      B,b CARGO 513
        "00000000000000000000001001000010",  # bucle: Copiar A, C
        "00000000000000000000000110010001",  # Restar      C,B
        "00000000000000000000100100001010",  # SaltarSiCero fin
        "00000000000000000001100100001000",  # SaltarSiNegativo menor
        "00000000000000000000000110000001",  # Restar      A,B
        "00000000000000000011100100000010",  # Saltar bucle
        "00000000000000000000000110001000",  # menor: Restar B,A
        "00000000000000000011100100000010",  # Saltar bucle
        "00000000000000011000000000001100",  # Verdadero: Almacenar D,m GUARDO EN 12
        "00000000000000000000000000000000",  # Parar
    ]
)
