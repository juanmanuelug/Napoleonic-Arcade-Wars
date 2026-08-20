"""Pruebas del nivel 2: sueltas, caducidad, efectos de los cuatro objetos y su HUD."""
import sys

import entorno
from entorno import comprobar, resumen
import pygame

pygame.init()
pygame.display.set_mode((500, 500))

import enemigo as E
import hud
import jugador as J
import objetos

reloj = {'ms': 20000}
pygame.time.get_ticks = lambda: reloj['ms']


class TeclasFalsas(object):
    def __init__(self, pulsadas):
        self.pulsadas = pulsadas

    def __getitem__(self, codigo):
        return codigo in self.pulsadas


ESPACIO = TeclasFalsas({pygame.K_SPACE})

# ---- 1. los cuatro objetos tienen icono, y se dibujan con algo dentro ----
comprobar("hay icono para los cuatro objetos", len(objetos.ICONOS) == 4)
for clave, icono in objetos.ICONOS.items():
    comprobar(f"el icono de {objetos.NOMBRES[clave]} mide {objetos.LADO_ICONO}x{objetos.LADO_ICONO}",
              icono.get_size() == (objetos.LADO_ICONO, objetos.LADO_ICONO))
    pintados = sum(1 for x in range(objetos.LADO_ICONO) for y in range(objetos.LADO_ICONO)
                   if icono.get_at((x, y))[3] > 0)
    comprobar(f"el icono de {objetos.NOMBRES[clave]} no esta vacio",
              pintados > objetos.LADO_ICONO, f"{pintados} pixeles pintados")

# ---- 2. suelta: la probabilidad la pone el tipo de enemigo ----
frances = E.enemigo(200, 200, 0, 0)
frances.actualizarRect()
comprobar("el de bayoneta tiene su probabilidad de suelta", 0 < frances.PROBABILIDAD_SUELTA < 1)
comprobar("el tirador suelta mas a menudo que el de bayoneta",
          E.enemigoDistancia.PROBABILIDAD_SUELTA > E.enemigo.PROBABILIDAD_SUELTA,
          f"{E.enemigoDistancia.PROBABILIDAD_SUELTA} contra {E.enemigo.PROBABILIDAD_SUELTA}")

frances.PROBABILIDAD_SUELTA = 1.0
soltado = objetos.sueltaDe(frances, reloj['ms'])
comprobar("con probabilidad 1 siempre suelta algo", soltado is not None)
comprobar("y cae donde cayo el frances",
          soltado.rect.center == frances.rect.center, str(soltado.rect.center))
frances.PROBABILIDAD_SUELTA = 0.0
comprobar("con probabilidad 0 no suelta nada", objetos.sueltaDe(frances, reloj['ms']) is None)

# el reparto respeta los pesos: las vendas son lo mas comun
frances.PROBABILIDAD_SUELTA = 1.0
cuenta = {clave: 0 for clave, _ in objetos.PESOS}
for _ in range(3000):
    cuenta[objetos.sueltaDe(frances, reloj['ms']).clave] += 1
comprobar("salen los cuatro objetos", all(veces > 0 for veces in cuenta.values()), str(cuenta))
comprobar("las vendas son lo mas comun, como dicen los pesos",
          cuenta[objetos.CLAVE_VENDAS] == max(cuenta.values()), str(cuenta))

