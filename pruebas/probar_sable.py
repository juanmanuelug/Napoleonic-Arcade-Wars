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


# ---- 1. el contrato con el danio de contacto ----
comprobar("el sable va al ritmo de la gracia de contacto del jugador",
          E.RECARGA_SABLE == J.GRACIA_CONTACTO,
          "sable %d ms, contacto %d ms" % (E.RECARGA_SABLE, J.GRACIA_CONTACTO))
comprobar("el alzado y el tajo caben dentro de una recarga",
          E.DURACION_ALZADO + E.DURACION_TAJO <= E.RECARGA_SABLE,
          "%d + %d contra %d" % (E.DURACION_ALZADO, E.DURACION_TAJO, E.RECARGA_SABLE))

# ---- 2. lejos del jugador no saca el sable ----
frances = unFrances()
lejos = pygame.Rect(400, 400, 20, 36)
frances.atacar(lejos, rastros)
comprobar("sin nadie al alcance no alza el sable", not frances.alzandoSable)
frances.stop = False
comprobar("y ensenia el sprite de andar",
          frances.sprite() in E.Andar_izq_Fr_cuerpo,
          "sprite de andar: %s" % (frances.sprite() in E.Andar_izq_Fr_cuerpo))

# ---- 3. con el jugador encima: alza, no avanza, y taja ----
frances = unFrances()
encima = frances.rect.copy()
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
encima = frances.rect.copy()
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
frances.atacar(frances.rect.copy(), rastros)
frances.pathFinding(400, 200)
comprobar("con el jugador a su derecha, se gira aunque tenga el sable en alto",
          frances.dch and not frances.izq)
comprobar("y saca el sprite de alzar del lado bueno", frances.sprite() is E.Alzar_dch_Fr)

# ---- 6. los que van con mosquete no tienen sable ----
sinSable = []
for clase in (E.enemigoDistancia, E.voltigeur, E.granadero):
    frances = unFrances(clase=clase)
    frances.atacar(frances.rect.copy(), rastros)
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

# ---- 8. el danio sigue siendo el de contacto, ni mas ni menos ----
soldado = J.jugador(200, 200)
frances = unFrances(x=200, y=200)
vidaAntes = soldado.vida
soldado.instanteUltimoGolpe = reloj['ms'] - J.GRACIA_CONTACTO
#un segundo entero de sable encima, frame a frame
for _ in range(30):
    frances.atacar(soldado.rect, rastros)
    frances.pathFinding(soldado.x, soldado.y)
    soldado.sufrirContacto([frances])
    reloj['ms'] += 33
perdida = vidaAntes - soldado.vida
comprobar("un segundo de sable encima quita lo mismo que antes: dos golpes de contacto",
          perdida == 2 * J.DANIO_CONTACTO, "%d de vida en 990 ms" % perdida)

# ---- 9. la pausa no regala tajos ----
juego = entorno.cargarJuego()
juego['reiniciarPartida']()
victima = unFrances()
victima.atacar(victima.rect.copy(), rastros)
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
encima = frances.rect.copy()
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
frances.atacar(frances.rect.copy(), alOtroLado)
reloj['ms'] += E.DURACION_ALZADO
frances.atacar(frances.rect.copy(), alOtroLado)
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
        frances.atacar(frances.rect.copy(), suyos)
        reloj['ms'] += 33
    if suyos:
        sinRastro.append(clase.__name__)
comprobar("el tirador, el voltigeur y el granadero no dejan rastro de hoja",
          not sinRastro, "dejan rastro: %s" % sinRastro)

sys.exit(resumen())
