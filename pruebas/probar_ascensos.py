"""Pruebas del progreso del jugador: umbrales, mejoras, topes y la escena de ascenso."""
import sys

import entorno
from entorno import comprobar, resumen
import pygame

pygame.init()
pygame.display.set_mode((500, 500))

import ascensos
import colisiones
import enemigo as E
import jugador as J
from proyectile import proyectil



# ---- 1. umbrales de ascenso ----
progreso = ascensos.Progreso()
comprobar("se empieza de soldado raso con 0 bajas",
          progreso.nombreRango() == 'Soldado raso' and progreso.bajas == 0)
progreso.apuntarBajas(2)
comprobar("con 2 bajas todavia no toca ascender", not progreso.tocaAscender())
progreso.apuntarBajas(1)
comprobar("con 3 bajas toca ascender", progreso.tocaAscender())
progreso.ascender()
comprobar("el primer ascenso es a cabo", progreso.nombreRango() == 'Cabo')
comprobar("ascender consume el aviso", not progreso.tocaAscender())
comprobar("el siguiente rango pide los puntos de la oleada 2",
          progreso.puntosParaAscender() == ascensos.PUNTOS_POR_RANGO[2])

# la escalera completa, punto a punto
progreso = ascensos.Progreso()
ascendidos = []
for punto in range(1, 120):
    progreso.apuntarBajas(1, 1)
    while progreso.tocaAscender():
        progreso.ascender()
        ascendidos.append((punto, progreso.nombreRango()))
esperado = [(ascensos.PUNTOS_POR_RANGO[indice], ascensos.RANGOS[indice])
            for indice in range(1, len(ascensos.RANGOS))]
comprobar("los siete ascensos caen en los puntos previstos", ascendidos == esperado,
          str(ascendidos))
comprobar("de coronel ya no se sube mas", progreso.esRangoMaximo() and not progreso.tocaAscender())
comprobar("en coronel no hay siguiente umbral", progreso.puntosParaAscender() is None)

# los puntos y las bajas son cosas distintas: un granadero vale por cuatro
progreso = ascensos.Progreso()
progreso.apuntarBajas(1, E.granadero.PUNTOS)
comprobar("una sola baja puede valer varios puntos",
          progreso.bajas == 1 and progreso.puntos == E.granadero.PUNTOS,
          f"{progreso.bajas} bajas, {progreso.puntos} puntos")
comprobar("y sin decir puntos, cada baja vale uno",
          (lambda p: (p.apuntarBajas(3), p.puntos)[1])(ascensos.Progreso()) == 3)

# cada tipo vale mas que el anterior, y en ese orden
comprobar("el tirador vale mas que la bayoneta",
          E.enemigoDistancia.PUNTOS > E.enemigo.PUNTOS,
          f"{E.enemigoDistancia.PUNTOS} contra {E.enemigo.PUNTOS}")
comprobar("y el granadero mas que el tirador",
          E.granadero.PUNTOS > E.enemigoDistancia.PUNTOS,
          f"{E.granadero.PUNTOS} contra {E.enemigoDistancia.PUNTOS}")

# ---- 2. las mejoras suben lo que dicen y respetan su tope ----
soldado = J.jugador(250, 250)
comprobar("de salida: recarga 1500, vida 100, dano 25",
          soldado.recarga == 1500 and soldado.vidaMaxima == 100 and soldado.danioBala == 25)

for _ in range(5):
    ascensos.aplicar(soldado, ascensos.CLAVE_RECARGA)
comprobar("la recarga no baja del suelo", soldado.recarga == ascensos.SUELO_RECARGA,
          f"recarga={soldado.recarga}")
for _ in range(5):
    ascensos.aplicar(soldado, ascensos.CLAVE_VIDA)
comprobar("la vida maxima no pasa del techo", soldado.vidaMaxima == ascensos.TECHO_VIDA,
          f"vida maxima={soldado.vidaMaxima}")
for _ in range(5):
    ascensos.aplicar(soldado, ascensos.CLAVE_DANIO)
comprobar("el dano se queda en el ultimo escalon", soldado.danioBala == ascensos.ESCALONES_DANIO[-1],
          f"dano={soldado.danioBala}")

# escalones de dano exactos
soldado = J.jugador(250, 250)
ascensos.aplicar(soldado, ascensos.CLAVE_DANIO)
comprobar("primer escalon de dano: 25 -> 38", soldado.danioBala == 38)
ascensos.aplicar(soldado, ascensos.CLAVE_DANIO)
comprobar("segundo escalon de dano: 38 -> 75", soldado.danioBala == 75)

