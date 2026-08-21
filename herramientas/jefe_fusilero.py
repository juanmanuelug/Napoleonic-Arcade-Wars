"""El jefe fusilero: el soldado de linea al doble de tamanio y con galon.

    python herramientas/jefe_fusilero.py

Tercero de los cuatro jefes, y el primero que sale del soldado de LINEA y no de una tropa
especial. Salen sus 18 sprites (7 de andar por lado y 2 de disparar por lado) de los 18 del
fusilero de siempre.

Igual que con el jefe granadero y el de sable: x2 y no x1,6, porque escalar arte de pixel por un
numero no entero reparte mal los pixeles. A x2 cada pixel del fusilero es un cuadrado limpio de
2x2, y encima queda sitio para detalle de un pixel, que es el contraste que hace que se lea como
un jefe y no como el mismo soldado visto de cerca.

EL ANCLA. Aqui no sirve el pompon de laton que usa el jefe de sable: el soldado de linea no lo
lleva. Se ancla en la ESQUINA ALTA IZQUIERDA DEL CHACO, igual que herramientas/voltigeur.py, que
opera sobre estos mismos 18 sprites. En los de andar hay que buscarla y no dar por hecho que es la
fila 0, porque el mosquete va en vertical POR ENCIMA de la cabeza: la esquina se busca como la
primera fila con suficiente cuerpo (menos que eso es el canio del mosquete, de tres pixeles).

DONDE SE PUEDE PINTAR. Medido en los 18: relativo a la esquina del chaco y en pixeles del
original, el chaco ocupa las filas 0 a 4 y el cuerpo de la casaca empieza en la fila 11 y llega a
la 18. Eso se cumple en los siete de andar y en los dos de disparar, que es lo raro y lo que hace
que una sola capa valga para todos. Lo que NO se cumple son los brazos: en los de disparar el
mosquete estirado se va 37 pixeles a un lado. Asi que el galon se queda en el chaco y en lo alto
de la casaca, y ni se acerca a los brazos.

Y todas las piezas pintan SOLO SOBRE CUERPO. Un jefe no necesita que le sobresalga nada nuevo, y
asi el lienzo mide exactamente el doble, sin crecer por ningun lado: los cuatro jefes cumplen la
misma regla y el anclaje de render.py no se entera de nada.

Los sprites de mirar a la derecha se voltean, se les pinta el galon y se vuelven a voltear, y asi
la charretera y la placa salen al frente en los dos lados sin escribir la capa dos veces.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), 'pruebas'))
import entorno
import pygame

CARPETA = 'sprites/franceses'
LADOS = ('izq', 'dch')
FOTOGRAMAS = range(7)
COLAS_DE_DISPARO = ('disparar_1', 'disparar')

DOBLE = 2

# El mismo dorado que llevan el oficial y los otros dos jefes: que los cuatro jefes se lean como
# de la misma casa importa mas que darle a este un color propio
ORO = (214, 172, 60)
ORO_CLARO = (240, 206, 116)
ORO_SOMBRA = (176, 132, 30)
# El penacho: blanco de oficial sobre el rojo que ya trae el sprite
BLANCO = (237, 242, 255)
BLANCO_SOMBRA = (192, 189, 192)
ROJO = (130, 0, 0)
ROJO_BRILLO = (176, 32, 34)

PALETA = {'.': None, 'O': ORO, 'C': ORO_CLARO, 'S': ORO_SOMBRA,
          'W': BLANCO, 'w': BLANCO_SOMBRA, 'R': ROJO, 'r': ROJO_BRILLO}

# DONDE VA CADA COSA. Medido en los 18 y relativo a la esquina del chaco, en pixeles del
# original: el chaco ocupa las filas 0 a 6, la cara la 8 a la 11 y la casaca empieza en la 12.
# Las tres cosas caen en el mismo sitio en los siete de andar Y en los dos de disparar.
#
# El hombro se queda sin charretera a proposito, aunque es donde la lleva el jefe de sable: en
# los sprites de disparar, a la altura del hombro y por delante esta el BRAZO ESTIRADO con el
# mosquete, no el hombro. La charretera saldria en el antebrazo en cuatro de los dieciocho, o
# desapareceria al disparar. El galon se queda en la cabeza, que es lo unico identico en todos.
#
# Las coordenadas van en pixeles del DOBLE (el original x2), que es donde se pinta.
PIEZAS_DE_GALON = (
    #la banda, justo encima de la visera (filas 5 y 6 del original). Llega a la columna 9 y no
    #mas alla: pasada esa columna esta la escarapela gris del lado de atras del chaco, y una
    #banda que la tapase dejaba de leerse como una banda y parecia una bandeja en la cabeza
    ((0, 10), ["CCCCCCCCCCCCCCCCCCCC",
               "OOOOOOOOOOOOOOOOOOOO",
               "SSSSSSSSSSSSSSSSSSSS"]),
    #la placa del frente del chaco, colgada de la banda hacia arriba (filas 2 a 4)
    ((2, 4), ["CCCCCC",
              "COOOOS",
              "COOOOS",
              "COOOOS",
              "CSOOSS",
              ".SOS.."]),
)

# El penacho es la unica pieza que pinta FUERA de la silueta: para eso sobresale. Va por delante
# del chaco (columnas 0 a 3 del original) y no por el medio, porque en los sprites de andar el
# mosquete va en vertical POR ENCIMA de la cabeza, por las columnas 8 a 11.
#
# Blanco sobre rojo, que es el penacho de oficial y no se confunde con el del voltigeur, que es
# amarillo sobre rojo (ver herramientas/voltigeur.py) y mide la mitad.
PENACHO = (0, ["WW..",
               "WWW.",
               "WWW.",
               "WWW.",
               "WWW.",
               "wWW.",
               "wWW.",
               "RRR.",
               "RRR.",
               "rRR.",
               "rRR.",
               ".RR."])

# Filas con al menos esto de cuerpo (medido en el original, no en el doble): menos que eso es el
# mosquete en vertical, que en los sprites de andar asoma por encima de la cabeza
CUERPO_MINIMO_DEL_CHACO = 5
OPACO = 20


def piezas():
    """Los 18 pares (origen, destino), en el orden en que se ensenian en la hoja."""
    pares = []
    for lado in LADOS:
        for numero in FOTOGRAMAS:
            pares.append(('soldado_fr_%s_%d.png' % (lado, numero),
                          'jefefusilero_fr_%s_%d.png' % (lado, numero)))
    for lado in LADOS:
        for cola in COLAS_DE_DISPARO:
            pares.append(('soldado_fr_%s_%s.png' % (lado, cola),
                          'jefefusilero_fr_%s_%s.png' % (lado, cola)))
    return tuple(pares)


def esquinaDelChaco(imagen):
    """(columna, fila) de la esquina alta izquierda del chaco, en pixeles de la imagen dada."""
    ancho, alto = imagen.get_size()
    for y in range(alto):
        opacos = [x for x in range(ancho) if imagen.get_at((x, y))[3] > OPACO]
        if len(opacos) >= CUERPO_MINIMO_DEL_CHACO:
            return min(opacos), y
    raise ValueError("no se encuentra el chaco")


def conMargenArriba(imagen, filas):
    """El mismo sprite con filas vacias por arriba, para que quepa el penacho.

    Crece por arriba y NUNCA por los lados: el juego ancla los sprites por los pies y, los que
    miran a la izquierda, por el borde derecho del lienzo (ver render.desplazamiento). Crecer
    hacia arriba no descoloca nada; crecer a un lado movería al jefe medio cuerpo.
    """
    if filas <= 0:
        return imagen.copy()
    ancho, alto = imagen.get_size()
    crecido = pygame.Surface((ancho, alto + filas), pygame.SRCALPHA)
    crecido.blit(imagen, (0, filas))
    return crecido


def aplicar(imagen):
    """La imagen al doble, con galon y penacho. Tiene que venir mirando a la izquierda.

    La esquina del chaco se busca en el ORIGINAL y se dobla, en vez de buscarla en el doble: en
    el doble el canio del mosquete mide seis pixeles y ya pasaria de CUERPO_MINIMO_DEL_CHACO, asi
    que la esquina saldria en lo alto del mosquete y el galon acabaria en el aire.
    """
    columna, fila = esquinaDelChaco(imagen)
    columna, fila = columna * DOBLE, fila * DOBLE
    doble = pygame.transform.scale(imagen, (imagen.get_width() * DOBLE,
                                            imagen.get_height() * DOBLE))
    #el penacho arranca justo encima del chaco y sube: si no hay tanto lienzo, se anade
    desplazamientoDelPenacho, dibujoDelPenacho = PENACHO
    faltanFilas = max(0, len(dibujoDelPenacho) - fila)
    doble = conMargenArriba(doble, faltanFilas)
    fila += faltanFilas
    ancho, alto = doble.get_size()

    def pintar(dx, dy, dibujo, soloSobreCuerpo):
        for y, filaDelDibujo in enumerate(dibujo):
            for x, letra in enumerate(filaDelDibujo):
                color = PALETA[letra]
                if not color:
                    continue
                destinoX, destinoY = columna + dx + x, fila + dy + y
                if not (0 <= destinoX < ancho and 0 <= destinoY < alto):
                    continue
                if soloSobreCuerpo and doble.get_at((destinoX, destinoY))[3] <= OPACO:
                    continue
                doble.set_at((destinoX, destinoY), color + (255,))

    #el penacho pinta fuera de la silueta, que para eso sobresale; el galon solo sobre cuerpo,
    #para no dejar pixeles dorados flotando donde el chaco se estrecha
    pintar(desplazamientoDelPenacho, -len(dibujoDelPenacho), dibujoDelPenacho, False)
    for (dx, dy), dibujo in PIEZAS_DE_GALON:
        pintar(dx, dy, dibujo, True)
    return doble


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    for dx, dibujo in [(PENACHO[0], PENACHO[1])] + [(dx, dibujo)
                       for (dx, _), dibujo in PIEZAS_DE_GALON]:
        if len(set(len(fila) for fila in dibujo)) != 1:
            raise ValueError("una pieza tiene filas de distinto largo")
        for fila in dibujo:
            for letra in fila:
                if letra not in PALETA:
                    raise ValueError("la pieza en %d usa %r" % (dx, letra))

    jefes = []
    for origen, destino in piezas():
        base = pygame.image.load(os.path.join(CARPETA, origen)).convert_alpha()
        #se trabaja mirando a la izquierda: la charretera y la placa van al lado de delante
        miraADerecha = '_dch_' in origen
        trabajo = pygame.transform.flip(base, True, False) if miraADerecha else base
        jefe = aplicar(trabajo)
        if miraADerecha:
            jefe = pygame.transform.flip(jefe, True, False)
        pygame.image.save(jefe, os.path.join(CARPETA, destino))
        jefes.append(jefe)
        print("%-38s %2dx%-2d -> %3dx%-2d" % (destino, base.get_width(), base.get_height(),
                                              jefe.get_width(), jefe.get_height()))

    #la hoja: el fusilero de la tropa a la misma escala y al lado sus fotogramas, para poder
    #comparar de un vistazo si el galon se lee o se pierde
    ESCALA = 4
    tropa = pygame.image.load(os.path.join(CARPETA, 'soldado_fr_izq_3.png')).convert_alpha()
    piezasDeLaHoja = [tropa] + jefes[:7] + jefes[14:16]
    ancho = sum(p.get_width() for p in piezasDeLaHoja) * ESCALA + 14 * (len(piezasDeLaHoja) + 1)
    alto = max(p.get_height() for p in piezasDeLaHoja) * ESCALA + 28
    hoja = pygame.Surface((ancho, alto))
    hoja.fill((96, 150, 88))
    x = 14
    for pieza in piezasDeLaHoja:
        grande = pygame.transform.scale(pieza, (pieza.get_width() * ESCALA,
                                                pieza.get_height() * ESCALA))
        hoja.blit(grande, (x, alto - 14 - grande.get_height()))
        x += grande.get_width() + 14
    pygame.image.save(hoja, os.path.join(entorno.CAPTURAS, 'jefe_fusilero.png'))
    print("guardados %d sprites y la hoja jefe_fusilero.png (el primero es la tropa, a escala)"
          % len(jefes))


main()
