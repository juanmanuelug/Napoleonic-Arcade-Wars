import math

import pygame

pygame.init()

# ######################################### Sablazos ##################################################
# El rastro que deja la hoja cuando la tropa de cuerpo a cuerpo suelta el tajo. No es un sprite:
# es un arco de bloques dibujado sobre la marcha, como el fogonazo de la granada.
#
# El arco no se queda quieto y se apaga, BARRE: primero crece desde donde acaba el alzado (el
# sable casi vertical) hasta donde queda el brazo extendido, y despues se le va deshaciendo la
# cola, asi que parece que la hoja ha pasado por ahi en vez de que ha aparecido una raya.
#
# Dura menos que el propio fotograma del tajo (enemigo.DURACION_TAJO): el rastro se apaga y el
# soldado se queda un instante con el brazo estirado, que es lo que hace que se lea el golpe.
DURACION_SABLAZO = 160
# Del arco entero, la parte del tiempo que tarda en barrerlo. El resto es la cola deshaciendose
FRACCION_DEL_BARRIDO = 0.45
# Radio del arco, contado desde la empunadura. La hoja mide 10 px medidos en el sprite, asi que
# el rastro pasa 3 px por fuera de la punta
RADIO = 13
# En cuantos trozos se parte el arco, y lo gordo que es cada trozo
BLOQUES = 9
GROSOR = 2
# De donde a donde barre, en grados, contando como en matematicas (0 a la derecha, 90 arriba).
# La hoja del fotograma del tajo apunta a 127 grados, medido pixel a pixel, asi que el arco se
# reparte a los dos lados de esa linea: entra por arriba, donde la deja el alzado, y sale por
# delante, ya pasada
ANGULO_INICIAL = 97
BARRIDO = 60
# El filo va delante y brilla; detras queda el gris de la hoja del sprite (192, 192, 192)
COLOR_FILO = (238, 238, 238)
COLOR_RASTRO = (192, 192, 192)
BLOQUES_DE_FILO = 2


class Sablazo(object):
    """El rastro de una hoja, anclado a la mano que la mueve."""

    def __init__(self, x, y, mirandoIzq, ahora):
        self.x = float(x)
        self.y = float(y)
        self.mirandoIzq = mirandoIzq
        self.instante = ahora

    def terminado(self, ahora):
        return ahora - self.instante >= DURACION_SABLAZO

    def _puntoDelArco(self, indice):
        """El centro del bloque numero indice, de 0 (donde empieza) a BLOQUES - 1 (donde acaba)."""
        parte = indice / float(BLOQUES - 1)
        grados = ANGULO_INICIAL + BARRIDO * parte
        if not self.mirandoIzq:
            #el mismo arco del otro lado: 180 menos el angulo lo espeja en vertical
            grados = 180 - grados
        radianes = math.radians(grados)
        #la y de la pantalla crece hacia abajo, de ahi el menos
        return (int(round(self.x + math.cos(radianes) * RADIO)),
                int(round(self.y - math.sin(radianes) * RADIO)))

    def tramoVisible(self, ahora):
        """(primer bloque, ultimo bloque) que se ven en este instante."""
        avance = min(1.0, max(0.0, (ahora - self.instante) / float(DURACION_SABLAZO)))
        if avance <= FRACCION_DEL_BARRIDO:
            #la hoja va abriendo el arco: la cola sigue en el sitio de salida
            ultimo = int(round((BLOQUES - 1) * avance / FRACCION_DEL_BARRIDO))
            return 0, ultimo
        #ya esta abierto del todo: ahora se deshace por la cola
        sobra = (avance - FRACCION_DEL_BARRIDO) / (1.0 - FRACCION_DEL_BARRIDO)
        primero = int(round((BLOQUES - 1) * sobra))
        return primero, BLOQUES - 1

    def dibujar(self, win, ahora):
        primero, ultimo = self.tramoVisible(ahora)
        for indice in range(primero, ultimo + 1):
            centro = self._puntoDelArco(indice)
            #los ultimos bloques son el filo, que es lo que va por delante
            esFilo = indice > ultimo - BLOQUES_DE_FILO
            color = COLOR_FILO if esFilo else COLOR_RASTRO
            pygame.draw.rect(win, color, pygame.Rect(centro[0] - GROSOR // 2,
                                                     centro[1] - GROSOR // 2,
                                                     GROSOR, GROSOR))


def limpiar(sablazos, ahora):
    """Se queda con los que todavia se ven."""
    return [sablazo for sablazo in sablazos if not sablazo.terminado(ahora)]

# ######################################### Estocadas #################################################
# El destello de la bayoneta al entrar. No es un arco como el sable: una estocada va RECTA, asi que
# es una raya que sale disparada por delante del acero y se recoge. Sale y se recoge en vez de
# aparecer y apagarse por lo mismo que el sablazo barre: lo que se lee es el movimiento.
DURACION_ESTOCADA = 130
# Del tiempo total, lo que tarda en salir. El resto es recogerse
FRACCION_DE_SALIDA = 0.4
# Lo que se estira por delante del acero, y lo gorda que es la raya
LARGO_DE_LA_ESTOCADA = 14
GROSOR_DE_LA_ESTOCADA = 2
COLOR_DEL_ACERO = (240, 240, 240)
COLOR_DEL_RASTRO_DE_ACERO = (198, 198, 198)


