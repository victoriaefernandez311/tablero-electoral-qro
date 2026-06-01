import os
import pandas as pd

from core.carga_datos import cargar_base_electoral
from core.calculos_generales import (
    calcular_kpis_generales,
    obtener_id_municipio,
)
from core.calculos_candidatos import calcular_top_candidatos
from core.ganadores import obtener_ganador_municipal, normalizar_texto
from core.limpieza import limpiar_numero


TIPO_ELECCION = "Ayuntamiento"
ANIO = 2018


CODIGOS_ESPECIALES_GANADORES_2018 = {
    12: None,      # Peñamiller: Juan Carlos Linares Aguilar aparece como vacío / NaN
    15: "JBLL",    # San Joaquín: Belén Ledezma Ledezma
    17: "JAML",    # Tequisquiapan: José Antonio Mejía Lira
}


def cargar_ayuntamiento_2018():
    """
    Carga la base electoral, candidatos y relación de secciones
    para Ayuntamiento 2018.
    """

    return cargar_base_electoral(TIPO_ELECCION, ANIO)


def obtener_municipios_ayuntamiento_2018(df_final):
    """
    Devuelve la lista de municipios disponibles en Ayuntamiento 2018,
    ordenados por NUM_MUN_OFICIAL.
    """

    municipios = (
        df_final[["NUM_MUN_OFICIAL", "CVE_MUN", "MUNICIPIO"]]
        .drop_duplicates()
        .sort_values("NUM_MUN_OFICIAL")
        .reset_index(drop=True)
    )

    return municipios


def filtrar_municipio_ayuntamiento_2018(df_final, num_mun_oficial):
    """
    Filtra la base por número oficial de municipio.
    """

    return df_final[
        df_final["NUM_MUN_OFICIAL"] == num_mun_oficial
    ].copy()


def normalizar_nombre_comparacion(nombre):
    """
    Normaliza nombres para comparar candidatos.
    """

    nombre_norm = normalizar_texto(nombre)

    nombre_norm = nombre_norm.replace("MA ", "MARIA ")
    nombre_norm = nombre_norm.replace("MA. ", "MARIA ")

    while "  " in nombre_norm:
        nombre_norm = nombre_norm.replace("  ", " ")

    return nombre_norm.strip()


def partido_oficial_en_top1(top1_etiqueta, partido_oficial):
    """
    Valida si el partido oficial está dentro de la fuerza calculada.

    Ejemplo:
    PAN dentro de PAN_+_PRD_+_MC -> True
    PRI dentro de PRI_+_PVEM -> True
    MORENA dentro de MORENA_PT_PES -> True
    """

    top1 = str(top1_etiqueta).upper().strip()
    oficial = str(partido_oficial).upper().strip()

    top1 = top1.replace("+", "_")
    top1 = top1.replace(" ", "_")

    partes = [p for p in top1.split("_") if p]

    return oficial in partes


def sumar_votos_seguro(df_mun, mascara, col_votos):
    """
    Suma una columna de votos aunque venga como texto o con tipos mezclados.
    """

    datos = df_mun.loc[mascara, col_votos]

    if isinstance(datos, pd.DataFrame):
        datos = datos.iloc[:, 0]

    datos_limpios = datos.apply(limpiar_numero)
    datos_limpios = pd.to_numeric(datos_limpios, errors="coerce").fillna(0)

    return float(datos_limpios.sum())


def recuperar_votos_por_codigo_lugar_2018(df_mun, codigo):
    """
    Recupera votos de candidatos especiales que no aparecen como columna directa,
    pero sí aparecen en columnas de lugares de la sábana.
    """

    total = 0.0

    pares = [
        ("1ER_LUGAR", "1ERO_VOTOS"),
        ("2DO_LUGAR", "2DO_VOTOS"),
        ("3ER_LUGAR", "3RO_VOTOS"),
        ("3ER_LUGAR", "3ERO_VOTOS"),
    ]

    for col_lugar, col_votos in pares:
        if col_lugar not in df_mun.columns or col_votos not in df_mun.columns:
            continue

        if codigo is None:
            mascara = df_mun[col_lugar].isna()
        else:
            mascara = (
                df_mun[col_lugar]
                .astype(str)
                .str.upper()
                .str.strip()
                == codigo
            )

        total += sumar_votos_seguro(
            df_mun=df_mun,
            mascara=mascara,
            col_votos=col_votos
        )

    return int(total)


