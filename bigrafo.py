class Nodo:
    def __init__(self, id, tipo, valor=None):
        self.id = id
        self.tipo = tipo
        self.valor = valor
        self.lugares = []
        self.enlaces = []

    def agregar_lugar(self, nodo):
        self.lugares.append(nodo)

    def agregar_enlace(self, nodo):
        self.enlaces.append(nodo)

    def __repr__(self):
        return f"Nodo(id={self.id}, tipo={self.tipo}, valor={self.valor}, lugares={self.lugares}, enlaces={self.enlaces})"


class Bigrafo:
    def __init__(self):
        self.nodos = {}

    def agregar_nodo(self, id, tipo, valor=None):
        if id not in self.nodos:
            self.nodos[id] = Nodo(id, tipo, valor)
        return self.nodos[id]

    def agregar_lugar(self, id_padre, id_hijo):
        if id_padre in self.nodos and id_hijo in self.nodos:
            self.nodos[id_padre].agregar_lugar(self.nodos[id_hijo])

    def agregar_enlace(self, id_origen, id_destino):
        if id_origen in self.nodos and id_destino in self.nodos:
            self.nodos[id_origen].agregar_enlace(self.nodos[id_destino])

    def union(self, otro_bigrafo):
        nuevo_bigrafo = Bigrafo()
        # Copiar nodos y conexiones del primer bigrafo
        for id, nodo in self.nodos.items():
            nuevo_bigrafo.nodos[id] = nodo
        # Copiar nodos y conexiones del segundo bigrafo
        for id, nodo in otro_bigrafo.nodos.items():
            if id not in nuevo_bigrafo.nodos:
                nuevo_bigrafo.nodos[id] = nodo
            else:
                # Si el nodo ya existe, combinar lugares y enlaces
                nuevo_bigrafo.nodos[id].lugares.extend(nodo.lugares)
                nuevo_bigrafo.nodos[id].enlaces.extend(nodo.enlaces)
        return nuevo_bigrafo

    def interseccion(self, otro_bigrafo):
        nuevo_bigrafo = Bigrafo()
        for id, nodo in self.nodos.items():
            if id in otro_bigrafo.nodos:
                nuevo_bigrafo.nodos[id] = nodo
        return nuevo_bigrafo

    def diferencia(self, otro_bigrafo):
        nuevo_bigrafo = Bigrafo()
        for id, nodo in self.nodos.items():
            if id not in otro_bigrafo.nodos:
                nuevo_bigrafo.nodos[id] = nodo
        return nuevo_bigrafo

    def clonar(self):
        nuevo_bigrafo = Bigrafo()
        for id, nodo in self.nodos.items():
            nuevo_bigrafo.nodos[id] = nodo
        return nuevo_bigrafo

    def contar_lugares(self, id_nodo):
        if id_nodo in self.nodos:
            return len(self.nodos[id_nodo].lugares)
        return 0

    def contar_enlaces(self, id_nodo):
        if id_nodo in self.nodos:
            return len(self.nodos[id_nodo].enlaces)
        return 0

    def __repr__(self):
        return f"Bigrafo(nodos={self.nodos})"
