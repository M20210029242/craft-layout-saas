"""
Interface Streamlit para o algoritmo CRAFT
Otimização de Layout Industrial — Padaria
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from craft_bakery import calcular_custo, executar_craft

# ──────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="CRAFT — Otimização de Layout",
    page_icon="🏭",
    layout="wide",
)

st.title("🏭 CRAFT — Otimização de Layout Industrial")
st.caption("Computerized Relative Allocation of Facilities Technique | Padaria")

# ──────────────────────────────────────────────
# DADOS PADRÃO
# ──────────────────────────────────────────────

DEPARTAMENTOS_PADRAO = [
    "D1-Insumos", "D2-Masseira", "D3-Bancada",
    "D4-Fermentação", "D5-Forno", "D6-Expedição"
]

FLUXO_PADRAO = [
    [ 0, 15,  2,  0,  0,  0],
    [ 5,  0, 20, 30,  0,  0],
    [ 0,  8,  0,  5,  0,  0],
    [ 0, 25,  3,  0, 20,  0],
    [ 0,  0,  0, 15,  0, 40],
    [ 0,  0,  0,  0, 10,  0],
]

DIST_PADRAO = [
    [0, 1, 2, 1, 2, 3],
    [1, 0, 1, 2, 1, 2],
    [2, 1, 0, 3, 2, 1],
    [1, 2, 3, 0, 1, 2],
    [2, 1, 2, 1, 0, 1],
    [3, 2, 1, 2, 1, 0],
]

# ──────────────────────────────────────────────
# SIDEBAR — EDIÇÃO DAS MATRIZES
# ──────────────────────────────────────────────

st.sidebar.header("⚙️ Configurações")
st.sidebar.markdown("Edite as matrizes e clique em **Otimizar**.")

# Nomes dos departamentos
st.sidebar.subheader("Departamentos")
nomes = []
for i, d in enumerate(DEPARTAMENTOS_PADRAO):
    nome = st.sidebar.text_input(f"Dep. {i+1}", value=d, key=f"dep_{i}")
    nomes.append(nome)

n = len(nomes)

# Matriz de Fluxo editável
st.sidebar.subheader("Matriz de Fluxo")
fluxo = []
for i in range(n):
    linha = []
    cols = st.sidebar.columns(n)
    for j in range(n):
        val = cols[j].number_input(
            f"{i}→{j}", min_value=0, value=FLUXO_PADRAO[i][j],
            key=f"f_{i}_{j}", label_visibility="collapsed"
        )
        linha.append(int(val))
    fluxo.append(linha)

# Matriz de Distâncias editável
st.sidebar.subheader("Matriz de Distâncias")
dist = []
for i in range(n):
    linha = []
    cols = st.sidebar.columns(n)
    for j in range(n):
        val = cols[j].number_input(
            f"{i}-{j}", min_value=0, value=DIST_PADRAO[i][j],
            key=f"d_{i}_{j}", label_visibility="collapsed"
        )
        linha.append(int(val))
    dist.append(linha)

# ──────────────────────────────────────────────
# BOTÃO DE EXECUÇÃO
# ──────────────────────────────────────────────

executar = st.sidebar.button("🚀 Otimizar Layout", use_container_width=True, type="primary")

# ──────────────────────────────────────────────
# EXIBIÇÃO DAS MATRIZES (área principal)
# ──────────────────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Matriz de Fluxo")
    df_fluxo = pd.DataFrame(fluxo, index=nomes, columns=nomes)
    st.dataframe(df_fluxo, use_container_width=True)

with col2:
    st.subheader("📏 Matriz de Distâncias")
    df_dist = pd.DataFrame(dist, index=[f"P{i}" for i in range(n)],
                           columns=[f"P{i}" for i in range(n)])
    st.dataframe(df_dist, use_container_width=True)

st.divider()

# ──────────────────────────────────────────────
# RESULTADO DA OTIMIZAÇÃO
# ──────────────────────────────────────────────

if executar:
    with st.spinner("Executando algoritmo CRAFT..."):
        resultado = executar_craft(fluxo, dist, nomes)

    # Métricas principais
    st.subheader("📈 Resultado da Otimização")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Custo Inicial (CTT)", f"{resultado['custo_inicial']:.0f}")
    m2.metric("Melhor Custo (CTT)", f"{resultado['custo_final']:.0f}",
              delta=f"-{resultado['reducao_total']:.0f}", delta_color="inverse")
    m3.metric("Redução", f"{resultado['percentual_reducao']:.1f}%")
    m4.metric("Iterações", resultado['iteracoes'])

    st.divider()

    # Layout inicial vs otimizado
    col_a, col_b = st.columns(2)

    def montar_grid(layout_ids, nomes, titulo):
        """Gera figura Plotly com o grid 2×3 do galpão."""
        cores = ["#B5D4F4","#CECBF6","#C0DD97","#FAC775","#F5C4B3","#9FE1CB"]
        fig = go.Figure()
        posicoes = [(col, row) for row in range(2) for col in range(3)]

        for pos_idx, dep_idx in enumerate(layout_ids):
            x, y = posicoes[pos_idx]
            cor = cores[dep_idx]
            fig.add_shape(type="rect",
                x0=x, y0=y, x1=x+0.9, y1=y+0.8,
                fillcolor=cor, line=dict(color="#888", width=1.5),
                layer="below"
            )
            fig.add_annotation(
                x=x+0.45, y=y+0.5,
                text=f"<b>P{pos_idx}</b>",
                showarrow=False, font=dict(size=10, color="#555")
            )
            fig.add_annotation(
                x=x+0.45, y=y+0.25,
                text=nomes[dep_idx],
                showarrow=False, font=dict(size=11, color="#222")
            )

        fig.update_layout(
            title=titulo,
            xaxis=dict(range=[-0.1, 3.1], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[-0.1, 1.9], showgrid=False, zeroline=False, showticklabels=False),
            height=280, margin=dict(l=10, r=10, t=40, b=10),
            plot_bgcolor="white", paper_bgcolor="white"
        )
        return fig

    with col_a:
        st.subheader("Layout Inicial")
        fig_ini = montar_grid(resultado['layout_inicial'], nomes, "Antes da otimização")
        st.plotly_chart(fig_ini, use_container_width=True)

    with col_b:
        st.subheader("Layout Otimizado ✅")
        fig_opt = montar_grid(resultado['layout_otimizado'], nomes, "Após CRAFT")
        st.plotly_chart(fig_opt, use_container_width=True)

    st.divider()

    # Histórico de iterações
    if resultado['historico']:
        st.subheader("🔄 Histórico de Trocas")
        rows = []
        for h in resultado['historico']:
            rows.append({
                "Iteração": h['iteracao'],
                "Troca realizada": f"{h['troca'][0]}  ↔  {h['troca'][1]}",
                "Custo antes": h['custo_antes'],
                "Custo depois": h['custo_depois'],
                "Redução": h['reducao'],
            })
        df_hist = pd.DataFrame(rows)
        st.dataframe(df_hist, use_container_width=True, hide_index=True)

        # Gráfico de evolução do custo
        custos = [resultado['custo_inicial']] + [h['custo_depois'] for h in resultado['historico']]
        labels = ["Inicial"] + [f"Iter. {h['iteracao']}" for h in resultado['historico']]

        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=labels, y=custos, mode="lines+markers+text",
            text=[str(c) for c in custos], textposition="top center",
            line=dict(color="#185FA5", width=2.5),
            marker=dict(size=10, color="#185FA5")
        ))
        fig_line.update_layout(
            title="Evolução do Custo Total de Transporte (CTT)",
            xaxis_title="Iteração", yaxis_title="CTT",
            height=300, plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(gridcolor="#eee"), margin=dict(t=50, b=40)
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # Layout final detalhado
    st.subheader("📋 Layout Final — Posição por Departamento")
    rows_layout = []
    for pos, dep_idx in enumerate(resultado['layout_otimizado']):
        rows_layout.append({"Posição física": f"P{pos}", "Departamento": nomes[dep_idx]})
    st.dataframe(pd.DataFrame(rows_layout), use_container_width=True, hide_index=True)

else:
    st.info("👈 Ajuste as matrizes na barra lateral e clique em **Otimizar Layout** para iniciar.")
    st.markdown("""
    ### Como usar
    1. **Edite os nomes** dos departamentos na barra lateral (opcional)
    2. **Ajuste a Matriz de Fluxo** — quantos movimentos ocorrem entre cada par de departamentos
    3. **Ajuste a Matriz de Distâncias** — distância física entre cada par de posições no galpão
    4. Clique em **🚀 Otimizar Layout**
    5. Veja o layout antes e depois, a redução de custo e o histórico de trocas

    ### Fórmula
    > **CTT = Σ (Fluxo × Distância)**
    """)
