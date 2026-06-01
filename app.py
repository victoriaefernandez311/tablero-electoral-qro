import streamlit as st
import pandas as pd
import unicodedata
import json
import copy
import folium
from streamlit_folium import st_folium
import plotly.express as px
import streamlit.components.v1 as components

from elecciones.ayuntamiento_2018 import generar_informe_control_ayuntamiento_2018
from elecciones.ayuntamiento_2021 import generar_informe_control_ayuntamiento_2021
from elecciones.ayuntamiento_2024 import generar_informe_control_ayuntamiento_2024
from visual.estilos import aplicar_estilos
from visual.layout import mostrar_titulo_dashboard
from visual.componentes import (
    mostrar_kpis,
    mostrar_top3_candidatos,
    mostrar_votos_partidos,
)
from visual.mapa import (
    cargar_geojson,
    crear_mapa_secciones,
    obtener_color_ganador,
    seccion_a_texto,
)
st.set_page_config(page_title="Tablero Electoral", layout="wide")


# ===================================================
# ESTILOS DEL DASHBOARD
# ===================================================

aplicar_estilos()

# ===================================================
# FUNCIONES GENERALES
# ===================================================

def normalizar_columna(col):
    col = str(col).strip().upper()
    col = unicodedata.normalize("NFKD", col).encode("ASCII", "ignore").decode("utf-8")
    col = col.replace(" ", "_").replace("\n", "_")
    col = col.replace("(", "").replace(")", "")
    col = col.replace("%", "PCN")
    col = col.replace(".", "_").replace("-", "_")
    while "__" in col:
        col = col.replace("__", "_")
    return col


def normalizar_texto(valor):
    valor = str(valor).strip().upper()
    valor = unicodedata.normalize("NFKD", valor).encode("ASCII", "ignore").decode("utf-8")
    valor = valor.replace("_", " ")
    while "  " in valor:
        valor = valor.replace("  ", " ")
    return valor.strip()


def limpiar_numero(valor):
    if pd.isna(valor):
        return 0

    valor = str(valor).strip().replace(",", "").replace("%", "")

    try:
        return float(valor)
    except:
        return 0


def leer_csv(ruta):
    df = pd.read_csv(ruta)
    df.columns = [normalizar_columna(c) for c in df.columns]

    if "NOMBR_FOTO" in df.columns:
        df = df.rename(columns={"NOMBR_FOTO": "NOMBRE_FOTO"})

    if "ID_ENTIDAD" in df.columns:
        df = df.rename(columns={"ID_ENTIDAD": "ID_ESTADO"})

    if "ID_MUNICIPIO_LOCAL" in df.columns:
        df = df.rename(columns={"ID_MUNICIPIO_LOCAL": "ID_MUNICIPIO"})

    return df


def leer_relacion(anio):
    df_rel = pd.read_excel(
        "relaciones/Relacion_Secciones_Electorales.xlsx",
        sheet_name=str(anio)
    )

    df_rel.columns = [normalizar_columna(c) for c in df_rel.columns]

    if "NOM_MUN" in df_rel.columns:
        df_rel = df_rel.rename(columns={"NOM_MUN": "MUNICIPIO"})

    return df_rel


def preparar_datos(df):
    if "SECCION_ELECTORAL" in df.columns:
        df = df.rename(columns={"SECCION_ELECTORAL": "SECCION"})

    if "SECCION" in df.columns:
        df["SECCION"] = pd.to_numeric(df["SECCION"], errors="coerce")

    return df


def normalizar_partido(valor):
    valor = str(valor).strip().upper()
    valor = unicodedata.normalize("NFKD", valor).encode("ASCII", "ignore").decode("utf-8")
    valor = valor.replace("-", "_").replace(" ", "_")
    valor = valor.replace("QUI", "QI")
    valor = valor.replace("FM", "FXM")

    while "__" in valor:
        valor = valor.replace("__", "_")

    return valor


def componentes_partido(partido):
    partido = normalizar_partido(partido)
    return [p for p in partido.split("_") if p]


def valor_columna_sumada(df, columnas):
    for col in columnas:
        if col in df.columns:
            return df[col].apply(limpiar_numero).sum()
    return 0


