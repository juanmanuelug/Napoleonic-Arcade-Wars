import pygame
from proyectile import proyectil

pygame.init()
# ####################################### Constantes  ##################################################
WINX = 500
WINY = 500
# #######################################   Sonidos  ###################################################
sound_musket = pygame.mixer.Sound('./sonido/musket_shot04.wav')
sound_musket.set_volume(0.2)
##############Soldados Franceses#################
Andar_izq_Fr = [pygame.image.load('./sprites/franceses/soldado_fr_izq_0.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_1.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_2.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_3.png'),
             pygame.image.load('./sprites/franceses/soldado_fr_izq_4.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_5.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_6.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_1.png'),
             pygame.image.load('./sprites/franceses/soldado_fr_izq_2.png')]
Andar_dch_Fr = [pygame.image.load('./sprites/franceses/soldado_fr_dch_0.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_1.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_2.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_3.png'),
             pygame.image.load('./sprites/franceses/soldado_fr_dch_4.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_5.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_6.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_1.png'),
             pygame.image.load('./sprites/franceses/soldado_fr_dch_2.png')]

Disparar_izq_Fr = [pygame.image.load('./sprites/franceses/soldado_fr_izq_disparar_1.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_disparar.png')]
Disparar_dch_Fr = [pygame.image.load('./sprites/franceses/soldado_fr_dch_disparar_1.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_disparar.png')]

# #######################################   Clases   ##################################################

#######Enemigos###############
class enemigo(object):
    def __init__(self,x,y,xObjectiv,yObjectiv):
        self.x=x
        self.y=y
        self.vel=2
        #para disparar
        self.disparo = False
        #recarga
        self.tiempo = pygame.time.get_ticks()
        self.recarga = 3000
        #Para controlar el sprite que va apareciendo cuando camina
        self.ContadorCaminar=0
        #Orientacion donde mira
        self.dch=False
        self.izq=True
        self.stop=True
        #Objetivo al que se dirige
        self.xObjectiv=xObjectiv
        self.yObjectiv=yObjectiv
        self.contadorPath=0
        #superficie de colision
        self.surface=Disparar_dch_Fr[0].convert()
        self.rect = self.surface.get_rect(center =(x,y))
        #vida
        self.vida=75
        self.vivo=True

    def pathFinding(self,xObjectiv,yObjectiv):
        self.xObjectiv=xObjectiv
        self.yObjectiv=yObjectiv
        if(self.yObjectiv!=self.y or self.xObjectiv!=self.x):
            if(self.xObjectiv < self.x):
                self.x-=self.vel
                self.dch=False
                self.izq=True
                self.stop=False
            else:
                self.x+=self.vel
                self.dch=True
                self.izq=False
                self.stop=False
            if(self.yObjectiv<self.y):
                self.y-=self.vel
                self.stop=False
            else:
                self.y+=self.vel
                self.stop=False
        else:
            self.stop=True


    def dibujarEnemigo(self, win):
        if self.ContadorCaminar + 1 >= 27:
            self.ContadorCaminar = 0

        if not self.stop:
            if self.izq:
                    #superficie de colision
                self.surface=Andar_izq_Fr[self.ContadorCaminar//3].convert()
                self.rect=self.surface.get_rect(center = (self.x,self.y))
                    #dibujado del sprite
                win.blit(Andar_izq_Fr[self.ContadorCaminar//3], (self.x, self.y))
                self.ContadorCaminar += 1
            else:
                    #superficie de colision
                self.surface=Andar_dch_Fr[self.ContadorCaminar//3].convert()
                self.rect=self.surface.get_rect(center = (self.x,self.y))
                    #dibujado del sprite
                win.blit(Andar_dch_Fr[self.ContadorCaminar//3], (self.x, self.y))
                self.ContadorCaminar += 1
        else:
            if self.dch:
                if self.disparo:
                    #superficie de colision
                    self.surface=Disparar_dch_Fr[1].convert()
                    self.rect=self.surface.get_rect(center = (self.x,self.y))
                    #dibujado del sprite
                    win.blit(Disparar_dch_Fr[1], (self.x, self.y))
                else:
                    #superficie de colision
                    self.surface=Disparar_dch_Fr[0].convert()
                    self.rect=self.surface.get_rect(center = (self.x,self.y))
                    #dibujado del sprite
                    win.blit(Disparar_dch_Fr[0], (self.x, self.y))
            else:
                if self.disparo:
                    #superficie de colision
                    self.surface=Disparar_izq_Fr[1].convert()
                    self.rect=self.surface.get_rect(center = (self.x,self.y))
                    #dibujado del sprite
                    win.blit(Disparar_izq_Fr[1], (self.x, self.y))
                else:
                    self.surface=Disparar_izq_Fr[0].convert()
                    self.rect=self.surface.get_rect(center = (self.x,self.y))
                    #dibujado del sprite
                    win.blit(Disparar_izq_Fr[0], (self.x, self.y))

    def checkColision(self,bullets):
        for bullet in bullets:
            if(self.rect.colliderect(bullet)):
                self.vida-= bullet.danio

    def checkEstadoVida(self):
        if(self.vida<=0):
            self.vivo=False

    def disparar(self,bullets):
        if self.izq:
            apuntando = -1
        else:
            apuntando = 1
        if self.y==self.yObjectiv:
            if self.disparo:
                #recarga del arma para poder volver a disparar
                ahora = pygame.time.get_ticks()
                if ahora - self.tiempo >= self.recarga:
                    self.tiempo = ahora
                    self.disparo = False
            else:
                sound_musket.play()
                self.disparo = True
                bullets.append(proyectil(round(self.x + 20//2.5), round(self.y + 20//2.5 ), apuntando))
        else:
            ahora = pygame.time.get_ticks()
            if ahora - self.tiempo >= self.recarga:
                self.tiempo = ahora
                self.disparo = False


