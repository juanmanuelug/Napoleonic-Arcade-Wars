"""Pruebas del oficial: sus sprites, su aura de mando y su sitio en las oleadas.

El oficial no dispara ni lanza nada. Lo que hace es multiplicar a los demas: los franceses que
tenga cerca van un 50% mas rapidos. Por eso la mayor parte de esta bateria no mira al oficial,
mira a los OTROS.
"""
import os
import sys

import entorno
from entorno import comprobar, resumen
import pygame

pygame.init()
pygame.display.set_mode((500, 500))

import enemigo as E
import objetos
import oleadas
import render

CARPETA = os.path.join(os.path.dirname(entorno.AQUI), 'sprites', 'franceses')
ORO = (246, 185, 0)
ORO_SOMBRA = (176, 132, 0)
BLANCO = (240, 240, 240)
COLORES_DE_LA_CAPA = (ORO, ORO_SOMBRA, BLANCO)
OPACO = 20


def parejas():
    return [('soldado_fr_%s_cuerpoAcuerpo_%d.png' % (lado, numero),
             'oficial_fr_%s_cuerpoAcuerpo_%d.png' % (lado, numero), lado == 'izq')
            for lado in ('izq', 'dch') for numero in range(7)]


PAREJAS = parejas()


def cargar(nombre):
    return pygame.image.load(os.path.join(CARPETA, nombre)).convert_alpha()


def esquinasDibujadas(imagen, mirandoIzq):
    """Donde acaba el cuerpo dibujado: (izquierda, derecha, pies)."""
    dx, dy = render.desplazamiento(imagen, E.enemigo.ANCHO_REFERENCIA,
                                   E.enemigo.ALTO_REFERENCIA, mirandoIzq)
    contenido = imagen.get_bounding_rect()
    return (dx + contenido.left, dx + contenido.right, dy + contenido.bottom)


def diferencias(base, oficial):
    """(pixeles repintados sobre el cuerpo, pixeles anadidos fuera, colores usados)."""
    filasAnadidas = oficial.get_height() - base.get_height()
    sobreElCuerpo, fueraDelCuerpo, colores = [], [], set()
    for y in range(base.get_height()):
        for x in range(base.get_width()):
            antes = base.get_at((x, y))
            luego = oficial.get_at((x, y + filasAnadidas))
            if antes == luego:
                continue
            colores.add((luego[0], luego[1], luego[2]))
            (fueraDelCuerpo if antes[3] <= OPACO else sobreElCuerpo).append((x, y))
    for y in range(filasAnadidas):
        for x in range(oficial.get_width()):
            pixel = oficial.get_at((x, y))
            if pixel[3] > OPACO:
                colores.add((pixel[0], pixel[1], pixel[2]))
                fueraDelCuerpo.append((x, y - filasAnadidas))
    return sobreElCuerpo, fueraDelCuerpo, colores


# ---- 1. los 14 sprites ----
faltan = [nombre for _, nombre, _ in PAREJAS
          if not os.path.exists(os.path.join(CARPETA, nombre))]
comprobar("estan los 14 sprites del oficial", not faltan, "faltan %s" % faltan)
if faltan:
    raise SystemExit(resumen())

descolocados, crecidos, sinCapa, coloresRaros, penachoAncho = [], [], [], {}, []
for origen, destino, mirandoIzq in PAREJAS:
    base, oficial = cargar(origen), cargar(destino)
    if esquinasDibujadas(base, mirandoIzq) != esquinasDibujadas(oficial, mirandoIzq):
        descolocados.append(destino)
    if oficial.get_width() != base.get_width() or oficial.get_height() < base.get_height():
        crecidos.append(destino)
    sobreElCuerpo, fueraDelCuerpo, colores = diferencias(base, oficial)
    if not sobreElCuerpo or not fueraDelCuerpo:
        sinCapa.append(destino)
    intrusos = colores - set(COLORES_DE_LA_CAPA)
    if intrusos:
        coloresRaros[destino] = sorted(intrusos)
    #fuera de la silueta solo asoma el penacho, que es de una columna
    columnas = set(x for x, _ in fueraDelCuerpo)
    if len(columnas) > 1:
        penachoAncho.append((destino, sorted(columnas)))

comprobar("el oficial se dibuja en el mismo sitio que la tropa", not descolocados,
          "descolocados: %s" % descolocados)
