"""Pruebas del bloque 4: reparto de danio, listas sin saltos y gracia entre golpes."""
import sys

import entorno
from entorno import comprobar, resumen
import pygame

pygame.init()
pygame.display.set_mode((500, 500))

import colisiones
import jugador as J
import enemigo as E
from proyectile import proyectil



def balaHacia(objetivo, desde_x=None):
    """Una bala colocada justo a la izquierda del objetivo y avanzando hacia el."""
    x = objetivo.rect.left - 8 if desde_x is None else desde_x
    return proyectil(x, objetivo.rect.centery, 1)


# ---- 1. una bala = un impacto = danio exacto ----
frances = E.enemigo(200, 200, 0, 0)
vida_inicial = frances.vida
balas = [balaHacia(frances)]
balas = colisiones.resolverBalas(balas, [frances], 500, 500)
comprobar("una bala resta exactamente su danio", vida_inicial - frances.vida == 25,
          f"{vida_inicial} -> {frances.vida}")
comprobar("la bala desaparece al impactar", balas == [])

# ---- 2. la bala no sigue restando vida frame tras frame ----
frances = E.enemigo(200, 200, 0, 0)
balas = [balaHacia(frances)]
for _ in range(10):
    balas = colisiones.resolverBalas(balas, [frances], 500, 500)
comprobar("tras 10 frames el danio sigue siendo de un solo impacto", frances.vida == 50,
          f"vida={frances.vida}")

# ---- 3. varias balas a la vez: el danio no se multiplica ----
frances = E.enemigo(200, 200, 0, 0)
balas = [balaHacia(frances, 150), balaHacia(frances, 160), balaHacia(frances, 170)]
vida = frances.vida
for _ in range(15):
    balas = colisiones.resolverBalas(balas, [frances], 500, 500)
comprobar("tres balas restan 75, ni mas ni menos", vida - frances.vida == 75,
          f"{vida} -> {frances.vida}")
frances.checkEstadoVida()
comprobar("con 75 de danio el enemigo cae", not frances.vivo)

# ---- 4. una bala impacta en un solo enemigo, aunque haya dos superpuestos ----
primero = E.enemigo(200, 200, 0, 0)
segundo = E.enemigo(205, 200, 0, 0)
balas = [balaHacia(primero)]
for _ in range(4):
    balas = colisiones.resolverBalas(balas, [primero, segundo], 500, 500)
tocados = [enemigo for enemigo in (primero, segundo) if enemigo.vida < 75]
comprobar("una bala solo hiere a un enemigo", len(tocados) == 1,
          f"vidas={primero.vida},{segundo.vida}")

# ---- 5. las balas que salen de pantalla se eliminan todas, sin saltarse ninguna ----
balas = [proyectil(495, 250, 1) for _ in range(5)]
for _ in range(3):
    balas = colisiones.resolverBalas(balas, [], 500, 500)
comprobar("las 5 balas fuera de pantalla se eliminan", balas == [], f"quedan {len(balas)}")

# ---- 6. separarCaidos no se salta enemigos (el bug del pop mientras se itera) ----
enemigos = [E.enemigo(100 + i * 10, 200, 0, 0) for i in range(6)]
for enemigo in enemigos:          # matamos los 4 primeros, que es donde el pop se saltaba uno
    enemigo.vida = 0
    enemigo.checkEstadoVida()
    if enemigo is enemigos[3]:
        break
vivos, caidos = colisiones.separarCaidos(enemigos)
comprobar("caen los 4 muertos de golpe", len(caidos) == 4 and len(vivos) == 2,
          f"vivos={len(vivos)} caidos={len(caidos)}")
comprobar("la lista original no se toca", len(enemigos) == 6)

# ---- 7. contacto: con la gracia entre golpes ya no son 105 de vida por segundo ----
soldado = J.jugador(200, 200)
frances = E.enemigo(200, 200, 0, 0)
frances.actualizarRect()
inicio = pygame.time.get_ticks()
frames = 0
while pygame.time.get_ticks() - inicio < 1000:      # un segundo de contacto continuo
    soldado.sufrirContacto([frances])
    frames += 1
perdida = 100 - soldado.vida
golpes_esperados = 1000 // J.GRACIA_CONTACTO
comprobar("un segundo pegado a un enemigo cuesta unos pocos golpes, no uno por frame",
          perdida <= (golpes_esperados + 1) * J.DANIO_CONTACTO,
          f"{frames} frames, vida perdida={perdida}")
comprobar("pero el contacto duele algo", perdida >= J.DANIO_CONTACTO, f"perdida={perdida}")

# ---- 8. las balas enemigas hieren al jugador una sola vez ----
soldado = J.jugador(200, 200)
bala_enemiga = proyectil(soldado.rect.left - 8, soldado.rect.centery, 1)
balasEnemigas = [bala_enemiga]
for _ in range(6):
    balasEnemigas = colisiones.resolverBalas(balasEnemigas, [soldado], 500, 500)
comprobar("una bala enemiga resta 25 de vida una sola vez", soldado.vida == 75,
          f"vida={soldado.vida}")
comprobar("la bala enemiga se consume", balasEnemigas == [])

# ---- 9. la bala lleva un vector de avance, no solo velocidad horizontal ----
recta = proyectil(100, 250, 1)
comprobar("por defecto la bala sale en horizontal",
          recta.avanceX == 8 and recta.avanceY == 0, f"({recta.avanceX}, {recta.avanceY})")
partida_x, partida_y = recta.rect.centerx, recta.rect.centery
recta.mover()
comprobar("y avanza 8 px en x sin desviarse en y",
          recta.rect.centerx - partida_x == 8 and recta.rect.centery == partida_y)

diagonal = proyectil(100, 250, 1, 25, avanceX=6, avanceY=-4)
partida_x, partida_y = diagonal.rect.centerx, diagonal.rect.centery
diagonal.mover()
comprobar("con vector propio se mueve en los dos ejes",
          diagonal.rect.centerx - partida_x == 6 and diagonal.rect.centery - partida_y == -4,
          f"({diagonal.rect.centerx - partida_x}, {diagonal.rect.centery - partida_y})")

arco = proyectil(100, 250, 1, 25, avanceX=4, avanceY=-6)
alturas = []
for _ in range(6):
    arco.avanceY += 2          # gravedad de juguete: sube y luego cae
    arco.mover()
    alturas.append(arco.rect.centery)
comprobar("el vector permite trayectorias con arco (sube y baja)",
          min(alturas) < alturas[0] or alturas[-1] > min(alturas),
          " ".join(str(altura) for altura in alturas))

# una bala que se va por arriba tambien se considera fuera: antes solo se miraba el eje x
fugada = proyectil(250, 12, 1, 25, avanceX=0, avanceY=-9)
comprobar("dentro de la pantalla esta dentro", fugada.en_pantalla(500, 500))
for _ in range(5):
    fugada.mover()
comprobar("y al salir por arriba se detecta fuera", not fugada.en_pantalla(500, 500))

municion = [proyectil(250, 12, 1, 25, avanceX=0, avanceY=-9),
            proyectil(250, 488, 1, 25, avanceX=0, avanceY=9)]
for _ in range(6):
    municion = colisiones.resolverBalas(municion, [], 500, 500)
comprobar("resolverBalas retira las que salen por arriba y por abajo", municion == [],
          f"quedan {len(municion)}")

sys.exit(resumen())
