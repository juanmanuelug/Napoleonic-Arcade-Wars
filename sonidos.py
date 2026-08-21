import math
import random
import struct

import pygame

pygame.init()

# ##################################### Efectos de sonido ##############################################
# En el repo solo hay un wav (el mosquete) y la marcha, asi que el impacto y la muerte se
# sintetizan aqui: se construye el buffer de audio a mano y se le da al mezclador. Ni ficheros
# nuevos ni dependencias nuevas.
VOLUMEN_IMPACTO = 0.35
VOLUMEN_MUERTE = 0.30
VOLUMEN_OBJETO = 0.30
VOLUMEN_MOCHILA = 0.22
VOLUMEN_ESTALLIDO = 0.40
# El sable suena bajo y corto a proposito: con tres o cuatro franceses encima se oye ocho veces
# por segundo, y a mas volumen taparia los mosquetes, que es lo que de verdad hay que oir
VOLUMEN_SABLE = 0.16
# El dash suena a viento, no a clic. Puede ser mas largo y mas alto que el sable porque solo
# suena cuando el jugador lo pide, y como mucho una vez por segundo
VOLUMEN_DASH = 0.30
DURACION_IMPACTO = 0.055
DURACION_MUERTE = 0.240
DURACION_OBJETO = 0.130
DURACION_MOCHILA = 0.055
DURACION_ESTALLIDO = 0.360
DURACION_SABLE = 0.110
DURACION_DASH = 0.240


class SonidoNulo(object):
    """Sustituto cuando no hay mezclador (o no se pudo crear el sonido): no suena y no falla."""

    def play(self):
        pass

    def set_volume(self, volumen):
        pass


def _crear(generador, duracion, volumen):
    """Construye un pygame.Sound muestreando generador(t) en [-1, 1]."""
    formato = pygame.mixer.get_init()
    if not formato:
        return SonidoNulo()
    frecuencia, tamanio, canales = formato
    if abs(tamanio) != 16:
        #solo se sabe construir buffers de 16 bits; con otro formato, mejor callarse
        return SonidoNulo()
    total = int(frecuencia * duracion)
    tope = 32767
    muestras = bytearray()
    for indice in range(total):
        instante = indice / float(frecuencia)
        valor = generador(instante, indice / float(total))
        entero = int(max(-1.0, min(1.0, valor)) * tope * volumen)
        muestras += struct.pack('<h', entero) * canales
    try:
        return pygame.mixer.Sound(buffer=bytes(muestras))
    except pygame.error:
        return SonidoNulo()


def _impacto(instante, avance):
    #golpe seco: ruido que se apaga rapido sobre un tono grave que cae
    caida = (1.0 - avance) ** 3
    ruido = random.uniform(-1.0, 1.0) * 0.7
    cuerpo = math.sin(2 * math.pi * (220 - 120 * avance) * instante) * 0.5
    return (ruido + cuerpo) * caida


def _muerte(instante, avance):
    #caida al suelo: tono grave descendente con un temblor de ruido encima
    caida = (1.0 - avance) ** 2
    tono = math.sin(2 * math.pi * (160 - 110 * avance) * instante)
    tierra = random.uniform(-1.0, 1.0) * 0.25 * (1.0 - avance)
    return (tono * 0.8 + tierra) * caida


def _objeto(instante, avance):
    #dos notas hacia arriba, que es como suena gastar algo bueno
    nota = 660 if avance < 0.45 else 990
    corte = 1.0 - abs(avance - 0.5) * 0.8
    return math.sin(2 * math.pi * nota * instante) * corte


def _estallido(instante, avance):
    #un reventon: golpe de ruido que se apaga, sobre un tono grave que cae hasta el suelo
    caida = (1.0 - avance) ** 1.6
    ruido = random.uniform(-1.0, 1.0)
    grave = math.sin(2 * math.pi * (90 - 55 * avance) * instante)
    return (ruido * 0.75 + grave * 0.6) * caida


def _mochila(instante, avance):
    #un clic corto y seco: guardar algo no es lo mismo que usarlo
    return math.sin(2 * math.pi * 520 * instante) * ((1.0 - avance) ** 2)


def _sable(instante, avance):
    #el silbido de la hoja al pasar. La campana es lo que lo hace un silbido y no un siseo:
    #empieza en nada, revienta a la mitad y se va, o sea que algo ha pasado al lado. Encima, un
    #barrido de agudo a grave, que es como suena el metal cortando aire
    campana = math.sin(math.pi * avance) ** 2
    ruido = random.uniform(-1.0, 1.0)
    barrido = math.sin(2 * math.pi * (2600 - 1700 * avance) * instante)
    return (ruido * 0.75 + barrido * 0.35) * campana


# Lo que convierte el ruido en VIENTO es quitarle lo agudo. Un filtro de un polo basta: cada
# muestra tira de la anterior, y eso se lleva las frecuencias altas, que son el siseo. Por eso
# este generador necesita memoria y los otros no: va en un cierre con su propio estado.
SUAVIDAD_DEL_VIENTO = 0.055
# El filtro se come casi toda la amplitud, asi que hay que devolverla a mano
GANANCIA_DEL_VIENTO = 3.4


def _viento():
    """Devuelve un generador de soplo: ruido sin agudos, en campana. El zummm del dash."""
    memoria = {'valor': 0.0}

    def soplo(instante, avance):
        memoria['valor'] += (random.uniform(-1.0, 1.0) - memoria['valor']) * SUAVIDAD_DEL_VIENTO
        #campana asimetrica: entra de golpe y se va despacio, como algo que pasa y se aleja
        campana = math.sin(math.pi * min(1.0, avance * 1.15)) ** 1.4
        return memoria['valor'] * GANANCIA_DEL_VIENTO * campana

    return soplo


sonido_impacto = _crear(_impacto, DURACION_IMPACTO, VOLUMEN_IMPACTO)
sonido_muerte = _crear(_muerte, DURACION_MUERTE, VOLUMEN_MUERTE)
sonido_objeto = _crear(_objeto, DURACION_OBJETO, VOLUMEN_OBJETO)
sonido_mochila = _crear(_mochila, DURACION_MOCHILA, VOLUMEN_MOCHILA)
sonido_estallido = _crear(_estallido, DURACION_ESTALLIDO, VOLUMEN_ESTALLIDO)
sonido_sable = _crear(_sable, DURACION_SABLE, VOLUMEN_SABLE)
sonido_dash = _crear(_viento(), DURACION_DASH, VOLUMEN_DASH)
