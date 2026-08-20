# ######################################### Oleadas ###################################################
# Cada oleada trae un cupo cerrado de franceses: no entra ninguno mas hasta que caen todos los
# de la ronda. Al limpiarla hay una calma corta, cae una caja en el campo y empieza la siguiente,
# mas larga y con mas tiradores. No se acaban nunca; la gracia es llegar lo mas lejos posible.
#
# El numero de oleada es ahora el eje de dificultad del juego. Antes lo era el rango del jugador,
# pero teniendo las dos cosas la dificultad subia por partida doble.
CUERPO_A_CUERPO = 'cuerpoACuerpo'
TIRADOR = 'tirador'
GRANADERO = 'granadero'
VOLTIGEUR = 'voltigeur'
OFICIAL = 'oficial'
# El orden en que se miran al sacar del cupo: primero lo raro, que es lo que da variedad
TIPOS = (GRANADERO, OFICIAL, VOLTIGEUR, TIRADOR, CUERPO_A_CUERPO)

PRIMERA_OLEADA = 1
# Lo que se respira entre una oleada y la siguiente
DURACION_CALMA = 3500
# Cupo: la primera trae tres de bayoneta y ningun tirador, para que se aprenda a disparar antes
# de tener que esquivar. A partir de ahi, uno mas de bayoneta por oleada y un tirador cada dos
CUERPO_A_CUERPO_BASE = 2
TIRADORES_CADA = 2
# El granadero es el enemigo duro y el que rompe la tactica de alinearse: aparece a partir de
# la tercera oleada y de uno en uno
PRIMERA_OLEADA_CON_GRANADEROS = 3
GRANADEROS_CADA = 3
# El voltigeur no viene ADEMAS del tirador, viene EN VEZ DE uno de ellos: uno de cada tres
# tiradores de la oleada entra como voltigeur. Asi la oleada se hace mas dura sin hacerse mas
# larga, que es lo mismo que busca el recorte del relleno de mas abajo. Empieza en la cuarta
# para dar una oleada de respiro entre conocer al granadero y conocer al voltigeur
PRIMERA_OLEADA_CON_VOLTIGEURS = 4
TIRADORES_POR_VOLTIGEUR = 3
# El oficial no se recorta como relleno: es de los duros. Aparece en la quinta y de uno en uno,
# porque no suma un cuerpo mas, multiplica a todos los que tenga alrededor
PRIMERA_OLEADA_CON_OFICIALES = 5
OFICIALES_CADA = 7
# Y con tope, que no lo tienen ni los granaderos: el aura NO se acumula (ver
# enemigo.aplicarMando), asi que un cuarto oficial no hace nada que no haga el tercero, y sin
# tope se comia a los tiradores en las oleadas altas (medido: la 40 se quedaba con cero)
TOPE_OFICIALES = 3
# Por debajo de esto una oleada deja de parecer una oleada
MINIMO_CUERPO_A_CUERPO = 4
# Un cupo sin techo acabaria dando rondas eternas, no mas dificiles
TOPE_POR_OLEADA = 24
# Ritmo de entrada dentro de la oleada: cuanto mas alta, mas seguido llegan
INTERVALO_INICIAL = 3600
RECORTE_INTERVALO = 150
INTERVALO_MINIMO = 1100


def composicion(numero):
    """Cuantos franceses de cada tipo trae la oleada, como {tipo: cuantos}."""
    tiradores = numero // TIRADORES_CADA
    if numero < PRIMERA_OLEADA_CON_GRANADEROS:
        granaderos = 0
    else:
        granaderos = 1 + (numero - PRIMERA_OLEADA_CON_GRANADEROS) // GRANADEROS_CADA
    if numero < PRIMERA_OLEADA_CON_OFICIALES:
        oficiales = 0
    else:
        oficiales = min(TOPE_OFICIALES,
                        1 + (numero - PRIMERA_OLEADA_CON_OFICIALES) // OFICIALES_CADA)
    cuerpoACuerpo = CUERPO_A_CUERPO_BASE + numero
    #al llegar al tope se recorta empezando por los de relleno y dejando los duros: si se
    #recortaran los granaderos, las oleadas altas serian mas largas pero mas faciles
    sobra = cuerpoACuerpo + tiradores + granaderos + oficiales - TOPE_POR_OLEADA
    if sobra > 0:
        quitar = min(sobra, cuerpoACuerpo - MINIMO_CUERPO_A_CUERPO)
        cuerpoACuerpo -= max(0, quitar)
        sobra -= max(0, quitar)
    if sobra > 0:
        quitar = min(sobra, tiradores - 1)
        tiradores -= max(0, quitar)
        sobra -= max(0, quitar)
    if sobra > 0:
        quitar = min(sobra, oficiales - 1)
        oficiales -= max(0, quitar)
        sobra -= max(0, quitar)
    if sobra > 0:
        granaderos = max(1, granaderos - sobra)
    #el reparto del voltigeur se hace despues del recorte, sobre los tiradores que sobrevivan:
    #asi el cupo total sale igual que si el voltigeur no existiera
    #y nunca se lleva al ultimo: una oleada sin tiradores de linea perderia un tipo entero
    if numero >= PRIMERA_OLEADA_CON_VOLTIGEURS and tiradores > 1:
        voltigeurs = min(max(1, tiradores // TIRADORES_POR_VOLTIGEUR), tiradores - 1)
        tiradores -= voltigeurs
    else:
        voltigeurs = 0
    return {CUERPO_A_CUERPO: cuerpoACuerpo, TIRADOR: tiradores, VOLTIGEUR: voltigeurs,
            OFICIAL: oficiales, GRANADERO: granaderos}


def intervaloDeEntrada(numero):
    """Milisegundos entre dos franceses de la misma oleada."""
    return max(INTERVALO_MINIMO, INTERVALO_INICIAL - RECORTE_INTERVALO * (numero - 1))


class Oleada(object):
    """El cupo de una oleada y su ritmo de entrada."""

    def __init__(self, numero, ahora):
        self.numero = numero
        self.pendientes = composicion(numero)
        self.intervalo = intervaloDeEntrada(numero)
        #el primero entra en cuanto se levanta la calma, sin esperar su turno
        self.instanteUltimaEntrada = ahora - self.intervalo

    def cupo(self):
        return sum(self.pendientes.values())

    def quedanPorEntrar(self):
        return self.cupo() > 0

    def tocaEntrar(self, ahora):
        return self.quedanPorEntrar() and ahora - self.instanteUltimaEntrada >= self.intervalo

    def sacarSiguiente(self, ahora):
        """Devuelve el tipo del siguiente frances y lo descuenta del cupo."""
        self.instanteUltimaEntrada = ahora
        #los duros se intercalan entre las bayonetas en vez de venir todos juntos al final:
        #toca uno cada tres del cupo, o cuando ya no quedan bayonetas
        for tipo in TIPOS:
            if not self.pendientes[tipo]:
                continue
            if (tipo == CUERPO_A_CUERPO or self.pendientes[CUERPO_A_CUERPO] == 0
                    or self.cupo() % 3 == 0):
                self.pendientes[tipo] -= 1
                return tipo
        self.pendientes[CUERPO_A_CUERPO] -= 1
        return CUERPO_A_CUERPO

    def limpiada(self, enemigosVivos):
        """La oleada se ha superado cuando ya no queda cupo ni nadie vivo en el campo."""
        return not self.quedanPorEntrar() and not enemigosVivos
