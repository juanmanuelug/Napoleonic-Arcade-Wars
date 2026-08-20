"""Simula un minuto de partida con reloj falso: spawns, muertes, vida del jugador."""
import os
import sys

import entorno
from entorno import comprobar, resumen
import pygame

juego = entorno.cargarJuego()

FPS = 30
MS_POR_FRAME = 1000 // FPS
reloj = {'ms': 0}
pygame.time.get_ticks = lambda: reloj['ms']


class TiempoFalso:
    def perf_counter(self):
        return reloj['ms'] / 1000.0


juego['time'] = TiempoFalso()


class RelojFalso:
    def tick(self, *args):
        reloj['ms'] += MS_POR_FRAME
        return MS_POR_FRAME


juego['clock'] = RelojFalso()


class TeclasFalsas:
    def __init__(self, pulsadas):
        self.pulsadas = pulsadas

    def __getitem__(self, codigo):
        return codigo in self.pulsadas


control = {'teclas': set(), 'frames': 0}
pygame.event.get = lambda *a, **k: []
pygame.key.get_pressed = lambda: TeclasFalsas(control['teclas'])

registro = []


def display_update_falso(*args, **kwargs):
    control['frames'] += 1
    numero = control['frames']
    # el jugador se pasea a izquierda y derecha disparando sin parar
    if (numero // 45) % 2 == 0:
        control['teclas'] = {pygame.K_RIGHT, pygame.K_SPACE}
    else:
        control['teclas'] = {pygame.K_LEFT, pygame.K_SPACE}
    if os.environ.get('INMORTAL'):
        juego['player'].vida = 100
    if numero % (int(os.environ.get('SEGUNDOS', '60')) * FPS // 8) == 0:
        registro.append((numero / FPS, juego['player'].vida, len(juego['enemies']),
                         len(juego['cadaveres']), len(juego['balas']), len(juego['balasEnemigas'])))
    if numero >= int(os.environ.get('SEGUNDOS', '60')) * FPS:
        raise KeyboardInterrupt


pygame.display.update = display_update_falso

juego['reiniciarPartida']()
try:
    resultado = juego['partida']()
except KeyboardInterrupt:
    resultado = 'sobrevivio al minuto'

print(f"{'seg':>5} {'vida':>5} {'enem':>5} {'cadav':>6} {'balas':>6} {'balasE':>7}")
for segundos, vida, enemigos, cadaveres, balas, balas_enemigas in registro:
    print(f"{segundos:5.0f} {vida:5.0f} {enemigos:5d} {cadaveres:6d} {balas:6d} {balas_enemigas:7d}")
print()
print("frames simulados:", control['frames'], "| resultado:", resultado)
print("posicion final del jugador:", juego['player'].x, juego['player'].y)
