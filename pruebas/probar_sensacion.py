"""Pruebas del nivel 1: diagonal, destello al recibir, empujon, sonidos y ventana escalada."""
import math
import sys

import entorno
from entorno import comprobar, resumen
import pygame

pygame.init()
pygame.display.set_mode((500, 500))

import colisiones
import enemigo as E
import jugador as J
import render
import sonidos
from proyectile import proyectil


class TeclasFalsas(object):
    def __init__(self, pulsadas):
        self.pulsadas = pulsadas

    def __getitem__(self, codigo):
        return codigo in self.pulsadas


# ---- 1. andar en diagonal ya no es mas rapido que andar en recto ----
soldado = J.jugador(250, 250)
partida = (soldado.x, soldado.y)
soldado.caminar(TeclasFalsas({pygame.K_RIGHT}))
recto = math.hypot(soldado.x - partida[0], soldado.y - partida[1])

soldado = J.jugador(250, 250)
partida = (soldado.x, soldado.y)
soldado.caminar(TeclasFalsas({pygame.K_RIGHT, pygame.K_DOWN}))
diagonal = math.hypot(soldado.x - partida[0], soldado.y - partida[1])

comprobar("en recto se avanzan 3 px", abs(recto - 3.0) < 0.01, f"{recto:.2f} px")
comprobar("en diagonal ya no se avanza mas que en recto", diagonal <= recto + 0.01,
          f"{diagonal:.2f} px en diagonal contra {recto:.2f} en recto")
comprobar("y sigue mereciendo la pena moverse en diagonal (no es un castigo)",
          diagonal > recto * 0.8, f"{diagonal / recto:.2f} veces el paso recto")
comprobar("el desvio respecto a la velocidad nominal es pequenio",
          abs(diagonal - recto) / recto < 0.10,
          f"{abs(diagonal - recto) / recto * 100:.0f}% (antes era un 41% de mas)")

# ---- 2. el destello: mismo sprite, mas blanco, con la transparencia intacta ----
normal = J.Andar_dch[0]
blanco = render.destello(normal)
comprobar("el destello no toca el original", blanco is not normal)
comprobar("y se cachea: la misma silueta no se blanquea dos veces",
          render.destello(normal) is blanco)
comprobar("mantiene el tamanio", blanco.get_size() == normal.get_size())

opacos = [(x, y) for x in range(normal.get_width()) for y in range(normal.get_height())
          if normal.get_at((x, y))[3] > 20]
transparentes = [(x, y) for x in range(normal.get_width()) for y in range(normal.get_height())
                 if normal.get_at((x, y))[3] == 0]
mas_claros = sum(1 for punto in opacos if sum(blanco.get_at(punto)[:3]) > sum(normal.get_at(punto)[:3]))
comprobar("los pixeles del soldado salen mas claros", mas_claros > len(opacos) * 0.8,
          f"{mas_claros} de {len(opacos)}")
comprobar("y lo transparente sigue transparente",
          all(blanco.get_at(punto)[3] == 0 for punto in transparentes),
          f"{len(transparentes)} pixeles vacios comprobados")

# ---- 3. el destello se enciende al recibir y se apaga solo ----
reloj = {'ms': 10000}
pygame.time.get_ticks = lambda: reloj['ms']

frances = E.enemigo(200, 200, 0, 0)
comprobar("recien aparecido no destella", not frances.mostrandoDestello(reloj['ms']))
frances.recibirImpacto(25)
comprobar("al recibir un impacto destella", frances.mostrandoDestello(reloj['ms']))
reloj['ms'] += E.DURACION_DESTELLO - 1
comprobar("sigue destellando justo antes de cumplirse el tiempo",
          frances.mostrandoDestello(reloj['ms']))
reloj['ms'] += 2
comprobar("y deja de destellar despues", not frances.mostrandoDestello(reloj['ms']))

soldado = J.jugador(250, 250)
comprobar("el jugador tampoco destella de salida", not soldado.mostrandoDestello(reloj['ms']))
soldado.recibirImpacto(25)
comprobar("y destella al recibir un impacto", soldado.mostrandoDestello(reloj['ms']))

# lo que se dibuja cambia de verdad mientras destella
lienzo = pygame.Surface((120, 120), pygame.SRCALPHA)
soldado = J.jugador(40, 40)
lienzo.fill((0, 0, 0, 0))
soldado.dibujar(lienzo)
sano = lienzo.copy()
soldado.recibirImpacto(10)
lienzo.fill((0, 0, 0, 0))
soldado.dibujar(lienzo)
distintos = sum(1 for x in range(120) for y in range(120)
                if sano.get_at((x, y)) != lienzo.get_at((x, y)))
comprobar("lo dibujado cambia mientras destella", distintos > 50, f"{distintos} pixeles distintos")

# ---- 4. el empujon: al enemigo si, al jugador no ----
frances = E.enemigo(200, 200, 0, 0)
antes_x = frances.x
antes_rect = frances.rect.left
frances.recibirImpacto(10, 1)
comprobar("una bala hacia la derecha lo empuja a la derecha",
          frances.x == antes_x + E.EMPUJE_IMPACTO, f"{antes_x} -> {frances.x}")
