"""Nota: los tiradores nacen con un desfase propio de hasta
DESFASE_MAXIMO_DESCARGA ms, asi que para darlos por listos hay que avanzar recarga + desfase.

Pruebas del bloque 6: cadaveres con caducidad, IA de los tiradores y aparicion en el borde."""
import sys

import entorno
from entorno import comprobar, resumen
import pygame

pygame.init()
pygame.display.set_mode((500, 500))

import enemigo as E
import jugador as J



reloj = {'ms': pygame.time.get_ticks()}
pygame.time.get_ticks = lambda: reloj['ms']

# ---- 1. aparicion en el perimetro y nunca encima del jugador ----
puntos = [E.puntoDeAparicion(250, 250) for _ in range(400)]
en_el_borde = all(x <= 0 or x >= 500 or y <= 0 or y >= 500 for x, y in puntos)
comprobar("todos los enemigos entran por el borde", en_el_borde)
distancias = [((x - 250) ** 2 + (y - 250) ** 2) ** 0.5 for x, y in puntos]
comprobar("ninguno aparece encima del jugador",
          min(distancias) >= E.DISTANCIA_MINIMA_APARICION,
          f"la mas cercana a {min(distancias):.0f} px (minimo {E.DISTANCIA_MINIMA_APARICION})")
lados = set()
for x, y in puntos:
    lados.add('izq' if x < 0 else 'dch' if x > 500 else 'arriba' if y < 0 else 'abajo')
comprobar("entran por los cuatro lados", len(lados) == 4, str(sorted(lados)))

# ---- 2. con el jugador pegado a una esquina sigue habiendo sitio ----
puntos_esquina = [E.puntoDeAparicion(0, 0) for _ in range(200)]
peor = min(((x ** 2 + y ** 2) ** 0.5) for x, y in puntos_esquina)
comprobar("con el jugador en la esquina se elige el punto mas lejano posible", peor > 0,
          f"la mas cercana a {peor:.0f} px")

# ---- 3. los cadaveres caducan y estan limitados ----
caidos = []
for indice in range(30):
    frances = E.enemigo(100, 100, 0, 0)
    frances.vida = 0
    frances.checkEstadoVida()
    caidos.append(frances)
comprobar("al caer se apunta el instante de la muerte", all(c.instanteMuerte == reloj['ms'] for c in caidos))
vigentes = E.cadaveresVigentes(caidos)
comprobar("nunca hay mas de MAX_CADAVERES en el campo", len(vigentes) == E.MAX_CADAVERES,
          f"{len(caidos)} caidos -> {len(vigentes)} en pantalla")
comprobar("se quedan los mas recientes", vigentes[-1] is caidos[-1])
reloj['ms'] += E.DURACION_CADAVER - 1
comprobar("justo antes de caducar siguen ahi", len(E.cadaveresVigentes(vigentes)) == E.MAX_CADAVERES)
reloj['ms'] += 2
comprobar("pasado su tiempo desaparecen", E.cadaveresVigentes(vigentes) == [])

# ---- 4. el tirador mira al jugador aunque este quieto ----
tirador = E.enemigoDistancia(400, 250, 250, 250)
tirador.pathFinding(250, 250)          # jugador a su izquierda
comprobar("mira a la izquierda si el jugador esta a su izquierda", tirador.izq and not tirador.dch)
tirador.pathFinding(480, 250)          # jugador a su derecha
comprobar("y a la derecha si se pone a su derecha", tirador.dch and not tirador.izq)

#en su puesto y a la altura del jugador, se planta
enSuPuesto = E.enemigoDistancia(300, 250, 250, 250)
enSuPuesto.x = 250 + enSuPuesto.distanciaDeTiro
enSuPuesto.pathFinding(250, 250)
comprobar("en su puesto y encarado, se queda quieto", enSuPuesto.stop,
          f"a {abs(250 - enSuPuesto.x)} px, su puesto es {enSuPuesto.distanciaDeTiro}")

#y si el jugador se le echa encima, retrocede en vez de quedarse a bocajarro
acorralado = E.enemigoDistancia(300, 250, 250, 250)
acorralado.x = 250 + 40
xAntes = acorralado.x
acorralado.pathFinding(250, 250)
comprobar("si el jugador se le echa encima, retrocede", acorralado.x > xAntes,
          f"{xAntes} -> {acorralado.x}")

