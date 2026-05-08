import streamlit as st
import pandas as pd
import unicodedata
import json
import copy
import folium
from streamlit_folium import st_folium
import plotly.express as px
import streamlit.components.v1 as components
st.set_page_config(page_title="Tablero Electoral", layout="wide")

# ===================================================
# ESTILOS DEL DASHBOARD
# ===================================================
st.markdown("""
<style>
.stApp {
    background-color: #eef7e8;
    color: #111;
}

.block-container {
    padding-top: 0rem !important;
    padding-left: 0.8rem !important;
    padding-right: 0.8rem !important;
    padding-bottom: 0rem !important;
    max-width: 100% !important;
    width: 100% !important;
}
/* Filtros claros */
div[data-baseweb="select"] > div {
    background-color: #f4faee !important;
    color: #111 !important;
    border: 1px solid #9fb79d !important;
}

div[data-baseweb="select"] span {
    color: #111 !important;
}

label {
    color: #111 !important;
    font-weight: 800 !important;
    font-size: 12px !important;
}

.stSelectbox {
    background-color: #eaf5df;
}

/* Header */
.main-title {
    font-size: 38px;
    font-weight: 900;
    color: #111;
    line-height: 1;
    margin-top: 0;
}

.year-box {
    background: #cfe3d0;
    padding: 6px 38px;
    font-size: 30px;
    font-weight: 900;
    color: #173f3a;
    text-align: center;
    line-height: 1.1;
}
.stApp {
    background-color: #eef7e8;
    color: #111;
}

.block-container {
    padding-top: 0.4rem;
    padding-left: 0.8rem;
    padding-right: 0.8rem;
    max-width: 100%;
}

.main-title {
    font-size: 38px;
    font-weight: 900;
    color: #111;
    line-height: 1;
    margin-top: 0;
}

.year-box {
    background: #cfe3d0;
    padding: 6px 38px;
    font-size: 30px;
    font-weight: 900;
    color: #173f3a;
    text-align: center;
    line-height: 1.1;
}

.kpi-card {
    background: white;
    border-radius: 10px;
    padding: 12px 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.10);
    height: 62px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.kpi-icon {
    width: 42px;
    height: 42px;
    border-radius: 9px;
    background: #eef3ed;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
}

.kpi-label {
    font-size: 10px;
    font-weight: 900;
    color: #666;
    text-transform: uppercase;
}

.kpi-value {
    font-size: 24px;
    font-weight: 900;
    color: #174126;
}

.result-card {
    background: white;
    border-radius: 14px;
    padding: 12px;
    min-height: 520px;
    height: 520px;
    text-align: center;
}

.first-card { border: 3px solid #d8bb2f; background:#fffbea; }
.second-card { border: 3px solid #a8abb0; background:#f7f7f7; }
.third-card { border: 3px solid #d9822b; background:#fff3e8; }

.result-badge {
    border-radius: 8px;
    padding: 8px;
    font-size: 12px;
    font-weight: 900;
    margin-bottom: 12px;
}

.first-badge { background:#d8bb2f; color:#111; }
.second-badge { background:#a8abb0; color:white; }
.third-badge { background:#d9822b; color:white; }

.candidate-name {
    color:#174126;
    font-weight:900;
    font-size:12px;
    line-height: 1.1;
    min-height:36px;
    margin-top:7px;
}

.party-box {
    background:#f4f1eb;
    border-radius:10px;
    padding:6px;
    margin-top:6px;
    font-weight:800;
    color:#333;
    font-size:12px;
}
.votes-box {
    background:white;
    border-radius:10px;
    border:1px solid #eee;
    padding:14px;
    margin-top:18px;
    min-height:140px;
}

.votes-title {
    font-size:8px;
    color:#555;
    font-weight:900;
}

.votes-number {
    font-size:18px;
    color:#174126;
    font-weight:900;
}

.percent-number {
    font-size:17px;
    font-weight:900;
}

.party-card {
    background:white;
    border-radius:14px;
    padding:14px 14px;
    margin-bottom:12px;
    box-shadow: 0 3px 8px rgba(0,0,0,0.10);

    height:165px;
    min-height:165px;

    overflow:hidden;

    display:flex;
    flex-direction:column;
    justify-content:space-between;
}
.party-name {
    font-size:13px;
    font-weight:900;
    color:#333;
    line-height:1.1;
    margin-bottom:8px;
}

.party-votes {
    font-size:17px;
    font-weight:900;
    color:#111;
    line-height:1.1;
}

.party-percent {
    font-size:18px;
    font-weight:900;
    line-height:1;
    margin-top:10px;
}

.warning-box {
    background:#fff3cd;
    border:1px solid #e3c75f;
    color:#4b3b00;
    padding:18px;
    border-radius:12px;
    font-weight:800;
}
header[data-testid="stHeader"] {
    display: none !important;
}

div[data-testid="stToolbar"] {
    display: none !important;
}

.block-container {
    padding-top: 0rem !important;
}
</style>
""", unsafe_allow_html=True)

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


