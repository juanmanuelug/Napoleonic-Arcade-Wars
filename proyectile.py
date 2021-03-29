import pygame

pygame.init()

balaImg = pygame.image.load('./sprites/bala.png')
#######Proyectiles############
class proyectil(object):
    def __init__(self, x, y, lado):
        #posicion
        self.x = x
        self.y = y
        #direccion hacia donde va
        self.lado = lado
        self.vel = lado * 8
        #superficie de colision
        self.surface = balaImg.convert()
        self.rect = self.surface.get_rect(center =(x,y))
        #danio bala
        self.danio=25
        self.colision=False


    def dibujar_bala(self, win):
        #superficie de colision
        self.surface = balaImg.convert()
        self.rect = self.surface.get_rect(center = (self.x,self.y))
        #dibujado
        win.blit(balaImg, (self.x, self.y))

    def checkColission(self,personaje):
        if(self.rect.colliderect(personaje)):
            self.colision=True