comprobar("el lienzo solo crece por arriba, para el penacho", not crecidos, "raros: %s" % crecidos)
comprobar("los 14 llevan penacho fuera de la silueta y banda encima del chaco",
          not sinCapa, "sin capa: %s" % sinCapa)
comprobar("no aparece ningun color que no sea el dorado y el blanco de la capa",
          not coloresRaros, "%s" % coloresRaros)
comprobar("no queda dorado flotando en el aire donde el chaco se estrecha",
          not penachoAncho, "%s" % penachoAncho)

# la banda va hacia la nuca, asi que en cada lado esta a un lado distinto del pompon
ladoDeLaBanda = {}
for origen, destino, mirandoIzq in PAREJAS:
    oficial = cargar(destino)
    ancho, alto = oficial.get_size()
    dorados = [(x, y) for y in range(alto) for x in range(ancho)
               if oficial.get_at((x, y))[:3] == ORO and oficial.get_at((x, y))[3] > OPACO]
    penacho = min(dorados, key=lambda punto: (punto[1], punto[0]))
    banda = [punto for punto in dorados if punto[1] > penacho[1] + 3]
    if banda:
        centroDeLaBanda = sum(x for x, _ in banda) / float(len(banda))
        ladoDeLaBanda[destino] = centroDeLaBanda - penacho[0]
comprobar("la banda del chaco se dibuja a los dos lados segun a donde mire",
          all(desvio > 0 for nombre, desvio in ladoDeLaBanda.items() if '_izq' in nombre)
          and all(desvio < 0 for nombre, desvio in ladoDeLaBanda.items() if '_dch' in nombre),
          "%s" % {nombre: round(desvio, 1) for nombre, desvio in ladoDeLaBanda.items()})

# ---- 2. la clase ----
comprobar("el oficial es tropa de cuerpo a cuerpo, no un enemigo aparte",
          issubclass(E.oficial, E.enemigo) and E.oficial.PELEA_CON_SABLE)
comprobar("aguanta mas que la tropa y menos que un granadero",
          E.enemigo.VIDA_INICIAL < E.oficial.VIDA_INICIAL < E.granadero.VIDA_INICIAL,
          "%d < %d < %d" % (E.enemigo.VIDA_INICIAL, E.oficial.VIDA_INICIAL,
                            E.granadero.VIDA_INICIAL))
comprobar("y vale mas que nadie, porque hace peligrosos a todos los demas",
          E.oficial.PUNTOS > max(E.enemigo.PUNTOS, E.enemigoDistancia.PUNTOS,
                                 E.voltigeur.PUNTOS, E.granadero.PUNTOS),
          "oficial %d, el siguiente %d" % (E.oficial.PUNTOS, E.granadero.PUNTOS))

mando = E.oficial(250, 250, 0, 0)
mando.actualizarRect()
balas, granadas = [], []
mando.disparar(balas)
mando.lanzar(granadas, (0, 0))
comprobar("no dispara ni lanza nada", balas == [] and granadas == [])
comprobar("usa sus propios sprites y no los de la tropa",
          mando.ANDAR_IZQ is E.Andar_izq_Of and mando.ALZAR_IZQ is E.Alzar_izq_Of
          and mando.ANDAR_IZQ is not E.Andar_izq_Fr_cuerpo)

sueltas = [objetos.sueltaDe(E.oficial(100, 100, 0, 0), 1000) for _ in range(40)]
comprobar("suelta objeto siempre, sin depender de la suerte",
          all(suelta is not None for suelta in sueltas),
          "%d de %d" % (sum(1 for s in sueltas if s), len(sueltas)))

# ---- 3. el aura de mando ----
def colocar(clase, x, y):
    frances = clase(x, y, 0, 0)
    frances.actualizarRect()
    return frances


mando = colocar(E.oficial, 250, 250)
acelerados = {}
for clase in (E.enemigo, E.enemigoDistancia, E.voltigeur, E.granadero):
    cerca = colocar(clase, 260, 250)
    E.aplicarMando([mando, cerca])
    acelerados[clase.__name__] = (cerca.VELOCIDAD, cerca.vel)
comprobar("el aura acelera a los cuatro tipos, cada uno desde su propia velocidad",
          all(rapida == base * E.FACTOR_DE_MANDO for base, rapida in acelerados.values()),
          "%s" % acelerados)

lejos = colocar(E.enemigo, 250 + E.RADIO_DE_MANDO + 40, 250)
E.aplicarMando([mando, lejos])
comprobar("y no llega a los que estan fuera del radio", lejos.vel == lejos.VELOCIDAD,
          "vel %.1f a %d px" % (lejos.vel, abs(lejos.rect.centerx - mando.rect.centerx)))

