import os
import pygame
import sys

import ascensos
import colisiones
import granadas
import hud
import objetos
import oleadas
import records
import sablazos
from jugador import jugador
from enemigo import (enemigo, enemigoDistancia, voltigeur, oficial, granadero, jefeGranadero,
                     jefeSable, jefeFusilero, puntoDeAparicion, cadaveresVigentes, aplicarMando)


pygame.init()
# ####################################### Constantes  ##################################################
WINX = 500
WINY = 500
FPS = 30
# Franceses vivos como mucho a la vez. Sin tope se acumulan sin fin (medidos 27 a los cinco
# minutos): al llegar al techo la aparicion se salta ese turno y espera al siguiente
MAX_ENEMIGOS = 18
# Tecla con la que se gasta lo que se lleva en la mochila
TECLA_MOCHILA = pygame.K_q
# Bayonetazo y dash. Van por pulsacion y no por mantener, como la mochila: son gestos, y
# mantenerlos pulsados no deberia dispararlos en bucle
TECLA_BAYONETA = pygame.K_e
TECLAS_DASH = (pygame.K_LSHIFT, pygame.K_RSHIFT)
# ##################################### Modo de pruebas ###############################################
# Para poder probar a mano sin jugarse una partida entera: llegar a la oleada del jefe eran ocho
# oleadas de peaje.
#
# ENCENDIDO. Mientras lo este, lo dice una linea en pantalla, porque un juego que se comporta
# distinto sin avisar es una trampa para quien lo prueba. Para apagarlo, cualquiera de las dos:
#
#     PRUEBAS=0 python main.py          (sin tocar el codigo)
#     MODO_PRUEBAS = False              (aqui abajo, a mano)
#
# Conviene apagarlo antes de ensenarle el juego a alguien: estas teclas meten jefes y hacen
# invulnerable, y una I sin querer deja la partida sin sentido.
MODO_PRUEBAS = os.environ.get('PRUEBAS', '1') != '0'
# En que oleada empezar. Por defecto la primera, o sea que la partida normal no cambia; con
# OLEADA=8 se empieza ahi, y entonces el soldado arranca ya con todas las mejoras, que es lo que
# tendria al llegar jugando: con el mosquete de recluta un jefe de 2400 de vida son dos minutos y
# medio de disparar, y eso no prueba nada
OLEADA_DE_PRUEBAS = int(os.environ.get('OLEADA', oleadas.PRIMERA_OLEADA))
# Teclas del modo de pruebas. Solo hacen algo con MODO_PRUEBAS encendido
TECLA_PRUEBAS_JEFE = pygame.K_j
TECLA_PRUEBAS_SIGUIENTE_OLEADA = pygame.K_n
TECLA_PRUEBAS_INMUNE = pygame.K_i
TECLA_PRUEBAS_FASE = pygame.K_f
# A que jefe saca la tecla J. Se pone a mano el que se este trabajando, que es lo que se quiere
# mirar cien veces seguidas; con None rota por la rueda entera, uno por pulsacion
JEFE_DE_PRUEBAS = oleadas.JEFE_FUSILERO
# Escenas del juego
ESCENA_MENU = "menu"
ESCENA_PARTIDA = "partida"
ESCENA_PAUSA = "pausa"
ESCENA_ASCENSO = "ascenso"
ESCENA_GAME_OVER = "game_over"
ESCENA_SALIR = "salir"
# #######################################   Sonidos  ###################################################
pygame.mixer.music.load('./music/marchaBritanica.wav')
# ######################################  Texturas   #####################################################

menu_images = pygame.image.load('./imgs/waterloo.jpg')
derrota_images = pygame.image.load('./imgs/derrota.jpg')

bg = pygame.image.load('./imgs/background.jpg')

# #####################################   FPS   ###########################################################
clock = pygame.time.Clock()
# #######################################   Ventana    #####################################################
# El juego se dibuja siempre en 500x500 (win) y se presenta escalado (ventana), asi que el
# arte no cambia con el tamanio. La escala se calcula para que la ventana quepa en la pantalla
# donde se ejecute: en un escritorio de 960 px de alto, una ventana de 1000 se sale por abajo.
# Para fijar un tamanio a mano, poner un numero en ESCALA_FORZADA (1 = 500x500, 2 = 1000x1000).
ESCALA_FORZADA = None
ESCALA_MINIMA = 1.0
ESCALA_MAXIMA = 2.0
PASO_ESCALA = 0.5
# Sitio que hay que dejarle al marco de la ventana, la barra de titulo y la de tareas
MARGEN_ESCRITORIO_ANCHO = 40
MARGEN_ESCRITORIO_ALTO = 120