comprobar("y su caja de colision va con el", frances.rect.left == antes_rect + E.EMPUJE_IMPACTO)

frances = E.enemigo(200, 200, 0, 0)
frances.recibirImpacto(10, -1)
comprobar("una bala hacia la izquierda lo empuja a la izquierda",
          frances.x == 200 - E.EMPUJE_IMPACTO, f"{frances.x}")

soldado = J.jugador(250, 250)
soldado.recibirImpacto(25, -1)
comprobar("al jugador no se le mueve de sitio (no se le quita el control)",
          (soldado.x, soldado.y) == (250, 250), f"({soldado.x}, {soldado.y})")

# el empujon llega desde la resolucion de balas, con el lado del disparo
frances = E.enemigo(300, 250, 0, 0)
frances.actualizarRect()
antes_x = frances.x
municion = [proyectil(frances.rect.left - 8, frances.rect.centery, 1)]
for _ in range(3):
    municion = colisiones.resolverBalas(municion, [frances], 500, 500)
comprobar("resolverBalas empuja en la direccion de la bala", frances.x > antes_x,
          f"{antes_x} -> {frances.x}")

# ---- 5. los sonidos sintetizados existen y no estan mudos ----
for nombre, sonido in (('impacto', sonidos.sonido_impacto), ('muerte', sonidos.sonido_muerte)):
    esNulo = isinstance(sonido, sonidos.SonidoNulo)
    comprobar(f"el sonido de {nombre} se ha podido crear", not esNulo)
    if not esNulo:
        crudo = sonido.get_raw()
        pico = max(crudo[indice] for indice in range(0, len(crudo), 2))
        comprobar(f"el sonido de {nombre} no es silencio", pico > 0, f"pico {pico}")
        comprobar(f"el sonido de {nombre} dura lo previsto",
                  0.02 < sonido.get_length() < 0.5, f"{sonido.get_length() * 1000:.0f} ms")
    sonido.play()
comprobar("sonar no lanza excepciones", True)

# ---- 6. la ventana se escala, pero el juego sigue dibujando en 500x500 ----
juego = entorno.cargarJuego()
comprobar("la ventana mide lo que dice la escala",
          juego['ventana'].get_size() == juego['TAMANIO_VENTANA'],
          str(juego['ventana'].get_size()))
comprobar("pero se sigue dibujando en 500x500", juego['win'].get_size() == (500, 500),
          str(juego['win'].get_size()))
comprobar("la escala es uno de los pasos previstos",
          juego['ESCALA_MINIMA'] <= juego['ESCALA'] <= juego['ESCALA_MAXIMA']
          and (juego['ESCALA'] / juego['PASO_ESCALA']) % 1 == 0,
          "escala " + str(juego['ESCALA']))

juego['win'].fill((10, 90, 40))
juego['presentar']()
ancho, alto = juego['ventana'].get_size()
esquina = juego['ventana'].get_at((0, 0))[:3]
opuesta = juego['ventana'].get_at((ancho - 1, alto - 1))[:3]
comprobar("presentar() llena toda la ventana con lo dibujado",
          esquina == (10, 90, 40) and opuesta == (10, 90, 40), f"{esquina} y {opuesta}")

# ---- 7. la ventana nunca se sale de la pantalla donde se juega ----
escalar = juego['escalaQueCabe']
pantallas = [((1536, 960), "tu escritorio"),
             ((1920, 1080), "1080p"),
             ((2560, 1440), "1440p"),
             ((3840, 2160), "4K"),
             ((1366, 768), "portatil pequenio")]
for tamanio, apodo in pantallas:
    escala = escalar(500, 500, tamanio)
    cabe = (500 * escala <= tamanio[0] - juego['MARGEN_ESCRITORIO_ANCHO']
            and 500 * escala <= tamanio[1] - juego['MARGEN_ESCRITORIO_ALTO'])
    comprobar(f"en {apodo} ({tamanio[0]}x{tamanio[1]}) la ventana cabe", cabe,
              f"escala {escala} -> {int(500 * escala)}x{int(500 * escala)}")

comprobar("en una pantalla de 960 de alto ya no se elige el doble",
          escalar(500, 500, (1536, 960)) < 2.0, str(escalar(500, 500, (1536, 960))))
comprobar("en una pantalla grande se aprovecha hasta el tope",
          escalar(500, 500, (3840, 2160)) == juego['ESCALA_MAXIMA'])
# En una pantalla en la que ni el tamanio nativo entra con margen se queda en el nativo: bajar
# de 500x500 significaria perder pixeles del sprite, que es peor que quedarse justo
comprobar("en una pantalla muy baja se queda en el tamanio nativo",
          escalar(500, 500, (1024, 600)) == juego['ESCALA_MINIMA'],
          str(escalar(500, 500, (1024, 600))))
comprobar("nunca baja del minimo, aunque la pantalla sea diminuta",
          escalar(500, 500, (320, 240)) == juego['ESCALA_MINIMA'])
comprobar("si SDL no sabe el tamanio de la pantalla, se queda en el minimo",
          escalar(500, 500, None) == juego['ESCALA_MINIMA'])

sys.exit(resumen())
