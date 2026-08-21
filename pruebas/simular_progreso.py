"""Simula una partida entera con un bot que apunta, para ver la curva de ascensos."""
import os
import sys

import entorno
from entorno import comprobar, resumen
import pygame

pygame.init()

juego = entorno.cargarJuego()

import ascensos
import jugador as J

FPS = 30
MS_POR_FRAME = 1000 // FPS
MINUTOS_MAXIMOS = float(os.environ.get('MINUTOS', '10'))
# orden en que el bot pide las mejoras: 1 recarga, 3 polvora, 2 coraza
PRIORIDAD = (ascensos.CLAVE_RECARGA, ascensos.CLAVE_DANIO, ascensos.CLAVE_VIDA)
TECLA_DE_CLAVE = {ascensos.CLAVE_RECARGA: pygame.K_1,
                  ascensos.CLAVE_VIDA: pygame.K_2,
                  ascensos.CLAVE_DANIO: pygame.K_3}

reloj = {'ms': 1000}
pygame.time.get_ticks = lambda: reloj['ms']


class TiempoFalso:
    def perf_counter(self):
        return reloj['ms'] / 1000.0


class RelojFalso:
    def tick(self, *args):
        reloj['ms'] += MS_POR_FRAME
        return MS_POR_FRAME


class TeclasFalsas:
    def __init__(self, pulsadas):
        self.pulsadas = pulsadas

    def __getitem__(self, codigo):
        return codigo in self.pulsadas


juego['time'] = TiempoFalso()
juego['clock'] = RelojFalso()

control = {'teclas': set(), 'eventos': [], 'frames': 0, 'modo': 'partida'}
pygame.event.get = lambda *a, **k: [control['eventos'].pop(0)] if control['eventos'] else []
pygame.key.get_pressed = lambda: TeclasFalsas(control['teclas'])

historial = []
# Danio recibido por oleada. Es la unica medida de dificultad que no depende de lo bien o lo mal
# que juegue el bot: si se deja acorralar en una esquina muere y no mide nada, pero el plomo que
# le entra por segundo sale igual. Con INMORTAL=1 se le cura cada frame y aguanta la partida
# entera, asi que se puede comparar oleada con oleada.
danioPorOleada = {}
framesPorOleada = {}


def elegirMejora():
    mejoras = {mejora.clave: mejora
           for mejora in ascensos.mejorasDisponibles(juego['player'], 75, juego['progreso'].rango)}
    for clave in PRIORIDAD:
        if mejoras[clave].disponible:
            return TECLA_DE_CLAVE[clave]
    return pygame.K_1


# ####################################### El bot ######################################################
# Con un solo umbral el bot se pasaba la partida huyendo y no disparaba nunca: en cuanto se
# paraba, el de bayoneta volvia a entrar en su distancia de peligro. Con dos umbrales gana aire
# hasta AIRE_SUFICIENTE y solo vuelve a huir cuando le llegan a DISTANCIA_DE_PELIGRO, que es
# como se juega esto de verdad: correr, girarse y disparar.
#
# Y huia EN LINEA RECTA hacia el lado contrario del que tenia encima, que es lo que le metia en
# las esquinas: en una esquina "el lado contrario" es la pared, asi que se quedaba clavado
# disparando al aire mientras las bayonetas lo molian. Medido: de 10 partidas, 7 morian entre
# 55 y 110 s y 3 sobrevivian los 10 minutos sin pasar de la oleada 1, y el danio por segundo
# salia mayor en la oleada 2 que en la 3, al reves de la realidad.
#
# Ahora PUNTUA las nueve opciones (las ocho direcciones y quedarse quieto) y se queda con la
# mejor. La puntuacion suma el aire que gana respecto al frances mas cercano y el sitio que le
# queda hasta el borde, asi que una esquina deja de ser una trampa: salir pegado a la pared
# puntua mejor que meterse en el vertice, y quedarse quieto puntua peor que cualquier salida.
DISTANCIA_DE_PELIGRO = 100
AIRE_SUFICIENTE = 200
# Cuanto sitio hasta el borde se considera ya "de sobra": a partir de aqui, mas espacio no
# puntua mas. Sin este tope el bot se pasaba la partida buscando el centro del mapa
HOLGURA_DE_SOBRA = 70
# Lo que pesa el sitio hasta el borde frente al aire. Por encima de 1 el bot prefiere salir del
# rincon aunque le cueste acercarse un poco al frances, que es justo lo que hace un humano
PESO_DEL_BORDE = 1.4
# Margen de alineacion con el que se da por encarado y dispara en vez de seguir colocandose
MARGEN_DE_PUNTERIA = 4
# El bot tambien pelea de cerca, porque si no no puede medir el cuerpo a cuerpo: estoca a lo que
# tenga a punta de bayoneta, y dashea cuando ve un sable subiendo dentro de su alcance. Ese es el
# bucle que se quiere medir (picar, salir, volver), no una floritura

