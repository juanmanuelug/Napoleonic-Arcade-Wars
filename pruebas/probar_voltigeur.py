"""Pruebas del voltigeur: sus sprites y su clase.

Los 18 sprites no se dibujan a mano, los saca herramientas/voltigeur.py pintando una capa
encima de los 18 del soldado de linea. La primera mitad de la bateria comprueba justo eso: que
lo unico que cambia es el penacho y la banda del chaco, y que el voltigeur se planta donde se
plantaria el soldado de linea. La segunda mitad prueba la clase, que es ese mismo tirador con
otros cuatro numeros.
"""
import os

import entorno
from entorno import comprobar, resumen
import pygame

pygame.init()
pygame.display.set_mode((500, 500))

import render

CARPETA = os.path.join(os.path.dirname(entorno.AQUI), 'sprites', 'franceses')

# La caja del cuerpo del tirador, que es la que usa el voltigeur
ANCHO_REFERENCIA = 20
ALTO_REFERENCIA = 36

AMARILLO = (234, 198, 62)
AMARILLO_SOMBRA = (176, 142, 30)
ROJO = (130, 0, 0)
ROJO_BRILLO = (176, 32, 34)
COLORES_DE_LA_CAPA = (AMARILLO, AMARILLO_SOMBRA, ROJO, ROJO_BRILLO)

OPACO = 20
ANCHO_DEL_PENACHO = 2


def parejas():
    """(nombre del sprite de linea, nombre del voltigeur, mira a la izquierda)."""
    lista = []
    for lado in ('izq', 'dch'):
        for numero in range(7):
            lista.append(('soldado_fr_%s_%d.png' % (lado, numero),
                          'voltigeur_fr_%s_%d.png' % (lado, numero), lado == 'izq'))
    for lado in ('izq', 'dch'):
        for cola in ('disparar_1', 'disparar'):
            lista.append(('soldado_fr_%s_%s.png' % (lado, cola),
                          'voltigeur_fr_%s_%s.png' % (lado, cola), lado == 'izq'))
    return lista


PAREJAS = parejas()


def cargar(nombre):
    return pygame.image.load(os.path.join(CARPETA, nombre)).convert_alpha()


def esquinasDibujadas(imagen, mirandoIzq):
    """Donde acaba el cuerpo ya dibujado: (izquierda, derecha, pies).

    No vale comparar el desplazamiento crudo: el sprite de apuntar del voltigeur lleva ocho
    filas mas por arriba para el penacho, y el anclaje por los pies las compensa a proposito.
    """
    dx, dy = render.desplazamiento(imagen, ANCHO_REFERENCIA, ALTO_REFERENCIA, mirandoIzq)
    contenido = imagen.get_bounding_rect()
    return (dx + contenido.left, dx + contenido.right, dy + contenido.bottom)


def filaAltaDelChaco(imagen):
    """(columnas opacas, fila) de la primera fila con cuerpo, que es el alto del chaco.

    Se piden 5 pixeles porque en los sprites de andar el mosquete va en vertical POR ENCIMA
    de la cabeza y mide tres de ancho.
    """
    ancho, alto = imagen.get_size()
    for y in range(alto):
        opacos = [x for x in range(ancho) if imagen.get_at((x, y))[3] > OPACO]
        if len(opacos) >= 5:
            return opacos, y
    return [], None


def diferencias(base, voltigeur):
    """Los pixeles que cambian, separados en los que repintan cuerpo y los que anaden dibujo."""
    filasAnadidas = voltigeur.get_height() - base.get_height()
    sobreElCuerpo, fueraDelCuerpo, colores = [], [], set()
    for y in range(base.get_height()):
        for x in range(base.get_width()):
            antes = base.get_at((x, y))
            luego = voltigeur.get_at((x, y + filasAnadidas))
            if antes == luego:
                continue
            colores.add((luego[0], luego[1], luego[2]))
            (fueraDelCuerpo if antes[3] <= OPACO else sobreElCuerpo).append((x, y))
    for y in range(filasAnadidas):
        for x in range(voltigeur.get_width()):
            pixel = voltigeur.get_at((x, y))
            if pixel[3] > OPACO:
                colores.add((pixel[0], pixel[1], pixel[2]))
                fueraDelCuerpo.append((x, y - filasAnadidas))
    return sobreElCuerpo, fueraDelCuerpo, colores


