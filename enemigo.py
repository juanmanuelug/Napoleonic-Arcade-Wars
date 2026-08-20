import pygame
import random
import granadas
import math
import sablazos
from proyectile import proyectil
import sonidos
from render import dibujar_anclado, destello, dibujar_aura

pygame.init()
# ####################################### Constantes  ##################################################
WINX = 500
WINY = 500
# Milisegundos entre disparo y disparo de un tirador, y lo que se le ve el fogonazo
RECARGA_ENEMIGO = 1500
DURACION_FOGONAZO = 180
# Milisegundos que se ve blanco al recibir un impacto, y pixeles que le echa atras el plomo
DURACION_DESTELLO = 100
EMPUJE_IMPACTO = 5
# Margen de alineacion vertical con el que un tirador se da por encarado al jugador. Exigir la
# misma y exacta hacia que casi nunca disparasen, porque el jugador se mueve de 3 en 3 pixeles.
# Cada tirador anade su propia pizca, para que no disparen todos en el mismo frame
TOLERANCIA_PUNTERIA = 6
VARIACION_PUNTERIA = 3
# Puestos de tiro. Con una sola distancia, todos los tiradores acababan plantados a los mismos
# 180 px y a la misma altura, en fila india. Ahora cada uno que entra en batalla toma el
# siguiente puesto y se reparten la profundidad.
# Holgura al llegar al puesto, para que no tiemble adelante y atras al colocarse
MARGEN_PUESTO = 4
# La separacion entre puestos tiene que ser mayor que el ancho de un cuerpo (20) mas dos veces
# la holgura, o dos tiradores de puestos contiguos podrian acabar solapados
SEPARACION_PUESTOS = 30
PUESTO_MAS_CERCANO = 140
# El puesto mas lejano no pasa de 230: mas alla, con el jugador en el centro, el tirador se
# quedaria fuera de la pantalla disparando a alguien que no puede verle
PUESTOS_DE_TIRO = tuple(PUESTO_MAS_CERCANO + SEPARACION_PUESTOS * indice
                        for indice in (0, 2, 1, 3))
# Milisegundos de desfase propio, para que las descargas no salgan a la vez
DESFASE_MAXIMO_DESCARGA = 700
# El sable de la tropa de cuerpo a cuerpo: alza y taja. RECARGA_SABLE tiene que ser la gracia
# de contacto del jugador (jugador.GRACIA_CONTACTO), porque el danio lo sigue haciendo el
# contacto y no el sable: yendo al mismo ritmo, el tajo cae cuando el jugador pierde vida.
# Hay una prueba que salta si los dos numeros se separan.
RECARGA_SABLE = 500
DURACION_ALZADO = 220
DURACION_TAJO = 200
# De donde sale el arco del sablazo. Medido sobre el sprite del tajo: la empunadura cae en el
# borde delantero de la caja del cuerpo (21x30) y a 12 px de su borde de arriba, y de ahi la
# hoja sale 10 px hacia delante y hacia arriba
DESPLAZAMIENTO_DE_LA_MANO = 1
ALTURA_DE_LA_MANO = 12
# El oficial: no dispara ni lanza nada, pero mientras esta en pie los franceses que tenga cerca
# van un 50% mas rapidos. Es el primer enemigo al que te conviene disparar ANTES que al que
# tienes encima, que hasta ahora era siempre lo mas cercano.
VIDA_OFICIAL = 100
RADIO_DE_MANDO = 90
FACTOR_DE_MANDO = 1.5
# El anillo que ensenia hasta donde llega el mando. Va A TROZOS y no lleno a proposito: es
# informacion, no una amenaza que esquivar, asi que no puede competir con la marca roja de la
# granada, que si hay que mirarla. Por lo mismo no parpadea. Dorado apagado, el color del oficial
COLOR_DE_MANDO = (222, 186, 74)
# El halo de los que estan bajo su mando: el mismo dorado, translucido, para que el anillo del
# suelo y los soldados que acelera digan lo mismo de un vistazo
ALFA_DEL_HALO = 255
TROZOS_DEL_ANILLO = 12
# Un paso por pixel de circunferencia. Con menos, los trozos salen como motas sueltas y no
# como rayas: probado con 96 pasos y se veian 96 puntos desperdigados por el campo
PASOS_DEL_ANILLO = int(2 * math.pi * RADIO_DE_MANDO)
# El voltigeur, el tirador de la infanteria ligera: va al doble de velocidad, recarga antes y
# se planta por detras de la linea de tiro del soldado de linea. Su amenaza es la posicion, no
# el aguante: tiene la misma vida que una bayoneta, cae con los mismos tres disparos.
VEL_VOLTIGEUR = 2
RECARGA_VOLTIGEUR = 1100
# Sus puestos van por detras de los del soldado de linea, que llegan a 230. Con el jugador en
# el centro de la pantalla no caben 260 px de separacion, asi que el voltigeur se queda pegado
# al borde, que es lo mas lejos que se puede estar de el; el freno de la retirada en
# pathFinding ya se encarga de que siga estando a la vista y al alcance del plomo.
PUESTO_VOLTIGEUR_MAS_CERCANO = 260
PUESTOS_DE_VOLTIGEUR = tuple(PUESTO_VOLTIGEUR_MAS_CERCANO + SEPARACION_PUESTOS * indice
                             for indice in (0, 1))
