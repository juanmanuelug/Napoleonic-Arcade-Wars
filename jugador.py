import pygame
from proyectile import proyectil, DANIO_BALA
import sablazos
import sonidos
from render import dibujar_anclado, destello, dibujar_silueta

pygame.init()

# ####################################### Constantes  ##################################################
WINX = 500
WINY = 500
###################Sonidos#############################
sound_musket = pygame.mixer.Sound('./sonido/musket_shot04.wav')
sound_musket.set_volume(0.2)
##############Soldados Ingleses################
Andar_izq = [pygame.image.load('./sprites/ingleses/soldado_ingles_izq_0_bayoneta.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_izq_1_bayoneta.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_izq_2_bayoneta.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_izq_3_bayoneta.png'),
             pygame.image.load('./sprites/ingleses/soldado_ingles_izq_4_bayoneta.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_izq_5_bayoneta.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_izq_6_bayoneta.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_izq_1_bayoneta.png'),
             pygame.image.load('./sprites/ingleses/soldado_ingles_izq_2_bayoneta.png')]
Andar_dch = [pygame.image.load('./sprites/ingleses/soldado_ingles_dch_0_bayoneta.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_dch_1_bayoneta.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_dch_2_bayoneta.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_dch_3_bayoneta.png'),
             pygame.image.load('./sprites/ingleses/soldado_ingles_dch_4_bayoneta.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_dch_5_bayoneta.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_dch_6_bayoneta.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_dch_1_bayoneta.png'),
             pygame.image.load('./sprites/ingleses/soldado_ingles_dch_2_bayoneta.png')]

