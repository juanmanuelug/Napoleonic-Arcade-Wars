"""Pruebas del record persistente: guardado, carga, ficheros rotos y su hueco en las pantallas."""
import json
import os
import sys

import entorno
from entorno import comprobar, resumen
import pygame

pygame.init()
pygame.display.set_mode((500, 500))

import ascensos
import records

# el record de verdad vive junto al juego; las pruebas usan el suyo y no lo tocan
records.RUTA = os.path.join(entorno.CAPTURAS, 'record_de_pruebas.json')


def borrarFichero():
    if os.path.exists(records.RUTA):
        os.remove(records.RUTA)


def escribirCrudo(contenido):
    with open(records.RUTA, 'w', encoding='utf-8') as fichero:
        fichero.write(contenido)


# ---- 1. sin fichero se empieza de cero ----
borrarFichero()
vacio = records.cargar()
comprobar("sin fichero el record esta vacio", vacio == records.VACIO, str(vacio))
comprobar("y se sabe que aun no hay marca", not records.hayRecord(vacio))
comprobar("el texto lo dice en vez de mentir con un cero",
          records.comoTexto(vacio, 'Soldado raso') == "Sin marca todavia",
          records.comoTexto(vacio, 'Soldado raso'))

# ---- 2. la primera partida siempre es marca ----
esRecord, record = records.guardarSiEsMejor(7, 2, 95.4, 3)
comprobar("la primera partida con bajas es marca", esRecord)
comprobar("y se guarda lo que se hizo",
          record == {'oleada': 3, 'bajas': 7, 'rango': 2, 'segundos': 95.4}, str(record))
comprobar("el fichero existe", os.path.exists(records.RUTA))
comprobar("y se relee igual", records.cargar() == record, str(records.cargar()))

# ---- 3. solo se guarda si se supera ----
esRecord, record = records.guardarSiEsMejor(7, 5, 300.0, 3)
comprobar("empatar oleada y bajas no es superar", not esRecord)
comprobar("y no se pisa la marca anterior", record['rango'] == 2 and record['segundos'] == 95.4,
          str(record))
esRecord, record = records.guardarSiEsMejor(6, 6, 999.0, 3)
comprobar("en la misma oleada, con menos bajas, tampoco", not esRecord)
comprobar("aunque se haya aguantado mucho mas tiempo", records.cargar()['bajas'] == 7)
esRecord, record = records.guardarSiEsMejor(8, 3, 60.0, 3)
comprobar("en la misma oleada, una baja mas si es marca",
          esRecord and record['bajas'] == 8, str(record))
#la marca es la oleada: llegar mas lejos manda, aunque se mate menos por el camino
esRecord, record = records.guardarSiEsMejor(2, 0, 30.0, 4)
comprobar("llegar a una oleada mas alta es marca aunque con menos bajas",
          esRecord and record['oleada'] == 4 and record['bajas'] == 2, str(record))
esRecord, record = records.guardarSiEsMejor(99, 7, 900.0, 3)
comprobar("y quedarse en una oleada anterior no es marca ni matando el triple", not esRecord,
          str(record))

# ---- 4. un fichero roto no debe impedir jugar ----
for descripcion, contenido in (("con basura dentro", "esto no es json"),
                               ("vacio del todo", ""),
                               ("con una lista en vez de un objeto", "[1, 2, 3]"),
                               ("con los tipos cambiados", '{"bajas": "muchas", "rango": null}')):
    escribirCrudo(contenido)
    cargado = records.cargar()
    comprobar(f"un record {descripcion} se ignora sin reventar", cargado == records.VACIO,
              str(cargado))

escribirCrudo(json.dumps({'bajas': 12}))
cargado = records.cargar()
comprobar("un record a medias completa lo que falta",
          cargado == {'oleada': 0, 'bajas': 12, 'rango': 0, 'segundos': 0.0}, str(cargado))

# ---- 5. el texto de la marca ----
borrarFichero()
records.guardarSiEsMejor(14, 2, 154.0, 5)
texto = records.comoTexto(records.cargar(), ascensos.RANGOS[2])
comprobar("el texto trae oleada, bajas, rango y tiempo",
          "oleada 5" in texto and "14 franceses" in texto and "Sargento" in texto
          and "2:34" in texto, texto)

# ---- 6. la partida lleva la cuenta del tiempo y guarda al morir ----
reloj = {'ms': 5000}
pygame.time.get_ticks = lambda: reloj['ms']
borrarFichero()

juego = entorno.cargarJuego()
juego['records'].RUTA = records.RUTA


class RelojFalso(object):
    def tick(self, *args):
        reloj['ms'] += 33
        return 33


class TeclasFalsas(object):
    def __getitem__(self, codigo):
        return False


control = {'frames': 0}
juego['clock'] = RelojFalso()
pygame.event.get = lambda *a, **k: []
pygame.key.get_pressed = lambda: TeclasFalsas()


def display_update_falso(*args, **kwargs):
    control['frames'] += 1
    if control['frames'] == 30:
        juego['player'].vida = 0


pygame.display.update = display_update_falso

juego['reiniciarPartida']()
comprobar("al empezar se apunta el instante de inicio",
          juego['instanteInicioPartida'] == reloj['ms'], str(juego['instanteInicioPartida']))
#dos bajas: por debajo del umbral del primer ascenso, para que la partida acabe en muerte
juego['progreso'].apuntarBajas(2)
resultado = juego['partida']()
comprobar("morir lleva al game over", resultado == juego['ESCENA_GAME_OVER'])
comprobar("y se ha guardado la marca de esa partida", juego['recordBatido'])
guardado = records.cargar()
comprobar("con las bajas de la partida", guardado['bajas'] == 2, str(guardado))
comprobar("y con la oleada en la que cayo", guardado['oleada'] == juego['oleada'].numero,
          f"oleada {guardado['oleada']}")
comprobar("y con un tiempo de sobrevivido razonable", 0.5 < guardado['segundos'] < 5,
          f"{guardado['segundos']} s")

# ---- 7. una pausa no cuenta como tiempo sobrevivido ----
juego['reiniciarPartida']()
inicioAntes = juego['instanteInicioPartida']
juego['compensarPausa'](4000)
comprobar("la pausa empuja el inicio de la partida",
          juego['instanteInicioPartida'] == inicioAntes + 4000,
          str(juego['instanteInicioPartida'] - inicioAntes))

# ---- 8. la segunda partida no borra la marca si es peor ----
borrarFichero()
records.guardarSiEsMejor(30, 5, 200.0, 9)
juego['reiniciarPartida']()
juego['progreso'].apuntarBajas(2)
control['frames'] = 0
juego['partida']()
comprobar("una partida peor no toca la marca", records.cargar()['oleada'] == 9,
          str(records.cargar()))
comprobar("y no se anuncia como nueva marca", not juego['recordBatido'])

borrarFichero()
sys.exit(resumen())