# El granadero de la Guardia: aguanta mas, va mas lento y no necesita ponerse a tu altura,
# porque una granada no se esquiva cambiando de fila. Se planta en un anillo alrededor del
# jugador: ni tan lejos que no llegue, ni tan cerca que le pille su propio estallido
VIDA_GRANADERO = 150
DISTANCIA_DE_LANZAMIENTO = 190
DISTANCIA_MINIMA_GRANADERO = 110
RECARGA_GRANADA = 3800
DURACION_ARMADO = 340
DURACION_SUELTA = 240
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

#El sable de la tropa de cuerpo a cuerpo. Estos dos fotogramas estaban ya dibujados y no se
#usaban: la animacion de andar de arriba solo gasta del 2 al 6. El 1 es el mas recogido (22 px
#de ancho util, el sable en alto) y el 0 el mas largo de los siete (30 px, el brazo extendido).
Alzar_izq_Fr = pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_1.png')
Tajar_izq_Fr = pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_0.png')
Alzar_dch_Fr = pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_1.png')
Tajar_dch_Fr = pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_0.png')

##############Oficiales#################
#los mismos 14 fotogramas de cuerpo a cuerpo con penacho y banda dorada; los saca
#herramientas/oficial.py
def _cicloDeCuerpoACuerpo(patron):
    #la misma lista de nueve entradas que la tropa de cuerpo a cuerpo: del 2 al 6 y vuelta a
    #empezar, porque el 0 y el 1 no son de andar, son el sable
    dibujos = [pygame.image.load(patron % numero) for numero in range(2, 7)]
    return dibujos + dibujos[:4]

Andar_izq_Of = _cicloDeCuerpoACuerpo('./sprites/franceses/oficial_fr_izq_cuerpoAcuerpo_%d.png')
Andar_dch_Of = _cicloDeCuerpoACuerpo('./sprites/franceses/oficial_fr_dch_cuerpoAcuerpo_%d.png')
Alzar_izq_Of = pygame.image.load('./sprites/franceses/oficial_fr_izq_cuerpoAcuerpo_1.png')
Tajar_izq_Of = pygame.image.load('./sprites/franceses/oficial_fr_izq_cuerpoAcuerpo_0.png')
Alzar_dch_Of = pygame.image.load('./sprites/franceses/oficial_fr_dch_cuerpoAcuerpo_1.png')
Tajar_dch_Of = pygame.image.load('./sprites/franceses/oficial_fr_dch_cuerpoAcuerpo_0.png')

##############Granaderos de la Guardia#################
def _cicloDeAndar(patron):
    #la misma lista de nueve entradas que usan los demas: siete dibujos y dos repetidos
    dibujos = [pygame.image.load(patron % numero) for numero in range(7)]
    return dibujos + [dibujos[1], dibujos[2]]

Andar_izq_Gr = _cicloDeAndar('./sprites/franceses/granadero_fr_izq_%d.png')
Andar_dch_Gr = _cicloDeAndar('./sprites/franceses/granadero_fr_dch_%d.png')
Lanzar_izq_Gr = [pygame.image.load('./sprites/franceses/granadero_fr_izq_lanzar_0.png'),
                 pygame.image.load('./sprites/franceses/granadero_fr_izq_lanzar_1.png')]