def recuperar_votos_ganador_especial_2018(df_mun, num_mun_oficial):
    """
    Recupera votos del ganador oficial en municipios donde el ganador no aparece
    correctamente enlazado por nombre ni por partido.
    """

    if num_mun_oficial not in CODIGOS_ESPECIALES_GANADORES_2018:
        return None

    codigo = CODIGOS_ESPECIALES_GANADORES_2018[num_mun_oficial]

    votos = recuperar_votos_por_codigo_lugar_2018(
        df_mun=df_mun,
        codigo=codigo
    )

    votos_emitidos = df_mun["VOTOS_EMITIDOS"].apply(limpiar_numero).sum()

    porcentaje = (
        votos / votos_emitidos * 100
        if votos_emitidos > 0
        else 0
    )

    return {
        "VOTOS": votos,
        "PORCENTAJE": porcentaje,
        "COLUMNAS_SUMADAS": (
            codigo if codigo is not None else "LUGARES_CON_VALOR_VACIO"
        ),
    }


def agregar_ganador_oficial_2018(resumen):
    """
    Agrega al resumen municipal el ganador oficial proveniente del CSV
    ganadores_QRO_2018-2021.csv.

    Además recupera votos del TOP1 oficial:
    - por nombre
    - por partido / coalición
    - por código especial
    """

    municipio = resumen["MUNICIPIO"]

    ganador = obtener_ganador_municipal(
        anio=ANIO,
        municipio=municipio
    )

    resumen["GANADOR_OFICIAL"] = ganador

    top = resumen["TOP_CANDIDATOS"]

    resumen["TOP1_VOTOS_OFICIAL"] = None
    resumen["TOP1_PORCENTAJE_OFICIAL"] = None
    resumen["TOP1_COLUMNAS_SUMADAS_OFICIAL"] = ""
    resumen["TOP1_ORIGEN_VOTOS"] = "OFICIAL SIN VOTOS CALCULADOS"

    if ganador is None:
        resumen["TOP1_COINCIDE_GANADOR_OFICIAL"] = False
        resumen["TOP1_COINCIDE_PARTIDO_OFICIAL"] = False
        resumen["TOP1_ORIGEN_VOTOS"] = "SIN GANADOR OFICIAL"
        return resumen

    if top is None or top.empty:
        resumen["TOP1_COINCIDE_GANADOR_OFICIAL"] = False
        resumen["TOP1_COINCIDE_PARTIDO_OFICIAL"] = False
        resumen["TOP1_ORIGEN_VOTOS"] = "SIN TOP CALCULADO"
        return resumen

    top1 = top.iloc[0]

    top1_candidato_norm = normalizar_nombre_comparacion(top1["CANDIDATO"])
    ganador_norm = normalizar_nombre_comparacion(
        ganador["PRESIDENTE_MUNICIPAL"]
    )

    top1_partido = str(top1["ETIQUETA_VISUAL"]).strip().upper()
    ganador_partido = str(ganador["PARTIDO_NORM"]).strip().upper()

    resumen["TOP1_COINCIDE_GANADOR_OFICIAL"] = (
        top1_candidato_norm == ganador_norm
    )

    resumen["TOP1_COINCIDE_PARTIDO_OFICIAL"] = partido_oficial_en_top1(
        top1_etiqueta=top1_partido,
        partido_oficial=ganador_partido
    )

    # 1. Buscar votos por nombre.
    for _, fila in top.iterrows():
        candidato_norm = normalizar_nombre_comparacion(fila["CANDIDATO"])

        if candidato_norm == ganador_norm:
            resumen["TOP1_VOTOS_OFICIAL"] = int(fila["VOTOS"])
            resumen["TOP1_PORCENTAJE_OFICIAL"] = float(fila["PORCENTAJE"])
            resumen["TOP1_COLUMNAS_SUMADAS_OFICIAL"] = fila["COLUMNAS_SUMADAS"]
            resumen["TOP1_ORIGEN_VOTOS"] = "OFICIAL + VOTOS POR NOMBRE"
            return resumen

    # 2. Buscar votos por partido / coalición.
    for _, fila in top.iterrows():
        etiqueta = str(fila["ETIQUETA_VISUAL"]).strip().upper()

        if partido_oficial_en_top1(etiqueta, ganador_partido):
            resumen["TOP1_VOTOS_OFICIAL"] = int(fila["VOTOS"])
            resumen["TOP1_PORCENTAJE_OFICIAL"] = float(fila["PORCENTAJE"])
            resumen["TOP1_COLUMNAS_SUMADAS_OFICIAL"] = fila["COLUMNAS_SUMADAS"]
            resumen["TOP1_ORIGEN_VOTOS"] = "OFICIAL + VOTOS POR PARTIDO"
            return resumen

    # 3. Buscar votos por código especial.
    votos_especiales = recuperar_votos_ganador_especial_2018(
        df_mun=resumen["DF_MUNICIPIO"],
        num_mun_oficial=resumen["NUM_MUN_OFICIAL"]
    )

    if votos_especiales is not None:
        resumen["TOP1_VOTOS_OFICIAL"] = votos_especiales["VOTOS"]
        resumen["TOP1_PORCENTAJE_OFICIAL"] = votos_especiales["PORCENTAJE"]
        resumen["TOP1_COLUMNAS_SUMADAS_OFICIAL"] = votos_especiales["COLUMNAS_SUMADAS"]
        resumen["TOP1_ORIGEN_VOTOS"] = "OFICIAL + VOTOS POR CÓDIGO ESPECIAL"

    return resumen