# la coraza cura, pero no por encima del maximo
soldado = J.jugador(250, 250)
soldado.vida = 40
ascensos.aplicar(soldado, ascensos.CLAVE_VIDA)
comprobar("la coraza sube el maximo y cura", soldado.vidaMaxima == 125 and soldado.vida == 65,
          f"vida={soldado.vida}/{soldado.vidaMaxima}")
soldado.vida = 124
ascensos.aplicar(soldado, ascensos.CLAVE_VIDA)
comprobar("la cura no pasa del maximo", soldado.vida == 149 and soldado.vidaMaxima == 150,
          f"vida={soldado.vida}/{soldado.vidaMaxima}")

# ---- 3. siete ascensos dan exactamente para dejarlo todo al maximo, en cualquier orden ----
for nombre_orden, orden in (("recarga->vida->dano",
                             [ascensos.CLAVE_RECARGA] * 3 + [ascensos.CLAVE_VIDA] * 2 + [ascensos.CLAVE_DANIO] * 2),
                            ("dano->recarga->vida",
                             [ascensos.CLAVE_DANIO] * 2 + [ascensos.CLAVE_RECARGA] * 3 + [ascensos.CLAVE_VIDA] * 2)):
    soldado = J.jugador(250, 250)
    for clave in orden:
        ascensos.aplicar(soldado, clave)
    todo_al_maximo = (soldado.recarga == ascensos.SUELO_RECARGA
                      and soldado.vidaMaxima == ascensos.TECHO_VIDA
                      and soldado.danioBala == ascensos.ESCALONES_DANIO[-1])
    comprobar(f"con 7 mejoras ({nombre_orden}) queda todo al maximo", todo_al_maximo,
              f"recarga={soldado.recarga} vida={soldado.vidaMaxima} dano={soldado.danioBala}")

# ---- 4. las opciones que ya estan al maximo dejan de ofrecerse ----
soldado = J.jugador(250, 250)
mejoras = ascensos.mejorasDisponibles(soldado, E.enemigo.VIDA_INICIAL, ascensos.RANGO_MINIMO_POLVORA)
comprobar("al principio se pueden elegir las tres", all(mejora.disponible for mejora in mejoras))
comprobar("el orden de las opciones es fijo",
          [mejora.clave for mejora in mejoras] == [ascensos.CLAVE_RECARGA, ascensos.CLAVE_VIDA, ascensos.CLAVE_DANIO])
comprobar("la opcion de dano dice cuantos disparos hara falta",
          "2 disparos" in mejoras[2].efecto, mejoras[2].efecto)
for _ in range(3):
    ascensos.aplicar(soldado, ascensos.CLAVE_RECARGA)
mejoras = ascensos.mejorasDisponibles(soldado, E.enemigo.VIDA_INICIAL, ascensos.RANGO_MINIMO_POLVORA)
comprobar("con la recarga al suelo su opcion se marca no disponible",
          not mejoras[0].disponible and mejoras[1].disponible and mejoras[2].disponible)

# ---- 5. la bala sale con el dano mejorado y mata en menos disparos ----
class TeclasFalsas:
    def __getitem__(self, codigo):
        return codigo == pygame.K_SPACE

soldado = J.jugador(100, 250)
ascensos.aplicar(soldado, ascensos.CLAVE_DANIO)
balas = []
soldado.disparar(TeclasFalsas(), balas)
comprobar("la bala del jugador lleva su dano mejorado", balas and balas[0].danio == 38,
          f"dano de la bala={balas[0].danio if balas else 'sin bala'}")

frances = E.enemigo(200, 250, 0, 0)
frances.actualizarRect()
disparos = 0
while frances.vida > 0 and disparos < 10:
    disparos += 1
    municion = [proyectil(frances.rect.left - 8, frances.rect.centery, 1, soldado.danioBala)]
    for _ in range(4):
        municion = colisiones.resolverBalas(municion, [frances], 500, 500)
comprobar("con 38 de dano el frances cae en 2 disparos", disparos == 2, f"{disparos} disparos")

frances = E.enemigo(200, 250, 0, 0)
frances.actualizarRect()
municion = [proyectil(frances.rect.left - 8, frances.rect.centery, 1, 75)]
for _ in range(4):
    municion = colisiones.resolverBalas(municion, [frances], 500, 500)
frances.checkEstadoVida()
comprobar("con 75 de dano cae de un solo disparo", not frances.vivo, f"vida={frances.vida}")

# La dificultad ya no sube con el rango: la lleva el numero de oleada, y se prueba en
# probar_oleadas.py. Tener las dos cosas la subia por partida doble.

