from enlazadorCargador import enlazador_cargador


class Computadora:
    def __init__(self, tamano_memoria=2048):
        # Simula la memoria (cada celda de memoria almacena un entero de 32 bits)
        self.memoria = ["0" * 32 for _ in range(tamano_memoria)]
        self.registros = [0] * 8

        """---------------------------------------------------------------------------------
        BANDERAS DE DREAMCHASER
        ------------------------------------------------------------------------------------"""
        # Bandera para carry
        self.bandera_carry = 0
        # Bandera para zero
        self.bandera_zero = 0
        # Bandera para negativo
        self.bandera_neg = 0
        # Bandera para par
        self.bandera_par = 0
        # Bandera para desbordamiento
        self.bandera_desb = 0
        # Puntero de instrucción (PC)
        self.pc = 0

        """----------------------------------------------------------------------------------------------------

        OPERACIONES DE DREAMCHASER

        -------------------------------------------------------------------------------------------------------"""

        self.operaciones_registro_memoria = {
            65536: self.cargar,  # CARGAR
            98304: self.almacenar,  # ALMACENAR
        }
        self.operaciones_registro_valor = {
            16384: self.lsl,  # LSL
            32768: self.lsr,  #  LSR
            49152: self.asr,  # ASR
            81920: self.cargar_valor,  # CARGAR VALOR
            114688: self.rotacionl,  # ROTACION IZQUIERDA
            131072: self.rotacionr,  # ROTACION DERECHA
        }

        self.operaciones_salto = {
            2048: self.saltar_si_cero,  # SALTAR SI CERO
            4096: self.saltar_si_positivo,  # SALTARSIPOS
            6144: self.saltar_si_negativo,  # SALTARSINEG
            8192: self.saltar_si_par,  # SALTARSIPAR
            10240: self.saltar_si_carry,  # SALTARSICARRY
            12288: self.saltar_si_desbordamiento,  # SALTARSIDES
            14336: self.saltar,  # SALTAR
            16384: self.saltar_si_no_desbordamiento,  # SALTASINODES
        }

        self.operaciones_registros = {
            64: self.or_,  # OR
            128: self.and_,  # AND
            192: self.xor_,  # XOR
            256: self.not_,  # NOT
            320: self.sumar,  # SUMAR
            384: self.restar,  # RESTAR
            448: self.multiplicar,  # MULT
            512: self.dividir,  # DIV
            576: self.copiar,  # COPIAR
            640: self.comparar,  # COMP
            704: self.intercambiar,  # INTERCAMBIAR
            832: self.modulo,  # MOD
        }

    """
    -------------------------
    ENLAZADOR - CARGADOR
    -------------------------
    """

    # Carga el código binario proporcionado por el ensamblador de manera contigua en memoria
    # Comenzando desde el 0
    def cargar_codigo(self, codigo_entrada, direccion_de_inicio=0x0000):
        mapa_memoria = enlazador_cargador(codigo_entrada, direccion_de_inicio)
        for direccion, instr in mapa_memoria.items():
            self.memoria[direccion] = instr
        return self.memoria

    def mostrar_memoria(self):
        memoria_ocupada = []

        for direccion, instr in enumerate(self.memoria):
            if instr != 0:
                memoria_ocupada.append(
                    (f"{direccion}", instr)
                )  # Dirección en Hex, valor binario

        if not memoria_ocupada:
            return [("No hay instrucciones en memoria", "")]  # Mensaje en la tabla

        return memoria_ocupada  # Retorna la lista de tuplas

    def ejecutar(self, direccion_inicio=0):
        """Ejecuta las instrucciones cargadas en la memoria"""
        self.pc = direccion_inicio
        while self.pc < len(self.memoria):  # Mientras haya instrucciones por ejecutar
            instruccion = int(self.memoria[self.pc], 2)
            if (
                instruccion == 0b00000000000000000000000000000000
            ):  # Código de operación 0 "PARAR"
                print("Ejecución finalizada.")
                break
            else:
                self.decodificar_y_ejecutar(instruccion)  # Ejecutar la instrucción
                self.pc += 1  # Incrementar el puntero de instrucción hasta que se ejecute la instrucción de parar

    """
    ---------------------------------------------------------------------------------------------------------


    FORMATO DE OPERACIONES Y ASIGNACIÓN DE OPCODE DREAMCHASER


    ---------------------------------------------------------------------------------------------------------
    """

    def decodificar_y_ejecutar(self, instruccion):
        """Carga y almacenamiento entre registro y memoria"""
        opcode = instruccion & 0xFFFFC000
        opcode1 = instruccion & 0xFFFFC000
        opcode2 = instruccion & 0xFFFFF800
        opcode3 = instruccion & 0xFFFFFFC0
        reg1 = (instruccion & 0x00003800) >> 11  # Registro 1
        direccion = instruccion & 0x000007FF  # direccion de memoria

        # Llamar la función correspondiente al opcode, si existe
        if opcode in self.operaciones_registro_memoria:
            self.operaciones_registro_memoria[opcode](reg1, direccion)
        elif opcode1 in self.operaciones_registro_valor:
            """Carga y almacenamiento entre registro y memoria"""
            reg1 = (instruccion & 0x00003800) >> 11  # Registro 1
            valor = instruccion & 0x000007FF  # Valor inmediato
            self.operaciones_registro_valor[opcode1](reg1, valor)
        elif opcode2 in self.operaciones_salto:
            """Operaciones de salto"""
            direccion = instruccion & 0x000007FF  # dirección de salto
            self.operaciones_salto[opcode2](direccion)
        elif opcode3 in self.operaciones_registros:
            reg1 = (instruccion & 0x00000038) >> 3
            reg2 = instruccion & 0x00000007
            self.operaciones_registros[opcode3](reg1, reg2)
        else:
            print(f"Operación desconocida: {opcode}")

    """--------------------------------------------
    OPERACIONES ENTRE REGISTRO Y MEMORIA
    ------------------------------------------------"""

    def cargar(self, reg1, direccion):
        """CARGAR R1, M[valor]"""
        self.registros[reg1] = int(self.memoria[direccion], 2)

    def almacenar(self, reg1, direccion):
        """ALMACENAR R1, M[valor]"""
        self.memoria[direccion] = format(self.registros[reg1], "032b")

    """---------------------------------------------
    OPERACIONES ENTRE REGISTRO Y VALORES
    ------------------------------------------------"""

    def lsl(self, reg1, valor):
        """LSL R1, valor"""
        self.registros[reg1] = self.registros[reg1] << valor

    def lsr(self, reg1, valor):
        """LSR (Logical Shift Right) R1, valor"""
        # Desplazamiento lógico a la derecha
        self.registros[reg1] = (self.registros[reg1] & 0xFFFFFFFF) >> valor

    def asr(self, reg1, valor):
        """ASR R1, valor"""
        self.registros[reg1] = self.registros[reg1] >> valor

    def cargar_valor(self, reg1, valor):
        """CARGAR VALOR R1, valor"""
        self.registros[reg1] = valor

    def rotacionl(self, reg1, valor):
        """ROTACION IZQUIERDA R1, valor"""
        self.registros[reg1] = (self.registros[reg1] << valor) | (
            self.registros[reg1] >> (32 - valor)
        )

    def rotacionr(self, reg1, valor):
        """ROTACION DERECHA R1, valor"""
        self.registros[reg1] = (self.registros[reg1] >> valor) | (
            self.registros[reg1] << (32 - valor)
        )

    """-------------------------------
    OPERACIONES DE SALTO
    ----------------------------------"""

    def saltar_si_cero(self, direccion):
        """SALTAR SI CERO M[valor]"""
        if self.bandera_zero == 1:
            self.pc = direccion - 1

    def saltar_si_positivo(self, direccion):
        """SALTAR SI POSITIVO M[valor]"""
        if self.bandera_neg == 0:
            self.pc = direccion - 1

    def saltar_si_negativo(self, direccion):
        """SALTAR SI NEGATIVO M[valor]"""
        if self.bandera_neg == 1:
            self.pc = direccion - 1

    def saltar_si_par(self, direccion):
        """SALTAR SI PAR M[valor]"""
        if self.bandera_par == 1:
            self.pc = direccion - 1

    def saltar_si_carry(self, direccion):
        """SALTAR SI CARRY M[valor]"""
        if self.bandera_carry == 1:
            self.pc = direccion - 1

    def saltar_si_desbordamiento(self, direccion):
        """SALTAR SI DESBORDAMIENTO M[valor]"""
        if self.bandera_desb == 1:
            self.pc = direccion - 1

    def saltar(self, direccion):
        """SALTAR M[valor]"""
        self.pc = direccion - 1

    def saltar_si_no_desbordamiento(self, direccion):
        """SALTAR SI NO DESBORDAMIENTO M[valor]"""
        if self.bandera_desb == 0:
            self.pc = direccion - 1

    """-----------------------------------------------------------------
    OPERACIONES ENTRE REGISTROS R1 Y R2 CON ACTUALIZACIÓN DE BANDERAS
    ----------------------------------------------------------------------"""

    def or_(self, reg1, reg2):
        """OR R1, R2"""
        self.registros[reg1] = self.registros[reg1] | self.registros[reg2]

    def and_(self, reg1, reg2):
        """AND R1, R2"""
        self.registros[reg1] = self.registros[reg1] & self.registros[reg2]

    def xor_(self, reg1, reg2):
        """XOR R1, R2"""
        self.registros[reg1] = self.registros[reg1] ^ self.registros[reg2]

    def not_(self, reg1):
        """NOT R1"""
        self.registros[reg1] = ~self.registros[reg1]

    def sumar(self, reg1, reg2):
        """SUMAR R1, R2"""
        resultado = self.registros[reg1] + self.registros[reg2]
        self.bandera_carry = 1 if resultado > 0xFFFFFFFF else 0
        # Esto permite que la bandera de desbordamiento se active si el resultado es inconsistente
        self.bandera_desb = 1 if resultado > 0xFFFFFFFF else 0
        self.bandera_par = 1 if resultado % 2 == 0 else 0
        self.bandera_neg = 1 if resultado < 0 else 0
        self.bandera_zero = 1 if resultado == 0 else 0
        if (
            self.registros[reg1] > 0 and self.registros[reg2] > 0 and resultado < 0
        ) or (self.registros[reg1] < 0 and self.registros[reg2] < 0 and resultado >= 0):
            self.bandera_desb = 1
        self.registros[reg1] = (
            resultado & 0xFFFFFFFF
        )  # Solo se almacenan los 32 bits menos significativos

    def restar(self, reg1, reg2):
        """RESTAR R1, R2"""
        resultado = self.registros[reg1] - self.registros[reg2]
        self.bandera_carry = 1 if resultado < 0 else 0
        # Esto permite que la bandera de desbordamiento se active si el resultado es inconsistente
        self.bandera_par = 1 if resultado % 2 == 0 else 0
        self.bandera_neg = 1 if resultado < 0 else 0
        self.bandera_zero = 1 if resultado == 0 else 0
        if (
            self.registros[reg1] > 0 and self.registros[reg2] > 0 and resultado < 0
        ) or (self.registros[reg1] < 0 and self.registros[reg2] < 0 and resultado >= 0):
            self.bandera_desb = 1
        self.registros[reg1] = resultado & 0xFFFFFFFF

    def multiplicar(self, reg1, reg2):
        """MULT R1, R2"""
        resultado = self.registros[reg1] * self.registros[reg2]
        self.bandera_carry = 1 if resultado > 0xFFFFFFFF else 0
        self.bandera_zero = 1 if resultado == 0 else 0
        self.bandera_zero = 1 if resultado == 0 else 0
        self.bandera_par = 1 if resultado % 2 == 0 else 0
        self.bandera_neg = 1 if resultado < 0 else 0
        if (
            self.registros[reg1] > 0 and self.registros[reg2] > 0 and resultado < 0
        ) or (self.registros[reg1] < 0 and self.registros[reg2] < 0 and resultado >= 0):
            self.bandera_desb = 1
        self.registros[reg1] = resultado & 0xFFFFFFFF

    def dividir(self, reg1, reg2):
        """DIV R1, R2"""
        cociente = self.registros[reg1] // self.registros[reg2]
        residuo = self.registros[reg1] % self.registros[reg2]

        self.bandera_carry = 1 if cociente > 0xFFFFFFFF else 0
        self.bandera_zero = 1 if cociente == 0 else 0
        self.bandera_par = 1 if cociente % 2 == 0 else 0
        self.bandera_neg = 1 if cociente < 0 else 0
        if (self.registros[reg1] > 0 and self.registros[reg2] > 0 and cociente < 0) or (
            self.registros[reg1] < 0 and self.registros[reg2] < 0 and cociente >= 0
        ):
            self.bandera_desb = 1

        self.registros[reg1] = cociente & 0xFFFFFFFF
        self.registros[reg2] = residuo & 0xFFFFFFFF

    def copiar(self, reg1, reg2):
        """COPIAR R1, R2"""
        self.registros[reg2] = self.registros[reg1]

    def comparar(self, reg1, reg2):
        """COMP R1, R2"""
        resultado = self.registros[reg1] - self.registros[reg2]
        self.bandera_zero = 1 if resultado == 0 else 0
        self.bandera_neg = 1 if resultado < 0 else 0
        self.bandera_carry = 1 if resultado < 0 else 0

    def intercambiar(self, reg1, reg2):
        """INTERCAMBIAR R1, R2"""
        self.registros[reg1], self.registros[reg2] = (
            self.registros[reg2],
            self.registros[reg1],
        )

    def modulo(self, reg1, reg2):
        """MOD R1, R2"""
        if self.registros[reg2] == 0:
            print(
                f"Error: División por cero en la operación MOD entre R{reg1} y R{reg2}"
            )
            return
        resultado = self.registros[reg1] % self.registros[reg2]
        self.bandera_carry = 1 if resultado > 0xFFFFFFFF else 0
        self.bandera_zero = 1 if resultado == 0 else 0
        self.bandera_par = 1 if resultado % 2 == 0 else 0
        self.bandera_neg = 1 if resultado < 0 else 0
        self.registros[reg1] = resultado & 0xFFFFFFFF

    """
    IMPRIMIR ESTADO DEL COMPUTADOR A TRAVÉS DEL CUAL SE PUEDEN INTERPRETAR RESULTADOS
    """

    def imprimir_estado(self, direccion_inicio=0, programa=[]):
        """Imprime el estado actual de DREAMCHASER"""
        print("Registros:", self.registros)
        print(
            "------------------------------------------------------------\n"
            "Banderas:\n"
        )
        print("Bandera Carry:", self.bandera_carry)
        print("Bandera Zero:", self.bandera_zero)
        print("Bandera Negativo:", self.bandera_neg)
        print("Bandera Par:", self.bandera_par)
        print("Bandera Desbordamiento:", self.bandera_desb)
        print("------------------------------------------------------------\n")
        print("------------------------------------------------------------\n")
        print(
            f"A continuación se muestran las primeras 16 instrucciones del programa en la memoria del computador"
        )

        print(
            "Memoria:", self.memoria[direccion_inicio : direccion_inicio + 16]
        )  # Solo las primeras 16 celdas
        print("------------------------------------------------------------\n")
        print("------------------------------------------------------------\n")
        print(
            "A continuación se muestran las siguientes 16 instrucciones luego de la agregar las instrucciones al computador, deben corresponder con el espacio en el que se modifiquen instrucciones"
        )
        print("Memoria:", self.memoria[len(programa) : len(programa) + 16])
        print("------------------------------------------------------------\n")
        print()