def es_fila_usada_por_top1_2018(fila, resumen):
    """
    Determina si una fila calculada ya fue usada para recuperar votos del TOP1 oficial.
    Si fue usada, no debe volver a aparecer como TOP2 o TOP3.
    """

    ganador = resumen["GANADOR_OFICIAL"]

    if ganador is None:
        return False

    candidato_fila = normalizar_nombre_comparacion(fila["CANDIDATO"])
    candidato_oficial = normalizar_nombre_comparacion(
        ganador["PRESIDENTE_MUNICIPAL"]
    )

    if candidato_fila == candidato_oficial:
        return True

    votos_top1 = resumen.get("TOP1_VOTOS_OFICIAL")
    porcentaje_top1 = resumen.get("TOP1_PORCENTAJE_OFICIAL")
    partido_oficial = ganador["PARTIDO_NORM"]

    if votos_top1 is None or porcentaje_top1 is None:
        return False

    votos_fila = int(fila["VOTOS"])
    porcentaje_fila = float(fila["PORCENTAJE"])
    etiqueta_fila = fila["ETIQUETA_VISUAL"]

    mismos_votos = votos_fila == int(votos_top1)
    mismo_porcentaje = round(porcentaje_fila, 2) == round(float(porcentaje_top1), 2)
    contiene_partido = partido_oficial_en_top1(etiqueta_fila, partido_oficial)

    if mismos_votos and mismo_porcentaje and contiene_partido:
        return True

    return False


