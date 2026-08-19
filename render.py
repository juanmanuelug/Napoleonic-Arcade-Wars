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
