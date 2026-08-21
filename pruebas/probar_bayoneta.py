"""Pruebas del cuerpo a cuerpo del jugador: el bayonetazo y el dash hacia atras.

Las tres cosas se apoyan entre si y hay que probarlas juntas: el frances avisa un segundo antes
de tajar (eso esta en probar_sable), tu bayoneta llega mas lejos que su sable, y el dash te saca
de los dos alcances. Si cualquiera de las tres se descuadra, el cuerpo a cuerpo deja de poder
jugarse y vuelve a ser solo sufrirlo.
"""
import os
import sys

import entorno
from entorno import comprobar, resumen
import pygame

pygame.init()
pygame.display.set_mode((500, 500))

import enemigo as E
import jugador as J
import render

CARPETA = os.path.join(os.path.dirname(entorno.AQUI), 'sprites', 'ingleses')
ACERO = ((206, 206, 206), (240, 240, 240))
OPACO = 20

reloj = {'ms': 90000}
pygame.time.get_ticks = lambda: reloj['ms']


def unSoldado(x=200, y=200, mirandoIzq=False):
    soldado = J.jugador(x, y)
    soldado.mirando_izq = mirandoIzq
    return soldado


def aDistancia(soldado, hueco, clase=E.enemigo):
    """Un frances cuya CAJA queda a 'hueco' pixeles de la caja del jugador, por delante."""
    frances = clase(0, soldado.y, 0, 0)
    frances.izq = True
    frances.dch = False
    frances.actualizarRect()
    if soldado.mirando_izq:
        frances.x = soldado.rect.left - hueco - frances.CUERPO_IZQ.left - frances.CUERPO_IZQ.width
    else:
        frances.x = soldado.rect.right + hueco - frances.CUERPO_IZQ.left
    frances.actualizarRect()
    return frances


# ---- 1. la bayoneta se ve en TODOS los sprites, y no mueve al soldado ----
POSES = ([('soldado_ingles_%s_%d.png' % (lado, numero), 'andando')
          for lado in ('izq', 'dch') for numero in range(7)]
         + [('soldado_ingles_%s_disparar_1.png' % lado, 'apuntando') for lado in ('izq', 'dch')]
         + [('soldado_ingles_%s_disparar.png' % lado, 'disparando') for lado in ('izq', 'dch')])


def conBayoneta(fichero):
    return fichero[:-len('.png')] + '_bayoneta.png'


faltan = [conBayoneta(fichero) for fichero, _ in POSES
          if not os.path.exists(os.path.join(CARPETA, conBayoneta(fichero)))]
comprobar("los 18 sprites del ingles tienen su version con bayoneta", not faltan,
          "faltan %s" % faltan)
if faltan:
    raise SystemExit(resumen())


def cargar(nombre):
    return pygame.image.load(os.path.join(CARPETA, nombre)).convert_alpha()


def dibujadoEnPantalla(imagen, mirandoIzq):
    """El sprite ya colocado en el campo, como lo pone el juego."""
    lienzo = pygame.Surface((200, 200), pygame.SRCALPHA)
    render.dibujar_anclado(lienzo, imagen, 80, 80, mirandoIzq, J.ANCHO_CUERPO, J.ALTO_CUERPO)
    return lienzo


#El contrato de verdad: la bayoneta ANADE acero y no mueve ni un pixel del soldado. Los lienzos
#crecen (por arriba en los de andar, por delante en los de apuntar) y el anclaje lo compensa
sinAcero, movidos, repintados = [], [], []
for fichero, pose in POSES:
    mirandoIzq = '_izq' in fichero
    limpio = dibujadoEnPantalla(cargar(fichero), mirandoIzq)
    calado = dibujadoEnPantalla(cargar(conBayoneta(fichero)), mirandoIzq)
    anadidos, cambiados = 0, []
    for y in range(200):
        for x in range(200):
            antes, luego = limpio.get_at((x, y)), calado.get_at((x, y))
            if antes == luego:
                continue
            if antes[3] <= OPACO:
                anadidos += 1
            else:
                cambiados.append((x, y))
    if anadidos + len(cambiados) == 0:
        sinAcero.append(conBayoneta(fichero))
    #en el fogonazo la hoja va pintada SOBRE el humo, asi que ahi si se repintan unos pocos
    if pose == 'disparando':
        if len(cambiados) > 14:
            repintados.append((fichero, len(cambiados)))
    elif cambiados:
        movidos.append((fichero, len(cambiados)))

comprobar("todos llevan acero anadido", not sinAcero, "sin acero: %s" % sinAcero)
comprobar("y ninguno mueve ni repinta al soldado: la bayoneta solo anade",
          not movidos, "%s" % movidos)
comprobar("salvo en el fogonazo, donde la hoja va pintada sobre el humo y son cuatro pixeles",
          not repintados, "%s" % repintados)

