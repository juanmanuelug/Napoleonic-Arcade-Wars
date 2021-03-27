import pygame
from proyectile import proyectil

pygame.init()

# ####################################### Constantes  ##################################################
WINX = 500
WINY = 500
###################Sonidos#############################
sound_musket = pygame.mixer.Sound('./sonido/musket_shot04.wav')
sound_musket.set_volume(0.2)
##############Soldados Ingleses################
Andar_izq = [pygame.image.load('./sprites/ingleses/soldado_ingles_izq_0.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_izq_1.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_izq_2.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_izq_3.png'),
             pygame.image.load('./sprites/ingleses/soldado_ingles_izq_4.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_izq_5.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_izq_6.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_izq_1.png'),
             pygame.image.load('./sprites/ingleses/soldado_ingles_izq_2.png')]
Andar_dch = [pygame.image.load('./sprites/ingleses/soldado_ingles_dch_0.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_dch_1.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_dch_2.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_dch_3.png'),
             pygame.image.load('./sprites/ingleses/soldado_ingles_dch_4.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_dch_5.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_dch_6.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_dch_1.png'),
             pygame.image.load('./sprites/ingleses/soldado_ingles_dch_2.png')]

Disparar_izq = [pygame.image.load('./sprites/ingleses/soldado_ingles_izq_disparar_1.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_izq_disparar.png')]
Disparar_dch = [pygame.image.load('./sprites/ingleses/soldado_ingles_dch_disparar_1.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_dch_disparar.png')]
######Jugador################
class jugador(object):
    def __init__(self, x, y, w, h, v, i, d, s,cont):
        #posicion
        self.x = x
        self.y = y
        #tamaño del jugador
        self.width = w
        self.height = h
        #velocidad
        self.vel = v
        #orientacion
        self.izq = i
        self.dch = d
        #estado de movimiento
        self.stop = s
        self.ContadorCaminar = cont
        #estado disparo
        self.disparo = False
        #recarga
        self.tiempo = pygame.time.get_ticks()
        self.recarga = 3000
        #colision/superficie
        self.surface = Disparar_dch[0].convert()
        self.rect = self.surface.get_rect(center =(x,y))
        #Vida
        self.vida=100

    # #Metodo de dibujar al jugador

    def dibujar(self, win):
        if self.ContadorCaminar + 1 >= 27:
            self.ContadorCaminar = 0

        if not self.stop:
            if self.izq:
                    #superficie de colision
                self.surface=Andar_izq[self.ContadorCaminar//3].convert()
                self.rect=self.surface.get_rect(center = (self.x,self.y))
                    #dibujado del sprite
                win.blit(Andar_izq[self.ContadorCaminar//3], (self.x, self.y))
                self.ContadorCaminar += 1
            else:
                    #superficie de colision
                self.surface=Andar_dch[self.ContadorCaminar//3].convert()
                self.rect=self.surface.get_rect(center = (self.x,self.y))
                    #dibujado del sprite
                win.blit(Andar_dch[self.ContadorCaminar//3], (self.x, self.y))
                self.ContadorCaminar += 1
        else:
            if self.dch:
                if self.disparo:
                    #superficie de colision
                    self.surface=Disparar_dch[1].convert()
                    self.rect=self.surface.get_rect(center = (self.x,self.y))
                    #dibujado del sprite
                    win.blit(Disparar_dch[1], (self.x, self.y))
                else:
                    #superficie de colision
                    self.surface=Disparar_dch[0].convert()
                    self.rect=self.surface.get_rect(center = (self.x,self.y))
                    #dibujado del sprite
                    win.blit(Disparar_dch[0], (self.x, self.y))
            else:
                if self.disparo:
                    #superficie de colision
                    self.surface=Disparar_izq[1].convert()
                    self.rect=self.surface.get_rect(center = (self.x,self.y))
                    #dibujado del sprite
                    win.blit(Disparar_izq[1], (self.x, self.y))
                else:
                    self.surface=Disparar_izq[0].convert()
                    self.rect=self.surface.get_rect(center = (self.x,self.y))
                    #dibujado del sprite
                    win.blit(Disparar_izq[0], (self.x, self.y))

    # #Metodo de caminar para el jugador

    def caminar(self, keys):
        if keys[pygame.K_UP] and keys[pygame.K_RIGHT] and self.x < WINX - self.width - self.vel and self.y > self.vel:
            self.x += self.vel
            self.dch = True
            self.stop = False
            self.izq = False
            self.y -= self.vel
        elif keys[pygame.K_UP] and keys[pygame.K_LEFT] and self.x > self.vel and self.y > self.vel:
            self.x -= self.vel
            self.izq = True
            self.stop = False
            self.dch = False
            self.y -= self.vel
        elif keys[pygame.K_DOWN] and keys[pygame.K_RIGHT] and self.x < WINX - self.width - self.vel and self.y < WINY - self.height - self.vel:
            self.x += self.vel
            self.dch = True
            self.stop = False
            self.izq = False
            self.y += self.vel
        elif keys[pygame.K_DOWN] and keys[pygame.K_LEFT] and self.x > self.vel and self.y < WINY - self.height - self.vel:
            self.x -= self.vel
            self.izq = True
            self.stop = False
            self.dch = False
            self.y += self.vel
        elif keys[pygame.K_LEFT] and self.x > self.vel:
            self.x -= self.vel
            self.izq = True
            self.stop = False
            self.dch = False
        elif keys[pygame.K_RIGHT] and self.x < WINX - self.width - self.vel:
            self.x += self.vel
            self.dch = True
            self.stop = False
            self.izq = False
        elif keys[pygame.K_DOWN] and self.y < WINY - self.height - self.vel:
            self.y += self.vel
            self.stop = False
            if not self.dch and not self.izq:
                self.dch = True
        elif keys[pygame.K_UP] and self.y > self.vel:
            self.y -= self.vel
            self.stop = False
            if not self.dch and not self.izq:
                self.dch = True
        else:
            self.stop = True
            self.ContadorCaminar = 0

    # #Metodo para disparar
    def disparar(self,keys,bullets):
        if self.izq:
            apuntando = -1
        else:
            apuntando = 1
        if keys[pygame.K_SPACE]:
            if self.disparo:
                #recarga del arma para poder volver a disparar
                ahora = pygame.time.get_ticks()
                if ahora - self.tiempo >= self.recarga:
                    self.tiempo = ahora
                    self.disparo = False
            else:
                sound_musket.play()
                self.disparo = True
                bullets.append(proyectil(round(self.x + self.width //2.5), round(self.y + self.height //2.5 ), apuntando))
        else:
            ahora = pygame.time.get_ticks()
            if ahora - self.tiempo >= self.recarga:
                self.tiempo = ahora
                self.disparo = False

    # # Método que comprueba la colision
    def checkColision(self,enemigos):
        for enemigo in enemigos:
            if(self.rect.colliderect(enemigo)):
                self.vida-=1.0
