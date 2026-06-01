import pandas as pd
import os
from config.archivos import ARCHIVOS_DATOS, ARCHIVOS_CANDIDATOS
from core.limpieza import normalizar_columna
from core.carga_datos import leer_relacion, agregar_numero_municipio_oficial
from core.calculos_candidatos import calcular_top_candidatos


TIPO_ELECCION = "Gobernatura"
ANIO = 2021


DISTRITOS_OFICIALES_GOBERNATURA_2021 = {
    1: "QUERÉTARO",
    2: "QUERÉTARO",
    3: "QUERÉTARO",
    4: "QUERÉTARO",
    5: "QUERÉTARO",
    6: "CORREGIDORA",
    7: "CORREGIDORA",
    8: "SAN JUAN DEL RÍO",
    9: "SAN JUAN DEL RÍO",
    10: "PEDRO ESCOBEDO",
    11: "TEQUISQUIAPAN",
    12: "EL MARQUÉS",
    13: "QUERÉTARO",
    14: "CADEREYTA DE MONTES",
    15: "JALPAN DE SERRA",
}


COLUMNAS_NUMERICAS_GOBERNATURA_2021 = [
    "LISTA_NOMINAL",
    "VOTOS_EMITIDOS",
    "PARTICIPACION",
    "ABSTENCION",
    "1ERO_VOTOS",
    "PCN",
    "DIF_VOTOS_2DO",
    "DIF_PCN_2DO",
    "2DO_VOTOS",
    "PCN_2",
    "DIF_VOTOS_3RO",
    "DIF_PCN_3RO",
    "3RO_VOTOS",
    "PCN_3",
    "VOTOS",
    "PCN_4",
    "DIF_2DO",
    "PCN_5",
    "VOTOS_2",
    "PCN_6",
    "DIF_3RO",
    "PCN_7",
    "VOTOS_3",
    "PCN_8",
    "PAN",
    "PCN_9",
    "PRI",
    "PCN_10",
    "PRD",
    "PCN_11",
    "MC",
    "PCN_12",
    "PVEM",
    "PCN_13",
    "MORENA",
    "PCN_14",
    "PT",
    "PCN_15",
    "QI",
    "PCN_16",
    "PES",
    "PCN_17",
    "RSP",
    "PCN_18",
    "FXM",
    "PCN_19",
    "PAN_QI",
    "PCN_20",
    "CNR",
    "PCN_21",
    "NULOS",
    "PCN_22",
    "TOT_VOTOS",
]


COLUMNAS_COMPONENTES_VOTOS_GOBERNATURA_2021 = [
    "PAN",
    "PRI",
    "PRD",
    "MC",
    "PVEM",
    "MORENA",
    "PT",
    "QI",
    "PES",
    "RSP",
    "FXM",
    "PAN_QI",
    "CNR",
    "NULOS",
]


def limpiar_numero_gobernatura_2021(valor):
    """
    Limpieza numérica específica para Gobernatura 2021.

    Esta sábana mezcla formatos como:

    729.000 -> 729
    638.000 -> 638
    1.070   -> 1070
    1.238   -> 1238
    1.000   -> 1000

    Regla clave:
    - Si termina en .000 y la parte izquierda tiene 1 solo dígito,
      se interpreta como miles.
      Ejemplo: 1.000 -> 1000.
    - Si termina en .000 y la parte izquierda tiene 3 dígitos,
      se interpreta como entero exportado con decimales.
      Ejemplo: 729.000 -> 729.
    """

    if pd.isna(valor):
        return 0

    valor = str(valor).strip()

    if valor == "":
        return 0

    valor = valor.replace("%", "")
    valor = valor.replace(" ", "")

    if "," in valor and "." in valor:
        ultima_coma = valor.rfind(",")
        ultimo_punto = valor.rfind(".")

        if ultima_coma > ultimo_punto:
            valor = valor.replace(".", "")
            valor = valor.replace(",", ".")
        else:
            valor = valor.replace(",", "")

        try:
            return float(valor)
        except ValueError:
            return 0

    if "," in valor:
        partes = valor.split(",")

        if len(partes[-1]) == 3 and all(p.isdigit() for p in partes):
            valor = valor.replace(",", "")
        else:
            valor = valor.replace(",", ".")

        try:
            return float(valor)
        except ValueError:
            return 0

    if "." in valor:
        partes = valor.split(".")

        if all(p.isdigit() for p in partes) and len(partes) == 2:
            parte_izquierda = partes[0]
            parte_derecha = partes[1]

            if parte_derecha == "000":
                if len(parte_izquierda) == 1:
                    return float(parte_izquierda + parte_derecha)
                else:
                    return float(parte_izquierda)

            if len(parte_derecha) == 3:
                valor = valor.replace(".", "")

        try:
            return float(valor)
        except ValueError:
            return 0

    try:
        return float(valor)
    except ValueError:
        return 0


