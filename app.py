import streamlit as st
import pandas as pd
import itertools

st.title("CRAFT - Otimizacao de Layout Industrial")
st.write("Padaria com 6 departamentos")

nomes = [
    "D1-Insumos", "D2-Masseira", "D3-Bancada",
    "D4-Fermentacao", "D5-Forno", "D6-Expedicao"
]

fluxo_padrao = [
    [ 0, 15,  2,  0,  0,  0],
    [ 5,  0, 20, 30,  0,  0],
    [ 0,  8,  0,  5,  0,  0],
    [ 0, 25,  3,  0, 20,  0],
    [ 0,  0,  0, 15,  0, 40],
    [ 0,  0,  0,  0, 10,  0],
]

dist_padrao = [
    [0, 1, 2, 1, 2, 3],
    [1, 0, 1, 2, 1, 2],
    [2, 1, 0, 3, 2, 1],
    [1, 2, 3, 0, 1, 2],
    [2, 1, 2, 1, 0, 1],
    [3, 2, 1, 2, 1, 0],
]

n = 6

st.subheader("Matriz de Fluxo")
st.dataframe(pd.DataFrame(fluxo_padrao, index=nomes, columns=nomes))

st.subheader("Matriz de Distancias")
st.dataframe(pd.DataFrame(dist_padrao,
    index=[f"P{i}" for i in range(n)],
    columns=[f"P{i}" for i in range(n)]))


def calcular_custo(layout, fluxo, dist):
    ctt = 0
    for i in range(n):
        for j in range(n):
            if fluxo[i][j] > 0:
                pi = layout.index(i)
                pj = layout.index(j)
                ctt += fluxo[i][j] * dist[pi][pj]
    return ctt


def executar_craft(fluxo, dist):
    layout = list(range(n))
    historico = []
    while True:
        melhor_custo = calcular_custo(layout, fluxo, dist)
        melhor_troca = None
        melhor_layout = layout[:]
        for i, j in itertools.combinations(range(n), 2):
            novo = layout[:]
            novo[i], novo[j] = novo[j], novo[i]
            c = calcular_custo(novo, fluxo, dist)
            if c < melhor_custo:
                melhor_custo = c
                melhor_troca = (i, j)
                melhor_layout = novo[:]
        custo_antes = calcular_custo(layout, fluxo, dist)
        if melhor_troca is None:
            break
        historico.append({
            "Troca": f"{nomes[layout[melhor_troca[0]]]} x {nomes[layout[melhor_troca[1]]]}",
            "Custo antes": custo_antes,
            "Custo depois": melhor_custo,
            "Reducao": custo_antes - melhor_custo,
        })
        layout = melhor_layout
    return layout, historico


st.subheader("Executar otimizacao")
if st.button("Otimizar Layout"):
    custo_inicial = calcular_custo(list(range(n)), fluxo_padrao, dist_padrao)
    layout_final, historico = executar_craft(fluxo_padrao, dist_padrao)
    custo_final = calcular_custo(layout_final, fluxo_padrao, dist_padrao)

    col1, col2, col3 = st.columns(3)
    col1.metric("Custo Inicial", custo_inicial)
    col2.metric("Custo Final", custo_final)
    col3.metric("Reducao", f"{((custo_inicial-custo_final)/custo_inicial*100):.1f}%")

    st.subheader("Layout Otimizado")
    for pos, dep in enumerate(layout_final):
        st.write(f"Posicao {pos} -> {nomes[dep]}")

    if historico:
        st.subheader("Historico de trocas")
        st.dataframe(pd.DataFrame(historico))
