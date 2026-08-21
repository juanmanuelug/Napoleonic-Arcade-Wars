"""El jefe de cuerpo a cuerpo: el oficial al doble de tamanio y con mas galon.

    python herramientas/jefe_sable.py

Se parte del OFICIAL y no de la tropa, y eso ahorra la mitad del trabajo: el oficial ya es esa
misma figura con penacho y banda dorada en el chaco (ver herramientas/oficial.py). Aqui solo hay
que doblarlo y subirle el galon un escalon mas.

Igual que con el jefe granadero: x2 y no x1,6, porque escalar arte de pixel por un numero no
entero reparte mal los pixeles. A x2 cada pixel del oficial es un cuadrado limpio de 2x2, y encima
hay sitio para detalle de un pixel, que es el contraste que hace que se lea como un jefe.

El galon se ancla en el POMPON DE LATON del chaco, el color (246,185,0) que ya venia en el sprite
de la tropa: es el unico punto de referencia que no se mueve respecto a la cabeza, y la cabeza se
mueve mucho entre fotogramas.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), 'pruebas'))
import entorno
import pygame

CARPETA = 'sprites/franceses'
ORIGEN = 'oficial_fr_%s_cuerpoAcuerpo_%d.png'
DESTINO = 'jefesable_fr_%s_cuerpoAcuerpo_%d.png'
LADOS = ('izq', 'dch')
FOTOGRAMAS = range(7)

DOBLE = 2

LATON = (246, 185, 0)          # el pompon del chaco: el ancla
ORO = (214, 172, 60)           # el mismo dorado que usa el oficial
ORO_CLARO = (240, 206, 116)
ORO_SOMBRA = (176, 132, 30)

PALETA = {'.': None, 'O': ORO, 'C': ORO_CLARO, 'S': ORO_SOMBRA}

# Cada pieza de galon: (desplazamiento respecto al pompon, dibujo). Todas pintan SOLO sobre cuerpo
PIEZAS_DE_GALON = (
    #la charretera del hombro, mucho mas grande que la del oficial
    ((16, 30), ["..CCCCCC",
                ".COOOOOC",
                "COOOOOOS",
                "COOOOOS.",
                "SOOOOS..",
                ".SSSS..."]),
    #el galon del punio del brazo del sable
    ((2, 32), ["OOOO",
               "SSSS"]),
    #y el galon del faldon de la casaca
    ((8, 42), ["OOOOOOOO",
               "SSSSSSSS"]),
)

OPACO = 20


def esquinaDelPompon(imagen):
    """(columna, fila) del pixel de laton mas alto: el pompon de lo alto del chaco."""
    ancho, alto = imagen.get_size()
    for y in range(alto):
        for x in range(ancho):
            if imagen.get_at((x, y))[:3] == LATON and imagen.get_at((x, y))[3] > OPACO:
                return x, y
    raise ValueError("no se encuentra el pompon de laton del chaco")


def aplicar(imagen):
    """La imagen al doble y con el galon. Tiene que venir mirando a la izquierda."""
    doble = pygame.transform.scale(imagen, (imagen.get_width() * DOBLE,
                                            imagen.get_height() * DOBLE))
    columna, fila = esquinaDelPompon(doble)
    ancho, alto = doble.get_size()
    for (dx, dy), dibujo in PIEZAS_DE_GALON:
        for y, filaDelDibujo in enumerate(dibujo):
            for x, letra in enumerate(filaDelDibujo):
                color = PALETA[letra]
                if not color:
                    continue
                destinoX, destinoY = columna + dx + x, fila + dy + y
                if not (0 <= destinoX < ancho and 0 <= destinoY < alto):
                    continue
                #solo sobre cuerpo: un jefe no necesita que le sobresalga nada nuevo
                if doble.get_at((destinoX, destinoY))[3] <= OPACO:
                    continue
                doble.set_at((destinoX, destinoY), color + (255,))
    return doble


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    for (dx, dy), dibujo in PIEZAS_DE_GALON:
        if len(set(len(fila) for fila in dibujo)) != 1:
            raise ValueError("una pieza de galon tiene filas de distinto largo")
        for fila in dibujo:
            for letra in fila:
                if letra not in PALETA:
                    raise ValueError("la pieza en %s usa %r" % ((dx, dy), letra))

    jefes = []
    for lado in LADOS:
        for numero in FOTOGRAMAS:
            base = pygame.image.load(os.path.join(CARPETA, ORIGEN % (lado, numero))).convert_alpha()
            #se trabaja mirando a la izquierda: la charretera y el punio van al lado de delante
            miraADerecha = lado == 'dch'
            trabajo = pygame.transform.flip(base, True, False) if miraADerecha else base
            jefe = aplicar(trabajo)
            if miraADerecha:
                jefe = pygame.transform.flip(jefe, True, False)
            destino = DESTINO % (lado, numero)
            pygame.image.save(jefe, os.path.join(CARPETA, destino))
            jefes.append(jefe)
            print("%-38s %2dx%-2d -> %2dx%-2d" % (destino, base.get_width(), base.get_height(),
                                                  jefe.get_width(), jefe.get_height()))

    ESCALA = 4
    tropa = pygame.image.load(os.path.join(CARPETA, 'oficial_fr_izq_cuerpoAcuerpo_3.png')).convert_alpha()
    piezas = [tropa] + jefes[:7]
    ancho = sum(p.get_width() for p in piezas) * ESCALA + 14 * (len(piezas) + 1)
    alto = max(p.get_height() for p in piezas) * ESCALA + 28
    hoja = pygame.Surface((ancho, alto))
    hoja.fill((96, 150, 88))
    x = 14
    for pieza in piezas:
        grande = pygame.transform.scale(pieza, (pieza.get_width() * ESCALA,
                                                pieza.get_height() * ESCALA))
        hoja.blit(grande, (x, alto - 14 - grande.get_height()))
        x += grande.get_width() + 14
    pygame.image.save(hoja, os.path.join(entorno.CAPTURAS, 'jefe_sable.png'))
    print("guardados %d sprites y la hoja jefe_sable.png (el primero es el oficial, a escala)"
          % len(jefes))


main()
