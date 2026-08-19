import pygame
import random
import sys
import time

from jugador import jugador
from enemigo import enemigo, enemigoDistancia


pygame.init()
# ####################################### Constantes  ##################################################
WINX = 500
WINY = 500
FPS = 30
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
ultimoTiempo = 0.0
ultimoTiempoDistancia = 0.0


def reiniciarPartida():
    # Deja el estado como recien empezada la batalla, para poder volver a jugar sin cerrar el juego
    global player, balas, balasEnemigas, enemies, cadaveres
    global ultimoTiempo, ultimoTiempoDistancia
    player = jugador(250, 250)
    balas = []
    balasEnemigas = []
    enemies = []
    cadaveres = []
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
    #dibujar balas
    for bala in balas:
        bala.dibujar_bala(win)

    for balaE in balasEnemigas:
        balaE.dibujar_bala(win)
    for cadaver in cadaveres:
        cadaver.dibujarCadaver(win)
    # actualizacion de la pantalla
    pygame.display.update()

def spawnEnemies(enemies):
    global ultimoTiempo, ultimoTiempoDistancia
    x = random.randint(0,500)
    y = random.randint(0,500)
    tiempo = time.perf_counter()
    if tiempo - ultimoTiempo > 7:
        enemies.append(enemigo(x,y,player.x,player.y))
        ultimoTiempo = time.perf_counter()
    if tiempo - ultimoTiempoDistancia > 13:
        enemies.append(enemigoDistancia(x,y,player.x,player.y))
        ultimoTiempoDistancia = time.perf_counter()



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
        dibujarBandaOpciones()
        dibujarTextoCentrado("ENTER - Volver al menu", FUENTE_OPCION, WINY - 55, (255,255,255))
        dibujarTextoCentrado("ESC - Salir", FUENTE_OPCION, WINY - 28, (255,255,255))
        pygame.display.update()

# ###########################################  Bucle del juego  ####################################################
def partida():
    while True:
        clock.tick(FPS)
        # Si pulsamos lo de cerrar la ventana, se cierra. Con ESC se vuelve al menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ESCENA_SALIR
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return ESCENA_MENU

        #balas
        for bala in balas:
            for enemy in enemies:
                bala.checkColission(enemy)
                enemy.checkColision(balas)
            if (bala.colision == False and bala.en_pantalla(WINX)):
                bala.mover()
            else:
                balas.pop(balas.index(bala))

        for balaE in balasEnemigas:
            balaE.checkColission(player)
            if (balaE.colision == False and balaE.en_pantalla(WINX)):
                balaE.mover()
            else:
                balasEnemigas.pop(balasEnemigas.index(balaE))
        #Enemigos

        for enemy in enemies:
            enemy.disparar(balasEnemigas)
            enemy.pathFinding(player.x,player.y)
            enemy.checkEstadoVida()
            if(enemy.vivo==False):
                cadaveres.append(enemy)
                enemies.pop(enemies.index(enemy))


        keys = pygame.key.get_pressed()
        player.caminar(keys)
        player.disparar(keys,balas)
        player.checkColision(enemies)
        player.checkColision(balasEnemigas)
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
