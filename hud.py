import pygame

pygame.init()

# ####################################### Indicadores en pantalla ######################################
# Todo lo que se pinta encima de la batalla: vida del jugador, recarga del mosquete, vida de
# cada enemigo y franceses abatidos.
FUENTE_HUD = pygame.font.Font('freesansbold.ttf', 12)

COLOR_PANEL = (0, 0, 0, 120)
COLOR_HUECO_BARRA = (35, 35, 35)
COLOR_BORDE_BARRA = (10, 10, 10)
COLOR_VIDA_ALTA = (70, 175, 80)
COLOR_VIDA_MEDIA = (225, 175, 45)
COLOR_VIDA_BAJA = (200, 55, 55)
COLOR_RECARGANDO = (150, 150, 155)
COLOR_MOSQUETE_LISTO = (95, 170, 230)
COLOR_TEXTO = (240, 240, 235)
COLOR_VIDA_ENEMIGO = (205, 60, 60)

MARGEN = 8
ANCHO_BARRA = 130
ALTO_BARRA_VIDA = 12
ALTO_BARRA_RECARGA = 6
SEPARACION = 4
ANCHO_BARRA_ENEMIGO = 22
ALTO_BARRA_ENEMIGO = 5
HUECO_SOBRE_LA_CABEZA = 4

TEXTO_RECARGANDO = "RECARGANDO"
TEXTO_LISTO = "LISTO"
# el panel tiene que tapar tambien los textos de la derecha, o no se leen sobre la hierba
ANCHO_TEXTOS = max(FUENTE_HUD.size(TEXTO_RECARGANDO)[0], FUENTE_HUD.size(TEXTO_LISTO)[0],
                   FUENTE_HUD.size("100")[0])
ANCHO_PANEL = MARGEN + ANCHO_BARRA + MARGEN + ANCHO_TEXTOS + MARGEN


def _dibujarBarra(win, rectangulo, proporcion, color):
    proporcion = max(0.0, min(1.0, proporcion))
    pygame.draw.rect(win, COLOR_HUECO_BARRA, rectangulo)
    relleno = pygame.Rect(rectangulo)
    relleno.width = int(round(rectangulo.width * proporcion))
    if relleno.width > 0:
        pygame.draw.rect(win, color, relleno)
    pygame.draw.rect(win, COLOR_BORDE_BARRA, rectangulo, 1)


def colorVida(proporcion):
    if proporcion > 0.6:
        return COLOR_VIDA_ALTA
    if proporcion > 0.3:
        return COLOR_VIDA_MEDIA
    return COLOR_VIDA_BAJA


def dibujarVidaEnemigo(win, enemigo):
    """Barrita roja flotando sobre la cabeza del enemigo."""
    proporcion = enemigo.vida / float(enemigo.vidaMaxima)
    barra = pygame.Rect(0, 0, ANCHO_BARRA_ENEMIGO, ALTO_BARRA_ENEMIGO)
    barra.centerx = enemigo.rect.centerx
    barra.bottom = max(ALTO_BARRA_ENEMIGO + 1, enemigo.rect.top - HUECO_SOBRE_LA_CABEZA)
    _dibujarBarra(win, barra, proporcion, COLOR_VIDA_ENEMIGO)


def dibujarPanelJugador(win, soldado, puntuacion, ancho_pantalla):
    """Vida, recarga del mosquete y franceses abatidos, sobre un panel oscuro para que se lea."""
    alto_panel = MARGEN + ALTO_BARRA_VIDA + SEPARACION + ALTO_BARRA_RECARGA + MARGEN
    panel = pygame.Surface((ANCHO_PANEL, alto_panel), pygame.SRCALPHA)
    panel.fill(COLOR_PANEL)
    win.blit(panel, (0, 0))

    proporcion_vida = soldado.vida / float(soldado.vidaMaxima)
    barra_vida = pygame.Rect(MARGEN, MARGEN, ANCHO_BARRA, ALTO_BARRA_VIDA)
    _dibujarBarra(win, barra_vida, proporcion_vida, colorVida(proporcion_vida))

    ahora = pygame.time.get_ticks()
    progreso = soldado.progresoRecarga(ahora)
    listo = progreso >= 1.0
    barra_recarga = pygame.Rect(MARGEN, barra_vida.bottom + SEPARACION, ANCHO_BARRA, ALTO_BARRA_RECARGA)
    _dibujarBarra(win, barra_recarga, progreso,
                  COLOR_MOSQUETE_LISTO if listo else COLOR_RECARGANDO)

    #vida en numeros al lado de su barra
    vida = FUENTE_HUD.render(str(int(max(0, soldado.vida))), True, COLOR_TEXTO)
    win.blit(vida, vida.get_rect(midleft=(barra_vida.right + MARGEN, barra_vida.centery)))

    #estado del mosquete al lado de la barra de recarga
    texto_arma = TEXTO_LISTO if listo else TEXTO_RECARGANDO
    arma = FUENTE_HUD.render(texto_arma, True,
                             COLOR_MOSQUETE_LISTO if listo else COLOR_RECARGANDO)
    win.blit(arma, arma.get_rect(midleft=(barra_recarga.right + MARGEN, barra_recarga.centery)))

    #franceses abatidos, arriba a la derecha
    marcador = FUENTE_HUD.render("FRANCESES: " + str(puntuacion), True, COLOR_TEXTO)
    sitio = marcador.get_rect(topright=(ancho_pantalla - MARGEN, MARGEN))
    fondo = pygame.Surface((sitio.width + MARGEN, sitio.height + MARGEN), pygame.SRCALPHA)
    fondo.fill(COLOR_PANEL)
    win.blit(fondo, (sitio.left - MARGEN // 2, sitio.top - MARGEN // 2))
    win.blit(marcador, sitio)
