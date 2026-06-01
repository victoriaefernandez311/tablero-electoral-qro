import json
import copy

import folium


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
    "PAN_PRI": "#005596",
    "PAN_PRI_PRD": "#005596",
    "PRI_PRD": "#00953B",
    "PVEM_MORENA": "#701A1A",
    "INDEPENDIENTE": "#555555",
    "IND": "#555555",
    "OTROS": "#555555",
}


ARCHIVOS_MAPAS = {
    2018: "mapas/secciones_2018.json",
    2021: "mapas/secciones_2021.json",
    2024: "mapas/secciones_2024.json",
}


def normalizar_partido_mapa(valor):
    valor = str(valor).strip().upper()
    valor = valor.replace("-", "_")
    valor = valor.replace("+", "_")
    valor = valor.replace(" ", "_")

    while "__" in valor:
        valor = valor.replace("__", "_")

    return valor
def limpiar_ganador_mapa(valor):
    """
    Limpia el valor del ganador para que no aparezca NaN en el mapa.

    Si viene vacío, NaN o sin dato, lo mostramos como OTROS.
    """

    valor_str = str(valor).strip().upper()

    if valor_str in ["", "NAN", "NONE", "NULL", "SIN DATO", "SIN_DATOS"]:
        return "OTROS"

    return valor

def seccion_a_texto(valor):
    try:
        return str(int(float(valor))).zfill(4)
    except Exception:
        return str(valor).zfill(4)


def cargar_geojson(anio):
    with open(ARCHIVOS_MAPAS[anio], "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def obtener_color_ganador(ganador):
    """
    Devuelve el color para pintar una sección según el ganador.

    - Partidos principales y coaliciones: color propio.
    - Independientes: gris oscuro.
    - Otros / partidos menores / códigos raros: gris oscuro.
    - Valores vacíos o NaN: gris oscuro como OTROS.
    """

    ganador = limpiar_ganador_mapa(ganador)
    ganador_norm = normalizar_partido_mapa(ganador)

    if ganador_norm in ["IND", "INDEPENDIENTE", "OTROS"]:
        return "#555555"

    if ganador_norm in COLORES_PARTIDOS:
        return COLORES_PARTIDOS[ganador_norm]

    return "#555555"
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


def crear_mapa_secciones(
    geojson_data,
    df_mapa,
    seccion_seleccionada,
    obtener_candidato_func,
    df_candidatos,
    tipo_eleccion,
    limpiar_numero_func,
):
    """
    Crea el mapa electoral por secciones.

    Este módulo solo arma la visual del mapa.
    Las funciones de candidatos y limpieza se reciben desde app.py por ahora.
    """

    df_aux = df_mapa.copy()
    df_aux["SECCION_TXT"] = df_aux["SECCION"].apply(seccion_a_texto)

    secciones_visibles = set(df_aux["SECCION_TXT"].unique())

    info_secciones = {}

    for _, row in df_aux.iterrows():
        sec = seccion_a_texto(row["SECCION"])
        ganador = row["1ER_LUGAR"] if "1ER_LUGAR" in row.index else "OTROS"
        ganador = limpiar_ganador_mapa(ganador)

        votos_ganador = 0

        if "1ERO_VOTOS" in row.index:
            votos_ganador = limpiar_numero_func(row["1ERO_VOTOS"])
        elif "VOTOS" in row.index:
            votos_ganador = limpiar_numero_func(row["VOTOS"])

        id_mun = None

        for col in ["CU_MUNICIPIO", "CVE_MUN", "ID_MUNICIPIO"]:
            if col in row.index:
                id_mun = int(limpiar_numero_func(row[col]))
                break

        candidato = obtener_candidato_func(
            df_candidatos=df_candidatos,
            id_municipio=id_mun,
            partido_o_coalicion=ganador,
            tipo_eleccion=tipo_eleccion,
            municipio_todos=False,
        )

        info_secciones[sec] = {
            "GANADOR": ganador,
            "CANDIDATO": candidato,
            "VOTOS_GANADOR": int(votos_ganador),
            "LISTA_NOMINAL": int(limpiar_numero_func(row.get("LISTA_NOMINAL", 0))),
            "VOTOS_EMITIDOS": int(
                limpiar_numero_func(
                    row.get("VOTOS_EMITIDOS", row.get("TOT_VOTOS", 0))
                )
            ),
            "NULOS": int(
                limpiar_numero_func(
                    row.get("VOTOS_NULOS", row.get("NULOS", 0))
                )
            ),
        }

    geojson_filtrado = copy.deepcopy(geojson_data)

    geojson_filtrado["features"] = [
        feature
        for feature in geojson_filtrado["features"]
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

    mapa = folium.Map(
        location=[20.6, -100.4],
        zoom_start=8,
        tiles="cartodbpositron",
    )

    def style_function(feature):
        sec_geo = feature["properties"]["SECCION_TXT"]
        ganador = feature["properties"].get("GANADOR", "OTROS")
        color = obtener_color_ganador(ganador)

        if (
            seccion_seleccionada != "Todos"
            and sec_geo == seccion_a_texto(seccion_seleccionada)
        ):
            return {
                "fillColor": color,
                "color": "#000000",
                "weight": 4,
                "fillOpacity": 0.9,
            }

        return {
            "fillColor": color,
            "color": "#555555",
            "weight": 0.7,
            "fillOpacity": 0.65,
        }

    folium.GeoJson(
        geojson_filtrado,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=[
                "SECCION_TXT",
                "GANADOR",
                "VOTOS_GANADOR",
            ],
            aliases=[
                "Sección:",
                "Ganador:",
                "Votos:",
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
            """,
        ),
    ).add_to(mapa)

    bounds = extraer_bounds_geojson(geojson_filtrado)

    if bounds:
        mapa.fit_bounds(bounds, padding=[12, 12])

    return mapa