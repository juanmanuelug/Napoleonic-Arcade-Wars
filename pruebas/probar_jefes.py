"""Pruebas del primer jefe: el granadero al doble, su lluvia de granadas y la rueda de jefes.

El jefe no es un enemigo mas: es el motivo de su oleada. Asi que aqui se comprueban tres cosas
distintas — que el sprite doblado no descoloca nada, que la lluvia se puede esquivar, y que la
rueda lo saca cuando toca sin romper el cupo de la oleada.
"""
import os
import sys

import entorno
from entorno import comprobar, resumen
import pygame

pygame.init()
pygame.display.set_mode((500, 500))

import enemigo as E
import math
import proyectile
import granadas
import hud
import jugador as J
import oleadas
import render

CARPETA = os.path.join(os.path.dirname(entorno.AQUI), 'sprites', 'franceses')
LATON = (198, 156, 48)
OPACO = 20

reloj = {'ms': 200000}
pygame.time.get_ticks = lambda: reloj['ms']

# ---- 1. el sprite: el doble, y nada mas que el doble ----
faltan = [nombre for lado in ('izq', 'dch') for numero in range(7)
          for nombre in ['jefegranadero_fr_%s_%d.png' % (lado, numero)]
          if not os.path.exists(os.path.join(CARPETA, nombre))]
comprobar("estan los 14 sprites del jefe", not faltan, "faltan %s" % faltan)
if faltan:
    raise SystemExit(resumen())


def cargar(nombre):
    return pygame.image.load(os.path.join(CARPETA, nombre)).convert_alpha()


malMedidos, sinGalon = [], []
for lado in ('izq', 'dch'):
    for numero in range(7):
        tropa = cargar('granadero_fr_%s_%d.png' % (lado, numero))
        jefe = cargar('jefegranadero_fr_%s_%d.png' % (lado, numero))
        if jefe.get_size() != (tropa.get_width() * 2, tropa.get_height() * 2):
            malMedidos.append((lado, numero, jefe.get_size(), tropa.get_size()))
        #el galon: pixeles de oro que la tropa no tiene
        oros = sum(1 for y in range(jefe.get_height()) for x in range(jefe.get_width())
                   if jefe.get_at((x, y))[3] > OPACO
                   and jefe.get_at((x, y))[0] > 190 and 150 < jefe.get_at((x, y))[1] < 215
                   and jefe.get_at((x, y))[2] < 130)
        orosDeLaTropa = sum(1 for y in range(tropa.get_height()) for x in range(tropa.get_width())
                            if tropa.get_at((x, y))[:3] == LATON)
        if oros <= orosDeLaTropa * 4:
            sinGalon.append(('%s_%d' % (lado, numero), oros, orosDeLaTropa * 4))

comprobar("el jefe mide exactamente el doble, en los 14", not malMedidos, "%s" % malMedidos)
comprobar("y lleva mas oro del que sale de escalar el de la tropa: tiene galon propio",
          not sinGalon, "%s" % sinGalon)

#A x2, cada pixel del original tiene que ser un cuadrado limpio de 2x2: eso es lo que se pierde
#escalando por un numero no entero. Se comprueba en el CUERPO y no en el galon, que lleva detalle
#de un pixel justamente para que se lea como un jefe y no como el mismo granadero de cerca
#La forma exacta de decirlo: el jefe tiene que ser el escalado PELADO del granadero salvo en los
#pixeles del galon. Comparandolo con el escalado pelado no hace falta adivinar que es galon y que
#no: lo que difiere ES el galon, y tiene que ser poco. Asi tambien se cubre el contorno oscuro de
#la placa, que no es dorado pero tambien es galon
tropa = cargar('granadero_fr_izq_0.png')
jefe = cargar('jefegranadero_fr_izq_0.png')
plano = pygame.transform.scale(tropa, (tropa.get_width() * 2, tropa.get_height() * 2))
distintos = [(x, y) for y in range(jefe.get_height()) for x in range(jefe.get_width())
             if tuple(jefe.get_at((x, y))) != tuple(plano.get_at((x, y)))]
totalDePixeles = jefe.get_width() * jefe.get_height()
comprobar("el jefe es el granadero escalado a pelo, salvo el galon",
          0 < len(distintos) < totalDePixeles * 0.08,
          "%d pixeles de galon sobre %d del sprite (%.1f%%)"
          % (len(distintos), totalDePixeles, 100.0 * len(distintos) / totalDePixeles))
comprobar("y el galon se concentra en el bonete y el hombro, no repartido por todo el cuerpo",
          max(y for _, y in distintos) - min(y for _, y in distintos) < jefe.get_height() * 0.6,
          "el galon va de la fila %d a la %d de %d"
          % (min(y for _, y in distintos), max(y for _, y in distintos), jefe.get_height()))

# ---- 2. la clase ----
jefe = E.jefeGranadero(100, 100, 300, 300)
comprobar("el jefe es un granadero: hereda su forma de plantarse y de lanzar",
          isinstance(jefe, E.granadero))
comprobar("se sabe jefe, y la tropa no",
          jefe.ES_JEFE and not E.granadero(0, 0, 0, 0).ES_JEFE and not E.enemigo(0, 0, 0, 0).ES_JEFE)
comprobar("su caja de cuerpo tambien es el doble",
          (jefe.ANCHO_REFERENCIA, jefe.ALTO_REFERENCIA)
          == (E.granadero.ANCHO_REFERENCIA * 2, E.granadero.ALTO_REFERENCIA * 2),
          "%s contra %s" % ((jefe.ANCHO_REFERENCIA, jefe.ALTO_REFERENCIA),
                            (E.granadero.ANCHO_REFERENCIA, E.granadero.ALTO_REFERENCIA)))
comprobar("aguanta cuatro veces mas que un granadero",
          jefe.vida >= 4 * E.granadero.VIDA_INICIAL,
          "%d contra %d" % (jefe.vida, E.granadero.VIDA_INICIAL))
comprobar("y suelta objeto seguro", jefe.PROBABILIDAD_SUELTA == 1.0)

# ---- 3. las rafagas: de una en una, y una fase por cada trozo de vida ----
JUGADOR = (250, 250)


def unJefeColocado():
    """Un jefe ya plantado en su anillo, como llega a estarlo en la partida."""
    jefe = E.jefeGranadero(480, 250, JUGADOR[0], JUGADOR[1])
    for _ in range(600):
        jefe.pathFinding(JUGADOR[0], JUGADOR[1])
    return jefe


def soltarUnaRafaga(jefe):
    """Le deja soltar una rafaga entera y devuelve las granadas."""
    enElAire = []
    #la recarga MAS el desfase propio: el granadero nace con un desfase aleatorio para que no
    #lancen todos a la vez, y sin contarlo esta espera se queda corta a veces
    reloj['ms'] += E.RECARGA_DE_LA_RAFAGA + E.DESFASE_MAXIMO_DESCARGA
    jefe.lanzar(enElAire, JUGADOR)
    reloj['ms'] += E.DURACION_ARMADO
    for _ in range(60):
        jefe.lanzar(enElAire, JUGADOR)
        reloj['ms'] += max(E.INTERVALO_DE_LA_RAFAGA, E.PAUSA_ENTRE_ANILLOS)
        if not jefe.rafagaPendiente:
            break
    return enElAire


jefe = unJefeColocado()
comprobar("el jefe se planta en su anillo, como el granadero",
          jefe.aTiro(JUGADOR) and jefe.stop,
          "a %.0f px, quieto=%s" % (jefe.distanciaA(JUGADOR), jefe.stop))

enElAire = []
reloj['ms'] += E.RECARGA_DE_LA_RAFAGA + E.DESFASE_MAXIMO_DESCARGA
jefe.lanzar(enElAire, JUGADOR)
comprobar("primero arma, como el granadero", jefe.armando and enElAire == [])
reloj['ms'] += E.DURACION_ARMADO
jefe.lanzar(enElAire, JUGADOR)
comprobar("al acabar el armado cae la primera de la rafaga", len(enElAire) == 1,
          "%d granadas" % len(enElAire))
comprobar("y quedan las demas pendientes", len(jefe.rafagaPendiente) >= 2,
          "quedan %d" % len(jefe.rafagaPendiente))
jefe.lanzar(enElAire, JUGADOR)
comprobar("las siguientes no salen todas en el mismo frame", len(enElAire) == 1,
          "%d granadas" % len(enElAire))
#solo hasta que se vacie: dejandolo correr mas, al jefe le entra la rafaga SIGUIENTE y la
#comprobacion mediria otra cosa
for _ in range(30):
    if not jefe.rafagaPendiente:
        break
    reloj['ms'] += E.INTERVALO_DE_LA_RAFAGA
    jefe.lanzar(enElAire, JUGADOR)
comprobar("pero acaba soltando la rafaga entera", not jefe.rafagaPendiente,
          "quedan %d, sueltas %d" % (len(jefe.rafagaPendiente), len(enElAire)))
comprobar("no empieza otra rafaga justo despues", not jefe.puedeLanzar(reloj['ms']),
          "recarga de %d ms" % jefe.recargaGranada)

# ---- las tres fases ----
comprobar("con la vida entera ataca con la lluvia",
          jefe.faseDelAtaque() == E.ATAQUE_LLUVIA, jefe.faseDelAtaque())
jefe.vida = int(jefe.vidaMaxima * E.VIDA_PARA_LOS_ANILLOS)
comprobar("bajando de tres cuartos pasa a los anillos",
          jefe.faseDelAtaque() == E.ATAQUE_ANILLOS, jefe.faseDelAtaque())
jefe.vida = int(jefe.vidaMaxima * E.VIDA_PARA_LAS_COLUMNAS)
comprobar("y bajando de un cuarto, a las columnas",
          jefe.faseDelAtaque() == E.ATAQUE_COLUMNAS, jefe.faseDelAtaque())

# fase 1: alrededor del jugador
jefe = unJefeColocado()
lluvia = soltarUnaRafaga(jefe)
comprobar("la lluvia son varias granadas", len(lluvia) == E.GRANADAS_DE_LA_LLUVIA,
          "%d granadas" % len(lluvia))
distancias = [((granada.destino[0] - JUGADOR[0]) ** 2
               + (granada.destino[1] - JUGADOR[1]) ** 2) ** 0.5 for granada in lluvia]
comprobar("y caen alrededor del JUGADOR, no del jefe",
          max(distancias) < 2 * E.DISPERSION_DE_LA_LLUVIA,
          "de %.0f a %.0f px del jugador" % (min(distancias), max(distancias)))

#Lo que hace justa la lluvia no es poder salirse corriendo del area (con nueve granadas y 150 de
#dispersion ya no se puede: el jugador recorre 135 px en el vuelo). Es que SIEMPRE quede un sitio
#a salvo dentro de lo que da tiempo a recorrer. Eso no se deduce de un area, se busca.
recorridoEnElVuelo = J.VELOCIDAD * (granadas.TIEMPO_DE_VUELO / (1000.0 / 30))