def obtener_candidato(df_candidatos, id_municipio, partido_o_coalicion, tipo_eleccion, municipio_todos=False):
    if df_candidatos.empty:
        return "Sin candidato cargado"

    if tipo_eleccion == "Ayuntamiento" and municipio_todos:
        return "Varios candidatos municipales"

    partido_norm = normalizar_partido(partido_o_coalicion)

    df_aux = df_candidatos.copy()
    df_aux["PARTIDO_NORM"] = df_aux["PARTIDO_CI"].apply(normalizar_partido)

    if id_municipio is not None and "ID_MUNICIPIO" in df_aux.columns:
        df_aux = df_aux[df_aux["ID_MUNICIPIO"].apply(limpiar_numero) == id_municipio]

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
# CÁLCULO ELECTORAL
# ===================================================

def calcular_resultados_candidatos(df_filtrado, df_candidatos, tipo_eleccion, id_municipio):
    df_cand = df_candidatos.copy()

    if tipo_eleccion == "Ayuntamiento" and id_municipio is not None and "ID_MUNICIPIO" in df_cand.columns:
        df_cand = df_cand[df_cand["ID_MUNICIPIO"].apply(limpiar_numero) == id_municipio]

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
        "PAN", "PRI", "PRD", "MC", "PVEM", "MORENA", "PT", "QI", "PES", "RSP", "FXM", "QS",
        "PRI_PVEM", "PAN_QI", "PAN_QUI", "PAN_PRD", "PAN_PRD_MC",
        "MORENA_PT", "MORENA_PT_PES", "PVEM_MORENA_PT", "PVEM_MORENA",
        "PAN_PRI_PRD", "PAN_PRI", "PAN_PRD", "PRI_PRD",
        "CNR", "NULOS", "VOTOS_NULOS", "OTROS"
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
# MAPA
# ===================================================

COLORES_PARTIDOS = {
    "PAN": "#005596",
    "PRI": "#00953B",
    "MORENA": "#B31934",
    "PRD": "#FFD700",
    "PVEM": "#00A650",
    "MC": "#FF8200",
    "PT": "#E03E2D",
    "PRI_PVEM": "#006B3F",
    "PAN_PRD": "#004B87",
    "MORENA_PT_PES": "#701A1A",
    "PAN_QI": "#005596",
    "PAN_QUI": "#005596",
    "PAN_PRD_MC": "#004B87",
    "MORENA_PT": "#701A1A",
    "PVEM_MORENA_PT": "#701A1A",
    "INDEPENDIENTE": "#808080",
    "OTROS": "#D3D3D3"
}

ARCHIVOS_MAPAS = {
    2018: "mapas/secciones_2018.json",
    2021: "mapas/secciones_2021.json",
    2024: "mapas/secciones_2024.json"
}


def seccion_a_texto(valor):
    try:
        return str(int(float(valor))).zfill(4)
    except:
        return str(valor).zfill(4)


def cargar_geojson(anio):
    with open(ARCHIVOS_MAPAS[anio], "r", encoding="utf-8") as f:
        return json.load(f)


def obtener_color_ganador(ganador):
    ganador_norm = normalizar_partido(ganador)
    return COLORES_PARTIDOS.get(ganador_norm, "#CFCFCF")


