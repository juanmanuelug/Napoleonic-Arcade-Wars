import json
import os

# ####################################### El record ###################################################
# Un arcade sin marca que batir no engancha: cuando mueres no hay nada que superar. Se guarda
# en un json al lado del juego, y si no existe o esta roto simplemente se empieza de cero:
# perder el record nunca debe impedir jugar.
RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'record.json')

VACIO = {'oleada': 0, 'bajas': 0, 'rango': 0, 'segundos': 0.0}


def cargar():
    """El mejor resultado guardado, o uno vacio si no hay nada legible."""
    try:
        with open(RUTA, encoding='utf-8') as fichero:
            datos = json.load(fichero)
    except (OSError, ValueError):
        return dict(VACIO)
    if not isinstance(datos, dict):
        return dict(VACIO)
    record = dict(VACIO)
    for clave, porDefecto in VACIO.items():
        valor = datos.get(clave)
        #se acepta solo lo que tenga el tipo que toca: un json manipulado no debe reventar
        if isinstance(valor, (int, float)) and not isinstance(valor, bool):
            record[clave] = type(porDefecto)(valor)
    return record


def hayRecord(record):
    return record['bajas'] > 0 or record['oleada'] > 0


def esMejor(bajas, oleada, record):
    #la marca es hasta que oleada se llego; a igualdad, los franceses abatidos deciden.
    #El rango y el tiempo se guardan solo para poder contarlo
    return (oleada, bajas) > (record['oleada'], record['bajas'])


def guardarSiEsMejor(bajas, rango, segundos, oleada):
    """Guarda la marca si supera la anterior. Devuelve (es_record, record_vigente)."""
    record = cargar()
    if not esMejor(bajas, oleada, record):
        return False, record
    nuevo = {'oleada': int(oleada), 'bajas': int(bajas), 'rango': int(rango),
             'segundos': round(float(segundos), 1)}
    try:
        with open(RUTA, 'w', encoding='utf-8') as fichero:
            json.dump(nuevo, fichero, indent=2)
    except OSError:
        #si no se puede escribir (carpeta de solo lectura, disco lleno) la partida sigue:
        #la marca se ha batido igual, solo que no sobrevivira al cierre del juego
        pass
    return True, nuevo


def comoTexto(record, nombreRango):
    """Una linea para el menu y la pantalla de derrota."""
    if not hayRecord(record):
        return "Sin marca todavia"
    minutos = int(record['segundos']) // 60
    segundos = int(record['segundos']) % 60
    return "Record: oleada %d - %d franceses - %s - %d:%02d" % (
        record['oleada'], record['bajas'], nombreRango, minutos, segundos)