def obtener_id_municipio(df_filtrado):
    for col in ["CU_MUNICIPIO", "CVE_MUN", "ID_MUNICIPIO"]:
        if col in df_filtrado.columns:
            valores = df_filtrado[col].dropna().unique()

            if len(valores) == 1:
                return int(limpiar_numero(valores[0]))

    return None


def obtener_candidato(
    df_candidatos,
    id_municipio,
    partido_o_coalicion,
    tipo_eleccion,
    municipio_todos=False
):
    if df_candidatos.empty:
        return "Sin candidato cargado"

    if tipo_eleccion == "Ayuntamiento" and municipio_todos:
        return "Varios candidatos municipales"

    partido_norm = normalizar_partido(partido_o_coalicion)

    df_aux = df_candidatos.copy()
    df_aux["PARTIDO_NORM"] = df_aux["PARTIDO_CI"].apply(normalizar_partido)

    if id_municipio is not None and "ID_MUNICIPIO" in df_aux.columns:
        df_aux = df_aux[
            df_aux["ID_MUNICIPIO"].apply(limpiar_numero) == id_municipio
        ]

    encontrado = df_aux[df_aux["PARTIDO_NORM"] == partido_norm]

    if not encontrado.empty:
        return encontrado.iloc[0]["CANDIDATO"]

    partes = partido_norm.split("_")
    encontrados = df_aux[df_aux["PARTIDO_NORM"].isin(partes)]

    if not encontrados.empty:
        candidatos = encontrados["CANDIDATO"].dropna().unique()

        if len(candidatos) == 1:
            return candidatos[0]

        return " / ".join(candidatos)

    return "Sin candidato cargado"


# ===================================================
# TOP 3 FINAL AYUNTAMIENTO
# ===================================================

@st.cache_data(show_spinner=False)
def cargar_informes_ayuntamiento(anio):
    if anio == 2018:
        return generar_informe_control_ayuntamiento_2018()

    if anio == 2021:
        return generar_informe_control_ayuntamiento_2021()

    if anio == 2024:
        return generar_informe_control_ayuntamiento_2024()

    return []


def obtener_top3_final_ayuntamiento(anio, municipio):
    """
    Devuelve el TOP3_FINAL de Ayuntamiento usando los módulos electorales.

    TOP1 viene del CSV oficial de ganadores.
    TOP2 y TOP3 vienen calculados desde la sábana, sin duplicar TOP1.
    """

    if municipio == "Todos":
        return []

    informes = cargar_informes_ayuntamiento(anio)
    municipio_norm = normalizar_texto(municipio)

    for informe in informes:
        municipio_informe_norm = normalizar_texto(informe["MUNICIPIO"])

        if municipio_informe_norm == municipio_norm:
            return informe.get("TOP3_FINAL", [])

    return []


# ===================================================
# CÁLCULO ELECTORAL VIEJO
# Se mantiene para Gobernatura y para casos generales.
# ===================================================

def calcular_resultados_candidatos(
    df_filtrado,
    df_candidatos,
    tipo_eleccion,
    id_municipio
):
    df_cand = df_candidatos.copy()

    if (
        tipo_eleccion == "Ayuntamiento"
        and id_municipio is not None
        and "ID_MUNICIPIO" in df_cand.columns
    ):
        df_cand = df_cand[
            df_cand["ID_MUNICIPIO"].apply(limpiar_numero) == id_municipio
        ]

    resultados = []

    for candidato, grupo in df_cand.groupby("CANDIDATO"):
        partidos_originales = grupo["PARTIDO_CI"].dropna().unique().tolist()

        componentes = set()

        for p in partidos_originales:
            componentes.update(componentes_partido(p))

        votos_total = 0
        columnas_usadas = []

        for col in df_filtrado.columns:
            col_norm = normalizar_partido(col)

            if col_norm in ["CNR", "NULOS", "VOTOS_NULOS", "OTROS"]:
                continue

            partes_col = set(componentes_partido(col_norm))

            if partes_col and partes_col.issubset(componentes):
                votos_col = df_filtrado[col].apply(limpiar_numero).sum()

                if votos_col > 0:
                    votos_total += votos_col
                    columnas_usadas.append(col_norm)

        if votos_total > 0:
            resultados.append({
                "CANDIDATO": candidato,
                "PARTIDOS": " + ".join(partidos_originales),
                "COLUMNAS_SUMADAS": " + ".join(columnas_usadas),
                "VOTOS": votos_total
            })

    return sorted(resultados, key=lambda x: x["VOTOS"], reverse=True)