TECLAS_POR_DIRECCION = {
    (0, 0): frozenset(),
    (0, -1): frozenset([pygame.K_UP]),
    (0, 1): frozenset([pygame.K_DOWN]),
    (-1, 0): frozenset([pygame.K_LEFT]),
    (1, 0): frozenset([pygame.K_RIGHT]),
    (-1, -1): frozenset([pygame.K_LEFT, pygame.K_UP]),
    (-1, 1): frozenset([pygame.K_LEFT, pygame.K_DOWN]),
    (1, -1): frozenset([pygame.K_RIGHT, pygame.K_UP]),
    (1, 1): frozenset([pygame.K_RIGHT, pygame.K_DOWN]),
}


def _aire(x, y, enemigos):
    """Distancia al frances mas cercano desde un punto."""
    return min(((x - enemigo.x) ** 2 + (y - enemigo.y) ** 2) ** 0.5 for enemigo in enemigos)


def _holguraAlBorde(x, y):
    """Lo que queda hasta el borde mas cercano, sin pasar de HOLGURA_DE_SOBRA."""
    hasta = min(x, y, 500 - J.ANCHO_CUERPO - x, 500 - J.ALTO_CUERPO - y)
    return min(max(0.0, hasta), HOLGURA_DE_SOBRA)


def _dondeCaeria(soldado, direccion):
    """Donde acabaria el soldado si pulsara esas teclas este frame."""
    avanceX, avanceY = direccion
    paso = J.VELOCIDAD_DIAGONAL if avanceX and avanceY else J.VELOCIDAD
    x = min(max(0, soldado.x + avanceX * paso), 500 - J.ANCHO_CUERPO)
    y = min(max(0, soldado.y + avanceY * paso), 500 - J.ALTO_CUERPO)
    return x, y


def _mejorEscapada(soldado, enemigos):
    """Las teclas de la direccion que mas aire y mas sitio deja."""
    mejores = None
    teclasElegidas = frozenset()
    for direccion, teclas in TECLAS_POR_DIRECCION.items():
        x, y = _dondeCaeria(soldado, direccion)
        puntos = _aire(x, y, enemigos) + PESO_DEL_BORDE * _holguraAlBorde(x, y)
        #quedarse quieto solo gana si de verdad es la mejor opcion, no por empate
        if mejores is None or puntos > mejores + 0.001:
            mejores = puntos
            teclasElegidas = teclas
    return set(teclasElegidas)


def _pulsar(tecla):
    """La bayoneta y el dash van por pulsacion, asi que hay que meter el evento en la cola."""
    control['eventos'].append(pygame.event.Event(pygame.KEYDOWN, key=tecla))


def _sableViniendo(soldado, enemigos):
    """El primero que tenga el sable en alto y a este ya dentro de su alcance."""
    for enemigo in enemigos:
        if getattr(enemigo, 'alzandoSable', False) and enemigo.alcanceDelSable().colliderect(soldado.rect):
            return enemigo
    return None


def pelearDeCerca(soldado, enemigos):
    """Estoca y dashea como lo haria una persona. Devuelve si el dash le ha quitado el turno."""
    ahora = pygame.time.get_ticks()
    #primero salvar la vida: si hay un sable cayendo encima, salir de ahi
    if _sableViniendo(soldado, enemigos) and soldado.puedeDashear(ahora):
        _pulsar(juego['TECLAS_DASH'][0])
        return True
    #y si no, aprovechar: a punta de bayoneta pega el acero, que va cuatro veces mas rapido
    if soldado.puedeEstocar(ahora):
        caja = soldado.cajaDeLaBayoneta()
        if any(caja.colliderect(enemigo.rect) for enemigo in enemigos):
            _pulsar(juego['TECLA_BAYONETA'])
    return False


def pilotarBot():
    """Gana aire cuando lo tiene encima y, si no, se alinea con el blanco mas facil y dispara."""
    soldado = juego['player']
    enemigos = juego['enemies']
    if not enemigos:
        control['teclas'] = set()
        return
    if pelearDeCerca(soldado, enemigos):
        #en mitad de un dash no se anda: el dash manda
        control['teclas'] = set()
        return
    aire = _aire(soldado.x, soldado.y, enemigos)
    if aire < DISTANCIA_DE_PELIGRO:
        control['huyendo'] = True
    elif aire >= AIRE_SUFICIENTE:
        control['huyendo'] = False
    if control.get('huyendo'):
        #se dispara igual mientras se corre: si alguien se pone delante, cae
        control['teclas'] = _mejorEscapada(soldado, enemigos) | {pygame.K_SPACE}
        return
    #el blanco mas facil no es el mas cercano, es el que ya esta casi a tu altura
    objetivo = min(enemigos, key=lambda enemigo: abs(enemigo.y - soldado.y))
    haciaLaIzquierda = objetivo.x < soldado.x
    teclas = set([pygame.K_SPACE])
    if abs(objetivo.y - soldado.y) > MARGEN_DE_PUNTERIA:
        teclas.add(pygame.K_DOWN if objetivo.y > soldado.y else pygame.K_UP)
    elif soldado.mirando_izq != haciaLaIzquierda:
        #encararlo cuesta un paso, porque la orientacion solo cambia al andar
        teclas.add(pygame.K_LEFT if haciaLaIzquierda else pygame.K_RIGHT)
    control['teclas'] = teclas


