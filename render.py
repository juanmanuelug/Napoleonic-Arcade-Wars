import pygame

# ####################################### Anclaje de sprites  ##########################################
# Los sprites de un mismo personaje no miden lo mismo: el de andar mide 20x36, el de apuntar
# 30x27 y el del fogonazo 53x35. Si todos se dibujan con la esquina superior izquierda en el
# mismo punto, el cuerpo salta de sitio al cambiar de sprite.
#
# Convenio: cada personaje tiene una "caja del cuerpo" (ancho y alto de referencia) cuya esquina
# superior izquierda es su posicion (x, y). Los sprites se desplazan para que coincidan:
#   - los pies (ultima fila con pixeles opacos) siempre a la misma altura
#   - los sprites de un personaje mirando a la izquierda crecen hacia la izquierda (el mosquete
#     ocupa el hueco extra del lienzo), y los de la derecha hacia la derecha
_desplazamientos = {}


def desplazamiento(imagen, ancho_referencia, alto_referencia, mirando_izq):
    """Devuelve el (dx, dy) con el que hay que dibujar la imagen. Se calcula una sola vez."""
    clave = (imagen, ancho_referencia, alto_referencia, mirando_izq)
    if clave not in _desplazamientos:
        contenido = imagen.get_bounding_rect()
        if mirando_izq:
            dx = ancho_referencia - imagen.get_width()
        else:
            dx = 0
        dy = alto_referencia - contenido.bottom
        _desplazamientos[clave] = (dx, dy)
    return _desplazamientos[clave]


def dibujar_anclado(win, imagen, x, y, mirando_izq, ancho_referencia, alto_referencia):
    """Dibuja la imagen anclada a la caja del cuerpo que empieza en (x, y)."""
    dx, dy = desplazamiento(imagen, ancho_referencia, alto_referencia, mirando_izq)
    win.blit(imagen, (x + dx, y + dy))


# ####################################### Destello al recibir un golpe #################################
# Copia blanqueada de cada sprite, cacheada: una silueta se blanquea una sola vez en toda la
# partida, no una vez por frame
_destellos = {}
BLANQUEO = 150


def destello(imagen):
    """La misma imagen pero blanca, para el fogonazo de dolor al recibir un impacto."""
    if imagen not in _destellos:
        copia = imagen.copy()
        #sumar solo al color, con alfa 0, deja intacta la transparencia del sprite
        copia.fill((BLANQUEO, BLANQUEO, BLANQUEO, 0), special_flags=pygame.BLEND_RGBA_ADD)
        _destellos[imagen] = copia
    return _destellos[imagen]

# ####################################### Aura de mando ###############################################
# El halo dorado de los soldados a los que un oficial esta acelerando. Es la silueta del propio
# sprite pintada de un color, dibujada cuatro veces alrededor y por DEBAJO del sprite: asi se ve
# un contorno y el soldado se sigue leyendo igual. Tenirlo entero no valia, porque estos sprites
# son casi todo negro y el tinte se los come.
#
# La silueta se construye con dos pasadas de fill, que es la unica forma de recolorear sin tocar
# el alfa: multiplicar por (0,0,0,255) deja el color a cero y el alfa intacto, y sumar el color
# con alfa 0 lo pinta sin volver a tocar el alfa. Una tercera pasada baja el alfa para que sea
# un halo y no un bloque. Y como cada silueta se calcula una sola vez y se guarda, esto no
# cuesta nada por frame.
_auras = {}
DESPLAZAMIENTOS_DEL_HALO = ((-1, 0), (1, 0), (0, -1), (0, 1))


def aura(imagen, color, alfa):
    """La silueta de la imagen pintada de color, con su alfa rebajado."""
    clave = (imagen, color, alfa)
    if clave not in _auras:
        silueta = imagen.copy()
        silueta.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
        silueta.fill(color + (0,), special_flags=pygame.BLEND_RGBA_ADD)
        silueta.fill((255, 255, 255, alfa), special_flags=pygame.BLEND_RGBA_MULT)
        _auras[clave] = silueta
    return _auras[clave]


def dibujar_aura(win, imagen, x, y, mirando_izq, ancho_referencia, alto_referencia, color, alfa):
    """Dibuja el halo alrededor de donde va a ir la imagen. Llamar ANTES de dibujar_anclado."""
    halo = aura(imagen, color, alfa)
    dx, dy = desplazamiento(imagen, ancho_referencia, alto_referencia, mirando_izq)
    for desplazaX, desplazaY in DESPLAZAMIENTOS_DEL_HALO:
        win.blit(halo, (x + dx + desplazaX, y + dy + desplazaY))