def leer_csv_gobernatura_2021(ruta):
    """
    Lee CSV de Gobernatura 2021 como texto para no perder separadores originales.
    """

    df = pd.read_csv(ruta, dtype=str)
    df.columns = [normalizar_columna(col) for col in df.columns]

    renombres = {
        "NOMBR_FOTO": "NOMBRE_FOTO",
        "ID_ENTIDAD": "ID_ESTADO",
        "SECCION_ELECTORAL": "SECCION",
    }

    df = df.rename(columns={k: v for k, v in renombres.items() if k in df.columns})

    if "SECCION" in df.columns:
        df["SECCION"] = pd.to_numeric(df["SECCION"], errors="coerce")

    return df


def limpiar_columnas_numericas_gobernatura_2021(df):
    """
    Convierte a número las columnas de votos, lista nominal y porcentajes
    usando limpieza específica de Gobernatura 2021.
    """

    df = df.copy()

    for col in COLUMNAS_NUMERICAS_GOBERNATURA_2021:
        if col in df.columns:
            df[col] = df[col].apply(limpiar_numero_gobernatura_2021)

    return df


def cargar_gobernatura_2021():
    """
    Carga Gobernatura 2021 con limpieza numérica específica.
    No modifica core/limpieza.py.
    """

    ruta_datos = ARCHIVOS_DATOS[(TIPO_ELECCION, ANIO)]
    ruta_candidatos = ARCHIVOS_CANDIDATOS[(TIPO_ELECCION, ANIO)]

    df = leer_csv_gobernatura_2021(ruta_datos)
    df_candidatos = leer_csv_gobernatura_2021(ruta_candidatos)
    df_rel = leer_relacion(ANIO)

    df = limpiar_columnas_numericas_gobernatura_2021(df)

    df_final = df.merge(
        df_rel,
        on="SECCION",
        how="left",
        suffixes=("", "_REL")
    )

    df_final = agregar_numero_municipio_oficial(df_final)

    return df_final, df_candidatos, df_rel


def calcular_votos_emitidos_por_componentes(df):
    """
    Calcula votos emitidos como suma real de componentes:

    partidos + coalición PAN_QI + CNR + NULOS.

    Esto coincide con el total oficial de Gobernatura 2021.
    """

    columnas = [
        col for col in COLUMNAS_COMPONENTES_VOTOS_GOBERNATURA_2021
        if col in df.columns
    ]

    if not columnas:
        return 0

    return df[columnas].sum(axis=1).sum()


def calcular_kpis_gobernatura_2021(df_filtrado):
    """
    Calcula KPIs para Gobernatura 2021.

    La lista nominal se toma de LISTA_NOMINAL.
    Los votos emitidos se calculan como suma de componentes reales:
    partidos + PAN_QI + CNR + NULOS.
    """

    lista_nominal = (
        df_filtrado["LISTA_NOMINAL"].sum()
        if "LISTA_NOMINAL" in df_filtrado.columns
        else 0
    )

    votos_emitidos = calcular_votos_emitidos_por_componentes(df_filtrado)

    votos_nulos = (
        df_filtrado["NULOS"].sum()
        if "NULOS" in df_filtrado.columns
        else 0
    )

    participacion = (
        votos_emitidos / lista_nominal * 100
        if lista_nominal > 0
        else 0
    )

    return {
        "lista_nominal": lista_nominal,
        "votos_emitidos": votos_emitidos,
        "votos_nulos": votos_nulos,
        "participacion": participacion,
    }


def obtener_nombre_distrito_oficial(distrito_local):
    """
    Devuelve el nombre oficial/cabecera del distrito según la página oficial.
    """

    try:
        distrito_num = int(float(distrito_local))
    except:
        return "DISTRITO"

    return DISTRITOS_OFICIALES_GOBERNATURA_2021.get(
        distrito_num,
        "DISTRITO"
    )


def formatear_distrito_label(nombre_distrito, distrito_local):
    """
    Devuelve el texto del distrito con formato oficial.
    """

    try:
        distrito_num = int(float(distrito_local))
        distrito_txt = f"{distrito_num:02d}"
    except:
        distrito_txt = str(distrito_local).strip()

    return f"{nombre_distrito} {distrito_txt}"