def display_update_falso(*args, **kwargs):
    control['frames'] += 1
    numeroOleada = juego['oleada'].numero
    if numeroOleada != control.get('ultimaOleada'):
        control['ultimaOleada'] = numeroOleada
        print('%5.0f OLEADA %-22d %8d %8d %5d %6d %5d'
              % (reloj['ms'] / 1000.0, numeroOleada, juego['player'].recarga,
                 juego['player'].vidaMaxima, juego['player'].danioBala,
                 juego['progreso'].bajas, len(juego['enemies'])))
    #el tope de frames se comprueba aqui y no solo entre escenas: con el bot inmortal,
    #partida() no vuelve nunca y el bucle de fuera no llegaba a cortar
    #el danio se mide ANTES de curar, y se recorta por abajo porque un ascenso o un aguardiente
    #suben la vida y eso no es danio negativo
    vidaAhora = juego['player'].vida
    perdida = max(0, control.get('vidaAnterior', vidaAhora) - vidaAhora)
    framesPorOleada[numeroOleada] = framesPorOleada.get(numeroOleada, 0) + 1
    if perdida:
        danioPorOleada[numeroOleada] = danioPorOleada.get(numeroOleada, 0) + perdida
    control['vidaAnterior'] = vidaAhora
    if control['frames'] >= frames_maximos:
        juego['player'].vida = 0
    elif os.environ.get('INMORTAL'):
        juego['player'].vida = juego['player'].vidaMaxima
        control['vidaAnterior'] = juego['player'].vida
    if control['modo'] == 'partida':
        pilotarBot()
    else:
        if control['frames'] % 3 == 0:
            control['eventos'].append(pygame.event.Event(pygame.KEYDOWN, key=elegirMejora()))


frames_maximos = int(MINUTOS_MAXIMOS * 60 * FPS)
pygame.display.update = display_update_falso

juego['reiniciarPartida']()
progreso = juego['progreso']
escena = juego['ESCENA_PARTIDA']

print(f"{'seg':>5} {'suceso':<28} {'recarga':>8} {'vidaMax':>8} {'dano':>5} {'bajas':>6} {'enem':>5}")
while escena == juego['ESCENA_PARTIDA'] or escena == juego['ESCENA_ASCENSO']:
    if control['frames'] >= frames_maximos:
        print(f"{reloj['ms']/1000:5.0f} {'fin del tiempo simulado':<28}")
        break
    if escena == juego['ESCENA_PARTIDA']:
        control['modo'] = 'partida'
        escena = juego['partida']()
    else:
        control['modo'] = 'ascenso'
        escena = juego['ascenso']()
        soldado = juego['player']
        historial.append((reloj['ms'] / 1000.0, 'ascenso a ' + progreso.nombreRango(),
                          soldado.recarga, soldado.vidaMaxima, soldado.danioBala,
                          progreso.bajas, len(juego['enemies'])))
        print(f"{historial[-1][0]:5.0f} {historial[-1][1]:<28} {soldado.recarga:8d} "
              f"{soldado.vidaMaxima:8d} {soldado.danioBala:5d} {progreso.bajas:6d} {len(juego['enemies']):5d}")

soldado = juego['player']
if escena == juego['ESCENA_GAME_OVER']:
    print(f"{reloj['ms']/1000:5.0f} {'MUERTO siendo ' + progreso.nombreRango():<28} "
          f"{soldado.recarga:8d} {soldado.vidaMaxima:8d} {soldado.danioBala:5d} {progreso.bajas:6d} {len(juego['enemies']):5d}")
print()
print(f"frames simulados: {control['frames']} ({control['frames']/FPS:.0f} s de juego)")
print(f"ascensos conseguidos: {len(historial)} de 7")
print(f"oleada alcanzada: {juego['oleada'].numero}")
if danioPorOleada:
    print()
    print(f"{'oleada':>6} {'segundos':>9} {'dano':>7} {'dano/s':>8}")
    for numero in sorted(framesPorOleada):
        segundos = framesPorOleada[numero] / FPS
        danio = danioPorOleada.get(numero, 0)
        print(f"{numero:6d} {segundos:9.0f} {danio:7d} {danio / max(1.0, segundos):8.1f}")
    total = sum(danioPorOleada.values())
    print(f"{'TOTAL':>6} {total:14d}   ({total / max(1, control['frames'] / FPS):.1f} por segundo)")
