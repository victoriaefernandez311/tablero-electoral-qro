import pandas as pd

from core.limpieza import normalizar_partido, limpiar_numero


def preparar_candidatos(df_candidatos):
    """
    Prepara el catálogo de candidatos para poder cruzarlo correctamente
    por partido, coalición y municipio.
    """

    df = df_candidatos.copy()

    if "PARTIDO_CI" in df.columns:
        df["PARTIDO_NORM"] = df["PARTIDO_CI"].apply(normalizar_partido)
    else:
        df["PARTIDO_NORM"] = ""

    if "ID_MUNICIPIO" in df.columns:
        df["ID_MUNICIPIO_NUM"] = df["ID_MUNICIPIO"].apply(limpiar_numero)
    else:
        df["ID_MUNICIPIO_NUM"] = None

    if "CANDIDATO" not in df.columns:
        df["CANDIDATO"] = "Sin candidato cargado"

    return df


def filtrar_candidatos_por_municipio(df_candidatos, id_municipio):
    """
    Filtra candidatos por municipio cuando corresponde.

    Si id_municipio es None, devuelve todos los candidatos.
    """

    df = preparar_candidatos(df_candidatos)

    if id_municipio is None:
        return df

    if "ID_MUNICIPIO_NUM" not in df.columns:
        return df

    return df[df["ID_MUNICIPIO_NUM"] == limpiar_numero(id_municipio)]


def obtener_candidato_por_partido(
    df_candidatos,
    partido_o_coalicion,
    id_municipio=None,
    tipo_eleccion="Ayuntamiento",
    municipio_todos=False
):
    """
    Busca el candidato correspondiente a un partido o coalición.

    La búsqueda prioriza:
    1. Municipio, si corresponde.
    2. Coincidencia exacta de partido/coalición.
    3. Coincidencia por componentes de coalición.
    """

    if df_candidatos is None or df_candidatos.empty:
        return "Sin candidato cargado"

    if tipo_eleccion == "Ayuntamiento" and municipio_todos:
        return "Seleccione un municipio"

    partido_norm = normalizar_partido(partido_o_coalicion)

    df = filtrar_candidatos_por_municipio(df_candidatos, id_municipio)

    if df.empty:
        return "Sin candidato cargado"

    # 1. Coincidencia exacta
    exacto = df[df["PARTIDO_NORM"] == partido_norm]

    if not exacto.empty:
        candidato = exacto.iloc[0]["CANDIDATO"]

        if pd.notna(candidato) and str(candidato).strip() != "":
            return candidato

    # 2. Coincidencia por partes de coalición
    partes = partido_norm.split("_")

    coincidencias = df[df["PARTIDO_NORM"].isin(partes)]

    if not coincidencias.empty:
        candidatos = coincidencias["CANDIDATO"].dropna().unique()

        if len(candidatos) == 1:
            return candidatos[0]

        if len(candidatos) > 1:
            return " / ".join(candidatos)

    return "Sin candidato cargado"


def revisar_catalogo_candidatos(df_candidatos):
    """
    Función de diagnóstico.
    Sirve para revisar rápidamente si el archivo de candidatos tiene
    las columnas necesarias.
    """

    df = preparar_candidatos(df_candidatos)

    columnas_clave = [
        col for col in [
            "ID_MUNICIPIO",
            "ID_MUNICIPIO_NUM",
            "MUNICIPIO",
            "PARTIDO_CI",
            "PARTIDO_NORM",
            "CANDIDATO"
        ]
        if col in df.columns
    ]

    return df[columnas_clave].head(20)