from pathlib import Path


CARPETA_RECURSOS = Path("recursos")


LOGO_DASHBOARD = CARPETA_RECURSOS / "logo.jpeg"


LOGOS_PARTIDOS_PRINCIPALES = {
    "PAN": "pan.png",
    "PRI": "pri.png",
    "PRD": "prd.png",
    "PVEM": "pvem.png",
    "MORENA": "morena.png",
    "MC": "mc.png",
    "PT": "pt.png",
}

CLAVES_INDEPENDIENTES = {
    "IND",
    "INDEPENDIENTE",
    "CANDIDATO_INDEPENDIENTE",
    "CANDIDATURA_INDEPENDIENTE",
}


def normalizar_clave_imagen(valor):
    """
    Normaliza una etiqueta de partido o coalición para buscar imagen.

    Ejemplos:
    PAN_PRI_PRD -> PAN_PRI_PRD
    PVEM-MORENA-PT -> PVEM_MORENA_PT
    independiente -> INDEPENDIENTE
    """

    valor = str(valor).strip().upper()
    valor = valor.replace("-", "_")
    valor = valor.replace("+", "_")
    valor = valor.replace(" ", "_")

    while "__" in valor:
        valor = valor.replace("__", "_")

    return valor


def obtener_logo_dashboard():
    """
    Devuelve la ruta del logo principal del dashboard.
    """

    if LOGO_DASHBOARD.exists():
        return str(LOGO_DASHBOARD)

    return None


def obtener_partido_principal(etiqueta):
    """
    Devuelve qué logo usar según la etiqueta.

    Regla:
    - Si contiene PAN, PRI, PRD, PVEM, MORENA o MC, usa ese logo.
    - Si es independiente, usa ind.png.
    - Todo lo demás usa otros.png.

    Para coaliciones se usa el primer partido principal detectado
    según el orden de aparición en la etiqueta.
    """

    etiqueta_norm = normalizar_clave_imagen(etiqueta)

    partes = [p for p in etiqueta_norm.split("_") if p]

    for parte in partes:
        if parte in LOGOS_PARTIDOS_PRINCIPALES:
            return parte

    if etiqueta_norm in CLAVES_INDEPENDIENTES:
        return "IND"

    for parte in partes:
        if parte in CLAVES_INDEPENDIENTES:
            return "IND"

    return "OTROS"


def obtener_logo_partido(etiqueta):
    """
    Devuelve la ruta del logo de un partido, coalición o candidatura.

    Principales:
    PAN, PRI, PRD, PVEM, MORENA, MC

    Independientes:
    ind.png

    Resto:
    otros.png
    """

    partido_principal = obtener_partido_principal(etiqueta)

    if partido_principal == "IND":
        ruta = CARPETA_RECURSOS / "ind.png"
    elif partido_principal == "OTROS":
        ruta = CARPETA_RECURSOS / "otros.png"
    else:
        ruta = CARPETA_RECURSOS / LOGOS_PARTIDOS_PRINCIPALES[partido_principal]

    if ruta.exists():
        return str(ruta)

    ruta_respaldo = CARPETA_RECURSOS / "otros.png"

    if ruta_respaldo.exists():
        return str(ruta_respaldo)

    return None