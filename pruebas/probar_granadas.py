"""Pruebas de las granadas: vuelo, marca del suelo, danio en area y el granadero que las lanza."""
import sys

import entorno
from entorno import comprobar, resumen
import pygame

pygame.init()
pygame.display.set_mode((500, 500))

import enemigo as E
import granadas
import jugador as J

reloj = {'ms': 40000}
pygame.time.get_ticks = lambda: reloj['ms']

# ---- 1. el vuelo: sale del granadero y cae donde dijo ----
granada = granadas.Granada(100, 200, 300, 260, reloj['ms'])
comprobar("recien lanzada no ha caido", not granada.haCaido(reloj['ms']))
comprobar("y su avance es 0", granada.avance(reloj['ms']) == 0.0)
comprobar("a mitad de vuelo el avance es 0.5",
          abs(granada.avance(reloj['ms'] + granadas.TIEMPO_DE_VUELO // 2) - 0.5) < 0.01)
comprobar("justo antes de tocar suelo aun no ha caido",
          not granada.haCaido(reloj['ms'] + granadas.TIEMPO_DE_VUELO - 1))
comprobar("y al cumplirse el vuelo cae", granada.haCaido(reloj['ms'] + granadas.TIEMPO_DE_VUELO))

alFinal = granada.posicion(reloj['ms'] + granadas.TIEMPO_DE_VUELO)
comprobar("cae exactamente en el punto marcado",
          (round(alFinal[0]), round(alFinal[1])) == (300, 260), str(alFinal))
alPrincipio = granada.posicion(reloj['ms'])
comprobar("y sale de la mano del granadero", (round(alPrincipio[0]), round(alPrincipio[1])) == (100, 200),
          str(alPrincipio))

# el arco: en el aire pasa por encima de la linea recta entre origen y destino
mitadRecta = (200 + 260) / 2.0
mitadReal = granada.posicion(reloj['ms'] + granadas.TIEMPO_DE_VUELO // 2)[1]
comprobar("describe un arco, no una linea recta", mitadReal < mitadRecta - 10,
          f"y={mitadReal:.0f} contra {mitadRecta:.0f} en linea recta")

# ---- 2. la marca del suelo parpadea, y cada vez mas rapido ----
def parpadeos(desde, hasta):
    estados = [granada.marcaVisible(reloj['ms'] + t) for t in range(desde, hasta, 10)]
    cambios = sum(1 for a, b in zip(estados, estados[1:]) if a != b)
    return cambios


comprobar("la marca parpadea al principio del vuelo", parpadeos(0, 500) >= 2,
          f"{parpadeos(0, 500)} cambios en el primer medio segundo")
comprobar("y parpadea mas rapido al final que al principio",
          parpadeos(granadas.TIEMPO_DE_VUELO - 500, granadas.TIEMPO_DE_VUELO) > parpadeos(0, 500),
          f"{parpadeos(0, 500)} -> {parpadeos(granadas.TIEMPO_DE_VUELO - 500, granadas.TIEMPO_DE_VUELO)}")

lienzo = pygame.Surface((500, 500))
lienzo.fill((90, 150, 80))
limpio = lienzo.copy()
granada.dibujarMarca(lienzo, reloj['ms'])
rojos = sum(1 for x in range(500) for y in range(500)
            if lienzo.get_at((x, y))[:3] == granadas.COLOR_MARCA)
comprobar("la marca se pinta en el suelo", rojos > 50, f"{rojos} pixeles rojos")
lienzo.fill((90, 150, 80))
granadaOculta = granadas.Granada(100, 200, 300, 260, reloj['ms'])
oculto = next(t for t in range(0, 400) if not granadaOculta.marcaVisible(reloj['ms'] + t))
granadaOculta.dibujarMarca(lienzo, reloj['ms'] + oculto)
comprobar("y en el parpadeo desaparece del todo", lienzo.get_at((300, 260))[:3] != granadas.COLOR_MARCA)

# ---- 3. danio en area: pilla a quien este dentro del circulo ----
dentro = J.jugador(300 - 10, 260 - 18)
fuera = J.jugador(300 + granadas.RADIO + 40, 260)
comprobar("alcanza a quien esta en el punto de caida", dentro in granada.alcanzados([dentro, fuera]))
comprobar("y no a quien esta lejos", fuera not in granada.alcanzados([dentro, fuera]))

justoEnElBorde = J.jugador(300 + granadas.RADIO - 12, 260 - 18)
comprobar("el borde del circulo cuenta como dentro",
          justoEnElBorde in granada.alcanzados([justoEnElBorde]),
          f"a {granadas.RADIO} px de radio")

soldado = J.jugador(300 - 10, 260 - 18)
vidaAntes = soldado.vida
enElAire, estallidos = granadas.resolver([granada], [soldado], reloj['ms'] + granadas.TIEMPO_DE_VUELO)
comprobar("al caer resta vida a quien pilla dentro", soldado.vida == vidaAntes - granadas.DANIO,
          f"{vidaAntes} -> {soldado.vida}")
comprobar("la granada desaparece del aire", enElAire == [])
comprobar("y deja un estallido", len(estallidos) == 1)

# quien se aparta no recibe nada: es lo que hace justa el arma
otra = granadas.Granada(100, 200, 300, 260, reloj['ms'])
esquivador = J.jugador(300 - 10, 260 - 18)
esquivador.x = 300 + granadas.RADIO + 30      # se ha ido antes de que cayera
esquivador.rect.topleft = (esquivador.x, esquivador.y)
vidaAntes = esquivador.vida
granadas.resolver([otra], [esquivador], reloj['ms'] + granadas.TIEMPO_DE_VUELO)
comprobar("y quien se aparta del circulo no recibe nada", esquivador.vida == vidaAntes,
          f"vida {esquivador.vida}")

# ---- 4. el estallido se apaga solo ----
estallido = granadas.Estallido(300, 260, reloj['ms'])
comprobar("el estallido dura un instante", not estallido.terminado(reloj['ms']))
comprobar("y se apaga", estallido.terminado(reloj['ms'] + granadas.DURACION_ESTALLIDO))
comprobar("limpiarEstallidos se lleva los apagados",
          granadas.limpiarEstallidos([estallido], reloj['ms'] + granadas.DURACION_ESTALLIDO) == [])

# ---- 5. el granadero: se planta en su anillo y lanza ----
frances = E.granadero(480, 250, 250, 250)
comprobar("aguanta mas que un soldado de linea",
          frances.vida > E.enemigo.VIDA_INICIAL, f"{frances.vida} contra {E.enemigo.VIDA_INICIAL}")
for _ in range(600):
    frances.pathFinding(250, 250)
distancia = frances.distanciaA((250, 250))
comprobar("se acerca hasta ponerse a tiro",
          distancia <= E.DISTANCIA_DE_LANZAMIENTO + 2, f"{distancia:.0f} px")
comprobar("pero no se pega al jugador: su propia granada le pillaria",
          distancia >= E.DISTANCIA_MINIMA_GRANADERO - 2, f"{distancia:.0f} px")

acorralado = E.granadero(250 + 40, 250, 250, 250)
antes = acorralado.distanciaA((250, 250))
for _ in range(30):
    acorralado.pathFinding(250, 250)
comprobar("si el jugador se le echa encima, retrocede",
          acorralado.distanciaA((250, 250)) > antes,
          f"{antes:.0f} -> {acorralado.distanciaA((250, 250)):.0f} px")

# ---- 6. el lanzamiento: primero arma, y la granada sale al acabar el armado ----
lanzador = E.granadero(250 + 150, 250, 250, 250)
lanzador.pathFinding(250, 250)
enElAire = []
lanzador.lanzar(enElAire, (250, 250))
comprobar("recien aparecido no lanza (esta recargando)", enElAire == [] and not lanzador.armando)

reloj['ms'] += E.RECARGA_GRANADA + E.DESFASE_MAXIMO_DESCARGA
lanzador.lanzar(enElAire, (250, 250))
comprobar("cuando le toca, empieza armando el brazo", lanzador.armando)
comprobar("y la granada todavia no ha salido", enElAire == [])
comprobar("mientras arma, se ve el sprite de armado",
          lanzador.sprite() in (E.Lanzar_izq_Gr[0], E.Lanzar_dch_Gr[0]))
lanzador.pathFinding(250, 250)
comprobar("y no se mueve mientras arma", lanzador.stop)

reloj['ms'] += E.DURACION_ARMADO
lanzador.lanzar(enElAire, (250, 250))
comprobar("al acabar el armado suelta la granada", len(enElAire) == 1)
comprobar("ya no esta armando", not lanzador.armando)
comprobar("la granada apunta a donde estaba el jugador",
          (round(enElAire[0].destino[0]), round(enElAire[0].destino[1])) == (250, 250),
          str(enElAire[0].destino))
comprobar("y ahora se ve el sprite de suelta",
          lanzador.sprite() in (E.Lanzar_izq_Gr[1], E.Lanzar_dch_Gr[1]))

reloj['ms'] += 1
lanzador.lanzar(enElAire, (250, 250))
comprobar("no lanza dos seguidas sin recargar", len(enElAire) == 1)
reloj['ms'] += E.RECARGA_GRANADA
lanzador.lanzar(enElAire, (250, 250))
reloj['ms'] += E.DURACION_ARMADO
lanzador.lanzar(enElAire, (250, 250))
comprobar("pasada la recarga vuelve a lanzar", len(enElAire) == 2)

# ---- 7. fuera de alcance no lanza ----
lejano = E.granadero(480, 250, 250, 250)
lejano.pathFinding(250, 250)
reloj['ms'] += E.RECARGA_GRANADA + E.DESFASE_MAXIMO_DESCARGA
municion = []
lejano.lanzar(municion, (250, 250))
comprobar("desde lejos no lanza, primero se acerca",
          municion == [] and not lejano.armando,
          f"a {lejano.distanciaA((250, 250)):.0f} px")

# ---- 8. la granada no distingue: tambien revienta a los franceses ----
victima = E.enemigo(300 - 10, 260 - 15, 0, 0)
victima.actualizarRect()
lejano = E.enemigo(300 + granadas.RADIO + 60, 260, 0, 0)
lejano.actualizarRect()
soldado = J.jugador(300 - 10, 260 - 18)
vidaFrances, vidaLejano, vidaJugador = victima.vida, lejano.vida, soldado.vida

reventon = granadas.Granada(100, 200, 300, 260, reloj['ms'])
#se avanza el reloj de verdad en vez de pasar un instante futuro: el destello se sella con
#pygame.time.get_ticks(), asi que en el juego los dos valores son el mismo
reloj['ms'] += granadas.TIEMPO_DE_VUELO
granadas.resolver([reventon], [soldado, victima, lejano], reloj['ms'])
comprobar("el frances que pilla dentro tambien lo paga",
          victima.vida == vidaFrances - granadas.DANIO, f"{vidaFrances} -> {victima.vida}")
comprobar("y el jugador igual, en el mismo estallido",
          soldado.vida == vidaJugador - granadas.DANIO, f"{vidaJugador} -> {soldado.vida}")
comprobar("el frances de fuera del circulo se salva", lejano.vida == vidaLejano)
comprobar("al frances alcanzado se le ve el destello", victima.mostrandoDestello(reloj['ms']))

# y si el frances estaba tocado, la granada de los suyos puede matarlo
moribundo = E.enemigo(300 - 10, 260 - 15, 0, 0)
moribundo.actualizarRect()
moribundo.vida = granadas.DANIO
otra = granadas.Granada(100, 200, 300, 260, reloj['ms'])
granadas.resolver([otra], [moribundo], reloj['ms'] + granadas.TIEMPO_DE_VUELO)
moribundo.checkEstadoVida()
comprobar("un frances tocado cae por la granada de los suyos", not moribundo.vivo,
          f"vida {moribundo.vida}")

# el granadero puede caer en su propio estallido si el jugador le obliga a lanzar de cerca
imprudente = E.granadero(300 - 10, 260 - 15, 0, 0)
imprudente.actualizarRect()
vidaAntes = imprudente.vida
suya = granadas.Granada(300, 260, 300, 260, reloj['ms'])
granadas.resolver([suya], [imprudente], reloj['ms'] + granadas.TIEMPO_DE_VUELO)
comprobar("y hasta el granadero se lleva lo suyo si la tira demasiado cerca",
          imprudente.vida == vidaAntes - granadas.DANIO, f"{vidaAntes} -> {imprudente.vida}")

# ---- 10. entre por donde entre, acaba lanzando: una sola vara de medir ----
# Esto se escapo hasta que se vio jugando: un granadero que llegaba por la izquierda o por
# arriba se plantaba y no tiraba nada. La causa era que main.py llama a pathFinding con la
# ESQUINA del cuerpo del jugador y a lanzar con su CENTRO, y se llevan 20 px. El granadero se
# paraba en cuanto la esquina entraba en el anillo, a 190, y desde ahi el centro le quedaba a
# 199: fuera de alcance, asi que no lanzaba nunca. Las pruebas de arriba no lo cogian porque le
# pasan el mismo punto a las dos cosas, que es justo lo que la partida no hace.
import jugador as J

JUGADOR_X, JUGADOR_Y = 250, 250
soldadoQuieto = J.jugador(JUGADOR_X, JUGADOR_Y)
ENTRADAS = (('izquierda', (-40, JUGADOR_Y)), ('derecha', (E.WINX + 40, JUGADOR_Y)),
            ('arriba', (JUGADOR_X, -40)), ('abajo', (JUGADOR_X, E.WINY + 40)))

plantados = []
incoherentes = []
for nombre, (entradaX, entradaY) in ENTRADAS:
    frances = E.granadero(entradaX, entradaY, JUGADOR_X, JUGADOR_Y)
    enElAire = []
    for _ in range(400):
        #el mismo orden y los mismos dos puntos que usa la partida de verdad
        frances.lanzar(enElAire, soldadoQuieto.rect.center)
        frances.pathFinding(JUGADOR_X, JUGADOR_Y)
        #parado y sin armar solo puede significar una cosa: que ya esta a tiro
        if (frances.stop and not frances.armando
                and not frances.aTiro((JUGADOR_X, JUGADOR_Y))):
            incoherentes.append((nombre, round(frances.x), round(frances.y)))
        reloj['ms'] += 33
    plantados.append((nombre, len(enElAire), round(frances.distanciaA((JUGADOR_X, JUGADOR_Y)))))

comprobar("entrando por los cuatro lados, los cuatro granaderos lanzan",
          all(cuantas > 0 for _, cuantas, _ in plantados), str(plantados))
comprobar("y ninguno se queda a medio camino, fuera de su anillo",
          all(distancia <= E.DISTANCIA_DE_LANZAMIENTO + 2 for _, _, distancia in plantados),
          str(plantados))
comprobar("y estando plantado, ninguno se queda fuera de su propio anillo",
          not incoherentes, "%d frames incoherentes, los primeros %s"
          % (len(incoherentes), incoherentes[:4]))

# el caso exacto que se veia en partida: plantado en el borde del anillo por la izquierda, con
# el centro del jugador (que es a donde apunta la granada) mas lejos que el propio anillo
plantado = E.granadero(-40, JUGADOR_Y, JUGADOR_X, JUGADOR_Y)
for _ in range(400):
    plantado.pathFinding(JUGADOR_X, JUGADOR_Y)
reloj['ms'] += E.RECARGA_GRANADA + E.DESFASE_MAXIMO_DESCARGA
plantado.lanzar([], soldadoQuieto.rect.center)
comprobar("plantado y con la recarga hecha, arma el brazo aunque el punto al que apunta le "
          "quede mas lejos que el anillo",
          plantado.armando,
          "a la esquina %.0f, al centro %.0f, anillo %d"
          % (plantado.distanciaA((JUGADOR_X, JUGADOR_Y)),
             plantado.distanciaA(soldadoQuieto.rect.center), E.DISTANCIA_DE_LANZAMIENTO))

# ---- 11. el cadaver del granadero es el suyo, con bonete ----
# moria con el cadaver del soldado de linea, con chaco, aunque en pie lleve piel de oso
comprobar("el granadero no muere con el cadaver del soldado de linea",
          E.cadaverGranaderoImg is not E.cadaverOficialImg
          and E.cadaverGranaderoImg is not E.cadaverImg)
comprobar("y su cadaver mide lo mismo que el de siempre, para que caiga en el mismo sitio",
          E.cadaverGranaderoImg.get_size() == E.cadaverOficialImg.get_size(),
          "%s contra %s" % (E.cadaverGranaderoImg.get_size(), E.cadaverOficialImg.get_size()))

ROJO_DEL_PENACHO = ((130, 0, 0), (176, 32, 34))


def cuentaDeColores(imagen, colores):
    ancho, alto = imagen.get_size()
    return sum(1 for y in range(alto) for x in range(ancho)
               if imagen.get_at((x, y))[:3] in colores and imagen.get_at((x, y))[3] > 20)


comprobar("lleva penacho rojo, que es lo que le distingue tirado en el suelo",
          cuentaDeColores(E.cadaverGranaderoImg, ROJO_DEL_PENACHO) >= 6,
          "%d pixeles de penacho" % cuentaDeColores(E.cadaverGranaderoImg, ROJO_DEL_PENACHO))
comprobar("y el cadaver del soldado de linea no lo lleva",
          cuentaDeColores(E.cadaverOficialImg, ROJO_DEL_PENACHO) == 0,
          "%d pixeles" % cuentaDeColores(E.cadaverOficialImg, ROJO_DEL_PENACHO))

caido = E.granadero(200, 200, 0, 0)
lienzo = pygame.Surface((500, 500), pygame.SRCALPHA)
caido.dibujarCadaver(lienzo)
comprobar("y es el que se dibuja al caer",
          cuentaDeColores(lienzo, ROJO_DEL_PENACHO) >= 6,
          "%d pixeles de penacho en el campo" % cuentaDeColores(lienzo, ROJO_DEL_PENACHO))

sys.exit(resumen())
