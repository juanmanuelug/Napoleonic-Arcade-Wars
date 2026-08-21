import math

import pygame

import sonidos

pygame.init()

# ######################################### Granadas ##################################################
# Una granada no vuela con fisica: se lanza a un punto del suelo y tarda un tiempo fijo en caer.
# Mientras esta en el aire, el sitio donde va a caer queda marcado con un circulo rojo que
# parpadea cada vez mas rapido. Eso es lo que hace justa un arma de area: te avisa, y salirte
# depende de ti. Y de paso rompe la unica tactica que resolvia el juego entero, porque una
# granada no se esquiva poniendose a otra altura.
granadaImg = pygame.image.load('./sprites/granada.png')

# Lo que tarda desde que sale de la mano hasta que cae
TIEMPO_DE_VUELO = 1500
# Radio del estallido y lo que quita a quien pille dentro
RADIO = 40
DANIO = 22
# Cuanto sube la granada en lo alto del arco. Es solo dibujo: no cambia donde cae
ALTURA_DEL_ARCO = 34
# La marca del suelo
COLOR_MARCA = (206, 42, 42)
GROSOR_MARCA = 2
PARPADEOS_AL_PRINCIPIO = 3.0
PARPADEOS_AL_FINAL = 11.0
# El fogonazo del estallido
DURACION_ESTALLIDO = 260
COLOR_ESTALLIDO = (250, 226, 150)
COLOR_HUMO = (120, 116, 110)


def parpadeoVisible(transcurrido, avance):
    """Si en este instante la marca esta encendida. Parpadea mas rapido cuanto menos queda.

    Esta suelto y no dentro de Granada porque no es solo de las granadas: cualquier ataque que
    avise antes de caer usa este mismo lenguaje, y el jugador tiene que reconocerlo de un vistazo
    venga de donde venga.
    """
    ritmo = PARPADEOS_AL_PRINCIPIO + (PARPADEOS_AL_FINAL - PARPADEOS_AL_PRINCIPIO) * avance
    return int(transcurrido * ritmo * 2) % 2 == 0


def dibujarAviso(win, centro, radio):
    """El circulo rojo de "aqui va a caer algo". Va en el suelo, debajo de todo."""
    pygame.draw.circle(win, COLOR_MARCA, (int(centro[0]), int(centro[1])), int(radio), GROSOR_MARCA)
    pygame.draw.circle(win, COLOR_MARCA, (int(centro[0]), int(centro[1])), 2)


class Granada(object):
    """Una granada en el aire, con su punto de caida ya decidido."""

    def __init__(self, origenX, origenY, destinoX, destinoY, ahora):
        self.origen = (float(origenX), float(origenY))
        self.destino = (float(destinoX), float(destinoY))
        self.instanteLanzamiento = ahora

    def avance(self, ahora):
        """De 0 (recien lanzada) a 1 (tocando el suelo)."""
        return min(1.0, max(0.0, (ahora - self.instanteLanzamiento) / float(TIEMPO_DE_VUELO)))

    def haCaido(self, ahora):
        return ahora - self.instanteLanzamiento >= TIEMPO_DE_VUELO

    def posicion(self, ahora):
        """Donde se dibuja la granada: linea recta al destino, con el arco restado a la altura."""
        t = self.avance(ahora)
        x = self.origen[0] + (self.destino[0] - self.origen[0]) * t
        y = self.origen[1] + (self.destino[1] - self.origen[1]) * t
        return (x, y - math.sin(math.pi * t) * ALTURA_DEL_ARCO)

    def marcaVisible(self, ahora):
        """El parpadeo de la marca, cada vez mas rapido conforme se acerca el impacto."""
        return parpadeoVisible((ahora - self.instanteLanzamiento) / 1000.0, self.avance(ahora))

    def dibujarMarca(self, win, ahora):
        """El circulo rojo en el suelo. Va debajo de todo, para no tapar a nadie."""
        if not self.marcaVisible(ahora):
            return
        dibujarAviso(win, self.destino, RADIO)

    def dibujar(self, win, ahora):
        x, y = self.posicion(ahora)
        win.blit(granadaImg, granadaImg.get_rect(center=(int(x), int(y))))

    def alcanzados(self, objetivos):
        """Los que estan dentro del radio del estallido."""
        return [objetivo for objetivo in objetivos
                if math.hypot(objetivo.rect.centerx - self.destino[0],
                              objetivo.rect.centery - self.destino[1]) <= RADIO]


class Estallido(object):
    """El fogonazo que queda un instante donde cayo la granada."""

    def __init__(self, x, y, ahora):
        self.x = x
        self.y = y
        self.instante = ahora

    def terminado(self, ahora):
        return ahora - self.instante >= DURACION_ESTALLIDO

    def dibujar(self, win, ahora):
        avance = min(1.0, (ahora - self.instante) / float(DURACION_ESTALLIDO))
        radio = int(RADIO * (0.35 + 0.65 * avance))
        pygame.draw.circle(win, COLOR_HUMO, (int(self.x), int(self.y)), radio, 3)
        pygame.draw.circle(win, COLOR_ESTALLIDO, (int(self.x), int(self.y)),
                           max(1, int(radio * (1.0 - avance))))


def resolver(granadas, objetivos, ahora):
    """Explota las que han caido y devuelve (las que siguen en el aire, los estallidos nuevos)."""
    enElAire = []
    estallidos = []
    for granada in granadas:
        if not granada.haCaido(ahora):
            enElAire.append(granada)
            continue
        for alcanzado in granada.alcanzados(objetivos):
            alcanzado.recibirImpacto(DANIO)
        estallidos.append(Estallido(granada.destino[0], granada.destino[1], ahora))
        sonidos.sonido_estallido.play()
    return enElAire, estallidos


def limpiarEstallidos(estallidos, ahora):
    return [estallido for estallido in estallidos if not estallido.terminado(ahora)]