#la hoja va donde apunta el canion: hacia arriba andando, hacia delante apuntando
andando = cargar(conBayoneta('soldado_ingles_izq_0.png'))
limpioAndando = cargar('soldado_ingles_izq_0.png')
crecimiento = andando.get_height() - limpioAndando.get_height()
comprobar("andando el lienzo crece por arriba, que es donde apunta el canion",
          crecimiento > 0 and andando.get_width() == limpioAndando.get_width(),
          "%s contra %s" % (andando.get_size(), limpioAndando.get_size()))
aceros = [(x, y) for y in range(andando.get_height()) for x in range(andando.get_width())
          if andando.get_at((x, y))[:3] in ACERO and andando.get_at((x, y))[3] > OPACO]
comprobar("y el acero esta en esas filas nuevas, no en medio del cuerpo",
          aceros and max(y for _, y in aceros) < crecimiento + 2,
          "acero en las filas %s, filas nuevas %d" % (sorted(set(y for _, y in aceros)), crecimiento))

apuntando = cargar(conBayoneta('soldado_ingles_izq_disparar_1.png'))
limpioApuntando = cargar('soldado_ingles_izq_disparar_1.png')
comprobar("apuntando crece por delante, que es donde apunta el canion",
          apuntando.get_width() > limpioApuntando.get_width()
          and apuntando.get_height() == limpioApuntando.get_height(),
          "%s contra %s" % (apuntando.get_size(), limpioApuntando.get_size()))

# ---- 2. la caja del acero ----
soldado = unSoldado()
caja = soldado.cajaDeLaBayoneta()
comprobar("mirando a la derecha, el acero barre por delante del cuerpo",
          caja.left == soldado.rect.right and caja.width == J.ALCANCE_BAYONETA,
          "caja %s, cuerpo %s" % (caja, soldado.rect))
soldado.mirando_izq = True
caja = soldado.cajaDeLaBayoneta()
comprobar("y mirando a la izquierda, por el otro lado",
          caja.right == soldado.rect.left and caja.width == J.ALCANCE_BAYONETA,
          "caja %s, cuerpo %s" % (caja, soldado.rect))

# ---- 3. el bayonetazo ----
soldado = unSoldado()
frances = aDistancia(soldado, 4)
vidaAntes = frances.vida
alcanzados = soldado.estocada([frances])
comprobar("el bayonetazo alcanza a quien tiene delante", alcanzados == [frances],
          "%d alcanzados" % len(alcanzados))
comprobar("y le quita DANIO_BAYONETA", vidaAntes - frances.vida == J.DANIO_BAYONETA,
          "%d de vida" % (vidaAntes - frances.vida))
comprobar("pega mas que un disparo, porque para darlo hay que meterse en su alcance",
          J.DANIO_BAYONETA > soldado.danioBala,
          "bayoneta %d, bala %d" % (J.DANIO_BAYONETA, soldado.danioBala))

reloj['ms'] += J.RECARGA_BAYONETA
detras = aDistancia(soldado, 4)
detras.x = soldado.rect.left - 60
detras.actualizarRect()
comprobar("y no alcanza a quien tiene a la espalda", soldado.estocada([detras]) == [])

reloj['ms'] += J.RECARGA_BAYONETA
lejano = aDistancia(soldado, J.ALCANCE_BAYONETA + 10)
comprobar("ni a quien esta fuera de su alcance", soldado.estocada([lejano]) == [])

#la recarga: dos bayonetazos seguidos no valen
reloj['ms'] += J.RECARGA_BAYONETA
victima = aDistancia(soldado, 4)
soldado.estocada([victima])
vidaTrasElPrimero = victima.vida
soldado.estocada([victima])
comprobar("no se puede estocar dos veces en el mismo frame",
          victima.vida == vidaTrasElPrimero, "vida %d" % victima.vida)
reloj['ms'] += J.RECARGA_BAYONETA
soldado.estocada([victima])
comprobar("pero cumplida la recarga, otra vez", victima.vida < vidaTrasElPrimero,
          "vida %d" % victima.vida)

#el estandarte tambien dobla el acero, no solo el plomo
reloj['ms'] += J.RECARGA_BAYONETA
soldado = unSoldado()
soldado.instanteFinDanioDoble = reloj['ms'] + 5000
conEstandarte = aDistancia(soldado, 4)
vidaAntes = conEstandarte.vida
soldado.estocada([conEstandarte])
comprobar("con el estandarte, el bayonetazo tambien pega doble",
          vidaAntes - conEstandarte.vida == J.DANIO_BAYONETA * J.MULTIPLICADOR_DANIO_DOBLE,
          "%d de vida" % (vidaAntes - conEstandarte.vida))

