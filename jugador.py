import pygame
from proyectile import proyectil
from render import dibujar_anclado

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

# Caja del cuerpo del soldado: es la referencia a la que se anclan todos sus sprites (el de
# andar mide 20x36) y a la vez su caja de colision, para que la hitbox coincida con lo que se ve
ANCHO_CUERPO = 20
ALTO_CUERPO = 36
# Altura de la boca del mosquete respecto a la esquina superior de la caja del cuerpo
ALTURA_CANON = 21
# Milisegundos que se ve el sprite del fogonazo despues de disparar
DURACION_FOGONAZO = 180
# Milisegundos entre disparo y disparo
RECARGA = 1500
######Jugador################
class jugador(object):
    def __init__(self, x, y):
        #posicion (esquina superior izquierda de la caja del cuerpo)
        self.x = x
        self.y = y
        #velocidad
        self.vel = 3
        #orientacion
        self.mirando_izq = False
        #estado de movimiento
        self.caminando = False
        self.contadorCaminar = 0
        #recarga: el sello de tiempo se pone en el instante del disparo, no al acabar la recarga
        self.recarga = RECARGA
        self.instanteUltimoDisparo = pygame.time.get_ticks() - RECARGA
        #colision
        self.rect = pygame.Rect(x, y, ANCHO_CUERPO, ALTO_CUERPO)
        #Vida
        self.vida = 100

    # # Estado del arma

    def puedeDisparar(self, ahora):
        return ahora - self.instanteUltimoDisparo >= self.recarga

    def mostrandoFogonazo(self, ahora):
        return ahora - self.instanteUltimoDisparo < DURACION_FOGONAZO

    def xCanon(self):
        if self.mirando_izq:
            return self.x
        return self.x + ANCHO_CUERPO

    # #Metodo de dibujar al jugador
    # El sprite del fogonazo tiene prioridad sobre el de andar, asi que se ve el disparo
    # aunque estemos en movimiento

    def dibujar(self, win):
        ahora = pygame.time.get_ticks()
        if self.mostrandoFogonazo(ahora):
            imagen = Disparar_izq[1] if self.mirando_izq else Disparar_dch[1]
        elif self.caminando:
            secuencia = Andar_izq if self.mirando_izq else Andar_dch
            imagen = secuencia[self.contadorCaminar // 3]
            self.contadorCaminar = (self.contadorCaminar + 1) % 27
        else:
            imagen = Disparar_izq[0] if self.mirando_izq else Disparar_dch[0]
        dibujar_anclado(win, imagen, self.x, self.y, self.mirando_izq, ANCHO_CUERPO, ALTO_CUERPO)

    # #Metodo de caminar para el jugador

    def caminar(self, keys):
        avanceX = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        avanceY = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        self.caminando = avanceX != 0 or avanceY != 0
        if not self.caminando:
            self.contadorCaminar = 0
            return
        if avanceX < 0:
            self.mirando_izq = True
        elif avanceX > 0:
            self.mirando_izq = False
        #los limites usan el tamanio real del cuerpo, no una medida inventada
        self.x = min(max(0, self.x + avanceX * self.vel), WINX - ANCHO_CUERPO)
        self.y = min(max(0, self.y + avanceY * self.vel), WINY - ALTO_CUERPO)
        self.rect.topleft = (self.x, self.y)

    # #Metodo para disparar

    def disparar(self, keys, balas):
        if not keys[pygame.K_SPACE]:
            return
        ahora = pygame.time.get_ticks()
        if not self.puedeDisparar(ahora):
            return
        self.instanteUltimoDisparo = ahora
        sound_musket.play()
        apuntando = -1 if self.mirando_izq else 1
        balas.append(proyectil(self.xCanon(), self.y + ALTURA_CANON, apuntando))

    # # Metodo que comprueba la colision
    def checkColision(self,enemigos):
        for enemigo in enemigos:
            if(self.rect.colliderect(enemigo)):
                self.vida-=3.5
