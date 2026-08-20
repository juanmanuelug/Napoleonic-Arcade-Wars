# ################################ Resolucion de colisiones ###########################################
# Todo el reparto de danio de las balas pasa por aqui, en una sola pasada por frame:
#   - cada bala se mueve, impacta como maximo UNA vez y contra UN solo objetivo, y desaparece
#   - las listas no se modifican mientras se recorren: se devuelve una lista nueva
# El objetivo solo necesita tener un .rect y un metodo recibirImpacto(danio)


def resolverBalas(balas, objetivos, ancho_pantalla, alto_pantalla):
    """Mueve las balas, aplica el danio de los impactos y devuelve las que siguen volando."""
    siguen_volando = []
    for bala in balas:
        bala.mover()
        if not bala.en_pantalla(ancho_pantalla, alto_pantalla):
            continue
        impactado = None
        for objetivo in objetivos:
            if bala.rect.colliderect(objetivo.rect):
                impactado = objetivo
                break
        if impactado is None:
            siguen_volando.append(bala)
        else:
            #se pasa el lado del disparo para que el impacto empuje en esa direccion
            impactado.recibirImpacto(bala.danio, bala.lado)
    return siguen_volando


def separarCaidos(enemigos):
    """Devuelve (los que siguen vivos, los que acaban de caer) sin tocar la lista original."""
    vivos = [enemigo for enemigo in enemigos if enemigo.vivo]
    caidos = [enemigo for enemigo in enemigos if not enemigo.vivo]
    return vivos, caidos