# ---- 1. estan los 18 ----
faltan = [nombre for _, nombre, _ in PAREJAS if not os.path.exists(os.path.join(CARPETA, nombre))]
comprobar("estan los 18 sprites del voltigeur", not faltan, "faltan %s" % faltan)

if faltan:
    raise SystemExit(resumen())

# ---- 2. se plantan donde el soldado de linea ----
descolocados = []
crecenSoloPorArriba = []
for origen, destino, mirandoIzq in PAREJAS:
    base, voltigeur = cargar(origen), cargar(destino)
    if esquinasDibujadas(base, mirandoIzq) != esquinasDibujadas(voltigeur, mirandoIzq):
        descolocados.append(destino)
    if (voltigeur.get_width() != base.get_width()
            or voltigeur.get_height() < base.get_height()):
        crecenSoloPorArriba.append(destino)

comprobar("el voltigeur se dibuja en el mismo sitio que el soldado de linea",
          not descolocados, "descolocados: %s" % descolocados)
comprobar("el lienzo solo crece por arriba, para el penacho",
          not crecenSoloPorArriba, "raros: %s" % crecenSoloPorArriba)

# ---- 3. la capa no se come nada del dibujo original ----
sinCapa = []
coloresRaros = {}
bandaEnElAire = []
for origen, destino, mirandoIzq in PAREJAS:
    base, voltigeur = cargar(origen), cargar(destino)
    sobreElCuerpo, fueraDelCuerpo, colores = diferencias(base, voltigeur)
    if not sobreElCuerpo or not fueraDelCuerpo:
        sinCapa.append(destino)
    intrusos = colores - set(COLORES_DE_LA_CAPA)
    if intrusos:
        coloresRaros[destino] = sorted(intrusos)
    #lo unico que asoma fuera de la silueta es el penacho, que mide dos columnas
    columnas = set(x for x, _ in fueraDelCuerpo)
    if len(columnas) > ANCHO_DEL_PENACHO:
        bandaEnElAire.append((destino, sorted(columnas)))

comprobar("los 18 llevan penacho fuera de la silueta y banda encima del chaco",
          not sinCapa, "sin capa: %s" % sinCapa)
comprobar("no aparece ningun color que no sea el amarillo y el rojo de la capa",
          not coloresRaros, "%s" % coloresRaros)
comprobar("no queda ningun pixel de la banda flotando en el aire",
          not bandaEnElAire, "%s" % bandaEnElAire)

# ---- 4. el penacho va al frente, en los dos lados ----
alReves = []
for origen, destino, mirandoIzq in PAREJAS:
    base, voltigeur = cargar(origen), cargar(destino)
    columnasDelChaco, _ = filaAltaDelChaco(base)
    _, fueraDelCuerpo, _ = diferencias(base, voltigeur)
    columnasDelPenacho = sorted(set(x for x, _ in fueraDelCuerpo))
    if mirandoIzq:
        esperadas = columnasDelChaco[:ANCHO_DEL_PENACHO]
    else:
        esperadas = columnasDelChaco[-ANCHO_DEL_PENACHO:]
    if columnasDelPenacho != sorted(esperadas):
        alReves.append((destino, columnasDelPenacho, sorted(esperadas)))

comprobar("el penacho sale por el frente del chaco, mire al lado que mire",
          not alReves, "%s" % alReves)

# ---- 5. al tirador le bastan andar y disparar: no hace falta cuerpo a cuerpo ----
import enemigo as E

comprobar("el tirador solo gasta andar y disparar, asi que 18 sprites bastan",
          len(E.Andar_izq_Fr) == 9 and len(E.Disparar_izq_Fr) == 2,
          "andar=%d disparar=%d" % (len(E.Andar_izq_Fr), len(E.Disparar_izq_Fr)))

# ---- 6. la clase: el mismo tirador con otros numeros ----
comprobar("el voltigeur es un tirador, no un enemigo aparte",
          issubclass(E.voltigeur, E.enemigoDistancia))
comprobar("va al doble de velocidad que el de linea",
          E.voltigeur.VELOCIDAD == 2 * E.enemigoDistancia.VELOCIDAD,
          "%d contra %d" % (E.voltigeur.VELOCIDAD, E.enemigoDistancia.VELOCIDAD))
