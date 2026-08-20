"""La granada y su mecha, dibujadas pixel a pixel.

    python herramientas/granada.py

Cosas pequenias y geometricas como esta salen bien dibujadas a mano; un soldado no. Se hace
mas grande que la bala (que son 4x4 pixeles visibles) porque tiene que verse venir.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), 'pruebas'))
import entorno
import pygame

DESTINO = 'sprites/granada.png'

PALETA = {
    '.': None,
    'K': (10, 10, 12),          # contorno
    'H': (48, 48, 54),          # hierro
    'h': (86, 86, 94),          # brillo del hierro
    'M': (96, 74, 46),          # mecha
    'C': (247, 142, 84),        # chispa (el naranja del propio juego)
    'c': (247, 214, 150),       # nucleo de la chispa
}

# 10x10: la esfera, la anilla y la mecha encendida
GRANADA = [
    "......c...",
    ".....cC...",
    "....CM....",
    "...KHK....",
    "..KHhHK...",
    ".KHhHHHK..",
    ".KHHHHHK..",
    ".KHHHHHK..",
    "..KHHHK...",
    "...KKK....",
]


def dibujar(mapa, paleta):
    ancho = len(mapa[0])
    for numero, fila in enumerate(mapa):
        if len(fila) != ancho:
            raise ValueError("la fila %d mide %d y no %d: %r" % (numero, len(fila), ancho, fila))
        for letra in fila:
            if letra not in paleta:
                raise ValueError("la fila %d usa %r, que no esta en la paleta" % (numero, letra))
    lienzo = pygame.Surface((ancho, len(mapa)), pygame.SRCALPHA)
    for y, fila in enumerate(mapa):
        for x, letra in enumerate(fila):
            color = paleta[letra]
            if color:
                lienzo.set_at((x, y), color + (255,))
    return lienzo


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    granada = dibujar(GRANADA, PALETA)
    pygame.image.save(granada, DESTINO)

    bala = pygame.image.load('sprites/bala.png').convert_alpha()
    ESCALA = 16
    piezas = (("granada", granada), ("bala", bala))
    hoja = pygame.Surface((sum(p.get_width() for _, p in piezas) * ESCALA + 60,
                           max(p.get_height() for _, p in piezas) * ESCALA + 20))
    hoja.fill((96, 150, 88))
    x = 20
    for nombre, pieza in piezas:
        grande = pygame.transform.scale(pieza, (pieza.get_width() * ESCALA,
                                                pieza.get_height() * ESCALA))
        hoja.blit(grande, (x, 10))
        x += grande.get_width() + 20
        print("%-10s %dx%d" % (nombre, pieza.get_width(), pieza.get_height()))
    pygame.image.save(hoja, os.path.join(entorno.CAPTURAS, 'granada.png'))
    print("escrito", DESTINO)


main()