def tamanioEscritorio():
    """(ancho, alto) del escritorio, o None si SDL no sabe decirlo."""
    try:
        tamanios = pygame.display.get_desktop_sizes()
        if tamanios and tamanios[0][0] > 0:
            return tamanios[0]
    except (AttributeError, pygame.error):
        pass
    try:
        informacion = pygame.display.Info()
        if informacion.current_w > 0:
            return (informacion.current_w, informacion.current_h)
    except pygame.error:
        pass
    return None


def escalaQueCabe(ancho, alto, escritorio):
    """La escala mas grande, en pasos de PASO_ESCALA, con la que la ventana entra en pantalla."""
    if not escritorio:
        return ESCALA_MINIMA
    anchoLibre = escritorio[0] - MARGEN_ESCRITORIO_ANCHO
    altoLibre = escritorio[1] - MARGEN_ESCRITORIO_ALTO
    escala = ESCALA_MINIMA
    candidata = ESCALA_MINIMA
    while candidata <= ESCALA_MAXIMA:
        if ancho * candidata <= anchoLibre and alto * candidata <= altoLibre:
            escala = candidata
        candidata += PASO_ESCALA
    return escala


ESCALA = ESCALA_FORZADA if ESCALA_FORZADA else escalaQueCabe(WINX, WINY, tamanioEscritorio())
TAMANIO_VENTANA = (int(WINX * ESCALA), int(WINY * ESCALA))
ventana = pygame.display.set_mode(TAMANIO_VENTANA)
win = pygame.Surface((WINX, WINY))


def presentar():
    # el escalado escribe directamente sobre la ventana, sin crear superficies cada frame
    pygame.transform.scale(win, TAMANIO_VENTANA, ventana)
    pygame.display.update()


# ######################################   Nombre de la ventana       ########################################
pygame.display.set_caption("Waterloo")
# ######################################   Fuentes (una sola vez, no en cada frame)  ###########################
FUENTE_TITULO = pygame.font.Font('freesansbold.ttf', 25)
FUENTE_OPCION = pygame.font.Font('freesansbold.ttf', 18)
FUENTE_PEQUENA = pygame.font.Font('freesansbold.ttf', 13)
FUENTE_DERROTA = pygame.font.Font('freesansbold.ttf', 50)
# ######################################   Velo para las pausas   #############################################
VELO_PAUSA = pygame.Surface((WINX, WINY), pygame.SRCALPHA)
VELO_PAUSA.fill((0, 0, 0, 175))
# #####################################   Estado de la partida   ##############################################
player = None
balas = []
balasEnemigas = []
enemies = []
cadaveres = []
objetosEnSuelo = []
#las granadas en el aire y los fogonazos de las que ya cayeron
granadasEnElAire = []
estallidos = []
#el rastro de las hojas de sable, que dura un pestañeo
sablazosEnElAire = []
#lo ultimo que se ha recogido, para anunciarlo un momento en pantalla
avisoObjeto = None
avisoObjetoMotivo = hud.AVISO_GUARDADO
avisoObjetoInstante = 0
progreso = ascensos.Progreso()
#cuando empezo la partida, para saber cuanto se ha sobrevivido
instanteInicioPartida = 0
#la marca guardada, y si la partida que acaba de terminar la ha batido
record = records.cargar()
recordBatido = False
#en el modo de pruebas, si el soldado es invulnerable, y por que jefe de la rueda va la tecla J
inmuneDePruebas = False
turnoDelJefeDePruebas = 0
#la oleada en curso y la calma entre una y otra
oleada = None
enCalma = False
instanteFinCalma = 0