comprobar("y recarga antes", E.voltigeur.RECARGA < E.enemigoDistancia.RECARGA,
          "%d ms contra %d ms" % (E.voltigeur.RECARGA, E.enemigoDistancia.RECARGA))
comprobar("dispara desde mas atras que toda la linea de tiro del soldado de linea",
          min(E.voltigeur.PUESTOS) > max(E.enemigoDistancia.PUESTOS),
          "%s contra %s" % (str(E.voltigeur.PUESTOS), str(E.enemigoDistancia.PUESTOS)))
comprobar("pero aguanta lo mismo: su amenaza es la posicion, no el plomo que traga",
          E.voltigeur.VIDA_INICIAL == E.enemigo.VIDA_INICIAL,
          "%d contra %d" % (E.voltigeur.VIDA_INICIAL, E.enemigo.VIDA_INICIAL))
comprobar("vale mas que el de linea y menos que el granadero",
          E.enemigoDistancia.PUNTOS < E.voltigeur.PUNTOS < E.granadero.PUNTOS,
          "%d < %d < %d" % (E.enemigoDistancia.PUNTOS, E.voltigeur.PUNTOS, E.granadero.PUNTOS))

ligero = E.voltigeur(480, 400, 100, 250)
comprobar("nace con la velocidad y la recarga de su clase",
          ligero.vel == E.VEL_VOLTIGEUR and ligero.recarga == E.RECARGA_VOLTIGEUR,
          "vel=%d recarga=%d" % (ligero.vel, ligero.recarga))
comprobar("y con un puesto de su propia linea de tiro",
          ligero.distanciaDeTiro in E.PUESTOS_DE_VOLTIGEUR, str(ligero.distanciaDeTiro))

# ---- 7. usa sus sprites, no los del soldado de linea ----
suyos = set(id(imagen) for lista in (E.Andar_izq_Vo, E.Andar_dch_Vo,
                                     E.Disparar_izq_Vo, E.Disparar_dch_Vo)
            for imagen in lista)
ajenos = []
for mirandoIzq in (True, False):
    ligero.izq, ligero.dch = mirandoIzq, not mirandoIzq
    for andando in (True, False):
        ligero.stop = not andando
        ligero.haDisparado = True
        if id(ligero.sprite()) not in suyos:
            ajenos.append((mirandoIzq, andando))
comprobar("saca sprites de voltigeur andando y disparando, mire al lado que mire",
          not ajenos, "casos con sprite ajeno: %s" % ajenos)

# ---- 8. los puestos van por tipo: las dos lineas de tiro no se pisan ----
enElCampo = [E.enemigoDistancia(480, 250, 100, 250) for _ in range(len(E.PUESTOS_DE_TIRO))]
recienLlegado = E.voltigeur(480, 250, 100, 250, enElCampo)
comprobar("con la linea del soldado de linea llena, el voltigeur coge puesto igual",
          recienLlegado.distanciaDeTiro in E.PUESTOS_DE_VOLTIGEUR,
          str(recienLlegado.distanciaDeTiro))
conVoltigeurs = [E.voltigeur(480, 250, 100, 250) for _ in range(len(E.PUESTOS_DE_VOLTIGEUR))]
deLinea = E.enemigoDistancia(480, 250, 100, 250, conVoltigeurs)
comprobar("y un soldado de linea no se va atras porque haya voltigeurs en el campo",
          deLinea.distanciaDeTiro in E.PUESTOS_DE_TIRO, str(deLinea.distanciaDeTiro))


def plantar(clase, xJugador, yJugador=250, frames=900):
    """Deja que uno entre por el borde derecho y se coloque, y devuelve como acaba."""
    frances = clase(E.WINX + 40, 400, xJugador, yJugador)
    for _ in range(frames):
        frances.pathFinding(xJugador, yJugador)
    return frances


# ---- 9. con sitio de sobra se planta en su puesto, mucho mas atras ----
JUGADOR_A_UN_LADO = 100
ligero = plantar(E.voltigeur, JUGADOR_A_UN_LADO)
deLinea = plantar(E.enemigoDistancia, JUGADOR_A_UN_LADO)
distanciaLigero = abs(ligero.x - JUGADOR_A_UN_LADO)
distanciaDeLinea = abs(deLinea.x - JUGADOR_A_UN_LADO)
comprobar("el voltigeur se para en su puesto",
          abs(distanciaLigero - ligero.distanciaDeTiro) <= E.MARGEN_PUESTO + ligero.vel,
          "%.0f px, puesto %d" % (distanciaLigero, ligero.distanciaDeTiro))
