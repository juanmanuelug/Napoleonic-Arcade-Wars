"""Los dos fotogramas de lanzar granada del granadero.

    python herramientas/granadero_lanzar.py

Se parte del granadero de pie y se le levanta el brazo TRASERO. El delantero no se puede tocar:
esta entrelazado con la madera del mosquete y borrarlo dejaria el arma flotando. El trasero, en
cambio, se puede pintar por encima de la casaca sin romper la silueta.

  fotograma 0 (armado): brazo arriba con la granada en la mano
  fotograma 1 (suelta): el brazo pasa por encima de la cabeza y la granada ya no esta
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), 'pruebas'))
import entorno
import pygame

ORIGEN = 'sprites/franceses/granadero_fr_%s_0.png'
DESTINO = 'sprites/franceses/granadero_fr_%s_lanzar_%d.png'
LADOS = ('izq', 'dch')

PALETA = {
    '.': None,
    'A': (0, 0, 145),           # azul de la casaca, el del propio sprite
    'a': (0, 0, 95),            # sombra de la casaca
    'S': (247, 142, 84),        # piel, la del propio sprite
    'K': (10, 10, 12),          # contorno de la granada
    'H': (48, 48, 54),          # hierro de la granada
    'C': (247, 214, 150),       # chispa de la mecha
}

# Brazo levantado con la granada en la mano
ARMADO = [
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "..................C.",
    ".................KHK",
    ".................HHH",
    ".................KHK",
    "................SS..",
    "...............SS...",
    "..............aS....",
    ".............aS.....",
    ".............aA.....",
    "............aA......",
    "............aA......",
    "............aA......",
    "............aA......",
    "............aA......",
]

# El brazo cruza por delante de la cabeza y la granada ya va por el aire
SUELTA = [
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    ".......SS...........",
    ".......SSS..........",
    "........aSS.........",
    ".........aSS........",
    "..........aSS.......",
    "...........aS.......",
    "............a.......",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
]


def reflejar(capa):
    return [fila[::-1] for fila in capa]


def aplicar(original, capa, paleta):
    ancho, alto = original.get_size()
    for numero, fila in enumerate(capa):
        if len(fila) != ancho:
            raise ValueError("la fila %d de la capa mide %d y no %d" % (numero, len(fila), ancho))
        for letra in fila:
            if letra not in paleta:
                raise ValueError("la fila %d usa %r, fuera de la paleta" % (numero, letra))
    copia = original.copy()
    for y, fila in enumerate(capa):
        if y >= alto:
            break
        for x, letra in enumerate(fila):
            color = paleta[letra]
            if color:
                copia.set_at((x, y), color + (255,))
    return copia


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    hechos = []
    for lado in LADOS:
        original = pygame.image.load(ORIGEN % lado).convert_alpha()
        capas = (ARMADO, SUELTA) if lado == 'izq' else (reflejar(ARMADO), reflejar(SUELTA))
        for numero, capa in enumerate(capas):
            pieza = aplicar(original, capa, PALETA)
            destino = DESTINO % (lado, numero)
            pygame.image.save(pieza, destino)
            hechos.append((os.path.basename(destino), pieza))
            print("%-34s %dx%d" % (os.path.basename(destino), pieza.get_width(), pieza.get_height()))
        hechos.append(('de pie (' + lado + ')', original))

    ESCALA = 8
    ancho = sum(pieza.get_width() for _, pieza in hechos) * ESCALA + 30 * (len(hechos) + 1)
    alto = max(pieza.get_height() for _, pieza in hechos) * ESCALA + 20
    hoja = pygame.Surface((ancho, alto))
    hoja.fill((96, 150, 88))
    x = 20
    for _, pieza in hechos:
        grande = pygame.transform.scale(pieza, (pieza.get_width() * ESCALA,
                                                pieza.get_height() * ESCALA))
        hoja.blit(grande, (x, alto - 10 - grande.get_height()))
        x += grande.get_width() + 30
    pygame.image.save(hoja, os.path.join(entorno.CAPTURAS, 'granadero_lanzar.png'))
    print("guardada granadero_lanzar.png")


main()