def equiparComoCoronel(soldado, marcador):
    """Le da al soldado todas las mejoras y el rango maximo, como si hubiera llegado jugando.

    Solo lo usa el modo de pruebas: empezar en una oleada alta con el mosquete de recluta no
    prueba nada, porque lo que se quiere ver es la pelea, no el tiempo que se tarda en matar.
    """
    marcador.rango = len(ascensos.RANGOS) - 1
    marcador.puntos = ascensos.PUNTOS_POR_RANGO[-1]
    for clave in (ascensos.CLAVE_RECARGA, ascensos.CLAVE_VIDA, ascensos.CLAVE_DANIO):
        #se aplica hasta que deje de cambiar: cada mejora tiene su propio tope
        for _ in range(10):
            antes = (soldado.recarga, soldado.vidaMaxima, soldado.danioBala)
            ascensos.aplicar(soldado, clave)
            if (soldado.recarga, soldado.vidaMaxima, soldado.danioBala) == antes:
                break
    soldado.vida = soldado.vidaMaxima


def atajoDePruebas(tecla):
    """Las teclas del modo de pruebas. Sin el modo encendido, ni una hace nada."""
    global enCalma, instanteFinCalma, inmuneDePruebas
    if not MODO_PRUEBAS:
        return False
    if tecla == TECLA_PRUEBAS_JEFE:
        #un jefe aqui y ahora, sin esperar a que toque su oleada. Si JEFE_DE_PRUEBAS dice cual,
        #sale siempre ese; si no, rota por la rueda, porque con cuatro jefes habria que llegar a la
        #oleada 23 para poder mirar el ultimo
        global turnoDelJefeDePruebas
        if JEFE_DE_PRUEBAS:
            cual = JEFE_DE_PRUEBAS
        else:
            cual = oleadas.RUEDA_DE_JEFES[turnoDelJefeDePruebas % len(oleadas.RUEDA_DE_JEFES)]
            turnoDelJefeDePruebas += 1
        entrarEnBatalla(oleadas.JEFE, cual)
        return True
    if tecla == TECLA_PRUEBAS_SIGUIENTE_OLEADA:
        #se limpia el campo y se vacia el cupo: el juego pasa de oleada por su propio camino
        for enemigo_vivo in enemies:
            enemigo_vivo.vida = 0
        oleada.pendientes = dict((tipo, 0) for tipo in oleada.pendientes)
        return True
    if tecla == TECLA_PRUEBAS_INMUNE:
        inmuneDePruebas = not inmuneDePruebas
        return True
    if tecla == TECLA_PRUEBAS_FASE:
        #le baja la vida al jefe hasta justo por debajo del siguiente tramo, para ver sus fases.
        #A los jefes que no cambian de ataque por vida no se les toca: dejarlos a un golpe de morir
        #no ensenia nada y encima confunde
        for enemigo_vivo in enemies:
            if not getattr(enemigo_vivo, 'ES_JEFE', False):
                continue
            tramo = siguienteTramoDeVida(enemigo_vivo)
            if tramo is not None:
                enemigo_vivo.vida = tramo
        return True
    return False


def siguienteTramoDeVida(jefe):
    """La vida con la que el jefe entra en su siguiente fase, o None si no tiene fases.

    Devolver None y no un numero importa: hay jefes que no cambian de ataque por vida (el de
    sable lleva sus dos ataques a la vez), y para esos la tecla no debe hacer nada.
    """
    umbrales = sorted(getattr(jefe, 'UMBRALES_DE_FASE', ()), reverse=True)
    if not umbrales:
        return None
    for umbral in umbrales:
        objetivo = int(jefe.vidaMaxima * umbral)
        if jefe.vida > objetivo:
            return objetivo
    #ya esta en el ultimo tramo: se le deja a un golpe, para poder ver el final
    return 1


