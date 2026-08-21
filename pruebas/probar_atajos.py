"""Pruebas del modo de pruebas: los atajos para probar a mano sin jugarse la partida entera.

El modo viene ENCENDIDO. Lo que mas importa aqui es la primera mitad: que con PRUEBAS=0 no haya
forma de que una tecla haga nada raro, porque estos atajos meten jefes y hacen inmune al jugador
y hay que poder apagarlos de verdad.
"""
import os
import sys

import entorno
from entorno import comprobar, resumen
import pygame

pygame.init()
pygame.display.set_mode((500, 500))

import enemigo as E
import oleadas

reloj = {'ms': 300000}
pygame.time.get_ticks = lambda: reloj['ms']

# ---- 1. con PRUEBAS=0, apagado y sin hacer nada ----
os.environ['PRUEBAS'] = '0'
os.environ.pop('OLEADA', None)
apagado = entorno.cargarJuego()
comprobar("con PRUEBAS=0 el modo se apaga", not apagado['MODO_PRUEBAS'])
apagado['reiniciarPartida']()
comprobar("y la partida empieza en la primera oleada",
          apagado['oleada'].numero == oleadas.PRIMERA_OLEADA,
          "oleada %d" % apagado['oleada'].numero)
comprobar("con el soldado de recluta, sin mejoras regaladas",
          apagado['progreso'].rango == 0
          and apagado['player'].danioBala == E.proyectil(0, 0, 1).danio,
          "rango %d, dano %d" % (apagado['progreso'].rango, apagado['player'].danioBala))

TECLAS = ('TECLA_PRUEBAS_JEFE', 'TECLA_PRUEBAS_SIGUIENTE_OLEADA', 'TECLA_PRUEBAS_INMUNE',
          'TECLA_PRUEBAS_FASE')
hicieronAlgo = []
for nombre in TECLAS:
    enemigosAntes = len(apagado['enemies'])
    cupoAntes = apagado['oleada'].cupo()
    if apagado['atajoDePruebas'](apagado[nombre]):
        hicieronAlgo.append(nombre)
    if len(apagado['enemies']) != enemigosAntes or apagado['oleada'].cupo() != cupoAntes:
        hicieronAlgo.append(nombre + ' (toco el campo)')
comprobar("con el modo apagado, ninguna de las cuatro teclas hace nada",
          not hicieronAlgo, "hicieron algo: %s" % hicieronAlgo)
comprobar("y el jugador no es inmune", not apagado['inmuneDePruebas'])

# ---- 2. encendido por defecto, y sin tocar la partida normal ----
os.environ.pop('PRUEBAS', None)
os.environ.pop('OLEADA', None)
porDefecto = entorno.cargarJuego()
comprobar("sin tocar nada, el modo viene encendido", porDefecto['MODO_PRUEBAS'])
comprobar("pero la partida normal sigue empezando en la primera oleada",
          porDefecto['OLEADA_DE_PRUEBAS'] == oleadas.PRIMERA_OLEADA,
          "empieza en la %d" % porDefecto['OLEADA_DE_PRUEBAS'])
porDefecto['reiniciarPartida']()
comprobar("y con el soldado de recluta, sin mejoras regaladas",
          porDefecto['progreso'].rango == 0
          and porDefecto['player'].vidaMaxima < 150,
          "rango %d, vida %d" % (porDefecto['progreso'].rango,
                                 porDefecto['player'].vidaMaxima))

os.environ['OLEADA'] = '8'
juego = entorno.cargarJuego()
comprobar("y con OLEADA se elige donde empezar", juego['MODO_PRUEBAS'])
comprobar("y se puede elegir en que oleada empezar",
          juego['OLEADA_DE_PRUEBAS'] == 8, "oleada %d" % juego['OLEADA_DE_PRUEBAS'])

juego['reiniciarPartida']()
comprobar("la partida arranca en esa oleada", juego['oleada'].numero == 8,
          "oleada %d" % juego['oleada'].numero)

