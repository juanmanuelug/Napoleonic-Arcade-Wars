import pygame
import random
from proyectile import proyectil
from render import dibujar_anclado

pygame.init()
# ####################################### Constantes  ##################################################
WINX = 500
WINY = 500
# Milisegundos entre disparo y disparo de un tirador, y lo que se le ve el fogonazo
RECARGA_ENEMIGO = 1500
DURACION_FOGONAZO = 180
# Margen de alineacion vertical con el que un tirador se da por encarado al jugador. Exigir la
# misma y exacta hacia que casi nunca disparasen, porque el jugador se mueve de 3 en 3 pixeles
TOLERANCIA_PUNTERIA = 6
# Distancia a la que un tirador se planta para disparar en vez de seguir acercandose
DISTANCIA_DE_TIRO = 180
# Los cadaveres desaparecen al cabo de un rato y nunca hay mas de MAX_CADAVERES en pantalla
DURACION_CADAVER = 12000
MAX_CADAVERES = 20
# Los enemigos aparecen por fuera del borde y nunca encima del jugador
MARGEN_APARICION = 40
DISTANCIA_MINIMA_APARICION = 150
INTENTOS_APARICION = 8
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
# #######################################   Funciones   ###############################################

def _puntoEnElBorde():
    #un punto justo por fuera de uno de los cuatro bordes
    lado = random.choice(('izquierda', 'derecha', 'arriba', 'abajo'))
    if lado == 'izquierda':
        return -MARGEN_APARICION, random.randint(0, WINY)
    if lado == 'derecha':
        return WINX + MARGEN_APARICION, random.randint(0, WINY)
    if lado == 'arriba':
        return random.randint(0, WINX), -MARGEN_APARICION
    return random.randint(0, WINX), WINY + MARGEN_APARICION


def _distanciaAlCuadrado(punto, otro):
    return (punto[0] - otro[0]) ** 2 + (punto[1] - otro[1]) ** 2


def puntoDeAparicion(xObjetivo, yObjetivo):
    """Un punto del borde por el que entrar en batalla, lo bastante lejos del jugador."""
    objetivo = (xObjetivo, yObjetivo)
    candidatos = [_puntoEnElBorde() for _ in range(INTENTOS_APARICION)]
    lejanos = [punto for punto in candidatos
               if _distanciaAlCuadrado(punto, objetivo) >= DISTANCIA_MINIMA_APARICION ** 2]
    if lejanos:
        return random.choice(lejanos)
    #si el jugador esta pegado a un borde puede que ninguno valga: se coge el mas lejano
    return max(candidatos, key=lambda punto: _distanciaAlCuadrado(punto, objetivo))


def cadaveresVigentes(cadaveres):
    """Quita los cadaveres que ya han cumplido su tiempo y limita cuantos se acumulan."""
    ahora = pygame.time.get_ticks()
    vigentes = [cadaver for cadaver in cadaveres
                if ahora - cadaver.instanteMuerte < DURACION_CADAVER]
    return vigentes[-MAX_CADAVERES:]

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
    #Vida con la que aparece
    VIDA_INICIAL = 75

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
        self.vida=self.VIDA_INICIAL
        self.vidaMaxima=self.VIDA_INICIAL
        self.vivo=True
        #cuando cae, para que el cadaver no se quede en el campo para siempre
        self.instanteMuerte=0

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

    def recibirImpacto(self,danio):
        #el reparto de danio lo hace colisiones.resolverBalas, aqui solo se apunta
        self.vida-= danio

    def checkEstadoVida(self):
        if(self.vida<=0 and self.vivo):
            self.vivo=False
            self.instanteMuerte=pygame.time.get_ticks()

    def disparar(self,bullets):
        #solo por herencia
        pass

    def dibujarCadaver(self,win):
        #anclado como el resto de sprites, para que caiga donde estaban sus pies
        dibujar_anclado(win, cadaverOficialImg, self.x, self.y, self.izq,
                        self.ANCHO_REFERENCIA, self.ALTO_REFERENCIA)

##Enemigo a distancia
class enemigoDistancia(enemigo):
    #sus sprites de andar miden 20x36, igual que los del jugador
    ANCHO_REFERENCIA = 20
    ALTO_REFERENCIA = 36
    CUERPO_IZQ = pygame.Rect(0, 0, 20, 36)
    CUERPO_DCH = pygame.Rect(0, 0, 20, 36)

    def __init__(self,x,y,xObjectiv,yObjectiv):
        enemigo.__init__(self,x,y,xObjectiv,yObjectiv)
        #recarga: como la del jugador, el sello de tiempo se pone al disparar. Empieza recargando,
        #asi no dispara a bocajarro en el mismo frame en que aparece
        self.recarga = RECARGA_ENEMIGO
        self.instanteUltimoDisparo = pygame.time.get_ticks()
        #sin esto se le veria el fogonazo al aparecer, antes de haber disparado nada
        self.haDisparado = False

    def puedeDisparar(self, ahora):
        return ahora - self.instanteUltimoDisparo >= self.recarga

    def mostrandoFogonazo(self, ahora):
        return self.haDisparado and ahora - self.instanteUltimoDisparo < DURACION_FOGONAZO

    def encarado(self):
        #a la altura del jugador con un margen, que es lo que le da linea de tiro
        return abs(self.yObjectiv - self.y) <= TOLERANCIA_PUNTERIA

    def pathFinding(self,xObjectiv,yObjectiv):
        self.xObjectiv=xObjectiv
        self.yObjectiv=yObjectiv
        #mira hacia el jugador siempre, tambien estando quieto: antes se quedaba con la
        #orientacion con la que aparecio y disparaba hacia el lado contrario
        self.izq = xObjectiv < self.x
        self.dch = not self.izq
        moviendose = False
        #primero se pone a la altura del jugador
        if not self.encarado():
            if(yObjectiv < self.y):
                self.y-=self.vel
            else:
                self.y+=self.vel
            moviendose = True
        #y se acerca hasta tenerlo a tiro
        if abs(xObjectiv - self.x) > DISTANCIA_DE_TIRO:
            if(xObjectiv < self.x):
                self.x-=self.vel
            else:
                self.x+=self.vel
            moviendose = True
        self.stop = not moviendose
        self.actualizarRect()

    def sprite(self):
        if not self.stop:
            secuencia = Andar_izq_Fr if self.izq else Andar_dch_Fr
            imagen = secuencia[self.contadorCaminar // 3]
            self.contadorCaminar = (self.contadorCaminar + 1) % 27
            return imagen
        secuencia = Disparar_izq_Fr if self.izq else Disparar_dch_Fr
        return secuencia[1] if self.mostrandoFogonazo(pygame.time.get_ticks()) else secuencia[0]

    def disparar(self,bullets):
        ahora = pygame.time.get_ticks()
        if not self.encarado() or not self.puedeDisparar(ahora):
            return
        self.instanteUltimoDisparo = ahora
        self.haDisparado = True
        sound_musket.play()
        apuntando = -1 if self.izq else 1
        bullets.append(proyectil(self.xCanon(), self.y + self.ALTURA_CANON, apuntando))

    def dibujarCadaver(self,win):
        dibujar_anclado(win, cadaverImg, self.x, self.y, self.izq,
                        self.ANCHO_REFERENCIA, self.ALTO_REFERENCIA)