# ---- 3. caducidad y parpadeo ----
cosa = objetos.objeto(objetos.CLAVE_VENDAS, 100, 100, reloj['ms'])
comprobar("recien caido no esta caducado", not cosa.caducado(reloj['ms']))
comprobar("y se ve", cosa.visible(reloj['ms']))
comprobar("a mitad de vida sigue sin parpadear",
          cosa.visible(reloj['ms'] + objetos.DURACION_EN_SUELO // 2))
justo_antes = reloj['ms'] + objetos.DURACION_EN_SUELO - 1
comprobar("justo antes de irse todavia no ha caducado", not cosa.caducado(justo_antes))
comprobar("y al cumplirse el tiempo caduca",
          cosa.caducado(reloj['ms'] + objetos.DURACION_EN_SUELO))

# en los ultimos segundos parpadea: hay momentos visibles y momentos no
inicio_aviso = reloj['ms'] + objetos.DURACION_EN_SUELO - objetos.AVISO_ANTES_DE_IRSE
estados = [cosa.visible(inicio_aviso + salto) for salto in range(0, objetos.AVISO_ANTES_DE_IRSE, 30)]
comprobar("parpadea en sus ultimos segundos", True in estados and False in estados,
          f"{estados.count(True)} visibles y {estados.count(False)} invisibles")

# ---- 4. las vendas curan, sin pasar del maximo ----
soldado = J.jugador(250, 250)
soldado.vida = 50
objetos.aplicar(objetos.CLAVE_VENDAS, soldado, reloj['ms'])
comprobar("las vendas curan lo que dicen", soldado.vida == 50 + objetos.CURA_VENDAS,
          f"vida {soldado.vida}")
soldado.vida = soldado.vidaMaxima - 1
objetos.aplicar(objetos.CLAVE_VENDAS, soldado, reloj['ms'])
comprobar("y no curan por encima del maximo", soldado.vida == soldado.vidaMaxima,
          f"vida {soldado.vida}/{soldado.vidaMaxima}")

# ---- 5. la cartuchera: tres disparos sin esperar la recarga ----
soldado = J.jugador(100, 250)
balas = []
soldado.disparar(ESPACIO, balas)
comprobar("el primer disparo sale siempre", len(balas) == 1)
soldado.disparar(ESPACIO, balas)
comprobar("el segundo, sin recargar, no sale", len(balas) == 1)

objetos.aplicar(objetos.CLAVE_CARTUCHERA, soldado, reloj['ms'])
comprobar("la cartuchera da tres disparos", soldado.disparosGratis == objetos.DISPAROS_DE_CARTUCHERA)
for _ in range(objetos.DISPAROS_DE_CARTUCHERA):
    soldado.disparar(ESPACIO, balas)
comprobar("y salen los tres seguidos, sin esperar", len(balas) == 4, f"{len(balas)} balas")
comprobar("la cartuchera se gasta", soldado.disparosGratis == 0)
soldado.disparar(ESPACIO, balas)
comprobar("gastada, se vuelve a depender de la recarga", len(balas) == 4)

# ---- 6. el aguardiente: inmune al contacto mientras dura ----
soldado = J.jugador(200, 200)
frances = E.enemigo(200, 200, 0, 0)
frances.actualizarRect()
vida_antes = soldado.vida
objetos.aplicar(objetos.CLAVE_AGUARDIENTE, soldado, reloj['ms'])
comprobar("el aguardiente da inmunidad", soldado.tieneInmunidad(reloj['ms']))
for _ in range(20):
    soldado.sufrirContacto([frances])
comprobar("y encima de un enemigo no se pierde vida", soldado.vida == vida_antes,
          f"vida {soldado.vida}")

reloj['ms'] += objetos.DURACION_AGUARDIENTE
comprobar("pasado su tiempo se acaba la inmunidad", not soldado.tieneInmunidad(reloj['ms']))
soldado.sufrirContacto([frances])
comprobar("y el contacto vuelve a doler", soldado.vida < vida_antes, f"vida {soldado.vida}")

# ---- 7. el estandarte: danio doble mientras dura ----
soldado = J.jugador(100, 250)
normal = soldado.danioDelProximoDisparo(reloj['ms'])
objetos.aplicar(objetos.CLAVE_ESTANDARTE, soldado, reloj['ms'])
comprobar("el estandarte dobla el danio",
          soldado.danioDelProximoDisparo(reloj['ms']) == normal * J.MULTIPLICADOR_DANIO_DOBLE,
          f"{normal} -> {soldado.danioDelProximoDisparo(reloj['ms'])}")
balas = []
soldado.disparar(ESPACIO, balas)
comprobar("y la bala sale con el danio doblado", balas[0].danio == normal * J.MULTIPLICADOR_DANIO_DOBLE,
          f"danio {balas[0].danio}")
reloj['ms'] += objetos.DURACION_ESTANDARTE
comprobar("pasado su tiempo el danio vuelve al normal",
          soldado.danioDelProximoDisparo(reloj['ms']) == normal)

# ---- 8. recoger guarda en la mochila, y no gasta nada ----
soldado = J.jugador(250, 250)
soldado.vida = 40
encima = objetos.objeto(objetos.CLAVE_VENDAS, soldado.rect.centerx, soldado.rect.centery, reloj['ms'])
lejos = objetos.objeto(objetos.CLAVE_ESTANDARTE, 20, 20, reloj['ms'])
viejo = objetos.objeto(objetos.CLAVE_CARTUCHERA, 40, 40, reloj['ms'] - objetos.DURACION_EN_SUELO)
quedan, recogidos = objetos.recogerYCaducar([encima, lejos, viejo], soldado, reloj['ms'])
comprobar("lo que se pisa va a la mochila", soldado.objetoEnMochila == objetos.CLAVE_VENDAS,
          str(soldado.objetoEnMochila))
comprobar("y NO se gasta al recogerlo", soldado.vida == 40, f"vida {soldado.vida}")
comprobar("lo caducado desaparece y lo demas se queda", quedan == [lejos],
          f"quedan {len(quedan)}")
comprobar("se dice que se ha recogido, para poder anunciarlo",
          recogidos == [objetos.CLAVE_VENDAS], str(recogidos))
comprobar("y si no se pisa nada, no hay nada que anunciar",
          objetos.recogerYCaducar([lejos], soldado, reloj['ms'])[1] == [])

# la mochila es de un solo hueco: lo nuevo sustituye a lo viejo
otro = objetos.objeto(objetos.CLAVE_AGUARDIENTE, soldado.rect.centerx, soldado.rect.centery,
                      reloj['ms'])
objetos.recogerYCaducar([otro], soldado, reloj['ms'])
comprobar("pisar algo llevando otra cosa sustituye lo que llevabas",
          soldado.objetoEnMochila == objetos.CLAVE_AGUARDIENTE, str(soldado.objetoEnMochila))
comprobar("y lo sustituido no se gasta por el camino", soldado.vida == 40)

# ---- 8b. la Q gasta lo que se lleva, y solo si se lleva algo ----
soldado = J.jugador(250, 250)
soldado.vida = 40
comprobar("de salida la mochila esta vacia", soldado.objetoEnMochila is None)
comprobar("usar con la mochila vacia no hace nada", objetos.usar(soldado, reloj['ms']) is None)
comprobar("y no cambia nada del soldado", soldado.vida == 40)

soldado.objetoEnMochila = objetos.CLAVE_VENDAS
usado = objetos.usar(soldado, reloj['ms'])
comprobar("usar devuelve lo que se ha gastado", usado == objetos.CLAVE_VENDAS, str(usado))
comprobar("aplica su efecto", soldado.vida == 40 + objetos.CURA_VENDAS, f"vida {soldado.vida}")
comprobar("y deja la mochila vacia", soldado.objetoEnMochila is None)
comprobar("insistir con la mochila vacia no repite el efecto",
          objetos.usar(soldado, reloj['ms']) is None
          and soldado.vida == 40 + objetos.CURA_VENDAS, f"vida {soldado.vida}")

# los efectos temporales empiezan a contar al usarlo, no al recogerlo
soldado = J.jugador(250, 250)
soldado.objetoEnMochila = objetos.CLAVE_AGUARDIENTE
comprobar("guardado en la mochila, el aguardiente no da inmunidad todavia",
          not soldado.tieneInmunidad(reloj['ms']))
objetos.usar(soldado, reloj['ms'])
comprobar("y al usarlo si", soldado.tieneInmunidad(reloj['ms']))

# ---- 9. el HUD ensenia los efectos activos con su cuenta atras ----
soldado = J.jugador(250, 250)
comprobar("sin efectos no se ensenia nada", hud.efectosActivos(soldado, reloj['ms']) == [])
objetos.aplicar(objetos.CLAVE_CARTUCHERA, soldado, reloj['ms'])
objetos.aplicar(objetos.CLAVE_AGUARDIENTE, soldado, reloj['ms'])
objetos.aplicar(objetos.CLAVE_ESTANDARTE, soldado, reloj['ms'])
activos = hud.efectosActivos(soldado, reloj['ms'])
comprobar("con los tres efectos se enselian tres filas", len(activos) == 3, str(len(activos)))
comprobar("la cartuchera se cuenta por disparos", activos[0][1] == "x3", activos[0][1])
comprobar("el aguardiente cuenta segundos",
          activos[1][1] == "%.1fs" % (objetos.DURACION_AGUARDIENTE / 1000.0), activos[1][1])

lienzo = pygame.Surface((500, 500))
lienzo.fill((90, 150, 80))
antes = lienzo.copy()
hud.dibujarEfectos(lienzo, soldado, reloj['ms'])
distintos = sum(1 for x in range(0, 120) for y in range(0, 140)
                if antes.get_at((x, y)) != lienzo.get_at((x, y)))
comprobar("y se pintan de verdad bajo el panel", distintos > 200, f"{distintos} pixeles")

reloj['ms'] += max(objetos.DURACION_AGUARDIENTE, objetos.DURACION_ESTANDARTE)
soldado.disparosGratis = 0
comprobar("cuando se acaban, el HUD se queda limpio", hud.efectosActivos(soldado, reloj['ms']) == [])

# ---- 10. cada objeto dice lo que es y lo que da al recogerlo ----
for clave in objetos.ICONOS:
    comprobar(f"{objetos.NOMBRES[clave]} tiene descripcion de su efecto",
              clave in objetos.DESCRIPCIONES and len(objetos.DESCRIPCIONES[clave]) > 4,
              objetos.DESCRIPCIONES.get(clave))
comprobar("las descripciones salen de las mismas constantes que los efectos",
          str(objetos.CURA_VENDAS) in objetos.DESCRIPCIONES[objetos.CLAVE_VENDAS]
          and str(objetos.DISPAROS_DE_CARTUCHERA) in objetos.DESCRIPCIONES[objetos.CLAVE_CARTUCHERA]
          and str(objetos.DURACION_AGUARDIENTE // 1000) in objetos.DESCRIPCIONES[objetos.CLAVE_AGUARDIENTE]
          and str(objetos.DURACION_ESTANDARTE // 1000) in objetos.DESCRIPCIONES[objetos.CLAVE_ESTANDARTE])

lienzo = pygame.Surface((500, 500))


def pixelesPintados(clave, instante, ahora, motivo=None):
    lienzo.fill((90, 150, 80))
    limpio = lienzo.copy()
    hud.dibujarAvisoObjeto(lienzo, 500, clave, motivo or hud.AVISO_USADO, instante, ahora)
    return sum(1 for x in range(500) for y in range(hud.ARRIBA_AVISO - 4, hud.ARRIBA_AVISO + 40)
               if limpio.get_at((x, y)) != lienzo.get_at((x, y)))


recien = pixelesPintados(objetos.CLAVE_AGUARDIENTE, reloj['ms'], reloj['ms'])
comprobar("el cartel se pinta al recoger", recien > 300, f"{recien} pixeles")
medio = pixelesPintados(objetos.CLAVE_AGUARDIENTE, reloj['ms'],
                        reloj['ms'] + hud.DURACION_AVISO - hud.DESVANECIDO_AVISO // 2)
comprobar("y sigue puesto mientras se apaga", medio > 300, f"{medio} pixeles")
apagado = pixelesPintados(objetos.CLAVE_AGUARDIENTE, reloj['ms'], reloj['ms'] + hud.DURACION_AVISO)
comprobar("pasado su tiempo desaparece del todo", apagado == 0, f"{apagado} pixeles")
comprobar("sin nada recogido no se pinta cartel",
          pixelesPintados(None, reloj['ms'], reloj['ms']) == 0)

# el cartel se va apagando: al final del desvanecido tiene que quedar mas tenue
def brilloMedio(ahora):
    lienzo.fill((90, 150, 80))
    hud.dibujarAvisoObjeto(lienzo, 500, objetos.CLAVE_VENDAS, hud.AVISO_USADO,
                           reloj['ms'], ahora)
    filas = range(hud.ARRIBA_AVISO, hud.ARRIBA_AVISO + 30)
    return sum(sum(lienzo.get_at((x, y))[:3]) for x in range(180, 320) for y in filas)


brilloFuerte = brilloMedio(reloj['ms'])
brilloTenue = brilloMedio(reloj['ms'] + hud.DURACION_AVISO - 60)
comprobar("el cartel se desvanece antes de irse", brilloTenue > brilloFuerte,
          f"oscuridad {brilloFuerte} -> {brilloTenue} (mas alto = mas transparente)")

# ---- 11. el hueco de la mochila en pantalla ----
lienzo.fill((90, 150, 80))
limpio = lienzo.copy()
soldado = J.jugador(250, 250)
hud.dibujarMochila(lienzo, soldado, 500)
vacia = sum(1 for x in range(0, 200) for y in range(440, 500)
            if limpio.get_at((x, y)) != lienzo.get_at((x, y)))
comprobar("la mochila vacia tambien se dibuja, para que se sepa que existe", vacia > 200,
          f"{vacia} pixeles")

#el panel oscuro ocupa lo mismo lleno que vacio, asi que se comparan los dos dibujados
#entre si, no contra la hierba
conMochilaVacia = lienzo.copy()
soldado.objetoEnMochila = objetos.CLAVE_ESTANDARTE
lienzo.fill((90, 150, 80))
hud.dibujarMochila(lienzo, soldado, 500)
distintos = sum(1 for x in range(0, 200) for y in range(440, 500)
                if conMochilaVacia.get_at((x, y)) != lienzo.get_at((x, y)))
comprobar("con algo dentro se ve distinto (icono, nombre y la tecla)", distintos > 150,
          f"{distintos} pixeles de diferencia")

# ---- 12. en la partida: la Q gasta lo que se lleva ----
reloj['ms'] = 90000
juego = entorno.cargarJuego()


class RelojFalso(object):
    def tick(self, *args):
        reloj['ms'] += 33
        return 33


control = {'frames': 0, 'eventos': []}
juego['clock'] = RelojFalso()
pygame.event.get = lambda *a, **k: [control['eventos'].pop(0)] if control['eventos'] else []
pygame.key.get_pressed = lambda: TeclasFalsas(set())


def display_update_falso(*args, **kwargs):
    control['frames'] += 1
    if control['frames'] == 3:
        control['eventos'].append(pygame.event.Event(pygame.KEYDOWN, key=juego['TECLA_MOCHILA']))
    if control['frames'] == 6:
        #se apunta la vida justo despues de usar el objeto: al final del bucle el jugador
        #esta muerto a proposito, para que partida() vuelva
        control['vidaTrasUsar'] = juego['player'].vida
    if control['frames'] >= 10:
        juego['player'].vida = 0


pygame.display.update = display_update_falso

juego['reiniciarPartida']()
juego['player'].vida = 50
juego['player'].objetoEnMochila = objetos.CLAVE_VENDAS
juego['partida']()
comprobar("la tecla de la mochila gasta el objeto en la partida",
          juego['player'].objetoEnMochila is None)
comprobar("y se aplica su efecto", control['vidaTrasUsar'] == 50 + objetos.CURA_VENDAS,
          f"vida {control['vidaTrasUsar']} justo despues de pulsarla")
comprobar("el cartel dice que se ha usado, no que se ha guardado",
          juego['avisoObjeto'] == objetos.CLAVE_VENDAS
          and juego['avisoObjetoMotivo'] == hud.AVISO_USADO,
          f"{juego['avisoObjeto']} / {juego['avisoObjetoMotivo']}")

#y con la mochila vacia, pulsarla no molesta
juego['reiniciarPartida']()
control['frames'] = 0
juego['player'].vida = 70
juego['partida']()
comprobar("pulsarla con la mochila vacia no rompe nada ni inventa efectos",
          juego['player'].objetoEnMochila is None and juego['player'].disparosGratis == 0)

sys.exit(resumen())