Lanzar_dch_Gr = [pygame.image.load('./sprites/franceses/granadero_fr_dch_lanzar_0.png'),
                 pygame.image.load('./sprites/franceses/granadero_fr_dch_lanzar_1.png')]

##############Voltigeurs de la infanteria ligera#################
#los mismos 18 sprites del soldado de linea con el penacho y la banda del chaco encima; los
#saca herramientas/voltigeur.py y no se dibujan a mano
Andar_izq_Vo = _cicloDeAndar('./sprites/franceses/voltigeur_fr_izq_%d.png')
Andar_dch_Vo = _cicloDeAndar('./sprites/franceses/voltigeur_fr_dch_%d.png')
Disparar_izq_Vo = [pygame.image.load('./sprites/franceses/voltigeur_fr_izq_disparar_1.png'),
                   pygame.image.load('./sprites/franceses/voltigeur_fr_izq_disparar.png')]
Disparar_dch_Vo = [pygame.image.load('./sprites/franceses/voltigeur_fr_dch_disparar_1.png'),
                   pygame.image.load('./sprites/franceses/voltigeur_fr_dch_disparar.png')]

cadaverImg = pygame.image.load('./sprites/franceses/cadaver.png')
cadaverOficialImg= pygame.image.load('./sprites/franceses/cadaverOficialImg.png')
#el granadero moria con el chaco del soldado de linea aunque en pie lleve bonete de piel de oso:
#este es el mismo cuerpo tirado con el bonete y su penacho (ver herramientas/cadaver_granadero.py)
cadaverGranaderoImg = pygame.image.load('./sprites/franceses/cadaver_granadero.png')
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


#un turno por linea de tiro: la del soldado de linea y la del voltigeur van cada una a lo suyo
_siguientePuesto = {}


def tomarPuestoDeTiro(puestos=PUESTOS_DE_TIRO):
    """Reparte los puestos por turno: dos tiradores seguidos nunca se plantan a la vez."""
    turno = _siguientePuesto.get(puestos, 0)
    _siguientePuesto[puestos] = turno + 1
    return puestos[turno % len(puestos)]


def puestoLibre(enemigosVivos, puestos=PUESTOS_DE_TIRO):
    """Un puesto que no tenga ya otro tirador; si estan todos cogidos, el siguiente por turno.

    Se mira solo dentro de su propia linea de tiro: un voltigeur, que se planta mucho mas
    atras, no le ocupa el puesto a un soldado de linea ni al contrario.
    """
    ocupados = [otro.distanciaDeTiro for otro in enemigosVivos
                if isinstance(otro, enemigoDistancia) and otro.PUESTOS == puestos]
    libres = [puesto for puesto in puestos if puesto not in ocupados]
    if libres:
        return random.choice(libres)
    return tomarPuestoDeTiro(puestos)


