import pygame

pygame.init()

balaImg = pygame.image.load('./sprites/bala.png')
# El lienzo de la bala mide 25x26 pero la bola visible son solo 4x4 pixeles. La caja de
# colision es la bola, no el lienzo, para que no se acierte con el vacio transparente.
CONTENIDO_BALA = balaImg.get_bounding_rect()
#######Proyectiles############
class proyectil(object):
    def __init__(self, x_canon, y_canon, lado):
        # (x_canon, y_canon) es el punto por el que sale la bala; self.x/self.y son la esquina
        # del lienzo, desplazada para que la bola visible caiga justo en la boca del mosquete
        self.x = x_canon - CONTENIDO_BALA.centerx
        self.y = y_canon - CONTENIDO_BALA.centery
        #direccion hacia donde va
        self.lado = lado
        self.vel = lado * 8
        #superficie de colision
        self.rect = CONTENIDO_BALA.move(self.x, self.y)
        #danio bala
        self.danio=25

    def mover(self):
        self.x += self.vel
        self.rect = CONTENIDO_BALA.move(self.x, self.y)

    def en_pantalla(self, ancho):
        return self.rect.right > 0 and self.rect.left < ancho

    def dibujar_bala(self, win):
        win.blit(balaImg, (self.x, self.y))