cerca = colocar(E.enemigo, 260, 250)
E.aplicarMando([mando, cerca])
E.aplicarMando([mando, mando, cerca])
comprobar("el aura no se acumula: dos oficiales aceleran lo mismo que uno",
          cerca.vel == cerca.VELOCIDAD * E.FACTOR_DE_MANDO, "vel %.1f" % cerca.vel)

otroMando = colocar(E.oficial, 260, 250)
E.aplicarMando([mando, otroMando])
comprobar("un oficial no se acelera a si mismo ni a otro oficial",
          mando.vel == mando.VELOCIDAD and otroMando.vel == otroMando.VELOCIDAD,
          "%.1f y %.1f" % (mando.vel, otroMando.vel))

E.aplicarMando([mando, cerca])
mando.vida = 0
mando.checkEstadoVida()
E.aplicarMando([mando, cerca])
comprobar("al caer el oficial, los suyos vuelven solos a su velocidad",
          cerca.vel == cerca.VELOCIDAD, "vel %.1f" % cerca.vel)

# y se nota de verdad al moverlos, no solo en el numero
def cuantoAvanza(conMando):
    mando = colocar(E.oficial, 300, 300)
    frances = colocar(E.enemigo, 300, 300) if conMando else colocar(E.enemigo, 0, 0)
    frances.x, frances.y = 300, 300
    frances.actualizarRect()
    campo = [mando, frances] if conMando else [frances]
    partida = frances.x
    for _ in range(20):
        E.aplicarMando(campo)
        frances.pathFinding(500, 300)
    return frances.x - partida


conAura, sinAura = cuantoAvanza(True), cuantoAvanza(False)
comprobar("con un oficial al lado, la tropa recorre un 50% mas en los mismos frames",
          abs(conAura - sinAura * E.FACTOR_DE_MANDO) < 1.0,
          "%.0f px con oficial contra %.0f px sin el" % (conAura, sinAura))

# ---- 4. los cadaveres dejan de estar cruzados ----
comprobar("el cadaver con dorados es del oficial",
          E.oficial(0, 0, 0, 0).__class__.dibujarCadaver.__code__.co_names.count('cadaverOficialImg')
          == 1)
lienzo = pygame.Surface((200, 200), pygame.SRCALPHA)
tropa = colocar(E.enemigo, 60, 60)
tropa.dibujarCadaver(lienzo)
dorados = sum(1 for y in range(200) for x in range(200)
              if lienzo.get_at((x, y))[:3] == ORO and lienzo.get_at((x, y))[3] > OPACO)
lienzoOficial = pygame.Surface((200, 200), pygame.SRCALPHA)
colocar(E.oficial, 60, 60).dibujarCadaver(lienzoOficial)
doradosOficial = sum(1 for y in range(200) for x in range(200)
                     if lienzoOficial.get_at((x, y))[:3] == ORO
                     and lienzoOficial.get_at((x, y))[3] > OPACO)
comprobar("y la tropa de bayoneta ya no muere con el cadaver del oficial",
          doradosOficial > dorados, "oficial %d dorados, tropa %d" % (doradosOficial, dorados))

# ---- 5. en las oleadas ----
comprobar("no hay oficiales antes de su oleada",
          all(oleadas.composicion(numero)[oleadas.OFICIAL] == 0
              for numero in range(1, oleadas.PRIMERA_OLEADA_CON_OFICIALES)))
comprobar("y aparece uno en cuanto toca",
          oleadas.composicion(oleadas.PRIMERA_OLEADA_CON_OFICIALES)[oleadas.OFICIAL] == 1,
          str(oleadas.composicion(oleadas.PRIMERA_OLEADA_CON_OFICIALES)))
cuantos = [oleadas.composicion(numero)[oleadas.OFICIAL] for numero in range(1, 81)]
comprobar("nunca pasan del tope, porque el aura no se acumula",
          max(cuantos) <= oleadas.TOPE_OFICIALES, "maximo %d, tope %d"
          % (max(cuantos), oleadas.TOPE_OFICIALES))
comprobar("y ninguna oleada alta se queda sin oficiales",
          all(oleadas.composicion(numero)[oleadas.OFICIAL] >= 1 for numero in range(5, 41)),
          str([oleadas.composicion(n)[oleadas.OFICIAL] for n in range(5, 41)]))

