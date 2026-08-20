"""Prueba la escena de ascenso dentro del bucle: pausa, eleccion, relojes y continuidad."""
import os
import sys

import entorno
from entorno import comprobar, resumen
import pygame

pygame.init()

juego = entorno.cargarJuego()

import ascensos

FPS = 30
MS_POR_FRAME = 1000 // FPS
reloj = {'ms': 1000}
pygame.time.get_ticks = lambda: reloj['ms']


class TiempoFalso:
    def perf_counter(self):
        return reloj['ms'] / 1000.0


class RelojFalso:
    def tick(self, *args):
        reloj['ms'] += MS_POR_FRAME
        return MS_POR_FRAME


class TeclasFalsas:
    def __init__(self, pulsadas):
        self.pulsadas = pulsadas

    def __getitem__(self, codigo):
        return codigo in self.pulsadas


juego['time'] = TiempoFalso()
juego['clock'] = RelojFalso()

control = {'frames': 0, 'eventos': [], 'teclas': set(), 'por_frame': None, 'capturas': {}}
pygame.event.get = lambda *a, **k: [control['eventos'].pop(0)] if control['eventos'] else []
pygame.key.get_pressed = lambda: TeclasFalsas(control['teclas'])


def display_update_falso(*args, **kwargs):
    control['frames'] += 1
    if control['frames'] in control['capturas']:
        pygame.image.save(juego['win'], os.path.join(entorno.CAPTURAS, control['capturas'][control['frames']]))
    if control['por_frame']:
        control['por_frame'](control['frames'])


pygame.display.update = display_update_falso



def correr(escena, por_frame=None, capturas=None):
    control['frames'] = 0
    control['por_frame'] = por_frame
    control['capturas'] = capturas or {}
    return escena()


# ---- preparamos una partida con un enemigo y un cadaver en el campo ----
juego['reiniciarPartida']()
soldado = juego['player']
frances = juego['enemigoDistancia'](400, 250, 250, 250)
juego['enemies'].append(frances)
caido = juego['enemigo'](150, 150, 0, 0)
caido.vida = 0
caido.checkEstadoVida()
juego['cadaveres'].append(caido)

# ---- 1. al cruzar el umbral, la partida sale a la escena de ascenso ----
juego['progreso'].apuntarBajas(4)
resultado = correr(juego['partida'])
comprobar("al cruzar el umbral la partida sale al ascenso", resultado == juego['ESCENA_ASCENSO'],
          str(resultado))
comprobar("todavia no ha subido de rango (eso pasa en la escena)",
          juego['progreso'].nombreRango() == 'Soldado raso')

# ---- 2. la escena de ascenso: sube de rango, ofrece tres y aplica la elegida ----
antesFinCalma = juego['instanteFinCalma']
antesDisparoEnemigo = frances.instanteUltimoDisparo
antesMuerte = caido.instanteMuerte
msAntes = reloj['ms']

resultado = correr(juego['ascenso'],
                   lambda n: control['eventos'].append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1)) if n == 6 else None,
                   {3: 'escena_ascenso.png'})
pausaMs = reloj['ms'] - msAntes

comprobar("elegir con la tecla 1 devuelve a la partida", resultado == juego['ESCENA_PARTIDA'])
comprobar("ha ascendido a cabo", juego['progreso'].nombreRango() == 'Cabo')
comprobar("la mejora 1 es la recarga y se ha aplicado", soldado.recarga == 1250,
          f"recarga={soldado.recarga}")
comprobar("la pantalla de ascenso se pinta varios frames", control['frames'] >= 6,
          f"{control['frames']} frames")

# ---- 3. la pausa no regala apariciones ni disparos ni caduca cadaveres ----
comprobar("el reloj de la oleada se empuja lo que duro la pausa",
          juego['instanteFinCalma'] - antesFinCalma == pausaMs,
          f"pausa={pausaMs} ms, reloj +{juego['instanteFinCalma'] - antesFinCalma} ms")
comprobar("la recarga del enemigo se empuja igual",
          frances.instanteUltimoDisparo - antesDisparoEnemigo == pausaMs)
comprobar("el cadaver no envejece durante la pausa",
          caido.instanteMuerte - antesMuerte == pausaMs)

# ---- 4. se vuelve a la MISMA partida, sin reiniciar nada ----
comprobar("el jugador es el mismo objeto", juego['player'] is soldado)
comprobar("el enemigo sigue en el campo", frances in juego['enemies'])
comprobar("el cadaver sigue en el campo", caido in juego['cadaveres'])
comprobar("las bajas se conservan", juego['progreso'].bajas == 4)

# ---- 5. una opcion agotada no se puede elegir ----
juego['progreso'].apuntarBajas(6)          # 10 bajas: toca el segundo ascenso
for _ in range(2):
    ascensos.aplicar(soldado, ascensos.CLAVE_RECARGA)   # recarga ya en el suelo
comprobar("la recarga esta en el suelo", soldado.recarga == ascensos.SUELO_RECARGA)
vidaMaximaAntes = soldado.vidaMaxima


def insistirConLaUno(numero):
    #la 1 esta agotada: aunque se pulse, no debe pasar nada hasta pulsar la 2
    if numero <= 4:
        control['eventos'].append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1))
    elif numero == 6:
        control['eventos'].append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2))


resultado = correr(juego['ascenso'], insistirConLaUno)
comprobar("la tecla de una mejora agotada no cierra la pantalla", control['frames'] >= 6,
          f"{control['frames']} frames")
comprobar("la recarga sigue en el suelo, no ha bajado mas", soldado.recarga == ascensos.SUELO_RECARGA)
comprobar("al elegir la 2 sube la vida maxima", soldado.vidaMaxima == vidaMaximaAntes + ascensos.SUBIDA_VIDA,
          f"vida maxima={soldado.vidaMaxima}")
comprobar("y ha ascendido a sargento", juego['progreso'].nombreRango() == 'Sargento')

# ---- 6. empezar otra partida borra el progreso ----
juego['reiniciarPartida']()
comprobar("la nueva partida empieza de soldado raso con 0 bajas",
          juego['progreso'].nombreRango() == 'Soldado raso' and juego['progreso'].bajas == 0)
comprobar("y el soldado vuelve a sus numeros de salida",
          juego['player'].recarga == 1500 and juego['player'].vidaMaxima == 100
          and juego['player'].danioBala == 25,
          f"recarga={juego['player'].recarga} vida={juego['player'].vidaMaxima} dano={juego['player'].danioBala}")

sys.exit(resumen())
