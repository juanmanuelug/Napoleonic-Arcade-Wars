"""Lanza todas las baterias de prueba y resume.

    python pruebas/todas.py

Cada bateria corre en su propio proceso a proposito: parchean cosas de pygame (el reloj, el
teclado, los eventos) y compartir intereprete las haria interferir entre si.
Devuelve 0 si todo esta en verde, 1 si hay algun fallo.
"""
import glob
import os
import subprocess
import sys

import entorno


def contarLineas(salida):
    correctas = sum(1 for linea in salida.splitlines() if linea.startswith('  OK  '))
    fallidas = sum(1 for linea in salida.splitlines() if linea.startswith(' FALLO '))
    return correctas, fallidas


def main():
    baterias = sorted(glob.glob(os.path.join(entorno.AQUI, 'probar_*.py')))
    if not baterias:
        print("No hay ninguna bateria probar_*.py en", entorno.AQUI)
        return 1

    print("%-26s %14s %7s  %s" % ("bateria", "comprobaciones", "fallos", "estado"))
    print("-" * 60)
    totalCorrectas = 0
    totalFallidas = 0
    rotas = []
    for ruta in baterias:
        nombre = os.path.basename(ruta)[:-3]
        proceso = subprocess.run([sys.executable, ruta], capture_output=True, text=True)
        correctas, fallidas = contarLineas(proceso.stdout)
        totalCorrectas += correctas
        totalFallidas += fallidas
        if proceso.returncode == 0 and fallidas == 0:
            estado = "OK"
        else:
            estado = "FALLO"
            rotas.append((nombre, proceso))
        print("%-26s %14d %7d  %s" % (nombre, correctas, fallidas, estado))

    print("-" * 60)
    print("%-26s %14d %7d" % ("%d baterias" % len(baterias), totalCorrectas, totalFallidas))

    for nombre, proceso in rotas:
        print()
        print("=" * 60)
        print("salida de", nombre)
        print("=" * 60)
        print(proceso.stdout.strip())
        if proceso.stderr.strip():
            print(proceso.stderr.strip())

    return 1 if rotas else 0


if __name__ == '__main__':
    sys.exit(main())
