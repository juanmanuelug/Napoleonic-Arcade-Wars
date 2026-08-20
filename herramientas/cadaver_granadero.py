"""Cadaver del granadero, hecho operando sobre el cadaver del soldado.

    python herramientas/cadaver_granadero.py

El granadero moria con el cadaver del soldado de linea, con su chaco, aunque en pie lleve bonete
de piel de oso. Este saca un cadaver propio: el mismo cuerpo tirado, con el bonete en vez del
chaco y con su penacho rojo.

El cadaver yace con la cabeza a la izquierda, y el chaco es el bulto oscuro de las columnas 1 a
7. El bonete es mas alto que el chaco, asi que la capa alarga ese bulto hacia arriba, que en el
lienzo esta libre (las filas 0 a 2 solo tienen el mosquete, a la derecha), y le saca el penacho
por delante en la columna 0.

Todo cabe SIN tocar el tamanio del lienzo, y eso importa: render.desplazamiento coloca los
sprites de mirar a la izquierda restando su ancho, asi que crecer por la izquierda habria
descolocado el cadaver de los que mueren mirando a la derecha.

Los colores no se inventan: el negro del contorno (4,4,4) y el relleno (31,31,31) son los
mismos numeros en el cadaver y en el granadero en pie, y el rojo del penacho y el laton estan
sacados de granadero_fr_izq_0.png.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), 'pruebas'))
import entorno
import pygame

CARPETA = 'sprites/franceses'
ORIGEN = 'cadaverOficialImg.png'
DESTINO = 'cadaver_granadero.png'

NEGRO = (4, 4, 4)            # contorno, igual en los dos sprites
PIEL_DE_OSO = (31, 31, 31)   # relleno del bonete, igual que el del chaco
PELO = (54, 54, 54)          # una pizca mas claro, para que el bonete no sea una mancha plana
ROJO = (130, 0, 0)
ROJO_BRILLO = (176, 32, 34)
LATON = (198, 156, 48)
LATON_SOMBRA = (140, 104, 28)

PALETA = {
    '.': None,
    'N': NEGRO,
    'P': PIEL_DE_OSO,
    'p': PELO,
    'R': ROJO,
    'r': ROJO_BRILLO,
    'L': LATON,
    'l': LATON_SOMBRA,
}

# La capa se pinta con su esquina en (0, 0) del lienzo del cadaver
CAPA = [
    "RR.NNNN.",
    "rRNPpPPN",
    "RrNPPPPN",
    "rRNPPPpN",
    "RR......",
    "r.......",
    "........",
    "...LL...",
    "...ll...",
]


def comprobarLaCapa():
    for numero, fila in enumerate(CAPA):
        if len(fila) != len(CAPA[0]):
            raise ValueError("la fila %d de la capa mide %d y no %d"
                             % (numero, len(fila), len(CAPA[0])))
        for letra in fila:
            if letra not in PALETA:
                raise ValueError("la fila %d usa %r, fuera de la paleta" % (numero, letra))


def aplicar(imagen):
    copia = imagen.copy()
    ancho, alto = copia.get_size()
    for y, fila in enumerate(CAPA):
        for x, letra in enumerate(fila):
            color = PALETA[letra]
            if color and x < ancho and y < alto:
                copia.set_at((x, y), color + (255,))
    return copia


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    comprobarLaCapa()

    base = pygame.image.load(os.path.join(CARPETA, ORIGEN)).convert_alpha()
    granadero = aplicar(base)
    pygame.image.save(granadero, os.path.join(CARPETA, DESTINO))
    print("%s  %dx%d -> %s  %dx%d"
          % (ORIGEN, base.get_width(), base.get_height(),
             DESTINO, granadero.get_width(), granadero.get_height()))

    ESCALA = 12
    enPie = pygame.image.load(os.path.join(CARPETA, 'granadero_fr_izq_0.png')).convert_alpha()
    piezas = [base, granadero, enPie]
    ancho = sum(p.get_width() for p in piezas) * ESCALA + 20 * (len(piezas) + 1)
    alto = max(p.get_height() for p in piezas) * ESCALA + 40
    hoja = pygame.Surface((ancho, alto))
    hoja.fill((96, 150, 88))
    x = 20
    for pieza in piezas:
        grande = pygame.transform.scale(pieza, (pieza.get_width() * ESCALA,
                                                pieza.get_height() * ESCALA))
        hoja.blit(grande, (x, alto - 20 - grande.get_height()))
        x += grande.get_width() + 20
    pygame.image.save(hoja, os.path.join(entorno.CAPTURAS, 'cadaver_granadero.png'))
    print("guardada cadaver_granadero.png (soldado, granadero y el granadero en pie)")


main()
