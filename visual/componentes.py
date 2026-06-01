import base64
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from visual.imagenes import obtener_logo_partido


PARTIDOS_PRINCIPALES = {
    "PAN",
    "PRI",
    "PRD",
    "PVEM",
    "MORENA",
    "MC",
    "PT",
}
CLAVES_INDEPENDIENTES = {
    "IND",
    "INDEPENDIENTE",
}

CLAVES_EXCLUIDAS = {
    "NULOS",
    "VOTOS_NULOS",
    "VOTO_NULO",
    "CNR",
    "CANDIDATOS_NO_REGISTRADOS",
    "CANDIDATURAS_NO_REGISTRADAS",
}


def normalizar_etiqueta(valor):
    valor = str(valor).strip().upper()
    valor = valor.replace("-", "_")
    valor = valor.replace("+", "_")
    valor = valor.replace(" ", "_")

    while "__" in valor:
        valor = valor.replace("__", "_")

    return valor


def clasificar_partido_visual(partido):
    """
    Regla visual:
    - PAN, PRI, PRD, PVEM, MORENA, MC y PT se muestran separados.
    - IND / INDEPENDIENTE se muestra como INDEPENDIENTE.
    - QI, QS, PQS, PES, RSP, FXM y demás partidos menores se agrupan en OTROS.
    - NULOS / VOTOS_NULOS / CNR no se muestran como partido.
    """

    partido_norm = normalizar_etiqueta(partido)

    if partido_norm in CLAVES_EXCLUIDAS:
        return None

    partes = [p for p in partido_norm.split("_") if p]

    for parte in partes:
        if parte in PARTIDOS_PRINCIPALES:
            return parte

    for parte in partes:
        if parte in CLAVES_INDEPENDIENTES:
            return "INDEPENDIENTE"

    if partido_norm in CLAVES_INDEPENDIENTES:
        return "INDEPENDIENTE"

    return "OTROS"

def preparar_partidos_para_visual(df_partidos):
    """
    Agrupa partidos para la visual:
    principales + independientes + otros.
    Excluye nulos y CNR.
    """

    if df_partidos is None or df_partidos.empty:
        return pd.DataFrame(columns=["Partido / Candidatura", "Votos", "Porcentaje"])

    filas = []

    for _, row in df_partidos.iterrows():
        partido_original = row["Partido / Candidatura"]
        votos = row["Votos"]

        partido_visual = clasificar_partido_visual(partido_original)

        if partido_visual is None:
            continue

        filas.append({
            "Partido / Candidatura": partido_visual,
            "Votos": votos,
        })

    df = pd.DataFrame(filas)

    if df.empty:
        return pd.DataFrame(columns=["Partido / Candidatura", "Votos", "Porcentaje"])

    df = (
        df.groupby("Partido / Candidatura", as_index=False)["Votos"]
        .sum()
        .sort_values("Votos", ascending=False)
    )

    total = df["Votos"].sum()

    df["Porcentaje"] = df["Votos"] / total * 100 if total > 0 else 0

    return df


def convertir_imagen_base64(ruta_imagen):
    """
    Convierte una imagen local a base64 para mostrarla dentro de HTML.
    """

    if ruta_imagen is None:
        return None

    ruta = Path(ruta_imagen)

    if not ruta.exists():
        return None

    extension = ruta.suffix.lower().replace(".", "")

    if extension == "jpg":
        extension = "jpeg"

    with open(ruta, "rb") as archivo:
        imagen_base64 = base64.b64encode(archivo.read()).decode("utf-8")

    return f"data:image/{extension};base64,{imagen_base64}"


def obtener_logo_base64(partido):
    ruta_logo = obtener_logo_partido(partido)
    return convertir_imagen_base64(ruta_logo)


