import pygame

pygame.init()

cadaverImg = pygame.image.load('./sprites/franceses/cadaver.png')
#######Cadaver################
class cadaver(object):
    def __init__(self,x,y):
        self.x=x
        self.y=y

    def dibujarCadaver(self,win):
        win.blit(cadaverImg, (self.x, self.y))