# ---- 6. entra en batalla de verdad ----
juego = entorno.cargarJuego()
juego['reiniciarPartida']()
juego['entrarEnBatalla'](oleadas.OFICIAL)
comprobar("la partida sabe meter un oficial en el campo",
          len(juego['enemies']) == 1 and isinstance(juego['enemies'][0], E.oficial),
          str([type(uno).__name__ for uno in juego['enemies']]))

# ---- 7. el anillo que ensenia hasta donde llega el mando ----
def pintados(quien, ancho=500, alto=500):
    lienzo = pygame.Surface((ancho, alto))
    lienzo.fill((0, 0, 0))
    quien.dibujarMando(lienzo)
    return [(x, y) for y in range(alto) for x in range(ancho)
            if lienzo.get_at((x, y))[:3] != (0, 0, 0)]


mando = colocar(E.oficial, 250, 250)
anillo = pintados(mando)
comprobar("el oficial pinta su anillo en el suelo", len(anillo) > 0, "%d pixeles" % len(anillo))

tambienLoPintan = [clase.__name__ for clase in
                   (E.enemigo, E.enemigoDistancia, E.voltigeur, E.granadero)
                   if pintados(colocar(clase, 250, 250))]
comprobar("y no lo pinta nadie mas", not tambienLoPintan, "tambien: %s" % tambienLoPintan)

centro = mando.rect.center
radios = [((x - centro[0]) ** 2 + (y - centro[1]) ** 2) ** 0.5 for x, y in anillo]
comprobar("todos sus pixeles caen sobre el radio del aura, que es lo que tiene que enseniar",
          all(abs(radio - E.RADIO_DE_MANDO) <= 1.0 for radio in radios),
          "radios entre %.1f y %.1f, aura %d" % (min(radios), max(radios), E.RADIO_DE_MANDO))

circunferencia = 2 * 3.14159 * E.RADIO_DE_MANDO
comprobar("va a trozos y no lleno: es informacion, no una amenaza que esquivar",
          0.25 * circunferencia < len(anillo) < 0.75 * circunferencia,
          "%d pixeles de %d de circunferencia" % (len(anillo), circunferencia))
comprobar("y los trozos son rayas, no motas: hay un paso por pixel de circunferencia",
          E.PASOS_DEL_ANILLO >= circunferencia - 1,
          "%d pasos para %d px" % (E.PASOS_DEL_ANILLO, circunferencia))

lienzo = pygame.Surface((500, 500))
lienzo.fill((0, 0, 0))
mando.dibujarMando(lienzo)
colores = set(lienzo.get_at(punto)[:3] for punto in anillo)
comprobar("con el dorado del oficial, no con el rojo de la granada",
          colores == {E.COLOR_DE_MANDO}, "%s" % sorted(colores))

seSale = None
for esquina in ((0, 0), (E.WINX - 30, 0), (0, E.WINY - 32), (E.WINX - 30, E.WINY - 32)):
    trozo = pintados(colocar(E.oficial, esquina[0], esquina[1]))
    if not all(0 <= x < E.WINX and 0 <= y < E.WINY for x, y in trozo) or not trozo:
        seSale = esquina
        break
comprobar("pegado a las cuatro esquinas se recorta sin salirse ni quedarse en nada",
          seSale is None, "falla en %s" % (seSale,))

# ---- 8. y la partida lo pinta de verdad ----
juego['reiniciarPartida']()
juego['enCalma'] = False
juego['player'].x, juego['player'].y = 460, 460
elOficial = E.oficial(200, 200, juego['player'].x, juego['player'].y)
elOficial.actualizarRect()
juego['enemies'].append(elOficial)
juego['drawWindow']()
puntosDelAnillo = pintados(elOficial)
enPantalla = sum(1 for punto in puntosDelAnillo
                 if juego['win'].get_at(punto)[:3] == E.COLOR_DE_MANDO)
comprobar("en la partida el anillo llega a la pantalla",
          enPantalla > 0.5 * len(puntosDelAnillo),
          "%d de %d puntos del anillo se ven" % (enPantalla, len(puntosDelAnillo)))

# ---- 9. el halo de los soldados bajo su mando ----
import render

mando = colocar(E.oficial, 250, 250)
cerca = colocar(E.enemigo, 265, 250)
lejos = colocar(E.enemigo, 250 + E.RADIO_DE_MANDO + 40, 250)
E.aplicarMando([mando, cerca, lejos])
comprobar("el que esta bajo mando lo sabe, y el de fuera no",
          cerca.conMando and not lejos.conMando,
          "cerca=%s lejos=%s" % (cerca.conMando, lejos.conMando))