# ---- 7. la polvora esta reservada a los rangos altos ----
soldado = J.jugador(250, 250)
for rango in range(ascensos.RANGO_MINIMO_POLVORA):
    mejoras = ascensos.mejorasDisponibles(soldado, E.enemigo.VIDA_INICIAL, rango)
    comprobar(f"de rango {rango} la polvora no se puede pedir", not mejoras[2].disponible)
    comprobar(f"y se dice desde cuando ({ascensos.RANGOS[ascensos.RANGO_MINIMO_POLVORA]})",
              ascensos.RANGOS[ascensos.RANGO_MINIMO_POLVORA] in mejoras[2].efecto,
              mejoras[2].efecto)
mejoras = ascensos.mejorasDisponibles(soldado, E.enemigo.VIDA_INICIAL, ascensos.RANGO_MINIMO_POLVORA)
comprobar("desde Brigada ya se ofrece", mejoras[2].disponible)
comprobar("y las dos primeras elecciones son recarga contra coraza",
          all(mejora.disponible for mejora in
              ascensos.mejorasDisponibles(soldado, E.enemigo.VIDA_INICIAL, 1)[:2]))

# ---- 8. con la polvora reservada, los siete ascensos siguen teniendo algo que dar ----
soldado = J.jugador(250, 250)
progreso = ascensos.Progreso()
pedidas = []
sinOpciones = []
for _ in range(len(ascensos.RANGOS) - 1):
    progreso.ascender()
    mejoras = ascensos.mejorasDisponibles(soldado, E.enemigo.VIDA_INICIAL, progreso.rango)
    elegibles = [mejora for mejora in mejoras if mejora.disponible]
    if not elegibles:
        sinOpciones.append(progreso.nombreRango())
        continue
    #un jugador voraz: coge la primera que pueda
    ascensos.aplicar(soldado, elegibles[0].clave)
    pedidas.append(elegibles[0].clave)
comprobar("en los siete ascensos siempre queda algo que elegir", not sinOpciones, str(sinOpciones))
comprobar("y al acabar sigue estando todo al maximo",
          soldado.recarga == ascensos.SUELO_RECARGA and soldado.vidaMaxima == ascensos.TECHO_VIDA
          and soldado.danioBala == ascensos.ESCALONES_DANIO[-1],
          f"recarga={soldado.recarga} vida={soldado.vidaMaxima} dano={soldado.danioBala}")
comprobar("se han pedido las siete mejoras", len(pedidas) == 7, f"{len(pedidas)}: {pedidas}")

# ---- 9. los umbrales cuadran con las oleadas: limpiar una es ascender ----
import oleadas

PUNTOS_POR_TIPO = {oleadas.CUERPO_A_CUERPO: E.enemigo.PUNTOS,
                   oleadas.TIRADOR: E.enemigoDistancia.PUNTOS,
                   oleadas.VOLTIGEUR: E.voltigeur.PUNTOS,
                   oleadas.OFICIAL: E.oficial.PUNTOS,
                   oleadas.GRANADERO: E.granadero.PUNTOS}

progreso = ascensos.Progreso()
rangosAlLimpiar = []
for numero in range(1, len(ascensos.RANGOS)):
    composicion = oleadas.composicion(numero)
    for tipo, cuantos in composicion.items():
        for _ in range(cuantos):
            progreso.apuntarBajas(1, PUNTOS_POR_TIPO[tipo])
    ascensos_de_esta = 0
    while progreso.tocaAscender():
        progreso.ascender()
        ascensos_de_esta += 1
    rangosAlLimpiar.append((numero, progreso.nombreRango(), ascensos_de_esta))

comprobar("limpiar cada una de las siete primeras oleadas da un ascenso, ni mas ni menos",
          all(cuantos == 1 for _, _, cuantos in rangosAlLimpiar),
          str([(numero, cuantos) for numero, _, cuantos in rangosAlLimpiar]))
comprobar("y al acabar la septima se es coronel", progreso.nombreRango() == 'Coronel',
          str([(numero, nombre) for numero, nombre, _ in rangosAlLimpiar]))
comprobar("los umbrales son exactamente los puntos acumulados de esas oleadas",
          list(ascensos.PUNTOS_POR_RANGO[1:]) ==
          [sum(sum(oleadas.composicion(o)[t] * PUNTOS_POR_TIPO[t] for t in PUNTOS_POR_TIPO)
               for o in range(1, hasta + 1))
           for hasta in range(1, len(ascensos.RANGOS))],
          str(ascensos.PUNTOS_POR_RANGO))

sys.exit(resumen())
