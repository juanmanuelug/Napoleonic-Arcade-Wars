import pygame
from proyectile import proyectil, DANIO_BALA
import sonidos
from render import dibujar_anclado, destello

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
# Vida con la que empieza el soldado
VIDA_MAXIMA = 100
# Velocidad al andar. En diagonal se avanza menos por eje: aplicar los 3 en los dos ejes
# hacia que correr en diagonal fuese un 41% mas rapido que en recto (3,3 = 4.24 px)
VELOCIDAD = 3
VELOCIDAD_DIAGONAL = 2
# Milisegundos que el soldado se ve blanco despues de recibir un golpe
DURACION_DESTELLO = 100
# Por cuanto se multiplica el danio mientras dura el estandarte
MULTIPLICADOR_DANIO_DOBLE = 2
# Danio por chocar con un enemigo cuerpo a cuerpo y milisegundos de gracia entre golpe y golpe.
# Sin esa espera el contacto restaba vida en CADA frame (3.5 x 30 fps = 105 de vida por segundo)
DANIO_CONTACTO = 8
GRACIA_CONTACTO = 500
######Jugador################
class jugador(object):
    def __init__(self, x, y):
        #posicion (esquina superior izquierda de la caja del cuerpo)
        self.x = x
        self.y = y
        #velocidad
        self.vel = VELOCIDAD
        #orientacion
        self.mirando_izq = False
        #estado de movimiento
        self.caminando = False
        self.contadorCaminar = 0
        #recarga y danio: los ascensos los mejoran, asi que son de la instancia, no constantes
        self.recarga = RECARGA
        self.danioBala = DANIO_BALA
        self.instanteUltimoDisparo = pygame.time.get_ticks() - RECARGA
        #ultimo golpe recibido por contacto, para no restar vida en cada frame
        self.instanteUltimoGolpe = pygame.time.get_ticks() - GRACIA_CONTACTO
        #ultimo danio recibido de cualquier clase, para el destello
        self.instanteUltimoDanio = pygame.time.get_ticks() - DURACION_DESTELLO
        #efectos que dan los objetos del campo: disparos sin recargar, inmunidad al
        #contacto y danio doble. Los dos ultimos caducan a una hora concreta
        self.disparosGratis = 0
        self.instanteFinInmunidad = 0
        self.instanteFinDanioDoble = 0
        #la mochila: un solo objeto guardado, que se gasta cuando el jugador quiere
        self.objetoEnMochila = None
        #colision
        self.rect = pygame.Rect(x, y, ANCHO_CUERPO, ALTO_CUERPO)
        #Vida
        self.vida = VIDA_MAXIMA
        self.vidaMaxima = VIDA_MAXIMA

    # # Estado del arma

    def puedeDisparar(self, ahora):
        return ahora - self.instanteUltimoDisparo >= self.recarga

    def mostrandoFogonazo(self, ahora):
        return ahora - self.instanteUltimoDisparo < DURACION_FOGONAZO

    def progresoRecarga(self, ahora):
        #de 0 (acabo de disparar) a 1 (mosquete listo), para la barra de recarga
        if self.recarga <= 0:
            return 1.0
        return min(1.0, (ahora - self.instanteUltimoDisparo) / float(self.recarga))

    def xCanon(self):
        if self.mirando_izq:
            return self.x
        return self.x + ANCHO_CUERPO

    # # Efectos que dan los objetos del campo

    def tieneInmunidad(self, ahora):
        return ahora < self.instanteFinInmunidad

    def tieneDanioDoble(self, ahora):
        return ahora < self.instanteFinDanioDoble

    def danioDelProximoDisparo(self, ahora):
        if self.tieneDanioDoble(ahora):
            return self.danioBala * MULTIPLICADOR_DANIO_DOBLE
        return self.danioBala

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
        if self.mostrandoDestello(ahora):
            imagen = destello(imagen)
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
        #en diagonal se avanza menos por eje, para que no salga mas rapido que en recto
        paso = VELOCIDAD_DIAGONAL if (avanceX != 0 and avanceY != 0) else self.vel
        #los limites usan el tamanio real del cuerpo, no una medida inventada
        self.x = min(max(0, self.x + avanceX * paso), WINX - ANCHO_CUERPO)
        self.y = min(max(0, self.y + avanceY * paso), WINY - ALTO_CUERPO)
        self.rect.topleft = (self.x, self.y)

    # #Metodo para disparar

    def disparar(self, keys, balas):
        if not keys[pygame.K_SPACE]:
            return
        ahora = pygame.time.get_ticks()
        #la cartuchera permite disparar sin esperar la recarga, y se gasta al usarla
        conCartuchera = self.disparosGratis > 0
        if not conCartuchera and not self.puedeDisparar(ahora):
            return
        if conCartuchera:
            self.disparosGratis -= 1
        self.instanteUltimoDisparo = ahora
        sound_musket.play()
        apuntando = -1 if self.mirando_izq else 1
        balas.append(proyectil(self.xCanon(), self.y + ALTURA_CANON, apuntando,
                               self.danioDelProximoDisparo(ahora)))

    # # Danio recibido de una bala: un impacto, un mordisco de vida
    # La direccion se recibe por simetria con los enemigos, pero al jugador no se le empuja:
    # moverlo sin que el lo pida es quitarle el control justo cuando mas lo necesita
    def recibirImpacto(self, danio, direccion=0):
        self.vida -= danio
        self.instanteUltimoDanio = pygame.time.get_ticks()
        sonidos.sonido_impacto.play()

    # # Danio recibido por tener un enemigo encima, como mucho uno cada GRACIA_CONTACTO ms
    def sufrirContacto(self, enemigos):
        ahora = pygame.time.get_ticks()
        #el aguardiente deja cruzar entre bayonetas sin pagarlo
        if self.tieneInmunidad(ahora):
            return
        if ahora - self.instanteUltimoGolpe < GRACIA_CONTACTO:
            return
        for enemigo in enemigos:
            if self.rect.colliderect(enemigo.rect):
                self.vida -= DANIO_CONTACTO
                self.instanteUltimoGolpe = ahora
                self.instanteUltimoDanio = ahora
                sonidos.sonido_impacto.play()
                return

    def mostrandoDestello(self, ahora):
        return ahora - self.instanteUltimoDanio < DURACION_DESTELLO