def hayDondeMeterse(destinos, desde, alcance, paso=8):
    """Si existe un punto a tiro de correr que ningun estallido alcanza."""
    radio = int(alcance)
    for dx in range(-radio, radio + 1, paso):
        for dy in range(-radio, radio + 1, paso):
            if dx * dx + dy * dy > radio * radio:
                continue
            candidato = (desde[0] + dx, desde[1] + dy)
            if not (0 <= candidato[0] <= E.WINX and 0 <= candidato[1] <= E.WINY):
                continue
            if all(((candidato[0] - x) ** 2 + (candidato[1] - y) ** 2) ** 0.5 > granadas.RADIO
                   for x, y in destinos):
                return True
    return False


sinSalida = 0
for _ in range(200):
    unaLluvia = [punto for punto, _ in jefe._destinosDeLaLluvia(JUGADOR)]
    if not hayDondeMeterse(unaLluvia, JUGADOR, recorridoEnElVuelo):
        sinSalida += 1
comprobar("en 200 lluvias, siempre queda un sitio a salvo a tiro de correr",
          sinSalida == 0, "%d lluvias sin salida" % sinSalida)
comprobar("y son bastantes granadas para que haya que buscarlo, no solo andar",
          E.GRANADAS_DE_LA_LLUVIA >= 8, "%d granadas" % E.GRANADAS_DE_LA_LLUVIA)

# fase 2: la onda, anillos concentricos alrededor del JUGADOR
# El fallo que habia: iban alrededor del JEFE, y bastaba con acorralarlo en una esquina para que
# la fase entera cayese lejos del jugador. Por eso el jefe de esta prueba esta en una esquina.
jefe = E.jefeGranadero(0, 0, JUGADOR[0], JUGADOR[1])
jefe.actualizarRect()
jefe.vida = int(jefe.vidaMaxima * 0.5)
destinos = jefe._destinosDeLaRafaga(JUGADOR)
puntos = [punto for punto, _ in destinos]
esperas = [espera for _, espera in destinos]

distanciasAlJugador = [((x - JUGADOR[0]) ** 2 + (y - JUGADOR[1]) ** 2) ** 0.5 for x, y in puntos]
distanciasAlJefe = [((x - jefe.rect.centerx) ** 2 + (y - jefe.rect.centery) ** 2) ** 0.5
                    for x, y in puntos]
#el centro de la figura tiene que caer sobre el jugador, no sobre el jefe: comparar distancias
#sueltas no vale, porque un punto del anillo grande queda lejos del jugador por definicion
centroDeLaFigura = (sum(x for x, _ in puntos) / float(len(puntos)),
                    sum(y for _, y in puntos) / float(len(puntos)))
alJugador = ((centroDeLaFigura[0] - JUGADOR[0]) ** 2
             + (centroDeLaFigura[1] - JUGADOR[1]) ** 2) ** 0.5
alJefe = ((centroDeLaFigura[0] - jefe.rect.centerx) ** 2
          + (centroDeLaFigura[1] - jefe.rect.centery) ** 2) ** 0.5
comprobar("la onda rodea al JUGADOR, no al jefe, aunque el jefe este acorralado",
          alJugador < 40 and alJefe > 200,
          "el centro de la figura cae a %.0f px del jugador y a %.0f del jefe"
          % (alJugador, alJefe))

#los radios, AGRUPADOS: la trigonometria y el redondeo a pixeles dejan los puntos de un mismo
#anillo a 49, 50 y 51, y contarlos como anillos distintos no mide nada
def agrupar(distancias, tolerancia=6):
    grupos = []
    for distancia in sorted(distancias):
        if grupos and distancia - grupos[-1][-1] <= tolerancia:
            grupos[-1].append(distancia)
        else:
            grupos.append([distancia])
    return grupos


gruposDeRadios = agrupar(distanciasAlJugador)
radios = [round(sum(grupo) / len(grupo)) for grupo in gruposDeRadios]
comprobar("son varios anillos, no una nube", len(radios) >= 3, "radios %s" % radios)
pasos = [b - a for a, b in zip(radios, radios[1:])]
comprobar("y cada anillo roza al de dentro: el paso es el diametro del estallido",
          all(abs(paso - 2 * granadas.RADIO) <= 1 for paso in pasos),
          "pasos %s, diametro del estallido %d" % (pasos, 2 * granadas.RADIO))
comprobar("el primero cae pegado al jugador", min(radios) <= E.RADIO_DEL_PRIMER_ANILLO + 1,
          "el primero a %d px" % min(radios))
comprobar("y el ultimo llega lejos, casi al borde del mapa", max(radios) >= 250,
          "el ultimo a %d px" % max(radios))

#el de dentro esta SELLADO y los de fuera no: eso es lo que echa al jugador del sitio
import math

huecos = [round(2 * math.pi * radio / len(grupo) - 2 * granadas.RADIO)
          for radio, grupo in zip(radios, gruposDeRadios)]
comprobar("el anillo de dentro no deja hueco: quedarse quieto no es una opcion",
          huecos[0] < 0, "hueco del primero: %d px" % huecos[0])
comprobar("y los de fuera si, cada vez mas: por ahi se sale",
          huecos[-1] > J.ANCHO_CUERPO and all(b >= a for a, b in zip(huecos, huecos[1:])),
          "huecos %s px, el jugador mide %d de ancho" % (huecos, J.ANCHO_CUERPO))

#el ritmo: dentro del anillo seguidas, entre anillos pausa
comprobar("dentro de un anillo las granadas van seguidas",
          esperas.count(E.INTERVALO_DENTRO_DEL_ANILLO) >= len(esperas) // 2,
          "esperas %s" % sorted(set(esperas)))
comprobar("y entre anillo y anillo hay pausa, para que se lean como circulos",
          E.PAUSA_ENTRE_ANILLOS > E.INTERVALO_DENTRO_DEL_ANILLO
          and esperas.count(E.PAUSA_ENTRE_ANILLOS) == len(radios),
          "%d pausas para %d anillos" % (esperas.count(E.PAUSA_ENTRE_ANILLOS), len(radios)))

#las que no caben en el campo se saltan, no se recortan al borde
comprobar("ninguna granada de la onda cae fuera del campo",
          all(0 <= x <= E.WINX and 0 <= y <= E.WINY for x, y in puntos), "%s" % puntos[:4])
enElBorde = sum(1 for x, y in puntos if x in (0, E.WINX) or y in (0, E.WINY))
comprobar("y no se amontonan en el borde: las de fuera se saltan, no se pegan al canto",
          enElBorde <= 2, "%d granadas justo en el borde" % enElBorde)

#y con el jugador en una esquina la onda sigue siendo una onda, no un monton
enLaEsquina = E.jefeGranadero(250, 250, 10, 10)
enLaEsquina.actualizarRect()
enLaEsquina.vida = int(enLaEsquina.vidaMaxima * 0.5)
suyos = [punto for punto, _ in enLaEsquina._destinosDeLaRafaga((10, 10))]
comprobar("con el jugador pegado a una esquina, la onda no se rompe",
          suyos and all(0 <= x <= E.WINX and 0 <= y <= E.WINY for x, y in suyos),
          "%d granadas" % len(suyos))

# fase 3: el barrido, que cubre el mapa ENTERO en un solo ataque
jefe = unJefeColocado()
jefe.vida = int(jefe.vidaMaxima * 0.1)
barrido = jefe._destinosDeLaRafaga(JUGADOR)
puntos = [punto for punto, _ in barrido]
columnas = sorted(set(x for x, _ in puntos))

comprobar("el barrido usa muchas columnas, no una", len(columnas) >= 6,
          "columnas en x=%s" % columnas)
separaciones = [b - a for a, b in zip(columnas, columnas[1:])]
comprobar("a lo ancho no queda hueco: cada columna se toca con la siguiente",
          all(separacion <= 2 * granadas.RADIO for separacion in separaciones),
          "separaciones %s, estallido de %d de diametro" % (separaciones, 2 * granadas.RADIO))
comprobar("y llega a los dos bordes del mapa",
          columnas[0] - granadas.RADIO <= 0 and columnas[-1] + granadas.RADIO >= E.WINX,
          "de x=%d a x=%d, con estallidos de radio %d"
          % (columnas[0], columnas[-1], granadas.RADIO))

#los pares: entran por los bordes y se cierran
pares = []
for punto, espera in barrido:
    if espera == E.PAUSA_ENTRE_COLUMNAS or not pares:
        pares.append([])
    pares[-1].append(punto)
columnasPorPar = [sorted(set(x for x, _ in par)) for par in pares]
comprobar("el barrido entra por par de columnas, uno por cada borde",
          len(columnasPorPar) >= 3 and len(columnasPorPar[0]) == 2,
          "%s" % columnasPorPar)
comprobar("el primer par son los dos bordes",
          columnasPorPar[0][0] < E.WINX * 0.15 and columnasPorPar[0][1] > E.WINX * 0.85,
          "primer par en x=%s" % columnasPorPar[0])
comprobar("y cada par se cierra sobre el anterior, hasta juntarse en el centro",
          all(b[0] > a[0] and b[-1] < a[-1] for a, b in zip(columnasPorPar, columnasPorPar[1:])),
          "%s" % columnasPorPar)
comprobar("todo eso en UN ataque, no uno por rafaga",
          len(barrido) == sum(len(par) for par in pares) and len(pares) >= 3,
          "%d granadas en %d pares" % (len(barrido), len(pares)))

#los pasillos: a lo alto, y del tamanio del jugador
pasillosPorPar = []
for par in pares:
    alturas = sorted(set(y for _, y in par))
    pasillosPorPar.append([b - a - 2 * granadas.RADIO for a, b in zip(alturas, alturas[1:])])
comprobar("a lo alto quedan pasillos, y cabe el jugador",
          all(pasillos and min(pasillos) >= J.ALTO_CUERPO for pasillos in pasillosPorPar),
          "pasillos por par: %s, el jugador mide %d" % (pasillosPorPar, J.ALTO_CUERPO))

#y los pasillos se MUEVEN de un par al siguiente: si no, bastaria con aparcar en uno
alturasPorPar = [sorted(set(y for _, y in par)) for par in pares]
comprobar("y los pasillos se desplazan de un par al siguiente: aparcar no vale",
          all(set(a) != set(b) for a, b in zip(alturasPorPar, alturasPorPar[1:])),
          "alturas por par: %s" % alturasPorPar)
#lo que hay que moverse, contra lo que se puede moverse en lo que tarda en llegar el par siguiente
saltoQuePide = abs(alturasPorPar[1][0] - alturasPorPar[0][0])
loQueSeMueve = J.VELOCIDAD * (len(pares[0]) * E.INTERVALO_DENTRO_DE_LA_COLUMNA
                              + E.PAUSA_ENTRE_COLUMNAS) / (1000.0 / 30)
