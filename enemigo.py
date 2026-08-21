import pygame
import random
import granadas
import math
import sablazos
from proyectile import proyectil
import sonidos
from render import dibujar_anclado, destello, dibujar_aura

pygame.init()
# ####################################### Constantes  ##################################################
WINX = 500
WINY = 500
# Milisegundos entre disparo y disparo de un tirador, y lo que se le ve el fogonazo
RECARGA_ENEMIGO = 1500
DURACION_FOGONAZO = 180
# Milisegundos que se ve blanco al recibir un impacto, y pixeles que le echa atras el plomo
DURACION_DESTELLO = 100
EMPUJE_IMPACTO = 5
# Margen de alineacion vertical con el que un tirador se da por encarado al jugador. Exigir la
# misma y exacta hacia que casi nunca disparasen, porque el jugador se mueve de 3 en 3 pixeles.
# Cada tirador anade su propia pizca, para que no disparen todos en el mismo frame
TOLERANCIA_PUNTERIA = 6
VARIACION_PUNTERIA = 3
# Puestos de tiro. Con una sola distancia, todos los tiradores acababan plantados a los mismos
# 180 px y a la misma altura, en fila india. Ahora cada uno que entra en batalla toma el
# siguiente puesto y se reparten la profundidad.
# Holgura al llegar al puesto, para que no tiemble adelante y atras al colocarse
MARGEN_PUESTO = 4
# La separacion entre puestos tiene que ser mayor que el ancho de un cuerpo (20) mas dos veces
# la holgura, o dos tiradores de puestos contiguos podrian acabar solapados
SEPARACION_PUESTOS = 30
PUESTO_MAS_CERCANO = 140
# El puesto mas lejano no pasa de 230: mas alla, con el jugador en el centro, el tirador se
# quedaria fuera de la pantalla disparando a alguien que no puede verle
PUESTOS_DE_TIRO = tuple(PUESTO_MAS_CERCANO + SEPARACION_PUESTOS * indice
                        for indice in (0, 2, 1, 3))
# Milisegundos de desfase propio, para que las descargas no salgan a la vez
DESFASE_MAXIMO_DESCARGA = 700
# El sable de la tropa de cuerpo a cuerpo: alza, AVISA UN SEGUNDO, y taja. El danio lo hace el
# tajo, no el contacto (ver jugador.sufrirContacto): tocarle no cuesta nada, y lo que cuesta es
# quedarse dentro de su alcance cuando cae el sable. Ese segundo de aviso es lo que hace que el
# cuerpo a cuerpo se pueda jugar en vez de solo sufrirlo: da tiempo a pegar y a apartarse.
# 600 ms y no 1000: con un segundo el aviso se hacia largo y el frances parecia parado. 600
# son 18 frames a 30 fps, que siguen siendo de sobra para verlo subir y salirse, y a cambio
# el golpe llega con intencion. El precio esta medido: aguantando quieto se pasa de 9,0 a
# 12,0 de danio por segundo; esquivando sigue siendo 0.
DURACION_ALZADO = 600
DURACION_TAJO = 200
# Lo que espera desde que cae un tajo hasta que empieza a alzar el siguiente
RECARGA_SABLE = 900
# Lo que quita un tajo. Es mas del doble de lo que costaba el contacto (8), a proposito: se
# esquiva entero, asi que comerselo tiene que doler
DANIO_SABLE = 18
# Cuanto se estira el alcance del sable mas alla del cuerpo. Sin esto, apartarse un pixel
# bastaria para esquivarlo, y el aviso de un segundo no significaria nada
ALCANCE_SABLE = 6
# De donde sale el arco del sablazo. Medido sobre el sprite del tajo: la empunadura cae en el
# borde delantero de la caja del cuerpo (21x30) y a 12 px de su borde de arriba, y de ahi la
# hoja sale 10 px hacia delante y hacia arriba
DESPLAZAMIENTO_DE_LA_MANO = 1
ALTURA_DE_LA_MANO = 12
# El oficial: no dispara ni lanza nada, pero mientras esta en pie los franceses que tenga cerca
# van un 50% mas rapidos. Es el primer enemigo al que te conviene disparar ANTES que al que
# tienes encima, que hasta ahora era siempre lo mas cercano.
VIDA_OFICIAL = 100
RADIO_DE_MANDO = 90
FACTOR_DE_MANDO = 1.5
# El anillo que ensenia hasta donde llega el mando. Va A TROZOS y no lleno a proposito: es
# informacion, no una amenaza que esquivar, asi que no puede competir con la marca roja de la
# granada, que si hay que mirarla. Por lo mismo no parpadea. Dorado apagado, el color del oficial
COLOR_DE_MANDO = (222, 186, 74)
# El halo de los que estan bajo su mando: el mismo dorado, translucido, para que el anillo del
# suelo y los soldados que acelera digan lo mismo de un vistazo
ALFA_DEL_HALO = 255
TROZOS_DEL_ANILLO = 12
# Un paso por pixel de circunferencia. Con menos, los trozos salen como motas sueltas y no
# como rayas: probado con 96 pasos y se veian 96 puntos desperdigados por el campo
PASOS_DEL_ANILLO = int(2 * math.pi * RADIO_DE_MANDO)
# El voltigeur, el tirador de la infanteria ligera: va al doble de velocidad, recarga antes y
# se planta por detras de la linea de tiro del soldado de linea. Su amenaza es la posicion, no
# el aguante: tiene la misma vida que una bayoneta, cae con los mismos tres disparos.
VEL_VOLTIGEUR = 2
RECARGA_VOLTIGEUR = 1100
# Sus puestos van por detras de los del soldado de linea, que llegan a 230. Con el jugador en
# el centro de la pantalla no caben 260 px de separacion, asi que el voltigeur se queda pegado
# al borde, que es lo mas lejos que se puede estar de el; el freno de la retirada en
# pathFinding ya se encarga de que siga estando a la vista y al alcance del plomo.
PUESTO_VOLTIGEUR_MAS_CERCANO = 260
PUESTOS_DE_VOLTIGEUR = tuple(PUESTO_VOLTIGEUR_MAS_CERCANO + SEPARACION_PUESTOS * indice
                             for indice in (0, 1))
# El granadero de la Guardia: aguanta mas, va mas lento y no necesita ponerse a tu altura,
# porque una granada no se esquiva cambiando de fila. Se planta en un anillo alrededor del
# jugador: ni tan lejos que no llegue, ni tan cerca que le pille su propio estallido
VIDA_GRANADERO = 150
DISTANCIA_DE_LANZAMIENTO = 190
DISTANCIA_MINIMA_GRANADERO = 110
RECARGA_GRANADA = 3800
DURACION_ARMADO = 340
DURACION_SUELTA = 240
# ##################################### El jefe de sable ##############################################
# El segundo de los cuatro jefes: el oficial al doble y con mas galon. Sus dos ataques son de
# cerca, asi que su problema es el contrario que el del granadero: el granadero te niega el suelo
# y este te persigue.
#
#   - el TAJO EN AREA, que no necesita tocarte: barre un circulo a su alrededor
#   - la CARGA, que cada cierto tiempo le lanza en linea recta contra ti
#
# Los dos avisan antes con el mismo circulo rojo que la granada (granadas.dibujarAviso), porque el
# jugador tiene que reconocer "aqui va a doler" venga de donde venga.
VIDA_JEFE_SABLE = 2400
# El tajo en area: avisa mas que el de la tropa (600) porque barre mucho mas, y pega mas
DURACION_ALZADO_DEL_JEFE = 850
RADIO_DEL_TAJO_DEL_JEFE = 82
DANIO_DEL_TAJO_DEL_JEFE = 30
RECARGA_DEL_TAJO_DEL_JEFE = 1700
# Lo que dura el giro con el que suelta el tajo. El cuerpo gira alternando el lado al que mira, que
# es como se gira en pixel art: rotar el sprite le hace dar volteretas y acaba boca abajo
DURACION_DEL_GIRO = 300
MS_POR_MEDIA_VUELTA = 60
# La carga: se planta, avisa marcando el pasillo por donde va a pasar, y sale disparado. Al acabar
# se queda un momento parado, que es la ventana para castigarle
RECARGA_DE_LA_CARGA = 5000
DISTANCIA_MAXIMA_DE_CARGA = 320
AVISO_DE_LA_CARGA = 750
VELOCIDAD_DE_LA_CARGA = 11
DURACION_DE_LA_CARGA = 700
RECUPERACION_DE_LA_CARGA = 700
DANIO_DE_LA_CARGA = 35
ANCHO_DEL_PASILLO_DE_CARGA = 26

# ##################################### El jefe granadero #############################################
# El primero de los cuatro jefes. Es el granadero al doble de tamanio y con galon (ver
# herramientas/jefe_granadero.py), y su habilidad es una LLUVIA: en vez de una granada suelta una
# rafaga de varias, una detras de otra y desperdigadas alrededor de donde estes.
#
# La rafaga se suelta de una en una y no todas a la vez a proposito: cada granada trae su marca
# roja, y verlas caer en secuencia se puede leer y correr. Cinco marcas apareciendo en el mismo
# frame no se leen, se sufren.
VIDA_JEFE_GRANADERO = 2400
# Y tiene TRES ataques, que van cambiando conforme le baja la vida. La idea es que la pelea tenga
# capitulos: lo que aprendiste a esquivar deja de servir y hay que leer otra cosa.
ATAQUE_LLUVIA = 'lluvia'
ATAQUE_ANILLOS = 'anillos'
ATAQUE_COLUMNAS = 'columnas'
#por encima de 3/4 de vida la lluvia; de 3/4 a 1/4 los anillos; por debajo de 1/4 las columnas
VIDA_PARA_LOS_ANILLOS = 0.75
VIDA_PARA_LAS_COLUMNAS = 0.25
# Lo que tarda en soltar una granada de la rafaga y la siguiente. Una a una y no todas de golpe:
# cada granada trae su marca, y en secuencia se pueden leer y correr
INTERVALO_DE_LA_RAFAGA = 220
# Lo que espera entre una rafaga y la siguiente. 2200 y no 5200: con cinco segundos de calma entre
# patrones, el combate era esquivar un rato y disparar tranquilo otro rato. Encadenandolas, las
# marcas de la siguiente aparecen mientras revientan las de la anterior y hay que pensar dos
# jugadas por delante, que es lo que convierte el combate en un combate
RECARGA_DE_LA_RAFAGA = 2200

# FASE 1, la lluvia: granadas desperdigadas alrededor del jugador. Tiene que dejar hueco: con el
# radio del estallido en 40 px y 1,5 s de vuelo, el jugador recorre unos 135 px
# Nueve y no cinco: cinco se esquivaban andando. Y con nueve hay que abrir la dispersion, o los
# estallidos taparian el area entera y dejaria de ser esquivable: con 110 tapaban el 93%.
#
# Pero la PRIMERA cae siempre justo encima del jugador, no desperdigada. Sin eso, con 150 de
# dispersion la probabilidad de que una granada suelta alcance a alguien quieto es del 6%, o sea
# media granada por rafaga: quedarse plantado disparando era la mejor jugada posible.
GRANADAS_DE_LA_LLUVIA = 9
DISPERSION_DE_LA_LLUVIA = 150

# FASE 2, la onda: anillos concentricos alrededor del JUGADOR, no del jefe. Antes iban alrededor
# del jefe, y bastaba con acorralarlo en una esquina para que la fase entera cayese lejos.
#
# El primero cae pegado a el, y cada uno siguiente ROZA al de dentro: el paso es justo el diametro
# del estallido, asi que dos anillos seguidos se tocan y no queda banda libre entre ellos. Como
# todos llevan el mismo numero de granadas, el hueco entre impactos crece con el radio: el centro
# queda sellado y hay que salir por fuera, que es lo que da la sensacion de onda que te echa.
ANILLOS_DE_LA_ONDA = 5
# El primero tiene que ser MENOR que el radio del estallido, o deja un agujero justo en el centro
# de la onda, que es exactamente donde esta el jugador cuando empieza. Con 50 el anillo tapaba de
# 10 a 90 px del centro y quedarse quieto era gratis; con 30 tapa de 0 a 70.
# Nueve por anillo y no seis: con seis, del segundo anillo hacia fuera se colaba cualquiera. Con
# nueve, los dos de dentro quedan sellados y hay que salir corriendo desde el primer aviso
GRANADAS_POR_ANILLO = 9
RADIO_DEL_PRIMER_ANILLO = 30
# Milisegundos entre las granadas de un mismo anillo y entre un anillo y el siguiente. Dentro del
# anillo van muy seguidas para que se lea como UN circulo y no como un goteo
INTERVALO_DENTRO_DEL_ANILLO = 70
PAUSA_ENTRE_ANILLOS = 600