# ---- 5. dispara hacia donde mira, y solo cuando tiene linea de tiro ----
tirador = E.enemigoDistancia(400, 250, 250, 250)
tirador.pathFinding(250, 250)
reloj['ms'] += E.RECARGA_ENEMIGO + E.DESFASE_MAXIMO_DESCARGA
balas = []
tirador.disparar(balas)
comprobar("dispara cuando esta a la altura del jugador", len(balas) == 1)
comprobar("la bala va hacia el jugador", balas[0].avanceX < 0, f"vel={balas[0].avanceX}")

desalineado = E.enemigoDistancia(400, 100, 250, 250)
desalineado.pathFinding(250, 250)      # 150 px por encima del jugador
reloj['ms'] += E.RECARGA_ENEMIGO + E.DESFASE_MAXIMO_DESCARGA
balas = []
desalineado.disparar(balas)
comprobar("no dispara si no tiene linea de tiro", balas == [])
comprobar("mientras se coloca, camina", not desalineado.stop)

# ---- 6. la tolerancia hace que el caso imposible de antes ahora funcione ----
casi = E.enemigoDistancia(400, 250 + E.TOLERANCIA_PUNTERIA, 250, 250)
#TOLERANCIA_PUNTERIA es el minimo garantizado: cada tirador tiene esa o algo mas
casi.pathFinding(250, 250)
reloj['ms'] += E.RECARGA_ENEMIGO + E.DESFASE_MAXIMO_DESCARGA
balas = []
casi.disparar(balas)
comprobar("a un pelo de la altura del jugador tambien dispara", len(balas) == 1,
          f"desalineado {E.TOLERANCIA_PUNTERIA} px")

# ---- 7. respeta la recarga y no dispara en el frame en que aparece ----
recien_llegado = E.enemigoDistancia(400, 250, 250, 250)
recien_llegado.pathFinding(250, 250)
balas = []
recien_llegado.disparar(balas)
comprobar("no dispara a bocajarro al aparecer", balas == [])
reloj['ms'] += E.RECARGA_ENEMIGO + E.DESFASE_MAXIMO_DESCARGA
recien_llegado.disparar(balas)
recien_llegado.disparar(balas)
recien_llegado.disparar(balas)
comprobar("un solo disparo por recarga, sin el disparo doble", len(balas) == 1, f"{len(balas)} balas")
reloj['ms'] += E.RECARGA_ENEMIGO + E.DESFASE_MAXIMO_DESCARGA
recien_llegado.disparar(balas)
comprobar("pasada la recarga vuelve a disparar", len(balas) == 2)

# ---- 8. el tirador se acerca si esta lejos y se planta a distancia de tiro ----
lejano = E.enemigoDistancia(-40, 250, 250, 250)
for _ in range(400):
    lejano.pathFinding(250, 250)
distancia = abs(250 - lejano.x)
comprobar("se acerca hasta SU distancia de tiro y se planta",
          abs(distancia - lejano.distanciaDeTiro) <= E.MARGEN_PUESTO and lejano.stop,
          f"se queda a {distancia} px (su puesto es {lejano.distanciaDeTiro})")

# ---- 9. los tiradores no se plantan todos en el mismo sitio (T3.7) ----
puestos = [E.tomarPuestoDeTiro() for _ in range(len(E.PUESTOS_DE_TIRO))]
comprobar("los puestos se reparten por turno, sin repetir en una vuelta",
          sorted(puestos) == sorted(E.PUESTOS_DE_TIRO), str(puestos))
comprobar("dos tiradores seguidos no toman el mismo puesto",
          all(puestos[i] != puestos[i + 1] for i in range(len(puestos) - 1)))
separacionMinima = min(abs(a - b) for a, b in zip(sorted(E.PUESTOS_DE_TIRO), sorted(E.PUESTOS_DE_TIRO)[1:]))
comprobar("y estan lo bastante separados para no solaparse",
          separacionMinima > E.enemigoDistancia.ANCHO_REFERENCIA,
          f"{separacionMinima} px de separacion minima, cuerpos de {E.enemigoDistancia.ANCHO_REFERENCIA}")