def reiniciarPartida():
    # Deja el estado como recien empezada la batalla, para poder volver a jugar sin cerrar el juego
    global player, balas, balasEnemigas, enemies, cadaveres, objetosEnSuelo, progreso
    global granadasEnElAire, estallidos, sablazosEnElAire
    global avisoObjeto, avisoObjetoMotivo, avisoObjetoInstante
    global instanteInicioPartida, recordBatido
    global oleada, enCalma, instanteFinCalma, inmuneDePruebas
    ahora = pygame.time.get_ticks()
    inmuneDePruebas = False
    player = jugador(250, 250)
    balas = []
    balasEnemigas = []
    enemies = []
    cadaveres = []
    objetosEnSuelo = []
    granadasEnElAire = []
    estallidos = []
    sablazosEnElAire = []
    avisoObjeto = None
    avisoObjetoMotivo = hud.AVISO_GUARDADO
    avisoObjetoInstante = 0
    progreso = ascensos.Progreso()
    instanteInicioPartida = ahora
    recordBatido = False
    #la partida arranca con la calma de la primera oleada, no en medio de la batalla
    primera = OLEADA_DE_PRUEBAS if MODO_PRUEBAS else oleadas.PRIMERA_OLEADA
    if MODO_PRUEBAS and primera > oleadas.PRIMERA_OLEADA:
        equiparComoCoronel(player, progreso)
    oleada = oleadas.Oleada(primera, ahora)
    enCalma = True
    instanteFinCalma = ahora + oleadas.DURACION_CALMA


def compensarPausa(milisegundos):
    # Un rato en la pantalla de ascenso no debe regalar disparos ni apariciones, ni caducar
    # cadaveres: se empujan todos los relojes de la partida lo que haya durado la pausa
    global avisoObjetoInstante, instanteInicioPartida, instanteFinCalma
    instanteFinCalma += milisegundos
    oleada.instanteUltimaEntrada += milisegundos
    player.instanteUltimoDisparo += milisegundos
    player.instanteUltimoGolpe += milisegundos
    player.instanteUltimaEstocada += milisegundos
    player.instanteUltimoDash += milisegundos
    for enemy in enemies:
        enemy.instanteUltimoDisparo += milisegundos
    for cadaver in cadaveres:
        cadaver.instanteMuerte += milisegundos
    for cosa in objetosEnSuelo:
        cosa.instanteAparicion += milisegundos
    for granada in granadasEnElAire:
        granada.instanteLanzamiento += milisegundos
    for estallido in estallidos:
        estallido.instante += milisegundos
    for sablazo in sablazosEnElAire:
        sablazo.instante += milisegundos
    for enemy in enemies:
        enemy.instanteUltimoLanzamiento += milisegundos
        enemy.instanteInicioArmado += milisegundos
        enemy.instanteUltimoTajo += milisegundos
        enemy.instanteInicioAlzado += milisegundos
        #los relojes de la carga del jefe de sable; los demas enemigos no los tienen
        if hasattr(enemy, 'instanteUltimaCarga'):
            enemy.instanteUltimaCarga += milisegundos
            enemy.instanteInicioCarga += milisegundos
        #y el compas con el que los jefes van soltando su rafaga o su descarga. Sin esto, volver
        #de la pausa le regalaba al jefe la siguiente granada o el siguiente anillo de plomo
        for reloj in ('instanteDeLaUltimaDeLaRafaga', 'instanteDeLaUltimaDeLaDescarga',
                      'instanteInicioPunteria'):
            if hasattr(enemy, reloj):
                setattr(enemy, reloj, getattr(enemy, reloj) + milisegundos)
    avisoObjetoInstante += milisegundos
    instanteInicioPartida += milisegundos
    if player.instanteFinInmunidad:
        player.instanteFinInmunidad += milisegundos
    if player.instanteFinDanioDoble:
        player.instanteFinDanioDoble += milisegundos

# #######################################   Funciones    ######################################################

