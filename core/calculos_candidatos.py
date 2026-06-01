import pandas as pd
import re
import unicodedata

from core.limpieza import limpiar_numero, normalizar_partido, componentes_partido
from core.calculos_generales import valor_columna_sumada
from core.candidatos import filtrar_candidatos_por_municipio

from config.reglas import (
    columna_es_voto_valida,
    clasificar_fuerza_politica,
    etiqueta_fuerza_politica,
)


def obtener_total_votos_emitidos(df):
    """
    Devuelve el total de votos emitidos para calcular porcentajes.

    Según el año, la columna puede llamarse:
    - VOTOS_EMITIDOS
    - VOTOS_EMITIDOS_1
    - TOT_VOTOS
    """

    return valor_columna_sumada(
        df,
        ["VOTOS_EMITIDOS", "VOTOS_EMITIDOS_1", "TOT_VOTOS"]
    )


def iniciales_candidato(nombre):
    """
    Convierte el nombre de un candidato independiente en siglas.

    Ejemplos:
    RUBEN HERNANDEZ ROBLES -> RHR
    J. BELEM LEDESMA LEDESMA -> JBLL
    EFRAIN MUNOZ COSME -> EMC
    """

    nombre = str(nombre).strip().upper()

    nombre = unicodedata.normalize("NFKD", nombre)
    nombre = nombre.encode("ASCII", "ignore").decode("utf-8")

    nombre = re.sub(r"[^A-Z ]", " ", nombre)

    partes = [p for p in nombre.split() if p]

    if not partes:
        return ""

    return "".join(p[0] for p in partes)


def obtener_componentes_candidato(candidato, partidos_originales):
    """
    Obtiene todos los componentes que se deben buscar en la sábana
    para sumar los votos del candidato.

    Casos:
    - PAN-PRI-PRD -> PAN, PRI, PRD
    - PVEM-MORENA-PT -> PVEM, MORENA, PT
    - PQS -> QS
    - IND -> iniciales del candidato, por ejemplo RHR o JBLL
    """

    componentes = set()

    for partido in partidos_originales:
        partido_norm = normalizar_partido(partido)

        componentes.update(componentes_partido(partido_norm))

        if partido_norm == "IND":
            sigla_independiente = iniciales_candidato(candidato)

            if sigla_independiente:
                componentes.add(sigla_independiente)

    return componentes


def calcular_votos_para_componentes(df, componentes):
    """
    Suma todas las columnas de votos que corresponden a los componentes
    del candidato.

    Ejemplo:
    Si el candidato es PAN-PRI-PRD, suma:
    PAN, PRI, PRD, PAN_PRI, PAN_PRD, PRI_PRD, PAN_PRI_PRD.

    Si el candidato es PVEM-MORENA-PT, suma:
    PVEM, MORENA, PT, PVEM_MORENA, PVEM_PT, MORENA_PT, PVEM_MORENA_PT.
    """

    componentes = set(componentes)

    votos_total = 0
    columnas_usadas = []

    for col in df.columns:
        col_norm = normalizar_partido(col)

        if not columna_es_voto_valida(col_norm):
            continue

        partes_columna = set(componentes_partido(col_norm))

        if partes_columna and partes_columna.issubset(componentes):
            votos_columna = df[col].apply(limpiar_numero).sum()

            if votos_columna > 0:
                votos_total += votos_columna
                columnas_usadas.append(col_norm)

    return votos_total, columnas_usadas


def calcular_top_candidatos(
    df_filtrado,
    df_candidatos,
    tipo_eleccion,
    id_municipio=None
):
    """
    Calcula el ranking de candidatos para el filtro actual.

    Incluye:
    - partidos principales
    - coaliciones
    - otros partidos
    - candidaturas independientes
    """

    total_votos_emitidos = obtener_total_votos_emitidos(df_filtrado)

    df_cand = filtrar_candidatos_por_municipio(
        df_candidatos=df_candidatos,
        id_municipio=id_municipio
    )

    resultados = []

    for candidato, grupo in df_cand.groupby("CANDIDATO"):
        partidos_originales = grupo["PARTIDO_CI"].dropna().unique().tolist()

        if not partidos_originales:
            continue

        componentes = obtener_componentes_candidato(
            candidato=candidato,
            partidos_originales=partidos_originales
        )

        votos, columnas_usadas = calcular_votos_para_componentes(
            df=df_filtrado,
            componentes=componentes
        )

        if votos > 0:
            porcentaje = (
                votos / total_votos_emitidos * 100
                if total_votos_emitidos > 0
                else 0
            )

            partido_mostrar = " + ".join(partidos_originales)
            partido_mostrar_norm = normalizar_partido(partido_mostrar)

            resultados.append({
                "CANDIDATO": candidato,
                "PARTIDOS": partido_mostrar,
                "PARTIDOS_NORM": partido_mostrar_norm,
                "CLASIFICACION_FUERZA": clasificar_fuerza_politica(partido_mostrar),
                "ETIQUETA_VISUAL": etiqueta_fuerza_politica(partido_mostrar),
                "COLUMNAS_SUMADAS": " + ".join(columnas_usadas),
                "VOTOS": int(votos),
                "PORCENTAJE": porcentaje,
            })

    df_resultados = pd.DataFrame(resultados)

    if not df_resultados.empty:
        df_resultados = df_resultados.sort_values(
            "VOTOS",
            ascending=False
        ).reset_index(drop=True)

    return df_resultados