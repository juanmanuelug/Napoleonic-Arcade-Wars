"""Arnes de prueba: recorre menu -> partida -> game over -> menu -> salir sin teclado real."""
import os
import sys

import entorno
from entorno import comprobar, resumen
import pygame

# ---- carga main.py sin ejecutar su main() ni el sys.exit() final ----
juego = entorno.cargarJuego()

# ---- control de frames, eventos y teclas ----
control = {'frames': 0, 'eventos': [], 'teclas': set(), 'por_frame': None, 'capturas': {}}


def event_get_falso(*args, **kwargs):
    pendientes, control['eventos'] = control['eventos'], []
    return pendientes


class TeclasFalsas:
    # los codigos de tecla de SDL2 son numeros enormes, asi que no vale una lista
    def __init__(self, pulsadas):
        self.pulsadas = pulsadas

    def __getitem__(self, codigo):
        return codigo in self.pulsadas


def key_get_pressed_falso():
    return TeclasFalsas(control['teclas'])


update_real = pygame.display.update


def display_update_falso(*args, **kwargs):
    control['frames'] += 1
    numero = control['frames']
    if numero in control['capturas']:
        pygame.image.save(juego['win'], os.path.join(entorno.CAPTURAS, control['capturas'][numero]))
    if control['por_frame']:
        control['por_frame'](numero)


pygame.event.get = event_get_falso
pygame.key.get_pressed = key_get_pressed_falso
pygame.display.update = display_update_falso
class RelojFalso:
    def tick(self, *args):
        return 0


juego['clock'] = RelojFalso()   # sin esperas, la prueba va a tope


def pulsar(tecla):
    control['eventos'].append(pygame.event.Event(pygame.KEYDOWN, key=tecla))


def correr(escena, por_frame, capturas=None):
    control['frames'] = 0
    control['por_frame'] = por_frame
    control['capturas'] = capturas or {}
    return escena()




# ---- 1. Menu: no debe bloquearse y ENTER arranca partida ----
resultado = correr(juego['menu'], lambda n: pulsar(pygame.K_RETURN) if n == 4 else None,
                   {2: 'escena_menu.png'})
comprobar("el menu responde a ENTER y pasa a la partida", resultado == juego['ESCENA_PARTIDA'])
comprobar("el menu pinta varios frames (no se queda congelado)", control['frames'] >= 4)
comprobar("ENTER prepara una partida nueva", juego['player'] is not None and juego['player'].vida == 100)

# ---- 2. Partida: mover, disparar y morir ----
juego['enemies'].append(juego['enemigo'](300, 250, 250, 250))
juego['enemies'].append(juego['enemigoDistancia'](80, 250, 250, 250))
control['teclas'] = {pygame.K_RIGHT, pygame.K_SPACE}
seguimiento = {'balas_maximas': 0, 'cadaveres': 0, 'vida_enemigo': None}


def durante_partida(numero):
    seguimiento['balas_maximas'] = max(seguimiento['balas_maximas'], len(juego['balas']))
    seguimiento['cadaveres'] = max(seguimiento['cadaveres'], len(juego['cadaveres']))
    if juego['enemies']:
        seguimiento['vida_enemigo'] = juego['enemies'][0].vida
    if numero == 40:
        control['teclas'] = set()
    if numero == 60:
        juego['player'].vida = 0   # forzamos la muerte para probar el game over


resultado = correr(juego['partida'], durante_partida,
                   {6: 'escena_partida_1.png', 25: 'escena_partida_2.png'})
comprobar("al morir se pasa a la escena de game over", resultado == juego['ESCENA_GAME_OVER'])
comprobar("el jugador dispara y la bala existe", seguimiento['balas_maximas'] >= 1)
comprobar("el jugador se mueve a la derecha", juego['player'].x > 250)
comprobar("las balas hacen danio al enemigo",
          seguimiento['vida_enemigo'] is None or seguimiento['cadaveres'] >= 1 or seguimiento['vida_enemigo'] < 75)

# ---- 3. Game over: ENTER vuelve al menu ----
resultado = correr(juego['gameOver'], lambda n: pulsar(pygame.K_RETURN) if n == 3 else None,
                   {2: 'escena_game_over.png'})
comprobar("game over vuelve al menu con ENTER", resultado == juego['ESCENA_MENU'])

# ---- 4. Segunda partida desde el menu: el estado se reinicia ----
resultado = correr(juego['menu'], lambda n: pulsar(pygame.K_RETURN) if n == 2 else None)
comprobar("se puede volver a jugar", resultado == juego['ESCENA_PARTIDA'])
comprobar("la vida se reinicia", juego['player'].vida == 100)
comprobar("se limpian enemigos, balas y cadaveres",
          juego['enemies'] == [] and juego['balas'] == [] and juego['cadaveres'] == [])

# ---- 5. ESC en la partida pausa, y la pausa no deja abandonar sin confirmar ----
control['teclas'] = set()
resultado = correr(juego['partida'], lambda n: pulsar(pygame.K_ESCAPE) if n == 3 else None)
comprobar("ESC en la partida abre la pausa", resultado == juego['ESCENA_PAUSA'])

soldado_antes = juego['player']
resultado = correr(juego['pausa'], lambda n: pulsar(pygame.K_RETURN) if n == 3 else None,
                   {2: 'escena_pausa.png'})
comprobar("ENTER en la pausa devuelve a la partida", resultado == juego['ESCENA_PARTIDA'])
comprobar("y se vuelve a la misma partida", juego['player'] is soldado_antes)

def unEscYLuegoSeguir(numero):
    #un solo ESC solo pide confirmacion: si despues pulsas ENTER, sigues jugando
    if numero == 3:
        pulsar(pygame.K_ESCAPE)
    elif numero == 6:
        pulsar(pygame.K_RETURN)


resultado = correr(juego['pausa'], unEscYLuegoSeguir)
comprobar("un solo ESC no abandona: con ENTER se sigue jugando",
          resultado == juego['ESCENA_PARTIDA'], str(resultado))

resultado = correr(juego['pausa'],
                   lambda n: pulsar(pygame.K_ESCAPE) if n in (3, 6) else None,
                   {5: 'escena_pausa_confirmando.png'})
comprobar("dos ESC seguidos si abandonan, y vuelven al menu", resultado == juego['ESCENA_MENU'])

resultado = correr(juego['menu'], lambda n: pulsar(pygame.K_ESCAPE) if n == 2 else None)
comprobar("ESC en el menu sale del juego", resultado == juego['ESCENA_SALIR'])

# ---- 6. Cerrar la ventana en cualquier escena ----
for nombre in ('menu', 'partida', 'pausa', 'gameOver'):
    resultado = correr(juego[nombre],
                       lambda n: control['eventos'].append(pygame.event.Event(pygame.QUIT)) if n == 2 else None)
    comprobar(f"la X de la ventana cierra desde {nombre}", resultado == juego['ESCENA_SALIR'])

# El techo de franceses simultaneos y todo lo que tiene que ver con las apariciones se prueba
# ahora en probar_oleadas.py: quien decide quien entra y cuando es la oleada, no esta escena.

sys.exit(resumen())
