"""Pruebas de las oleadas cerradas: cupo, ritmo de entrada, limpiar para pasar y la calma."""
import sys

import entorno
from entorno import comprobar, resumen
import pygame

pygame.init()
pygame.display.set_mode((500, 500))

import enemigo as E
import objetos
import oleadas

# ---- 1. el cupo de cada oleada ----
primera = oleadas.composicion(1)
comprobar("la primera oleada no trae tiradores, para aprender a disparar antes de esquivar",
          primera[oleadas.TIRADOR] == 0, str(primera))
comprobar("ni granaderos", primera[oleadas.GRANADERO] == 0, str(primera))
comprobar("y trae unos pocos de bayoneta", 2 <= primera[oleadas.CUERPO_A_CUERPO] <= 5, str(primera))
comprobar("los tiradores aparecen en la segunda",
          oleadas.composicion(2)[oleadas.TIRADOR] >= 1, str(oleadas.composicion(2)))
comprobar("los granaderos no aparecen antes de su oleada",
          all(oleadas.composicion(numero)[oleadas.GRANADERO] == 0
              for numero in range(1, oleadas.PRIMERA_OLEADA_CON_GRANADEROS)))
comprobar("y aparecen en cuanto toca",
          oleadas.composicion(oleadas.PRIMERA_OLEADA_CON_GRANADEROS)[oleadas.GRANADERO] == 1,
          str(oleadas.composicion(oleadas.PRIMERA_OLEADA_CON_GRANADEROS)))

cupos = [sum(oleadas.composicion(numero).values()) for numero in range(1, 30)]
comprobar("el cupo nunca baja de una oleada a la siguiente",
          all(b >= a for a, b in zip(cupos, cupos[1:])), str(cupos[:12]))
comprobar("y crece de verdad al principio", cupos[5] > cupos[0], f"{cupos[0]} -> {cupos[5]}")
comprobar("pero tiene techo, para que no salgan rondas eternas",
          max(cupos) <= oleadas.TOPE_POR_OLEADA, f"maximo {max(cupos)}")

# con el cupo al tope, lo que se recorta es el relleno: las oleadas altas tienen que ser mas
# duras, no mas largas
altas = [oleadas.composicion(numero) for numero in (12, 20, 30, 40)]
comprobar("en las oleadas altas los granaderos no dejan de crecer",
          all(b[oleadas.GRANADERO] >= a[oleadas.GRANADERO] for a, b in zip(altas, altas[1:])),
          str([c[oleadas.GRANADERO] for c in altas]))
comprobar("y el relleno de bayonetas es el que se recorta",
          altas[-1][oleadas.CUERPO_A_CUERPO] < altas[0][oleadas.CUERPO_A_CUERPO],
          str([c[oleadas.CUERPO_A_CUERPO] for c in altas]))
comprobar("sin dejar nunca una oleada sin bayonetas",
          all(c[oleadas.CUERPO_A_CUERPO] >= oleadas.MINIMO_CUERPO_A_CUERPO for c in altas),
          str([c[oleadas.CUERPO_A_CUERPO] for c in altas]))

# ---- 2. el ritmo de entrada se acelera con la oleada, con suelo ----
intervalos = [oleadas.intervaloDeEntrada(numero) for numero in range(1, 40)]
comprobar("entran mas seguido conforme suben las oleadas", intervalos[0] > intervalos[10],
          f"{intervalos[0]} ms -> {intervalos[10]} ms")
comprobar("el intervalo nunca baja del suelo", min(intervalos) == oleadas.INTERVALO_MINIMO,
          f"minimo {min(intervalos)} ms")

# ---- 3. la oleada saca su cupo entero, y ni uno mas ----
reloj = {'ms': 10000}
oleada = oleadas.Oleada(6, reloj['ms'])
cupoEsperado = sum(oleadas.composicion(6).values())
sacados = []
for _ in range(cupoEsperado * 3):
    if oleada.tocaEntrar(reloj['ms']):
        sacados.append(oleada.sacarSiguiente(reloj['ms']))
    reloj['ms'] += oleada.intervalo
comprobar("saca exactamente su cupo", len(sacados) == cupoEsperado,
          f"{len(sacados)} de {cupoEsperado}")
comprobar("y despues ya no queda nadie por entrar", not oleada.quedanPorEntrar())
comprobar("saca los cinco tipos", set(sacados) == set(oleadas.TIPOS),
          str({tipo: sacados.count(tipo) for tipo in oleadas.TIPOS}))
comprobar("y de cada uno los que decia la composicion",
          all(sacados.count(tipo) == oleadas.composicion(6)[tipo] for tipo in oleadas.TIPOS),
          str({tipo: sacados.count(tipo) for tipo in oleadas.TIPOS}))
comprobar("los duros vienen repartidos, no todos al final",
          sacados.index(oleadas.GRANADERO) < len(sacados) - 3, str(sacados))