import ascensos

soldado = juego['player']
comprobar("y el soldado arranca con todas las mejoras, que es lo que tendria al llegar ahi",
          soldado.recarga == ascensos.SUELO_RECARGA
          and soldado.vidaMaxima == ascensos.TECHO_VIDA
          and soldado.danioBala == ascensos.ESCALONES_DANIO[-1],
          "recarga %d, vida %d, dano %d" % (soldado.recarga, soldado.vidaMaxima,
                                            soldado.danioBala))
comprobar("con el rango que le corresponde",
          juego['progreso'].nombreRango() == ascensos.RANGOS[-1],
          juego['progreso'].nombreRango())
comprobar("y a vida llena", soldado.vida == soldado.vidaMaxima,
          "%d de %d" % (soldado.vida, soldado.vidaMaxima))

# ---- 3. la tecla del jefe ----
juego['reiniciarPartida']()
juego['enCalma'] = False
comprobar("el campo empieza vacio", juego['enemies'] == [])
juego['atajoDePruebas'](juego['TECLA_PRUEBAS_JEFE'])
jefes = [uno for uno in juego['enemies'] if getattr(uno, 'ES_JEFE', False)]
comprobar("la tecla del jefe mete un jefe en el campo, sin esperar su oleada",
          len(jefes) == 1, str([type(uno).__name__ for uno in juego['enemies']]))
comprobar("y entra solo, porque su escolta va por fases",
          len(juego['enemies']) == 1, "%d en el campo" % len(juego['enemies']))

#JEFE_DE_PRUEBAS manda: se pone el jefe que se este trabajando y la tecla saca siempre ese
def jefesQueSacaLaTecla(cuantasPulsaciones):
    juego['reiniciarPartida']()
    juego['enCalma'] = False
    juego['oleada'] = oleadas.Oleada(3, reloj['ms'])       # una oleada SIN jefe
    sacados = []
    for _ in range(cuantasPulsaciones):
        antes = len(juego['enemies'])
        juego['atajoDePruebas'](juego['TECLA_PRUEBAS_JEFE'])
        sacados += [type(uno).__name__ for uno in juego['enemies'][antes:]
                    if getattr(uno, 'ES_JEFE', False)]
    return sacados


comprobar("con JEFE_DE_PRUEBAS puesto, la tecla saca siempre ese jefe",
          set(jefesQueSacaLaTecla(3)) == set([juego['JEFE_DE_PRUEBAS']]),
          "pedido %s, salieron %s" % (juego['JEFE_DE_PRUEBAS'], jefesQueSacaLaTecla(3)))

#y sin ponerlo, rota por la rueda: con cuatro jefes, sin rotar habria que llegar a la oleada 23
#para poder mirar el ultimo
juego['JEFE_DE_PRUEBAS'] = None
sacados = jefesQueSacaLaTecla(len(oleadas.RUEDA_DE_JEFES) + 1)
comprobar("y sin ponerlo, la tecla rota y saca todos los de la rueda",
          len(set(sacados)) == len(oleadas.RUEDA_DE_JEFES), "%s" % sacados)
comprobar("dando la vuelta al acabar", sacados[0] == sacados[len(oleadas.RUEDA_DE_JEFES)],
          "%s" % sacados)

#y en una oleada que NO es de jefe tambien: es justo para lo que sirve el atajo. Antes esto
#reventaba, porque la rueda no tiene turno para una oleada sin jefe
juego['reiniciarPartida']()
juego['enCalma'] = False
juego['oleada'] = oleadas.Oleada(3, reloj['ms'])
comprobar("la oleada 3 no es de jefe", not oleadas.tocaJefe(3))
juego['atajoDePruebas'](juego['TECLA_PRUEBAS_JEFE'])
comprobar("y el atajo mete jefe igual, sin romperse",
          sum(1 for uno in juego['enemies'] if getattr(uno, 'ES_JEFE', False)) == 1,
          str([type(uno).__name__ for uno in juego['enemies']]))

