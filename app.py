
import streamlit as st
import pandas as pd
import math

st.set_page_config(
    page_title="Calculadora de Debate",
    page_icon="📊",
    layout="centered"
)

st.title("Calculadora de Debate")
st.caption("Estimación de resultados clasificatorios WSDC y Parlamento Británico")

st.header("Configuración del torneo")

formato = st.selectbox(
    "Formato de debate",
    ["Parlamento Británico", "World Schools"]
)

rc = st.number_input(
    "Rondas clasificatorias",
    min_value=1,
    value=4,
    step=1
)

n = st.number_input(
    "Total de equipos",
    min_value=1,
    value=60,
    step=1
)

ec = st.number_input(
    "Equipos que clasifican",
    min_value=1,
    max_value=int(n),
    value=min(8, int(n)),
    step=1
)

if st.button("Calcular resultados", type="primary"):

    if formato == "World Schools":
        puntos = [0, 1]
        divisor = 2 ** rc
        nombre = "victorias"

    else:
        puntos = [0, 1, 2, 3]
        divisor = 4 ** rc
        nombre = "puntos"

    # Construcción del polinomio mediante coeficientes
    lista_piso = [1]

    for ronda in range(rc):
        nueva_lista = [0] * (len(lista_piso) + max(puntos))

        for i, valor in enumerate(lista_piso):
            for p in puntos:
                nueva_lista[i+p] += valor

        lista_piso = nueva_lista

    # Distribución estimada
    lista_equipos = [
        valor * n / divisor
        for valor in lista_piso
    ]

    # Tabla de distribución
    datos = []

    for i, valor in enumerate(lista_equipos):

        if math.isclose(valor, round(valor)):
            intervalo = str(round(valor))
        else:
            intervalo = (
                f"Entre {math.floor(valor)} y "
                f"{math.ceil(valor)}"
            )

        datos.append({
            "Puntaje": f"{i} {nombre}",
            "Equipos estimados": round(valor, 2),
            "Intervalo": intervalo
        })

    st.header("Distribución de equipos")

    df = pd.DataFrame(datos)
    st.dataframe(df, hide_index=True, use_container_width=True)

    # Cálculo del corte
    acumulado = 0

    for i, valor in enumerate(lista_equipos[::-1]):
        acumulado += valor

        if acumulado >= ec:
            corte = len(lista_equipos) - 1 - i
            break

    equipos_superiores = sum(lista_equipos[corte+1:])
    equipos_corte = lista_equipos[corte]

    cupos_restantes = ec - equipos_superiores

    porcentaje = cupos_restantes / equipos_corte * 100

    # Resultados
    st.header("Resultados de clasificación")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Puntaje de corte",
            f"{corte} {nombre}"
        )

    with col2:
        st.metric(
            "Equipos en el corte",
            f"{equipos_corte:.2f}"
        )

    st.metric(
        "Probabilidad estimada de clasificar en el corte",
        f"{porcentaje:.2f}%"
    )

    st.subheader("Distribución visual")

    grafico = pd.DataFrame({
        "Equipos estimados": lista_equipos
    }, index=[
        f"{i} {nombre}" for i in range(len(lista_equipos))
    ])

    st.bar_chart(grafico)

    st.caption(
        "Los resultados son estimaciones basadas en una "
        "distribución uniforme e independiente de los resultados."
    )
