"""Voltigeur de infanteria ligera, hecho operando sobre el soldado de linea.

    python herramientas/voltigeur.py

Mismo metodo que con el granadero: se parte de los sprites buenos y se les pintan encima las
senias del uniforme, en vez de dibujar un soldado de cero. Salen los 18 sprites del voltigeur
(7 de andar por lado y 2 de disparar por lado) a partir de los 18 del soldado de linea.

Del cuadro de referencia (HaT 28003, French Light Infantry Voltigeurs) se sacan las senias que
caben en 20 pixeles de ancho:

  - penacho alto, ROJO abajo y AMARILLO arriba, al frente del chaco
  - banda amarilla en la parte alta del chaco

El cuerno de caza, el cuello y la franja del pantalon se quedan fuera. El cuerno serian tres
pixeles marrones y no se leeria a este tamanio. El cuello y la franja caen por debajo de la
cabeza, que es donde las poses dejan de coincidir (apuntar, disparar y andar llevan el mosquete
en tres sitios distintos), asi que una sola capa no puede acertar en todas: probado, el amarillo
del cuello acaba en la barriga.

Dos cosas hacen que la misma capa sirva para los 18 sprites:

  - Se ancla por la ESQUINA DEL CHACO, no por el borde del lienzo. Cada sprite tiene la cabeza
    en un sitio (el de apuntar en la fila 0, el del fogonazo en la 8, los de andar entre la 9 y
    la 11 segun el balanceo, y encima el de andar lleva el mosquete en vertical POR ENCIMA del
    chaco). Se busca la cabeza en cada uno y se pinta relativo a ella.
  - La banda solo pinta donde ya hay cuerpo, para no dejar pixeles sueltos en el aire donde el
    chaco se estrecha. El penacho si pinta fuera de la silueta, que para eso sobresale.

Los sprites de mirar a la derecha se voltean, se les pinta la capa y se vuelven a voltear, y asi
el penacho sale al frente en los dos lados sin escribir la capa dos veces.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), 'pruebas'))
import entorno
import pygame

CARPETA = 'sprites/franceses'


def _piezas():
    """Los 18 pares (origen, destino), en el orden en que se ensenian en la hoja."""
    pares = []
    for lado in ('izq', 'dch'):
        for numero in range(7):
            pares.append(('soldado_fr_%s_%d.png' % (lado, numero),
                          'voltigeur_fr_%s_%d.png' % (lado, numero)))
    for lado in ('izq', 'dch'):
        for cola in ('disparar_1', 'disparar'):
            pares.append(('soldado_fr_%s_%s.png' % (lado, cola),
                          'voltigeur_fr_%s_%s.png' % (lado, cola)))
    return tuple(pares)


PIEZAS = _piezas()

AMARILLO = (234, 198, 62)           # amarillo del uniforme (nuevo en la paleta)
AMARILLO_SOMBRA = (176, 142, 30)    # su sombra (nuevo)
ROJO = (130, 0, 0)                  # rojo que ya usa el sprite
ROJO_BRILLO = (176, 32, 34)

# El penacho se pinta aunque caiga fuera de la silueta; la banda, solo sobre el cuerpo
PENACHO = {'P': AMARILLO, 'p': AMARILLO_SOMBRA, 'R': ROJO, 'r': ROJO_BRILLO}
BANDA = {'B': AMARILLO, 'b': AMARILLO_SOMBRA}

# Fila y columna de la capa que caen sobre la esquina alta izquierda del chaco
FILA_DEL_CHACO = 8
COLUMNA_DEL_CHACO = 2

CAPA = [
    "..PP............",
    "..PP............",
    "..PP............",
    "..Pp............",
    "..RR............",
    "..RR............",
    "..rR............",
    "...R............",
    "................",
    "................",
    "..BBBBBBBB......",
    "..bbbbbbbb......",
]

# Filas con al menos esto de cuerpo: menos que eso es el mosquete en vertical, que en los
# sprites de andar asoma por encima de la cabeza y mide tres pixeles de ancho
CUERPO_MINIMO_DEL_CHACO = 5
OPACO = 20


def esquinaDelChaco(imagen):
    """(columna, fila) de la esquina alta izquierda del chaco."""
    ancho, alto = imagen.get_size()
    for y in range(alto):
        opacos = [x for x in range(ancho) if imagen.get_at((x, y))[3] > OPACO]
        if len(opacos) >= CUERPO_MINIMO_DEL_CHACO:
            return min(opacos), y
    raise ValueError("no se encuentra el chaco")


def conMargenArriba(imagen, filas):
    """El mismo sprite con filas vacias por arriba, para que quepa el penacho.

    Crece por arriba y no por abajo a proposito: el juego ancla los sprites por los pies
    (ver render.desplazamiento), asi que las filas de arriba no descolocan nada.
    """
    if filas <= 0:
        return imagen.copy()
    ancho, alto = imagen.get_size()
    crecido = pygame.Surface((ancho, alto + filas), pygame.SRCALPHA)
    crecido.blit(imagen, (0, filas))
    return crecido


def aplicar(imagen):
    """El sprite con la capa del voltigeur pintada. Devuelve (imagen, filas anadidas)."""
    columna, fila = esquinaDelChaco(imagen)
    margen = max(0, FILA_DEL_CHACO - fila)
    copia = conMargenArriba(imagen, margen)
    ancho, alto = copia.get_size()
    dx = columna - COLUMNA_DEL_CHACO
    dy = fila + margen - FILA_DEL_CHACO
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


def hojaDeContacto(sprites, porFila=7, escala=6, margen=12):
    """Todos los sprites en una rejilla, para poder mirarlos de un tiron."""
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

    voltigeurs = []
    for origen, destino in PIEZAS:
        base = pygame.image.load(os.path.join(CARPETA, origen)).convert_alpha()
        miraADerecha = '_dch' in origen
        if miraADerecha:
            base = pygame.transform.flip(base, True, False)
        voltigeur, margen = aplicar(base)
        if miraADerecha:
            voltigeur = pygame.transform.flip(voltigeur, True, False)
        pygame.image.save(voltigeur, os.path.join(CARPETA, destino))
        voltigeurs.append(voltigeur)
        print("%-32s %2dx%-2d -> %2dx%-2d  %s"
              % (destino, base.get_width(), base.get_height(),
                 voltigeur.get_width(), voltigeur.get_height(),
                 '+%d filas arriba' % margen if margen else ''))

    pygame.image.save(hojaDeContacto(voltigeurs), os.path.join(entorno.CAPTURAS, 'voltigeur.png'))
    print("guardados %d sprites y la hoja voltigeur.png" % len(voltigeurs))


main()