# ---- 4. la tecla de fase ----
#se pide expresamente el jefe CON fases: la tecla J saca el que diga JEFE_DE_PRUEBAS, que puede
#ser cualquiera, y esta seccion va de las fases
juego['reiniciarPartida']()
juego['enCalma'] = False
juego['entrarEnBatalla'](oleadas.JEFE, oleadas.JEFE_GRANADERO)
elJefe = [uno for uno in juego['enemies'] if getattr(uno, 'ES_JEFE', False)][0]
fases = [elJefe.faseDelAtaque()]
for _ in range(3):
    juego['atajoDePruebas'](juego['TECLA_PRUEBAS_FASE'])
    fases.append(elJefe.faseDelAtaque())
comprobar("la tecla de fase lo lleva por sus tres ataques sin pelear la pelea entera",
          fases[:3] == [E.ATAQUE_LLUVIA, E.ATAQUE_ANILLOS, E.ATAQUE_COLUMNAS],
          "fases %s" % fases)
comprobar("y en el ultimo tramo le deja un golpe de vida, no lo mata",
          elJefe.vida >= 1 and elJefe.vivo, "vida %d" % elJefe.vida)

#y a un jefe SIN fases la tecla no le toca: dejarlo a un golpe de morir no ensenia nada
juego['reiniciarPartida']()
juego['enCalma'] = False
juego['entrarEnBatalla'](oleadas.JEFE, oleadas.JEFE_SABLE)
sinFases = [uno for uno in juego['enemies'] if getattr(uno, 'ES_JEFE', False)][0]
vidaAntes = sinFases.vida
juego['atajoDePruebas'](juego['TECLA_PRUEBAS_FASE'])
comprobar("a un jefe sin fases la tecla de fase no le hace nada",
          sinFases.vida == vidaAntes and not sinFases.UMBRALES_DE_FASE,
          "vida %d de %d" % (sinFases.vida, vidaAntes))

# ---- 5. la tecla de oleada ----
juego['reiniciarPartida']()
juego['enCalma'] = False
juego['oleada'] = oleadas.Oleada(3, reloj['ms'])
for _ in range(3):
    juego['entrarEnBatalla'](oleadas.CUERPO_A_CUERPO)
comprobar("hay franceses y cupo por entrar",
          juego['enemies'] and juego['oleada'].quedanPorEntrar())
juego['atajoDePruebas'](juego['TECLA_PRUEBAS_SIGUIENTE_OLEADA'])
comprobar("la tecla de oleada deja el cupo a cero", not juego['oleada'].quedanPorEntrar(),
          "quedan %d" % juego['oleada'].cupo())
comprobar("y manda al suelo a los que estaban en el campo",
          all(uno.vida <= 0 for uno in juego['enemies']),
          str([uno.vida for uno in juego['enemies']]))

# ---- 6. la tecla de inmunidad ----
juego['reiniciarPartida']()
comprobar("empieza sin inmunidad", not juego['inmuneDePruebas'])
juego['atajoDePruebas'](juego['TECLA_PRUEBAS_INMUNE'])
comprobar("la tecla la enciende", juego['inmuneDePruebas'])
juego['atajoDePruebas'](juego['TECLA_PRUEBAS_INMUNE'])
comprobar("y la vuelve a apagar", not juego['inmuneDePruebas'])

# ---- 7. y se ve en pantalla que el modo esta encendido ----
import hud

lienzo = pygame.Surface((500, 500))
lienzo.fill((0, 0, 0))
hud.dibujarAvisoDePruebas(lienzo, 500, 500)
pintados = sum(1 for y in range(440, 500) for x in range(500)
               if lienzo.get_at((x, y))[:3] != (0, 0, 0))
comprobar("el modo encendido se anuncia en pantalla", pintados > 100,
          "%d pixeles de aviso" % pintados)

raise SystemExit(resumen())