comprobar("y el oficial no se pone halo a si mismo", not mando.conMando)

mando.vida = 0
mando.checkEstadoVida()
E.aplicarMando([mando, cerca])
comprobar("al caer el oficial se les quita el halo, sin tener que avisarles",
          not cerca.conMando)


def dibujado(frances):
    lienzo = pygame.Surface((500, 500), pygame.SRCALPHA)
    frances.dibujarEnemigo(lienzo)
    return lienzo


def cuentaDelDorado(lienzo):
    return sum(1 for y in range(180, 320) for x in range(180, 340)
               if lienzo.get_at((x, y))[:3] == E.COLOR_DE_MANDO)


conHalo = colocar(E.enemigo, 250, 250)
conHalo.conMando = True
sinHalo = colocar(E.enemigo, 250, 250)
sinHalo.conMando = False
dorandoConHalo = cuentaDelDorado(dibujado(conHalo))
dorandoSinHalo = cuentaDelDorado(dibujado(sinHalo))
comprobar("el soldado bajo mando se dibuja con halo dorado alrededor",
          dorandoConHalo > 20, "%d pixeles de halo" % dorandoConHalo)
comprobar("y el que no lo esta se dibuja como siempre",
          dorandoSinHalo == 0, "%d pixeles de halo" % dorandoSinHalo)

#el halo va DEBAJO: donde el sprite es opaco, el pixel tiene que ser el del sprite
lienzoConHalo, lienzoSinHalo = dibujado(conHalo), dibujado(sinHalo)
tapados = 0
distintos = []
sprite = conHalo.sprite()
dx, dy = render.desplazamiento(sprite, conHalo.ANCHO_REFERENCIA, conHalo.ALTO_REFERENCIA, True)
for y in range(sprite.get_height()):
    for x in range(sprite.get_width()):
        if sprite.get_at((x, y))[3] < 255:
            continue
        punto = (int(conHalo.x + dx + x), int(conHalo.y + dy + y))
        tapados += 1
        if lienzoConHalo.get_at(punto) != lienzoSinHalo.get_at(punto):
            distintos.append(punto)
comprobar("el halo no toca ni un pixel del soldado: va por debajo",
          not distintos, "%d de %d pixeles del sprite cambiados" % (len(distintos), tapados))

#el anillo del suelo y el halo tienen que salir del mismo color EN PANTALLA, no solo en el
#codigo: es lo que hace que el jugador ate una cosa con la otra de un vistazo
lienzoDelAnillo = pygame.Surface((500, 500))
lienzoDelAnillo.fill((0, 0, 0))
colocar(E.oficial, 250, 250).dibujarMando(lienzoDelAnillo)
coloresDelAnillo = set(lienzoDelAnillo.get_at((x, y))[:3]
                       for y in range(500) for x in range(500)
                       if lienzoDelAnillo.get_at((x, y))[:3] != (0, 0, 0))
lienzoDelHalo = dibujado(conHalo)
coloresDelHalo = set(lienzoDelHalo.get_at((x, y))[:3]
                     for y in range(180, 320) for x in range(180, 340)
                     if lienzoDelHalo.get_at((x, y))[:3] == E.COLOR_DE_MANDO)
comprobar("el halo y el anillo del suelo salen del mismo dorado en pantalla",
          coloresDelAnillo == coloresDelHalo and len(coloresDelAnillo) == 1,
          "anillo %s, halo %s" % (sorted(coloresDelAnillo), sorted(coloresDelHalo)))
comprobar("la silueta del halo se calcula una vez y se guarda, no en cada frame",
          render.aura(sprite, E.COLOR_DE_MANDO, E.ALFA_DEL_HALO)
          is render.aura(sprite, E.COLOR_DE_MANDO, E.ALFA_DEL_HALO))

# y con los cuatro tipos, porque los cuatro pueden estar bajo mando
sinHaloNinguno = []
for clase in (E.enemigo, E.enemigoDistancia, E.voltigeur, E.granadero):
    frances = colocar(clase, 250, 250)
    frances.conMando = True
    if cuentaDelDorado(dibujado(frances)) < 10:
        sinHaloNinguno.append(clase.__name__)
comprobar("los cuatro tipos se dibujan con halo cuando estan bajo mando",
          not sinHaloNinguno, "sin halo: %s" % sinHaloNinguno)

raise SystemExit(resumen())
