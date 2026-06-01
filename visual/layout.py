import streamlit as st

from visual.imagenes import obtener_logo_dashboard


def mostrar_titulo_dashboard():
    """
    Muestra el título principal del dashboard con el logo al lado.
    Logo y título quedan más centrados como bloque.
    """

    ruta_logo = obtener_logo_dashboard()

    col_izq, col_logo, col_titulo, col_der = st.columns(
        [1.25, 0.32, 2.2, 1.25]
    )

    with col_logo:
        if ruta_logo is not None:
            st.image(ruta_logo, width=64)

    with col_titulo:
        st.markdown(
            """
            <div style="
                display:flex;
                align-items:center;
                height:64px;
            ">
                <h1 style="
                    font-size:42px;
                    font-weight:900;
                    color:#111;
                    margin:0;
                    letter-spacing:4px;
                    font-family:Arial, sans-serif;
                    white-space:nowrap;
                ">
                    TABLERO ELECTORAL
                </h1>
            </div>
            """,
            unsafe_allow_html=True
        )