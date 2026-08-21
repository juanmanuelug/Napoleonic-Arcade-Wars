"""Bayoneta calada en TODOS los sprites del soldado ingles.

    python herramientas/bayoneta.py

El soldado lleva la bayoneta puesta siempre, asi que tiene que verse en las tres poses. Y en cada
una el mosquete apunta a otro sitio, asi que hay tres casos:

  - ANDANDO (14 sprites): el mosquete va en vertical y la boca esta en la fila 0. La hoja va
    hacia arriba, y hay que darle filas nuevas al lienzo por arriba.
  - APUNTANDO (2): el mosquete va en horizontal y la boca toca el borde. La hoja va hacia
    delante, y hay que darle columnas nuevas por delante.
  - DISPARANDO (2): el mosquete va en horizontal pero la boca queda DENTRO de la humareda del
    fogonazo. Ahi no hay que crecer nada, hay que pintar la hoja encima del humo, y en un acero
    mas oscuro, porque el humo es casi blanco y un acero claro no se veria.

Nada de esto descoloca el cuerpo: render.desplazamiento ancla por los pies y por el borde de
atras, asi que crecer por arriba o por delante es gratis. Hay pruebas que lo comprueban en los
dos lados y en las tres poses.

Los sprites originales NO se tocan: cada uno saca su variante con el sufijo _bayoneta, igual que
el voltigeur y el oficial salen de los sprites del frances. Asi el script se puede volver a pasar
cuantas veces haga falta sin calar una bayoneta encima de otra, y quitarla es cambiar tres listas
en jugador.py.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), 'pruebas'))
import entorno
import pygame

CARPETA = 'sprites/ingleses'
LADOS = ('izq', 'dch')

ACERO = (206, 206, 206)          # la hoja
ACERO_FILO = (240, 240, 240)     # su brillo
ACERO_EN_EL_HUMO = (138, 138, 138)   # mas oscuro, para que se vea contra la humareda
NEGRO = (12, 12, 12)             # el encaje, para que la hoja no salga flotando

OPACO = 20
# Un pixel se da por humo si es casi blanco: es lo que distingue la humareda del canion
CLARO_DEL_HUMO = 150
# Y por canion si es oscuro
OSCURO_DEL_CANION = 90

# La hoja mirando hacia delante (poses de apuntar): 5 de acero y una de encaje
COLUMNAS_NUEVAS = 6
CAPA_DELANTE = [
    "FAAAAn",
    "nnnnnn",
]
# La hoja hacia arriba (poses de andar). El lienzo crece estas filas
FILAS_NUEVAS = 5
CAPA_ARRIBA = [
    ".F",
    "AF",
    "AF",
    "AF",
    "nn",
]
# La hoja dentro del humo: solo la hoja, sin encaje, porque va pintada sobre el propio humo
LARGO_EN_EL_HUMO = 6

PALETA = {'.': None, 'A': ACERO, 'F': ACERO_FILO, 'n': NEGRO}


def _opacos(imagen, y):
    ancho = imagen.get_width()
    return [x for x in range(ancho) if imagen.get_at((x, y))[3] > OPACO]


def bocaDeArriba(imagen):
    """(columnas, fila) de la boca del canion cuando el mosquete va en vertical."""
    for y in range(imagen.get_height()):
        columnas = _opacos(imagen, y)
        if columnas:
            if len(columnas) > 3:
                raise ValueError("la fila de arriba tiene %d pixeles: no parece un canion"
                                 % len(columnas))
            return columnas, y
    raise ValueError("el sprite esta vacio")


def filaDelCanion(imagen):
    """La fila mas ancha: la del mosquete cruzando el lienzo en horizontal."""
    mejor, mejorAncho = None, 0
    for y in range(imagen.get_height()):
        cuantos = len(_opacos(imagen, y))
        if cuantos > mejorAncho:
            mejor, mejorAncho = y, cuantos
    if mejorAncho < 18:
        raise ValueError("no se encuentra el canion (la fila mas ancha mide %d)" % mejorAncho)
    return mejor


def bocaEnElHumo(imagen, fila):
    """La columna donde acaba el canion y empieza la humareda, en la fila del canion."""
    for x in range(imagen.get_width()):
        color = imagen.get_at((x, fila))
        if color[3] <= OPACO:
            continue
        luz = (color[0] + color[1] + color[2]) / 3
        if luz < OSCURO_DEL_CANION:
            return x
    raise ValueError("no se encuentra la boca dentro del humo")


def pintar(imagen, capa, columna, fila):
    for y, filaDeLaCapa in enumerate(capa):
        for x, letra in enumerate(filaDeLaCapa):
            color = PALETA[letra]
            if not color:
                continue
            destinoX, destinoY = columna + x, fila + y
            if 0 <= destinoX < imagen.get_width() and 0 <= destinoY < imagen.get_height():
                imagen.set_at((destinoX, destinoY), color + (255,))


def conMargen(imagen, columnas=0, filas=0):
    ancho, alto = imagen.get_size()
    crecido = pygame.Surface((ancho + columnas, alto + filas), pygame.SRCALPHA)
    crecido.blit(imagen, (columnas, filas))
    return crecido


def calarAndando(imagen):
    """La hoja hacia arriba, saliendo de la boca del canion vertical."""
    columnas, fila = bocaDeArriba(imagen)
    crecido = conMargen(imagen, filas=FILAS_NUEVAS)
    pintar(crecido, CAPA_ARRIBA, min(columnas), fila)
    return crecido


def calarApuntando(imagen):
    """La hoja hacia delante. La imagen tiene que venir mirando a la izquierda."""
    fila = filaDelCanion(imagen)
    crecido = conMargen(imagen, columnas=COLUMNAS_NUEVAS)
    pintar(crecido, CAPA_DELANTE, 0, fila)
    return crecido


def calarDisparando(imagen):
    """La hoja pintada sobre la humareda. La imagen tiene que venir mirando a la izquierda."""
    fila = filaDelCanion(imagen)
    boca = bocaEnElHumo(imagen, fila)
    copia = imagen.copy()
    desde = max(0, boca - LARGO_EN_EL_HUMO)
    for x in range(desde, boca):
        copia.set_at((x, fila), ACERO_EN_EL_HUMO + (255,))
        if fila + 1 < copia.get_height():
            copia.set_at((x, fila + 1), NEGRO + (255,))
    return copia


def piezas():
    """(fichero, como se cala). El de disparar va aparte porque su boca esta en el humo."""
    lista = []
    for lado in LADOS:
        for numero in range(7):
            lista.append(('soldado_ingles_%s_%d.png' % (lado, numero), 'andando', lado))
        lista.append(('soldado_ingles_%s_disparar_1.png' % lado, 'apuntando', lado))
        lista.append(('soldado_ingles_%s_disparar.png' % lado, 'disparando', lado))
    return lista


def conBayoneta(fichero):
    """El nombre de la variante: el mismo con el sufijo _bayoneta."""
    return fichero[:-len('.png')] + '_bayoneta.png'


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))

    hechos = []
    for fichero, como, lado in piezas():
        base = pygame.image.load(os.path.join(CARPETA, fichero)).convert_alpha()

        #se trabaja siempre mirando a la izquierda cuando la hoja va hacia delante
        volteado = lado == 'dch' and como != 'andando'
        trabajo = pygame.transform.flip(base, True, False) if volteado else base
        if como == 'andando':
            calado = calarAndando(trabajo)
        elif como == 'apuntando':
            calado = calarApuntando(trabajo)
        else:
            calado = calarDisparando(trabajo)
        if volteado:
            calado = pygame.transform.flip(calado, True, False)
        pygame.image.save(calado, os.path.join(CARPETA, conBayoneta(fichero)))
        hechos.append((conBayoneta(fichero), como, base.get_size(), calado.get_size()))

    for fichero, como, antes, luego in hechos:
        print("%-42s %-11s %2dx%-2d -> %2dx%-2d" % (fichero, como, antes[0], antes[1],
                                                    luego[0], luego[1]))
    print("%d sprites con la bayoneta calada, sin tocar ni uno de los originales" % len(hechos))

    ESCALA = 7
    muestra = [conBayoneta('soldado_ingles_izq_%d.png' % numero) for numero in range(7)]
    muestra += [conBayoneta('soldado_ingles_izq_disparar_1.png'),
                conBayoneta('soldado_ingles_izq_disparar.png')]
    imagenes = [pygame.image.load(os.path.join(CARPETA, nombre)).convert_alpha()
                for nombre in muestra]
    ancho = sum(i.get_width() for i in imagenes) * ESCALA + 14 * (len(imagenes) + 1)
    alto = max(i.get_height() for i in imagenes) * ESCALA + 28
    hoja = pygame.Surface((ancho, alto))
    hoja.fill((96, 150, 88))
    x = 14
    for imagen in imagenes:
        grande = pygame.transform.scale(imagen, (imagen.get_width() * ESCALA,
                                                 imagen.get_height() * ESCALA))
        hoja.blit(grande, (x, alto - 14 - grande.get_height()))
        x += grande.get_width() + 14
    pygame.image.save(hoja, os.path.join(entorno.CAPTURAS, 'bayoneta.png'))
    print("guardada bayoneta.png (los 7 de andar, apuntar y disparar, mirando a la izquierda)")


main()