def obtener_distritos_gobernatura_2021(df_final):
    """
    Devuelve los distritos locales disponibles, ordenados por número.
    """

    if "DISTRITO_LOCAL" not in df_final.columns:
        return []

    distritos_reales = sorted(df_final["DISTRITO_LOCAL"].dropna().unique())

    distritos = []

    for distrito in distritos_reales:
        df_distrito = df_final[df_final["DISTRITO_LOCAL"] == distrito].copy()

        distrito_num = int(float(distrito))
        nombre_distrito = obtener_nombre_distrito_oficial(distrito_num)
        etiqueta = formatear_distrito_label(nombre_distrito, distrito_num)

        distritos.append({
            "DISTRITO_LOCAL": distrito_num,
            "DISTRITO_LABEL": etiqueta,
            "NOMBRE_DISTRITO": nombre_distrito,
            "SECCION_MIN": int(df_distrito["SECCION"].min()),
            "SECCION_MAX": int(df_distrito["SECCION"].max()),
            "CANTIDAD_SECCIONES": df_distrito["SECCION"].nunique(),
        })

    return distritos


def filtrar_distrito_gobernatura_2021(df_final, distrito_local):
    """
    Filtra la base por distrito local.
    """

    return df_final[
        df_final["DISTRITO_LOCAL"] == distrito_local
    ].copy()


def calcular_resumen_general_gobernatura_2021(df_final, df_candidatos):
    """
    Calcula el resumen general estatal de Gobernatura 2021.
    """

    df_general = df_final.copy()

    kpis = calcular_kpis_gobernatura_2021(df_general)

    top_candidatos = calcular_top_candidatos(
        df_filtrado=df_general,
        df_candidatos=df_candidatos,
        tipo_eleccion=TIPO_ELECCION,
        id_municipio=None
    )

    resumen = {
        "ANIO": ANIO,
        "TIPO_ELECCION": TIPO_ELECCION,
        "NIVEL": "GENERAL",
        "DISTRITO_LOCAL": None,
        "DISTRITO_LABEL": "GENERAL ESTATAL",
        "NOMBRE_DISTRITO": "GENERAL ESTATAL",
        "SECCION_MIN": int(df_general["SECCION"].min()),
        "SECCION_MAX": int(df_general["SECCION"].max()),
        "CANTIDAD_SECCIONES": df_general["SECCION"].nunique(),
        "KPIS": kpis,
        "TOP_CANDIDATOS": top_candidatos,
    }

    return resumen


def calcular_resumen_distrital_gobernatura_2021(
    df_final,
    df_candidatos,
    distrito_local
):
    """
    Calcula resumen completo de un distrito.
    """

    df_distrito = filtrar_distrito_gobernatura_2021(
        df_final=df_final,
        distrito_local=distrito_local
    )

    if df_distrito.empty:
        return None

    distrito_num = int(float(distrito_local))
    nombre_distrito = obtener_nombre_distrito_oficial(distrito_num)

    distrito_label = formatear_distrito_label(
        nombre_distrito=nombre_distrito,
        distrito_local=distrito_num
    )

    seccion_min = int(df_distrito["SECCION"].min())
    seccion_max = int(df_distrito["SECCION"].max())
    cantidad_secciones = df_distrito["SECCION"].nunique()

    kpis = calcular_kpis_gobernatura_2021(df_distrito)

    top_candidatos = calcular_top_candidatos(
        df_filtrado=df_distrito,
        df_candidatos=df_candidatos,
        tipo_eleccion=TIPO_ELECCION,
        id_municipio=None
    )

    resumen = {
        "ANIO": ANIO,
        "TIPO_ELECCION": TIPO_ELECCION,
        "NIVEL": "DISTRITO",
        "DISTRITO_LOCAL": distrito_num,
        "DISTRITO_LABEL": distrito_label,
        "NOMBRE_DISTRITO": nombre_distrito,
        "SECCION_MIN": seccion_min,
        "SECCION_MAX": seccion_max,
        "CANTIDAD_SECCIONES": cantidad_secciones,
        "KPIS": kpis,
        "TOP_CANDIDATOS": top_candidatos,
    }

    return resumen


