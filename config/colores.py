from core.limpieza import normalizar_partido


COLORES_BASE = {
    "PAN": "#005596",
    "PRI": "#00953B",
    "MORENA": "#B31934",
    "PRD": "#FFD700",
    "PVEM": "#00A650",
    "MC": "#FF8200",
    "PT": "#E03E2D",
    "QI": "#808080",
    "PES": "#6A1B9A",
    "RSP": "#E91E63",
    "FXM": "#E91E63",
    "QS": "#808080",
    "CNR": "#A0A0A0",
    "NULOS": "#999999",
    "VOTOS_NULOS": "#999999",
    "OTROS": "#D3D3D3",
}


PARTIDO_REPRESENTATIVO_COALICION = {
    # Coaliciones / candidaturas comunes con PAN
    "PAN_PRD": "PAN",
    "PAN_QI": "PAN",
    "PAN_QUI": "PAN",
    "PAN_PRD_MC": "PAN",
    "PAN_PRI_PRD": "PAN",
    "PAN_PRI": "PAN",

    # Coaliciones / candidaturas comunes con PRI
    "PRI_PVEM": "PRI",
    "PRI_PRD": "PRI",

    # Coaliciones / candidaturas comunes con MORENA
    "MORENA_PT": "MORENA",
    "MORENA_PT_PES": "MORENA",
    "PVEM_MORENA_PT": "MORENA",
    "PVEM_MORENA": "MORENA",
}


PRIORIDAD_COLOR_COALICION = [
    "MORENA",
    "PAN",
    "PRI",
    "MC",
    "PVEM",
    "PT",
    "PRD",
    "PES",
    "QI",
    "QS",
    "RSP",
    "FXM",
]


def obtener_partido_representativo(partido_o_coalicion):
    """
    Devuelve el partido que se usará como color representativo.

    Ejemplo:
    PAN_PRD -> PAN
    MORENA_PT_PES -> MORENA
    PRI_PVEM -> PRI
    """

    partido_norm = normalizar_partido(partido_o_coalicion)

    if partido_norm in PARTIDO_REPRESENTATIVO_COALICION:
        return PARTIDO_REPRESENTATIVO_COALICION[partido_norm]

    partes = partido_norm.split("_")

    for partido in PRIORIDAD_COLOR_COALICION:
        if partido in partes:
            return partido

    return partido_norm


def obtener_color(partido_o_coalicion):
    """
    Devuelve el color del partido o coalición.
    Si es coalición, usa el partido más representativo.
    """

    partido_representativo = obtener_partido_representativo(partido_o_coalicion)

    return COLORES_BASE.get(partido_representativo, "#CFCFCF")