comprobar("y da tiempo a cambiar de pasillo antes de que llegue el par siguiente",
          loQueSeMueve > saltoQuePide,
          "hay que moverse %d px y se pueden mover %.0f" % (saltoQuePide, loQueSeMueve))

#el ritmo, como en la onda
esperas = [espera for _, espera in barrido]
comprobar("dentro de un par las granadas van seguidas, y entre pares hay pausa",
          E.PAUSA_ENTRE_COLUMNAS > E.INTERVALO_DENTRO_DE_LA_COLUMNA
          and esperas.count(E.PAUSA_ENTRE_COLUMNAS) == len(pares),
          "%d pausas para %d pares" % (esperas.count(E.PAUSA_ENTRE_COLUMNAS), len(pares)))
comprobar("y ninguna granada del barrido cae fuera del campo",
          all(0 <= x <= E.WINX and 0 <= y <= E.WINY for x, y in puntos), "%s" % puntos[:4])

# ---- 4. la rueda de jefes ----
conJefe = [numero for numero in range(1, 41) if oleadas.tocaJefe(numero)]
comprobar("no hay jefes antes de su oleada", min(conJefe) == oleadas.PRIMERA_OLEADA_CON_JEFE,
          "el primero en la %d" % min(conJefe))
comprobar("y luego cada cierto numero de oleadas, siempre el mismo",
          all(b - a == oleadas.OLEADAS_ENTRE_JEFES for a, b in zip(conJefe, conJefe[1:])),
          "%s" % conJefe)
comprobar("cada oleada con jefe dice cual le toca, y las demas ninguno",
          all((oleadas.jefeDeLaOleada(numero) is not None) == oleadas.tocaJefe(numero)
              for numero in range(1, 41)))
comprobar("la rueda da la vuelta en vez de acabarse",
          oleadas.jefeDeLaOleada(conJefe[0])
          == oleadas.jefeDeLaOleada(conJefe[len(oleadas.RUEDA_DE_JEFES)]),
          "rueda de %d: %s" % (len(oleadas.RUEDA_DE_JEFES), str(oleadas.RUEDA_DE_JEFES)))

#el jefe entra el PRIMERO de su oleada: si sale a mitad, el campo ya esta lleno y se pierde
oleada = oleadas.Oleada(oleadas.PRIMERA_OLEADA_CON_JEFE, reloj['ms'])
comprobar("el primero que saca una oleada con jefe es el jefe",
          oleada.sacarSiguiente(reloj['ms']) == oleadas.JEFE)
sacados = [oleada.sacarSiguiente(reloj['ms']) for _ in range(oleada.cupo())]
comprobar("y solo hay uno en toda la oleada", sacados.count(oleadas.JEFE) == 0,
          "%d jefes mas" % sacados.count(oleadas.JEFE))

# ---- 5. la barra de vida del jefe ----
def pintado(enemigos):
    """Pixeles de VIDA de la barra. El fondo del marco no cuenta: ese no se mueve.

    La franja donde mirar se saca del propio HUD y no de un numero a mano: la barra va debajo del
    panel del jugador, y si el panel cambia de alto la barra se mueve con el.
    """
    lienzo = pygame.Surface((500, 500))
    lienzo.fill((0, 0, 0))
    hud.dibujarVidaJefe(lienzo, enemigos, 500)
    arriba = hud.altoPanel() + hud.SEPARACION_BAJO_EL_PANEL
    return sum(1 for y in range(arriba, arriba + hud.ALTO_BARRA_JEFE) for x in range(500)
               if lienzo.get_at((x, y))[:3] == hud.COLOR_VIDA_JEFE)


comprobar("sin jefes en el campo no hay barra de jefe",
          pintado([E.granadero(0, 0, 0, 0), E.enemigo(0, 0, 0, 0)]) == 0)
elJefe = E.jefeGranadero(100, 100, 0, 0)
conBarra = pintado([elJefe])
comprobar("con un jefe vivo si", conBarra > 0, "%d pixeles" % conBarra)
elJefe.vida = elJefe.vidaMaxima // 2
aMedias = pintado([elJefe])
comprobar("y baja cuando le baja la vida", aMedias < conBarra,
          "%d pixeles a media vida contra %d a vida entera" % (aMedias, conBarra))
elJefe.vida = 0
elJefe.checkEstadoVida()
comprobar("y desaparece cuando cae", pintado([elJefe]) == 0)

# ---- 6. la partida sabe meterlo en el campo ----
juego = entorno.cargarJuego()
juego['reiniciarPartida']()
juego['oleada'] = oleadas.Oleada(oleadas.PRIMERA_OLEADA_CON_JEFE, reloj['ms'])
juego['entrarEnBatalla'](oleadas.JEFE)
jefes = [uno for uno in juego['enemies'] if getattr(uno, 'ES_JEFE', False)]
comprobar("entrarEnBatalla construye el jefe que dice la rueda",
          len(jefes) == 1 and isinstance(jefes[0], E.jefeGranadero),
          str([type(uno).__name__ for uno in juego['enemies']]))
#la escolta NO entra con el: la pide el propio jefe conforme le baja la vida
comprobar("el jefe entra solo: la escolta va por fases",
          len(juego['enemies']) == 1, "%d en el campo" % len(juego['enemies']))

elJefeDeLaEscolta = jefes[0]
juego['llamarEscoltaDeLosJefes']()
primerGrupo = len(juego['enemies']) - 1
comprobar("con la vida entera ya llama al primer grupo",
          primerGrupo == len(oleadas.ESCOLTA_POR_FASES[0][1]),
          "%d de escolta para un grupo de %d"
          % (primerGrupo, len(oleadas.ESCOLTA_POR_FASES[0][1])))
comprobar("y no llama al siguiente sin que le baje la vida",
          [juego['llamarEscoltaDeLosJefes']() for _ in range(5)]
          and len(juego['enemies']) - 1 == primerGrupo,
          "%d de escolta" % (len(juego['enemies']) - 1))
comprobar("la escolta es tropa de a pie, no mas jefes",
          sum(1 for uno in juego['enemies'] if getattr(uno, 'ES_JEFE', False)) == 1,
          str([type(uno).__name__ for uno in juego['enemies']]))

#y va llamando un grupo por cada escalon de vida que cruza, cada vez mas duro
grupos = [primerGrupo]
for umbral, _ in oleadas.ESCOLTA_POR_FASES[1:]:
    juego['enemies'][:] = [uno for uno in juego['enemies'] if getattr(uno, 'ES_JEFE', False)]
    elJefeDeLaEscolta.vida = int(elJefeDeLaEscolta.vidaMaxima * umbral)
    juego['llamarEscoltaDeLosJefes']()
    grupos.append(len(juego['enemies']) - 1)
comprobar("cruzar cada escalon de vida le trae un grupo nuevo",
          all(grupo > 0 for grupo in grupos), "grupos de %s" % grupos)
comprobar("y el ultimo grupo es el mas gordo: el final del combate es el peor momento",
          grupos[-1] > grupos[0], "primero %d, ultimo %d" % (grupos[0], grupos[-1]))
comprobar("cuando ya ha pedido todos, deja de pedir",
          elJefeDeLaEscolta.oleadasDeEscoltaPedidas == len(oleadas.ESCOLTA_POR_FASES),
          "%d de %d grupos" % (elJefeDeLaEscolta.oleadasDeEscoltaPedidas,
                               len(oleadas.ESCOLTA_POR_FASES)))

#y un grupo entra entero o no entra: gastar el escalon con el campo lleno perderia media escolta
juego['reiniciarPartida']()
juego['entrarEnBatalla'](oleadas.JEFE, oleadas.JEFE_GRANADERO)
elApretado = juego['enemies'][0]
cuantosCabenDelPrimerGrupo = len(oleadas.ESCOLTA_POR_FASES[0][1]) - 1
while len(juego['enemies']) < juego['MAX_ENEMIGOS'] - cuantosCabenDelPrimerGrupo:
    juego['entrarEnBatalla'](oleadas.CUERPO_A_CUERPO)
elCampoLleno = len(juego['enemies'])
juego['llamarEscoltaDeLosJefes']()
comprobar("con el campo casi lleno no mete el grupo a medias",
          len(juego['enemies']) == elCampoLleno and elApretado.oleadasDeEscoltaPedidas == 0,
          "%d en el campo, %d grupos pedidos"
          % (len(juego['enemies']), elApretado.oleadasDeEscoltaPedidas))
juego['enemies'].pop()
juego['llamarEscoltaDeLosJefes']()
comprobar("y en cuanto hay sitio para el grupo entero, entra",
          elApretado.oleadasDeEscoltaPedidas == 1
          and len(juego['enemies']) == elCampoLleno - 1 + len(oleadas.ESCOLTA_POR_FASES[0][1]),
          "%d en el campo, %d grupos pedidos"
          % (len(juego['enemies']), elApretado.oleadasDeEscoltaPedidas))
comprobar("y nunca pasa del techo de franceses",
          len(juego['enemies']) <= juego['MAX_ENEMIGOS'],
          "%d de %d" % (len(juego['enemies']), juego['MAX_ENEMIGOS']))

# ---- 7. el jefe de sable: el oficial al doble, con tajo en area y carga ----
faltanSable = ['jefesable_fr_%s_cuerpoAcuerpo_%d.png' % (lado, numero)
               for lado in ('izq', 'dch') for numero in range(7)
               if not os.path.exists(os.path.join(
                   CARPETA, 'jefesable_fr_%s_cuerpoAcuerpo_%d.png' % (lado, numero)))]
comprobar("estan los 14 sprites del jefe de sable", not faltanSable, "faltan %s" % faltanSable)

malMedidos, sinGalon = [], []
for lado in ('izq', 'dch'):
    for numero in range(7):
        oficial = cargar('oficial_fr_%s_cuerpoAcuerpo_%d.png' % (lado, numero))
        jefeSprite = cargar('jefesable_fr_%s_cuerpoAcuerpo_%d.png' % (lado, numero))
        if jefeSprite.get_size() != (oficial.get_width() * 2, oficial.get_height() * 2):
            malMedidos.append((lado, numero, jefeSprite.get_size(), oficial.get_size()))
        plano = pygame.transform.scale(oficial, jefeSprite.get_size())
        distintos = sum(1 for y in range(jefeSprite.get_height())
                        for x in range(jefeSprite.get_width())
                        if tuple(jefeSprite.get_at((x, y))) != tuple(plano.get_at((x, y))))
        if not distintos:
            sinGalon.append('%s_%d' % (lado, numero))
comprobar("el jefe de sable mide exactamente el doble que el oficial, en los 14",
          not malMedidos, "%s" % malMedidos)
comprobar("y los 14 llevan galon propio encima del escalado",
          not sinGalon, "sin galon: %s" % sinGalon)