Disparar_izq = [pygame.image.load('./sprites/ingleses/soldado_ingles_izq_disparar_1_bayoneta.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_izq_disparar_bayoneta.png')]
Disparar_dch = [pygame.image.load('./sprites/ingleses/soldado_ingles_dch_disparar_1_bayoneta.png'), pygame.image.load('./sprites/ingleses/soldado_ingles_dch_disparar_bayoneta.png')]
#La estocada usa la misma pose de apuntar: la bayoneta se ve ya en todos los sprites, asi
#que lo que dice "golpe" no es que aparezca el acero, es que el cuerpo se adelante
Bayoneta_izq = Disparar_izq[0]
Bayoneta_dch = Disparar_dch[0]

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
# ####################################### Bayoneta ####################################################
# El bayonetazo: pega mas que un disparo (40 contra 25) porque para darlo hay que meterse en el
# alcance del sable del frances, y eso es lo que se paga
DANIO_BAYONETA = 40
# La recarga sale de la cuenta al reves: el techo pedido eran 70 de danio por segundo, y
# 40 / 0,570 s = 70,2. Se toca la recarga y no el danio para que sigan bastando DOS golpes
# para tumbar a un frances de 75 de vida; bajando el danio harian falta tres
RECARGA_BAYONETA = 570
DURACION_ESTOCADA = 180
# Hasta donde llega el acero por delante del cuerpo, y lo alto que barre
ALCANCE_BAYONETA = 16
ALTO_BAYONETA = 26
# Lo que se adelanta el sprite mientras dura la estocada. Esto es lo que la hace legible: el
# dibujo es la misma pose de apuntar, y lo que dice "golpe" es que el cuerpo salte hacia
# delante. Cinco pixeles y no tres, porque ahora la bayoneta se ve siempre y el salto es la
# unica pista que queda
PASO_DE_ESTOCADA = 5
# ######################################### Dash ######################################################
# Un salto corto HACIA ATRAS, al lado contrario del que mira el soldado. Sirve para salirse del
# alcance de un sable que ya viene sin dejar de encarar a quien te ataca, que es lo que lo hace
# util: girarse para huir es perder el disparo
# 40 px y no 60: con 60 el salto sacaba al jugador de la pelea entera, y la idea es salirse
# del sable sin perder de vista al enemigo. Tiene que seguir pasando del alcance de tu
# bayoneta (15 px de hueco), o el dash te sacaria tambien de tu propio alcance
DISTANCIA_DASH = 40
VELOCIDAD_DASH = 12
RECARGA_DASH = 900
# La estela del dash: siluetas del propio cuerpo en los sitios por los que ha pasado, que se
# van apagando. Es lo que hace que el salto se lea como velocidad y no como un teletransporte.
# Va floja y de una sola pasada: la primera version usaba el halo del oficial (cuatro pasadas) a
# alfa 150 y dejaba un borron pálido enorme en vez de una estela
DURACION_ESTELA = 170
COLOR_DE_LA_ESTELA = (176, 192, 214)
ALFA_MAXIMO_DE_LA_ESTELA = 70
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
        #la bayoneta y el dash: los dos con su propio reloj, y el dash con lo que le queda
        #por recorrer, porque no es un salto instantaneo sino unos frames de carrera
        self.instanteUltimaEstocada = pygame.time.get_ticks() - RECARGA_BAYONETA
        self.instanteUltimoDash = pygame.time.get_ticks() - RECARGA_DASH
        self.dashPendiente = 0
        self.dashHacia = 0
        #por donde ha pasado el dash, para la estela
        self.estelaDelDash = []
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
        adelanto = 0
        if self.mostrandoEstocada(ahora):
            #la estocada manda sobre el fogonazo: es el gesto mas reciente y el que hay que ver
            imagen = Bayoneta_izq if self.mirando_izq else Bayoneta_dch
            adelanto = -PASO_DE_ESTOCADA if self.mirando_izq else PASO_DE_ESTOCADA
        elif self.mostrandoFogonazo(ahora):
            imagen = Disparar_izq[1] if self.mirando_izq else Disparar_dch[1]
        elif self.caminando:
            secuencia = Andar_izq if self.mirando_izq else Andar_dch
            imagen = secuencia[self.contadorCaminar // 3]
            self.contadorCaminar = (self.contadorCaminar + 1) % 27
        else:
            imagen = Disparar_izq[0] if self.mirando_izq else Disparar_dch[0]
        if self.mostrandoDestello(ahora):
            imagen = destello(imagen)
        #la estela del dash, por DEBAJO del cuerpo y de mas vieja a mas nueva
        self.estelaDelDash = [huella for huella in self.estelaDelDash
                              if ahora - huella[2] < DURACION_ESTELA]
        for huellaX, huellaY, instante in self.estelaDelDash:
            queda = 1.0 - (ahora - instante) / float(DURACION_ESTELA)
            dibujar_silueta(win, imagen, huellaX, huellaY, self.mirando_izq,
                            ANCHO_CUERPO, ALTO_CUERPO, COLOR_DE_LA_ESTELA,
                            max(1, int(ALFA_MAXIMO_DE_LA_ESTELA * queda)))
        dibujar_anclado(win, imagen, self.x + adelanto, self.y, self.mirando_izq,
                        ANCHO_CUERPO, ALTO_CUERPO)

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

    # # La bayoneta: el cuerpo a cuerpo del jugador

    def puedeEstocar(self, ahora):
        return ahora - self.instanteUltimaEstocada >= RECARGA_BAYONETA

    def mostrandoEstocada(self, ahora):
        return ahora - self.instanteUltimaEstocada < DURACION_ESTOCADA

    def cajaDeLaBayoneta(self):
        """El trozo de campo que barre el acero, por delante del cuerpo."""
        arriba = self.y + (ALTO_CUERPO - ALTO_BAYONETA) // 2
        if self.mirando_izq:
            return pygame.Rect(self.x - ALCANCE_BAYONETA, arriba, ALCANCE_BAYONETA, ALTO_BAYONETA)
        return pygame.Rect(self.x + ANCHO_CUERPO, arriba, ALCANCE_BAYONETA, ALTO_BAYONETA)

    def danioDeLaEstocada(self, ahora):
        if self.tieneDanioDoble(ahora):
            return DANIO_BAYONETA * MULTIPLICADOR_DANIO_DOBLE
        return DANIO_BAYONETA

    def estocada(self, enemigos, destellos=None):
        """Da un bayonetazo si le toca. Devuelve a los que alcanza.

        No se puede estocar en mitad de un dash: el dash es un compromiso, y poder pegar mientras
        te apartas quitaria la gracia de tener que elegir.
        """
        ahora = pygame.time.get_ticks()
        if self.dashPendiente or not self.puedeEstocar(ahora):
            return []
        self.instanteUltimaEstocada = ahora
        #el silbido del acero es el mismo que el del sable frances: es acero cortando aire
        sonidos.sonido_sable.play()
        caja = self.cajaDeLaBayoneta()
        if destellos is not None:
            #el destello sale de la punta del acero y a la ALTURA DEL CANION, que es la
            #misma por la que salen las balas. Centrado en la caja del golpe salia 4 px
            #por encima de la hoja y se veia despegado del mosquete
            destellos.append(sablazos.Estocada(caja.left if self.mirando_izq else caja.right,
                                              self.y + ALTURA_CANON, self.mirando_izq,
                                              pygame.time.get_ticks()))
        empuje = -1 if self.mirando_izq else 1
        alcanzados = [enemigo for enemigo in enemigos if caja.colliderect(enemigo.rect)]
        for enemigo in alcanzados:
            enemigo.recibirImpacto(self.danioDeLaEstocada(ahora), empuje)
        return alcanzados

    # # El dash: un salto atras

    def puedeDashear(self, ahora):
        return not self.dashPendiente and ahora - self.instanteUltimoDash >= RECARGA_DASH

    def dashear(self):
        """Arranca el salto hacia atras. Devuelve si ha salido."""
        ahora = pygame.time.get_ticks()
        if not self.puedeDashear(ahora):
            return False
        self.instanteUltimoDash = ahora
        #hacia el lado CONTRARIO al que mira: es un salto atras, no una carrera
        self.dashHacia = 1 if self.mirando_izq else -1
        self.dashPendiente = DISTANCIA_DASH
        sonidos.sonido_dash.play()
        return True

    def avanzarDash(self):
        """Mueve lo que toque de dash este frame. Devuelve si sigue en el aire.

        Mientras dura, el dash MANDA sobre las teclas de andar: quien llama tiene que preguntar
        por esto antes de llamar a caminar(), o el jugador se movria dos veces en el mismo frame.
        """
        if not self.dashPendiente:
            return False
        #se apunta de donde sale antes de moverse: la estela va por detras
        self.estelaDelDash.append((self.x, self.y, pygame.time.get_ticks()))
        paso = min(VELOCIDAD_DASH, self.dashPendiente)
        self.x = min(max(0, self.x + self.dashHacia * paso), WINX - ANCHO_CUERPO)
        self.dashPendiente -= paso
        self.caminando = True
        self.rect.topleft = (self.x, self.y)
        return True

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
            #al que lleva sable no se le paga por tocarlo: su danio lo hace el tajo, que
            #avisa un segundo antes. Cobrar las dos cosas dejaria sin sentido esquivarlo
            if getattr(enemigo, 'PELEA_CON_SABLE', False):
                continue
            if self.rect.colliderect(enemigo.rect):
                self.vida -= DANIO_CONTACTO
                self.instanteUltimoGolpe = ahora
                self.instanteUltimoDanio = ahora
                sonidos.sonido_impacto.play()
                return

    def mostrandoDestello(self, ahora):
        return ahora - self.instanteUltimoDanio < DURACION_DESTELLO
