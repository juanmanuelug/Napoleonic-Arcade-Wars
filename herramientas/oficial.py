"""Oficial frances, hecho operando sobre la tropa de cuerpo a cuerpo.

    python herramientas/oficial.py

Los sprites de cuerpo a cuerpo ya son una figura con SABLE, no con bayoneta, y con dorados en el
chaco y en la guarnicion. O sea que el oficial no hay que inventarlo: se le sube el galon a esa
misma figura. Salen 14 sprites (7 por lado), que cubren andar (del 2 al 6) y el sable (el 0 y el 1).

Las senias que caben a este tamanio:

  - penacho alto, dorado abajo y BLANCO en la punta, encima del pompon del chaco
  - banda dorada en el chaco

La capa se ancla en el POMPON del chaco, que es el pixel dorado mas alto del sprite. Es el mejor
anclaje que hay aqui: la cabeza se mueve mucho de un fotograma a otro (el pompon va de la columna
5 a la 13 segun como se incline la figura) y el pompon se mueve con ella, asi que buscandolo se
acierta en los 14 sin tocar la capa. Ojo: los sprites de mirar a la derecha tienen el dorado en
(245,184,0) y los de la izquierda en (246,185,0), un punto de diferencia, asi que se busca con
tolerancia y no por igualdad.

La banda solo pinta donde ya hay cuerpo: el chaco se estrecha hacia abajo y un rectangulo dejaria
pixeles dorados flotando en el aire. El penacho si pinta fuera, que para eso sobresale.

Y los sprites de mirar a la derecha se voltean, se les pinta la capa y se vuelven a voltear.
Sin eso la banda se salia del chaco por el lado equivocado (probado: quedaban dos pixeles
dorados en el borde en vez de una banda), porque el chaco crece hacia la nuca y la nuca esta
a un lado o a otro segun a donde mire.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), 'pruebas'))
import entorno
import pygame

CARPETA = 'sprites/franceses'
ORIGEN = 'soldado_fr_%s_cuerpoAcuerpo_%d.png'
DESTINO = 'oficial_fr_%s_cuerpoAcuerpo_%d.png'
LADOS = ('izq', 'dch')
FOTOGRAMAS = range(7)

ORO = (246, 185, 0)            # el dorado que ya usa el sprite
ORO_SOMBRA = (176, 132, 0)     # su sombra (nuevo)
BLANCO = (240, 240, 240)       # la punta del penacho
TOLERANCIA_DEL_ORO = 6         # los sprites de la derecha lo tienen un punto mas oscuro

# El penacho se pinta aunque caiga fuera de la silueta; la banda, solo sobre el cuerpo
PENACHO = {'B': BLANCO, 'D': ORO}
BANDA = {'G': ORO, 'g': ORO_SOMBRA}

# Fila y columna de la capa que caen sobre el pompon del chaco
FILA_DEL_POMPON = 4
COLUMNA_DEL_POMPON = 2

CAPA = [
    "..B........",
    "..B........",
    "..D........",
    "..D........",
    "...........",
    "...........",
    "...........",
    "...........",
    "...........",
    "....GGGGG..",
    "....ggggg..",
]

OPACO = 20


def esOro(color):
    rojo, verde, azul, alfa = color
    return (alfa > OPACO
            and abs(rojo - ORO[0]) <= TOLERANCIA_DEL_ORO
            and abs(verde - ORO[1]) <= TOLERANCIA_DEL_ORO
            and abs(azul - ORO[2]) <= TOLERANCIA_DEL_ORO)


def pomponDelChaco(imagen):
    """(columna, fila) del pixel dorado mas alto, que es el pompon de lo alto del chaco."""
    ancho, alto = imagen.get_size()
    for y in range(alto):
        for x in range(ancho):
            if esOro(imagen.get_at((x, y))):
                return x, y
    raise ValueError("no se encuentra el pompon del chaco")


def conMargenArriba(imagen, filas):
    """El mismo sprite con filas vacias por arriba, para que quepa el penacho.

    Crece por arriba y no por abajo a proposito: el juego ancla por los pies (ver
    render.desplazamiento), y el ancho no cambia, asi que no descoloca nada.
    """
    if filas <= 0:
        return imagen.copy()
    ancho, alto = imagen.get_size()
    crecido = pygame.Surface((ancho, alto + filas), pygame.SRCALPHA)
    crecido.blit(imagen, (0, filas))
    return crecido


def aplicar(imagen):
    """El sprite con la capa del oficial pintada. Devuelve (imagen, filas anadidas)."""
    columna, fila = pomponDelChaco(imagen)
    margen = max(0, FILA_DEL_POMPON - fila)
    copia = conMargenArriba(imagen, margen)
    ancho, alto = copia.get_size()
    dx = columna - COLUMNA_DEL_POMPON
    dy = fila + margen - FILA_DEL_POMPON
    for y, filaDeLaCapa in enumerate(CAPA):
        for x, letra in enumerate(filaDeLaCapa):
            if letra == '.':
                continue
            destinoX, destinoY = x + dx, y + dy
            if not (0 <= destinoX < ancho and 0 <= destinoY < alto):
                continue
            if letra in BANDA and copia.get_at((destinoX, destinoY))[3] <= OPACO:
                continue
            color = PENACHO[letra] if letra in PENACHO else BANDA[letra]
            copia.set_at((destinoX, destinoY), color + (255,))
    return copia, margen


def comprobarLaCapa():
    for numero, fila in enumerate(CAPA):
        if len(fila) != len(CAPA[0]):
            raise ValueError("la fila %d de la capa mide %d y no %d"
                             % (numero, len(fila), len(CAPA[0])))
        for letra in fila:
            if letra != '.' and letra not in PENACHO and letra not in BANDA:
                raise ValueError("la fila %d usa %r, fuera de la paleta" % (numero, letra))


def hojaDeContacto(sprites, porFila=7, escala=7, margen=12):
    filas = [sprites[i:i + porFila] for i in range(0, len(sprites), porFila)]
    anchoDeFila = [sum(s.get_width() for s in fila) * escala + margen * (len(fila) + 1)
                   for fila in filas]
    altoDeFila = [max(s.get_height() for s in fila) * escala + margen for fila in filas]
    hoja = pygame.Surface((max(anchoDeFila), sum(altoDeFila) + margen))
    hoja.fill((96, 150, 88))
    y = margen
    for fila, alto in zip(filas, altoDeFila):
        x = margen
        for sprite in fila:
            grande = pygame.transform.scale(sprite, (sprite.get_width() * escala,
                                                     sprite.get_height() * escala))
            hoja.blit(grande, (x, y + alto - margen - grande.get_height()))
            x += grande.get_width() + margen
        y += alto
    return hoja


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    comprobarLaCapa()

    oficiales = []
    for lado in LADOS:
        for numero in FOTOGRAMAS:
            base = pygame.image.load(os.path.join(CARPETA, ORIGEN % (lado, numero))).convert_alpha()
            #los de mirar a la derecha se voltean, se pintan y se devuelven: la banda del
            #chaco tiene que ir hacia la nuca, y el chaco crece al lado contrario en cada lado
            miraADerecha = lado == 'dch'
            if miraADerecha:
                base = pygame.transform.flip(base, True, False)
            oficial, margen = aplicar(base)
            if miraADerecha:
                oficial = pygame.transform.flip(oficial, True, False)
            destino = DESTINO % (lado, numero)
            pygame.image.save(oficial, os.path.join(CARPETA, destino))
            oficiales.append(oficial)
            print("%-40s %2dx%-2d -> %2dx%-2d  %s"
                  % (destino, base.get_width(), base.get_height(),
                     oficial.get_width(), oficial.get_height(),
                     '+%d filas arriba' % margen if margen else ''))

    pygame.image.save(hojaDeContacto(oficiales), os.path.join(entorno.CAPTURAS, 'oficial.png'))
    print("guardados %d sprites y la hoja oficial.png" % len(oficiales))


main()
