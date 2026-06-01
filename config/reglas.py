from core.limpieza import normalizar_partido, componentes_partido


PARTIDOS_CLAVE = {
    "PAN",
    "PRI",
    "PRD",
    "PVEM",
    "MORENA",
    "MC",
}


PARTIDOS_OTROS = {
    "PT",
    "QS",
    "QI",
    "CQ",
    "PES",
    "RSP",
    "FXM",
    "PQS",
}


VALORES_SIN_DATO = {
    "",
    "NAN",
    "NONE",
    "#DIV/0!",
    "#DIV_0!",
    "SIN_DATO",
    "SIN_DATOS",
}


COLUMNAS_NO_VOTOS = {
    "#",
    "ENTIDAD",
    "ELECCION",
    "ANO",
    "ANIO",
    "SECCION",
    "SECCION_ELECTORAL",
    "LISTA_NOMINAL",
    "VOTOS_EMITIDOS",
    "VOTOS_EMITIDOS_1",
    "TOT_VOTOS",
    "VOTOS_NULOS",
    "NULOS",
    "PARTICIPACION_PCN",
    "ABSTENCION_PCN",
    "1ER_LUGAR",
    "1ERO_VOTOS",
    "PCN",
    "DIF_VOTOS_2DO",
    "DIF_PCN_2DO",
    "2DO_LUGAR",
    "2DO_VOTOS",
    "PCN_1",
    "DIF_VOTOS_3RO",
    "DIF_PCN_3RO",
    "3ER_LUGAR",
    "3ERO_VOTOS",
    "PCN_2",
    "MUNICIPIO",
    "MUNICIPIO_NORM",
    "DISTRITO_LOCAL",
    "DISTRITO_FEDERAL",
    "ID_MUNICIPIO",
    "CU_MUNICIPIO",
    "CVE_MUN",
    "NUM_MUN_OFICIAL",
    "NOM_MUN",
}


def es_valor_sin_dato(valor):
    valor_norm = normalizar_partido(valor)
    return valor_norm in VALORES_SIN_DATO


def es_partido_clave(partido_o_coalicion):
    partido_norm = normalizar_partido(partido_o_coalicion)

    if es_valor_sin_dato(partido_norm):
        return False

    partes = componentes_partido(partido_norm)

    return any(parte in PARTIDOS_CLAVE for parte in partes)


def es_partido_otro(partido_o_coalicion):
    partido_norm = normalizar_partido(partido_o_coalicion)

    if es_valor_sin_dato(partido_norm):
        return False

    partes = componentes_partido(partido_norm)

    return any(parte in PARTIDOS_OTROS for parte in partes)


def es_independiente(partido_o_coalicion):
    partido_norm = normalizar_partido(partido_o_coalicion)

    if es_valor_sin_dato(partido_norm):
        return False

    partes = componentes_partido(partido_norm)

    if "IND" in partes:
        return True

    if es_partido_clave(partido_norm):
        return False

    if es_partido_otro(partido_norm):
        return False

    return True


def clasificar_fuerza_politica(partido_o_coalicion):
    partido_norm = normalizar_partido(partido_o_coalicion)

    if es_valor_sin_dato(partido_norm):
        return "SIN DATO"

    if es_partido_clave(partido_norm):
        return "PARTIDO / COALICION"

    if es_partido_otro(partido_norm):
        return "OTROS"

    if es_independiente(partido_norm):
        return "INDEPENDIENTE"

    return "SIN DATO"


def etiqueta_fuerza_politica(partido_o_coalicion):
    partido_norm = normalizar_partido(partido_o_coalicion)

    clasificacion = clasificar_fuerza_politica(partido_norm)

    if clasificacion == "OTROS":
        return "OTROS"

    if clasificacion == "INDEPENDIENTE":
        return "INDEPENDIENTE"

    if clasificacion == "SIN DATO":
        return "SIN DATO"

    return partido_norm


def columna_es_voto_valida(columna):
    col_norm = normalizar_partido(columna)

    if es_valor_sin_dato(col_norm):
        return False

    if col_norm in COLUMNAS_NO_VOTOS:
        return False

    if col_norm in {"CNR", "NULOS", "VOTOS_NULOS", "OTROS"}:
        return False

    if col_norm.startswith("PCN"):
        return False

    if col_norm.startswith("DIF"):
        return False

    if col_norm.startswith("VOTACION_PCN"):
        return False

    return True