# ---- 4. el hueco donde tu llegas y el no ----
# Esto es lo que hace jugable el cuerpo a cuerpo: hay una franja en la que tu bayoneta alcanza
# y su sable todavia no. Si desaparece, acercarse a pegar deja de tener sentido
soldado = unSoldado()
tuyo, suyo = [], []
for hueco in range(0, 30):
    frances = aDistancia(soldado, hueco)
    if soldado.cajaDeLaBayoneta().colliderect(frances.rect):
        tuyo.append(hueco)
    if frances.alcanceDelSable().colliderect(soldado.rect):
        suyo.append(hueco)
soloTuyo = [hueco for hueco in tuyo if hueco not in suyo]
comprobar("tu bayoneta llega mas lejos que su sable",
          max(tuyo) > max(suyo), "tu hasta %d, el hasta %d" % (max(tuyo), max(suyo)))
comprobar("y queda una franja donde le llegas sin que te llegue",
          len(soloTuyo) >= 6, "huecos %s" % soloTuyo)
comprobar("el dash te saca de las dos franjas de un salto",
          J.DISTANCIA_DASH > max(tuyo) + J.ANCHO_CUERPO,
          "dash %d px, alcance maximo %d" % (J.DISTANCIA_DASH, max(tuyo)))

# ---- 5. el dash ----
soldado = unSoldado(x=250, mirandoIzq=False)
reloj['ms'] += J.RECARGA_DASH
comprobar("el dash esta listo", soldado.puedeDashear(reloj['ms']))
comprobar("y arranca", soldado.dashear())
partida = soldado.x
frames = 0
while soldado.avanzarDash():
    frames += 1
    if frames > 100:
        break
comprobar("va HACIA ATRAS, al lado contrario del que mira", soldado.x < partida,
          "de %d a %d mirando a la derecha" % (partida, soldado.x))
comprobar("recorre la distancia del dash, ni mas ni menos",
          partida - soldado.x == J.DISTANCIA_DASH, "%d px" % (partida - soldado.x))
comprobar("en unos pocos frames, no de golpe", 2 <= frames <= 10, "%d frames" % frames)

soldado = unSoldado(x=250, mirandoIzq=True)
reloj['ms'] += J.RECARGA_DASH
soldado.dashear()
partida = soldado.x
while soldado.avanzarDash():
    pass
comprobar("mirando a la izquierda, salta a la derecha", soldado.x > partida,
          "de %d a %d" % (partida, soldado.x))

#la recarga
soldado = unSoldado(x=250)
reloj['ms'] += J.RECARGA_DASH
soldado.dashear()
while soldado.avanzarDash():
    pass
comprobar("no se puede dashear dos veces seguidas", not soldado.dashear())
reloj['ms'] += J.RECARGA_DASH
comprobar("hasta que pasa la recarga", soldado.dashear())
while soldado.avanzarDash():
    pass

#el borde
soldado = unSoldado(x=10, mirandoIzq=False)
reloj['ms'] += J.RECARGA_DASH
soldado.dashear()
while soldado.avanzarDash():
    pass
comprobar("y contra el borde se para en el borde, no se sale",
          soldado.x == 0 and soldado.rect.left == 0, "x=%d" % soldado.x)

#no se puede estocar en mitad de un dash: el dash es un compromiso
soldado = unSoldado(x=250)
reloj['ms'] += J.RECARGA_BAYONETA + J.RECARGA_DASH
victima = aDistancia(soldado, 4)
soldado.dashear()
comprobar("en mitad de un dash no se estoca", soldado.estocada([victima]) == [],
          "vida del frances %d" % victima.vida)
while soldado.avanzarDash():
    pass
comprobar("y al acabar el dash se vuelve a poder", soldado.estocada([aDistancia(soldado, 4)]) != [])

# ---- 6. el dibujo: el cuerpo se adelanta al estocar ----
def contenidoDibujado(soldado):
    lienzo = pygame.Surface((500, 500), pygame.SRCALPHA)
    soldado.dibujar(lienzo)
    return lienzo.get_bounding_rect()


soldado = unSoldado(x=250, mirandoIzq=True)
reloj['ms'] += J.RECARGA_BAYONETA
quieto = contenidoDibujado(soldado)
soldado.estocada([])
estocando = contenidoDibujado(soldado)
comprobar("mientras dura la estocada el cuerpo sale adelantado, que es lo que la hace legible",
          estocando.left < quieto.left,
          "estocando hasta %d, quieto hasta %d" % (estocando.left, quieto.left))
reloj['ms'] += J.DURACION_ESTOCADA
comprobar("y pasada la estocada vuelve a su sitio",
          contenidoDibujado(soldado).left == quieto.left,
          "%d contra %d" % (contenidoDibujado(soldado).left, quieto.left))

# ---- 7. los dos efectos: el destello de la estocada y la estela del dash ----
import sablazos