def tabla_partidos(df_filtrado):
    columnas_posibles = [
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
        "QS",
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
        "OTROS"
    ]

    datos = []
    total = valor_columna_sumada(df_filtrado, ["VOTOS_EMITIDOS", "TOT_VOTOS"])

    for col in columnas_posibles:
        if col in df_filtrado.columns:
            votos = df_filtrado[col].apply(limpiar_numero).sum()

            if votos > 0:
                datos.append({
                    "Partido / Candidatura": col,
                    "Votos": int(votos),
                    "Porcentaje": (votos / total * 100) if total > 0 else 0
                })

    df_tabla = pd.DataFrame(datos)

    if not df_tabla.empty:
        df_tabla = df_tabla.sort_values("Votos", ascending=False)

    return df_tabla


# ===================================================
# ===================================================
# MAPA
# Las funciones del mapa se importan desde visual/mapa.py
# ===================================================

# ===================================================
# ARCHIVOS
# ===================================================

ARCHIVOS_DATOS = {
    ("Ayuntamiento", 2018): "datos/ayuntamiento_2018.csv",
    ("Ayuntamiento", 2021): "datos/ayuntamiento_2021.csv",
    ("Ayuntamiento", 2024): "datos/ayuntamiento_2024.csv",
    ("Gobernatura", 2021): "datos/gobernatura_2021.csv"
}

ARCHIVOS_CANDIDATOS = {
    ("Ayuntamiento", 2018): "candidatos/candidatos_ayuntamiento_2018.csv",
    ("Ayuntamiento", 2021): "candidatos/candidatos_ayuntamiento_2021.csv",
    ("Ayuntamiento", 2024): "candidatos/candidatos_ayuntamiento_2024.csv",
    ("Gobernatura", 2021): "candidatos/candidatos_gobernatura_2021.csv"
}


# ===================================================
# CARGA Y FILTROS
# ===================================================

mostrar_titulo_dashboard()


# -------------------------------
# Filtros principales
# -------------------------------

f_tipo, f_anio = st.columns([1, 1])

with f_tipo:
    tipo_eleccion = st.selectbox(
        "Tipo de elección",
        ["Ayuntamiento", "Gobernatura"],
        key="tipo_eleccion"
    )

with f_anio:
    if tipo_eleccion == "Gobernatura":
        anio = 2021
        st.selectbox("Año", [2021], disabled=True, key="anio_gob")
    else:
        anio = st.selectbox("Año", [2018, 2021, 2024], key="anio_ayun")


df = leer_csv(ARCHIVOS_DATOS[(tipo_eleccion, anio)])
df = preparar_datos(df)

df_candidatos = leer_csv(ARCHIVOS_CANDIDATOS[(tipo_eleccion, anio)])
df_rel = leer_relacion(anio)

df_final = df.merge(
    df_rel,
    on="SECCION",
    how="left",
    suffixes=("", "_REL")
)

distrito = "Todos"
municipio = "Todos"
seccion = "Todos"


# ===================================================
# HEADER ELECCIÓN + FILTROS SECUNDARIOS
# ===================================================