def drawWindow():
    # fondo de la pantalla
    win.blit(bg, (0, 0))
    ahoraMarcas = pygame.time.get_ticks()
    #las marcas de las granadas van pintadas en el suelo, antes que nadie, para que no
    #tapen a los soldados ni se confundan con ellos
    for granada in granadasEnElAire:
        granada.dibujarMarca(win, ahoraMarcas)
    #y el anillo de mando de los oficiales, tambien en el suelo
    for enemy in enemies:
        enemy.dibujarMando(win)
    # dibujar al jugador
    player.dibujar(win)
    for enemy in enemies:
        enemy.dibujarEnemigo(win)
        hud.dibujarVidaEnemigo(win, enemy)
    #dibujar balas
    for bala in balas:
        bala.dibujar_bala(win)

    for balaE in balasEnemigas:
        balaE.dibujar_bala(win)
    for cadaver in cadaveres:
        cadaver.dibujarCadaver(win)
    #las granadas en el aire y los fogonazos, por encima de todo el mundo
    for granada in granadasEnElAire:
        granada.dibujar(win, ahoraMarcas)
    for estallido in estallidos:
        estallido.dibujar(win, ahoraMarcas)
    #el rastro del sable, por encima de los cuerpos: sale de la mano de quien lo mueve
    for sablazo in sablazosEnElAire:
        sablazo.dibujar(win, ahoraMarcas)
    #lo que han soltado los caidos, por encima de los cuerpos
    ahora = pygame.time.get_ticks()
    for cosa in objetosEnSuelo:
        cosa.dibujar(win, ahora)
    # indicadores por encima de la batalla
    hud.dibujarPanelJugador(win, player, progreso, WINX, oleada.numero)
    hud.dibujarVidaJefe(win, enemies, WINX)
    hud.dibujarEfectos(win, player, ahora)
    hud.dibujarAvisoObjeto(win, WINX, avisoObjeto, avisoObjetoMotivo,
                           avisoObjetoInstante, ahora)
    hud.dibujarMochila(win, player, WINY)
    if MODO_PRUEBAS:
        hud.dibujarAvisoDePruebas(win, WINX, WINY, inmuneDePruebas)
    if enCalma:
        hud.dibujarAvisoOleada(win, WINX, oleada.numero, instanteFinCalma - ahora)
    # actualizacion de la pantalla
    presentar()

def entrarEnBatalla(tipo, cual=None):
    """Mete en el campo un frances del tipo que se pida.

    Con 'cual' se puede forzar QUE jefe entra, en vez de dejarlo en manos de la rueda. Lo usa el
    atajo del modo de pruebas, que tiene que poder sacar cualquiera de los cuatro sin esperar a
    que le toque su oleada.
    """
    # Entra por el borde, nunca encima del jugador
    x, y = puntoDeAparicion(player.x, player.y)
    if tipo == oleadas.JEFE:
        #cual de los jefes toca lo dice la rueda, no el tipo: el cupo solo dice "aqui va jefe"
        cuales = {oleadas.JEFE_GRANADERO: jefeGranadero, oleadas.JEFE_SABLE: jefeSable,
                  oleadas.JEFE_FUSILERO: jefeFusilero}
        #si la oleada no es de jefe no hay turno de rueda, y aun asi hay que dar uno
        elegido = cual or oleadas.jefeDeLaOleada(oleada.numero) or oleadas.RUEDA_DE_JEFES[0]
        enemies.append(cuales[elegido](x, y, player.x, player.y))
        #su escolta no entra aqui: la llama el propio jefe conforme le baja la vida, en
        #llamarEscoltaDeLosJefes
    elif tipo == oleadas.OFICIAL:
        enemies.append(oficial(x, y, player.x, player.y))
    elif tipo == oleadas.GRANADERO:
        enemies.append(granadero(x, y, player.x, player.y))
    elif tipo == oleadas.VOLTIGEUR:
        #tambien coge puesto libre, pero de la linea del voltigeur, que va mucho mas atras
        enemies.append(voltigeur(x, y, player.x, player.y, enemies))
    elif tipo == oleadas.TIRADOR:
        #se le pasa quien esta ya en el campo para que coja un puesto de tiro libre
        enemies.append(enemigoDistancia(x, y, player.x, player.y, enemies))
    else:
        enemies.append(enemigo(x, y, player.x, player.y))


def llamarEscoltaDeLosJefes():
    """Mete la escolta que le toque a cada jefe segun la vida que le quede.

    Se llama cada frame. Los grupos salen de uno en uno conforme el jefe cruza cada escalon de
    vida, y un grupo entra entero o no entra: si no cabe se queda pendiente y vuelve a intentarlo
    el frame siguiente, cuando el jugador haya hecho sitio. Meter medio grupo seria peor que
    esperar, porque el escalon se gastaria y la mitad que falta no volveria nunca.
    """
    #se saca la lista de jefes antes de meter tropa: entrarEnBatalla escribe en enemies, y no se
    #recorre una lista a la que se le esta anadiendo
    for jefe in [uno for uno in enemies
                 if getattr(uno, 'ES_JEFE', False) and uno.vivo and uno.LLAMA_ESCOLTA]:
        while jefe.oleadasDeEscoltaPedidas < len(oleadas.ESCOLTA_POR_FASES):
            umbral, tipos = oleadas.ESCOLTA_POR_FASES[jefe.oleadasDeEscoltaPedidas]
            if jefe.vida / float(jefe.vidaMaxima) > umbral:
                break
            if len(enemies) + len(tipos) > MAX_ENEMIGOS:
                break
            jefe.oleadasDeEscoltaPedidas += 1
            for tipoDeEscolta in tipos:
                entrarEnBatalla(tipoDeEscolta)


