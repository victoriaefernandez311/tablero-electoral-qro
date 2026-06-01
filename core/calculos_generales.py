from core.limpieza import limpiar_numero


def valor_columna_sumada(df, columnas):
    """
    Busca la primera columna disponible dentro de una lista de posibles nombres
    y suma sus valores numéricos.

    Ejemplo:
    valor_columna_sumada(df, ["VOTOS_EMITIDOS", "TOT_VOTOS"])
    """

    for col in columnas:
        if col in df.columns:
            return df[col].apply(limpiar_numero).sum()

    return 0


def calcular_kpis_generales(df):
    """
    Calcula los KPIs principales del tablero:
    - Lista nominal
    - Votos emitidos
    - Votos nulos
    - Participación
    """

    lista_nominal = valor_columna_sumada(
        df,
        ["LISTA_NOMINAL"]
    )

    votos_emitidos = valor_columna_sumada(
        df,
        ["VOTOS_EMITIDOS", "VOTOS_EMITIDOS_1", "TOT_VOTOS"]
    )

    votos_nulos = valor_columna_sumada(
        df,
        ["VOTOS_NULOS", "NULOS"]
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


def obtener_id_municipio(df):
    """
    Devuelve el número de municipio que se debe usar para buscar candidatos.

    Prioridad:
    1. NUM_MUN_OFICIAL: número oficial del municipio.
    2. ID_MUNICIPIO: si el archivo lo trae.
    3. CU_MUNICIPIO: alternativa.
    4. CVE_MUN: último recurso, porque puede ser un código interno.
    """

    columnas_posibles = [
        "NUM_MUN_OFICIAL",
        "ID_MUNICIPIO",
        "CU_MUNICIPIO",
        "CVE_MUN",
    ]

    for col in columnas_posibles:
        if col in df.columns:
            valores = df[col].dropna().unique()

            if len(valores) == 1:
                return int(limpiar_numero(valores[0]))

    return None


def formatear_entero(valor):
    """
    Formatea valores enteros con separador de miles.
    """

    return f"{int(valor):,}"


def formatear_porcentaje(valor, decimales=2):
    """
    Formatea valores porcentuales.
    """

    return f"{valor:.{decimales}f}%"