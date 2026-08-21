"""Pruebas del sable de la tropa de cuerpo a cuerpo: alza, taja, y no cambia el danio.

La animacion son dos fotogramas que ya estaban dibujados y no se usaban (el 0 y el 1 de
cuerpoAcuerpo; la animacion de andar solo gasta del 2 al 6). El danio lo sigue haciendo el
contacto, no el sable: aqui se comprueba tanto que el sable se mueve como que no ha tocado el
equilibrio del juego.
"""
import sys

import entorno
from entorno import comprobar, resumen
import pygame

pygame.init()
pygame.display.set_mode((500, 500))

import enemigo as E
import jugador as J
import sablazos

#donde van cayendo los rastros de hoja que sueltan los tajos
rastros = []

reloj = {'ms': 80000}
pygame.time.get_ticks = lambda: reloj['ms']


def unFrances(x=200, y=200, clase=E.enemigo):
    frances = clase(x, y, 0, 0)
    frances.actualizarRect()
    return frances


def unJugador(x=200, y=200):
    #el objetivo del sable es el jugador entero y no su caja: el tajo tiene que poder herirlo
    return J.jugador(x, y)


# ---- 1. el contrato del cuerpo a cuerpo: el tajo hace el danio, y avisa antes ----
#el aviso se mide en FRAMES, que es lo que de verdad tiene el jugador para reaccionar
FRAMES_MINIMOS_DE_AVISO = 15
comprobar("el sable avisa lo bastante para verlo venir y apartarse",
          E.DURACION_ALZADO >= FRAMES_MINIMOS_DE_AVISO * 1000 // 30,
          "%d ms de aviso, o sea %d frames a 30 fps"
          % (E.DURACION_ALZADO, E.DURACION_ALZADO * 30 // 1000))
comprobar("y el tajo duele mas del doble que lo que costaba el contacto, porque se esquiva",
          E.DANIO_SABLE > 2 * J.DANIO_CONTACTO,
          "tajo %d, contacto %d" % (E.DANIO_SABLE, J.DANIO_CONTACTO))
comprobar("entre dos tajos pasa mas de un segundo y medio: hay hueco para pegar y salir",
          E.DURACION_ALZADO + E.RECARGA_SABLE >= 1500,
          "%d de alzado + %d de recarga" % (E.DURACION_ALZADO, E.RECARGA_SABLE))

primerSoldado = unJugador()
primerFrances = unFrances()
vidaDePartida = primerSoldado.vida
for _ in range(60):
    primerSoldado.sufrirContacto([primerFrances])
comprobar("tocar a un sable no cuesta vida: lo que cuesta es quedarse cuando cae",
          primerSoldado.vida == vidaDePartida,
          "vida %d de %d" % (primerSoldado.vida, vidaDePartida))

# ---- 2. lejos del jugador no saca el sable ----
frances = unFrances()
lejos = unJugador(400, 400)
frances.atacar(lejos, rastros)
comprobar("sin nadie al alcance no alza el sable", not frances.alzandoSable)
frances.stop = False
comprobar("y ensenia el sprite de andar",
          frances.sprite() in E.Andar_izq_Fr_cuerpo,
          "sprite de andar: %s" % (frances.sprite() in E.Andar_izq_Fr_cuerpo))

# ---- 3. con el jugador encima: alza, no avanza, y taja ----
frances = unFrances()
encima = unJugador(frances.x, frances.y)
frances.atacar(encima, rastros)
comprobar("con el jugador encima alza el sable", frances.alzandoSable)
comprobar("y ensenia el sprite de alzar", frances.sprite() is E.Alzar_izq_Fr)

xAntes, yAntes = frances.x, frances.y
for _ in range(5):
    frances.pathFinding(0, 0)
comprobar("con el sable en alto no avanza",
          (frances.x, frances.y) == (xAntes, yAntes),
          "de (%s, %s) a (%s, %s)" % (xAntes, yAntes, frances.x, frances.y))
comprobar("pero se da por plantado, no por andando", frances.stop)

reloj['ms'] += E.DURACION_ALZADO
frances.atacar(encima, rastros)
comprobar("cumplido el alzado, cae el tajo", not frances.alzandoSable)
comprobar("y ensenia el sprite de tajar", frances.sprite() is E.Tajar_izq_Fr)
comprobar("el tajo se ve un rato", frances.mostrandoTajo(reloj['ms']))

reloj['ms'] += E.DURACION_TAJO
comprobar("y despues ya no", not frances.mostrandoTajo(reloj['ms']))
frances.stop = False
comprobar("vuelve al sprite de andar", frances.sprite() in E.Andar_izq_Fr_cuerpo)

# ---- 4. no taja dos veces sin recargar ----
frances = unFrances()
encima = unJugador(frances.x, frances.y)
frances.atacar(encima, rastros)
reloj['ms'] += E.DURACION_ALZADO
frances.atacar(encima, rastros)
tajos = 1
for _ in range(int(E.RECARGA_SABLE // 10) - 1):
    reloj['ms'] += 10
    frances.atacar(encima, rastros)
    if frances.alzandoSable:
        tajos += 1
        break
comprobar("no vuelve a alzar antes de recargar", tajos == 1, "%d alzados" % tajos)
reloj['ms'] += E.RECARGA_SABLE
frances.atacar(encima, rastros)
comprobar("y cumplida la recarga, vuelve a alzar", frances.alzandoSable)

# ---- 5. mira al jugador aunque este alzando el sable ----
frances = unFrances(x=200)
frances.atacar(unJugador(frances.x, frances.y), rastros)
frances.pathFinding(400, 200)
comprobar("con el jugador a su derecha, se gira aunque tenga el sable en alto",
          frances.dch and not frances.izq)
comprobar("y saca el sprite de alzar del lado bueno", frances.sprite() is E.Alzar_dch_Fr)

# ---- 6. los que van con mosquete no tienen sable ----
sinSable = []
for clase in (E.enemigoDistancia, E.voltigeur, E.granadero):
    frances = unFrances(clase=clase)
    frances.atacar(unJugador(frances.x, frances.y), rastros)
    if frances.alzandoSable or frances.PELEA_CON_SABLE:
        sinSable.append(clase.__name__)
comprobar("el tirador, el voltigeur y el granadero no sacan sable",
          not sinSable, "sacan sable: %s" % sinSable)

# ---- 7. el sable no descoloca el cuerpo ----
lienzos = set(imagen.get_size() for imagen in
              list(E.Andar_izq_Fr_cuerpo) + list(E.Andar_dch_Fr_cuerpo)
              + [E.Alzar_izq_Fr, E.Tajar_izq_Fr, E.Alzar_dch_Fr, E.Tajar_dch_Fr])
comprobar("los fotogramas de sable miden lo mismo que los de andar, asi que el cuerpo no salta",
          len(lienzos) == 1, str(sorted(lienzos)))

# ---- 8. el tajo hace el danio, y solo si el jugador sigue ahi cuando cae ----
soldado = unJugador(200, 200)
frances = unFrances(x=200, y=200)
vidaAntes = soldado.vida
frances.atacar(soldado, rastros)
comprobar("mientras alza el sable todavia no ha quitado nada", soldado.vida == vidaAntes,
          "vida %d" % soldado.vida)
reloj['ms'] += E.DURACION_ALZADO
frances.atacar(soldado, rastros)
comprobar("al caer el tajo, quita DANIO_SABLE de una vez",
          vidaAntes - soldado.vida == E.DANIO_SABLE, "%d de vida" % (vidaAntes - soldado.vida))

#el caso que da sentido al aviso: apartarse durante el alzado sale gratis
esquivador = unJugador(200, 200)
otro = unFrances(x=200, y=200)
reloj['ms'] += E.RECARGA_SABLE
otro.atacar(esquivador, rastros)
comprobar("el frances empieza a alzar con el jugador encima", otro.alzandoSable)
esquivador.x += E.ALCANCE_SABLE + J.ANCHO_CUERPO + 20
esquivador.rect.topleft = (esquivador.x, esquivador.y)
reloj['ms'] += E.DURACION_ALZADO
otro.atacar(esquivador, rastros)
comprobar("pero si se aparta durante el aviso, el tajo cae al aire y no le cuesta nada",
          esquivador.vida == esquivador.vidaMaxima, "vida %d" % esquivador.vida)
comprobar("y el frances gasta el golpe igual: el sable se suelta",
          not otro.alzandoSable and otro.mostrandoTajo(reloj['ms']))

# ---- 9. la pausa no regala tajos ----
juego = entorno.cargarJuego()
juego['reiniciarPartida']()
victima = unFrances()
victima.atacar(unJugador(victima.x, victima.y), rastros)
juego['enemies'].append(victima)
inicioAntes = victima.instanteInicioAlzado
tajoAntes = victima.instanteUltimoTajo
juego['compensarPausa'](5000)
comprobar("la pausa empuja el reloj del alzado",
          victima.instanteInicioAlzado == inicioAntes + 5000,
          "%d -> %d" % (inicioAntes, victima.instanteInicioAlzado))
comprobar("y el del ultimo tajo",
          victima.instanteUltimoTajo == tajoAntes + 5000,
          "%d -> %d" % (tajoAntes, victima.instanteUltimoTajo))

# ---- 10. el rastro de la hoja ----
frances = unFrances(x=200, y=200)
encima = unJugador(frances.x, frances.y)
recien = []
frances.atacar(encima, recien)
comprobar("mientras alza el sable no hay rastro todavia", recien == [], "%d rastros" % len(recien))
reloj['ms'] += E.DURACION_ALZADO
frances.atacar(encima, recien)
comprobar("al caer el tajo sale un rastro, y solo uno", len(recien) == 1, "%d rastros" % len(recien))

rastro = recien[0]
comprobar("el rastro sale de la mano que lleva el sable, no del centro del cuerpo",
          (rastro.x, rastro.y) == (frances.rect.left + E.DESPLAZAMIENTO_DE_LA_MANO,
                                   frances.rect.top + E.ALTURA_DE_LA_MANO),
          "rastro en (%.0f, %.0f), cuerpo en %s" % (rastro.x, rastro.y, frances.rect))
comprobar("y sale por delante del cuerpo, del lado al que mira",
          rastro.x < frances.rect.centerx and rastro.mirandoIzq,
          "x del rastro %.0f, centro del cuerpo %d" % (rastro.x, frances.rect.centerx))

frances = unFrances(x=200, y=200)
frances.izq, frances.dch = False, True
frances.actualizarRect()
alOtroLado = []
frances.atacar(unJugador(frances.x, frances.y), alOtroLado)
reloj['ms'] += E.DURACION_ALZADO
frances.atacar(unJugador(frances.x, frances.y), alOtroLado)
comprobar("mirando a la derecha, el rastro sale por el otro lado",
          alOtroLado[0].x > frances.rect.centerx and not alOtroLado[0].mirandoIzq,
          "x del rastro %.0f, centro del cuerpo %d" % (alOtroLado[0].x, frances.rect.centerx))

# el arco barre: primero se abre y despues se le deshace la cola
import sablazos

barrido = sablazos.Sablazo(250, 250, True, 0)
tramos = [barrido.tramoVisible(ms) for ms in (0, 30, 60, 90, 120, 150)]
comprobar("el arco empieza siendo un trozo y se abre",
          tramos[0][1] < tramos[2][1], "%s" % [t for t in tramos])
comprobar("y despues se le deshace la cola, en vez de quedarse quieto apagandose",
          tramos[-1][0] > tramos[0][0], "%s" % [t for t in tramos])
comprobar("nunca se sale del arco", all(0 <= a <= b <= sablazos.BLOQUES - 1 for a, b in tramos),
          "%s" % [t for t in tramos])

comprobar("el rastro dura menos que el fotograma del tajo, para que el brazo se quede estirado",
          sablazos.DURACION_SABLAZO < E.DURACION_TAJO,
          "%d ms contra %d ms" % (sablazos.DURACION_SABLAZO, E.DURACION_TAJO))
comprobar("y se acaba", barrido.terminado(sablazos.DURACION_SABLAZO))
comprobar("limpiar se lleva los acabados y deja los vivos",
          sablazos.limpiar([barrido], sablazos.DURACION_SABLAZO) == []
          and sablazos.limpiar([barrido], 10) == [barrido])


def pixelesPintados(sablazo, ms):
    lienzo = pygame.Surface((500, 500))
    lienzo.fill((0, 0, 0))
    sablazo.dibujar(lienzo, ms)
    return sum(1 for y in range(230, 275) for x in range(230, 275)
               if lienzo.get_at((x, y))[:3] != (0, 0, 0))


comprobar("el rastro se ve de verdad en la pantalla", pixelesPintados(barrido, 60) > 0,
          "%d pixeles" % pixelesPintados(barrido, 60))
comprobar("y el filo, que va delante, es mas claro que la cola",
          sablazos.COLOR_FILO > sablazos.COLOR_RASTRO,
          "%s contra %s" % (str(sablazos.COLOR_FILO), str(sablazos.COLOR_RASTRO)))

# ---- 11. los del mosquete tampoco dejan rastro ----
sinRastro = []
for clase in (E.enemigoDistancia, E.voltigeur, E.granadero):
    frances = unFrances(clase=clase)
    suyos = []
    for _ in range(30):
        frances.atacar(unJugador(frances.x, frances.y), suyos)
        reloj['ms'] += 33
    if suyos:
        sinRastro.append(clase.__name__)
comprobar("el tirador, el voltigeur y el granadero no dejan rastro de hoja",
          not sinRastro, "dejan rastro: %s" % sinRastro)

# ---- 12. el tajo tambien suena ----
import sonidos


class SonidoContado(object):
    def __init__(self):
        self.veces = 0

    def play(self):
        self.veces += 1


comprobar("el silbido del sable se ha podido sintetizar",
          not isinstance(sonidos.sonido_sable, sonidos.SonidoNulo),
          type(sonidos.sonido_sable).__name__)
comprobar("es corto y bajo, porque con cuatro franceses encima suena ocho veces por segundo",
          sonidos.DURACION_SABLE <= 0.15 and sonidos.VOLUMEN_SABLE < sonidos.VOLUMEN_IMPACTO,
          "%.3f s a volumen %.2f, contra el impacto a %.2f"
          % (sonidos.DURACION_SABLE, sonidos.VOLUMEN_SABLE, sonidos.VOLUMEN_IMPACTO))

#la campana es lo que lo hace un silbido y no un siseo: sin ella no se lee como algo que pasa
def fuerzaMedia(avance):
    return sum(abs(sonidos._sable(avance * sonidos.DURACION_SABLE, avance))
               for _ in range(300)) / 300.0


comprobar("suena en campana: nada, todo, nada",
          fuerzaMedia(0.5) > 3 * fuerzaMedia(0.1) and fuerzaMedia(0.5) > 3 * fuerzaMedia(0.9),
          "principio %.3f, medio %.3f, final %.3f"
          % (fuerzaMedia(0.1), fuerzaMedia(0.5), fuerzaMedia(0.9)))

contado = SonidoContado()
verdadero = sonidos.sonido_sable
E.sonidos.sonido_sable = contado
try:
    frances = unFrances()
    encima = unJugador(frances.x, frances.y)
    frances.atacar(encima, rastros)
    comprobar("alzando el sable todavia no suena", contado.veces == 0, "%d veces" % contado.veces)
    reloj['ms'] += E.DURACION_ALZADO
    frances.atacar(encima, rastros)
    comprobar("suena al caer el tajo, una sola vez", contado.veces == 1, "%d veces" % contado.veces)
    for _ in range(20):
        reloj['ms'] += 10
        frances.atacar(encima, rastros)
    comprobar("y no vuelve a sonar hasta el siguiente tajo", contado.veces == 1,
              "%d veces" % contado.veces)
    #los del mosquete no tienen sable, asi que no pueden sonar a sable
    for clase in (E.enemigoDistancia, E.voltigeur, E.granadero):
        otro = unFrances(clase=clase)
        for _ in range(40):
            otro.atacar(unJugador(otro.x, otro.y), rastros)
            reloj['ms'] += 33
    comprobar("y el tirador, el voltigeur y el granadero no suenan a sable",
              contado.veces == 1, "%d veces" % contado.veces)
finally:
    E.sonidos.sonido_sable = verdadero

sys.exit(resumen())