# FASE 3, el barrido: columnas de granadas que cubren el mapa ENTERO en un solo ataque. Entran
# por los dos bordes a la vez y se van cerrando hacia el centro, par a par.
#
# Las columnas van a 70 px unas de otras y el estallido mide 80 de diametro, asi que a lo ancho no
# queda hueco: el mapa se cubre de lado a lado y esquivar a los lados no sirve. Lo que si queda son
# huecos a lo ALTO, y ahi esta el juego. Y para que no baste con aparcar en un pasillo, cada par
# entra desplazado medio hueco respecto al anterior: los pasillos se mueven y hay que ir con ellos.
# 130 de separacion deja pasillos de 50 px, con un jugador de 36: catorce de margen. Con 140 eran
# 60 y sobraba sitio
SEPARACION_EN_LA_COLUMNA = 130
PASO_DE_LA_COLUMNA = 70
MARGEN_DE_LA_COLUMNA = 30
# Dentro de un par las granadas van seguidas y entre par y par hay pausa, igual que en la onda:
# asi se ven las dos paredes avanzando en vez de un goteo
INTERVALO_DENTRO_DE_LA_COLUMNA = 70
# 480 y no 600: menos tiempo para cambiar de pasillo entre pared y pared, pero sigue dando
PAUSA_ENTRE_COLUMNAS = 480

# ##################################### El jefe fusilero ##############################################
# El tercero de los cuatro jefes: el soldado de linea al doble y con galon (ver
# herramientas/jefe_fusilero.py). Los otros dos jefes juegan con el suelo (el granadero) y con la
# distancia corta (el de sable); este juega con las LINEAS DE FUEGO.
#
# Su plomo no cae del cielo con aviso: sale de su mosquete y viaja, se ve venir y ocupa un sitio
# durante todo el camino. Asi que no se esquiva leyendo el suelo ni saliendo de un circulo, se
# esquiva COLOCANDOSE: eligiendo donde estar respecto a el.
#
# Y trae una regla propia que ninguno de los otros dos tiene: el abanico se abre con la distancia.
# Pegado a el las balas van juntas y no hay hueco; lejos se separan y se cuela cualquiera. Es el
# unico jefe al que conviene NO acercarse, y eso ya es una leccion distinta que aprender.
VIDA_JEFE_FUSILERO = 2400
# Se planta por detras de la tropa de linea (140 a 230) y por delante del voltigeur (260 a 290).
#
# Y 210 y no 260 porque a 260, con el jugador en el centro del mapa, la distancia no cabe: el jefe
# se quedaba pegado al borde y medio fuera de pantalla, que es donde acaba el voltigeur y para un
# jefe con barra de vida propia no vale.
PUESTO_DEL_JEFE_FUSILERO = 210
# Y tiene TRES ataques, uno por trozo de vida, igual que el granadero: lo que aprendes a esquivar
# deja de servir y hay que leer otra cosa
ATAQUE_ABANICO = 'abanico'
ATAQUE_CORTINA = 'cortina'
ATAQUE_PLAZA = 'plaza'
#por encima de 3/4 el abanico; de 3/4 a 1/4 la cortina; por debajo de 1/4 el fuego de plaza
VIDA_PARA_LA_CORTINA = 0.75
VIDA_PARA_LA_PLAZA = 0.25
# Lo que espera entre una descarga y la siguiente. Cuatro segundos, y aqui este jefe se sale de la
# regla de los otros dos a proposito.
#
# El granadero encadena rafagas cada 2,2 s porque su aviso es una marca en el suelo que revienta y
# se acaba: entre rafaga y rafaga el suelo queda limpio. El plomo de este va lento y tarda tres
# segundos y pico en cruzar el mapa, asi que las balas de una descarga TODAVIA ESTAN VOLANDO cuando
# empieza la siguiente. Medido: con 1,4 s de recarga hay plomo en pantalla el 98% del tiempo y en la
# fase del abanico arranca una descarga cada 2,1 s. Eso no es un jefe exigente, es un jefe que no
# calla, y encima tapa su propio aviso: el arco rojo del suelo se lee mal con la pantalla llena de
# plomo de la descarga anterior.
#
# A 4 s hay calma de verdad entre descarga y descarga, y esa calma es la que hace que el aviso valga
# para algo y la que deja tiempo de mirar a la escolta y de disparar.
RECARGA_DE_LA_DESCARGA = 4000
# Una bala suya pega menos que una de la tropa (25 de DANIO_BALA): son muchas a la vez, y con el
# danio de la tropa dos que te pillasen serian medio jugador
DANIO_DE_LA_PERDIGONADA = 15
# Y su plomo va MAS LENTO que el de la tropa (8 px por frame). Es lo que convierte una descarga en
# un paraguas: a 8 px las balas cruzan la pantalla en dos segundos y lo que se ve es un pestanieo,
# a 5 tardan tres y pico y se ve el chorro ABRIRSE, que es la forma que hay que leer. Y como se ve
# venir, se puede andar entre las balas en vez de tener que adivinar el hueco de antemano.
VELOCIDAD_DEL_PLOMO_DEL_JEFE = 5
# Antes de cada descarga APUNTA: se planta, se le marca en el suelo por donde va a salir el plomo, y
# entonces empieza a salir. Los otros dos jefes avisan con el circulo rojo de la granada; este avisa
# con el arco, porque lo suyo no es un sitio del suelo, es una direccion.
#
# Y apuntando esta PLANTADO, igual que el jefe de sable cuando se recupera de la carga: mientras
# suelta el paraguas es un blanco quieto, y esa es la ventana para castigarle.
DURACION_DE_LA_PUNTERIA = 550
LARGO_DEL_AVISO_DEL_PLOMO = 110
PASO_DEL_AVISO_DEL_PLOMO = 7
# Y ENTRE DESCARGA Y DESCARGA embiste a la bayoneta, como el jefe de sable. Los dos ataques se
# turnan: descarga, carga, descarga, carga. Es lo que arregla el problema de fondo de un jefe de
# tiro con cuatro segundos de recarga: con solo disparar, esos cuatro segundos eran cuatro segundos
# de nada, y el combate era esperar. Turnandose, siempre viene algo, pero nunca lo mismo dos veces.
#
# Y por eso este jefe no trae escolta: la escolta estaba para que no te quedases quieto mirando al
# jefe, y de eso ya se encarga el jefe solo. Es el unico de los cuatro que pelea sin guardias.
#
# Embiste desde mas lejos y mas rapido que el de sable, porque tiene que cruzar todo su puesto de
# tiro (210 px) para llegar; y se queda plantado mas rato al acabar, porque acaba pegado a ti con un
# mosquete y eso tiene que costarle algo.
ESPERA_HASTA_LA_CARGA = 1200
DISTANCIA_DE_LA_CARGA_DEL_FUSILERO = 340
AVISO_DE_LA_CARGA_DEL_FUSILERO = 800
VELOCIDAD_DE_LA_CARGA_DEL_FUSILERO = 13
DURACION_DE_LA_CARGA_DEL_FUSILERO = 800
RECUPERACION_DE_LA_CARGA_DEL_FUSILERO = 900
DANIO_DE_LA_CARGA_DEL_FUSILERO = 30

# FASE 1, el abanico: una descarga de balas en arco, centrada en la direccion del jugador.
#
# El abanico se mide en PIXELES DE HUECO, no en grados de apertura, y esto es lo que hace que sea
# justo. Con una apertura fija en grados, el hueco entre dos balas crece con la distancia: a 260 px
# eran 53 px de hueco (esquivable, el jugador mide 36 de alto) y a 154 px eran 27 (imposible, 30 de
# danio inevitables por descarga). O sea que la justicia del ataque dependia de una distancia que
# el jefe no puede garantizar, porque el jugador decide donde ponerse.
#
# Poniendo el hueco en pixeles a la altura del jugador, el abanico se abre o se cierra solo y deja
# el mismo paso desde donde sea. 54 px de hueco para un jugador de 36 de alto son 18 de margen, el
# mismo que deja el barrido del jefe granadero, que esta probado que se esquiva.
#
# Y es el MISMO hueco en las tres fases, no uno por fase: el jugador aprende una sola medida y le
# sirve para todo el combate. Lo que cambia entre fases es como le llega el plomo, no por donde cabe
SEPARACION_ENTRE_BALAS = 54
BALAS_DEL_ABANICO = 7
# Las balas de un mismo abanico salen todas en el MISMO frame, al contrario que las granadas del
# granadero. Con las granadas hay que espaciarlas porque su aviso es una marca en el suelo y siete
# marcas apareciendo juntas no se leen; una bala se lee sola, porque la ves viajar.
#
# Pero la descarga son DOS abanicos seguidos con los MISMOS angulos, y ahi esta la salida al
# atasco de subir el danio sin cerrar los huecos: repetir el mismo arco no cierra ninguno, porque
# los angulos no cambian. Quien esta en un hueco sigue estandolo y quien no, cobra dos veces.
# Medido: subir de 7 a 9 balas dobla el danio pero deja los sitios a salvo en el 2%; repetir el
# abanico lo dobla igual y los deja en el 10%.
#
# Y el segundo NO vuelve a apuntar: el abanico va a donde estabas, y aprovechar eso es el juego.
# Reapuntando seria un ataque que te persigue, que es lo del jefe de sable y no lo suyo.
ABANICOS_POR_DESCARGA = 2
#130 ms, o sea cuatro frames: los dos arcos se leen como una descarga doble y no como dos ataques.
#Y cuanto mas separados, menos vale estar en un hueco, porque el jugador se mueve entre uno y otro:
#medido, con 380 ms los sitios a salvo caen del 8% al 3%
PAUSA_ENTRE_ABANICOS = 130

# FASE 2, la cortina: el mismo abanico pero BARRIDO, disparando mientras el arco gira. Sale una
# bala cada poco desde un extremo del arco hasta el otro, como un limpiaparabrisas.
#
# El abanico se esquiva colandose por un hueco; la cortina no, porque el hueco se mueve: hay que
# correr hacia donde el barrido YA HA PASADO, o sea al contrario de como gira. Eso es lo que la
# hace un ataque distinto y no el mismo con mas balas.
# Es EL MISMO ARCO del abanico, con los mismos huecos de 54 px, pero mas ancho y soltado bala a
# bala en vez de de golpe. Once balas hacen una pared de 540 px a la altura del jugador, o sea el
# alto entero del mapa: de la cortina no se sale por los lados, se sale por un hueco.
#
# Y ahi esta la diferencia con el abanico, que es lo que la hace un ataque distinto y no el mismo
# con mas balas: el hueco del abanico esta quieto y te colocas en el; el de la cortina se mueve,
# porque las balas van saliendo en orden, y hay que ir con el.
BALAS_DE_LA_CORTINA = 11
# Rapido, para que se lea como una cortina que barre y no como once tiros sueltos. Y 60 ms y no 80:
# medido, a 80 ms la cortina hacia 7 de danio por segundo a un blanco quieto y a 60 hace 11
INTERVALO_DE_LA_CORTINA = 60
# Y barre de IDA Y VUELTA, por lo mismo que el abanico va doble: la vuelta pasa por los mismos
# angulos que la ida, asi que no tapa ningun hueco, pero al que se quedo en medio le cobra dos
# veces. Con una sola pasada la cortina hacia 4 de danio por segundo a un blanco quieto, que es no
# hacer nada. Y de paso, un limpiaparabrisas que va y vuelve se lee mejor que uno que solo va.
#
# Tres pasadas y no dos: con tres, la descarga dura casi dos segundos y la fase se convierte en
# fuego continuo, que es lo que le toca a la fase de en medio. Medido, de 7 a 11 de danio por
# segundo dejando a salvo el 10% de los sitios.
PASADAS_DE_LA_CORTINA = 3

