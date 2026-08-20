# ##################################### Ascensos del jugador ##########################################
# Cada rango se gana con bajas y trae UNA mejora a elegir entre tres.
# Los topes de las mejoras (3 recortes de recarga + 2 subidas de vida + 2 escalones de danio = 7)
# coinciden con los siete ascensos: al llegar a Coronel lo tienes todo al maximo, pero el orden
# en que llegas hasta ahi lo eliges tu.

RANGOS = ('Soldado raso', 'Cabo', 'Sargento', 'Brigada', 'Teniente', 'Capitan', 'Comandante',
          'Coronel')
# Puntos necesarios para cada rango. No son bajas: cada tipo de frances vale lo suyo (una
# bayoneta 1, un tirador 2, un voltigeur 3, un granadero 4, un oficial 5), porque el rango tiene
# que premiar la dificultad y no el volumen.
#
# Los numeros no estan inventados: son exactamente los puntos acumulados de limpiar las oleadas
# 1 a 7. Como las oleadas son cerradas, hay que matarlos todos para pasar, asi que el total de
# cada una es fijo y sale de oleadas.composicion(). El efecto es que cada una de las siete
# primeras oleadas termina con un ascenso, justo en la calma.
PUNTOS_POR_RANGO = (0, 3, 9, 20, 35, 56, 84, 113)

# ####################################### Mejoras ######################################################
CLAVE_RECARGA = 'recarga'
CLAVE_VIDA = 'vida'
CLAVE_DANIO = 'danio'

# Recarga: es la mejora que mas se nota, porque el danio por segundo esta limitado por ella.
# El suelo son 750 ms; por debajo el fogonazo (180 ms) y el ritmo del juego se vuelven ridiculos
RECORTE_RECARGA = 250
SUELO_RECARGA = 750
# Vida: +25 son unos 1.5 s mas de aguante rodeado, y el ascenso cura otros 25
SUBIDA_VIDA = 25
TECHO_VIDA = 150
# Danio: con franceses de 75 de vida, subirlo de 25 a 26...37 no cambia nada, siguen haciendo
# falta 3 disparos. Los unicos valores que se notan son 38 (2 disparos) y 75 (1 disparo)
ESCALONES_DANIO = (38, 75)
# La polvora no se ofrece hasta Brigada. Medido: pedirla primero llega a Coronel en 1:35 y
# pedir coraza primero tarda 3:30, porque el danio divide los disparos por frances (3 -> 2 -> 1)
# mientras la recarga solo va de 1500 a 750. Reservandola, las dos primeras elecciones son
# de verdad una eleccion: recarga contra coraza
RANGO_MINIMO_POLVORA = 3

# La dificultad ya no depende del rango: la lleva el numero de oleada (ver oleadas.py). Con las
# dos cosas a la vez subia por partida doble, porque los rangos se ganan matando y matar es
# justo lo que hace avanzar las oleadas.


class Mejora(object):
    """Una de las tres opciones que se ofrecen al ascender."""

    def __init__(self, clave, nombre, efecto, disponible):
        self.clave = clave
        self.nombre = nombre
        self.efecto = efecto
        self.disponible = disponible


class Progreso(object):
    """Bajas, puntos y rango del jugador en la partida en curso.

    Las bajas y los puntos son dos cosas distintas a proposito: las bajas son cuantos franceses
    han caido (lo que se ensenia y lo que guarda el record) y los puntos son lo que valian (lo
    que decide el rango).
    """

    def __init__(self):
        self.bajas = 0
        self.puntos = 0
        self.rango = 0

    def nombreRango(self):
        return RANGOS[self.rango]

    def esRangoMaximo(self):
        return self.rango + 1 >= len(RANGOS)

    def puntosParaAscender(self):
        #None cuando ya no queda rango al que subir
        if self.esRangoMaximo():
            return None
        return PUNTOS_POR_RANGO[self.rango + 1]

    def apuntarBajas(self, cuantas, puntos=None):
        """Apunta las bajas y lo que valian. Sin puntos, cada baja vale uno."""
        self.bajas += cuantas
        self.puntos += cuantas if puntos is None else puntos

    def tocaAscender(self):
        siguiente = self.puntosParaAscender()
        return siguiente is not None and self.puntos >= siguiente

    def ascender(self):
        if not self.esRangoMaximo():
            self.rango += 1


def siguienteDanio(danioActual):
    for escalon in ESCALONES_DANIO:
        if escalon > danioActual:
            return escalon
    return danioActual


def disparosParaMatar(danio, vidaEnemigo):
    #para poder contarlo en el cartel del ascenso
    return -(-vidaEnemigo // danio)


TEXTO_AL_MAXIMO = 'ya esta al maximo'


def mejorasDisponibles(soldado, vidaEnemigo, rango):
    """Las tres mejoras, siempre en el mismo orden, para que 1/2/3 signifiquen lo mismo.

    Cada una trae ya escrito lo que hace, o por que no se puede pedir todavia.
    """
    quedaRecarga = soldado.recarga > SUELO_RECARGA
    quedaVida = soldado.vidaMaxima < TECHO_VIDA
    quedaPolvora = soldado.danioBala < ESCALONES_DANIO[-1]
    polvoraDesbloqueada = rango >= RANGO_MINIMO_POLVORA

    if quedaRecarga:
        efectoRecarga = 'recarga %d ms' % max(SUELO_RECARGA, soldado.recarga - RECORTE_RECARGA)
    else:
        efectoRecarga = TEXTO_AL_MAXIMO

    if quedaVida:
        efectoVida = 'vida maxima %d y cura %d' % (min(TECHO_VIDA, soldado.vidaMaxima + SUBIDA_VIDA),
                                                  SUBIDA_VIDA)
    else:
        efectoVida = TEXTO_AL_MAXIMO

    if not quedaPolvora:
        efectoPolvora = TEXTO_AL_MAXIMO
    elif not polvoraDesbloqueada:
        efectoPolvora = 'reservada a los oficiales: desde %s' % RANGOS[RANGO_MINIMO_POLVORA]
    else:
        danioMejorado = siguienteDanio(soldado.danioBala)
        efectoPolvora = 'dano %d, %d disparos por frances' % (
            danioMejorado, disparosParaMatar(danioMejorado, vidaEnemigo))

    return [
        Mejora(CLAVE_RECARGA, 'Mosquete afinado', efectoRecarga, quedaRecarga),
        Mejora(CLAVE_VIDA, 'Coraza', efectoVida, quedaVida),
        Mejora(CLAVE_DANIO, 'Polvora doble', efectoPolvora, quedaPolvora and polvoraDesbloqueada),
    ]


def aplicar(soldado, clave):
    """Aplica al soldado la mejora elegida, respetando su tope."""
    if clave == CLAVE_RECARGA:
        soldado.recarga = max(SUELO_RECARGA, soldado.recarga - RECORTE_RECARGA)
    elif clave == CLAVE_VIDA:
        soldado.vidaMaxima = min(TECHO_VIDA, soldado.vidaMaxima + SUBIDA_VIDA)
        soldado.vida = min(soldado.vidaMaxima, soldado.vida + SUBIDA_VIDA)
    elif clave == CLAVE_DANIO:
        soldado.danioBala = siguienteDanio(soldado.danioBala)