# ---- 4. respeta su ritmo: no los suelta todos de golpe ----
reloj['ms'] = 20000
oleada = oleadas.Oleada(3, reloj['ms'])
comprobar("el primero entra en cuanto se levanta la calma", oleada.tocaEntrar(reloj['ms']))
oleada.sacarSiguiente(reloj['ms'])
comprobar("pero el siguiente tiene que esperar su turno", not oleada.tocaEntrar(reloj['ms']))
comprobar("y a medio intervalo tampoco", not oleada.tocaEntrar(reloj['ms'] + oleada.intervalo // 2))
comprobar("cumplido el intervalo, entra", oleada.tocaEntrar(reloj['ms'] + oleada.intervalo))

# ---- 5. limpiar para pasar ----
oleada = oleadas.Oleada(1, reloj['ms'])
comprobar("con cupo pendiente la oleada no esta limpiada", not oleada.limpiada([]))
while oleada.quedanPorEntrar():
    oleada.sacarSiguiente(reloj['ms'])
unFrances = E.enemigo(100, 100, 0, 0)
comprobar("sin cupo pero con franceses vivos, tampoco", not oleada.limpiada([unFrances]))
comprobar("sin cupo y sin nadie vivo, limpiada", oleada.limpiada([]))

# ---- 6. en la partida: calma, entrada, limpieza y siguiente oleada ----
reloj['ms'] = 50000
pygame.time.get_ticks = lambda: reloj['ms']

juego = entorno.cargarJuego()


class RelojFalso(object):
    def tick(self, *args):
        reloj['ms'] += 33
        return 33


class TeclasFalsas(object):
    def __getitem__(self, codigo):
        return False


control = {'frames': 0, 'maxVivos': 0, 'oleadasVistas': set(), 'objetosVistos': 0}
juego['clock'] = RelojFalso()
pygame.event.get = lambda *a, **k: []
pygame.key.get_pressed = lambda: TeclasFalsas()


def display_update_falso(*args, **kwargs):
    control['frames'] += 1
    control['maxVivos'] = max(control['maxVivos'], len(juego['enemies']))
    control['oleadasVistas'].add(juego['oleada'].numero)
    control['objetosVistos'] = max(control['objetosVistos'], len(juego['objetosEnSuelo']))
    #se mata a todo lo que entra, para que las oleadas se sucedan
    for enemigo_vivo in juego['enemies']:
        enemigo_vivo.vida = 0
    #y se dejan las bajas Y LOS PUNTOS a cero, para que ningun ascenso interrumpa la
    #prueba: el rango va por puntos, no por bajas
    juego['progreso'].bajas = 0
    juego['progreso'].puntos = 0
    if control['frames'] >= 900:
        juego['player'].vida = 0


pygame.display.update = display_update_falso

juego['reiniciarPartida']()
comprobar("la partida arranca en calma, no en medio de la batalla", juego['enCalma'])
comprobar("y arranca por la primera oleada", juego['oleada'].numero == oleadas.PRIMERA_OLEADA)
comprobar("en la calma no hay nadie en el campo", juego['enemies'] == [])

juego['partida']()
comprobar("se han sucedido varias oleadas", len(control['oleadasVistas']) >= 3,
          f"vistas: {sorted(control['oleadasVistas'])}")
comprobar("las oleadas van en orden y sin saltos",
          sorted(control['oleadasVistas']) == list(range(1, max(control['oleadasVistas']) + 1)),
          str(sorted(control['oleadasVistas'])))
comprobar("al limpiar una oleada cae una caja en el campo", control['objetosVistos'] >= 1,
          f"{control['objetosVistos']} objetos vistos a la vez")
comprobar("nunca se pasa del techo de franceses vivos",
          control['maxVivos'] <= juego['MAX_ENEMIGOS'],
          f"{control['maxVivos']} como maximo, techo {juego['MAX_ENEMIGOS']}")

# ---- 7. la pausa no adelanta ni la calma ni la entrada de la oleada ----
juego['reiniciarPartida']()
finCalmaAntes = juego['instanteFinCalma']
entradaAntes = juego['oleada'].instanteUltimaEntrada
juego['compensarPausa'](5000)
comprobar("la pausa empuja el final de la calma",
          juego['instanteFinCalma'] == finCalmaAntes + 5000)
comprobar("y el reloj de entrada de la oleada",
          juego['oleada'].instanteUltimaEntrada == entradaAntes + 5000)

# ---- 8. el techo de franceses no rompe el cupo: los que faltan esperan ----
juego['reiniciarPartida']()
juego['enCalma'] = False
juego['oleada'] = oleadas.Oleada(20, reloj['ms'])
cupoGrande = juego['oleada'].cupo()
comprobar("una oleada alta trae mas franceses que el techo simultaneo",
          cupoGrande > juego['MAX_ENEMIGOS'], f"cupo {cupoGrande}, techo {juego['MAX_ENEMIGOS']}")
for _ in range(cupoGrande * 4):
    juego['llevarOleada'](reloj['ms'])
    reloj['ms'] += juego['oleada'].intervalo
comprobar("con el campo lleno se deja de sacar cupo",
          len(juego['enemies']) <= juego['MAX_ENEMIGOS'], f"{len(juego['enemies'])} vivos")
comprobar("y el cupo que falta sigue pendiente, no se pierde", juego['oleada'].quedanPorEntrar())

sys.exit(resumen())
