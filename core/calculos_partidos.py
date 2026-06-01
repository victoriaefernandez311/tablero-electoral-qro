import pandas as pd

from core.limpieza import limpiar_numero, normalizar_partido
from core.calculos_generales import valor_columna_sumada


COLUMNAS_EXCLUIDAS_PARTIDOS = {
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
    "DISTRITO_LOCAL",
    "DISTRITO_FEDERAL",
    "ID_MUNICIPIO",
    "CU_MUNICIPIO",
    "CVE_MUN",
    "NOM_MUN",
}


COLUMNAS_PARTIDOS_POSIBLES = [
    "PAN",
    "PRI",
    "PRD",
    "MC",
    "PVEM",
    "MORENA",
    "PT",
    "QI",
    "QUI",
    "PES",
    "RSP",
    "FXM",
    "QS",
    "CQ",
    "IND",
    "INDEPENDIENTE",

    "PRI_PVEM",
    "PAN_QI",
    "PAN_QUI",
    "PAN_PRD",
    "PAN_PRD_MC",
    "MORENA_PT",
    "MORENA_PT_PES",
    "PVEM_MORENA_PT",
    "PVEM_MORENA",
    "PAN_PRI_PRD",
    "PAN_PRI",
    "PRI_PRD",

    "CNR",
    "NULOS",
    "VOTOS_NULOS",
    "OTROS",
]


def obtener_total_votos_para_porcentaje(df):
    """
    Devuelve el total contra el cual se calculan los porcentajes.
    Prioriza votos emitidos o total de votos.
    """

    return valor_columna_sumada(
        df,
        ["VOTOS_EMITIDOS", "VOTOS_EMITIDOS_1", "TOT_VOTOS"]
    )


def tabla_votos_por_partido(df):
    """
    Calcula votos y porcentaje por partido o coalición,
    usando solamente columnas electorales conocidas.
    """

    total = obtener_total_votos_para_porcentaje(df)

    datos = []

    for col in COLUMNAS_PARTIDOS_POSIBLES:
        if col in df.columns:
            votos = df[col].apply(limpiar_numero).sum()

            if votos > 0:
                datos.append({
                    "PARTIDO": normalizar_partido(col),
                    "COLUMNA_ORIGEN": col,
                    "VOTOS": int(votos),
                    "PORCENTAJE": (votos / total * 100) if total > 0 else 0
                })

    df_tabla = pd.DataFrame(datos)

    if not df_tabla.empty:
        df_tabla = df_tabla.sort_values("VOTOS", ascending=False).reset_index(drop=True)

    return df_tabla