def extraer_bounds_geojson(geojson_data):
    lats = []
    lons = []

    def recorrer(coords):
        if isinstance(coords[0], (int, float)):
            lon, lat = coords
            lats.append(lat)
            lons.append(lon)
        else:
            for c in coords:
                recorrer(c)

    for feature in geojson_data["features"]:
        recorrer(feature["geometry"]["coordinates"])

    if not lats or not lons:
        return None

    return [[min(lats), min(lons)], [max(lats), max(lons)]]


def crear_mapa_secciones(geojson_data, df_mapa, seccion_seleccionada, df_candidatos, tipo_eleccion):
    df_aux = df_mapa.copy()
    df_aux["SECCION_TXT"] = df_aux["SECCION"].apply(seccion_a_texto)
    secciones_visibles = set(df_aux["SECCION_TXT"].unique())

    info_secciones = {}

    for _, row in df_aux.iterrows():
        sec = seccion_a_texto(row["SECCION"])
        ganador = row["1ER_LUGAR"] if "1ER_LUGAR" in row.index else "OTROS"

        votos_ganador = 0
        if "1ERO_VOTOS" in row.index:
            votos_ganador = limpiar_numero(row["1ERO_VOTOS"])
        elif "VOTOS" in row.index:
            votos_ganador = limpiar_numero(row["VOTOS"])

        id_mun = None
        for col in ["CU_MUNICIPIO", "CVE_MUN", "ID_MUNICIPIO"]:
            if col in row.index:
                id_mun = int(limpiar_numero(row[col]))
                break

        candidato = obtener_candidato(
            df_candidatos=df_candidatos,
            id_municipio=id_mun,
            partido_o_coalicion=ganador,
            tipo_eleccion=tipo_eleccion,
            municipio_todos=False
        )

        info_secciones[sec] = {
            "GANADOR": ganador,
            "CANDIDATO": candidato,
            "VOTOS_GANADOR": int(votos_ganador),
            "LISTA_NOMINAL": int(limpiar_numero(row.get("LISTA_NOMINAL", 0))),
            "VOTOS_EMITIDOS": int(limpiar_numero(row.get("VOTOS_EMITIDOS", row.get("TOT_VOTOS", 0)))),
            "NULOS": int(limpiar_numero(row.get("VOTOS_NULOS", row.get("NULOS", 0))))
        }

    geojson_filtrado = copy.deepcopy(geojson_data)
    geojson_filtrado["features"] = [
        feature for feature in geojson_filtrado["features"]
        if seccion_a_texto(feature["properties"]["SECCION"]) in secciones_visibles
    ]

    for feature in geojson_filtrado["features"]:
        sec_geo = seccion_a_texto(feature["properties"]["SECCION"])
        info = info_secciones.get(sec_geo, {})

        feature["properties"]["SECCION_TXT"] = sec_geo
        feature["properties"]["GANADOR"] = info.get("GANADOR", "Sin datos")
        feature["properties"]["CANDIDATO"] = info.get("CANDIDATO", "Sin datos")
        feature["properties"]["VOTOS_GANADOR"] = info.get("VOTOS_GANADOR", 0)
        feature["properties"]["LISTA_NOMINAL"] = info.get("LISTA_NOMINAL", 0)
        feature["properties"]["VOTOS_EMITIDOS"] = info.get("VOTOS_EMITIDOS", 0)
        feature["properties"]["NULOS"] = info.get("NULOS", 0)

    mapa = folium.Map(location=[20.6, -100.4], zoom_start=8, tiles="cartodbpositron")

    def style_function(feature):
        sec_geo = feature["properties"]["SECCION_TXT"]
        ganador = feature["properties"].get("GANADOR", "OTROS")
        color = obtener_color_ganador(ganador)

        if seccion_seleccionada != "Todos" and sec_geo == seccion_a_texto(seccion_seleccionada):
            return {
                "fillColor": color,
                "color": "#000000",
                "weight": 4,
                "fillOpacity": 0.9
            }

        return {
            "fillColor": color,
            "color": "#555555",
            "weight": 0.7,
            "fillOpacity": 0.65
        }

    folium.GeoJson(
        geojson_filtrado,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=[
                "SECCION_TXT",
                "GANADOR",
                "VOTOS_GANADOR"
            ],
            aliases=[
                "Sección:",
                "Ganador:",
                "Votos:"
            ],
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 6px;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.15);
                font-size: 10px;
                padding: 4px;
            """
        )
    ).add_to(mapa)

    bounds = extraer_bounds_geojson(geojson_filtrado)
    if bounds:
        mapa.fit_bounds(bounds, padding=[12, 12])

    return mapa


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

st.markdown(
    """
    <h1 style="
        text-align:center;
        font-size:42px;
        font-weight:900;
        color:#111;
        margin:0 0 8px 0;
    ">
        TABLERO ELECTORAL
    </h1>
    """,
    unsafe_allow_html=True
)

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

df_final = df.merge(df_rel, on="SECCION", how="left", suffixes=("", "_REL"))

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
        nombre = df_d["MUNICIPIO"].dropna().iloc[0]
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

    # Formato visual tipo: CADEREYTA DE MONTES 14
    opciones_distrito = ["Todos"]
    mapa_distritos = {"Todos": "Todos"}

    for d in distritos_reales:
        if d == "Todos":
            continue

        df_d = df_final[df_final["DISTRITO_LOCAL"] == d]
        municipios_d = df_d["MUNICIPIO"].dropna().unique()

        if len(municipios_d) > 0:
            nombre = str(municipios_d[0])
        else:
            nombre = "DISTRITO"

        etiqueta = f"{nombre} {int(float(d))}"
        opciones_distrito.append(etiqueta)
        mapa_distritos[etiqueta] = d


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

    municipios = ["Todos"] + sorted(df_final["MUNICIPIO"].dropna().unique())

    if "municipio_mapa" in st.session_state and st.session_state["municipio_mapa"] in municipios:
        indice_municipio = municipios.index(st.session_state["municipio_mapa"])
    else:
        indice_municipio = 0

    with h_mun:
        municipio = st.selectbox(
            "Municipio",
            municipios,
            index=indice_municipio,
            key="filtro_municipio"
        )

    if municipio != "Todos":
        df_final = df_final[df_final["MUNICIPIO"] == municipio]

    secciones = ["Todos"] + sorted(df_final["SECCION"].dropna().unique())

    if "seccion_mapa" in st.session_state and st.session_state["seccion_mapa"] in secciones:
        indice_seccion = secciones.index(st.session_state["seccion_mapa"])
    else:
        indice_seccion = 0

    with h_sec:
        seccion = st.selectbox(
            "Sección electoral",
            secciones,
            index=indice_seccion,
            key="filtro_seccion"
        )

    if seccion != "Todos":
        df_final = df_final[df_final["SECCION"] == seccion]

df_filtrado = df_final.copy()

if df_filtrado.empty:
    st.error("No hay datos para la selección actual.")
    st.stop()

# ===================================================
# KPIs
# ===================================================

lista_nominal = valor_columna_sumada(df_filtrado, ["LISTA_NOMINAL"])
votos_emitidos = valor_columna_sumada(df_filtrado, ["VOTOS_EMITIDOS", "VOTOS_EMITIDOS_1", "TOT_VOTOS"])
votos_nulos = valor_columna_sumada(df_filtrado, ["VOTOS_NULOS", "NULOS"])
participacion = (votos_emitidos / lista_nominal) * 100 if lista_nominal > 0 else 0

k1, k2, k3, k4 = st.columns(4)

kpis = [
    ("👥", "Lista nominal", lista_nominal),
    ("🗳️", "Votos emitidos", votos_emitidos),
    ("❌", "Votos nulos", votos_nulos),
    ("📊", "Participación", participacion)
]

for col, (icono, label, value) in zip([k1, k2, k3, k4], kpis):
    with col:
        valor = f"{value:.2f}%" if label == "Participación" else f"{int(value):,}"

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">{icono}</div>
                <div>
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{valor}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ===================================================
# RESULTADOS
# ===================================================

id_municipio = obtener_id_municipio(df_filtrado)

resultados = calcular_resultados_candidatos(
    df_filtrado=df_filtrado,
    df_candidatos=df_candidatos,
    tipo_eleccion=tipo_eleccion,
    id_municipio=id_municipio
)

df_partidos = tabla_partidos(df_filtrado)

layout_left, layout_mid, layout_map = st.columns([1.45, 0.95, 1.2])
# ===================================================
# TOP 3
# ===================================================

with layout_left:
    st.markdown("### TOP 3 CANDIDATOS")

    if tipo_eleccion == "Ayuntamiento" and municipio == "Todos":
        st.warning("Seleccione un municipio para ver los candidatos.")
    else:
        c1, c2, c3 = st.columns(3)
        cols = [c1, c2, c3]

        clases = [
            ("PRIMER LUGAR", "#d8bb2f", "#fffbea"),
            ("SEGUNDO LUGAR", "#a8abb0", "#f7f7f7"),
            ("TERCER LUGAR", "#d9822b", "#fff3e8")
        ]

        for i in range(3):
            if i < len(resultados):
                r = resultados[i]
                pct = (r["VOTOS"] / votos_emitidos * 100) if votos_emitidos > 0 else 0

                titulo, color, fondo = clases[i]

                html_card = f"""
                <div style="
                    background:{fondo};
                    border:3px solid {color};
                    border-radius:14px;
                    padding:8px;
                    height:520px;
                    text-align:center;
                    font-family:Arial;
                    box-sizing:border-box;
                ">
                    <div style="
                        background:{color};
                        color:#111;
                        border-radius:8px;
                        padding:7px;
                        font-size:11px;
                        font-weight:900;
                        margin-bottom:8px;
                    ">
                        {titulo}
                    </div>

                    <div style="
                        height:170px;
                        background:#f8f8f8;
                        border-radius:10px;
                        border:1px solid #ddd;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        color:#999;
                        font-weight:800;
                        font-size:11px;
                        margin-bottom:8px;
                    ">
                        FOTO
                    </div>

                    <div style="
                        color:#174126;
                        font-weight:900;
                        font-size:12px;
                        line-height:1.1;
                        min-height:40px;
                        margin-bottom:8px;
                    ">
                        {r['CANDIDATO']}
                    </div>

                    <div style="
                        background:#f4f1eb;
                        border-radius:10px;
                        padding:7px;
                        font-weight:800;
                        color:#333;
                        font-size:11px;
                        margin-bottom:8px;
                    ">
                        {r['PARTIDOS']}
                    </div>

                    <div style="
                        background:white;
                        border-radius:10px;
                        border:1px solid #eee;
                        padding:8px;
                    ">
                        <div style="font-size:8px;color:#555;font-weight:900;">
                            VOTOS TOTALES
                        </div>
                        <div style="font-size:20px;color:#174126;font-weight:900;">
                            {int(r['VOTOS']):,}
                        </div>
                        <hr style="margin:5px 0;">
                        <div style="font-size:8px;color:#555;font-weight:900;">
                            PORCENTAJE
                        </div>
                        <div style="font-size:18px;font-weight:900;">
                            {pct:.1f}%
                        </div>
                    </div>
                </div>
                """

                with cols[i]:
                    components.html(html_card, height=540)
# ===================================================
# VOTOS POR PARTIDOS
# ===================================================

with layout_mid:
    st.markdown("### Votos por partidos políticos")

    partidos_mostrar = df_partidos.head(6).reset_index(drop=True)

    for i in range(0, len(partidos_mostrar), 2):
        pc1, pc2 = st.columns(2)

        for col_card, idx in zip([pc1, pc2], [i, i + 1]):
            if idx < len(partidos_mostrar):
                row = partidos_mostrar.iloc[idx]
                partido = row["Partido / Candidatura"]
                votos = row["Votos"]
                pct = row["Porcentaje"]
                color = obtener_color_ganador(partido)

                with col_card:
                    st.markdown(
                        f"""
                        <div class="party-card">
                            <div class="party-name">{partido}</div>
                            <div class="party-votes">{votos:,}</div>
                            <div style="height:10px;background:#ddd;border-radius:10px;margin-top:4px;">
                                <div style="height:6px;width:{min(pct,100)}%;background:{color};border-radius:6px;"></div>
                            </div>
                            <div class="party-percent" style="color:{color};">{pct:.1f}%</div>
                        </div>
                        """,
                        unsafe_allow_html=True
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
        df_candidatos=df_candidatos,
        tipo_eleccion=tipo_eleccion
    )

    st_folium(
        mapa,
        width=520,
        height=445,
        returned_objects=[]
    )