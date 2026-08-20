"""Granadero de la Vieille Garde, hecho operando sobre los sprites del soldado de linea.

    python herramientas/granadero.py

Dibujar un soldado de cero sale plano y rigido: la pose, el volumen y el sombreado son lo
dificil. Asi que en vez de eso se parte de los sprites buenos y se les hace cirugia:

  - el chaco crece hacia arriba hasta ser un bonete de piel de oso, aprovechando que las
    primeras filas del lienzo solo tienen el mosquete
  - se le anade el penacho rojo al frente y la placa de laton
  - los colores salen de la paleta del propio sprite, para que no cante

Asi hereda gratis la pose, el volumen y el sombreado del original, y el lienzo, los pies y la
caja de colision siguen siendo exactamente los mismos.

La capa esta dibujada contra soldado_fr_izq_0. En los demas fotogramas la cabeza esta en otro
sitio (al andar la figura se inclina: hasta 2 filas mas arriba y 3 columnas a un lado), asi que
para cada uno se calcula el desplazamiento por correlacion de la mancha oscura de la cabeza,
en vez de a ojo. Para los que miran a la derecha, la capa se refleja: el penacho va delante.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), 'pruebas'))
import entorno
import pygame

REFERENCIA = 'sprites/franceses/soldado_fr_izq_0.png'
ORIGEN = 'sprites/franceses/soldado_fr_%s_%d.png'
DESTINO = 'sprites/franceses/granadero_fr_%s_%d.png'
FOTOGRAMAS = range(7)
LADOS = ('izq', 'dch')

# Zona donde esta la cabeza en la referencia, y cuanto se busca el desplazamiento
FILAS_DE_LA_CABEZA = (6, 20)
BUSQUEDA = 5
# El bonete empieza en esta fila: por encima se repinta el original, para que el canion siga
# asomando sobre el gorro como en el sprite de linea. Pintarlo por delante quedaba peor:
# parecia clavado en el bonete.
PRIMERA_FILA_DEL_BONETE = 4

# Colores tomados del propio soldado de linea, menos dos: el brillo del penacho y el laton
PALETA = {
    '.': None,                  # no se toca el pixel del original
    'N': (4, 4, 4),             # negro dominante del sprite
    'F': (31, 31, 31),          # gris muy oscuro: piel de oso
    'f': (54, 54, 54),          # brillo de la piel de oso
    'R': (130, 0, 0),           # rojo del sprite
    'r': (176, 32, 34),         # brillo del penacho (nuevo)
    'O': (198, 156, 48),        # laton de la placa (nuevo: el dorado del sprite era casi
                                #   del color de la cara y se confundia con ella)
    'o': (140, 104, 28),        # sombra del laton
}

# El bonete va de ancho constante, como un cilindro: la primera version se estrechaba hacia
# arriba y parecia una capucha en punta. Los brillos van dispersos y no en columna, que
# alineados parecian botones.
CAPA = [
    "....................",
    "....................",
    "....r...............",
    "....r...............",
    "...rr.NNNN..........",
    "...rrNFFFFFN........",
    "...rrNFFFFFFN.......",
    "...rRNfFFFFFN.......",
    "...rRNFFFFFFN.......",
    "...RRNFFFFfFN.......",
    "...RRNFFFFFFN.......",
    "....RNFFFFFFN.......",
    ".....NFfFFFFN.......",
    ".....NFFFFFFN.......",
    ".....NFOOFFFN.......",
    ".....NFOoFFFN.......",
    ".....NFFFFFFN.......",
]


def validarCapa(capa, paleta, ancho):
    for numero, fila in enumerate(capa):
        if len(fila) != ancho:
            raise ValueError("la fila %d de la capa mide %d y no %d: %r"
                             % (numero, len(fila), ancho, fila))
        for letra in fila:
            if letra not in paleta:
                raise ValueError("la fila %d usa la letra %r, que no esta en la paleta"
                                 % (numero, letra))


def reflejar(capa):
    """La capa mirando al otro lado: el penacho tiene que ir siempre por delante."""
    return [fila[::-1] for fila in capa]


def mascaraDeLaCabeza(imagen, reflejada=False):
    """Los pixeles oscuros de la zona de la cabeza, que es la mancha por la que se alinea."""
    ancho, alto = imagen.get_size()
    desde, hasta = FILAS_DE_LA_CABEZA
    puntos = set()
    for y in range(desde, min(hasta, alto)):
        for x in range(ancho):
            color = imagen.get_at((x, y))
            if color[3] > 20 and color[0] + color[1] + color[2] < 140:
                puntos.add((ancho - 1 - x if reflejada else x, y))
    return puntos


def desplazamientoQueEncaja(referencia, mascara):
    """El (dx, dy) que hace coincidir mejor las dos manchas. Fuerza bruta, que es barato."""
    mejor, mejorPuntuacion = (0, 0), -1
    for dy in range(-BUSQUEDA, BUSQUEDA + 1):
        for dx in range(-BUSQUEDA, BUSQUEDA + 1):
            puntuacion = sum(1 for (x, y) in referencia if (x + dx, y + dy) in mascara)
            #a igualdad gana el desplazamiento mas pequenio
            if (puntuacion > mejorPuntuacion
                    or (puntuacion == mejorPuntuacion
                        and abs(dx) + abs(dy) < abs(mejor[0]) + abs(mejor[1]))):
                mejor, mejorPuntuacion = (dx, dy), puntuacion
    return mejor


def aplicarCapa(original, capa, paleta, dx, dy):
    """Pinta la capa desplazada encima del sprite y devuelve la copia."""
    ancho, alto = original.get_size()
    copia = original.copy()
    for y, fila in enumerate(capa):
        for x, letra in enumerate(fila):
            color = paleta[letra]
            if not color:
                continue
            destinoX, destinoY = x + dx, y + dy
            if 0 <= destinoX < ancho and 0 <= destinoY < alto:
                copia.set_at((destinoX, destinoY), color + (255,))
    for y in range(max(0, min(alto, PRIMERA_FILA_DEL_BONETE + dy))):
        for x in range(ancho):
            pixel = original.get_at((x, y))
            if pixel[3] > 20:
                copia.set_at((x, y), pixel)
    return copia


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    referencia = pygame.image.load(REFERENCIA).convert_alpha()
    validarCapa(CAPA, PALETA, referencia.get_width())
    capaPorLado = {'izq': CAPA, 'dch': reflejar(CAPA)}
    mascaraPorLado = {'izq': mascaraDeLaCabeza(referencia),
                      'dch': mascaraDeLaCabeza(referencia, reflejada=True)}

    hechos = []
    print("%-26s %-10s %s" % ("fotograma", "desplaza", "lienzo"))
    for lado in LADOS:
        for numero in FOTOGRAMAS:
            original = pygame.image.load(ORIGEN % (lado, numero)).convert_alpha()
            dx, dy = desplazamientoQueEncaja(mascaraPorLado[lado], mascaraDeLaCabeza(original))
            granadero = aplicarCapa(original, capaPorLado[lado], PALETA, dx, dy)
            destino = DESTINO % (lado, numero)
            pygame.image.save(granadero, destino)
            hechos.append(granadero)
            print("%-26s (%+d,%+d)%4s %dx%d" % (os.path.basename(destino), dx, dy, "",
                                                granadero.get_width(), granadero.get_height()))

    # hoja de contactos, para revisar los catorce de un vistazo
    ESCALA = 5
    porFila = 7
    celdaAncho, celdaAlto = 24 * ESCALA, 42 * ESCALA
    hoja = pygame.Surface((porFila * celdaAncho + 20, 2 * celdaAlto + 20))
    hoja.fill((96, 150, 88))
    for indice, pieza in enumerate(hechos):
        columna, fila = indice % porFila, indice // porFila
        grande = pygame.transform.scale(pieza, (pieza.get_width() * ESCALA,
                                                pieza.get_height() * ESCALA))
        hoja.blit(grande, (10 + columna * celdaAncho,
                           10 + fila * celdaAlto + (celdaAlto - grande.get_height())))
    pygame.image.save(hoja, os.path.join(entorno.CAPTURAS, 'granadero_hoja.png'))
    print("guardada granadero_hoja.png con los 14 fotogramas")


main()