comprobar("hereda del oficial, asi que trae su aura de mando puesta",
          issubclass(E.jefeSable, E.oficial))
elSable = E.jefeSable(100, 250, JUGADOR[0], JUGADOR[1])
comprobar("se sabe jefe y aguanta como un jefe",
          elSable.ES_JEFE and elSable.vida == E.VIDA_JEFE_SABLE,
          "vida %d" % elSable.vida)
comprobar("su caja es el doble que la del oficial",
          (elSable.ANCHO_REFERENCIA, elSable.ALTO_REFERENCIA)
          == (E.oficial.ANCHO_REFERENCIA * 2, E.oficial.ALTO_REFERENCIA * 2),
          "%s" % str((elSable.ANCHO_REFERENCIA, elSable.ALTO_REFERENCIA)))


def unBlanco(x, y):
    """Un jugador de carton, para ver a quien alcanza cada ataque."""
    soldado = J.jugador(x, y)
    soldado.rect.topleft = (x, y)
    return soldado


# ---- el tajo en area: alcanza sin tocar ----
elSable = E.jefeSable(250, 250, 250, 250)
elSable.actualizarRect()
comprobar("su tajo barre un circulo mas grande que el alcance de la tropa",
          E.RADIO_DEL_TAJO_DEL_JEFE > E.ALCANCE_SABLE + E.enemigo.ANCHO_REFERENCIA,
          "circulo de %d px contra el cuerpo+%d de la tropa"
          % (E.RADIO_DEL_TAJO_DEL_JEFE, E.ALCANCE_SABLE))

aTiro = unBlanco(elSable.rect.centerx + E.RADIO_DEL_TAJO_DEL_JEFE - 30, elSable.rect.centery)
sinTocar = not elSable.rect.colliderect(aTiro.rect)
rastros = []
reloj['ms'] += E.RECARGA_DEL_TAJO_DEL_JEFE
elSable.atacar(aTiro, rastros)
comprobar("empieza a alzar con el jugador dentro del circulo, aunque no le toque",
          elSable.alzandoSable and sinTocar,
          "alzando=%s, cuerpos separados=%s" % (elSable.alzandoSable, sinTocar))
vidaAntes = aTiro.vida
reloj['ms'] += E.DURACION_ALZADO_DEL_JEFE
elSable.atacar(aTiro, rastros)
comprobar("y al caer el tajo le alcanza sin haberle tocado nunca",
          vidaAntes - aTiro.vida == E.DANIO_DEL_TAJO_DEL_JEFE,
          "%d de vida" % (vidaAntes - aTiro.vida))

#y se esquiva saliendose del circulo durante el aviso
elSable = E.jefeSable(250, 250, 250, 250)
elSable.actualizarRect()
esquivador = unBlanco(elSable.rect.centerx + 40, elSable.rect.centery)
reloj['ms'] += E.RECARGA_DEL_TAJO_DEL_JEFE
elSable.atacar(esquivador, rastros)
comprobar("el tajo avisa antes de caer", elSable.alzandoSable)
comprobar("y avisa mas que el de la tropa, porque barre mucho mas",
          E.DURACION_ALZADO_DEL_JEFE > E.DURACION_ALZADO,
          "%d ms contra %d" % (E.DURACION_ALZADO_DEL_JEFE, E.DURACION_ALZADO))
esquivador.x = elSable.rect.centerx + E.RADIO_DEL_TAJO_DEL_JEFE + 60
esquivador.rect.topleft = (esquivador.x, esquivador.y)
reloj['ms'] += E.DURACION_ALZADO_DEL_JEFE
elSable.atacar(esquivador, rastros)
comprobar("saliendose del circulo durante el aviso, el tajo cae al aire",
          esquivador.vida == esquivador.vidaMaxima, "vida %d" % esquivador.vida)

# ---- la carga ----
elSable = E.jefeSable(60, 250, 250, 250)
elSable.actualizarRect()
victima = unBlanco(300, 250)
reloj['ms'] += E.RECARGA_DE_LA_CARGA
elSable.cargar(victima)
comprobar("con el jugador a tiro, avisa antes de embestir",
          elSable.avisandoCarga and not elSable.cargando)
partida = elSable.x
elSable.pathFinding(victima.x, victima.y)
comprobar("no se mueve mientras avisa", elSable.x == partida,
          "de %s a %s" % (partida, elSable.x))

reloj['ms'] += E.AVISO_DE_LA_CARGA
elSable.cargar(victima)
comprobar("cumplido el aviso, embiste", elSable.cargando and not elSable.avisandoCarga)
antesDeCargar = elSable.x
vidaAntes = victima.vida
for _ in range(60):
    elSable.cargar(victima)
    reloj['ms'] += 33
    if not elSable.cargando:
        break
comprobar("la embestida le lleva hacia el jugador, y lejos", elSable.x - antesDeCargar > 100,
          "ha recorrido %.0f px" % (elSable.x - antesDeCargar))
comprobar("y al alcanzarle le quita DANIO_DE_LA_CARGA de una vez",
          vidaAntes - victima.vida == E.DANIO_DE_LA_CARGA,
          "%d de vida" % (vidaAntes - victima.vida))
comprobar("al acertar se para: embestir y seguir empujando seria imparable",
          not elSable.cargando)
comprobar("y se queda un momento plantado, que es la ventana para castigarle",
          elSable.recuperandoDeLaCarga(reloj['ms']),
          "recuperacion de %d ms" % E.RECUPERACION_DE_LA_CARGA)

#el rumbo se decide AL AVISAR, asi que apartarse funciona
elSable = E.jefeSable(60, 250, 250, 250)
elSable.actualizarRect()
listo = unBlanco(300, 250)
reloj['ms'] += E.RECARGA_DE_LA_CARGA + E.RECUPERACION_DE_LA_CARGA
elSable.cargar(listo)
comprobar("avisa apuntando a donde esta el jugador", elSable.avisandoCarga)
listo.y = 60
listo.rect.topleft = (listo.x, listo.y)
reloj['ms'] += E.AVISO_DE_LA_CARGA
vidaAntes = listo.vida
for _ in range(60):
    elSable.cargar(listo)
    reloj['ms'] += 33
    if not elSable.cargando:
        break
comprobar("apartandose durante el aviso, la embestida pasa de largo",
          listo.vida == vidaAntes, "%d de vida perdida" % (vidaAntes - listo.vida))

#no hace las dos cosas a la vez
elSable = E.jefeSable(250, 250, 250, 250)
elSable.actualizarRect()
pegado = unBlanco(elSable.rect.centerx + 20, elSable.rect.centery)
reloj['ms'] += E.RECARGA_DE_LA_CARGA + E.RECARGA_DEL_TAJO_DEL_JEFE
elSable.cargar(pegado)
vidaAntes = pegado.vida
elSable.atacar(pegado, rastros)
comprobar("mientras avisa la carga no taja: un ataque a la vez",
          not elSable.alzandoSable and pegado.vida == vidaAntes)

#y no se sale del campo embistiendo
elSable = E.jefeSable(400, 250, 250, 250)
elSable.actualizarRect()
enElBorde = unBlanco(490, 250)
reloj['ms'] += E.RECARGA_DE_LA_CARGA + E.RECUPERACION_DE_LA_CARGA
elSable.cargar(enElBorde)
reloj['ms'] += E.AVISO_DE_LA_CARGA
for _ in range(80):
    elSable.cargar(enElBorde)
    reloj['ms'] += 33
    if not elSable.cargando:
        break
comprobar("embistiendo no se sale de la pantalla",
          0 <= elSable.x <= E.WINX - elSable.ANCHO_REFERENCIA
          and 0 <= elSable.y <= E.WINY - elSable.ALTO_REFERENCIA,
          "acaba en (%.0f, %.0f)" % (elSable.x, elSable.y))

#los demas enemigos no embisten: el metodo existe por herencia y no hace nada
sinCarga = []
for clase in (E.enemigo, E.enemigoDistancia, E.voltigeur, E.granadero, E.oficial):
    otro = clase(200, 200, 0, 0)
    otro.actualizarRect()
    antes = (otro.x, otro.y)
    for _ in range(30):
        otro.cargar(unBlanco(250, 200))
    if (otro.x, otro.y) != antes:
        sinCarga.append(clase.__name__)
comprobar("y ningun otro enemigo embiste, aunque tenga el metodo por herencia",
          not sinCarga, "se han movido: %s" % sinCarga)

# ---- la rueda alterna los dos jefes ----
conJefe = [numero for numero in range(1, 41) if oleadas.tocaJefe(numero)]
cuales = [oleadas.jefeDeLaOleada(numero) for numero in conJefe[:4]]
comprobar("la rueda alterna los jefes en vez de repetir el mismo",
          len(set(cuales)) == min(len(oleadas.RUEDA_DE_JEFES), len(cuales)),
          "%s" % cuales)
comprobar("y la partida sabe construir los dos",
          all(oleadas.jefeDeLaOleada(numero) in oleadas.RUEDA_DE_JEFES for numero in conJefe),
          "%s" % [oleadas.jefeDeLaOleada(numero) for numero in conJefe[:4]])

# ---- la pausa no regala cargas ----
juegoDelSable = entorno.cargarJuego()
juegoDelSable['reiniciarPartida']()
elSable = E.jefeSable(100, 100, 0, 0)
juegoDelSable['enemies'].append(elSable)
cargaAntes = elSable.instanteUltimaCarga
juegoDelSable['compensarPausa'](5000)
comprobar("la pausa empuja el reloj de la carga",
          elSable.instanteUltimaCarga == cargaAntes + 5000,
          "%d -> %d" % (cargaAntes, elSable.instanteUltimaCarga))

# ---- 8. el giro del tajo en area ----
import sablazos

elSable = E.jefeSable(250, 250, 250, 250)
elSable.actualizarRect()
victima = unBlanco(elSable.rect.centerx + 40, elSable.rect.centery)
rastros = []
reloj['ms'] += E.RECARGA_DEL_TAJO_DEL_JEFE
elSable.atacar(victima, rastros)
comprobar("mientras avisa no ha soltado ningun rastro", rastros == [], "%d rastros" % len(rastros))
reloj['ms'] += E.DURACION_ALZADO_DEL_JEFE
elSable.atacar(victima, rastros)
comprobar("al tajar suelta un barrido, no un sablazo de los de la tropa",
          len(rastros) == 1 and isinstance(rastros[0], sablazos.Barrido),
          "%s" % [type(uno).__name__ for uno in rastros])

barrido = rastros[0]
comprobar("el barrido sale de su centro", (barrido.x, barrido.y) == elSable.rect.center,
          "barrido en (%.0f,%.0f), centro en %s" % (barrido.x, barrido.y, elSable.rect.center))
