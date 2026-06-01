import pandas as pd

from config.archivos import ARCHIVOS_GANADORES_AYUNTAMIENTO
from core.limpieza import normalizar_columna, normalizar_partido


MAPEO_PARTIDOS_GANADORES = {
    "PARTIDO ACCION NACIONAL": "PAN",
    "PARTIDO REVOLUCIONARIO INSTITUCIONAL": "PRI",
    "MOVIMIENTO REGENERACION NACIONAL": "MORENA",
    "MOVIMIENTO CIUDADANO": "MC",
    "PARTIDO VERDE ECOLOGISTA DE MEXICO": "PVEM",
    "NUEVA ALIANZA": "QI",
    "INDEPENDIENTE": "INDEPENDIENTE",
    "CANDIDATO INDEPENDIENTE": "INDEPENDIENTE",
}


def normalizar_texto(valor):
    """
    Normaliza texto para comparar municipios, partidos y nombres.

    Ejemplo:
    San Juan del Río -> SAN JUAN DEL RIO
    Querétaro -> QUERETARO
    """
    return normalizar_partido(valor).replace("_", " ")


def normalizar_partido_ganador(partido):
    """
    Convierte el nombre largo del partido oficial a sigla.

    Ejemplos:
    Partido Acción Nacional -> PAN
    Movimiento Regeneración Nacional -> MORENA
    Candidato independiente -> INDEPENDIENTE
    """

    partido_norm = normalizar_texto(partido)

    return MAPEO_PARTIDOS_GANADORES.get(partido_norm, partido_norm)


def cargar_ganadores_ayuntamiento(anio):
    """
    Carga el archivo oficial de ganadores municipales según el año.

    Años soportados:
    - 2018
    - 2021
    - 2024
    """

    if anio not in ARCHIVOS_GANADORES_AYUNTAMIENTO:
        raise ValueError(
            f"No hay archivo de ganadores registrado para Ayuntamiento {anio}"
        )

    ruta = ARCHIVOS_GANADORES_AYUNTAMIENTO[anio]

    df = pd.read_csv(ruta, dtype=str, encoding="utf-8-sig")

    df.columns = [normalizar_columna(col) for col in df.columns]

    columnas_requeridas = {
        "MUNICIPIO",
        "PRESIDENTE_MUNICIPAL",
        "PARTIDO",
    }

    columnas_faltantes = columnas_requeridas - set(df.columns)

    if columnas_faltantes:
        raise ValueError(
            f"Faltan columnas en {ruta}: {columnas_faltantes}"
        )

    df["MUNICIPIO_NORM"] = df["MUNICIPIO"].apply(normalizar_texto)
    df["PRESIDENTE_MUNICIPAL_NORM"] = df["PRESIDENTE_MUNICIPAL"].apply(normalizar_texto)
    df["PARTIDO_NORM"] = df["PARTIDO"].apply(normalizar_partido_ganador)

    return df


def obtener_ganador_municipal(anio, municipio):
    """
    Devuelve el ganador oficial de un municipio para un año determinado.

    Retorna un diccionario con:
    - MUNICIPIO
    - PRESIDENTE_MUNICIPAL
    - PARTIDO
    - PARTIDO_NORM
    """

    df = cargar_ganadores_ayuntamiento(anio)

    municipio_norm = normalizar_texto(municipio)

    coincidencia = df[df["MUNICIPIO_NORM"] == municipio_norm]

    if coincidencia.empty:
        return None

    fila = coincidencia.iloc[0]

    return {
        "ANIO": anio,
        "MUNICIPIO": fila["MUNICIPIO"],
        "MUNICIPIO_NORM": fila["MUNICIPIO_NORM"],
        "PRESIDENTE_MUNICIPAL": fila["PRESIDENTE_MUNICIPAL"],
        "PRESIDENTE_MUNICIPAL_NORM": fila["PRESIDENTE_MUNICIPAL_NORM"],
        "PARTIDO": fila["PARTIDO"],
        "PARTIDO_NORM": fila["PARTIDO_NORM"],
    }


def obtener_ganadores_por_anio(anio):
    """
    Devuelve todos los ganadores municipales oficiales de un año.
    """

    return cargar_ganadores_ayuntamiento(anio)


def obtener_todos_los_ganadores_ayuntamiento():
    """
    Devuelve todos los ganadores municipales oficiales de 2018, 2021 y 2024
    en un solo DataFrame.
    """

    dfs = []

    for anio in sorted(ARCHIVOS_GANADORES_AYUNTAMIENTO.keys()):
        df = cargar_ganadores_ayuntamiento(anio)
        df["ANIO"] = anio
        dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)