def construir_top3_final_ayuntamiento_2018(resumen):
    """
    Construye el Top 3 final:
    - TOP1 oficial desde CSV de ganadores.
    - TOP2 y TOP3 calculados, excluyendo la fila usada por TOP1.
    """

    ganador = resumen["GANADOR_OFICIAL"]
    top_calculado = resumen["TOP_CANDIDATOS"]

    top_final = []

    if ganador is not None:
        top_final.append({
            "PUESTO": 1,
            "CANDIDATO": ganador["PRESIDENTE_MUNICIPAL"],
            "PARTIDO": ganador["PARTIDO_NORM"],
            "VOTOS": resumen.get("TOP1_VOTOS_OFICIAL"),
            "PORCENTAJE": resumen.get("TOP1_PORCENTAJE_OFICIAL"),
            "COLUMNAS_SUMADAS": resumen.get("TOP1_COLUMNAS_SUMADAS_OFICIAL", ""),
            "ORIGEN": resumen.get("TOP1_ORIGEN_VOTOS", "OFICIAL"),
        })

    if top_calculado is not None and not top_calculado.empty:
        for _, fila in top_calculado.iterrows():

            if es_fila_usada_por_top1_2018(fila, resumen):
                continue

            top_final.append({
                "PUESTO": len(top_final) + 1,
                "CANDIDATO": fila["CANDIDATO"],
                "PARTIDO": fila["ETIQUETA_VISUAL"],
                "VOTOS": int(fila["VOTOS"]),
                "PORCENTAJE": float(fila["PORCENTAJE"]),
                "COLUMNAS_SUMADAS": fila["COLUMNAS_SUMADAS"],
                "ORIGEN": "CALCULADO",
            })

            if len(top_final) == 3:
                break

    return top_final


def calcular_resumen_municipal_ayuntamiento_2018(
    df_final,
    df_candidatos,
    num_mun_oficial
):
    """
    Calcula el resumen completo de un municipio para Ayuntamiento 2018.

    Incluye:
    - datos básicos del municipio
    - KPIs generales
    - Top calculado desde la sábana
    - Ganador oficial desde CSV
    - Top 3 final sin duplicados
    """

    df_mun = filtrar_municipio_ayuntamiento_2018(
        df_final=df_final,
        num_mun_oficial=num_mun_oficial
    )

    if df_mun.empty:
        return None

    municipio = df_mun["MUNICIPIO"].iloc[0]
    cve_mun_interno = int(df_mun["CVE_MUN"].iloc[0])

    seccion_min = int(df_mun["SECCION"].min())
    seccion_max = int(df_mun["SECCION"].max())
    cantidad_secciones = df_mun["SECCION"].nunique()

    id_municipio = obtener_id_municipio(df_mun)

    kpis = calcular_kpis_generales(df_mun)

    top_candidatos = calcular_top_candidatos(
        df_filtrado=df_mun,
        df_candidatos=df_candidatos,
        tipo_eleccion=TIPO_ELECCION,
        id_municipio=id_municipio
    )

    resumen = {
        "ANIO": ANIO,
        "TIPO_ELECCION": TIPO_ELECCION,
        "NUM_MUN_OFICIAL": int(num_mun_oficial),
        "CVE_MUN_INTERNO": cve_mun_interno,
        "MUNICIPIO": municipio,
        "SECCION_MIN": seccion_min,
        "SECCION_MAX": seccion_max,
        "CANTIDAD_SECCIONES": cantidad_secciones,
        "ID_MUNICIPIO_CANDIDATOS": id_municipio,
        "KPIS": kpis,
        "TOP_CANDIDATOS": top_candidatos,
        "DF_MUNICIPIO": df_mun,
    }

    resumen = agregar_ganador_oficial_2018(resumen)
    resumen["TOP3_FINAL"] = construir_top3_final_ayuntamiento_2018(resumen)

    return resumen


def generar_informe_control_ayuntamiento_2018():
    """
    Genera un informe de control en memoria para todos los municipios
    de Ayuntamiento 2018.
    """

    df_final, df_candidatos, df_rel = cargar_ayuntamiento_2018()

    municipios = obtener_municipios_ayuntamiento_2018(df_final)

    informes = []

    for _, row in municipios.iterrows():
        num_mun_oficial = int(row["NUM_MUN_OFICIAL"])

        resumen = calcular_resumen_municipal_ayuntamiento_2018(
            df_final=df_final,
            df_candidatos=df_candidatos,
            num_mun_oficial=num_mun_oficial
        )

        if resumen is not None:
            informes.append(resumen)

    return informes