comprobar("y tiene el MISMO radio que el alcance del golpe: se aprende mirandolo",
          barrido.radio == E.RADIO_DEL_TAJO_DEL_JEFE,
          "rastro de %d, golpe de %d" % (barrido.radio, E.RADIO_DEL_TAJO_DEL_JEFE))

angulos = [barrido.anguloDeLaHoja(barrido.instante + paso)
           for paso in range(0, sablazos.DURACION_BARRIDO + 1, 40)]
comprobar("la hoja va girando, no se queda quieta",
          all(b > a for a, b in zip(angulos, angulos[1:])),
          "angulos %s" % [round(a) for a in angulos])
comprobar("y da mas de una vuelta entera, para que se lea como un giro",
          angulos[-1] > 360, "acaba en %.0f grados" % angulos[-1])
comprobar("el barrido se acaba", barrido.terminado(barrido.instante + sablazos.DURACION_BARRIDO))
comprobar("y lo limpia el mismo limpiar() que los demas rastros",
          sablazos.limpiar([barrido], barrido.instante + sablazos.DURACION_BARRIDO) == [])

#el cuerpo: gira alternando el lado al que mira. Rotar el sprite le haria dar volteretas
elSable.izq = True
elSable.dch = False
elSable.instanteUltimoTajo = reloj['ms']
elSable.alzandoSable = False
lados = []
for paso in range(0, E.DURACION_DEL_GIRO, E.MS_POR_MEDIA_VUELTA // 2):
    reloj['ms'] = elSable.instanteUltimoTajo + paso
    lados.append('izq' if elSable.sprite() is elSable.TAJAR_IZQ else 'dch')
comprobar("mientras gira, el cuerpo alterna el lado al que mira",
          'izq' in lados and 'dch' in lados, "lados %s" % lados)
#lo que importa es que alterne con REGULARIDAD, no que los lados salgan empatados: el giro dura
#cinco medias vueltas, asi que empatados no pueden salir
rachas = []
for lado in lados:
    if rachas and rachas[-1][0] == lado:
        rachas[-1][1] += 1
    else:
        rachas.append([lado, 1])
comprobar("y alterna a un ritmo regular, no a saltos",
          len(set(largo for _, largo in rachas[:-1])) == 1,
          "rachas %s" % [largo for _, largo in rachas])

reloj['ms'] = elSable.instanteUltimoTajo + E.DURACION_DEL_GIRO + 10
comprobar("acabado el giro deja de girar", not elSable.girando(reloj['ms']))
elSable.stop = True
comprobar("y vuelve a su sprite de siempre",
          elSable.sprite() in (elSable.ANDAR_IZQ[0], elSable.ANDAR_DCH[0],
                               elSable.TAJAR_IZQ, elSable.TAJAR_DCH),
          "sprite de %dx%d" % elSable.sprite().get_size())

#la tropa sigue con su sablazo de toda la vida: el barrido es del jefe
tropa = E.enemigo(200, 200, 0, 0)
tropa.actualizarRect()
suyos = []
tropa.atacar(unBlanco(tropa.rect.centerx, tropa.rect.centery), suyos)
reloj['ms'] += E.DURACION_ALZADO
tropa.atacar(unBlanco(tropa.rect.centerx, tropa.rect.centery), suyos)
comprobar("la tropa sigue soltando su sablazo de siempre, no un barrido",
          suyos and all(isinstance(uno, sablazos.Sablazo) for uno in suyos),
          "%s" % [type(uno).__name__ for uno in suyos])

# ---- 8. el jefe fusilero: el soldado de linea al doble, con descargas de plomo ----
faltanFusilero = [nombre for nombre in
                  ['jefefusilero_fr_%s_%d.png' % (lado, numero)
                   for lado in ('izq', 'dch') for numero in range(7)]
                  + ['jefefusilero_fr_%s_%s.png' % (lado, cola)
                     for lado in ('izq', 'dch') for cola in ('disparar', 'disparar_1')]
                  if not os.path.exists(os.path.join(CARPETA, nombre))]
comprobar("estan los 18 sprites del jefe fusilero", not faltanFusilero,
          "faltan %s" % faltanFusilero)

#el jefe mide el doble de ancho SIEMPRE, y de alto el doble mas lo que haga falta para el penacho.
#El ancho no puede crecer ni un pixel: los sprites que miran a la izquierda se anclan por el borde
#derecho del lienzo (ver render.desplazamiento), asi que un lienzo mas ancho movería al jefe de sitio
malMedidos, sinGalon, sinPenacho = [], [], []
for lado in ('izq', 'dch'):
    for cola in [str(numero) for numero in range(7)] + ['disparar', 'disparar_1']:
        tropa = cargar('soldado_fr_%s_%s.png' % (lado, cola))
        jefeSprite = cargar('jefefusilero_fr_%s_%s.png' % (lado, cola))
        crecido = jefeSprite.get_height() - tropa.get_height() * 2
        if jefeSprite.get_width() != tropa.get_width() * 2 or crecido < 0:
            malMedidos.append((lado, cola, jefeSprite.get_size(), tropa.get_size()))
        #el galon: se compara con el escalado PELADO, y lo que difiera ES el galon
        plano = pygame.transform.scale(tropa, (tropa.get_width() * 2, tropa.get_height() * 2))
        distintos = sum(1 for y in range(plano.get_height())
                        for x in range(plano.get_width())
                        if tuple(jefeSprite.get_at((x, y + crecido))) != tuple(plano.get_at((x, y))))
        if not distintos:
            sinGalon.append('%s_%s' % (lado, cola))
        #y el penacho: pixeles opacos por encima de donde empieza el chaco de la tropa
        alturaDelChaco = crecido + 2 * min(y for y in range(tropa.get_height())
                                           if sum(1 for x in range(tropa.get_width())
                                                  if tropa.get_at((x, y))[3] > OPACO) >= 5)
        blancos = sum(1 for y in range(alturaDelChaco) for x in range(jefeSprite.get_width())
                      if jefeSprite.get_at((x, y))[3] > OPACO
                      and sum(jefeSprite.get_at((x, y))[:3]) > 400)
        if not blancos:
            sinPenacho.append('%s_%s' % (lado, cola))

comprobar("el jefe fusilero mide el doble de ancho, en los 18", not malMedidos, "%s" % malMedidos)
comprobar("y los 18 llevan galon propio encima del escalado", not sinGalon,
          "sin galon: %s" % sinGalon)
comprobar("y penacho blanco por encima del chaco, en los 18", not sinPenacho,
          "sin penacho: %s" % sinPenacho)

# ---- la clase ----
comprobar("es un tirador: hereda su forma de plantarse en su puesto y de mirar al jugador",
          issubclass(E.jefeFusilero, E.enemigoDistancia))
elFusilero = E.jefeFusilero(60, 250, 250, 250)
comprobar("se sabe jefe y aguanta como un jefe",
          elFusilero.ES_JEFE and elFusilero.vida == E.VIDA_JEFE_FUSILERO,
          "vida %d" % elFusilero.vida)
comprobar("su caja es el doble que la del tirador",
          (elFusilero.ANCHO_REFERENCIA, elFusilero.ALTO_REFERENCIA)
          == (E.enemigoDistancia.ANCHO_REFERENCIA * 2, E.enemigoDistancia.ALTO_REFERENCIA * 2),
          "%s" % str((elFusilero.ANCHO_REFERENCIA, elFusilero.ALTO_REFERENCIA)))
comprobar("y la boca del mosquete tambien, o el plomo saldria de la barriga",
          elFusilero.ALTURA_CANON == E.enemigoDistancia.ALTURA_CANON * 2,
          "%d contra %d" % (elFusilero.ALTURA_CANON, E.enemigoDistancia.ALTURA_CANON))
comprobar("se planta el solo en su distancia, sin repartir puesto con la tropa",
          elFusilero.PUESTOS == (E.PUESTO_DEL_JEFE_FUSILERO,)
          and elFusilero.distanciaDeTiro == E.PUESTO_DEL_JEFE_FUSILERO,
          "puestos %s" % (elFusilero.PUESTOS,))
comprobar("y su puesto cabe en el mapa: un jefe pegado al borde se ve a medias",
          E.PUESTO_DEL_JEFE_FUSILERO < E.WINX / 2, "%d px" % E.PUESTO_DEL_JEFE_FUSILERO)

# ---- las tres fases ----
elFusilero.vida = elFusilero.vidaMaxima
comprobar("con la vida entera ataca con el abanico",
          elFusilero.faseDelAtaque() == E.ATAQUE_ABANICO, elFusilero.faseDelAtaque())
elFusilero.vida = int(elFusilero.vidaMaxima * (E.VIDA_PARA_LA_CORTINA - 0.05))
comprobar("bajando de 3/4 pasa a la cortina",
          elFusilero.faseDelAtaque() == E.ATAQUE_CORTINA, elFusilero.faseDelAtaque())
elFusilero.vida = int(elFusilero.vidaMaxima * (E.VIDA_PARA_LA_PLAZA - 0.05))
comprobar("y bajando de 1/4, al fuego de plaza",
          elFusilero.faseDelAtaque() == E.ATAQUE_PLAZA, elFusilero.faseDelAtaque())
comprobar("las dos fronteras las conoce el modo de pruebas, para poder saltar de fase",
          elFusilero.UMBRALES_DE_FASE == (E.VIDA_PARA_LA_CORTINA, E.VIDA_PARA_LA_PLAZA),
          "%s" % (elFusilero.UMBRALES_DE_FASE,))


def unFusileroColocado(proporcion, jugador=(250, 250)):
    """Un jefe fusilero ya plantado en su puesto, como llega a estarlo en la partida."""
    jefe = E.jefeFusilero(60, jugador[1] - 18, jugador[0], jugador[1])
    for _ in range(700):
        jefe.vida = int(jefe.vidaMaxima * proporcion)
        jefe.pathFinding(jugador[0], jugador[1])
    return jefe


def soltarUnaDescarga(jefe, proporcion, jugador=(250, 250)):
    """Le deja soltar una descarga entera y devuelve las balas, en el orden en que salieron."""
    enElAire = []
    #la recarga, el desfase propio Y el medio segundo de apuntado: sin eso no sale ni una bala
    reloj['ms'] += E.RECARGA_DE_LA_DESCARGA + E.DESFASE_MAXIMO_DESCARGA
    for _ in range(400):
        jefe.vida = int(jefe.vidaMaxima * proporcion)
        jefe.disparar(enElAire)
        if enElAire and not jefe.descargaPendiente:
            break
        reloj['ms'] += max(E.DURACION_DE_LA_PUNTERIA, E.INTERVALO_DE_LA_CORTINA,
                           E.PAUSA_ENTRE_ABANICOS, E.PAUSA_ENTRE_ANILLOS_DE_PLOMO)
    return enElAire


def rumbos(balas):
    """El angulo de cada bala, en grados, para poder mirar la forma de la descarga."""
    return [math.degrees(math.atan2(bala.avanceY, bala.avanceX)) for bala in balas]


# ---- fase 1, el abanico: un arco de huecos, y dos veces ----
jefeDelAbanico = unFusileroColocado(1.00)
comprobar("se planta en su puesto, como cualquier tirador",
          jefeDelAbanico.stop and abs(abs(250 - jefeDelAbanico.x) - E.PUESTO_DEL_JEFE_FUSILERO)
          <= E.MARGEN_PUESTO + E.jefeFusilero.VELOCIDAD,
          "a %.0f px de su puesto de %d" % (abs(250 - jefeDelAbanico.x),
                                            E.PUESTO_DEL_JEFE_FUSILERO))
enElAire = soltarUnaDescarga(jefeDelAbanico, 1.00)
comprobar("la descarga son los dos abanicos completos, ni uno mas ni uno menos",
          len(enElAire) == E.BALAS_DEL_ABANICO * E.ABANICOS_POR_DESCARGA,
          "%d balas para %d abanicos de %d"
          % (len(enElAire), E.ABANICOS_POR_DESCARGA, E.BALAS_DEL_ABANICO))
primerArco = rumbos(enElAire[:E.BALAS_DEL_ABANICO])
segundoArco = rumbos(enElAire[E.BALAS_DEL_ABANICO:])
comprobar("el segundo abanico repite los MISMOS angulos: repetir no cierra huecos",
          all(abs(uno - otro) < 0.01 for uno, otro in zip(primerArco, segundoArco)),
          "primero %s / segundo %s" % ([round(a) for a in primerArco],
                                       [round(a) for a in segundoArco]))
comprobar("y el arco va en abanico, cada bala mas abierta que la anterior",
          all(otro > uno for uno, otro in zip(primerArco, primerArco[1:])),
          "%s" % [round(a) for a in primerArco])

#Lo que hace justo el abanico: el hueco junto a la linea de tiro mide lo mismo de lejos que de
#cerca. Se mide simulando, no proyectando angulos sobre una vertical: la punteria no es horizontal
#(la boca del mosquete esta a 42 px del suelo de su caja) y proyectando salian numeros absurdos.
#
#Y se miran los huecos DEL CENTRO, no los de los extremos. Todas las balas recorren lo mismo, asi
#que al llegar estan sobre un arco y no sobre una linea recta, y en el arco los huecos de fuera se
#comprimen. Pero los de fuera caen a mas de 100 px del eje de tiro, o sea donde el jugador no esta:
#el hueco que de verdad usa es el de al lado de la linea de tiro.
def huecosDelAbanico(distanciaAlJefe):
    jefe = E.jefeFusilero(250 - distanciaAlJefe, 250, 250, 250)
    jefe.actualizarRect()
    jefe.pathFinding(250, 250)
    arco = jefe.arcoDeHuecos(jefe.anguloAlObjetivo(), E.BALAS_DEL_ABANICO)
    recorrido = jefe.distanciaAlObjetivo()
    llegada = [(math.cos(angulo) * recorrido, math.sin(angulo) * recorrido) for angulo in arco]
    return [round(((otro[0] - uno[0]) ** 2 + (otro[1] - uno[1]) ** 2) ** 0.5)
            for uno, otro in zip(llegada, llegada[1:])]


DISTANCIAS = (100, 150, 210, 280, 350)
huecos = dict((distancia, huecosDelAbanico(distancia)) for distancia in DISTANCIAS)
#el hueco del centro: con siete balas hay seis huecos y los dos de en medio son los del eje
delCentro = dict((distancia, min(pasos[len(pasos) // 2 - 1:len(pasos) // 2 + 1]))
                 for distancia, pasos in huecos.items())
comprobar("el hueco del eje de tiro deja pasar al jugador desde cualquier distancia",
          all(hueco > J.ALTO_CUERPO for hueco in delCentro.values()),
          "%s, con un jugador de %d de alto" % (delCentro, J.ALTO_CUERPO))
comprobar("y apenas cambia con la distancia, que es de lo que se trata",
          max(delCentro.values()) - min(delCentro.values()) < E.SEPARACION_ENTRE_BALAS / 3,
          "de %d a %d px entre %d y %d de distancia"
          % (min(delCentro.values()), max(delCentro.values()), min(DISTANCIAS), max(DISTANCIAS)))
comprobar("nunca pasa de la separacion pedida: es el techo al que tiende",
          all(hueco <= E.SEPARACION_ENTRE_BALAS for hueco in delCentro.values()),
          "%s para una separacion de %d" % (delCentro, E.SEPARACION_ENTRE_BALAS))

# ---- fase 2, la cortina: el mismo arco, bala a bala y de ida y vuelta ----
jefeDeLaCortina = unFusileroColocado(0.50)
enElAire = soltarUnaDescarga(jefeDeLaCortina, 0.50)
comprobar("la cortina son todas sus pasadas completas",
          len(enElAire) == E.BALAS_DE_LA_CORTINA * E.PASADAS_DE_LA_CORTINA,
          "%d balas para %d pasadas de %d"
          % (len(enElAire), E.PASADAS_DE_LA_CORTINA, E.BALAS_DE_LA_CORTINA))
angulosDeLaIda = rumbos(enElAire[:E.BALAS_DE_LA_CORTINA])
angulosDeLaVuelta = rumbos(enElAire[E.BALAS_DE_LA_CORTINA:2 * E.BALAS_DE_LA_CORTINA])
comprobar("barre en un solo sentido dentro de cada pasada: un barrido que cambia no se lee",
          all(otro > uno for uno, otro in zip(angulosDeLaIda, angulosDeLaIda[1:]))
          or all(otro < uno for uno, otro in zip(angulosDeLaIda, angulosDeLaIda[1:])),
          "%s" % [round(a) for a in angulosDeLaIda])
comprobar("y la vuelta pasa por los MISMOS angulos, al reves: los huecos siguen donde estaban",
          all(abs(uno - otro) < 0.01
              for uno, otro in zip(angulosDeLaIda, reversed(angulosDeLaVuelta))),
          "ida %s / vuelta %s" % ([round(a) for a in angulosDeLaIda],
                                  [round(a) for a in angulosDeLaVuelta]))
#el mismo hueco que el abanico, medido igual: la distancia entre dos balas contiguas al llegar
def huecoCentral(jefe, balas):
    arco = jefe.arcoDeHuecos(jefe.anguloAlObjetivo(), balas)
    recorrido = jefe.distanciaAlObjetivo()
    llegada = [(math.cos(angulo) * recorrido, math.sin(angulo) * recorrido) for angulo in arco]
    pasos = [((otro[0] - uno[0]) ** 2 + (otro[1] - uno[1]) ** 2) ** 0.5
             for uno, otro in zip(llegada, llegada[1:])]
    return round(min(pasos[len(pasos) // 2 - 1:len(pasos) // 2 + 1]))


mismoJefe = unFusileroColocado(0.50)
huecoDeLaCortina = huecoCentral(mismoJefe, E.BALAS_DE_LA_CORTINA)
huecoDelAbanico = huecoCentral(mismoJefe, E.BALAS_DEL_ABANICO)
comprobar("es EL MISMO hueco que el abanico: el jugador aprende una sola medida",
          huecoDeLaCortina == huecoDelAbanico,
          "cortina %d px, abanico %d px" % (huecoDeLaCortina, huecoDelAbanico))
comprobar("pero la cortina es mas ancha: es la escalada de la fase de en medio",
          E.BALAS_DE_LA_CORTINA > E.BALAS_DEL_ABANICO,
          "cortina de %d balas, abanico de %d" % (E.BALAS_DE_LA_CORTINA, E.BALAS_DEL_ABANICO))

#y la cortina es mas ancha que el mapa: no se sale por los lados, se sale por un hueco
jefe = unFusileroColocado(0.50)
arco = jefe.arcoDeHuecos(jefe.anguloAlObjetivo(), E.BALAS_DE_LA_CORTINA)
anchoDeLaPared = E.SEPARACION_ENTRE_BALAS * (E.BALAS_DE_LA_CORTINA - 1)
comprobar("la cortina es mas alta que el mapa: no se sale por los lados",
          anchoDeLaPared >= E.WINY, "pared de %d px en un mapa de %d" % (anchoDeLaPared, E.WINY))

# ---- fase 3, el fuego de plaza: anillos que van girando ----
jefeDeLaPlaza = unFusileroColocado(0.10)
enElAire = soltarUnaDescarga(jefeDeLaPlaza, 0.10)
comprobar("el fuego de plaza son sus anillos completos",
          len(enElAire) == E.BALAS_DEL_ANILLO * E.ANILLOS_DE_LA_PLAZA,
          "%d balas para %d anillos de %d"
          % (len(enElAire), E.ANILLOS_DE_LA_PLAZA, E.BALAS_DEL_ANILLO))
primerAnillo = sorted(rumbos(enElAire[:E.BALAS_DEL_ANILLO]))
pasosDelAnillo = [round(otro - uno) for uno, otro in zip(primerAnillo, primerAnillo[1:])]
comprobar("el anillo reparte las balas por igual en los 360 grados",
          all(abs(paso - 360.0 / E.BALAS_DEL_ANILLO) <= 1 for paso in pasosDelAnillo),
          "pasos de %s grados para un paso de %.1f"
          % (sorted(set(pasosDelAnillo)), 360.0 / E.BALAS_DEL_ANILLO))
segundoAnillo = sorted(rumbos(enElAire[E.BALAS_DEL_ANILLO:2 * E.BALAS_DEL_ANILLO]))
giro = abs(segundoAnillo[0] - primerAnillo[0])
pasoEnGrados = 360.0 / E.BALAS_DEL_ANILLO
comprobar("cada anillo sale girado respecto al anterior: el hueco se mueve",
          giro > 0.5, "girado %.1f grados" % giro)
comprobar("pero girado menos de medio paso, o el hueco se iria mas rapido que el jugador",
          giro < pasoEnGrados / 2 + 0.01,
          "girado %.1f de un paso de %.1f" % (giro, pasoEnGrados))
terceroAnillo = sorted(rumbos(enElAire[2 * E.BALAS_DEL_ANILLO:]))
comprobar("y el tercero no repite al primero, que es lo que pasaba girando medio paso",
          abs(terceroAnillo[0] - primerAnillo[0]) > 0.5,
          "primero %.1f, tercero %.1f" % (primerAnillo[0], terceroAnillo[0]))

#el anillo sale del pecho y no de la punta del canio, o se veria descentrado
jefe = unFusileroColocado(0.10)
jefe.vida = int(jefe.vidaMaxima * 0.10)
comprobar("el anillo sale de su pecho: saliendo de la punta del canio se veria descentrado",
          jefe.origenDelPlomo() == jefe.rect.center,
          "%s contra el centro %s" % (jefe.origenDelPlomo(), jefe.rect.center))
jefe.vida = jefe.vidaMaxima
comprobar("y el abanico sale de la boca del mosquete, que es de donde tiene que salir",
          jefe.origenDelPlomo() == (jefe.xCanon(), jefe.y + jefe.ALTURA_CANON),
          "%s" % (jefe.origenDelPlomo(),))

# ---- dispara sin estar encarado, al contrario que la tropa ----
jefeDeLado = E.jefeFusilero(60, 60, 250, 400)
jefeDeLado.pathFinding(250, 400)
jefeDeLado.actualizarRect()
comprobar("no esta a la altura del jugador",
          not jefeDeLado.encarado(), "desnivel de %d px" % abs(400 - jefeDeLado.y))
enElAire = []
reloj['ms'] += E.RECARGA_DE_LA_DESCARGA + E.DESFASE_MAXIMO_DESCARGA
jefeDeLado.disparar(enElAire)
comprobar("primero apunta, y todavia no ha salido plomo",
          jefeDeLado.apuntando and not enElAire, "%d balas" % len(enElAire))
reloj['ms'] += E.DURACION_DE_LA_PUNTERIA
jefeDeLado.disparar(enElAire)
comprobar("y aun asi dispara: si tuviera que alinearse bastaria con no ponerse a su altura",
          len(enElAire) == E.BALAS_DEL_ABANICO, "%d balas" % len(enElAire))
comprobar("apuntando de verdad al jugador, en diagonal",
          any(abs(bala.avanceY) > 1 for bala in enElAire),
          "rumbos %s" % [round(a) for a in rumbos(enElAire)])
tirador = E.enemigoDistancia(60, 60, 250, 400)
tirador.pathFinding(250, 400)
balasDeLaTropa = []
reloj['ms'] += E.RECARGA_ENEMIGO + E.DESFASE_MAXIMO_DESCARGA
tirador.disparar(balasDeLaTropa)
comprobar("la tropa, en cambio, sigue teniendo que alinearse antes de disparar",
          not balasDeLaTropa, "%d balas" % len(balasDeLaTropa))

# ---- su plomo pega menos que el de la tropa, porque es mucho mas ----
comprobar("cada bala suya pega menos que una de la tropa: son muchas a la vez",
          E.DANIO_DE_LA_PERDIGONADA < proyectile.DANIO_BALA,
          "%d contra %d" % (E.DANIO_DE_LA_PERDIGONADA, proyectile.DANIO_BALA))
comprobar("y todas las de la descarga llevan su danio, no el de la tropa",
          all(bala.danio == E.DANIO_DE_LA_PERDIGONADA for bala in enElAire),
          "%s" % sorted(set(bala.danio for bala in enElAire)))

# ---- no se solapan dos descargas ----
jefe = unFusileroColocado(0.50)
enElAire = []
reloj['ms'] += E.RECARGA_DE_LA_DESCARGA + E.DESFASE_MAXIMO_DESCARGA
jefe.disparar(enElAire)
reloj['ms'] += E.DURACION_DE_LA_PUNTERIA
jefe.disparar(enElAire)
comprobar("empezada la descarga, quedan grupos pendientes", jefe.descargaPendiente,
          "%d grupos" % len(jefe.descargaPendiente))
salidasDeGolpe = len(enElAire)
jefe.disparar(enElAire)
comprobar("y no se sueltan dos grupos en el mismo frame",
          len(enElAire) == salidasDeGolpe, "%d balas" % len(enElAire))

# ---- los cadaveres de los jefes van al doble, como ellos ----
comprobar("los tres jefes mueren con el cadaver al doble, no encogiendose a la mitad",
          all(clase.ESCALA_CADAVER == 2
              for clase in (E.jefeGranadero, E.jefeSable, E.jefeFusilero)),
          "%s" % [(clase.__name__, clase.ESCALA_CADAVER)
                  for clase in (E.jefeGranadero, E.jefeSable, E.jefeFusilero)])
comprobar("y la tropa sigue muriendo a su tamanio",
          all(clase.ESCALA_CADAVER == 1
              for clase in (E.enemigo, E.enemigoDistancia, E.voltigeur, E.granadero, E.oficial)))
comprobar("el cadaver escalado se calcula una sola vez y se guarda",
          E.cadaverEscalado(E.cadaverImg, 2) is E.cadaverEscalado(E.cadaverImg, 2))
comprobar("y a escala 1 devuelve el mismo dibujo, sin copiarlo",
          E.cadaverEscalado(E.cadaverImg, 1) is E.cadaverImg)

# ---- la rueda ya trae tres jefes ----
comprobar("el fusilero esta en la rueda de jefes",
          oleadas.JEFE_FUSILERO in oleadas.RUEDA_DE_JEFES, "%s" % (oleadas.RUEDA_DE_JEFES,))
conJefe = [numero for numero in range(1, 41) if oleadas.tocaJefe(numero)]
cuales = [oleadas.jefeDeLaOleada(numero) for numero in conJefe[:len(oleadas.RUEDA_DE_JEFES)]]
comprobar("y la rueda saca los tres antes de repetir ninguno",
          len(set(cuales)) == len(oleadas.RUEDA_DE_JEFES), "%s" % cuales)
juegoDelFusilero = entorno.cargarJuego()
juegoDelFusilero['reiniciarPartida']()
juegoDelFusilero['entrarEnBatalla'](oleadas.JEFE, oleadas.JEFE_FUSILERO)
comprobar("y la partida sabe construirlo",
          [type(uno).__name__ for uno in juegoDelFusilero['enemies']] == ['jefeFusilero'],
          "%s" % [type(uno).__name__ for uno in juegoDelFusilero['enemies']])

# ---- la pausa no le regala descargas ----
elFusilero = E.jefeFusilero(100, 100, 0, 0)
juegoDelFusilero['enemies'].append(elFusilero)
descargaAntes = elFusilero.instanteDeLaUltimaDeLaDescarga
juegoDelFusilero['compensarPausa'](5000)
comprobar("la pausa empuja el compas de su descarga",
          elFusilero.instanteDeLaUltimaDeLaDescarga == descargaAntes + 5000,
          "%d -> %d" % (descargaAntes, elFusilero.instanteDeLaUltimaDeLaDescarga))
elGranadero = E.jefeGranadero(100, 100, 0, 0)
juegoDelFusilero['enemies'].append(elGranadero)
rafagaAntes = elGranadero.instanteDeLaUltimaDeLaRafaga
juegoDelFusilero['compensarPausa'](5000)
comprobar("y tambien el de la rafaga del granadero, que antes se quedaba sin compensar",
          elGranadero.instanteDeLaUltimaDeLaRafaga == rafagaAntes + 5000,
          "%d -> %d" % (rafagaAntes, elGranadero.instanteDeLaUltimaDeLaRafaga))

# ---- el paraguas: apunta primero, y su plomo va lento ----
comprobar("su plomo va mas lento que el de la tropa: es lo que deja verlo abrirse",
          E.VELOCIDAD_DEL_PLOMO_DEL_JEFE < proyectile.VELOCIDAD_BALA,
          "%d px por frame contra %d"
          % (E.VELOCIDAD_DEL_PLOMO_DEL_JEFE, proyectile.VELOCIDAD_BALA))
jefeLento = unFusileroColocado(1.00)
enElAire = soltarUnaDescarga(jefeLento, 1.00)
velocidades = set(round((bala.avanceX ** 2 + bala.avanceY ** 2) ** 0.5, 3) for bala in enElAire)
comprobar("y todas sus balas van a esa velocidad, en cualquier direccion",
          velocidades == {round(float(E.VELOCIDAD_DEL_PLOMO_DEL_JEFE), 3)}, "%s" % velocidades)
comprobar("con plomo tan lento, cruzar el mapa le lleva mas de tres segundos: se ve venir",
          E.WINX / float(E.VELOCIDAD_DEL_PLOMO_DEL_JEFE) / 30 > 3,
          "%.1f s en cruzar %d px" % (E.WINX / float(E.VELOCIDAD_DEL_PLOMO_DEL_JEFE) / 30, E.WINX))

#el apuntado: se planta, avisa, y entonces empieza a salir plomo
jefeQueApunta = unFusileroColocado(1.00)
enElAire = []
reloj['ms'] += E.RECARGA_DE_LA_DESCARGA + E.DESFASE_MAXIMO_DESCARGA
jefeQueApunta.disparar(enElAire)
comprobar("antes de cada descarga apunta, y todavia no sale plomo",
          jefeQueApunta.apuntando and not enElAire, "%d balas" % len(enElAire))
comprobar("y mientras apunta se queda plantado, que es la ventana para castigarle",
          [jefeQueApunta.pathFinding(400, 400)] and jefeQueApunta.stop,
          "quieto=%s" % jefeQueApunta.stop)
dondeEstaba = (jefeQueApunta.x, jefeQueApunta.y)
for _ in range(20):
    jefeQueApunta.pathFinding(400, 400)
comprobar("no se mueve ni persiguiendo al jugador", (jefeQueApunta.x, jefeQueApunta.y) == dondeEstaba,
          "de %s a %s" % (dondeEstaba, (jefeQueApunta.x, jefeQueApunta.y)))
comprobar("pero si le encara: se ve a donde va a disparar",
          jefeQueApunta.dch, "mira a la izquierda=%s" % jefeQueApunta.izq)
reloj['ms'] += E.DURACION_DE_LA_PUNTERIA
jefeQueApunta.disparar(enElAire)
comprobar("cumplido el aviso, empieza a salir plomo",
          enElAire and not jefeQueApunta.apuntando, "%d balas" % len(enElAire))
comprobar("y avisa menos que el tajo del jefe de sable, porque este no te toca al caer",
          E.DURACION_DE_LA_PUNTERIA < E.DURACION_ALZADO_DEL_JEFE,
          "%d ms contra %d" % (E.DURACION_DE_LA_PUNTERIA, E.DURACION_ALZADO_DEL_JEFE))

#el aviso del suelo: un rayo por cada direccion por la que va a salir plomo
avisos = {}
for proporcion, fase in ((1.00, E.ATAQUE_ABANICO), (0.50, E.ATAQUE_CORTINA),
                         (0.10, E.ATAQUE_PLAZA)):
    jefe = unFusileroColocado(proporcion)
    jefe.vida = int(jefe.vidaMaxima * proporcion)
    avisos[fase] = jefe.angulosDelAviso()
comprobar("el aviso lleva un rayo por bala del abanico",
          len(avisos[E.ATAQUE_ABANICO]) == E.BALAS_DEL_ABANICO,
          "%d rayos para %d balas" % (len(avisos[E.ATAQUE_ABANICO]), E.BALAS_DEL_ABANICO))
comprobar("y la cortina avisa mas ancho que el abanico, que es lo que la distingue",
          len(avisos[E.ATAQUE_CORTINA]) > len(avisos[E.ATAQUE_ABANICO]),
          "%d rayos contra %d" % (len(avisos[E.ATAQUE_CORTINA]),
                                  len(avisos[E.ATAQUE_ABANICO])))
vueltaEntera = sorted(math.degrees(angulo) % 360 for angulo in avisos[E.ATAQUE_PLAZA])
comprobar("y el fuego de plaza avisa en los 360 grados: no hay lado bueno",
          len(vueltaEntera) == E.BALAS_DEL_ANILLO
          and max(vueltaEntera) - min(vueltaEntera) > 300,
          "de %.0f a %.0f grados" % (min(vueltaEntera), max(vueltaEntera)))

#el aviso se recalcula, no se fija: fijandolo, salirse del arco esquivaba la descarga entera
jefeQueApunta = unFusileroColocado(1.00)
enElAire = []
reloj['ms'] += E.RECARGA_DE_LA_DESCARGA + E.DESFASE_MAXIMO_DESCARGA
jefeQueApunta.disparar(enElAire)
avisoAlEmpezar = list(jefeQueApunta.angulosDelAviso())
jefeQueApunta.pathFinding(250, 60)
avisoDespues = list(jefeQueApunta.angulosDelAviso())
comprobar("el aviso sigue al jugador mientras apunta: no se puede pre-esquivar",
          any(abs(uno - otro) > 0.05 for uno, otro in zip(avisoAlEmpezar, avisoDespues)),
          "%s -> %s" % ([round(math.degrees(a)) for a in avisoAlEmpezar],
                        [round(math.degrees(a)) for a in avisoDespues]))
comprobar("y sin apuntar no hay aviso que dibujar",
          not E.jefeFusilero(100, 100, 0, 0).apuntando)

#la pausa tampoco le regala el apuntado
elQueApunta = E.jefeFusilero(100, 100, 0, 0)
juegoDelFusilero['enemies'].append(elQueApunta)
punteriaAntes = elQueApunta.instanteInicioPunteria
juegoDelFusilero['compensarPausa'](5000)
comprobar("la pausa empuja tambien el reloj de su apuntado",
          elQueApunta.instanteInicioPunteria == punteriaAntes + 5000,
          "%d -> %d" % (punteriaAntes, elQueApunta.instanteInicioPunteria))

# ---- la escolta de los jefes es toda de cuerpo a cuerpo ----
tiposDeLaEscolta = sorted(set(tipo for _, tipos in oleadas.ESCOLTA_POR_FASES for tipo in tipos))
comprobar("la escolta de los jefes es TODA de cuerpo a cuerpo, sin un solo tirador",
          tiposDeLaEscolta == [oleadas.CUERPO_A_CUERPO], "%s" % tiposDeLaEscolta)
comprobar("y sin granaderos: sus marcas del suelo competirian con las del jefe",
          oleadas.GRANADERO not in tiposDeLaEscolta and oleadas.VOLTIGEUR not in tiposDeLaEscolta)
#y en el campo de verdad, con un jefe que si pide escolta
juegoDelFusilero['reiniciarPartida']()
juegoDelFusilero['entrarEnBatalla'](oleadas.JEFE, oleadas.JEFE_GRANADERO)
elJefe = juegoDelFusilero['enemies'][0]
for umbral, _ in oleadas.ESCOLTA_POR_FASES:
    elJefe.vida = int(elJefe.vidaMaxima * umbral)
    juegoDelFusilero['llamarEscoltaDeLosJefes']()
escolta = [uno for uno in juegoDelFusilero['enemies'] if not getattr(uno, 'ES_JEFE', False)]
comprobar("y en el campo, de verdad, no entra ni un tirador con el jefe",
          escolta and all(type(uno) is E.enemigo for uno in escolta),
          "%s" % sorted(set(type(uno).__name__ for uno in escolta)))
comprobar("el jefe es el unico que reparte plomo en su combate",
          all(not isinstance(uno, E.enemigoDistancia) for uno in escolta),
          "%s" % sorted(set(type(uno).__name__ for uno in escolta)))

# ---- el fusilero pelea sin guardias: su carga hace el trabajo que hacia la escolta ----
comprobar("el fusilero es el unico de los jefes que no pide escolta",
          not E.jefeFusilero.LLAMA_ESCOLTA
          and E.jefeGranadero.LLAMA_ESCOLTA and E.jefeSable.LLAMA_ESCOLTA,
          "%s" % [(clase.__name__, clase.LLAMA_ESCOLTA)
                  for clase in (E.jefeGranadero, E.jefeSable, E.jefeFusilero)])
juegoDelFusilero['reiniciarPartida']()
juegoDelFusilero['entrarEnBatalla'](oleadas.JEFE, oleadas.JEFE_FUSILERO)
elSolitario = juegoDelFusilero['enemies'][0]
for umbral, _ in oleadas.ESCOLTA_POR_FASES:
    elSolitario.vida = int(elSolitario.vidaMaxima * umbral)
    for _ in range(4):
        juegoDelFusilero['llamarEscoltaDeLosJefes']()
comprobar("y de verdad no le llega nadie en toda la pelea",
          len(juegoDelFusilero['enemies']) == 1,
          "%s" % [type(uno).__name__ for uno in juegoDelFusilero['enemies']])
comprobar("ni se le apunta ningun grupo pedido, para que no le lleguen luego",
          elSolitario.oleadasDeEscoltaPedidas == 0,
          "%d grupos" % elSolitario.oleadasDeEscoltaPedidas)

# ---- su carga a la bayoneta: se turna con la descarga ----
comprobar("usa la misma embestida que el jefe de sable, no una copia",
          issubclass(E.jefeFusilero, E.embestida) and issubclass(E.jefeSable, E.embestida))
comprobar("pero con sus propios numeros: embiste desde mas lejos y mas rapido",
          E.jefeFusilero.DISTANCIA_CARGA > E.jefeSable.DISTANCIA_CARGA
          and E.jefeFusilero.VELOCIDAD_CARGA > E.jefeSable.VELOCIDAD_CARGA,
          "distancia %d contra %d, velocidad %d contra %d"
          % (E.jefeFusilero.DISTANCIA_CARGA, E.jefeSable.DISTANCIA_CARGA,
             E.jefeFusilero.VELOCIDAD_CARGA, E.jefeSable.VELOCIDAD_CARGA))
recorridoDeLaCarga = (E.jefeFusilero.VELOCIDAD_CARGA
                      * (E.jefeFusilero.DURACION_CARGA / (1000.0 / 30)))
comprobar("y la embestida le alcanza desde su puesto de tiro, o no la usaria nunca",
          recorridoDeLaCarga > E.PUESTO_DEL_JEFE_FUSILERO,
          "recorre %.0f px y su puesto esta a %d"
          % (recorridoDeLaCarga, E.PUESTO_DEL_JEFE_FUSILERO))
comprobar("se queda plantado mas rato que el de sable: acaba pegado a ti con un mosquete",
          E.jefeFusilero.RECUPERACION_CARGA > E.jefeSable.RECUPERACION_CARGA,
          "%d ms contra %d" % (E.jefeFusilero.RECUPERACION_CARGA,
                               E.jefeSable.RECUPERACION_CARGA))

#el turno: entra disparando, y solo despues de la descarga le toca embestir
elDelTurno = unFusileroColocado(1.00)
comprobar("entra disparando, no corriendo a por el jugador", not elDelTurno.leTocaCargar)
victima = unBlanco(250, 250)
reloj['ms'] += E.ESPERA_HASTA_LA_CARGA
elDelTurno.cargar(victima)
comprobar("y no embiste si no le toca, aunque tenga al jugador a tiro",
          not elDelTurno.avisandoCarga and not elDelTurno.cargando)
enElAire = soltarUnaDescarga(elDelTurno, 1.00)
comprobar("soltada la descarga, le toca embestir", elDelTurno.leTocaCargar,
          "%d balas soltadas" % len(enElAire))
soltadas = len(enElAire)
reloj['ms'] += E.RECARGA_DE_LA_DESCARGA + E.DESFASE_MAXIMO_DESCARGA
elDelTurno.disparar(enElAire)
comprobar("y esperando su turno de embestir no vuelve a disparar",
          len(enElAire) == soltadas and not elDelTurno.apuntando,
          "%d balas de mas" % (len(enElAire) - soltadas))
elDelTurno.cargar(victima)
comprobar("cumplida la espera, avisa la embestida", elDelTurno.avisandoCarga)
vidaAntes = victima.vida
elDelTurno.disparar(enElAire)
comprobar("y avisando la carga no dispara: un ataque a la vez",
          len(enElAire) == soltadas, "%d balas de mas" % (len(enElAire) - soltadas))
reloj['ms'] += E.AVISO_DE_LA_CARGA_DEL_FUSILERO
elDelTurno.cargar(victima)
comprobar("cumplido el aviso, embiste", elDelTurno.cargando)
comprobar("y embistiendo lleva el mosquete por delante, no al hombro",
          elDelTurno.sprite() in (elDelTurno.DISPARAR_IZQ[0], elDelTurno.DISPARAR_DCH[0]),
          "sprite de %dx%d" % elDelTurno.sprite().get_size())
for _ in range(60):
    elDelTurno.cargar(victima)
    reloj['ms'] += 33
    if not elDelTurno.cargando:
        break
comprobar("le quita DANIO_DE_LA_CARGA_DEL_FUSILERO al alcanzarle",
          vidaAntes - victima.vida == E.DANIO_DE_LA_CARGA_DEL_FUSILERO,
          "%d de vida" % (vidaAntes - victima.vida))
comprobar("acabada la embestida le vuelve a tocar disparar: los dos se turnan",
          not elDelTurno.leTocaCargar)
comprobar("y se queda un momento plantado, que es la ventana para castigarle",
          elDelTurno.recuperandoDeLaCarga(reloj['ms']))

#y si el jugador se queda lejisimos, dispara igual y se guarda el turno: si no, quedandose en el
#fondo del mapa se le desactivaba el jefe entero
elLejano = unFusileroColocado(1.00)
soltarUnaDescarga(elLejano, 1.00)
comprobar("con el turno de embestir pendiente", elLejano.leTocaCargar)
elLejano.xObjectiv = elLejano.x + E.DISTANCIA_DE_LA_CARGA_DEL_FUSILERO + 200
elLejano.yObjectiv = elLejano.y
enElAire = []
reloj['ms'] += E.RECARGA_DE_LA_DESCARGA + E.DESFASE_MAXIMO_DESCARGA + E.ESPERA_HASTA_LA_CARGA
elLejano.disparar(enElAire)
comprobar("con el jugador mas lejos de lo que alcanza la embestida, dispara igual",
          elLejano.apuntando, "apuntando=%s" % elLejano.apuntando)
comprobar("pero se guarda el turno de embestir para cuando se acerque",
          elLejano.leTocaCargar)

raise SystemExit(resumen())
