import random

import pygame

import sonidos

pygame.init()

# ################################### Objetos del campo de batalla ####################################
# Los franceses caidos sueltan cosas. Cada objeto responde a un aprieto distinto, para que
# recogerlo sea una decision y no un reflejo: ir a por las vendas puede costarte una bayoneta.
CLAVE_VENDAS = 'vendas'
CLAVE_CARTUCHERA = 'cartuchera'
CLAVE_AGUARDIENTE = 'aguardiente'
CLAVE_ESTANDARTE = 'estandarte'

# Cuanto aguanta en el suelo, y desde cuando avisa parpadeando de que se va
DURACION_EN_SUELO = 10000
AVISO_ANTES_DE_IRSE = 2500
PARPADEOS_POR_SEGUNDO = 4

LADO_ICONO = 12

# Efectos
CURA_VENDAS = 25
DISPAROS_DE_CARTUCHERA = 3
DURACION_AGUARDIENTE = 5000
DURACION_ESTANDARTE = 8000

# Lo que sale mas a menudo. Las vendas son lo mas comun porque son lo que siempre hace falta
PESOS = ((CLAVE_VENDAS, 40), (CLAVE_CARTUCHERA, 30), (CLAVE_AGUARDIENTE, 15),
         (CLAVE_ESTANDARTE, 15))

NOMBRES = {CLAVE_VENDAS: 'Vendas',
           CLAVE_CARTUCHERA: 'Cartuchera',
           CLAVE_AGUARDIENTE: 'Aguardiente',
           CLAVE_ESTANDARTE: 'Estandarte'}

