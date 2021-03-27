import pygame
import random
import time

from jugador import jugador
from enemigo import enemigo
from cadaver import cadaver

pygame.init()
# ####################################### Constantes  ##################################################
WINX = 500
WINY = 500
# #######################################   Sonidos  ###################################################
sound_intro = pygame.mixer.music.load('./music/marchaBritanica.wav')
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
    # actualización de la pantalla
    pygame.display.update()

def spawnEnemies(enemies):
    global ultimoTiempo
    x = random.randint(0,500)
    y = random.randint(0,500)
    tiempo = time.perf_counter()
    if tiempo - ultimoTiempo > 10:
        enemies.append(enemigo(x,y,player.x,player.y))
        ultimoTiempo = time.perf_counter()



# ########################################### Intro ################################################################
def text_objects(text, font):
    textSurface = font.render(text, True, (0,0,0))
    return textSurface, textSurface.get_rect()

def game_intro():

    intro = True
    while intro:
        pygame.mixer.music.play()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        win.blit(menu_images, (0, 0))
        largeText = pygame.font.Font('freesansbold.ttf',25)
        TextSurf, TextRect = text_objects("La Batalla de Waterloo", largeText)
        TextRect.center = ((WINX/2),(50/2))
        win.blit(TextSurf, TextRect)
        pygame.display.update()
        clock.tick(float(0.1))
        intro =False
    pygame.mixer.music.stop()

def game_end():

    end = True
    while end:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        win.blit(derrota_images, (0, 0))
        largeText = pygame.font.Font('freesansbold.ttf',50)
        TextSurf, TextRect = text_objects("Has Muerto", largeText)
        TextRect.center = ((WINX/2),(50/2))
        win.blit(TextSurf, TextRect)
        pygame.display.update()
        clock.tick(float(0.1))
        end =False

# ###########################################  Bucle del juego  ####################################################

player = jugador(250, 250, 21, 35, 4, False, False, True, 0)
balas = []
balasEnemigas = []
#enemy = enemigo(0,0,player.x,player.y)
enemies = []
cadaveres = []
ultimoTiempo = time.perf_counter()
def main():
    run = True
    game_intro()
    while run:
        clock.tick(30)
        # Si pulsamos lo de cerrar pestaña, se cierra
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        #balas
        for bala in balas:
            for enemy in enemies:
                bala.checkColission(enemy)
                enemy.checkColision(balas)
            if (bala.colision == False and bala.x < WINX and bala.x > 0):
                bala.x += bala.vel
            else:
                balas.pop(balas.index(bala))

        for balaE in balasEnemigas:
            balaE.checkColission(player)
            if (balaE.colision == False and balaE.x < WINX and balaE.x > 0):
                balaE.x += balaE.vel
            else:
                balasEnemigas.pop(balasEnemigas.index(balaE))
        #Enemigos

        for enemy in enemies:
            enemy.disparar(balasEnemigas)
            enemy.pathFinding(player.x,player.y)
            enemy.checkEstadoVida()
            if(enemy.vivo==False):
                cadaveres.append(cadaver(enemy.x,enemy.y))
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
            game_end()
            quit()

main()
# ################################################   Fin   #####################################################
pygame.quit()
quit()

#####################WORKING IN:
#1-Spawn Enemigos delay
#2-Menu
#3-barrita de vida
#4-más tipos de enemigo
#5-puntuacion