if tipo_eleccion == "Gobernatura":
    h_titulo, h_dist = st.columns([1.2, 3])

    with h_titulo:
        st.markdown(
            f"""
            <div style="display:flex;gap:12px;align-items:center;">
                <div style="font-size:34px;font-weight:900;color:#111;line-height:1;">
                    GOBERNATURA
                </div>
                <div style="background:#cfe3d0;padding:6px 30px;font-size:30px;font-weight:900;color:#173f3a;">
                    {anio}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    distritos_reales = sorted(df_final["DISTRITO_LOCAL"].dropna().unique())

    opciones_distrito = ["Todos"]
    mapa_distritos = {"Todos": "Todos"}

    for d in distritos_reales:
        df_d = df_final[df_final["DISTRITO_LOCAL"] == d]
        municipios_d = df_d["MUNICIPIO"].dropna().unique()

        if len(municipios_d) > 0:
            nombre = str(municipios_d[0])
        else:
            nombre = "DISTRITO"

        etiqueta = f"{nombre} {int(float(d))}"
        opciones_distrito.append(etiqueta)
        mapa_distritos[etiqueta] = d

    with h_dist:
        distrito_label = st.selectbox(
            "Distritos",
            opciones_distrito,
            key="filtro_distrito_gob"
        )

    distrito = mapa_distritos[distrito_label]

    if distrito != "Todos":
        df_final = df_final[df_final["DISTRITO_LOCAL"] == distrito]

else:
    h_titulo, h_mun, h_sec = st.columns([1.2, 1.7, 1.7])

    with h_titulo:
        st.markdown(
            f"""
            <div style="display:flex;gap:12px;align-items:center;">
                <div style="font-size:34px;font-weight:900;color:#111;line-height:1;">
                    AYUNTAMIENTO
                </div>
                <div style="background:#cfe3d0;padding:6px 30px;font-size:30px;font-weight:900;color:#173f3a;">
                    {anio}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    df_ayuntamiento_base = df_final.copy()

    # ===================================================
    # OPCIONES BASE
    # ===================================================

    municipios_base = (
        df_ayuntamiento_base["MUNICIPIO"]
        .dropna()
        .sort_values()
        .unique()
        .tolist()
    )

    opciones_municipio_base = ["Todos"] + municipios_base

    def formato_municipio(valor):
        if valor == "Todos":
            return "🔎 Todos / buscar municipio..."
        return valor

    def formato_seccion(valor):
        if valor == "Todos":
            return "🔎 Todas / buscar sección..."
        return valor

    # ===================================================
    # ESTADO ACTUAL
    # ===================================================

    municipio_actual = st.session_state.get("filtro_municipio", "Todos")
    seccion_actual = st.session_state.get("filtro_seccion", "Todos")

    if municipio_actual not in opciones_municipio_base:
        municipio_actual = "Todos"

    # ===================================================
    # SI HAY SECCIÓN SELECCIONADA, ESA SECCIÓN MANDA
    # ===================================================

    if seccion_actual != "Todos":
        df_seccion_actual = df_ayuntamiento_base[
            df_ayuntamiento_base["SECCION"].astype(int) == int(seccion_actual)
        ].copy()

        municipios_de_seccion = (
            df_seccion_actual["MUNICIPIO"]
            .dropna()
            .sort_values()
            .unique()
            .tolist()
        )

        if municipios_de_seccion:
            municipio_actual = municipios_de_seccion[0]
        else:
            municipio_actual = "Todos"

    # ===================================================
    # FILTRO MUNICIPIO
    # ===================================================

    if seccion_actual != "Todos" and municipio_actual != "Todos":
        opciones_municipio = [municipio_actual]
        index_municipio = 0
        municipio_disabled = True
    else:
        opciones_municipio = opciones_municipio_base
        index_municipio = (
            opciones_municipio.index(municipio_actual)
            if municipio_actual in opciones_municipio
            else 0
        )
        municipio_disabled = False

    with h_mun:
        municipio_seleccionado = st.selectbox(
            "Municipio",
            opciones_municipio,
            index=index_municipio,
            format_func=formato_municipio,
            key="filtro_municipio",
            disabled=municipio_disabled
        )

    municipio = municipio_seleccionado

    # ===================================================
    # FILTRO SECCIÓN
    # Si hay municipio seleccionado, muestra solo secciones de ese municipio.
    # Si municipio es Todos, muestra todas las secciones.
    # ===================================================

    if municipio != "Todos":
        df_para_secciones = df_ayuntamiento_base[
            df_ayuntamiento_base["MUNICIPIO"] == municipio
        ].copy()
    else:
        df_para_secciones = df_ayuntamiento_base.copy()

    secciones_disponibles = (
        df_para_secciones["SECCION"]
        .dropna()
        .astype(int)
        .sort_values()
        .unique()
        .tolist()
    )

    opciones_seccion = ["Todos"] + [
        str(int(seccion_valor)).zfill(4)
        for seccion_valor in secciones_disponibles
    ]

    if seccion_actual not in opciones_seccion:
        seccion_actual = "Todos"

    index_seccion = opciones_seccion.index(seccion_actual)

    with h_sec:
        seccion_seleccionada = st.selectbox(
            "Sección electoral",
            opciones_seccion,
            index=index_seccion,
            format_func=formato_seccion,
            key="filtro_seccion"
        )

    seccion = seccion_seleccionada

    # ===================================================
    # SI SELECCIONÓ UNA SECCIÓN, AJUSTAMOS MUNICIPIO FINAL
    # ===================================================

    if seccion != "Todos":
        df_seccion = df_ayuntamiento_base[
            df_ayuntamiento_base["SECCION"].astype(int) == int(seccion)
        ].copy()

        municipios_de_seccion = (
            df_seccion["MUNICIPIO"]
            .dropna()
            .sort_values()
            .unique()
            .tolist()
        )

        if municipios_de_seccion:
            municipio = municipios_de_seccion[0]

    # ===================================================
    # APLICACIÓN DE FILTROS
    # ===================================================

    df_final = df_ayuntamiento_base.copy()

    if municipio != "Todos":
        df_final = df_final[df_final["MUNICIPIO"] == municipio]

    if seccion != "Todos":
        df_final = df_final[
            df_final["SECCION"].astype(int) == int(seccion)
        ]
df_filtrado = df_final.copy()

if df_filtrado.empty:
    st.error("No hay datos para la selección actual.")
    st.stop()


# ===================================================
# KPIs
# ===================================================

lista_nominal = valor_columna_sumada(df_filtrado, ["LISTA_NOMINAL"])
votos_emitidos = valor_columna_sumada(
    df_filtrado,
    ["VOTOS_EMITIDOS", "VOTOS_EMITIDOS_1", "TOT_VOTOS"]
)
votos_nulos = valor_columna_sumada(df_filtrado, ["VOTOS_NULOS", "NULOS"])
participacion = (votos_emitidos / lista_nominal) * 100 if lista_nominal > 0 else 0

mostrar_kpis(
    lista_nominal=lista_nominal,
    votos_emitidos=votos_emitidos,
    votos_nulos=votos_nulos,
    participacion=participacion
)
# ===================================================
# RESULTADOS
# ===================================================

id_municipio = obtener_id_municipio(df_filtrado)

resultados_calculados = calcular_resultados_candidatos(
    df_filtrado=df_filtrado,
    df_candidatos=df_candidatos,
    tipo_eleccion=tipo_eleccion,
    id_municipio=id_municipio
)

if tipo_eleccion == "Ayuntamiento" and municipio != "Todos" and seccion == "Todos":
    resultados = obtener_top3_final_ayuntamiento(anio, municipio)
else:
    resultados = resultados_calculados

df_partidos = tabla_partidos(df_filtrado)

layout_left, layout_mid, layout_map = st.columns([1.45, 0.95, 1.2])


# ===================================================
# TOP 3
# ===================================================

with layout_left:
    mostrar_top3_candidatos(
        resultados=resultados,
        votos_emitidos=votos_emitidos,
        tipo_eleccion=tipo_eleccion,
        municipio=municipio
    )

# ===================================================
# VOTOS POR PARTIDOS
# ===================================================

with layout_mid:
    mostrar_votos_partidos(
        df_partidos=df_partidos,
        obtener_color_ganador=obtener_color_ganador
    )
# ===================================================
# MAPA
# ===================================================

with layout_map:
    st.markdown("### Mapa electoral")

    geojson_data = cargar_geojson(anio)

    mapa = crear_mapa_secciones(
        geojson_data=geojson_data,
        df_mapa=df_filtrado,
        seccion_seleccionada=seccion,
        obtener_candidato_func=obtener_candidato,
        df_candidatos=df_candidatos,
        tipo_eleccion=tipo_eleccion,
        limpiar_numero_func=limpiar_numero,
    )

    st_folium(
        mapa,
        height=485,
        use_container_width=True,
        returned_objects=[]
    )