soldado = unSoldado(x=250, mirandoIzq=False)
reloj['ms'] += J.RECARGA_BAYONETA
destellos = []
soldado.estocada([], destellos)
comprobar("la estocada suelta un destello, y solo uno", len(destellos) == 1,
          "%d destellos" % len(destellos))
destello = destellos[0]
caja = soldado.cajaDeLaBayoneta()
comprobar("sale de la punta del acero", destello.x == caja.right,
          "destello en x=%.0f, punta del acero en %d" % (destello.x, caja.right))
#el fallo que se vio mirandolo: centrado en la caja del golpe salia 4 px por encima de la hoja
comprobar("y a la altura del canion, no al centro de la caja del golpe",
          destello.y == soldado.y + J.ALTURA_CANON and destello.y != caja.centery,
          "destello en y=%.0f, canion en %d, centro de la caja en %d"
          % (destello.y, soldado.y + J.ALTURA_CANON, caja.centery))

#los instantes van CONTADOS DESDE que nacio el destello, no en absoluto: su reloj arranca en
#el tiempo falso de esta bateria, no en cero
largos = [destello.largoVisible(destello.instante + pasado) for pasado in
          (0, 20, 50, 80, 110, sablazos.DURACION_ESTOCADA)]
comprobar("el destello sale disparado y se recoge, no aparece y se apaga",
          largos[0] < max(largos) and largos[-1] < max(largos),
          "largos %s" % largos)
comprobar("y se acaba", destello.terminado(destello.instante + sablazos.DURACION_ESTOCADA))
comprobar("el mismo limpiar() se lleva destellos y sablazos, que van en la misma lista",
          sablazos.limpiar([destello], destello.instante + sablazos.DURACION_ESTOCADA) == [])

#la estela del dash
soldado = unSoldado(x=250, mirandoIzq=False)
reloj['ms'] += J.RECARGA_DASH
soldado.dashear()
huellas = 0
while soldado.avanzarDash():
    huellas = len(soldado.estelaDelDash)
comprobar("el dash deja huellas por donde ha pasado", huellas >= 2, "%d huellas" % huellas)


def pixelesDeEstela(soldado):
    lienzo = pygame.Surface((500, 500))
    lienzo.fill((0, 0, 0))
    soldado.dibujar(lienzo)
    return sum(1 for y in range(200, 320) for x in range(150, 350)
               if lienzo.get_at((x, y))[:3] not in ((0, 0, 0),)
               and lienzo.get_at((x, y))[0] < lienzo.get_at((x, y))[2])


comprobar("y la estela se ve en pantalla", pixelesDeEstela(soldado) > 0,
          "%d pixeles azulados de estela" % pixelesDeEstela(soldado))
reloj['ms'] += J.DURACION_ESTELA
soldado.dibujar(pygame.Surface((500, 500)))
comprobar("y se borra sola al cabo de su tiempo", soldado.estelaDelDash == [],
          "%d huellas" % len(soldado.estelaDelDash))

# ---- 8. el dash suena a viento, no a clic ----
import random
import sonidos


def crucesPorCero(generador, muestras=4000):
    """Cuantas veces cambia de signo la onda. Es la forma barata de medir si algo es agudo."""
    valores = [generador(indice / 44100.0, indice / float(muestras)) for indice in range(muestras)]
    return sum(1 for antes, luego in zip(valores, valores[1:]) if (antes < 0) != (luego < 0))


comprobar("el zumbido del dash se ha podido sintetizar",
          not isinstance(sonidos.sonido_dash, sonidos.SonidoNulo),
          type(sonidos.sonido_dash).__name__)
delViento = crucesPorCero(sonidos._viento())
delSable = crucesPorCero(sonidos._sable)
delRuido = crucesPorCero(lambda instante, avance: random.uniform(-1.0, 1.0))
comprobar("y suena grave: cruza el cero muchas menos veces que un siseo, o sea que es viento",
          delViento < delRuido / 3 and delViento < delSable / 3,
          "viento %d, sable %d, ruido blanco %d" % (delViento, delSable, delRuido))
comprobar("dura mas que el silbido del sable, que un soplo no es un chasquido",
          sonidos.DURACION_DASH > sonidos.DURACION_SABLE,
          "%.3f s contra %.3f s" % (sonidos.DURACION_DASH, sonidos.DURACION_SABLE))

# ---- 9. la pausa no regala bayonetazos ni dashes ----
juego = entorno.cargarJuego()
juego['reiniciarPartida']()
estocadaAntes = juego['player'].instanteUltimaEstocada
dashAntes = juego['player'].instanteUltimoDash
juego['compensarPausa'](5000)
comprobar("la pausa empuja el reloj de la bayoneta",
          juego['player'].instanteUltimaEstocada == estocadaAntes + 5000)
comprobar("y el del dash", juego['player'].instanteUltimoDash == dashAntes + 5000)

raise SystemExit(resumen())