def aplicarMando(enemigos):
    """Pone a cada frances su velocidad, x1.5 si tiene un oficial cerca. Una vez por frame.

    Se recalcula entera en vez de ir sumando y restando: asi, cuando el oficial cae o se aleja,
    la velocidad vuelve sola a la suya sin que nadie tenga que llevar la cuenta.
    """
    mandos = [uno for uno in enemigos if isinstance(uno, oficial) and uno.vivo]
    for frances in enemigos:
        frances.vel = frances.VELOCIDAD
        frances.conMando = False
        #un oficial no se acelera a si mismo ni a otro oficial: el aura es para la tropa
        if isinstance(frances, oficial):
            continue
        for mando in mandos:
            if (_distanciaAlCuadrado(frances.rect.center, mando.rect.center)
                    <= RADIO_DE_MANDO ** 2):
                frances.vel = frances.VELOCIDAD * FACTOR_DE_MANDO
                frances.conMando = True
                break


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
    #Lo que vale para el rango del jugador. Matar un granadero de 150 de vida no puede contar
    #lo mismo que una bayoneta de 75: el rango premia la dificultad, no el volumen
    PUNTOS = 1
    #Con que probabilidad suelta algo al caer. Es la palanca con la que se ajusta el ritmo
    #de objetos de toda la partida, y cada tipo de enemigo trae la suya
    PROBABILIDAD_SUELTA = 0.18
    #esta tropa pelea con sable. Los que van con el mosquete heredan de esta clase, asi que
    #heredan tambien el sable: lo apagan poniendo esto a False
    PELEA_CON_SABLE = True
    #velocidad propia. Esta aqui y no solo en el __init__ porque el aura del oficial la
    #recalcula cada frame, y necesita saber a que valor volver cuando el oficial cae
    VELOCIDAD = 1
    #sus sprites. Asi el oficial es esta misma clase con otros dibujos y otros numeros
    ANDAR_IZQ = Andar_izq_Fr_cuerpo
    ANDAR_DCH = Andar_dch_Fr_cuerpo
    ALZAR_IZQ = Alzar_izq_Fr
    ALZAR_DCH = Alzar_dch_Fr
    TAJAR_IZQ = Tajar_izq_Fr
    TAJAR_DCH = Tajar_dch_Fr

    def __init__(self,x,y,xObjectiv,yObjectiv):
        self.x=x
        self.y=y
        self.vel=self.VELOCIDAD
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
        #ultimo impacto recibido, para el destello
        self.instanteUltimoDanio=pygame.time.get_ticks() - DURACION_DESTELLO
        #solo lo usan los que disparan, pero lo tienen todos para poder ajustar los relojes
        #de golpe cuando la partida se pausa en un ascenso
        self.instanteUltimoDisparo=pygame.time.get_ticks()
        #idem para los que lanzan granadas
        self.instanteUltimoLanzamiento=pygame.time.get_ticks()
        self.instanteInicioArmado=0
        #el sable: alzando o no, cuando empezo el alzado y cuando cayo el ultimo tajo. Empieza
        #con la recarga cumplida, para que el primero que te alcance no tenga que esperar
        self.alzandoSable=False
        self.instanteInicioAlzado=0
        self.instanteUltimoTajo=pygame.time.get_ticks() - RECARGA_SABLE
        #si ahora mismo le esta acelerando un oficial. Lo pone aplicarMando cada frame
        self.conMando=False

    def actualizarRect(self):
        #la caja de colision sigue al cuerpo dibujado, no al lienzo completo del sprite
        cuerpo = self.CUERPO_IZQ if self.izq else self.CUERPO_DCH
        self.rect = cuerpo.move(self.x, self.y)

    def xCanon(self):
        if self.izq:
            return self.rect.left
        return self.rect.right

    def atacar(self, cajaObjetivo, sablazosEnElAire):
        """Se llama cada frame: alza el sable con el jugador encima y suelta el tajo al acabar.

        El danio NO lo hace esto, lo sigue haciendo jugador.sufrirContacto. Aqui solo se mueve
        el sable, y va al mismo ritmo porque RECARGA_SABLE es la gracia de contacto del jugador:
        el tajo cae cuando el jugador pierde vida, no en un compas aparte.
        """
        if not self.PELEA_CON_SABLE:
            return
        ahora = pygame.time.get_ticks()
        if self.alzandoSable:
            if ahora - self.instanteInicioAlzado >= DURACION_ALZADO:
                self.alzandoSable = False
                self.instanteUltimoTajo = ahora
                sablazosEnElAire.append(sablazos.Sablazo(self.xDeLaMano(),
                                                         self.yDeLaMano(), self.izq, ahora))
            return
        if (self.rect.colliderect(cajaObjetivo)
                and ahora - self.instanteUltimoTajo >= RECARGA_SABLE):
            self.alzandoSable = True
            self.instanteInicioAlzado = ahora

    def xDeLaMano(self):
        #la mano que lleva el sable va en el borde delantero del cuerpo
        if self.izq:
            return self.rect.left + DESPLAZAMIENTO_DE_LA_MANO
        return self.rect.right - DESPLAZAMIENTO_DE_LA_MANO

    def yDeLaMano(self):
        return self.rect.top + ALTURA_DE_LA_MANO

    def mostrandoTajo(self, ahora):
        return not self.alzandoSable and ahora - self.instanteUltimoTajo < DURACION_TAJO

    def pathFinding(self,xObjectiv,yObjectiv):
        self.xObjectiv=xObjectiv
        self.yObjectiv=yObjectiv
        if self.alzandoSable:
            #con el sable en alto no avanza, pero sigue encarando al jugador
            self.izq = xObjectiv < self.x
            self.dch = not self.izq
            self.stop = True
            self.actualizarRect()
            return
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
        if self.alzandoSable:
            return self.ALZAR_IZQ if self.izq else self.ALZAR_DCH
        if self.mostrandoTajo(pygame.time.get_ticks()):
            return self.TAJAR_IZQ if self.izq else self.TAJAR_DCH
        if not self.stop:
            secuencia = self.ANDAR_IZQ if self.izq else self.ANDAR_DCH
            imagen = secuencia[self.contadorCaminar // 3]
            self.contadorCaminar = (self.contadorCaminar + 1) % 27
            return imagen
        return self.ANDAR_IZQ[0] if self.izq else self.ANDAR_DCH[0]

    def dibujarEnemigo(self, win):
        imagen = self.sprite()
        if self.mostrandoDestello(pygame.time.get_ticks()):
            imagen = destello(imagen)
        #el halo va debajo del sprite, para que el soldado se siga leyendo igual
        if self.conMando:
            dibujar_aura(win, imagen, self.x, self.y, self.izq,
                         self.ANCHO_REFERENCIA, self.ALTO_REFERENCIA,
                         COLOR_DE_MANDO, ALFA_DEL_HALO)
        dibujar_anclado(win, imagen, self.x, self.y, self.izq,
                        self.ANCHO_REFERENCIA, self.ALTO_REFERENCIA)

    def recibirImpacto(self,danio,direccion=0):
        #el reparto de danio lo hace colisiones.resolverBalas, aqui solo se apunta
        self.vida-= danio
        self.instanteUltimoDanio = pygame.time.get_ticks()
        sonidos.sonido_impacto.play()
        #un empujon en la direccion del disparo: confirma el acierto sin numeros flotantes
        self.x += direccion * EMPUJE_IMPACTO
        self.actualizarRect()

    def mostrandoDestello(self, ahora):
        return ahora - self.instanteUltimoDanio < DURACION_DESTELLO

    def checkEstadoVida(self):
        if(self.vida<=0 and self.vivo):
            self.vivo=False
            self.instanteMuerte=pygame.time.get_ticks()
            sonidos.sonido_muerte.play()

    def disparar(self,bullets):
        #solo por herencia
        pass

    def lanzar(self,granadasEnElAire,puntoObjetivo):
        #solo por herencia
        pass

    def dibujarMando(self,win):
        #solo por herencia: el unico que tiene algo que enseniar en el suelo es el oficial
        pass

    def dibujarCadaver(self,win):
        #anclado como el resto de sprites, para que caiga donde estaban sus pies. El cadaver
        #con dorados (cadaverOficialImg) es del oficial, no de la tropa
        dibujar_anclado(win, cadaverImg, self.x, self.y, self.izq,
                        self.ANCHO_REFERENCIA, self.ALTO_REFERENCIA)

##Enemigo a distancia
class enemigoDistancia(enemigo):
    #sus sprites de andar miden 20x36, igual que los del jugador
    ANCHO_REFERENCIA = 20
    ALTO_REFERENCIA = 36
    CUERPO_IZQ = pygame.Rect(0, 0, 20, 36)
    CUERPO_DCH = pygame.Rect(0, 0, 20, 36)
    #el tirador es mas peligroso y esta mas lejos: suelta algo mas a menudo
    PROBABILIDAD_SUELTA = 0.28
    #y vale el doble: te dispara desde lejos
    PUNTOS = 2
    #va con el mosquete: no tiene fotogramas de sable
    PELEA_CON_SABLE = False
    #lo que distingue a un tirador de otro. Estan aqui y no en el __init__ para que el
    #voltigeur sea esta misma clase con otros cuatro numeros y otros sprites
    VELOCIDAD = 1
    RECARGA = RECARGA_ENEMIGO
    PUESTOS = PUESTOS_DE_TIRO
    ANDAR_IZQ = Andar_izq_Fr
    ANDAR_DCH = Andar_dch_Fr
    DISPARAR_IZQ = Disparar_izq_Fr
    DISPARAR_DCH = Disparar_dch_Fr

    def __init__(self,x,y,xObjectiv,yObjectiv,enemigosVivos=None):
        enemigo.__init__(self,x,y,xObjectiv,yObjectiv)
        self.vel = self.VELOCIDAD
        #recarga: como la del jugador, el sello de tiempo se pone al disparar. Empieza recargando
        #y con un desfase propio, asi no dispara a bocajarro al aparecer ni a la vez que los demas
        self.recarga = self.RECARGA
        self.instanteUltimoDisparo = (pygame.time.get_ticks()
                                      + random.randint(0, DESFASE_MAXIMO_DESCARGA))
        #su puesto en la linea de tiro: si le dicen quien esta ya en el campo, coge uno libre
        if enemigosVivos is None:
            self.distanciaDeTiro = tomarPuestoDeTiro(self.PUESTOS)
        else:
            self.distanciaDeTiro = puestoLibre(enemigosVivos, self.PUESTOS)
        #y su propio pulso al apuntar
        self.toleranciaPunteria = TOLERANCIA_PUNTERIA + random.randint(0, VARIACION_PUNTERIA)
        #sin esto se le veria el fogonazo al aparecer, antes de haber disparado nada
        self.haDisparado = False

    def puedeDisparar(self, ahora):
        return ahora - self.instanteUltimoDisparo >= self.recarga

    def mostrandoFogonazo(self, ahora):
        return self.haDisparado and ahora - self.instanteUltimoDisparo < DURACION_FOGONAZO

    def encarado(self):
        #a la altura del jugador con un margen, que es lo que le da linea de tiro
        return abs(self.yObjectiv - self.y) <= self.toleranciaPunteria

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
        #y busca su puesto en profundidad: se acerca si esta lejos y RETROCEDE si el jugador se
        #le ha echado encima. Antes solo sabia acercarse, asi que un tirador que aparecia mas
        #cerca que su puesto se quedaba clavado donde entro, amontonado con los que entraron ahi
        haciaElJugador = 1 if xObjectiv > self.x else -1
        distanciaAlJugador = abs(xObjectiv - self.x)
        #recien aparecido esta fuera del campo: lo primero es entrar, su puesto ya se vera
        fueraDelCampo = self.x < 0 or self.x > WINX - self.ANCHO_REFERENCIA
        if fueraDelCampo or distanciaAlJugador > self.distanciaDeTiro + MARGEN_PUESTO:
            self.x += haciaElJugador * self.vel
            moviendose = True
        elif distanciaAlJugador < self.distanciaDeTiro - MARGEN_PUESTO:
            #se retira, pero nunca hasta salirse de la pantalla: un tirador al que no puedes
            #ver ni alcanzar, y que si te dispara, no es un enemigo, es una trampa
            retirada = self.x - haciaElJugador * self.vel
            if 0 <= retirada <= WINX - self.ANCHO_REFERENCIA:
                self.x = retirada
                moviendose = True
        self.stop = not moviendose
        self.actualizarRect()

    def sprite(self):
        if not self.stop:
            secuencia = self.ANDAR_IZQ if self.izq else self.ANDAR_DCH
            imagen = secuencia[self.contadorCaminar // 3]
            self.contadorCaminar = (self.contadorCaminar + 1) % 27
            return imagen
        secuencia = self.DISPARAR_IZQ if self.izq else self.DISPARAR_DCH
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


##Voltigeur: el tirador de la infanteria ligera. El mismo tirador con otros cuatro numeros
class voltigeur(enemigoDistancia):
    #vale mas que el de linea y menos que el granadero: no aguanta mas plomo, pero te dispara
    #desde donde no puedes contestarle sin moverte de donde estas
    PUNTOS = 3
    PROBABILIDAD_SUELTA = 0.32
    VELOCIDAD = VEL_VOLTIGEUR
    RECARGA = RECARGA_VOLTIGEUR
    PUESTOS = PUESTOS_DE_VOLTIGEUR
    ANDAR_IZQ = Andar_izq_Vo
    ANDAR_DCH = Andar_dch_Vo
    DISPARAR_IZQ = Disparar_izq_Vo
    DISPARAR_DCH = Disparar_dch_Vo


##Oficial: no dispara, manda. Los suyos van mas rapidos mientras el siga en pie
class oficial(enemigo):
    #aguanta mas que la tropa pero menos que un granadero: cuatro disparos del mosquete base
    VIDA_INICIAL = VIDA_OFICIAL
    #vale mas que nadie, y no por lo que aguanta: mientras esta en pie, TODOS los demas son
    #mas peligrosos, asi que dejarlo vivo sale mas caro que dejar vivo a cualquier otro
    PUNTOS = 5
    #suelta objeto seguro. Es el enemigo al que hay que ir a buscar, y buscarlo tiene que pagar
    PROBABILIDAD_SUELTA = 1.0
    ANDAR_IZQ = Andar_izq_Of
    ANDAR_DCH = Andar_dch_Of
    ALZAR_IZQ = Alzar_izq_Of
    ALZAR_DCH = Alzar_dch_Of
    TAJAR_IZQ = Tajar_izq_Of
    TAJAR_DCH = Tajar_dch_Of

    def dibujarMando(self,win):
        """El anillo hasta donde llega su mando, pintado en el suelo y a trozos.

        Se dibuja antes que los soldados (ver main.drawWindow) para que quede debajo de todos:
        es una marca del terreno, no algo que flote por encima de la batalla.
        """
        centroX, centroY = self.rect.center
        for paso in range(PASOS_DEL_ANILLO):
            #un trozo si, un trozo no
            if (paso * TROZOS_DEL_ANILLO) // PASOS_DEL_ANILLO % 2:
                continue
            angulo = 2 * math.pi * paso / PASOS_DEL_ANILLO
            x = int(round(centroX + math.cos(angulo) * RADIO_DE_MANDO))
            y = int(round(centroY + math.sin(angulo) * RADIO_DE_MANDO))
            if 0 <= x < WINX and 0 <= y < WINY:
                win.set_at((x, y), COLOR_DE_MANDO)

    def dibujarCadaver(self,win):
        #el cadaver con dorados es suyo: hasta ahora lo llevaba la tropa de bayoneta y el
        #nombre del fichero (cadaverOficialImg) siempre canto que estaba cruzado
        dibujar_anclado(win, cadaverOficialImg, self.x, self.y, self.izq,
                        self.ANCHO_REFERENCIA, self.ALTO_REFERENCIA)


##Granadero de la Guardia: lanza granadas con danio en area
class granadero(enemigo):
    #usa los sprites de andar de 20x36, como el tirador
    ANCHO_REFERENCIA = 20
    ALTO_REFERENCIA = 36
    CUERPO_IZQ = pygame.Rect(0, 0, 20, 36)
    CUERPO_DCH = pygame.Rect(0, 0, 20, 36)
    VIDA_INICIAL = VIDA_GRANADERO
    #cuesta mas de matar, asi que suelta algo mas a menudo
    PROBABILIDAD_SUELTA = 0.40
    #y vale cuatro: 150 de vida y granadas
    PUNTOS = 4
    #va al paso de la tropa: carga el bonete y el saco de granadas
    VELOCIDAD = 1
    #va con el mosquete y las granadas: nada de sable
    PELEA_CON_SABLE = False

    def __init__(self,x,y,xObjectiv,yObjectiv):
        enemigo.__init__(self,x,y,xObjectiv,yObjectiv)
        self.recargaGranada = RECARGA_GRANADA
        #empieza recargando y con desfase propio, como los tiradores
        self.instanteUltimoLanzamiento = (pygame.time.get_ticks()
                                          + random.randint(0, DESFASE_MAXIMO_DESCARGA))
        #armado: esta con el brazo atras y la granada sale al terminar
        self.armando = False
        self.instanteInicioArmado = 0

    # # A que distancia esta de su objetivo

    def distanciaA(self, punto):
        return ((punto[0] - self.rect.centerx) ** 2 + (punto[1] - self.rect.centery) ** 2) ** 0.5

    def aTiro(self, punto):
        return self.distanciaA(punto) <= DISTANCIA_DE_LANZAMIENTO

    def puedeLanzar(self, ahora):
        return ahora - self.instanteUltimoLanzamiento >= self.recargaGranada

    def mostrandoArmado(self, ahora):
        return self.armando

    def mostrandoSuelta(self, ahora):
        return (not self.armando
                and ahora - self.instanteUltimoLanzamiento < DURACION_SUELTA)

    def lanzar(self, granadasEnElAire, puntoObjetivo):
        """Se llama cada frame: arranca el armado cuando toca, y suelta la granada al acabarlo.

        La granada apunta a donde esta el jugador EN EL MOMENTO DE SOLTARLA, no al empezar el
        armado: asi la marca del suelo aparece con el vuelo entero por delante para esquivarla.
        """
        ahora = pygame.time.get_ticks()
        if self.armando:
            if ahora - self.instanteInicioArmado >= DURACION_ARMADO:
                granadasEnElAire.append(granadas.Granada(self.rect.centerx, self.rect.centery,
                                                         puntoObjetivo[0], puntoObjetivo[1], ahora))
                self.armando = False
                self.instanteUltimoLanzamiento = ahora
            return
        #OJO: el alcance se mide contra el MISMO punto con el que pathFinding busca el anillo,
        #que es la esquina del cuerpo del jugador, y no contra puntoObjetivo, que es su centro.
        #Midiendo cada cosa con un punto distinto (se llevan 20 px), el granadero que llegaba
        #por la izquierda o por arriba se plantaba justo en el borde del anillo, a 190 de la
        #esquina pero a 199 del centro, y ya no lanzaba nunca: quieto y sin tirar nada.
        #La granada si se apunta al centro del cuerpo, que es lo que hay que acertar, y eso da
        #igual para el alcance porque el vuelo dura lo mismo caiga donde caiga.
        if self.aTiro((self.xObjectiv, self.yObjectiv)) and self.puedeLanzar(ahora):
            self.armando = True
            self.instanteInicioArmado = ahora

    def pathFinding(self,xObjectiv,yObjectiv):
        self.xObjectiv=xObjectiv
        self.yObjectiv=yObjectiv
        #mira al jugador siempre, tambien plantado
        self.izq = xObjectiv < self.x
        self.dch = not self.izq
        if self.armando:
            #mientras arma el brazo no se mueve
            self.stop = True
            self.actualizarRect()
            return
        #busca el anillo: no necesita ponerse a tu altura, porque una granada cae de arriba
        distancia = self.distanciaA((xObjectiv, yObjectiv))
        moviendose = False
        fueraDelCampo = self.x < 0 or self.x > WINX - self.ANCHO_REFERENCIA
        #se pregunta con aTiro, el mismo predicado que decide si lanza: asi el sitio donde se
        #para y el sitio desde donde lanza no pueden volver a separarse
        if fueraDelCampo or not self.aTiro((xObjectiv, yObjectiv)):
            paso = 1
        elif distancia < DISTANCIA_MINIMA_GRANADERO:
            #demasiado cerca: se retira, o su propia granada le pillaria dentro
            paso = -1
        else:
            paso = 0
        if paso:
            if xObjectiv < self.x:
                self.x -= paso * self.vel
            elif xObjectiv > self.x:
                self.x += paso * self.vel
            if yObjectiv < self.y:
                self.y -= paso * self.vel
            elif yObjectiv > self.y:
                self.y += paso * self.vel
            #no se retira fuera de la pantalla
            self.x = min(max(0, self.x), WINX - self.ANCHO_REFERENCIA)
            self.y = min(max(0, self.y), WINY - self.ALTO_REFERENCIA)
            moviendose = True
        self.stop = not moviendose
        self.actualizarRect()

    def sprite(self):
        ahora = pygame.time.get_ticks()
        if self.mostrandoArmado(ahora):
            return Lanzar_izq_Gr[0] if self.izq else Lanzar_dch_Gr[0]
        if self.mostrandoSuelta(ahora):
            return Lanzar_izq_Gr[1] if self.izq else Lanzar_dch_Gr[1]
        secuencia = Andar_izq_Gr if self.izq else Andar_dch_Gr
        if not self.stop:
            imagen = secuencia[self.contadorCaminar // 3]
            self.contadorCaminar = (self.contadorCaminar + 1) % 27
            return imagen
        return secuencia[0]

    def dibujarCadaver(self,win):
        dibujar_anclado(win, cadaverGranaderoImg, self.x, self.y, self.izq,
                        self.ANCHO_REFERENCIA, self.ALTO_REFERENCIA)
