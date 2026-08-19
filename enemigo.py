import pygame
from proyectile import proyectil
from render import dibujar_anclado

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

Andar_izq_Fr_cuerpo = [pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_2.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_3.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_4.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_5.png'),
             pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_6.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_2.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_3.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_4.png'),
             pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_5.png')]
Andar_dch_Fr_cuerpo = [pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_2.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_3.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_4.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_5.png'),
             pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_6.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_2.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_3.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_4.png'),
             pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_5.png')]

cadaverImg = pygame.image.load('./sprites/franceses/cadaver.png')
cadaverOficialImg= pygame.image.load('./sprites/franceses/cadaverOficialImg.png')
# #######################################   Clases   ##################################################

#######Enemigos###############
##Enemigo BASE
class enemigo(object):
    #Lienzo de referencia de sus sprites (los de cuerpo a cuerpo miden 30x32) y caja del
    #cuerpo dentro de ese lienzo: excluye la bayoneta, que sobresale por el lado al que mira
    ANCHO_REFERENCIA = 30
    ALTO_REFERENCIA = 32
    CUERPO_IZQ = pygame.Rect(6, 2, 21, 30)
    CUERPO_DCH = pygame.Rect(3, 2, 21, 30)
    #Altura de la boca del mosquete respecto a la esquina de la caja del cuerpo
    ALTURA_CANON = 21

    def __init__(self,x,y,xObjectiv,yObjectiv):
        self.x=x
        self.y=y
        self.vel=1
        #Para controlar el sprite que va apareciendo cuando camina
        self.contadorCaminar=0
        #Orientacion donde mira
        self.dch=False
        self.izq=True
        self.stop=True
        #Objetivo al que se dirige
        self.xObjectiv=xObjectiv
        self.yObjectiv=yObjectiv
        self.contadorPath=0
        #superficie de colision
        self.rect = self.CUERPO_IZQ.move(x, y)
        #vida
        self.vida=75
        self.vivo=True

    def actualizarRect(self):
        #la caja de colision sigue al cuerpo dibujado, no al lienzo completo del sprite
        cuerpo = self.CUERPO_IZQ if self.izq else self.CUERPO_DCH
        self.rect = cuerpo.move(self.x, self.y)

    def xCanon(self):
        if self.izq:
            return self.rect.left
        return self.rect.right

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
        self.actualizarRect()

    def sprite(self):
        #sprite que toca este frame; la clase hija anade el disparo
        if not self.stop:
            secuencia = Andar_izq_Fr_cuerpo if self.izq else Andar_dch_Fr_cuerpo
            imagen = secuencia[self.contadorCaminar // 3]
            self.contadorCaminar = (self.contadorCaminar + 1) % 27
            return imagen
        return Andar_izq_Fr_cuerpo[0] if self.izq else Andar_dch_Fr_cuerpo[0]

    def dibujarEnemigo(self, win):
        dibujar_anclado(win, self.sprite(), self.x, self.y, self.izq,
                        self.ANCHO_REFERENCIA, self.ALTO_REFERENCIA)

    def checkColision(self,bullets):
        for bullet in bullets:
            if(self.rect.colliderect(bullet)):
                self.vida-= bullet.danio

    def checkEstadoVida(self):
        if(self.vida<=0):
            self.vivo=False

    def disparar(self,bullets):
        #solo por herencia
        pass

    def dibujarCadaver(self,win):
        win.blit(cadaverOficialImg, (self.x, self.y))

##Enemigo a distancia
class enemigoDistancia(enemigo):
    #sus sprites de andar miden 20x36, igual que los del jugador
    ANCHO_REFERENCIA = 20
    ALTO_REFERENCIA = 36
    CUERPO_IZQ = pygame.Rect(0, 0, 20, 36)
    CUERPO_DCH = pygame.Rect(0, 0, 20, 36)

    def __init__(self,x,y,xObjectiv,yObjectiv):
        enemigo.__init__(self,x,y,xObjectiv,yObjectiv)
        #para disparar
        self.disparo = False
        #recarga
        self.tiempo = pygame.time.get_ticks()
        self.recarga = 1500

    def pathFinding(self,xObjectiv,yObjectiv):
        self.xObjectiv=xObjectiv
        self.yObjectiv=yObjectiv
        if(self.yObjectiv!=self.y):
            if(self.xObjectiv < self.x):
                self.dch=False
                self.izq=True
                self.stop=False
            else:
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
        self.actualizarRect()

    def sprite(self):
        if not self.stop:
            secuencia = Andar_izq_Fr if self.izq else Andar_dch_Fr
            imagen = secuencia[self.contadorCaminar // 3]
            self.contadorCaminar = (self.contadorCaminar + 1) % 27
            return imagen
        secuencia = Disparar_izq_Fr if self.izq else Disparar_dch_Fr
        return secuencia[1] if self.disparo else secuencia[0]

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
                bullets.append(proyectil(self.xCanon(), self.y + self.ALTURA_CANON, apuntando))
        else:
            ahora = pygame.time.get_ticks()
            if ahora - self.tiempo >= self.recarga:
                self.tiempo = ahora
                self.disparo = False


    def dibujarCadaver(self,win):
        win.blit(cadaverImg, (self.x, self.y))