def generar_informe_control_gobernatura_2021():
    """
    Genera informe de control en memoria para Gobernatura 2021.

    Incluye:
    1. General estatal
    2. Distritos locales
    """

    df_final, df_candidatos, df_rel = cargar_gobernatura_2021()

    informes = []

    resumen_general = calcular_resumen_general_gobernatura_2021(
        df_final=df_final,
        df_candidatos=df_candidatos
    )

    informes.append(resumen_general)

    distritos = obtener_distritos_gobernatura_2021(df_final)

    for distrito in distritos:
        distrito_local = distrito["DISTRITO_LOCAL"]

        resumen = calcular_resumen_distrital_gobernatura_2021(
            df_final=df_final,
            df_candidatos=df_candidatos,
            distrito_local=distrito_local
        )

        if resumen is not None:
            informes.append(resumen)

    return informes
def convertir_resumen_a_fila_csv(resumen):
    """
    Convierte un resumen general o distrital en una fila plana para CSV.
    """

    kpis = resumen["KPIS"]
    top = resumen["TOP_CANDIDATOS"]

    fila = {
        "ANIO": resumen["ANIO"],
        "TIPO_ELECCION": resumen["TIPO_ELECCION"],
        "NIVEL": resumen["NIVEL"],
        "DISTRITO_LOCAL": resumen["DISTRITO_LOCAL"],
        "DISTRITO_LABEL": resumen["DISTRITO_LABEL"],
        "NOMBRE_DISTRITO": resumen["NOMBRE_DISTRITO"],
        "SECCION_MIN": resumen["SECCION_MIN"],
        "SECCION_MAX": resumen["SECCION_MAX"],
        "CANTIDAD_SECCIONES": resumen["CANTIDAD_SECCIONES"],
        "LISTA_NOMINAL": int(kpis["lista_nominal"]),
        "VOTOS_EMITIDOS": int(kpis["votos_emitidos"]),
        "VOTOS_NULOS": int(kpis["votos_nulos"]),
        "PARTICIPACION_PCN": round(kpis["participacion"], 2),
    }

    for i in range(3):
        puesto = i + 1

        if top is not None and not top.empty and i < len(top):
            candidato = top.iloc[i]

            fila[f"TOP{puesto}_CANDIDATO"] = candidato["CANDIDATO"]
            fila[f"TOP{puesto}_PARTIDOS_ORIGINAL"] = candidato["PARTIDOS"]
            fila[f"TOP{puesto}_PARTIDOS_NORM"] = candidato["PARTIDOS_NORM"]
            fila[f"TOP{puesto}_CLASIFICACION"] = candidato["CLASIFICACION_FUERZA"]
            fila[f"TOP{puesto}_ETIQUETA_VISUAL"] = candidato["ETIQUETA_VISUAL"]
            fila[f"TOP{puesto}_COLUMNAS_SUMADAS"] = candidato["COLUMNAS_SUMADAS"]
            fila[f"TOP{puesto}_VOTOS"] = int(candidato["VOTOS"])
            fila[f"TOP{puesto}_PORCENTAJE"] = round(candidato["PORCENTAJE"], 2)
        else:
            fila[f"TOP{puesto}_CANDIDATO"] = ""
            fila[f"TOP{puesto}_PARTIDOS_ORIGINAL"] = ""
            fila[f"TOP{puesto}_PARTIDOS_NORM"] = ""
            fila[f"TOP{puesto}_CLASIFICACION"] = ""
            fila[f"TOP{puesto}_ETIQUETA_VISUAL"] = ""
            fila[f"TOP{puesto}_COLUMNAS_SUMADAS"] = ""
            fila[f"TOP{puesto}_VOTOS"] = 0
            fila[f"TOP{puesto}_PORCENTAJE"] = 0

    return fila


def generar_dataframe_control_gobernatura_2021():
    """
    Genera el DataFrame de control para Gobernatura 2021.

    Incluye:
    - 1 fila GENERAL ESTATAL
    - 15 filas de DISTRITOS
    """

    informes = generar_informe_control_gobernatura_2021()

    filas = []

    for resumen in informes:
        fila = convertir_resumen_a_fila_csv(resumen)
        filas.append(fila)

    df_control = pd.DataFrame(filas)

    return df_control


def exportar_informe_control_gobernatura_2021(
    ruta_salida="reportes/informe_control_gobernatura_2021.csv"
):
    """
    Exporta el informe de control de Gobernatura 2021 a CSV.
    """

    df_control = generar_dataframe_control_gobernatura_2021()

    carpeta = os.path.dirname(ruta_salida)

    if carpeta:
        os.makedirs(carpeta, exist_ok=True)

    df_control.to_csv(
        ruta_salida,
        index=False,
        encoding="utf-8-sig"
    )

    return ruta_salida, df_control