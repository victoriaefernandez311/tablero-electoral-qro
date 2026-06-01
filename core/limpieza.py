import unicodedata
import pandas as pd


def normalizar_columna(columna):
    columna = str(columna).strip().upper()
    columna = unicodedata.normalize("NFKD", columna)
    columna = columna.encode("ASCII", "ignore").decode("utf-8")
    columna = columna.replace(" ", "_")
    columna = columna.replace("\n", "_")
    columna = columna.replace("(", "")
    columna = columna.replace(")", "")
    columna = columna.replace("%", "PCN")
    columna = columna.replace(".", "_")
    columna = columna.replace("-", "_")
    columna = columna.replace("/", "_")

    while "__" in columna:
        columna = columna.replace("__", "_")

    return columna.strip("_")


def limpiar_numero(valor):
    if pd.isna(valor):
        return 0

    valor = str(valor).strip()
    valor = valor.replace(",", "")
    valor = valor.replace("%", "")
    valor = valor.replace(" ", "")

    try:
        return float(valor)
    except ValueError:
        return 0


def normalizar_partido(valor):
    valor = str(valor).strip().upper()

    valor = unicodedata.normalize("NFKD", valor)
    valor = valor.encode("ASCII", "ignore").decode("utf-8")

    valor = valor.replace("-", "_")
    valor = valor.replace(" ", "_")
    valor = valor.replace("/", "_")
    valor = valor.replace(".", "")

    # Correcciones de nombres/códigos frecuentes
    valor = valor.replace("QUI", "QI")
    valor = valor.replace("FM", "FXM")
    valor = valor.replace("PQS", "QS")

    while "__" in valor:
        valor = valor.replace("__", "_")

    return valor.strip("_")


def componentes_partido(partido_o_coalicion):
    partido_o_coalicion = normalizar_partido(partido_o_coalicion)

    if partido_o_coalicion == "":
        return []

    return [p for p in partido_o_coalicion.split("_") if p]