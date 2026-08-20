"""Pruebas del bloque 5: proporciones de las barras, progreso de recarga y capturas."""
import os
import sys

import entorno
from entorno import comprobar, resumen
import pygame

pygame.init()
pygame.display.set_mode((500, 500))

import ascensos
import hud
import jugador as J
import enemigo as E



def progresoCon(bajas):
    progreso = ascensos.Progreso()
    progreso.apuntarBajas(bajas)
    return progreso


def anchoRelleno(superficie, color, rectangulo):
    """Cuenta los pixeles del color de relleno a lo largo de la barra."""
    fila = rectangulo.centery
    return sum(1 for x in range(rectangulo.left, rectangulo.right)
               if superficie.get_at((x, fila))[:3] == color)


lienzo = pygame.Surface((500, 500))

# ---- 1. la barra de vida del jugador es proporcional ----
soldado = J.jugador(250, 250)
barra_vida = pygame.Rect(hud.MARGEN, hud.MARGEN, hud.ANCHO_BARRA, hud.ALTO_BARRA_VIDA)
for vida, esperado_aprox in ((100, 130), (75, 97), (50, 65), (25, 32), (0, 0)):
    soldado.vida = vida
    lienzo.fill((90, 150, 80))
    hud.dibujarPanelJugador(lienzo, soldado, progresoCon(0), 500)
    ancho = anchoRelleno(lienzo, hud.colorVida(vida / 100.0), barra_vida)
    comprobar(f"barra de vida al {vida}%", abs(ancho - esperado_aprox) <= 2,
              f"{ancho} px de {hud.ANCHO_BARRA} (esperado ~{esperado_aprox})")

# ---- 2. el color avisa cuando queda poca vida ----
comprobar("verde con vida alta", hud.colorVida(0.9) == hud.COLOR_VIDA_ALTA)
comprobar("amarillo a media vida", hud.colorVida(0.5) == hud.COLOR_VIDA_MEDIA)
comprobar("rojo con poca vida", hud.colorVida(0.15) == hud.COLOR_VIDA_BAJA)

# ---- 3. progreso de recarga de 0 a 1 ----
soldado = J.jugador(250, 250)
ahora = pygame.time.get_ticks()
soldado.instanteUltimoDisparo = ahora
comprobar("recien disparado la recarga esta a 0", soldado.progresoRecarga(ahora) == 0.0)
comprobar("a mitad de recarga vale 0.5",
          abs(soldado.progresoRecarga(ahora + J.RECARGA // 2) - 0.5) < 0.01,
          f"{soldado.progresoRecarga(ahora + J.RECARGA // 2):.2f}")
comprobar("pasada la recarga vale 1", soldado.progresoRecarga(ahora + J.RECARGA) == 1.0)
comprobar("no se pasa de 1", soldado.progresoRecarga(ahora + J.RECARGA * 10) == 1.0)
comprobar("la barra de recarga y el poder disparar van a la par",
          soldado.puedeDisparar(ahora + J.RECARGA) and not soldado.puedeDisparar(ahora + 100))

# ---- 4. la barrita del enemigo sigue su vida y se queda sobre su cabeza ----
frances = E.enemigo(200, 200, 0, 0)
frances.actualizarRect()
barra_enemigo = pygame.Rect(0, 0, hud.ANCHO_BARRA_ENEMIGO, hud.ALTO_BARRA_ENEMIGO)
barra_enemigo.centerx = frances.rect.centerx
barra_enemigo.bottom = frances.rect.top - hud.HUECO_SOBRE_LA_CABEZA
for vida, esperado in ((75, 22), (50, 15), (25, 7)):
    frances.vida = vida
    lienzo.fill((90, 150, 80))
    hud.dibujarVidaEnemigo(lienzo, frances)
    ancho = anchoRelleno(lienzo, hud.COLOR_VIDA_ENEMIGO, barra_enemigo)
    # tolerancia de 2 px: el borde de 1 px tapa un pixel de relleno a cada lado
    comprobar(f"barra del enemigo con {vida} de vida", abs(ancho - esperado) <= 2,
              f"{ancho} px de {hud.ANCHO_BARRA_ENEMIGO}")
comprobar("la barra queda por encima del cuerpo del enemigo", barra_enemigo.bottom <= frances.rect.top)

# ---- 5. un enemigo pegado al borde de arriba no pierde su barra ----
arriba = E.enemigo(200, 0, 0, 0)
arriba.actualizarRect()
lienzo.fill((90, 150, 80))
hud.dibujarVidaEnemigo(lienzo, arriba)
recuento = sum(1 for x in range(500) for y in range(20)
               if lienzo.get_at((x, y))[:3] == hud.COLOR_VIDA_ENEMIGO)
comprobar("la barra sigue visible pegado al borde de arriba", recuento > 0, f"{recuento} px")

# ---- 6. capturas para mirarlas ----
soldado = J.jugador(240, 240)
enemigos = [E.enemigo(120, 200, 0, 0), E.enemigoDistancia(380, 300, 0, 0), E.enemigo(300, 400, 0, 0)]
enemigos[0].vida = 75
enemigos[1].vida = 45
enemigos[2].vida = 20
for enemigo in enemigos:
    enemigo.actualizarRect()

fondo = pygame.image.load('./imgs/background.jpg')
for nombre, vida, ms_desde_disparo, puntos in (('hud_lleno.png', 100, 1500, 0),
                                               ('hud_medio.png', 55, 700, 4),
                                               ('hud_critico.png', 12, 100, 11)):
    soldado.vida = vida
    soldado.instanteUltimoDisparo = pygame.time.get_ticks() - ms_desde_disparo
    lienzo.blit(fondo, (0, 0))
    soldado.dibujar(lienzo)
    for enemigo in enemigos:
        enemigo.dibujarEnemigo(lienzo)
        hud.dibujarVidaEnemigo(lienzo, enemigo)
    hud.dibujarPanelJugador(lienzo, soldado, progresoCon(puntos), 500)
    pygame.image.save(lienzo, os.path.join(entorno.CAPTURAS, nombre))
    print("  captura", nombre)

sys.exit(resumen())
