import pygame

import objetos
from ascensos import RANGOS

pygame.init()

# ####################################### Indicadores en pantalla ######################################
# Todo lo que se pinta encima de la batalla: vida del jugador, recarga del mosquete, vida de
# cada enemigo y franceses abatidos.
FUENTE_HUD = pygame.font.Font('freesansbold.ttf', 12)
FUENTE_OLEADA = pygame.font.Font('freesansbold.ttf', 28)

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
COLOR_OLEADA = (240, 220, 150)

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
# ...y la linea del rango, que es la mas larga de todas
ANCHO_TEXTO_RANGO = max(FUENTE_HUD.size(nombre.upper() + "   000/000")[0] for nombre in RANGOS)
ANCHO_PANEL = max(MARGEN + ANCHO_BARRA + MARGEN + ANCHO_TEXTOS + MARGEN,
                  MARGEN + ANCHO_TEXTO_RANGO + MARGEN)


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


def altoPanel():
    """Lo que ocupa el panel del jugador. Los efectos activos se cuelgan justo debajo."""
    return (MARGEN + ALTO_BARRA_VIDA + SEPARACION + ALTO_BARRA_RECARGA
            + SEPARACION + FUENTE_HUD.get_height() + MARGEN)


def dibujarPanelJugador(win, soldado, progreso, ancho_pantalla, numeroOleada=None):
    """Vida, recarga, rango, oleada y franceses abatidos, sobre paneles oscuros para que se lean."""
    alto_panel = altoPanel()
    panel = pygame.Surface((ANCHO_PANEL, alto_panel), pygame.SRCALPHA)
    panel.fill(COLOR_PANEL)
    win.blit(panel, (0, 0))

    proporcion_vida = soldado.vida / float(soldado.vidaMaxima)
    barra_vida = pygame.Rect(MARGEN, MARGEN, ANCHO_BARRA, ALTO_BARRA_VIDA)
    _dibujarBarra(win, barra_vida, proporcion_vida, colorVida(proporcion_vida))

    ahora = pygame.time.get_ticks()
    avanceRecarga = soldado.progresoRecarga(ahora)
    listo = avanceRecarga >= 1.0
    barra_recarga = pygame.Rect(MARGEN, barra_vida.bottom + SEPARACION, ANCHO_BARRA, ALTO_BARRA_RECARGA)
    _dibujarBarra(win, barra_recarga, avanceRecarga,
                  COLOR_MOSQUETE_LISTO if listo else COLOR_RECARGANDO)

    #vida en numeros al lado de su barra
    vida = FUENTE_HUD.render(str(int(max(0, soldado.vida))), True, COLOR_TEXTO)
    win.blit(vida, vida.get_rect(midleft=(barra_vida.right + MARGEN, barra_vida.centery)))

    #estado del mosquete al lado de la barra de recarga
    texto_arma = TEXTO_LISTO if listo else TEXTO_RECARGANDO
    arma = FUENTE_HUD.render(texto_arma, True,
                             COLOR_MOSQUETE_LISTO if listo else COLOR_RECARGANDO)
    win.blit(arma, arma.get_rect(midleft=(barra_recarga.right + MARGEN, barra_recarga.centery)))

    #rango y cuanto falta para el siguiente ascenso
    #el rango va por puntos, que no son las bajas: un granadero vale por cuatro bayonetas
    siguiente = progreso.puntosParaAscender()
    if siguiente is None:
        texto_rango = progreso.nombreRango().upper()
    else:
        texto_rango = "%s   %d/%d" % (progreso.nombreRango().upper(), progreso.puntos, siguiente)
    rango = FUENTE_HUD.render(texto_rango, True, COLOR_TEXTO)
    win.blit(rango, (MARGEN, barra_recarga.bottom + SEPARACION))

    #oleada y franceses abatidos, arriba a la derecha
    lineas = []
    if numeroOleada is not None:
        lineas.append(FUENTE_HUD.render("OLEADA " + str(numeroOleada), True, COLOR_OLEADA))
    lineas.append(FUENTE_HUD.render("FRANCESES: " + str(progreso.bajas), True, COLOR_TEXTO))
    anchoMarcador = max(linea.get_width() for linea in lineas)
    altoMarcador = sum(linea.get_height() for linea in lineas)
    fondo = pygame.Surface((anchoMarcador + MARGEN, altoMarcador + MARGEN), pygame.SRCALPHA)
    fondo.fill(COLOR_PANEL)
    win.blit(fondo, (ancho_pantalla - MARGEN - anchoMarcador - MARGEN // 2, MARGEN // 2))
    y = MARGEN
    for linea in lineas:
        win.blit(linea, linea.get_rect(topright=(ancho_pantalla - MARGEN, y)))
        y += linea.get_height()


# ##################################### Efectos activos ################################################
# Los efectos que dan los objetos duran poco, asi que se ven colgados bajo el panel con su
# cuenta atras: un efecto temporal que no se ve es un efecto que no existe
ALTO_FILA_EFECTO = 16
ANCHO_PANEL_EFECTOS = 92


def efectosActivos(soldado, ahora):
    """Lista de (icono, texto) con lo que el soldado lleva encima ahora mismo."""
    activos = []
    if soldado.disparosGratis > 0:
        activos.append((objetos.ICONOS[objetos.CLAVE_CARTUCHERA],
                        "x%d" % soldado.disparosGratis))
    if soldado.tieneInmunidad(ahora):
        activos.append((objetos.ICONOS[objetos.CLAVE_AGUARDIENTE],
                        "%.1fs" % ((soldado.instanteFinInmunidad - ahora) / 1000.0)))
    if soldado.tieneDanioDoble(ahora):
        activos.append((objetos.ICONOS[objetos.CLAVE_ESTANDARTE],
                        "%.1fs" % ((soldado.instanteFinDanioDoble - ahora) / 1000.0)))
    return activos


def dibujarEfectos(win, soldado, ahora):
    activos = efectosActivos(soldado, ahora)
    if not activos:
        return
    arriba = altoPanel() + SEPARACION
    fondo = pygame.Surface((ANCHO_PANEL_EFECTOS, len(activos) * ALTO_FILA_EFECTO + MARGEN),
                           pygame.SRCALPHA)
    fondo.fill(COLOR_PANEL)
    win.blit(fondo, (0, arriba))
    for fila, (icono, texto) in enumerate(activos):
        y = arriba + MARGEN // 2 + fila * ALTO_FILA_EFECTO
        win.blit(icono, (MARGEN, y))
        etiqueta = FUENTE_HUD.render(texto, True, COLOR_TEXTO)
        win.blit(etiqueta, etiqueta.get_rect(midleft=(MARGEN + objetos.LADO_ICONO + 6,
                                                     y + objetos.LADO_ICONO // 2)))


# ################################## Aviso al recoger un objeto ########################################
# Un icono de 12x12 no puede explicar que hace lo que acabas de pisar, asi que al recogerlo se
# anuncia con su nombre y su efecto, y el cartel se apaga solo
DURACION_AVISO = 2200
DESVANECIDO_AVISO = 700
ARRIBA_AVISO = 76
COLOR_EFECTO_AVISO = (188, 226, 188)
AVISO_GUARDADO = 'guardado'
AVISO_USADO = 'usado'
TEXTO_GUARDADO = 'en la mochila - pulsa Q'


def dibujarAvisoObjeto(win, ancho_pantalla, clave, motivo, instante, ahora):
    """Cartel centrado con lo que se acaba de recoger. No pinta nada si ya se ha apagado."""
    if clave is None:
        return
    transcurrido = ahora - instante
    if transcurrido < 0 or transcurrido >= DURACION_AVISO:
        return
    restante = DURACION_AVISO - transcurrido
    if restante >= DESVANECIDO_AVISO:
        alfa = 255
    else:
        alfa = int(255 * restante / float(DESVANECIDO_AVISO))

    icono = objetos.ICONOS[clave]
    nombre = FUENTE_HUD.render(objetos.NOMBRES[clave].upper(), True, COLOR_TEXTO)
    if motivo == AVISO_GUARDADO:
        segundaLinea = TEXTO_GUARDADO
    else:
        segundaLinea = objetos.DESCRIPCIONES[clave]
    efecto = FUENTE_HUD.render(segundaLinea, True, COLOR_EFECTO_AVISO)
    anchoTextos = max(nombre.get_width(), efecto.get_width())
    ancho = MARGEN + objetos.LADO_ICONO + MARGEN + anchoTextos + MARGEN
    alto = MARGEN // 2 + nombre.get_height() + efecto.get_height() + MARGEN // 2

    tarjeta = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    tarjeta.fill(COLOR_PANEL)
    tarjeta.blit(icono, (MARGEN, (alto - objetos.LADO_ICONO) // 2))
    izquierdaTextos = MARGEN + objetos.LADO_ICONO + MARGEN
    tarjeta.blit(nombre, (izquierdaTextos, MARGEN // 2))
    tarjeta.blit(efecto, (izquierdaTextos, MARGEN // 2 + nombre.get_height()))
    tarjeta.set_alpha(alfa)
    win.blit(tarjeta, ((ancho_pantalla - ancho) // 2, ARRIBA_AVISO))


# ################################### Aviso de oleada ##################################################
# El cartel de la calma entre rondas: dice cual viene y cuanto queda para que entre
ARRIBA_AVISO_OLEADA = 170


def dibujarAvisoOleada(win, ancho_pantalla, numero, milisegundosRestantes):
    """Cartel de la calma: OLEADA n y la cuenta atras."""
    titulo = FUENTE_OLEADA.render("OLEADA %d" % numero, True, COLOR_OLEADA)
    segundos = max(0, int(milisegundosRestantes / 1000.0) + 1)
    cuenta = FUENTE_HUD.render("entran en %d..." % segundos, True, COLOR_TEXTO)
    ancho = max(titulo.get_width(), cuenta.get_width()) + MARGEN * 4
    alto = titulo.get_height() + cuenta.get_height() + MARGEN * 2
    tarjeta = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    tarjeta.fill(COLOR_PANEL)
    tarjeta.blit(titulo, titulo.get_rect(midtop=(ancho // 2, MARGEN)))
    tarjeta.blit(cuenta, cuenta.get_rect(midtop=(ancho // 2, MARGEN + titulo.get_height())))
    win.blit(tarjeta, ((ancho_pantalla - ancho) // 2, ARRIBA_AVISO_OLEADA))


# ####################################### La mochila ###################################################
# El hueco unico donde se guarda lo recogido hasta que el jugador decide gastarlo. Va siempre en
# la misma esquina, tambien cuando esta vacio: si no se ve, nadie descubre que existe la tecla
ALTO_MOCHILA = 30
ANCHO_MOCHILA = 150
COLOR_TECLA = (240, 220, 150)
COLOR_MOCHILA_VACIA = (150, 150, 145)
TEXTO_MOCHILA_VACIA = "MOCHILA VACIA"
TECLA_DE_USO = "Q"


def dibujarMochila(win, soldado, alto_pantalla):
    arriba = alto_pantalla - ALTO_MOCHILA - MARGEN
    fondo = pygame.Surface((ANCHO_MOCHILA, ALTO_MOCHILA), pygame.SRCALPHA)
    fondo.fill(COLOR_PANEL)
    win.blit(fondo, (MARGEN, arriba))

    if soldado.objetoEnMochila is None:
        vacia = FUENTE_HUD.render(TEXTO_MOCHILA_VACIA, True, COLOR_MOCHILA_VACIA)
        win.blit(vacia, vacia.get_rect(midleft=(MARGEN * 2, arriba + ALTO_MOCHILA // 2)))
        return

    clave = soldado.objetoEnMochila
    win.blit(objetos.ICONOS[clave], (MARGEN * 2, arriba + (ALTO_MOCHILA - objetos.LADO_ICONO) // 2))
    nombre = FUENTE_HUD.render(objetos.NOMBRES[clave].upper(), True, COLOR_TEXTO)
    win.blit(nombre, nombre.get_rect(midleft=(MARGEN * 2 + objetos.LADO_ICONO + MARGEN,
                                              arriba + ALTO_MOCHILA // 2)))
    #la tecla, a la derecha del hueco, para que se vea que hay algo que pulsar
    tecla = FUENTE_HUD.render(TECLA_DE_USO, True, COLOR_TECLA)
    recuadro = tecla.get_rect(midright=(MARGEN + ANCHO_MOCHILA - MARGEN, arriba + ALTO_MOCHILA // 2))
    pygame.draw.rect(win, COLOR_TECLA, recuadro.inflate(8, 6), 1)
    win.blit(tecla, recuadro)