def llevarOleada(ahora):
    # Va sacando el cupo de la oleada, y cuando el campo queda limpio da la calma, suelta la
    # caja del premio y prepara la siguiente
    global oleada, enCalma, instanteFinCalma
    if enCalma:
        if ahora >= instanteFinCalma:
            enCalma = False
        return
    if oleada.tocaEntrar(ahora):
        #si el campo esta al tope, el que falta espera a que se libere un hueco
        if len(enemies) < MAX_ENEMIGOS:
            entrarEnBatalla(oleada.sacarSiguiente(ahora))
        return
    if oleada.limpiada(enemies):
        objetosEnSuelo.append(objetos.sueltaGarantizada(WINX // 2, WINY // 2, ahora))
        oleada = oleadas.Oleada(oleada.numero + 1, ahora)
        enCalma = True
        instanteFinCalma = ahora + oleadas.DURACION_CALMA



# ########################################### Textos #############################################################
def dibujarTextoCentrado(texto, fuente, y, color=(0,0,0)):
    superficie = fuente.render(texto, True, color)
    win.blit(superficie, superficie.get_rect(center=(WINX/2, y)))

def dibujarBanda(arriba, alto, opacidad=160):
    # Banda oscura para que el texto se lea sobre cualquier imagen
    banda = pygame.Surface((WINX, alto), pygame.SRCALPHA)
    banda.fill((0, 0, 0, opacidad))
    win.blit(banda, (0, arriba))

def dibujarBandaOpciones():
    dibujarBanda(WINY - 72, 62)

# ########################################### Escenas ############################################################
def menu():
    pygame.mixer.music.play(-1)
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ESCENA_SALIR
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    pygame.mixer.music.stop()
                    reiniciarPartida()
                    return ESCENA_PARTIDA
                if event.key == pygame.K_ESCAPE:
                    return ESCENA_SALIR

        win.blit(menu_images, (0, 0))
        dibujarBanda(8, 56, 150)
        dibujarTextoCentrado("La Batalla de Waterloo", FUENTE_TITULO, 25, (240, 234, 214))
        dibujarTextoCentrado(records.comoTexto(record, ascensos.RANGOS[record["rango"]]),
                             FUENTE_PEQUENA, 50, (240, 235, 210))
        dibujarBandaOpciones()
        dibujarTextoCentrado("ENTER - A la batalla", FUENTE_OPCION, WINY - 55, (255,255,255))
        dibujarTextoCentrado("ESC - Salir", FUENTE_OPCION, WINY - 28, (255,255,255))
        presentar()

def gameOver():
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ESCENA_SALIR
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    return ESCENA_MENU
                if event.key == pygame.K_ESCAPE:
                    return ESCENA_SALIR

        win.blit(derrota_images, (0, 0))
        dibujarBanda(16, 140, 170)
        dibujarTextoCentrado("Has Muerto", FUENTE_DERROTA, 45, (238, 232, 220))
        dibujarTextoCentrado("Caido siendo " + progreso.nombreRango(), FUENTE_OPCION, 85, (238, 232, 220))
        dibujarTextoCentrado("Franceses abatidos: " + str(progreso.bajas), FUENTE_OPCION, 110, (238, 232, 220))
        if recordBatido:
            dibujarTextoCentrado("NUEVA MARCA", FUENTE_OPCION, 138, (245, 225, 130))
        else:
            dibujarTextoCentrado(records.comoTexto(record, ascensos.RANGOS[record["rango"]]),
                                 FUENTE_PEQUENA, 138, (225, 225, 225))
        dibujarBandaOpciones()
        dibujarTextoCentrado("ENTER - Volver al menu", FUENTE_OPCION, WINY - 55, (255,255,255))
        dibujarTextoCentrado("ESC - Salir", FUENTE_OPCION, WINY - 28, (255,255,255))
        presentar()

def pausa():
    # La batalla se queda congelada. ESC pide abandonar y hace falta confirmarlo: antes ESC
    # te devolvia al menu de golpe y perdias la partida sin preguntar
    fondoCongelado = win.copy()
    inicio = pygame.time.get_ticks()
    confirmandoAbandono = False
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ESCENA_SALIR
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    compensarPausa(pygame.time.get_ticks() - inicio)
                    return ESCENA_PARTIDA
                if event.key == pygame.K_ESCAPE:
                    if confirmandoAbandono:
                        return ESCENA_MENU
                    confirmandoAbandono = True

        win.blit(fondoCongelado, (0, 0))
        win.blit(VELO_PAUSA, (0, 0))
        dibujarTextoCentrado("ALTO EL FUEGO", FUENTE_TITULO, 150, (245, 235, 200))
        dibujarTextoCentrado("ENTER - Seguir combatiendo", FUENTE_OPCION, 215, (245, 245, 240))
        if confirmandoAbandono:
            dibujarTextoCentrado("ESC otra vez - Abandonar la batalla", FUENTE_OPCION, 250, (228, 88, 95))
            dibujarTextoCentrado("perderas esta partida", FUENTE_PEQUENA, 272, (228, 88, 95))
        else:
            dibujarTextoCentrado("ESC - Abandonar la batalla", FUENTE_OPCION, 250, (215, 215, 215))
        presentar()

TECLAS_MEJORA = {pygame.K_1: 0, pygame.K_KP1: 0,
                 pygame.K_2: 1, pygame.K_KP2: 1,
                 pygame.K_3: 2, pygame.K_KP3: 2}

def ascenso():
    # Pausa con la batalla congelada de fondo: se sube de rango y se elige una de las tres mejoras
    fondoCongelado = win.copy()
    progreso.ascender()
    mejoras = ascensos.mejorasDisponibles(player, enemigo.VIDA_INICIAL, progreso.rango)
    inicio = pygame.time.get_ticks()
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ESCENA_SALIR
            if event.type == pygame.KEYDOWN and event.key in TECLAS_MEJORA:
                elegida = mejoras[TECLAS_MEJORA[event.key]]
                if elegida.disponible:
                    ascensos.aplicar(player, elegida.clave)
                    compensarPausa(pygame.time.get_ticks() - inicio)
                    return ESCENA_PARTIDA

        win.blit(fondoCongelado, (0, 0))
        win.blit(VELO_PAUSA, (0, 0))
        dibujarTextoCentrado("ASCENDIDO A " + progreso.nombreRango().upper(),
                             FUENTE_TITULO, 120, (245, 235, 200))
        dibujarTextoCentrado("Elige tu mejora", FUENTE_OPCION, 155, (215, 215, 215))
        y = 215
        for numero, mejora in enumerate(mejoras, start=1):
            #cada mejora ya trae escrito lo que hace, o por que no se puede pedir todavia
            color = (245, 245, 240) if mejora.disponible else (115, 115, 115)
            dibujarTextoCentrado("%d - %s" % (numero, mejora.nombre), FUENTE_OPCION, y, color)
            dibujarTextoCentrado(mejora.efecto, FUENTE_PEQUENA, y + 19, color)
            y += 55
        presentar()

# ###########################################  Bucle del juego  ####################################################
def partida():
    global balas, balasEnemigas, enemies, cadaveres, objetosEnSuelo, oleada
    global avisoObjeto, avisoObjetoMotivo, avisoObjetoInstante, record, recordBatido
    global granadasEnElAire, estallidos, sablazosEnElAire
    while True:
        clock.tick(FPS)
        # Si pulsamos lo de cerrar la ventana, se cierra. Con ESC se pausa
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ESCENA_SALIR
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return ESCENA_PAUSA
            #usar lo que se lleve en la mochila: es una pulsacion, no un mantener
            if event.type == pygame.KEYDOWN and atajoDePruebas(event.key):
                continue
            if event.type == pygame.KEYDOWN and event.key == TECLA_BAYONETA:
                player.estocada(enemies, sablazosEnElAire)
            if event.type == pygame.KEYDOWN and event.key in TECLAS_DASH:
                player.dashear()
            if event.type == pygame.KEYDOWN and event.key == TECLA_MOCHILA:
                usado = objetos.usar(player, pygame.time.get_ticks())
                if usado:
                    avisoObjeto = usado
                    avisoObjetoMotivo = hud.AVISO_USADO
                    avisoObjetoInstante = pygame.time.get_ticks()

        #balas: una sola pasada, cada bala impacta una vez y las listas se reconstruyen
        balas = colisiones.resolverBalas(balas, enemies, WINX, WINY)
        balasEnemigas = colisiones.resolverBalas(balasEnemigas, [player], WINX, WINY)
        #Enemigos

        #la escolta que pidan los jefes, antes de mover a nadie
        llamarEscoltaDeLosJefes()
        #el aura de los oficiales, antes de moverlos: pone a cada uno su velocidad de este frame
        aplicarMando(enemies)
        for enemy in enemies:
            enemy.disparar(balasEnemigas)
            enemy.lanzar(granadasEnElAire, player.rect.center)
            enemy.atacar(player, sablazosEnElAire)
            enemy.cargar(player)
            enemy.pathFinding(player.x,player.y)
            enemy.checkEstadoVida()
        enemies, caidos = colisiones.separarCaidos(enemies)
        cadaveres.extend(caidos)
        cadaveres = cadaveresVigentes(cadaveres)
        #lo que sueltan al caer, y lo que el jugador pisa o se le pasa
        ahora = pygame.time.get_ticks()
        for caido in caidos:
            soltado = objetos.sueltaDe(caido, ahora)
            if soltado:
                objetosEnSuelo.append(soltado)
        objetosEnSuelo, recogidos = objetos.recogerYCaducar(objetosEnSuelo, player, ahora)
        if recogidos:
            avisoObjeto = recogidos[-1]
            avisoObjetoMotivo = hud.AVISO_GUARDADO
            avisoObjetoInstante = ahora
        #cada tipo de frances vale lo suyo para el rango; las bajas se cuentan aparte
        progreso.apuntarBajas(len(caidos), sum(caido.PUNTOS for caido in caidos))

        #las granadas que tocan suelo revientan y hacen danio en area, y no distinguen:
        #el que este dentro del circulo lo paga, frances incluido. Con eso se puede jugar:
        #si te colocas bien, el granadero revienta a los suyos
        granadasEnElAire, nuevosEstallidos = granadas.resolver(
            granadasEnElAire, [player] + enemies, ahora)
        estallidos = granadas.limpiarEstallidos(estallidos + nuevosEstallidos, ahora)
        sablazosEnElAire = sablazos.limpiar(sablazosEnElAire, ahora)

        keys = pygame.key.get_pressed()
        #mientras dura el dash, el dash manda sobre las teclas de andar
        if not player.avanzarDash():
            player.caminar(keys)
        player.disparar(keys,balas)
        player.sufrirContacto(enemies)
        if MODO_PRUEBAS and inmuneDePruebas:
            player.vida = player.vidaMaxima
        llevarOleada(ahora)
        drawWindow()
        ##Muerte del jugador
        if(player.vida<=0):
            segundos = (pygame.time.get_ticks() - instanteInicioPartida) / 1000.0
            recordBatido, record = records.guardarSiEsMejor(progreso.bajas, progreso.rango,
                                                           segundos, oleada.numero)
            return ESCENA_GAME_OVER
        ##Ascenso: se sale a elegir mejora y se vuelve a la misma partida
        if progreso.tocaAscender():
            return ESCENA_ASCENSO

# Cada escena es una funcion que corre hasta que toca cambiar y devuelve la siguiente
ESCENAS = {ESCENA_MENU: menu,
           ESCENA_PARTIDA: partida,
           ESCENA_PAUSA: pausa,
           ESCENA_ASCENSO: ascenso,
           ESCENA_GAME_OVER: gameOver}

def main():
    escena = ESCENA_MENU
    while escena != ESCENA_SALIR:
        escena = ESCENAS[escena]()

main()
# ################################################   Fin   #####################################################
pygame.quit()
sys.exit()

#####################WORKING IN:
#3-barrita de vida
#4-mas tipos de enemigo
#5-puntuacion