class Estocada(object):
    """El destello recto de una bayoneta, anclado a la punta del acero.

    Vive en la misma lista que los sablazos y la limpia el mismo limpiar(): las dos cosas saben
    decir si han terminado y saben dibujarse, y no hacen falta dos listas para eso.
    """

    def __init__(self, x, y, mirandoIzq, ahora):
        self.x = float(x)
        self.y = float(y)
        self.mirandoIzq = mirandoIzq
        self.instante = ahora

    def terminado(self, ahora):
        return ahora - self.instante >= DURACION_ESTOCADA

    def largoVisible(self, ahora):
        """Cuanto mide la raya en este instante: sale rapido y se recoge."""
        avance = min(1.0, max(0.0, (ahora - self.instante) / float(DURACION_ESTOCADA)))
        if avance <= FRACCION_DE_SALIDA:
            parte = avance / FRACCION_DE_SALIDA
        else:
            parte = 1.0 - (avance - FRACCION_DE_SALIDA) / (1.0 - FRACCION_DE_SALIDA)
        return int(round(LARGO_DE_LA_ESTOCADA * max(0.0, parte)))

    def dibujar(self, win, ahora):
        largo = self.largoVisible(ahora)
        if largo <= 0:
            return
        hacia = -1 if self.mirandoIzq else 1
        for paso in range(largo):
            #la punta va delante y brilla; lo de detras es el rastro
            color = COLOR_DEL_ACERO if paso >= largo - 3 else COLOR_DEL_RASTRO_DE_ACERO
            x = int(self.x) + hacia * paso
            pygame.draw.rect(win, color, pygame.Rect(x, int(self.y),
                                                     1, GROSOR_DE_LA_ESTOCADA))

# ######################################### Barridos ##################################################
# La hoja dando la vuelta entera alrededor de quien la lleva: el ataque en area del jefe de sable.
# No es un arco delante (eso es el Sablazo) ni una raya recta (la Estocada), es un circulo completo.
#
# El radio es el MISMO que el alcance del golpe, a proposito: el jugador tiene que poder aprender
# hasta donde llega mirandolo, no muriendose. Quien lo crea le pasa su radio.
DURACION_BARRIDO = 300
# Vueltas que da la hoja en ese tiempo. Mas de una para que se lea como un giro y no como un arco
VUELTAS_DEL_BARRIDO = 1.25
# Lo que arrastra la hoja por detras, en grados: es lo que hace que parezca un giro y no un punto
COLA_DEL_BARRIDO = 110
# Un bloque por pixel de cola: con 26 la cola salia punteada, como una linea de puntos,
# en vez de una hoja. Al radio del tajo (82 px) esos 110 grados son unos 157 px de arco
BLOQUES_DEL_BARRIDO = 60
GROSOR_DEL_BARRIDO = 3


class Barrido(object):
    """La hoja girando alrededor de su duenio. Vive en la misma lista que los demas rastros."""

    def __init__(self, x, y, radio, ahora):
        self.x = float(x)
        self.y = float(y)
        self.radio = float(radio)
        self.instante = ahora

    def terminado(self, ahora):
        return ahora - self.instante >= DURACION_BARRIDO

    def anguloDeLaHoja(self, ahora):
        """Donde esta la punta de la hoja ahora mismo, en grados."""
        avance = min(1.0, max(0.0, (ahora - self.instante) / float(DURACION_BARRIDO)))
        return 360.0 * VUELTAS_DEL_BARRIDO * avance

    def dibujar(self, win, ahora):
        if self.terminado(ahora):
            return
        cabeza = self.anguloDeLaHoja(ahora)
        for bloque in range(BLOQUES_DEL_BARRIDO):
            #del mas viejo (el final de la cola) al mas nuevo (la punta)
            parte = bloque / float(BLOQUES_DEL_BARRIDO - 1)
            grados = cabeza - COLA_DEL_BARRIDO * (1.0 - parte)
            radianes = math.radians(grados)
            x = int(round(self.x + math.cos(radianes) * self.radio))
            y = int(round(self.y - math.sin(radianes) * self.radio))
            #la punta brilla y la cola se apaga hacia el gris de la hoja
            color = COLOR_DEL_ACERO if parte > 0.82 else COLOR_DEL_RASTRO_DE_ACERO
            pygame.draw.rect(win, color, pygame.Rect(x - GROSOR_DEL_BARRIDO // 2,
                                                     y - GROSOR_DEL_BARRIDO // 2,
                                                     GROSOR_DEL_BARRIDO, GROSOR_DEL_BARRIDO))
