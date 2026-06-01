import streamlit as st


def aplicar_estilos():
    """
    Aplica los estilos generales del dashboard electoral.

    Este archivo concentra únicamente CSS y estilos visuales.
    app.py solo debe llamar a esta función.
    """

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

    .first-card { 
        border: 3px solid #d8bb2f; 
        background:#fffbea; 
    }

    .second-card { 
        border: 3px solid #a8abb0; 
        background:#f7f7f7; 
    }

    .third-card { 
        border: 3px solid #d9822b; 
        background:#fff3e8; 
    }

    .result-badge {
        border-radius: 8px;
        padding: 8px;
        font-size: 12px;
        font-weight: 900;
        margin-bottom: 12px;
    }

    .first-badge { 
        background:#d8bb2f; 
        color:#111; 
    }

    .second-badge { 
        background:#a8abb0; 
        color:white; 
    }

    .third-badge { 
        background:#d9822b; 
        color:white; 
    }

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
    /* Buscador interno de los selectbox */
div[data-baseweb="select"] input {
    color: #111 !important;
    background-color: transparent !important;
    caret-color: #111 !important;
}

/* Placeholder / texto del buscador */
div[data-baseweb="select"] input::placeholder {
    color: #555 !important;
    opacity: 1 !important;
}

/* Dropdown abierto */
div[data-baseweb="popover"] {
    background-color: #ffffff !important;
    color: #111 !important;
}

/* Opciones del dropdown */
div[role="option"] {
    color: #111 !important;
    background-color: #ffffff !important;
}

/* Opción al pasar el mouse */
div[role="option"]:hover {
    background-color: #eaf5df !important;
    color: #111 !important;
}

/* Texto dentro del menú desplegable */
div[data-baseweb="menu"] {
    background-color: #ffffff !important;
    color: #111 !important;
}

/* Caja de búsqueda del menú */
div[data-baseweb="menu"] input {
    color: #111 !important;
    caret-color: #111 !important;
}
    </style>
    """, unsafe_allow_html=True)