# FASE 3, el fuego de plaza: anillos de balas en todas las direcciones, uno detras de otro.
#
# Un anillo de balas deja huecos que se abren conforme se alejan del jefe, asi que el hueco por el
# que sales existe siempre. Lo que no se puede es quedarse: cada anillo sale GIRADO medio paso
# respecto al anterior, asi que el hueco por el que se colo el primero lo tapa el segundo.
BALAS_DEL_ANILLO = 16
ANILLOS_DE_LA_PLAZA = 3
# Cuanto gira cada anillo respecto al anterior, en fracciones del paso entre dos balas. Un cuarto
# y no medio: con medio, el hueco se mueve 51 px de arco entre anillo y anillo y el jugador solo
# recorre 38 en ese rato, asi que no llegaba y el ataque era inevitable. Y encima con tres anillos
# y medio paso, el tercero cae en los mismos angulos que el primero. Con un cuarto de paso el
# hueco se desplaza 25 px cada vez: hay que ir siguiendolo, y se puede
GIRO_POR_ANILLO = 0.25
# Dentro del anillo van todas en el mismo frame, para que se lea como un circulo que se abre
PAUSA_ENTRE_ANILLOS_DE_PLOMO = 420
# Los cadaveres desaparecen al cabo de un rato y nunca hay mas de MAX_CADAVERES en pantalla
DURACION_CADAVER = 12000
MAX_CADAVERES = 20
# Los enemigos aparecen por fuera del borde y nunca encima del jugador
MARGEN_APARICION = 40
DISTANCIA_MINIMA_APARICION = 150
INTENTOS_APARICION = 8
# #######################################   Sonidos  ###################################################
sound_musket = pygame.mixer.Sound('./sonido/musket_shot04.wav')
sound_musket.set_volume(0.2)
##############Soldados Franceses#################
Andar_izq_Fr = [pygame.image.load('./sprites/franceses/soldado_fr_izq_0.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_1.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_2.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_3.png'),
             pygame.image.load('./sprites/franceses/soldado_fr_izq_4.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_5.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_6.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_1.png'),
             pygame.image.load('./sprites/franceses/soldado_fr_izq_2.png')]
Andar_dch_Fr = [pygame.image.load('./sprites/franceses/soldado_fr_dch_0.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_1.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_2.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_3.png'),
             pygame.image.load('./sprites/franceses/soldado_fr_dch_4.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_5.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_6.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_1.png'),
             pygame.image.load('./sprites/franceses/soldado_fr_dch_2.png')]

Disparar_izq_Fr = [pygame.image.load('./sprites/franceses/soldado_fr_izq_disparar_1.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_disparar.png')]
Disparar_dch_Fr = [pygame.image.load('./sprites/franceses/soldado_fr_dch_disparar_1.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_disparar.png')]

Andar_izq_Fr_cuerpo = [pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_2.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_3.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_4.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_5.png'),
             pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_6.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_2.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_3.png'), pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_4.png'),
             pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_5.png')]
Andar_dch_Fr_cuerpo = [pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_2.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_3.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_4.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_5.png'),
             pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_6.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_2.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_3.png'), pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_4.png'),
             pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_5.png')]

#El sable de la tropa de cuerpo a cuerpo. Estos dos fotogramas estaban ya dibujados y no se
#usaban: la animacion de andar de arriba solo gasta del 2 al 6. El 1 es el mas recogido (22 px
#de ancho util, el sable en alto) y el 0 el mas largo de los siete (30 px, el brazo extendido).
Alzar_izq_Fr = pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_1.png')
Tajar_izq_Fr = pygame.image.load('./sprites/franceses/soldado_fr_izq_cuerpoAcuerpo_0.png')
Alzar_dch_Fr = pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_1.png')
Tajar_dch_Fr = pygame.image.load('./sprites/franceses/soldado_fr_dch_cuerpoAcuerpo_0.png')

##############Oficiales#################
#los mismos 14 fotogramas de cuerpo a cuerpo con penacho y banda dorada; los saca
#herramientas/oficial.py
def _cicloDeCuerpoACuerpo(patron):
    #la misma lista de nueve entradas que la tropa de cuerpo a cuerpo: del 2 al 6 y vuelta a
    #empezar, porque el 0 y el 1 no son de andar, son el sable
    dibujos = [pygame.image.load(patron % numero) for numero in range(2, 7)]
    return dibujos + dibujos[:4]

Andar_izq_Of = _cicloDeCuerpoACuerpo('./sprites/franceses/oficial_fr_izq_cuerpoAcuerpo_%d.png')
Andar_dch_Of = _cicloDeCuerpoACuerpo('./sprites/franceses/oficial_fr_dch_cuerpoAcuerpo_%d.png')
Alzar_izq_Of = pygame.image.load('./sprites/franceses/oficial_fr_izq_cuerpoAcuerpo_1.png')
Tajar_izq_Of = pygame.image.load('./sprites/franceses/oficial_fr_izq_cuerpoAcuerpo_0.png')
Alzar_dch_Of = pygame.image.load('./sprites/franceses/oficial_fr_dch_cuerpoAcuerpo_1.png')
Tajar_dch_Of = pygame.image.load('./sprites/franceses/oficial_fr_dch_cuerpoAcuerpo_0.png')

##############Granaderos de la Guardia#################
def _cicloDeAndar(patron):
    #la misma lista de nueve entradas que usan los demas: siete dibujos y dos repetidos
    dibujos = [pygame.image.load(patron % numero) for numero in range(7)]
    return dibujos + [dibujos[1], dibujos[2]]

Andar_izq_Gr = _cicloDeAndar('./sprites/franceses/granadero_fr_izq_%d.png')
Andar_dch_Gr = _cicloDeAndar('./sprites/franceses/granadero_fr_dch_%d.png')
Lanzar_izq_Gr = [pygame.image.load('./sprites/franceses/granadero_fr_izq_lanzar_0.png'),
                 pygame.image.load('./sprites/franceses/granadero_fr_izq_lanzar_1.png')]
Lanzar_dch_Gr = [pygame.image.load('./sprites/franceses/granadero_fr_dch_lanzar_0.png'),
                 pygame.image.load('./sprites/franceses/granadero_fr_dch_lanzar_1.png')]

##############Voltigeurs de la infanteria ligera#################
#los mismos 18 sprites del soldado de linea con el penacho y la banda del chaco encima; los
#saca herramientas/voltigeur.py y no se dibujan a mano
Andar_izq_Vo = _cicloDeAndar('./sprites/franceses/voltigeur_fr_izq_%d.png')
Andar_dch_Vo = _cicloDeAndar('./sprites/franceses/voltigeur_fr_dch_%d.png')
Disparar_izq_Vo = [pygame.image.load('./sprites/franceses/voltigeur_fr_izq_disparar_1.png'),
                   pygame.image.load('./sprites/franceses/voltigeur_fr_izq_disparar.png')]
Disparar_dch_Vo = [pygame.image.load('./sprites/franceses/voltigeur_fr_dch_disparar_1.png'),
                   pygame.image.load('./sprites/franceses/voltigeur_fr_dch_disparar.png')]

##############El jefe de sable: el oficial al doble, con mas galon#################
Andar_izq_JSa = _cicloDeCuerpoACuerpo('./sprites/franceses/jefesable_fr_izq_cuerpoAcuerpo_%d.png')
Andar_dch_JSa = _cicloDeCuerpoACuerpo('./sprites/franceses/jefesable_fr_dch_cuerpoAcuerpo_%d.png')
Alzar_izq_JSa = pygame.image.load('./sprites/franceses/jefesable_fr_izq_cuerpoAcuerpo_1.png')
Tajar_izq_JSa = pygame.image.load('./sprites/franceses/jefesable_fr_izq_cuerpoAcuerpo_0.png')
Alzar_dch_JSa = pygame.image.load('./sprites/franceses/jefesable_fr_dch_cuerpoAcuerpo_1.png')
Tajar_dch_JSa = pygame.image.load('./sprites/franceses/jefesable_fr_dch_cuerpoAcuerpo_0.png')

##############El jefe granadero: el mismo al doble, con galon#################
Andar_izq_JGr = _cicloDeAndar('./sprites/franceses/jefegranadero_fr_izq_%d.png')
Andar_dch_JGr = _cicloDeAndar('./sprites/franceses/jefegranadero_fr_dch_%d.png')

##############El jefe fusilero: el soldado de linea al doble, con galon y penacho#################
#los saca herramientas/jefe_fusilero.py a partir de los 18 del soldado de linea
Andar_izq_JFu = _cicloDeAndar('./sprites/franceses/jefefusilero_fr_izq_%d.png')
Andar_dch_JFu = _cicloDeAndar('./sprites/franceses/jefefusilero_fr_dch_%d.png')
Disparar_izq_JFu = [pygame.image.load('./sprites/franceses/jefefusilero_fr_izq_disparar_1.png'),
                    pygame.image.load('./sprites/franceses/jefefusilero_fr_izq_disparar.png')]
Disparar_dch_JFu = [pygame.image.load('./sprites/franceses/jefefusilero_fr_dch_disparar_1.png'),
                    pygame.image.load('./sprites/franceses/jefefusilero_fr_dch_disparar.png')]

cadaverImg = pygame.image.load('./sprites/franceses/cadaver.png')
cadaverOficialImg= pygame.image.load('./sprites/franceses/cadaverOficialImg.png')
#el granadero moria con el chaco del soldado de linea aunque en pie lleve bonete de piel de oso:
#este es el mismo cuerpo tirado con el bonete y su penacho (ver herramientas/cadaver_granadero.py)
cadaverGranaderoImg = pygame.image.load('./sprites/franceses/cadaver_granadero.png')

# Los jefes miden el doble, y con el cadaver de la tropa morian encogiendose a la mitad. Se escala
# el mismo dibujo, que a x2 sale limpio (cada pixel es un cuadrado de 2x2), y se guarda: un cadaver
# se escala una sola vez en toda la partida, no una vez por frame
_cadaveresEscalados = {}


def cadaverEscalado(imagen, escala):
    if escala == 1:
        return imagen
    if (imagen, escala) not in _cadaveresEscalados:
        _cadaveresEscalados[(imagen, escala)] = pygame.transform.scale(
            imagen, (imagen.get_width() * escala, imagen.get_height() * escala))
    return _cadaveresEscalados[(imagen, escala)]
# #######################################   Funciones   ###############################################

def _puntoEnElBorde():
    #un punto justo por fuera de uno de los cuatro bordes
    lado = random.choice(('izquierda', 'derecha', 'arriba', 'abajo'))
    if lado == 'izquierda':
        return -MARGEN_APARICION, random.randint(0, WINY)
    if lado == 'derecha':
        return WINX + MARGEN_APARICION, random.randint(0, WINY)
    if lado == 'arriba':
        return random.randint(0, WINX), -MARGEN_APARICION
    return random.randint(0, WINX), WINY + MARGEN_APARICION


def _distanciaAlCuadrado(punto, otro):
    return (punto[0] - otro[0]) ** 2 + (punto[1] - otro[1]) ** 2


def puntoDeAparicion(xObjetivo, yObjetivo):
    """Un punto del borde por el que entrar en batalla, lo bastante lejos del jugador."""
    objetivo = (xObjetivo, yObjetivo)
    candidatos = [_puntoEnElBorde() for _ in range(INTENTOS_APARICION)]
    lejanos = [punto for punto in candidatos
               if _distanciaAlCuadrado(punto, objetivo) >= DISTANCIA_MINIMA_APARICION ** 2]
    if lejanos:
        return random.choice(lejanos)
    #si el jugador esta pegado a un borde puede que ninguno valga: se coge el mas lejano
    return max(candidatos, key=lambda punto: _distanciaAlCuadrado(punto, objetivo))


#un turno por linea de tiro: la del soldado de linea y la del voltigeur van cada una a lo suyo
_siguientePuesto = {}


def tomarPuestoDeTiro(puestos=PUESTOS_DE_TIRO):
    """Reparte los puestos por turno: dos tiradores seguidos nunca se plantan a la vez."""
    turno = _siguientePuesto.get(puestos, 0)
    _siguientePuesto[puestos] = turno + 1
    return puestos[turno % len(puestos)]


def puestoLibre(enemigosVivos, puestos=PUESTOS_DE_TIRO):
    """Un puesto que no tenga ya otro tirador; si estan todos cogidos, el siguiente por turno.

    Se mira solo dentro de su propia linea de tiro: un voltigeur, que se planta mucho mas
    atras, no le ocupa el puesto a un soldado de linea ni al contrario.
    """
    ocupados = [otro.distanciaDeTiro for otro in enemigosVivos
                if isinstance(otro, enemigoDistancia) and otro.PUESTOS == puestos]
    libres = [puesto for puesto in puestos if puesto not in ocupados]
    if libres:
        return random.choice(libres)
    return tomarPuestoDeTiro(puestos)


def aplicarMando(enemigos):
    """Pone a cada frances su velocidad, x1.5 si tiene un oficial cerca. Una vez por frame.

    Se recalcula entera en vez de ir sumando y restando: asi, cuando el oficial cae o se aleja,
    la velocidad vuelve sola a la suya sin que nadie tenga que llevar la cuenta.
    """
    mandos = [uno for uno in enemigos if isinstance(uno, oficial) and uno.vivo]
    for frances in enemigos:
        frances.vel = frances.VELOCIDAD
        frances.conMando = False
        #un oficial no se acelera a si mismo ni a otro oficial: el aura es para la tropa
        if isinstance(frances, oficial):
            continue
        for mando in mandos:
            if (_distanciaAlCuadrado(frances.rect.center, mando.rect.center)
                    <= RADIO_DE_MANDO ** 2):
                frances.vel = frances.VELOCIDAD * FACTOR_DE_MANDO
                frances.conMando = True
                break


