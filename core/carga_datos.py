import pandas as pd
import unicodedata

from config.archivos import (
    ARCHIVOS_DATOS,
    ARCHIVOS_CANDIDATOS,
    ARCHIVO_RELACION_SECCIONES
)

from core.limpieza import normalizar_columna


NUMERO_MUNICIPIO_OFICIAL = {
    "AMEALCO DE BONFIL": 1,
    "ARROYO SECO": 2,
    "CADEREYTA DE MONTES": 3,
    "COLON": 4,
    "CORREGIDORA": 5,
    "EZEQUIEL MONTES": 6,
    "HUIMILPAN": 7,
    "JALPAN DE SERRA": 8,
    "LANDA DE MATAMOROS": 9,
    "EL MARQUES": 10,
    "PEDRO ESCOBEDO": 11,
    "PENAMILLER": 12,
    "PINAL DE AMOLES": 13,
    "QUERETARO": 14,
    "SAN JOAQUIN": 15,
    "SAN JUAN DEL RIO": 16,
    "TEQUISQUIAPAN": 17,
    "TOLIMAN": 18,
}


def normalizar_nombre_municipio(valor):
    """
    Normaliza nombres de municipios para poder mapearlos al número oficial.

    Ejemplo:
    'Colón' -> 'COLON'
    'El Marqués' -> 'EL MARQUES'
    'San Juan del Río' -> 'SAN JUAN DEL RIO'
    """

    valor = str(valor).strip().upper()

    valor = unicodedata.normalize("NFKD", valor)
    valor = valor.encode("ASCII", "ignore").decode("utf-8")

    while "  " in valor:
        valor = valor.replace("  ", " ")

    return valor


def leer_csv(ruta):
    """
    Lee un archivo CSV y normaliza sus columnas.
    También corrige nombres de columnas que pueden venir distintos según el año.
    """

    df = pd.read_csv(ruta)
    df.columns = [normalizar_columna(col) for col in df.columns]

    renombres = {
        "NOMBR_FOTO": "NOMBRE_FOTO",
        "ID_ENTIDAD": "ID_ESTADO",
        "ID_MUNICIPIO_LOCAL": "ID_MUNICIPIO",
        "SECCION_ELECTORAL": "SECCION",
    }

    df = df.rename(columns={k: v for k, v in renombres.items() if k in df.columns})

    if "SECCION" in df.columns:
        df["SECCION"] = pd.to_numeric(df["SECCION"], errors="coerce")

    return df


def leer_relacion(anio):
    """
    Lee el archivo Excel de relación de secciones electorales.
    Usa la pestaña correspondiente al año seleccionado.
    """

    df_rel = pd.read_excel(
        ARCHIVO_RELACION_SECCIONES,
        sheet_name=str(anio)
    )

    df_rel.columns = [normalizar_columna(col) for col in df_rel.columns]

    if "NOM_MUN" in df_rel.columns:
        df_rel = df_rel.rename(columns={"NOM_MUN": "MUNICIPIO"})

    if "SECCION" in df_rel.columns:
        df_rel["SECCION"] = pd.to_numeric(df_rel["SECCION"], errors="coerce")

    return df_rel


def agregar_numero_municipio_oficial(df):
    """
    Agrega NUM_MUN_OFICIAL según el orden oficial de municipios.

    Importante:
    - No reemplaza CVE_MUN.
    - CVE_MUN queda como código interno original.
    - NUM_MUN_OFICIAL será el número usado para mostrar y validar candidatos.
    """

    df = df.copy()

    if "MUNICIPIO" not in df.columns:
        df["MUNICIPIO_NORM"] = None
        df["NUM_MUN_OFICIAL"] = None
        return df

    df["MUNICIPIO_NORM"] = df["MUNICIPIO"].apply(normalizar_nombre_municipio)

    df["NUM_MUN_OFICIAL"] = df["MUNICIPIO_NORM"].map(NUMERO_MUNICIPIO_OFICIAL)

    return df


def cargar_base_electoral(tipo_eleccion, anio):
    """
    Carga:
    - datos electorales del año
    - candidatos del año
    - relación de secciones
    - dataframe final unido por SECCION
    """

    ruta_datos = ARCHIVOS_DATOS[(tipo_eleccion, anio)]
    ruta_candidatos = ARCHIVOS_CANDIDATOS[(tipo_eleccion, anio)]

    df = leer_csv(ruta_datos)
    df_candidatos = leer_csv(ruta_candidatos)
    df_rel = leer_relacion(anio)

    df_final = df.merge(
        df_rel,
        on="SECCION",
        how="left",
        suffixes=("", "_REL")
    )

    df_final = agregar_numero_municipio_oficial(df_final)

    return df_final, df_candidatos, df_rel