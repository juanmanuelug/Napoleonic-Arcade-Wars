import pygame
import sys
import time

import colisiones
import hud
from jugador import jugador
from enemigo import enemigo, enemigoDistancia, puntoDeAparicion, cadaveresVigentes


pygame.init()
# ####################################### Constantes  ##################################################
WINX = 500
WINY = 500
FPS = 30
# Cada cuanto entra en batalla un enemigo de cada tipo
SEGUNDOS_ENTRE_APARICIONES = 7
SEGUNDOS_ENTRE_APARICIONES_DISTANCIA = 13
# Escenas del juego
ESCENA_MENU = "menu"
ESCENA_PARTIDA = "partida"
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
win = pygame.display.set_mode((WINX, WINY))
# ######################################   Nombre de la ventana       ########################################
pygame.display.set_caption("Waterloo")
# ######################################   Fuentes (una sola vez, no en cada frame)  ###########################
FUENTE_TITULO = pygame.font.Font('freesansbold.ttf', 25)
FUENTE_OPCION = pygame.font.Font('freesansbold.ttf', 18)
FUENTE_DERROTA = pygame.font.Font('freesansbold.ttf', 50)
# #####################################   Estado de la partida   ##############################################
player = None
balas = []
balasEnemigas = []
enemies = []
cadaveres = []
puntuacion = 0
ultimoTiempo = 0.0
ultimoTiempoDistancia = 0.0


def reiniciarPartida():
    # Deja el estado como recien empezada la batalla, para poder volver a jugar sin cerrar el juego
    global player, balas, balasEnemigas, enemies, cadaveres, puntuacion
    global ultimoTiempo, ultimoTiempoDistancia
    player = jugador(250, 250)
    balas = []
    balasEnemigas = []
    enemies = []
    cadaveres = []
    puntuacion = 0
    ultimoTiempo = time.perf_counter()
    ultimoTiempoDistancia = time.perf_counter()

# #######################################   Funciones    ######################################################

def drawWindow():
    # fondo de la pantalla
    win.blit(bg, (0, 0))
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
    # indicadores por encima de la batalla
    hud.dibujarPanelJugador(win, player, puntuacion, WINX)
    # actualizacion de la pantalla
    pygame.display.update()

def spawnEnemies(enemies):
    # Cada tipo entra por su propio punto del borde, nunca encima del jugador
    global ultimoTiempo, ultimoTiempoDistancia
    tiempo = time.perf_counter()
    if tiempo - ultimoTiempo > SEGUNDOS_ENTRE_APARICIONES:
        x, y = puntoDeAparicion(player.x, player.y)
        enemies.append(enemigo(x,y,player.x,player.y))
        ultimoTiempo = tiempo
    if tiempo - ultimoTiempoDistancia > SEGUNDOS_ENTRE_APARICIONES_DISTANCIA:
        x, y = puntoDeAparicion(player.x, player.y)
        enemies.append(enemigoDistancia(x,y,player.x,player.y))
        ultimoTiempoDistancia = tiempo



# ########################################### Textos #############################################################
def dibujarTextoCentrado(texto, fuente, y, color=(0,0,0)):
    superficie = fuente.render(texto, True, color)
    win.blit(superficie, superficie.get_rect(center=(WINX/2, y)))

def dibujarBandaOpciones():
    # Banda oscura al pie para que las opciones se lean sobre cualquier imagen
    banda = pygame.Surface((WINX, 62), pygame.SRCALPHA)
    banda.fill((0,0,0,160))
    win.blit(banda, (0, WINY - 72))

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
        dibujarTextoCentrado("La Batalla de Waterloo", FUENTE_TITULO, 25)
        dibujarBandaOpciones()
        dibujarTextoCentrado("ENTER - A la batalla", FUENTE_OPCION, WINY - 55, (255,255,255))
        dibujarTextoCentrado("ESC - Salir", FUENTE_OPCION, WINY - 28, (255,255,255))
        pygame.display.update()

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
        dibujarTextoCentrado("Has Muerto", FUENTE_DERROTA, 45)
        dibujarTextoCentrado("Franceses abatidos: " + str(puntuacion), FUENTE_OPCION, 85)
        dibujarBandaOpciones()
        dibujarTextoCentrado("ENTER - Volver al menu", FUENTE_OPCION, WINY - 55, (255,255,255))
        dibujarTextoCentrado("ESC - Salir", FUENTE_OPCION, WINY - 28, (255,255,255))
        pygame.display.update()

# ###########################################  Bucle del juego  ####################################################
def partida():
    global balas, balasEnemigas, enemies, cadaveres, puntuacion
    while True:
        clock.tick(FPS)
        # Si pulsamos lo de cerrar la ventana, se cierra. Con ESC se vuelve al menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ESCENA_SALIR
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return ESCENA_MENU

        #balas: una sola pasada, cada bala impacta una vez y las listas se reconstruyen
        balas = colisiones.resolverBalas(balas, enemies, WINX)
        balasEnemigas = colisiones.resolverBalas(balasEnemigas, [player], WINX)
        #Enemigos

        for enemy in enemies:
            enemy.disparar(balasEnemigas)
            enemy.pathFinding(player.x,player.y)
            enemy.checkEstadoVida()
        enemies, caidos = colisiones.separarCaidos(enemies)
        cadaveres.extend(caidos)
        cadaveres = cadaveresVigentes(cadaveres)
        puntuacion += len(caidos)

        keys = pygame.key.get_pressed()
        player.caminar(keys)
        player.disparar(keys,balas)
        player.sufrirContacto(enemies)
        spawnEnemies(enemies)
        drawWindow()
        ##Muerte del jugador
        if(player.vida<=0):
            return ESCENA_GAME_OVER

def main():
    escena = ESCENA_MENU
    while escena != ESCENA_SALIR:
        if escena == ESCENA_MENU:
            escena = menu()
        elif escena == ESCENA_PARTIDA:
            escena = partida()
        else:
            escena = gameOver()

main()
# ################################################   Fin   #####################################################
pygame.quit()
sys.exit()

#####################WORKING IN:
#3-barrita de vida
#4-mas tipos de enemigo
#5-puntuacion
