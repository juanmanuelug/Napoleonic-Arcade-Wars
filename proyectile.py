import pygame

pygame.init()

balaImg = pygame.image.load('./sprites/bala.png')
# El lienzo de la bala mide 25x26 pero la bola visible son solo 4x4 pixeles. La caja de
# colision es la bola, no el lienzo, para que no se acierte con el vacio transparente.
CONTENIDO_BALA = balaImg.get_bounding_rect()
# Danio de una bala corriente. El jugador puede llevar mas si ha ascendido
DANIO_BALA = 25
# Pixeles que avanza una bala de mosquete por frame
VELOCIDAD_BALA = 8
#######Proyectiles############
class proyectil(object):
    def __init__(self, x_canon, y_canon, lado, danio=DANIO_BALA, avanceX=None, avanceY=0.0):
        # (x_canon, y_canon) es el punto por el que sale la bala; self.x/self.y son la esquina
        # del lienzo, desplazada para que la bola visible caiga justo en la boca del mosquete
        self.x = float(x_canon - CONTENIDO_BALA.centerx)
        self.y = float(y_canon - CONTENIDO_BALA.centery)
        #direccion hacia donde mira quien dispara: -1 izquierda, 1 derecha
        self.lado = lado
        #vector de avance por frame. Por defecto horizontal, que es un disparo de mosquete,
        #pero se puede dar cualquier otro (granadas con arco, tiros en diagonal...)
        self.avanceX = lado * VELOCIDAD_BALA if avanceX is None else float(avanceX)
        self.avanceY = float(avanceY)
        #superficie de colision
        self.rect = CONTENIDO_BALA.move(round(self.x), round(self.y))
        #danio bala
        self.danio=danio

    def mover(self):
        self.x += self.avanceX
        self.y += self.avanceY
        self.rect = CONTENIDO_BALA.move(round(self.x), round(self.y))

    def en_pantalla(self, ancho, alto):
        return (self.rect.right > 0 and self.rect.left < ancho
                and self.rect.bottom > 0 and self.rect.top < alto)

    def dibujar_bala(self, win):
        win.blit(balaImg, (round(self.x), round(self.y)))
