"""El jefe granadero: el granadero de la Guardia al doble de tamanio y con galon.

    python herramientas/jefe_granadero.py

Dos pasos, y en este orden:

  1. ESCALAR x2, no x1,6. Escalar arte de pixel por un numero no entero reparte mal los pixeles
     (unos salen de 1x1 y otros de 2x2) y el sprite se ve sucio. A x2 cada pixel del original es
     un cuadrado limpio de 2x2.
  2. GALON encima. Ya escalado hay sitio para detalle de un pixel, y ese contraste entre el
     cuerpo a bloques de 2x2 y los detalles finos es justo lo que hace que se lea como un jefe y
     no como el mismo granadero visto de cerca.

El galon se ancla en la PLACA DE LATON del bonete, que es el punto mas reconocible que tiene: un
cuadrado de 4x4 (2x2 en el original) de un color que no se repite en ningun otro sitio. La cabeza
se mueve de un fotograma a otro y la placa se mueve con ella.

Todas las piezas de galon pintan SOLO donde ya hay cuerpo. Un jefe no necesita que le sobresalga
nada nuevo, y asi ninguna pieza puede quedarse flotando en el aire.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), 'pruebas'))
import entorno
import pygame

CARPETA = 'sprites/franceses'
ORIGEN = 'granadero_fr_%s_%d.png'
DESTINO = 'jefegranadero_fr_%s_%d.png'
LADOS = ('izq', 'dch')
FOTOGRAMAS = range(7)

DOBLE = 2

LATON = (198, 156, 48)          # el que ya tiene el sprite: sirve de ancla
ORO = (214, 172, 60)
ORO_CLARO = (240, 206, 116)
ORO_SOMBRA = (140, 104, 28)
NEGRO = (8, 8, 8)

PALETA = {'.': None, 'O': ORO, 'C': ORO_CLARO, 'S': ORO_SOMBRA, 'n': NEGRO}

# Cada pieza de galon: (desplazamiento respecto a la esquina de la placa, dibujo)
PIEZAS_DE_GALON = (
    #la placa del bonete: el cuadrado de 4x4 que ya tenia, con un reborde claro que le da relieve.
    #Nada mas en el bonete: probado con un galon en el borde de abajo, y la placa y el galon se
    #juntaban en una sola mancha dorada que dejaba de leerse como piel de oso negra
    ((-1, -1), ["nCCCCn",
                "COOOOC",
                "COSSOC",
                "COSSOC",
                "COOOOC",
                "nCCCCn"]),
    #la charretera del hombro de delante, que es la marca que mas dice oficial. Grande, porque
    #pequenia no se veia a la escala del juego
    ((-8, 13), ["...CCCC.",
                "..COOOOC",
                ".COOOOOS",
                "COOOOOS.",
                "SOOOOS..",
                ".SSSS..."]),
    #y los botones de la casaca
    ((-3, 20), ["OO"]),
    ((-3, 24), ["OO"]),
)

OPACO = 20


def esquinaDeLaPlaca(imagen):
    """(columna, fila) de la esquina alta izquierda de la placa de laton."""
    ancho, alto = imagen.get_size()
    for y in range(alto):
        for x in range(ancho):
            if imagen.get_at((x, y))[:3] == LATON and imagen.get_at((x, y))[3] > OPACO:
                return x, y
    raise ValueError("no se encuentra la placa de laton del bonete")


def aplicar(imagen):
    """La imagen ya al doble, con el galon pintado. Tiene que venir mirando a la izquierda."""
    doble = pygame.transform.scale(imagen, (imagen.get_width() * DOBLE,
                                            imagen.get_height() * DOBLE))
    columna, fila = esquinaDeLaPlaca(doble)
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
                    raise ValueError("la pieza en %s usa %r, fuera de la paleta" % ((dx, dy), letra))

    jefes = []
    for lado in LADOS:
        for numero in FOTOGRAMAS:
            base = pygame.image.load(os.path.join(CARPETA, ORIGEN % (lado, numero))).convert_alpha()
            #se trabaja mirando a la izquierda: el galon va al hombro de delante y a la casaca,
            #y eso cambia de lado segun a donde mire
            miraADerecha = lado == 'dch'
            trabajo = pygame.transform.flip(base, True, False) if miraADerecha else base
            jefe = aplicar(trabajo)
            if miraADerecha:
                jefe = pygame.transform.flip(jefe, True, False)
            destino = DESTINO % (lado, numero)
            pygame.image.save(jefe, os.path.join(CARPETA, destino))
            jefes.append(jefe)
            print("%-32s %2dx%-2d -> %2dx%-2d" % (destino, base.get_width(), base.get_height(),
                                                  jefe.get_width(), jefe.get_height()))

    ESCALA = 4
    tropa = pygame.image.load(os.path.join(CARPETA, 'granadero_fr_izq_0.png')).convert_alpha()
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
    pygame.image.save(hoja, os.path.join(entorno.CAPTURAS, 'jefe_granadero.png'))
    print("guardados %d sprites y la hoja jefe_granadero.png (el primero es la tropa, a escala)"
          % len(jefes))


main()
