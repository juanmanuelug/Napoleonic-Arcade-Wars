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
from enemigo import (enemigo, enemigoDistancia, voltigeur, oficial, granadero,
                     puntoDeAparicion, cadaveresVigentes, aplicarMando)


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
#la oleada en curso y la calma entre una y otra
oleada = None
enCalma = False
instanteFinCalma = 0


def reiniciarPartida():
    # Deja el estado como recien empezada la batalla, para poder volver a jugar sin cerrar el juego
    global player, balas, balasEnemigas, enemies, cadaveres, objetosEnSuelo, progreso
    global granadasEnElAire, estallidos, sablazosEnElAire
    global avisoObjeto, avisoObjetoMotivo, avisoObjetoInstante
    global instanteInicioPartida, recordBatido
    global oleada, enCalma, instanteFinCalma
    ahora = pygame.time.get_ticks()
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
    oleada = oleadas.Oleada(oleadas.PRIMERA_OLEADA, ahora)
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
    hud.dibujarEfectos(win, player, ahora)
    hud.dibujarAvisoObjeto(win, WINX, avisoObjeto, avisoObjetoMotivo,
                           avisoObjetoInstante, ahora)
    hud.dibujarMochila(win, player, WINY)
    if enCalma:
        hud.dibujarAvisoOleada(win, WINX, oleada.numero, instanteFinCalma - ahora)
    # actualizacion de la pantalla
    presentar()

def entrarEnBatalla(tipo):
    # Entra por el borde, nunca encima del jugador
    x, y = puntoDeAparicion(player.x, player.y)
    if tipo == oleadas.OFICIAL:
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

        #el aura de los oficiales, antes de moverlos: pone a cada uno su velocidad de este frame
        aplicarMando(enemies)
        for enemy in enemies:
            enemy.disparar(balasEnemigas)
            enemy.lanzar(granadasEnElAire, player.rect.center)
            enemy.atacar(player.rect, sablazosEnElAire)
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
        player.caminar(keys)
        player.disparar(keys,balas)
        player.sufrirContacto(enemies)
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
