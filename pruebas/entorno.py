"""Preparacion comun de las pruebas.

Hay que importar este modulo ANTES que pygame: es lo que pone SDL en modo sin ventana, de
forma que las pruebas corren sin abrir nada y sin sonar. Tambien deja el directorio de
trabajo en la raiz del repo, porque el juego carga sus assets con rutas relativas.
"""
import os
import sys

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
CAPTURAS = os.path.join(AQUI, 'capturas')

os.chdir(RAIZ)
sys.path.insert(0, RAIZ)
if not os.path.isdir(CAPTURAS):
    os.makedirs(CAPTURAS)

_fallos = []


def comprobar(descripcion, condicion, detalle=""):
    """Apunta una comprobacion, la imprime y guarda el fallo si lo hay."""
    print(('  OK  ' if condicion else ' FALLO ') + descripcion
          + ("   [" + str(detalle) + "]" if detalle else ""))
    if not condicion:
        _fallos.append(descripcion)


def resumen():
    """Imprime el resultado de la bateria y devuelve el codigo de salida (0 si todo bien)."""
    print()
    if _fallos:
        print("RESULTADO: %d fallos -> %s" % (len(_fallos), _fallos))
        return 1
    print("RESULTADO: todo OK")
    return 0


def cargarJuego():
    """Ejecuta main.py sin llegar a su main(), y devuelve sus variables globales.

    Asi se pueden llamar las escenas (menu, partida, pausa, ascenso, gameOver) una a una y
    leer el estado de la partida desde fuera.
    """
    fuente = open('main.py', encoding='utf-8').read()
    juego = {'__name__': 'juego_bajo_prueba'}
    exec(compile(fuente[:fuente.index('\nmain()')], 'main.py', 'exec'), juego)
    return juego


def ruta_captura(nombre):
    return os.path.join(CAPTURAS, nombre)