# una vuelta completa de puestos, todos entrando por el mismo lado: es el caso que antes
# acababa en fila india, con los cuatro plantados en el mismo pixel
def colocarHorda(cuantos, xEntrada):
    horda = [E.enemigoDistancia(xEntrada, 100 + indice * 7, 250, 250) for indice in range(cuantos)]
    for tirador in horda:
        for _ in range(500):
            tirador.pathFinding(250, 250)
    return horda


tiradores = colocarHorda(len(E.PUESTOS_DE_TIRO), 480)
distancias = sorted(abs(250 - tirador.x) for tirador in tiradores)
comprobar("una vuelta de tiradores acaba a distancias distintas",
          len(set(distancias)) == len(distancias), str(distancias))
comprobar("y ninguna pareja se queda pegada",
          all(b - a > E.enemigoDistancia.ANCHO_REFERENCIA for a, b in zip(distancias, distancias[1:])),
          str(distancias))
solapes = sum(1 for uno in tiradores for otro in tiradores
              if uno is not otro and uno.rect.colliderect(otro.rect))
comprobar("ninguno acaba encima de otro", solapes == 0, f"{solapes} solapes")
comprobar("y ninguno se queda fuera de la pantalla",
          all(0 <= tirador.x <= 500 - E.enemigoDistancia.ANCHO_REFERENCIA for tirador in tiradores),
          str([tirador.x for tirador in tiradores]))

# en la partida de verdad se le dice a cada tirador quien esta ya en el campo, y coge un
# puesto libre en vez de uno por turno: asi no se pisan ni cuando mueren y entran otros
enElCampo = []
for _ in range(len(E.PUESTOS_DE_TIRO)):
    enElCampo.append(E.enemigoDistancia(520, 200, 250, 250, enElCampo))
puestosOcupados = [tirador.distanciaDeTiro for tirador in enElCampo]
comprobar("sabiendo quien esta en el campo, nadie repite puesto",
          len(set(puestosOcupados)) == len(puestosOcupados), str(puestosOcupados))

#y si de verdad estan todos cogidos, se reparte por turno (limite documentado)
enElCampo.append(E.enemigoDistancia(520, 200, 250, 250, enElCampo))
comprobar("con todos los puestos cogidos, el siguiente comparte con alguien",
          enElCampo[-1].distanciaDeTiro in puestosOcupados,
          f"puesto {enElCampo[-1].distanciaDeTiro} entre {puestosOcupados}")

#al morir uno, su puesto vuelve a quedar libre
libre = puestosOcupados[1]
delDiezmado = [tirador for tirador in enElCampo if tirador.distanciaDeTiro != libre]
relevo = E.enemigoDistancia(520, 200, 250, 250, delDiezmado)
comprobar("el puesto de un caido lo ocupa el relevo", relevo.distanciaDeTiro == libre,
          f"puesto libre {libre}, el relevo tomo {relevo.distanciaDeTiro}")

# el pulso de cada uno es suyo: no disparan todos en el mismo frame. Se mira sobre una muestra
# grande, que con cuatro tiradores salir los cuatro iguales pasa un 6% de las veces
muestra = [E.enemigoDistancia(520, 200, 250, 250) for _ in range(40)]
tolerancias = [tirador.toleranciaPunteria for tirador in muestra]
comprobar("la tolerancia de punteria varia de un tirador a otro",
          len(set(tolerancias)) > 1, f"{len(set(tolerancias))} valores distintos")
comprobar("y siempre esta entre el minimo y el minimo mas la variacion",
          all(E.TOLERANCIA_PUNTERIA <= valor <= E.TOLERANCIA_PUNTERIA + E.VARIACION_PUNTERIA
              for valor in tolerancias),
          f"de {min(tolerancias)} a {max(tolerancias)}")
desfases = [tirador.instanteUltimoDisparo - reloj['ms'] for tirador in muestra]
comprobar("y el desfase de la descarga tambien varia, sin pasarse del maximo",
          len(set(desfases)) > 1 and all(0 <= valor <= E.DESFASE_MAXIMO_DESCARGA for valor in desfases),
          f"de {min(desfases)} a {max(desfases)} ms")

sys.exit(resumen())