# A. Euclides
# Crear una instancia de la computadora
dreamchaser = Computadora()

# # Programa de prueba en formato binario (simple)
# # Formato: [opcode][reg1][reg2][valor_inmediato o dirección]
# programa = [
#     "00000000000000010000001000000000",  # Cargar      A,a CARGO 512
#     "00000000000000010000101000000001",  # Cargar      B,b CARGO 513
#     "00000000000000000000001001000010",  # bucle: Copiar A, C
#     "00000000000000000000000110010001",  # Restar      C,B
#     "00000000000000000000100100001010",  # SaltarSiCero fin
#     "00000000000000000001100100001000",  # SaltarSiNegativo menor
#     "00000000000000000000000110000001",  # Restar      A,B
#     "00000000000000000011100100000010",  # Saltar bucle
#     "00000000000000000000000110001000",  # menor: Restar B,A
#     "00000000000000000011100100000010",  # Saltar bucle
#     "00000000000000011000000000001100",  # Verdadero: Almacenar D,m GUARDO EN 12
#     "00000000000000000000000000000000",  # Parar
# ]


# # Cargar datos iniciales en memoria, ojo estos datos deben agregarse
# # luego de los datos del programa para un programa con 3 instrucciones
# # estos datos iniciales se guardan desde la dirección 3 en adelante

# # Cargando datos en memoria directamente, HAY QUE TENER EN CUENTA CÓDIGO RELOCALIZABLE.
# comp.memoria[768] = "00000000000000000000000010000000"  # M[768] = 128
# comp.memoria[769] = "00000000000000000000000000000111"  # M[769] = 7
# direccion_inicio = 256


# # # Cargar el programa en memoria
# comp.cargar_codigo(programa, direccion_inicio)
# print(comp.mostrar_memoria())

# # # Ejecutar el programa
# comp.ejecutar(direccion_inicio)

# # # Imprimir el estado final
# comp.imprimir_estado(direccion_inicio, programa)