def cadaveresVigentes(cadaveres):
    """Quita los cadaveres que ya han cumplido su tiempo y limita cuantos se acumulan."""
    ahora = pygame.time.get_ticks()
    vigentes = [cadaver for cadaver in cadaveres
                if ahora - cadaver.instanteMuerte < DURACION_CADAVER]
    return vigentes[-MAX_CADAVERES:]

# #######################################   Clases   ##################################################

#######Enemigos###############
##Enemigo BASE
class enemigo(object):
    #Lienzo de referencia de sus sprites (los de cuerpo a cuerpo miden 30x32) y caja del
    #cuerpo dentro de ese lienzo: excluye la bayoneta, que sobresale por el lado al que mira
    ANCHO_REFERENCIA = 30
    ALTO_REFERENCIA = 32
    CUERPO_IZQ = pygame.Rect(6, 2, 21, 30)
    CUERPO_DCH = pygame.Rect(3, 2, 21, 30)
    #Altura de la boca del mosquete respecto a la esquina de la caja del cuerpo
    ALTURA_CANON = 21
    #Vida con la que aparece
    VIDA_INICIAL = 75
    #Lo que vale para el rango del jugador. Matar un granadero de 150 de vida no puede contar
    #lo mismo que una bayoneta de 75: el rango premia la dificultad, no el volumen
    PUNTOS = 1
    #Con que probabilidad suelta algo al caer. Es la palanca con la que se ajusta el ritmo
    #de objetos de toda la partida, y cada tipo de enemigo trae la suya
    PROBABILIDAD_SUELTA = 0.18
    #esta tropa pelea con sable. Los que van con el mosquete heredan de esta clase, asi que
    #heredan tambien el sable: lo apagan poniendo esto a False
    PELEA_CON_SABLE = True
    #si es uno de los cuatro jefes. Lo usa el HUD para saber a quien le pone barra
    ES_JEFE = False
    #cuanto se agranda su cadaver. Los jefes miden el doble y su cadaver tambien
    ESCALA_CADAVER = 1
    #si es jefe, si pide escolta conforme le baja la vida. Lo lee main.llamarEscoltaDeLosJefes
    LLAMA_ESCOLTA = True
    #cuantos grupos de escolta ha llamado ya, para los que son jefes. Vive aqui y no en
    #las clases de jefe porque quien lo lee es main, y le da igual de que jefe se trate
    oleadasDeEscoltaPedidas = 0
    #velocidad propia. Esta aqui y no solo en el __init__ porque el aura del oficial la
    #recalcula cada frame, y necesita saber a que valor volver cuando el oficial cae
    VELOCIDAD = 1
    #sus sprites. Asi el oficial es esta misma clase con otros dibujos y otros numeros
    ANDAR_IZQ = Andar_izq_Fr_cuerpo
    ANDAR_DCH = Andar_dch_Fr_cuerpo
    ALZAR_IZQ = Alzar_izq_Fr
    ALZAR_DCH = Alzar_dch_Fr
    TAJAR_IZQ = Tajar_izq_Fr
    TAJAR_DCH = Tajar_dch_Fr

    def __init__(self,x,y,xObjectiv,yObjectiv):
        self.x=x
        self.y=y
        self.vel=self.VELOCIDAD
        #Para controlar el sprite que va apareciendo cuando camina
        self.contadorCaminar=0
        #Orientacion donde mira
        self.dch=False
        self.izq=True
        self.stop=True
        #Objetivo al que se dirige
        self.xObjectiv=xObjectiv
        self.yObjectiv=yObjectiv
        self.contadorPath=0
        #superficie de colision
        self.rect = self.CUERPO_IZQ.move(x, y)
        #vida
        self.vida=self.VIDA_INICIAL
        self.vidaMaxima=self.VIDA_INICIAL
        self.vivo=True
        #cuando cae, para que el cadaver no se quede en el campo para siempre
        self.instanteMuerte=0
        #ultimo impacto recibido, para el destello
        self.instanteUltimoDanio=pygame.time.get_ticks() - DURACION_DESTELLO
        #solo lo usan los que disparan, pero lo tienen todos para poder ajustar los relojes
        #de golpe cuando la partida se pausa en un ascenso
        self.instanteUltimoDisparo=pygame.time.get_ticks()
        #idem para los que lanzan granadas
        self.instanteUltimoLanzamiento=pygame.time.get_ticks()
        self.instanteInicioArmado=0
        #el sable: alzando o no, cuando empezo el alzado y cuando cayo el ultimo tajo. Empieza
        #con la recarga cumplida, para que el primero que te alcance no tenga que esperar
        self.alzandoSable=False
        self.instanteInicioAlzado=0
        self.instanteUltimoTajo=pygame.time.get_ticks() - RECARGA_SABLE
        #si ahora mismo le esta acelerando un oficial. Lo pone aplicarMando cada frame
        self.conMando=False

    def actualizarRect(self):
        #la caja de colision sigue al cuerpo dibujado, no al lienzo completo del sprite
        cuerpo = self.CUERPO_IZQ if self.izq else self.CUERPO_DCH
        self.rect = cuerpo.move(self.x, self.y)

    def xCanon(self):
        if self.izq:
            return self.rect.left
        return self.rect.right

    def alcanceDelSable(self):
        """Hasta donde llega el acero: su cuerpo estirado unos pixeles por todos los lados."""
        return self.rect.inflate(ALCANCE_SABLE * 2, ALCANCE_SABLE * 2)

    def atacar(self, objetivo, sablazosEnElAire):
        """Se llama cada frame: alza el sable, avisa un segundo, y al acabar suelta el tajo.

        El tajo SI hace el danio, y solo si el objetivo sigue dentro del alcance cuando cae. Ahi
        esta el juego: el alzado se ve venir, asi que apartarse a tiempo es gratis y quedarse
        cuesta DANIO_SABLE.
        """
        if not self.PELEA_CON_SABLE:
            return
        ahora = pygame.time.get_ticks()
        if self.alzandoSable:
            if ahora - self.instanteInicioAlzado >= DURACION_ALZADO:
                self.alzandoSable = False
                self.instanteUltimoTajo = ahora
                sablazosEnElAire.append(sablazos.Sablazo(self.xDeLaMano(),
                                                         self.yDeLaMano(), self.izq, ahora))
                sonidos.sonido_sable.play()
                #el aguardiente deja cruzar una linea de sables sin pagarlo
                if (self.alcanceDelSable().colliderect(objetivo.rect)
                        and not objetivo.tieneInmunidad(ahora)):
                    objetivo.recibirImpacto(DANIO_SABLE, 0)
            return
        if (self.alcanceDelSable().colliderect(objetivo.rect)
                and ahora - self.instanteUltimoTajo >= RECARGA_SABLE):
            self.alzandoSable = True
            self.instanteInicioAlzado = ahora

    def xDeLaMano(self):
        #la mano que lleva el sable va en el borde delantero del cuerpo
        if self.izq:
            return self.rect.left + DESPLAZAMIENTO_DE_LA_MANO
        return self.rect.right - DESPLAZAMIENTO_DE_LA_MANO

    def yDeLaMano(self):
        return self.rect.top + ALTURA_DE_LA_MANO

    def mostrandoTajo(self, ahora):
        return not self.alzandoSable and ahora - self.instanteUltimoTajo < DURACION_TAJO

    def pathFinding(self,xObjectiv,yObjectiv):
        self.xObjectiv=xObjectiv
        self.yObjectiv=yObjectiv
        if self.alzandoSable:
            #con el sable en alto no avanza, pero sigue encarando al jugador
            self.izq = xObjectiv < self.x
            self.dch = not self.izq
            self.stop = True
            self.actualizarRect()
            return
        if(self.yObjectiv!=self.y or self.xObjectiv!=self.x):
            if(self.xObjectiv < self.x):
                self.x-=self.vel
                self.dch=False
                self.izq=True
                self.stop=False
            else:
                self.x+=self.vel
                self.dch=True
                self.izq=False
                self.stop=False
            if(self.yObjectiv<self.y):
                self.y-=self.vel
                self.stop=False
            else:
                self.y+=self.vel
                self.stop=False
        else:
            self.stop=True
        self.actualizarRect()

    def sprite(self):
        #sprite que toca este frame; la clase hija anade el disparo
        if self.alzandoSable:
            return self.ALZAR_IZQ if self.izq else self.ALZAR_DCH
        if self.mostrandoTajo(pygame.time.get_ticks()):
            return self.TAJAR_IZQ if self.izq else self.TAJAR_DCH
        if not self.stop:
            secuencia = self.ANDAR_IZQ if self.izq else self.ANDAR_DCH
            imagen = secuencia[self.contadorCaminar // 3]
            self.contadorCaminar = (self.contadorCaminar + 1) % 27
            return imagen
        return self.ANDAR_IZQ[0] if self.izq else self.ANDAR_DCH[0]

    def dibujarEnemigo(self, win):
        imagen = self.sprite()
        if self.mostrandoDestello(pygame.time.get_ticks()):
            imagen = destello(imagen)
        #el halo va debajo del sprite, para que el soldado se siga leyendo igual
        if self.conMando:
            dibujar_aura(win, imagen, self.x, self.y, self.izq,
                         self.ANCHO_REFERENCIA, self.ALTO_REFERENCIA,
                         COLOR_DE_MANDO, ALFA_DEL_HALO)
        dibujar_anclado(win, imagen, self.x, self.y, self.izq,
                        self.ANCHO_REFERENCIA, self.ALTO_REFERENCIA)

    def recibirImpacto(self,danio,direccion=0):
        #el reparto de danio lo hace colisiones.resolverBalas, aqui solo se apunta
        self.vida-= danio
        self.instanteUltimoDanio = pygame.time.get_ticks()
        sonidos.sonido_impacto.play()
        #un empujon en la direccion del disparo: confirma el acierto sin numeros flotantes
        self.x += direccion * EMPUJE_IMPACTO
        self.actualizarRect()

    def mostrandoDestello(self, ahora):
        return ahora - self.instanteUltimoDanio < DURACION_DESTELLO

    def checkEstadoVida(self):
        if(self.vida<=0 and self.vivo):
            self.vivo=False
            self.instanteMuerte=pygame.time.get_ticks()
            sonidos.sonido_muerte.play()

    def disparar(self,bullets):
        #solo por herencia
        pass

    def lanzar(self,granadasEnElAire,puntoObjetivo):
        #solo por herencia
        pass

    def dibujarMando(self,win):
        #solo por herencia: el unico que tiene algo que enseniar en el suelo es el oficial
        pass

    def cargar(self,objetivo):
        #solo por herencia: el unico que embiste es el jefe de sable
        pass

    def dibujarCadaver(self,win):
        #anclado como el resto de sprites, para que caiga donde estaban sus pies. El cadaver
        #con dorados (cadaverOficialImg) es del oficial, no de la tropa
        dibujar_anclado(win, cadaverEscalado(cadaverImg, self.ESCALA_CADAVER),
                        self.x, self.y, self.izq, self.ANCHO_REFERENCIA, self.ALTO_REFERENCIA)

##Enemigo a distancia
class enemigoDistancia(enemigo):
    #sus sprites de andar miden 20x36, igual que los del jugador
    ANCHO_REFERENCIA = 20
    ALTO_REFERENCIA = 36
    CUERPO_IZQ = pygame.Rect(0, 0, 20, 36)
    CUERPO_DCH = pygame.Rect(0, 0, 20, 36)
    #el tirador es mas peligroso y esta mas lejos: suelta algo mas a menudo
    PROBABILIDAD_SUELTA = 0.28
    #y vale el doble: te dispara desde lejos
    PUNTOS = 2
    #va con el mosquete: no tiene fotogramas de sable
    PELEA_CON_SABLE = False
    #lo que distingue a un tirador de otro. Estan aqui y no en el __init__ para que el
    #voltigeur sea esta misma clase con otros cuatro numeros y otros sprites
    VELOCIDAD = 1
    RECARGA = RECARGA_ENEMIGO
    PUESTOS = PUESTOS_DE_TIRO
    ANDAR_IZQ = Andar_izq_Fr
    ANDAR_DCH = Andar_dch_Fr
    DISPARAR_IZQ = Disparar_izq_Fr
    DISPARAR_DCH = Disparar_dch_Fr

    def __init__(self,x,y,xObjectiv,yObjectiv,enemigosVivos=None):
        enemigo.__init__(self,x,y,xObjectiv,yObjectiv)
        self.vel = self.VELOCIDAD
        #recarga: como la del jugador, el sello de tiempo se pone al disparar. Empieza recargando
        #y con un desfase propio, asi no dispara a bocajarro al aparecer ni a la vez que los demas
        self.recarga = self.RECARGA
        self.instanteUltimoDisparo = (pygame.time.get_ticks()
                                      + random.randint(0, DESFASE_MAXIMO_DESCARGA))
        #su puesto en la linea de tiro: si le dicen quien esta ya en el campo, coge uno libre
        if enemigosVivos is None:
            self.distanciaDeTiro = tomarPuestoDeTiro(self.PUESTOS)
        else:
            self.distanciaDeTiro = puestoLibre(enemigosVivos, self.PUESTOS)
        #y su propio pulso al apuntar
        self.toleranciaPunteria = TOLERANCIA_PUNTERIA + random.randint(0, VARIACION_PUNTERIA)
        #sin esto se le veria el fogonazo al aparecer, antes de haber disparado nada
        self.haDisparado = False

    def puedeDisparar(self, ahora):
        return ahora - self.instanteUltimoDisparo >= self.recarga

    def mostrandoFogonazo(self, ahora):
        return self.haDisparado and ahora - self.instanteUltimoDisparo < DURACION_FOGONAZO

    def encarado(self):
        #a la altura del jugador con un margen, que es lo que le da linea de tiro
        return abs(self.yObjectiv - self.y) <= self.toleranciaPunteria

    def pathFinding(self,xObjectiv,yObjectiv):
        self.xObjectiv=xObjectiv
        self.yObjectiv=yObjectiv
        #mira hacia el jugador siempre, tambien estando quieto: antes se quedaba con la
        #orientacion con la que aparecio y disparaba hacia el lado contrario
        self.izq = xObjectiv < self.x
        self.dch = not self.izq
        moviendose = False
        #primero se pone a la altura del jugador
        if not self.encarado():
            if(yObjectiv < self.y):
                self.y-=self.vel
            else:
                self.y+=self.vel
            moviendose = True
        #y busca su puesto en profundidad: se acerca si esta lejos y RETROCEDE si el jugador se
        #le ha echado encima. Antes solo sabia acercarse, asi que un tirador que aparecia mas
        #cerca que su puesto se quedaba clavado donde entro, amontonado con los que entraron ahi
        haciaElJugador = 1 if xObjectiv > self.x else -1
        distanciaAlJugador = abs(xObjectiv - self.x)
        #recien aparecido esta fuera del campo: lo primero es entrar, su puesto ya se vera
        fueraDelCampo = self.x < 0 or self.x > WINX - self.ANCHO_REFERENCIA
        if fueraDelCampo or distanciaAlJugador > self.distanciaDeTiro + MARGEN_PUESTO:
            self.x += haciaElJugador * self.vel
            moviendose = True
        elif distanciaAlJugador < self.distanciaDeTiro - MARGEN_PUESTO:
            #se retira, pero nunca hasta salirse de la pantalla: un tirador al que no puedes
            #ver ni alcanzar, y que si te dispara, no es un enemigo, es una trampa
            retirada = self.x - haciaElJugador * self.vel
            if 0 <= retirada <= WINX - self.ANCHO_REFERENCIA:
                self.x = retirada
                moviendose = True
        self.stop = not moviendose
        self.actualizarRect()

    def sprite(self):
        if not self.stop:
            secuencia = self.ANDAR_IZQ if self.izq else self.ANDAR_DCH
            imagen = secuencia[self.contadorCaminar // 3]
            self.contadorCaminar = (self.contadorCaminar + 1) % 27
            return imagen
        secuencia = self.DISPARAR_IZQ if self.izq else self.DISPARAR_DCH
        return secuencia[1] if self.mostrandoFogonazo(pygame.time.get_ticks()) else secuencia[0]

    def disparar(self,bullets):
        ahora = pygame.time.get_ticks()
        if not self.encarado() or not self.puedeDisparar(ahora):
            return
        self.instanteUltimoDisparo = ahora
        self.haDisparado = True
        sound_musket.play()
        apuntando = -1 if self.izq else 1
        bullets.append(proyectil(self.xCanon(), self.y + self.ALTURA_CANON, apuntando))

    def dibujarCadaver(self,win):
        dibujar_anclado(win, cadaverEscalado(cadaverImg, self.ESCALA_CADAVER),
                        self.x, self.y, self.izq, self.ANCHO_REFERENCIA, self.ALTO_REFERENCIA)


##Voltigeur: el tirador de la infanteria ligera. El mismo tirador con otros cuatro numeros
class voltigeur(enemigoDistancia):
    #vale mas que el de linea y menos que el granadero: no aguanta mas plomo, pero te dispara
    #desde donde no puedes contestarle sin moverte de donde estas
    PUNTOS = 3
    PROBABILIDAD_SUELTA = 0.32
    VELOCIDAD = VEL_VOLTIGEUR
    RECARGA = RECARGA_VOLTIGEUR
    PUESTOS = PUESTOS_DE_VOLTIGEUR
    ANDAR_IZQ = Andar_izq_Vo
    ANDAR_DCH = Andar_dch_Vo
    DISPARAR_IZQ = Disparar_izq_Vo
    DISPARAR_DCH = Disparar_dch_Vo


##Oficial: no dispara, manda. Los suyos van mas rapidos mientras el siga en pie
class oficial(enemigo):
    #aguanta mas que la tropa pero menos que un granadero: cuatro disparos del mosquete base
    VIDA_INICIAL = VIDA_OFICIAL
    #vale mas que nadie, y no por lo que aguanta: mientras esta en pie, TODOS los demas son
    #mas peligrosos, asi que dejarlo vivo sale mas caro que dejar vivo a cualquier otro
    PUNTOS = 5
    #suelta objeto seguro. Es el enemigo al que hay que ir a buscar, y buscarlo tiene que pagar
    PROBABILIDAD_SUELTA = 1.0
    ANDAR_IZQ = Andar_izq_Of
    ANDAR_DCH = Andar_dch_Of
    ALZAR_IZQ = Alzar_izq_Of
    ALZAR_DCH = Alzar_dch_Of
    TAJAR_IZQ = Tajar_izq_Of
    TAJAR_DCH = Tajar_dch_Of

    def dibujarMando(self,win):
        """El anillo hasta donde llega su mando, pintado en el suelo y a trozos.

        Se dibuja antes que los soldados (ver main.drawWindow) para que quede debajo de todos:
        es una marca del terreno, no algo que flote por encima de la batalla.
        """
        centroX, centroY = self.rect.center
        for paso in range(PASOS_DEL_ANILLO):
            #un trozo si, un trozo no
            if (paso * TROZOS_DEL_ANILLO) // PASOS_DEL_ANILLO % 2:
                continue
            angulo = 2 * math.pi * paso / PASOS_DEL_ANILLO
            x = int(round(centroX + math.cos(angulo) * RADIO_DE_MANDO))
            y = int(round(centroY + math.sin(angulo) * RADIO_DE_MANDO))
            if 0 <= x < WINX and 0 <= y < WINY:
                win.set_at((x, y), COLOR_DE_MANDO)

    def dibujarCadaver(self,win):
        #el cadaver con dorados es suyo: hasta ahora lo llevaba la tropa de bayoneta y el
        #nombre del fichero (cadaverOficialImg) siempre canto que estaba cruzado
        dibujar_anclado(win, cadaverEscalado(cadaverOficialImg, self.ESCALA_CADAVER),
                        self.x, self.y, self.izq, self.ANCHO_REFERENCIA, self.ALTO_REFERENCIA)


##Granadero de la Guardia: lanza granadas con danio en area
class granadero(enemigo):
    #usa los sprites de andar de 20x36, como el tirador
    ANCHO_REFERENCIA = 20
    ALTO_REFERENCIA = 36
    CUERPO_IZQ = pygame.Rect(0, 0, 20, 36)
    CUERPO_DCH = pygame.Rect(0, 0, 20, 36)
    VIDA_INICIAL = VIDA_GRANADERO
    #cuesta mas de matar, asi que suelta algo mas a menudo
    PROBABILIDAD_SUELTA = 0.40
    #y vale cuatro: 150 de vida y granadas
    PUNTOS = 4
    #va al paso de la tropa: carga el bonete y el saco de granadas
    VELOCIDAD = 1
    #va con el mosquete y las granadas: nada de sable
    PELEA_CON_SABLE = False
    #sus sprites, como atributos y no como globales: el jefe es este mismo granadero con los
    #dibujos al doble, y con las globales clavadas aqui aparecia y desaparecia de tamanio
    ANDAR_IZQ = Andar_izq_Gr
    ANDAR_DCH = Andar_dch_Gr
    LANZAR_IZQ = Lanzar_izq_Gr
    LANZAR_DCH = Lanzar_dch_Gr

    def __init__(self,x,y,xObjectiv,yObjectiv):
        enemigo.__init__(self,x,y,xObjectiv,yObjectiv)
        self.recargaGranada = RECARGA_GRANADA
        #empieza recargando y con desfase propio, como los tiradores
        self.instanteUltimoLanzamiento = (pygame.time.get_ticks()
                                          + random.randint(0, DESFASE_MAXIMO_DESCARGA))
        #armado: esta con el brazo atras y la granada sale al terminar
        self.armando = False
        self.instanteInicioArmado = 0

    # # A que distancia esta de su objetivo

    def distanciaA(self, punto):
        return ((punto[0] - self.rect.centerx) ** 2 + (punto[1] - self.rect.centery) ** 2) ** 0.5

    def aTiro(self, punto):
        return self.distanciaA(punto) <= DISTANCIA_DE_LANZAMIENTO

    def puedeLanzar(self, ahora):
        return ahora - self.instanteUltimoLanzamiento >= self.recargaGranada

    def mostrandoArmado(self, ahora):
        return self.armando

    def mostrandoSuelta(self, ahora):
        return (not self.armando
                and ahora - self.instanteUltimoLanzamiento < DURACION_SUELTA)

    def lanzar(self, granadasEnElAire, puntoObjetivo):
        """Se llama cada frame: arranca el armado cuando toca, y suelta la granada al acabarlo.

        La granada apunta a donde esta el jugador EN EL MOMENTO DE SOLTARLA, no al empezar el
        armado: asi la marca del suelo aparece con el vuelo entero por delante para esquivarla.
        """
        ahora = pygame.time.get_ticks()
        if self.armando:
            if ahora - self.instanteInicioArmado >= DURACION_ARMADO:
                granadasEnElAire.append(granadas.Granada(self.rect.centerx, self.rect.centery,
                                                         puntoObjetivo[0], puntoObjetivo[1], ahora))
                self.armando = False
                self.instanteUltimoLanzamiento = ahora
            return
        #OJO: el alcance se mide contra el MISMO punto con el que pathFinding busca el anillo,
        #que es la esquina del cuerpo del jugador, y no contra puntoObjetivo, que es su centro.
        #Midiendo cada cosa con un punto distinto (se llevan 20 px), el granadero que llegaba
        #por la izquierda o por arriba se plantaba justo en el borde del anillo, a 190 de la
        #esquina pero a 199 del centro, y ya no lanzaba nunca: quieto y sin tirar nada.
        #La granada si se apunta al centro del cuerpo, que es lo que hay que acertar, y eso da
        #igual para el alcance porque el vuelo dura lo mismo caiga donde caiga.
        if self.aTiro((self.xObjectiv, self.yObjectiv)) and self.puedeLanzar(ahora):
            self.armando = True
            self.instanteInicioArmado = ahora

    def pathFinding(self,xObjectiv,yObjectiv):
        self.xObjectiv=xObjectiv
        self.yObjectiv=yObjectiv
        #mira al jugador siempre, tambien plantado
        self.izq = xObjectiv < self.x
        self.dch = not self.izq
        if self.armando:
            #mientras arma el brazo no se mueve
            self.stop = True
            self.actualizarRect()
            return
        #busca el anillo: no necesita ponerse a tu altura, porque una granada cae de arriba
        distancia = self.distanciaA((xObjectiv, yObjectiv))
        moviendose = False
        fueraDelCampo = self.x < 0 or self.x > WINX - self.ANCHO_REFERENCIA
        #se pregunta con aTiro, el mismo predicado que decide si lanza: asi el sitio donde se
        #para y el sitio desde donde lanza no pueden volver a separarse
        if fueraDelCampo or not self.aTiro((xObjectiv, yObjectiv)):
            paso = 1
        elif distancia < DISTANCIA_MINIMA_GRANADERO:
            #demasiado cerca: se retira, o su propia granada le pillaria dentro
            paso = -1
        else:
            paso = 0
        if paso:
            if xObjectiv < self.x:
                self.x -= paso * self.vel
            elif xObjectiv > self.x:
                self.x += paso * self.vel
            if yObjectiv < self.y:
                self.y -= paso * self.vel
            elif yObjectiv > self.y:
                self.y += paso * self.vel
            #no se retira fuera de la pantalla
            self.x = min(max(0, self.x), WINX - self.ANCHO_REFERENCIA)
            self.y = min(max(0, self.y), WINY - self.ALTO_REFERENCIA)
            moviendose = True
        self.stop = not moviendose
        self.actualizarRect()

    def sprite(self):
        ahora = pygame.time.get_ticks()
        if self.mostrandoArmado(ahora):
            return self.LANZAR_IZQ[0] if self.izq else self.LANZAR_DCH[0]
        if self.mostrandoSuelta(ahora):
            return self.LANZAR_IZQ[1] if self.izq else self.LANZAR_DCH[1]
        secuencia = self.ANDAR_IZQ if self.izq else self.ANDAR_DCH
        if not self.stop:
            imagen = secuencia[self.contadorCaminar // 3]
            self.contadorCaminar = (self.contadorCaminar + 1) % 27
            return imagen
        return secuencia[0]

    def dibujarCadaver(self,win):
        dibujar_anclado(win, cadaverEscalado(cadaverGranaderoImg, self.ESCALA_CADAVER),
                        self.x, self.y, self.izq, self.ANCHO_REFERENCIA, self.ALTO_REFERENCIA)


##El jefe granadero: el granadero al doble, y su granada es una lluvia
class jefeGranadero(granadero):
    #el doble de todo: el sprite mide 40x72 y la caja del cuerpo tambien
    ANCHO_REFERENCIA = 40
    ALTO_REFERENCIA = 72
    CUERPO_IZQ = pygame.Rect(0, 0, 40, 72)
    CUERPO_DCH = pygame.Rect(0, 0, 40, 72)
    VIDA_INICIAL = VIDA_JEFE_GRANADERO
    #un jefe suelta objeto seguro: es el premio de haberlo tumbado
    PROBABILIDAD_SUELTA = 1.0
    #vale como una oleada entera. Los jefes salen cuando ya se es Coronel, asi que esto es mas
    #para el marcador que para el rango
    PUNTOS = 25
    ANDAR_IZQ = Andar_izq_JGr
    ANDAR_DCH = Andar_dch_JGr
    #no tiene fotogramas de lanzar al doble, asi que arma y suelta con el mismo plantado. Antes
    #esto heredaba los del granadero normal y el jefe se encogia a la mitad al lanzar
    LANZAR_IZQ = (Andar_izq_JGr[0], Andar_izq_JGr[0])
    LANZAR_DCH = (Andar_dch_JGr[0], Andar_dch_JGr[0])
    #es un jefe: se sabe que lo es
    ES_JEFE = True
    #el cadaver de su tropa al doble, o moriria encogiendose a la mitad
    ESCALA_CADAVER = 2
    #donde cambia de ataque, en fracciones de vida. Lo lee el modo de pruebas para poder
    #saltar de fase sin pelear la pelea entera
    UMBRALES_DE_FASE = (VIDA_PARA_LOS_ANILLOS, VIDA_PARA_LAS_COLUMNAS)

    def __init__(self, x, y, xObjectiv, yObjectiv):
        granadero.__init__(self, x, y, xObjectiv, yObjectiv)
        self.recargaGranada = RECARGA_DE_LA_RAFAGA
        #los sitios donde va a caer la rafaga en curso, y cuando solto la ultima
        self.rafagaPendiente = []
        self.instanteDeLaUltimaDeLaRafaga = 0
        #no hace falta llevar cuenta de rondas: cada rafaga trae el patron completo de su fase

    # # Las tres fases: la vida decide que ataque toca

    def faseDelAtaque(self):
        queda = self.vida / float(self.vidaMaxima)
        if queda > VIDA_PARA_LOS_ANILLOS:
            return ATAQUE_LLUVIA
        if queda > VIDA_PARA_LAS_COLUMNAS:
            return ATAQUE_ANILLOS
        return ATAQUE_COLUMNAS

    def _dentroDelCampo(self, x, y):
        return (min(max(0, int(x)), WINX), min(max(0, int(y)), WINY))

    def _cabeEnElCampo(self, x, y):
        return 0 <= x <= WINX and 0 <= y <= WINY

    def _destinosDeLaLluvia(self, puntoObjetivo):
        """Fase 1: la primera justo encima del jugador y las demas desperdigadas."""
        destinos = [(self._dentroDelCampo(puntoObjetivo[0], puntoObjetivo[1]),
                     INTERVALO_DE_LA_RAFAGA)]
        for _ in range(GRANADAS_DE_LA_LLUVIA - 1):
            destinos.append((self._dentroDelCampo(
                puntoObjetivo[0] + random.randint(-DISPERSION_DE_LA_LLUVIA,
                                                  DISPERSION_DE_LA_LLUVIA),
                puntoObjetivo[1] + random.randint(-DISPERSION_DE_LA_LLUVIA,
                                                  DISPERSION_DE_LA_LLUVIA)),
                INTERVALO_DE_LA_RAFAGA))
        return destinos

    def _destinosDeLaOnda(self, puntoObjetivo):
        """Fase 2: anillos concentricos alrededor del JUGADOR, cada uno rozando al de dentro."""
        destinos = []
        for anillo in range(ANILLOS_DE_LA_ONDA):
            radio = RADIO_DEL_PRIMER_ANILLO + 2 * granadas.RADIO * anillo
            #cada anillo arranca en un angulo distinto, para que la onda no salga cuadriculada
            giro = random.uniform(0, 2 * math.pi)
            #la pausa la paga la primera del anillo que SOBREVIVE, no la de indice cero: si esa
            #cae fuera del campo y se salta, el anillo se quedaba sin su pausa y se pegaba al
            #anterior
            faltaLaPausa = True
            for indice in range(GRANADAS_POR_ANILLO):
                angulo = giro + 2 * math.pi * indice / GRANADAS_POR_ANILLO
                x = puntoObjetivo[0] + math.cos(angulo) * radio
                y = puntoObjetivo[1] + math.sin(angulo) * radio
                #las que caerian fuera del campo se saltan en vez de recortarse al borde:
                #recortandolas, los anillos grandes amontonaban granadas en los bordes y dejaban
                #de parecer circulos
                if not self._cabeEnElCampo(x, y):
                    continue
                espera = PAUSA_ENTRE_ANILLOS if faltaLaPausa else INTERVALO_DENTRO_DEL_ANILLO
                faltaLaPausa = False
                destinos.append((self._dentroDelCampo(x, y), espera))
        return destinos

    def _destinosDelBarrido(self):
        """Fase 3: el mapa entero cubierto por columnas, de los bordes al centro, en un ataque."""
        destinos = []
        par = 0
        while True:
            izquierda = MARGEN_DE_LA_COLUMNA + PASO_DE_LA_COLUMNA * par
            derecha = WINX - MARGEN_DE_LA_COLUMNA - PASO_DE_LA_COLUMNA * par
            if izquierda > derecha:
                break
            #cada par entra desplazado medio hueco: asi los pasillos se mueven y no vale aparcar
            desfase = (SEPARACION_EN_LA_COLUMNA // 2) * (par % 2)
            alturas = list(range(SEPARACION_EN_LA_COLUMNA // 2 + desfase, WINY,
                                 SEPARACION_EN_LA_COLUMNA))
            #las dos columnas del par, intercaladas, para que se vean venir las dos a la vez
            faltaLaPausa = True
            for altura in alturas:
                for columna in (izquierda, derecha):
                    if columna == derecha and izquierda == derecha:
                        #al juntarse en el centro es una sola columna, no dos encima
                        continue
                    espera = (PAUSA_ENTRE_COLUMNAS if faltaLaPausa
                              else INTERVALO_DENTRO_DE_LA_COLUMNA)
                    faltaLaPausa = False
                    destinos.append((self._dentroDelCampo(columna, altura), espera))
            par += 1
        return destinos

    def _destinosDeLaRafaga(self, puntoObjetivo):
        """Donde va a caer la rafaga que empieza ahora, segun la fase."""
        fase = self.faseDelAtaque()
        if fase == ATAQUE_LLUVIA:
            return self._destinosDeLaLluvia(puntoObjetivo)
        if fase == ATAQUE_ANILLOS:
            return self._destinosDeLaOnda(puntoObjetivo)
        return self._destinosDelBarrido()

    def lanzar(self, granadasEnElAire, puntoObjetivo):
        """Igual que el granadero, pero al acabar el armado suelta una RAFAGA entera.

        La rafaga se va soltando de una en una, y la recarga no empieza a contar hasta que cae la
        ultima: si contara desde la primera, las rafagas se solaparian.
        """
        ahora = pygame.time.get_ticks()
        if self.rafagaPendiente:
            #cada granada trae su propia espera: dentro de un anillo van seguidas y entre anillos
            #hay pausa, y asi la onda se lee como circulos y no como un goteo
            if ahora - self.instanteDeLaUltimaDeLaRafaga >= self.rafagaPendiente[0][1]:
                self._soltarUnaDeLaRafaga(granadasEnElAire, ahora)
            return
        if self.armando:
            if ahora - self.instanteInicioArmado >= DURACION_ARMADO:
                self.armando = False
                self.rafagaPendiente = self._destinosDeLaRafaga(puntoObjetivo)
                self._soltarUnaDeLaRafaga(granadasEnElAire, ahora)
            return
        if self.aTiro((self.xObjectiv, self.yObjectiv)) and self.puedeLanzar(ahora):
            self.armando = True
            self.instanteInicioArmado = ahora

    def _soltarUnaDeLaRafaga(self, granadasEnElAire, ahora):
        destino, _ = self.rafagaPendiente.pop(0)
        granadasEnElAire.append(granadas.Granada(self.rect.centerx, self.rect.centery,
                                                 destino[0], destino[1], ahora))
        self.instanteDeLaUltimaDeLaRafaga = ahora
        #la recarga empieza a contar desde la ultima que cae de la rafaga
        self.instanteUltimoLanzamiento = ahora


##La embestida: se planta, marca en el suelo el pasillo por donde va a pasar, y sale disparado
#
# La usan el jefe de sable y el jefe fusilero, y es la MISMA maniobra con otros numeros. Vive aqui
# y no copiada en las dos clases porque es la pieza mas delicada de los jefes: el rumbo se decide al
# avisar y no al salir, se para al acertar, y deja una ventana de recuperacion. Tener eso dos veces
# es garantizar que un dia se arregle en una copia y no en la otra.
#
# Lo que cambia de un jefe a otro son los ocho numeros de abajo. Los valores por defecto son los del
# jefe de sable, que fue quien la estreno.
class embestida(object):
    RECARGA_CARGA = RECARGA_DE_LA_CARGA
    DISTANCIA_CARGA = DISTANCIA_MAXIMA_DE_CARGA
    AVISO_CARGA = AVISO_DE_LA_CARGA
    VELOCIDAD_CARGA = VELOCIDAD_DE_LA_CARGA
    DURACION_CARGA = DURACION_DE_LA_CARGA
    RECUPERACION_CARGA = RECUPERACION_DE_LA_CARGA
    DANIO_CARGA = DANIO_DE_LA_CARGA
    ANCHO_PASILLO_CARGA = ANCHO_DEL_PASILLO_DE_CARGA

    def arrancarEmbestida(self):
        """Los cuatro datos de la carga. Se llama desde el __init__ del jefe que la use."""
        self.avisandoCarga = False
        self.cargando = False
        self.instanteInicioCarga = 0
        self.instanteUltimaCarga = pygame.time.get_ticks()
        self.rumboDeLaCarga = (0.0, 0.0)
        self.hastaDondeCarga = (0, 0)

    def ocupadoEnOtroAtaque(self):
        """Si esta a medias de su OTRO ataque. Cada jefe sabe cual es el suyo."""
        return False

    def leTocaEmbestir(self):
        """Si ahora mismo le toca embestir. Por defecto siempre que la recarga lo permita."""
        return True

    def puedeCargar(self, ahora):
        return (not self.cargando and not self.avisandoCarga and not self.ocupadoEnOtroAtaque()
                and self.leTocaEmbestir()
                and ahora - self.instanteUltimaCarga >= self.RECARGA_CARGA)

    def _apuntarLaCarga(self, objetivo):
        """Guarda el rumbo y hasta donde llega. Se decide AL AVISAR, no al salir: por eso la
        carga se esquiva apartandose, y no corriendo mas que ella."""
        centro = self.rect.center
        hacia = (objetivo.rect.centerx - centro[0], objetivo.rect.centery - centro[1])
        largo = (hacia[0] ** 2 + hacia[1] ** 2) ** 0.5 or 1.0
        self.rumboDeLaCarga = (hacia[0] / largo, hacia[1] / largo)
        alcance = self.VELOCIDAD_CARGA * (self.DURACION_CARGA / (1000.0 / 30))
        self.hastaDondeCarga = (centro[0] + self.rumboDeLaCarga[0] * alcance,
                                centro[1] + self.rumboDeLaCarga[1] * alcance)

    def cargar(self, objetivo):
        """Se llama cada frame. Lleva el aviso, la embestida y la recuperacion."""
        ahora = pygame.time.get_ticks()
        if self.avisandoCarga:
            if ahora - self.instanteInicioCarga >= self.AVISO_CARGA:
                self.avisandoCarga = False
                self.cargando = True
                self.instanteInicioCarga = ahora
            return
        if self.cargando:
            if ahora - self.instanteInicioCarga >= self.DURACION_CARGA:
                self._acabarLaCarga(ahora)
                return
            self.x += self.rumboDeLaCarga[0] * self.VELOCIDAD_CARGA
            self.y += self.rumboDeLaCarga[1] * self.VELOCIDAD_CARGA
            self.x = min(max(0, self.x), WINX - self.ANCHO_REFERENCIA)
            self.y = min(max(0, self.y), WINY - self.ALTO_REFERENCIA)
            self.actualizarRect()
            if self.rect.colliderect(objetivo.rect) and not objetivo.tieneInmunidad(ahora):
                objetivo.recibirImpacto(self.DANIO_CARGA, 0)
                #al acertar se para: embestir y seguir empujando seria imparable
                self._acabarLaCarga(ahora)
            return
        distancia = _distanciaAlCuadrado(self.rect.center, objetivo.rect.center) ** 0.5
        if self.puedeCargar(ahora) and distancia <= self.DISTANCIA_CARGA:
            self.avisandoCarga = True
            self.instanteInicioCarga = ahora
            self._apuntarLaCarga(objetivo)

    def _acabarLaCarga(self, ahora):
        #la recuperacion se cobra sobre la recarga: al acabar la embestida se queda un momento
        #plantado, y ese momento es la ventana para castigarle
        self.cargando = False
        self.instanteUltimaCarga = ahora + self.RECUPERACION_CARGA
        self.alAcabarLaEmbestida(ahora)

    def alAcabarLaEmbestida(self, ahora):
        """Gancho para el jefe que la use: al fusilero le toca volver a disparar."""
        pass

    def recuperandoDeLaCarga(self, ahora):
        return not self.cargando and ahora < self.instanteUltimaCarga

    def embistiendo(self, ahora):
        """Si la carga manda sobre los pies: avisando, embistiendo o recuperandose."""
        return self.avisandoCarga or self.cargando or self.recuperandoDeLaCarga(ahora)

    def pasosDeLaCarga(self, xObjectiv, yObjectiv):
        """Mueve (o planta) al jefe mientras la carga manda. Devuelve si se ha ocupado del frame."""
        if not self.embistiendo(pygame.time.get_ticks()):
            return False
        self.xObjectiv = xObjectiv
        self.yObjectiv = yObjectiv
        if not self.cargando:
            #plantado pero encarando, para que se vea a donde va a embestir
            self.izq = xObjectiv < self.x
            self.dch = not self.izq
        self.stop = not self.cargando
        self.actualizarRect()
        return True

    def dibujarAvisoDeLaCarga(self, win):
        """El pasillo por donde va a pasar la carga, parpadeando en el suelo."""
        if not self.avisandoCarga:
            return
        ahora = pygame.time.get_ticks()
        transcurrido = (ahora - self.instanteInicioCarga) / 1000.0
        avance = min(1.0, transcurrido * 1000.0 / self.AVISO_CARGA)
        if not granadas.parpadeoVisible(transcurrido, avance):
            return
        centro = self.rect.center
        largo = int(((self.hastaDondeCarga[0] - centro[0]) ** 2
                     + (self.hastaDondeCarga[1] - centro[1]) ** 2) ** 0.5)
        for paso in range(0, largo, 6):
            x = int(centro[0] + self.rumboDeLaCarga[0] * paso)
            y = int(centro[1] + self.rumboDeLaCarga[1] * paso)
            pygame.draw.rect(win, granadas.COLOR_MARCA,
                             pygame.Rect(x - self.ANCHO_PASILLO_CARGA // 2, y - 1,
                                         self.ANCHO_PASILLO_CARGA, 2))


##El jefe de sable: el oficial al doble. Taja en area y carga
class jefeSable(embestida, oficial):
    #el doble de todo: 60x64 de caja, y el cuerpo dentro sin contar el sable, que sobresale
    ANCHO_REFERENCIA = 60
    ALTO_REFERENCIA = 64
    CUERPO_IZQ = pygame.Rect(12, 4, 42, 60)
    CUERPO_DCH = pygame.Rect(6, 4, 42, 60)
    VIDA_INICIAL = VIDA_JEFE_SABLE
    PROBABILIDAD_SUELTA = 1.0
    PUNTOS = 25
    ANDAR_IZQ = Andar_izq_JSa
    ANDAR_DCH = Andar_dch_JSa
    ALZAR_IZQ = Alzar_izq_JSa
    ALZAR_DCH = Alzar_dch_JSa
    TAJAR_IZQ = Tajar_izq_JSa
    TAJAR_DCH = Tajar_dch_JSa
    ES_JEFE = True
    #el cadaver de su tropa al doble, o moriria encogiendose a la mitad
    ESCALA_CADAVER = 2
    #no cambia de ataque por vida: sus dos ataques van a la vez, cada uno con su reloj
    UMBRALES_DE_FASE = ()

    def __init__(self, x, y, xObjectiv, yObjectiv):
        oficial.__init__(self, x, y, xObjectiv, yObjectiv)
        self.arrancarEmbestida()

    # # El tajo en area: como el de la tropa, pero barre un circulo y no necesita tocar

    def alcanceDelSable(self):
        """Su alcance es un circulo a su alrededor, no su cuerpo estirado unos pixeles."""
        centro = self.rect.center
        return pygame.Rect(centro[0] - RADIO_DEL_TAJO_DEL_JEFE,
                           centro[1] - RADIO_DEL_TAJO_DEL_JEFE,
                           2 * RADIO_DEL_TAJO_DEL_JEFE, 2 * RADIO_DEL_TAJO_DEL_JEFE)

    def _dentroDelTajo(self, objetivo):
        """Si la caja del objetivo entra en el circulo del tajo."""
        centro = self.rect.center
        cercano = (max(objetivo.rect.left, min(centro[0], objetivo.rect.right)),
                   max(objetivo.rect.top, min(centro[1], objetivo.rect.bottom)))
        return _distanciaAlCuadrado(centro, cercano) <= RADIO_DEL_TAJO_DEL_JEFE ** 2

    def atacar(self, objetivo, sablazosEnElAire):
        """El tajo en area. Mismo compas que el de la tropa: alza, avisa, y barre.

        Mientras carga no taja: un ataque a la vez, o no habria forma de leerle.
        """
        if self.cargando or self.avisandoCarga:
            return
        ahora = pygame.time.get_ticks()
        if self.alzandoSable:
            if ahora - self.instanteInicioAlzado >= DURACION_ALZADO_DEL_JEFE:
                self.alzandoSable = False
                self.instanteUltimoTajo = ahora
                #el rastro es un circulo entero y del MISMO radio que el golpe: asi se aprende
                #su alcance mirandolo, no muriendose
                sablazosEnElAire.append(sablazos.Barrido(self.rect.centerx, self.rect.centery,
                                                         RADIO_DEL_TAJO_DEL_JEFE, ahora))
                sonidos.sonido_sable.play()
                if self._dentroDelTajo(objetivo) and not objetivo.tieneInmunidad(ahora):
                    objetivo.recibirImpacto(DANIO_DEL_TAJO_DEL_JEFE, 0)
            return
        if (self._dentroDelTajo(objetivo)
                and ahora - self.instanteUltimoTajo >= RECARGA_DEL_TAJO_DEL_JEFE):
            self.alzandoSable = True
            self.instanteInicioAlzado = ahora

    # # La carga la trae el mixin embestida. Lo unico suyo es que no embiste tajando

    def ocupadoEnOtroAtaque(self):
        return self.alzandoSable

    def girando(self, ahora):
        """Si esta en mitad del giro con el que suelta el tajo."""
        return not self.alzandoSable and ahora - self.instanteUltimoTajo < DURACION_DEL_GIRO

    def sprite(self):
        """Mientras gira, alterna el lado al que mira: eso es girar sobre los pies en pixel art."""
        ahora = pygame.time.get_ticks()
        if self.girando(ahora):
            medioGiros = (ahora - self.instanteUltimoTajo) // MS_POR_MEDIA_VUELTA
            deEspaldas = medioGiros % 2 == 1
            mirando = self.izq if not deEspaldas else not self.izq
            return self.TAJAR_IZQ if mirando else self.TAJAR_DCH
        return oficial.sprite(self)

    def pathFinding(self, xObjectiv, yObjectiv):
        #mientras avisa, carga o se recupera, la carga manda sobre los pies
        if self.pasosDeLaCarga(xObjectiv, yObjectiv):
            return
        oficial.pathFinding(self, xObjectiv, yObjectiv)

    def dibujarMando(self, win):
        """El anillo de mando del oficial, y encima los avisos de sus dos ataques."""
        oficial.dibujarMando(self, win)
        ahora = pygame.time.get_ticks()
        if self.alzandoSable:
            transcurrido = (ahora - self.instanteInicioAlzado) / 1000.0
            avance = min(1.0, transcurrido * 1000.0 / DURACION_ALZADO_DEL_JEFE)
            if granadas.parpadeoVisible(transcurrido, avance):
                granadas.dibujarAviso(win, self.rect.center, RADIO_DEL_TAJO_DEL_JEFE)
        self.dibujarAvisoDeLaCarga(win)


##El jefe fusilero: el soldado de linea al doble. En vez de un tiro, descargas de plomo
class jefeFusilero(embestida, enemigoDistancia):
    #el doble de todo: la caja del cuerpo mide 40x72
    ANCHO_REFERENCIA = 40
    ALTO_REFERENCIA = 72
    CUERPO_IZQ = pygame.Rect(0, 0, 40, 72)
    CUERPO_DCH = pygame.Rect(0, 0, 40, 72)
    #la boca del mosquete tambien: en la tropa esta a 21 de los 36 de alto
    ALTURA_CANON = 42
    VIDA_INICIAL = VIDA_JEFE_FUSILERO
    PROBABILIDAD_SUELTA = 1.0
    PUNTOS = 25
    ANDAR_IZQ = Andar_izq_JFu
    ANDAR_DCH = Andar_dch_JFu
    DISPARAR_IZQ = Disparar_izq_JFu
    DISPARAR_DCH = Disparar_dch_JFu
    #se planta el solo en su distancia, sin repartirse puestos con nadie: es el unico de su linea
    PUESTOS = (PUESTO_DEL_JEFE_FUSILERO,)
    ES_JEFE = True
    #el cadaver de la tropa al doble, o el jefe moriria encogiendose a la mitad
    ESCALA_CADAVER = 2
    #donde cambia de ataque, en fracciones de vida. Lo lee el modo de pruebas para poder saltar
    #de fase sin pelear la pelea entera
    UMBRALES_DE_FASE = (VIDA_PARA_LA_CORTINA, VIDA_PARA_LA_PLAZA)
    #el unico de los cuatro que pelea sin guardias: su carga a la bayoneta ya hace el trabajo
    #que hacia la escolta, que era no dejarte quieto mirando al jefe
    LLAMA_ESCOLTA = False
    #su embestida: mas larga y mas rapida que la del jefe de sable, porque tiene que cruzar todo
    #su puesto de tiro para llegar. Y su reloj no es una recarga propia, es el turno: embiste
    #cuando le toca (ver leTocaEmbestir), asi que la recarga del mixin sobra
    RECARGA_CARGA = 0
    DISTANCIA_CARGA = DISTANCIA_DE_LA_CARGA_DEL_FUSILERO
    AVISO_CARGA = AVISO_DE_LA_CARGA_DEL_FUSILERO
    VELOCIDAD_CARGA = VELOCIDAD_DE_LA_CARGA_DEL_FUSILERO
    DURACION_CARGA = DURACION_DE_LA_CARGA_DEL_FUSILERO
    RECUPERACION_CARGA = RECUPERACION_DE_LA_CARGA_DEL_FUSILERO
    DANIO_CARGA = DANIO_DE_LA_CARGA_DEL_FUSILERO

    def __init__(self, x, y, xObjectiv, yObjectiv, enemigosVivos=None):
        enemigoDistancia.__init__(self, x, y, xObjectiv, yObjectiv, enemigosVivos)
        self.recarga = RECARGA_DE_LA_DESCARGA
        #los grupos de balas que le quedan por soltar de la descarga en curso, y sus relojes
        self.descargaPendiente = []
        self.esperaDeLaDescarga = 0
        self.instanteDeLaUltimaDeLaDescarga = 0
        #y si esta apuntando, con lo que arranca cada descarga
        self.apuntando = False
        self.instanteInicioPunteria = 0
        self.arrancarEmbestida()
        #de quien es el turno. Empieza disparando: entra por el borde y lo primero que hace es
        #plantarse a tiro, no salir corriendo a por el jugador
        self.leTocaCargar = False

    # # Las tres fases: la vida decide que descarga toca

    def faseDelAtaque(self):
        queda = self.vida / float(self.vidaMaxima)
        if queda > VIDA_PARA_LA_CORTINA:
            return ATAQUE_ABANICO
        if queda > VIDA_PARA_LA_PLAZA:
            return ATAQUE_CORTINA
        return ATAQUE_PLAZA

    def distanciaAlObjetivo(self):
        """Los pixeles que hay de su boca del mosquete al jugador."""
        origenX, origenY = self.origenDelPlomo()
        return ((self.xObjectiv - origenX) ** 2 + (self.yObjectiv - origenY) ** 2) ** 0.5

    def anguloAlObjetivo(self):
        """El angulo, en radianes, desde su boca del mosquete hasta el jugador."""
        origenX, origenY = self.origenDelPlomo()
        return math.atan2(self.yObjectiv - origenY, self.xObjectiv - origenX)

    def arcoDeHuecos(self, centro, balas):
        """Los angulos de un arco de 'balas' separadas SEPARACION_ENTRE_BALAS px entre si.

        La separacion va en PIXELES a la altura del jugador, no en grados: asi el hueco entre dos
        balas mide lo mismo este el jefe cerca o lejos, y la esquiva no depende de una distancia
        que el jefe no controla, porque quien decide donde ponerse es el jugador.
        """
        distancia = max(1.0, self.distanciaAlObjetivo())
        return [centro + math.atan2((indice - (balas - 1) / 2.0) * SEPARACION_ENTRE_BALAS,
                                    distancia)
                for indice in range(balas)]

    def _abanico(self, centro):
        """Los abanicos de la descarga, todos con los MISMOS angulos y centrados en 'centro'."""
        arco = self.arcoDeHuecos(centro, BALAS_DEL_ABANICO)
        return [(list(arco), PAUSA_ENTRE_ABANICOS) for _ in range(ABANICOS_POR_DESCARGA)]

    def _cortina(self, centro):
        """El mismo arco, pero soltado bala a bala mientras gira: un limpiaparabrisas.

        Gira siempre en el mismo sentido dentro de una descarga, porque un barrido que cambiara
        de sentido a media pasada no se podria leer. El sentido lo decide de que lado esta el
        jugador, para que la cortina le barra encima y no se le vaya por detras.
        """
        ida = self.arcoDeHuecos(centro, BALAS_DE_LA_CORTINA)
        #el barrido empieza por el lado en el que esta el jugador, para que le pase por encima
        #cuanto antes: empezando por el otro lado, la mitad de la cortina se gasta en el vacio
        if self.yObjectiv < self.rect.centery:
            ida.reverse()
        pasadas = []
        for numero in range(PASADAS_DE_LA_CORTINA):
            #la vuelta son los mismos angulos al reves: los huecos siguen donde estaban
            pasadas.extend(ida if numero % 2 == 0 else list(reversed(ida)))
        return [([angulo], INTERVALO_DE_LA_CORTINA) for angulo in pasadas]

    def _plaza(self, centro):
        """Anillos completos, cada uno girado medio paso respecto al anterior.

        El giro es la clave: el hueco por el que se colo un anillo no esta donde estaba cuando
        llega el siguiente, asi que no vale quedarse quieto en el hueco, hay que ir con el.
        """
        paso = 2 * math.pi / BALAS_DEL_ANILLO
        anillos = []
        for numero in range(ANILLOS_DE_LA_PLAZA):
            arranque = centro + paso * GIRO_POR_ANILLO * numero
            anillos.append(([arranque + paso * indice for indice in range(BALAS_DEL_ANILLO)],
                            PAUSA_ENTRE_ANILLOS_DE_PLOMO))
        return anillos

    def descargaDeLaFase(self):
        """Los grupos de balas de la descarga que toca: [(angulos, espera), ...]."""
        centro = self.anguloAlObjetivo()
        fase = self.faseDelAtaque()
        if fase == ATAQUE_ABANICO:
            return self._abanico(centro)
        if fase == ATAQUE_CORTINA:
            return self._cortina(centro)
        return self._plaza(centro)

    # # El disparo

    def origenDelPlomo(self):
        """De donde sale el plomo.

        El abanico y la cortina salen de la boca del mosquete, que es de donde tienen que salir.
        El fuego de plaza sale del PECHO: un anillo que rodea al jefe saliendo de la punta del
        canio se ve descentrado, y encima las balas de atras naceriran cruzandole el cuerpo.
        """
        if self.faseDelAtaque() == ATAQUE_PLAZA:
            return self.rect.center
        return (self.xCanon(), self.y + self.ALTURA_CANON)

    def disparar(self, bullets):
        """Se llama cada frame: apunta, y luego suelta la descarga de su fase grupo a grupo.

        No exige estar encarado, al contrario que la tropa. Un tirador de a pie solo sabe disparar
        en horizontal, asi que tiene que alinearse primero; este apunta en cualquier direccion, y
        si tuviera que alinearse bastaria con no ponerse nunca a su altura para desarmarlo.
        """
        ahora = pygame.time.get_ticks()
        #avisando, embistiendo o recuperandose no dispara: un ataque a la vez, o no hay forma
        #de leerle. Es la misma regla que la del jefe de sable con su tajo
        if self.embistiendo(ahora):
            return
        if self.descargaPendiente:
            if ahora - self.instanteDeLaUltimaDeLaDescarga >= self.esperaDeLaDescarga:
                self._soltarGrupo(bullets, ahora)
            return
        if self.apuntando:
            if ahora - self.instanteInicioPunteria < DURACION_DE_LA_PUNTERIA:
                return
            #los angulos se fijan AL SOLTAR, no al empezar a apuntar: fijandolos antes bastaria
            #con salirse del arco durante el aviso y la descarga entera caia al aire, que con
            #plomo lento seria esquivarla gratis. El aviso dice "va a disparar, y por ahi"
            self.apuntando = False
            self.descargaPendiente = self.descargaDeLaFase()
            self.esperaDeLaDescarga = 0
            self._soltarGrupo(bullets, ahora)
            return
        if self.leTocaCargar and self.distanciaAlObjetivo() <= self.DISTANCIA_CARGA:
            #le toca embestir: espera su turno en vez de disparar. Si el jugador esta MAS LEJOS de
            #lo que alcanza la embestida, dispara igual y se guarda el turno: si no, quedandose
            #en el fondo del mapa se le desactivaba el jefe entero
            return
        if self.puedeDisparar(ahora):
            self.apuntando = True
            self.instanteInicioPunteria = ahora

    # # La embestida a la bayoneta la trae el mixin embestida. Aqui van sus dos ganchos

    def ocupadoEnOtroAtaque(self):
        return self.apuntando or bool(self.descargaPendiente)

    def leTocaEmbestir(self):
        """Embiste por turnos con la descarga, y no de seguido: primero una, luego la otra.

        El rato de ESPERA_HASTA_LA_CARGA es para que se distingan: soltando el aviso de la carga
        pegado al ultimo tiro, las dos cosas se leen como un solo manotazo.
        """
        return (self.leTocaCargar
                and pygame.time.get_ticks() - self.instanteUltimoDisparo >= ESPERA_HASTA_LA_CARGA)

    def alAcabarLaEmbestida(self, ahora):
        #le vuelve a tocar disparar, y la recarga de la descarga cuenta desde aqui: asi la calma
        #de despues de la embestida es la misma que la de despues de una descarga
        self.leTocaCargar = False
        self.instanteUltimoDisparo = ahora

    def sprite(self):
        """Avisando y embistiendo lleva el mosquete por delante: es una carga A LA BAYONETA.

        El fotograma de disparar es justo esa pose. Con el de andar el mosquete va al hombro, en
        vertical, y la embestida se leia como un paseo.
        """
        if self.avisandoCarga or self.cargando:
            secuencia = self.DISPARAR_IZQ if self.izq else self.DISPARAR_DCH
            return secuencia[0]
        return enemigoDistancia.sprite(self)

    def pathFinding(self, xObjectiv, yObjectiv):
        #la embestida manda sobre los pies antes que nada
        if self.pasosDeLaCarga(xObjectiv, yObjectiv):
            return
        #y mientras apunta o suelta la descarga no se mueve: el paraguas se dispara a pie firme,
        #y de paso eso le convierte en blanco quieto, que es la ventana para castigarle
        if self.apuntando or self.descargaPendiente:
            self.xObjectiv = xObjectiv
            self.yObjectiv = yObjectiv
            self.izq = xObjectiv < self.x
            self.dch = not self.izq
            self.stop = True
            self.actualizarRect()
            return
        enemigoDistancia.pathFinding(self, xObjectiv, yObjectiv)

    def angulosDelAviso(self):
        """Los angulos que se le marcan en el suelo mientras apunta: la forma de lo que viene.

        No son exactamente los de la descarga (esos se fijan al soltar): son el arco de su fase
        tal como esta ahora mismo. El aviso ensenia la FORMA, no el sitio.
        """
        centro = self.anguloAlObjetivo()
        fase = self.faseDelAtaque()
        if fase == ATAQUE_ABANICO:
            return self.arcoDeHuecos(centro, BALAS_DEL_ABANICO)
        if fase == ATAQUE_CORTINA:
            return self.arcoDeHuecos(centro, BALAS_DE_LA_CORTINA)
        paso = 2 * math.pi / BALAS_DEL_ANILLO
        return [centro + paso * indice for indice in range(BALAS_DEL_ANILLO)]

    def dibujarMando(self, win):
        """Los avisos de sus dos ataques. Se dibujan debajo de todos, como el anillo del oficial."""
        self.dibujarAvisoDeLaCarga(win)
        if not self.apuntando:
            return
        ahora = pygame.time.get_ticks()
        transcurrido = (ahora - self.instanteInicioPunteria) / 1000.0
        avance = min(1.0, transcurrido * 1000.0 / DURACION_DE_LA_PUNTERIA)
        if not granadas.parpadeoVisible(transcurrido, avance):
            return
        origenX, origenY = self.origenDelPlomo()
        for angulo in self.angulosDelAviso():
            for paso in range(0, LARGO_DEL_AVISO_DEL_PLOMO, PASO_DEL_AVISO_DEL_PLOMO):
                x = int(origenX + math.cos(angulo) * paso)
                y = int(origenY + math.sin(angulo) * paso)
                pygame.draw.rect(win, granadas.COLOR_MARCA, pygame.Rect(x - 1, y - 1, 2, 2))

    def _soltarGrupo(self, bullets, ahora):
        angulos, espera = self.descargaPendiente.pop(0)
        origenX, origenY = self.origenDelPlomo()
        for angulo in angulos:
            #el 'lado' de la bala es solo para saber hacia donde mira quien disparo; el rumbo de
            #verdad va en el vector de avance, que es lo que permite tirar en diagonal
            bullets.append(proyectil(origenX, origenY, -1 if self.izq else 1,
                                     DANIO_DE_LA_PERDIGONADA,
                                     math.cos(angulo) * VELOCIDAD_DEL_PLOMO_DEL_JEFE,
                                     math.sin(angulo) * VELOCIDAD_DEL_PLOMO_DEL_JEFE))
        self.esperaDeLaDescarga = espera
        self.instanteDeLaUltimaDeLaDescarga = ahora
        if not self.descargaPendiente:
            #acabada la descarga, le toca embestir
            self.leTocaCargar = True
        #el mismo sello para la recarga y para el fogonazo: la recarga cuenta desde el ULTIMO
        #grupo de la descarga, que es cuando de verdad acaba de disparar
        self.instanteUltimoDisparo = ahora
        self.haDisparado = True
        #una sola vez por grupo y no una por bala: dieciseis mosquetes a la vez saturan
        sound_musket.play()