def mostrar_kpis(lista_nominal, votos_emitidos, votos_nulos, participacion):
    """
    Muestra las tarjetas superiores de KPIs.
    """

    k1, k2, k3, k4 = st.columns(4)

    kpis = [
        ("👥", "Lista nominal", lista_nominal),
        ("🗳️", "Votos emitidos", votos_emitidos),
        ("❌", "Votos nulos", votos_nulos),
        ("📊", "Participación", participacion),
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
def construir_bloque_logos_partido(partido):
    """
    Construye el bloque de logos de partido o coalición.

    Ejemplos:
    PAN -> logo PAN
    PRI_PVEM -> logo PRI + logo PVEM
    MORENA_PT_PES -> logo MORENA + logo PT + logo OTROS
    INDEPENDIENTE -> logo IND
    """

    partido_norm = str(partido).strip().upper()
    partido_norm = partido_norm.replace("+", "_")
    partido_norm = partido_norm.replace("-", "_")
    partido_norm = partido_norm.replace(" ", "_")

    while "__" in partido_norm:
        partido_norm = partido_norm.replace("__", "_")

    partes = [p for p in partido_norm.split("_") if p]

    # Si no se pudo separar, usamos el partido completo.
    if not partes:
        partes = [partido_norm]

    logos_html = []

    for parte in partes:
        # Evitar palabras vacías o conectores raros.
        if parte in ["Y", "CON"]:
            continue

        logo_base64 = obtener_logo_base64(parte)

        if logo_base64 is not None:
            logos_html.append(
                f"""
                <img src="{logo_base64}" style="
                    width:28px;
                    height:28px;
                    object-fit:contain;
                    margin:0 3px;
                ">
                """
            )

    if not logos_html:
        return f"""
        <div style="
            font-size:11px;
            font-weight:900;
            color:#333;
            font-family:Arial, sans-serif;
        ">
            {partido}
        </div>
        """

    return f"""
    <div style="
        display:flex;
        justify-content:center;
        align-items:center;
        gap:3px;
        margin-bottom:4px;
    ">
        {''.join(logos_html)}
    </div>
    <div style="
        font-size:11px;
        font-weight:900;
        color:#333;
        font-family:Arial, sans-serif;
    ">
        {partido}
    </div>
    """

def construir_html_tarjeta_top(fila, posicion, votos_emitidos):
    """
    Construye el HTML de una tarjeta del TOP 3.

    En el cuadro grande va la foto del candidato.
    Debajo del nombre va el bloque de partido/coalición con logos.
    """

    estilos = {
        1: ("PRIMER LUGAR", "#d8bb2f", "#fffbea"),
        2: ("SEGUNDO LUGAR", "#a8abb0", "#f7f7f7"),
        3: ("TERCER LUGAR", "#d9822b", "#fff3e8"),
    }

    titulo, color, fondo = estilos[posicion]

    candidato = fila.get("CANDIDATO", "Sin dato")
    partido = fila.get("PARTIDO", fila.get("PARTIDOS", "Sin dato"))
    votos = fila.get("VOTOS", 0)
    porcentaje = fila.get("PORCENTAJE", None)

    if porcentaje is None:
        porcentaje = (votos / votos_emitidos * 100) if votos_emitidos > 0 else 0

    bloque_partido = construir_bloque_logos_partido(partido)

    html_card = f"""
    <div style="
        background:{fondo};
        border:3px solid {color};
        border-radius:14px;
        padding:8px;
        height:520px;
        text-align:center;
        font-family:Arial, sans-serif;
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
            font-family:Arial, sans-serif;
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
            margin-bottom:8px;
            color:#999;
            font-weight:900;
            font-size:12px;
            font-family:Arial, sans-serif;
        ">
            FOTO DEL CANDIDATO
        </div>

        <div style="
            color:#174126;
            font-weight:900;
            font-size:12px;
            line-height:1.1;
            min-height:40px;
            margin-bottom:8px;
            font-family:Arial, sans-serif;
        ">
            {candidato}
        </div>

        <div style="
            background:#f4f1eb;
            border-radius:10px;
            padding:7px;
            margin-bottom:8px;
            min-height:48px;
            display:flex;
            flex-direction:column;
            align-items:center;
            justify-content:center;
            font-family:Arial, sans-serif;
        ">
            {bloque_partido}
        </div>

        <div style="
            background:white;
            border-radius:10px;
            border:1px solid #eee;
            padding:8px;
            font-family:Arial, sans-serif;
        ">
            <div style="font-size:8px;color:#555;font-weight:900;">
                VOTOS TOTALES
            </div>
            <div style="font-size:20px;color:#174126;font-weight:900;">
                {int(votos):,}
            </div>
            <hr style="margin:5px 0;">
            <div style="font-size:8px;color:#555;font-weight:900;">
                PORCENTAJE
            </div>
            <div style="font-size:18px;font-weight:900;">
                {porcentaje:.1f}%
            </div>
        </div>
    </div>
    """

    return html_card

def mostrar_top3_candidatos(resultados, votos_emitidos, tipo_eleccion, municipio):
    """
    Muestra las tarjetas del TOP 3 de candidatos.
    """

    st.markdown("### TOP 3 CANDIDATOS")

    if tipo_eleccion == "Ayuntamiento" and municipio == "Todos":
        st.warning("Seleccione un municipio para ver los candidatos.")
        return

    c1, c2, c3 = st.columns(3)
    cols = [c1, c2, c3]

    for i in range(3):
        if i < len(resultados):
            html_card = construir_html_tarjeta_top(
                fila=resultados[i],
                posicion=i + 1,
                votos_emitidos=votos_emitidos
            )

            with cols[i]:
                components.html(html_card, height=540)


def construir_html_partido(partido, votos, porcentaje, color):
    """
    Construye una tarjeta HTML de partido.
    """

    logo_base64 = obtener_logo_base64(partido)

    if logo_base64 is not None:
        bloque_logo = f"""
        <img src="{logo_base64}" style="
            width:34px;
            height:34px;
            object-fit:contain;
            margin-bottom:4px;
        ">
        """
    else:
        bloque_logo = ""

    html = f"""
    <div style="
        background:white;
        border-radius:14px;
        padding:12px;
        margin-bottom:12px;
        box-shadow:0 3px 8px rgba(0,0,0,0.10);
        height:150px;
        min-height:150px;
        overflow:hidden;
        display:flex;
        flex-direction:column;
        justify-content:space-between;
        box-sizing:border-box;
        font-family:Arial, sans-serif;
    ">
        <div>
            {bloque_logo}
            <div style="
                font-size:12px;
                font-weight:900;
                color:#333;
                line-height:1.1;
                margin-bottom:6px;
                font-family:Arial, sans-serif;
            ">
                {partido}
            </div>
        </div>

        <div>
            <div style="
                font-size:16px;
                font-weight:900;
                color:#111;
                line-height:1.1;
                font-family:Arial, sans-serif;
            ">
                {int(votos):,}
            </div>

            <div style="
                height:10px;
                background:#ddd;
                border-radius:10px;
                margin-top:5px;
            ">
                <div style="
                    height:6px;
                    width:{min(porcentaje,100)}%;
                    background:{color};
                    border-radius:6px;
                "></div>
            </div>

            <div style="
                font-size:17px;
                font-weight:900;
                line-height:1;
                margin-top:9px;
                color:{color};
                font-family:Arial, sans-serif;
            ">
                {porcentaje:.1f}%
            </div>
        </div>
    </div>
    """

    return html


def mostrar_votos_partidos(df_partidos, obtener_color_ganador):
    """
    Muestra las tarjetas de votos por partidos políticos.
    Excluye votos nulos y agrupa partidos menores en OTROS.
    """

    st.markdown("### Votos por partidos políticos")

    df_visual = preparar_partidos_para_visual(df_partidos)

    partidos_mostrar = df_visual.head(6).reset_index(drop=True)

    for i in range(0, len(partidos_mostrar), 2):
        pc1, pc2 = st.columns(2)

        for col_card, idx in zip([pc1, pc2], [i, i + 1]):
            if idx < len(partidos_mostrar):
                row = partidos_mostrar.iloc[idx]

                partido = row["Partido / Candidatura"]
                votos = row["Votos"]
                porcentaje = row["Porcentaje"]
                color = obtener_color_ganador(partido)

                html_card = construir_html_partido(
                    partido=partido,
                    votos=votos,
                    porcentaje=porcentaje,
                    color=color
                )

                with col_card:
                    components.html(html_card, height=165)