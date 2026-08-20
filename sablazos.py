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