# Lo que hace cada uno, dicho en la pantalla al recogerlo: un icono de 12x12 no puede
# explicar por si solo que un trago de aguardiente te deja cruzar entre bayonetas
DESCRIPCIONES = {CLAVE_VENDAS: '+%d de vida' % CURA_VENDAS,
                 CLAVE_CARTUCHERA: '%d disparos sin recargar' % DISPAROS_DE_CARTUCHERA,
                 CLAVE_AGUARDIENTE: 'inmune al contacto %d s' % (DURACION_AGUARDIENTE // 1000),
                 CLAVE_ESTANDARTE: 'dano doble %d s' % (DURACION_ESTANDARTE // 1000)}


# ##################################### Iconos dibujados a mano #######################################
# En el repo no hay ni un sprite de objeto, asi que se dibujan con primitivas. A 12x12 y sobre
# hierba se leen bien, y el dia que existan sprites de verdad basta con cambiar esta funcion.
def _lienzo():
    return pygame.Surface((LADO_ICONO, LADO_ICONO), pygame.SRCALPHA)


def _iconoVendas():
    icono = _lienzo()
    icono.fill((242, 242, 236))
    pygame.draw.rect(icono, (120, 120, 114), icono.get_rect(), 1)
    pygame.draw.rect(icono, (188, 34, 40), pygame.Rect(5, 2, 2, 8))
    pygame.draw.rect(icono, (188, 34, 40), pygame.Rect(2, 5, 8, 2))
    return icono


def _iconoCartuchera():
    icono = _lienzo()
    pygame.draw.rect(icono, (96, 62, 30), pygame.Rect(0, 2, LADO_ICONO, 9))
    pygame.draw.rect(icono, (54, 34, 16), pygame.Rect(0, 2, LADO_ICONO, 9), 1)
    #la correa cruzada y el cierre
    pygame.draw.line(icono, (188, 160, 120), (0, 4), (LADO_ICONO - 1, 4))
    pygame.draw.rect(icono, (214, 190, 96), pygame.Rect(5, 5, 3, 3))
    return icono


def _iconoAguardiente():
    icono = _lienzo()
    #cristal ambar, no verde: una botella verde sobre hierba verde no se distingue de nada
    pygame.draw.rect(icono, (86, 54, 22), pygame.Rect(5, 0, 3, 2))       # el corcho
    pygame.draw.rect(icono, (196, 126, 40), pygame.Rect(5, 2, 3, 3))     # el cuello
    pygame.draw.rect(icono, (214, 146, 52), pygame.Rect(2, 5, 9, 7))     # el cuerpo
    pygame.draw.rect(icono, (120, 70, 20), pygame.Rect(2, 5, 9, 7), 1)   # el contorno
    pygame.draw.line(icono, (248, 208, 130), (4, 6), (4, 10))            # el brillo del cristal
    pygame.draw.rect(icono, (244, 238, 216), pygame.Rect(6, 7, 4, 3))    # la etiqueta
    return icono


def _iconoEstandarte():
    icono = _lienzo()
    #asta
    pygame.draw.rect(icono, (140, 108, 66), pygame.Rect(2, 0, 2, LADO_ICONO))
    #panio al viento, con la cruz
    pygame.draw.rect(icono, (176, 32, 42), pygame.Rect(4, 1, 8, 6))
    pygame.draw.line(icono, (238, 238, 232), (4, 4), (11, 4))
    pygame.draw.line(icono, (238, 238, 232), (7, 1), (7, 6))
    return icono


ICONOS = {CLAVE_VENDAS: _iconoVendas(),
          CLAVE_CARTUCHERA: _iconoCartuchera(),
          CLAVE_AGUARDIENTE: _iconoAguardiente(),
          CLAVE_ESTANDARTE: _iconoEstandarte()}


# ####################################### El objeto en el suelo #######################################
class objeto(object):
    def __init__(self, clave, x, y, ahora):
        self.clave = clave
        self.icono = ICONOS[clave]
        #(x, y) es el centro: los objetos caen donde cayo el frances
        self.rect = self.icono.get_rect(center=(x, y))
        self.instanteAparicion = ahora

    def nombre(self):
        return NOMBRES[self.clave]

    def caducado(self, ahora):
        return ahora - self.instanteAparicion >= DURACION_EN_SUELO

    def visible(self, ahora):
        """Parpadea en sus ultimos segundos, para avisar de que se va."""
        restante = DURACION_EN_SUELO - (ahora - self.instanteAparicion)
        if restante > AVISO_ANTES_DE_IRSE:
            return True
        return int(restante / (1000.0 / PARPADEOS_POR_SEGUNDO / 2)) % 2 == 0

    def dibujar(self, win, ahora):
        if self.visible(ahora):
            win.blit(self.icono, self.rect)


# ####################################### Sueltas y recogidas #########################################
def _claveAlAzar():
    total = sum(peso for _, peso in PESOS)
    tirada = random.uniform(0, total)
    acumulado = 0
    for clave, peso in PESOS:
        acumulado += peso
        if tirada <= acumulado:
            return clave
    return PESOS[0][0]


def sueltaDe(caido, ahora):
    """Lo que deja un frances al caer, o None. La probabilidad la pone cada tipo de enemigo."""
    if random.random() >= caido.PROBABILIDAD_SUELTA:
        return None
    return objeto(_claveAlAzar(), caido.rect.centerx, caido.rect.centery, ahora)


def sueltaGarantizada(x, y, ahora):
    """Un objeto seguro, para premiar el haber limpiado una oleada."""
    return objeto(_claveAlAzar(), x, y, ahora)


def aplicar(clave, soldado, ahora):
    """Le da al soldado lo que llevaba el objeto."""
    if clave == CLAVE_VENDAS:
        soldado.vida = min(soldado.vidaMaxima, soldado.vida + CURA_VENDAS)
    elif clave == CLAVE_CARTUCHERA:
        soldado.disparosGratis += DISPAROS_DE_CARTUCHERA
    elif clave == CLAVE_AGUARDIENTE:
        soldado.instanteFinInmunidad = ahora + DURACION_AGUARDIENTE
    elif clave == CLAVE_ESTANDARTE:
        soldado.instanteFinDanioDoble = ahora + DURACION_ESTANDARTE


def recogerYCaducar(objetosEnSuelo, soldado, ahora):
    """Guarda en la mochila lo que el soldado pisa y retira lo caducado.

    Recoger no gasta el objeto: lo deja en la mochila hasta que se pulse la tecla de usar.
    Si ya llevaba algo, lo nuevo lo sustituye: pisar un objeto es voluntario, y bloquear la
    mochila dejaria al jugador atascado con algo que no le sirve.
    Devuelve (lo que sigue en el suelo, las claves recogidas en este frame).
    """
    siguen = []
    recogidos = []
    for cosa in objetosEnSuelo:
        if soldado.rect.colliderect(cosa.rect):
            soldado.objetoEnMochila = cosa.clave
            sonidos.sonido_mochila.play()
            recogidos.append(cosa.clave)
        elif not cosa.caducado(ahora):
            siguen.append(cosa)
    return siguen, recogidos


def usar(soldado, ahora):
    """Gasta lo que el soldado lleve en la mochila. Devuelve la clave usada, o None."""
    clave = soldado.objetoEnMochila
    if clave is None:
        return None
    aplicar(clave, soldado, ahora)
    soldado.objetoEnMochila = None
    sonidos.sonido_objeto.play()
    return clave