comprobar("y se queda mas lejos del jugador que el soldado de linea",
          distanciaLigero > distanciaDeLinea,
          "%.0f px contra %.0f px" % (distanciaLigero, distanciaDeLinea))
comprobar("los dos acaban quietos y encarados, listos para disparar",
          ligero.stop and deLinea.stop and ligero.encarado() and deLinea.encarado())

# ---- 10. con el jugador en el centro no caben 260 px, y aun asi no se sale de la pantalla ----
# esto es lo que evita el tirador-trampa: uno al que no puedes ver ni alcanzar y que te dispara.
# El freno de la retirada le deja pegado al borde, no fuera
CENTRO = E.WINX // 2
acorralado = plantar(E.voltigeur, CENTRO)
comprobar("con el jugador en el centro no le cabe su puesto entero",
          abs(acorralado.x - CENTRO) < acorralado.distanciaDeTiro - E.MARGEN_PUESTO,
          "%.0f px de %d" % (abs(acorralado.x - CENTRO), acorralado.distanciaDeTiro))
comprobar("pero se queda dentro de la pantalla, entero y alcanzable",
          0 <= acorralado.x <= E.WINX - E.voltigeur.ANCHO_REFERENCIA
          and acorralado.rect.left >= 0 and acorralado.rect.right <= E.WINX,
          "x=%.0f rect=%s" % (acorralado.x, acorralado.rect))
comprobar("y se planta en vez de temblar contra el borde", acorralado.stop)

# ---- 11. dispara mas seguido que el de linea ----
reloj = {'ms': 60000}
pygame.time.get_ticks = lambda: reloj['ms']
ligero = E.voltigeur(200, 250, 100, 250)
deLinea = E.enemigoDistancia(200, 250, 100, 250)
for tirador in (ligero, deLinea):
    tirador.instanteUltimoDisparo = reloj['ms'] - E.RECARGA_VOLTIGEUR
comprobar("cumplida la recarga del voltigeur, el voltigeur ya puede disparar",
          ligero.puedeDisparar(reloj['ms']))
comprobar("y el de linea todavia no", not deLinea.puedeDisparar(reloj['ms']))
balas = []
ligero.y = 250
ligero.actualizarRect()
ligero.disparar(balas)
comprobar("y al disparar suelta una bala", len(balas) == 1, "%d balas" % len(balas))

# ---- 12. en las oleadas sale de la cuota de tiradores, no ademas de ella ----
import oleadas

comprobar("no hay voltigeurs antes de su oleada",
          all(oleadas.composicion(numero)[oleadas.VOLTIGEUR] == 0
              for numero in range(1, oleadas.PRIMERA_OLEADA_CON_VOLTIGEURS)))
comprobar("y aparece en cuanto toca",
          oleadas.composicion(oleadas.PRIMERA_OLEADA_CON_VOLTIGEURS)[oleadas.VOLTIGEUR] == 1,
          str(oleadas.composicion(oleadas.PRIMERA_OLEADA_CON_VOLTIGEURS)))
#hasta la 12 el cupo no toca el tope, asi que el reparto se ve limpio
SIN_TOPE = range(1, 13)
comprobar("el voltigeur sale de la cuota de tiradores: entre los dos son los de siempre",
          all(oleadas.composicion(numero)[oleadas.TIRADOR]
              + oleadas.composicion(numero)[oleadas.VOLTIGEUR]
              == numero // oleadas.TIRADORES_CADA for numero in SIN_TOPE),
          str([(oleadas.composicion(n)[oleadas.TIRADOR],
                oleadas.composicion(n)[oleadas.VOLTIGEUR]) for n in SIN_TOPE]))
comprobar("y el reparto no deja ninguna oleada sin tiradores de linea",
          all(oleadas.composicion(numero)[oleadas.TIRADOR] >= 1 for numero in range(2, 81)),
          str([oleadas.composicion(n)[oleadas.TIRADOR] for n in range(2, 81)]))

raise SystemExit(resumen())
