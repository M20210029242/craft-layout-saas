"""
╔══════════════════════════════════════════════════════════════════╗
║   CRAFT - Computerized Relative Allocation of Facilities         ║
║   Micro SaaS para Otimização de Layout Industrial                ║
║   Caso de Uso: Padaria com 6 Departamentos                       ║
╚══════════════════════════════════════════════════════════════════╝

Fórmula base:
    CTT = Σ (Fluxo[i][j] × Distância[posição_i][posição_j])

Autor: Engenheiro de Produção / Pesquisa Operacional
"""

import copy
import itertools


# ──────────────────────────────────────────────
# CONFIGURAÇÃO DOS DADOS DO PROBLEMA
# ──────────────────────────────────────────────

DEPARTAMENTOS = ["D1-Insumos", "D2-Masseira", "D3-Bancada",
                 "D4-Fermentação", "D5-Forno", "D6-Expedição"]

# Matriz de Fluxo (De → Para) — fluxos bidirecionais e cruzados
# D2-Masseira e D4-Fermentação têm alto intercâmbio (amassamento + fermentação)
# D4-Fermentação e D5-Forno também têm alto fluxo (pré-assamento)
MATRIZ_FLUXO = [
    [ 0, 15,  2,  0,  0,  0],   # D1-Insumos
    [ 5,  0, 20, 30,  0,  0],   # D2-Masseira  ← forte troca com D4
    [ 0,  8,  0,  5,  0,  0],   # D3-Bancada
    [ 0, 25,  3,  0, 20,  0],   # D4-Fermentação ← forte troca com D2 e D5
    [ 0,  0,  0, 15,  0, 40],   # D5-Forno     ← forte troca com D4
    [ 0,  0,  0,  0, 10,  0],   # D6-Expedição
]

# Matriz de Distâncias baseada em grid 2×3 (layout real de galpão)
# Posições físicas:  [P0] [P1] [P2]
#                    [P3] [P4] [P5]
# Distâncias Manhattan entre posições físicas
MATRIZ_DISTANCIAS = [
    [0, 1, 2, 1, 2, 3],
    [1, 0, 1, 2, 1, 2],
    [2, 1, 0, 3, 2, 1],
    [1, 2, 3, 0, 1, 2],
    [2, 1, 2, 1, 0, 1],
    [3, 2, 1, 2, 1, 0],
]


# ──────────────────────────────────────────────
# FUNÇÃO 1: Cálculo do Custo Total de Transporte
# ──────────────────────────────────────────────

def calcular_custo(layout: list, fluxo: list, distancias: list) -> float:
    """
    Calcula o Custo Total de Transporte (CTT) para um dado layout.

    Args:
        layout     : lista com a ordem dos departamentos nas posições físicas
                     Ex: [0, 1, 2, 3, 4, 5] → Dep0 na pos0, Dep1 na pos1...
        fluxo      : matriz de fluxo entre departamentos
        distancias : matriz de distâncias entre posições físicas

    Returns:
        float : custo total de transporte
    """
    n = len(layout)
    ctt = 0.0

    for i in range(n):
        for j in range(n):
            if fluxo[i][j] > 0:
                # Posição física do departamento i e j no layout atual
                pos_i = layout.index(i)
                pos_j = layout.index(j)
                # Acumula: fluxo × distância física entre as posições
                ctt += fluxo[i][j] * distancias[pos_i][pos_j]

    return ctt


# ──────────────────────────────────────────────
# FUNÇÃO 2: Troca de Dois Departamentos no Layout
# ──────────────────────────────────────────────

def trocar_departamentos(layout: list, i: int, j: int) -> list:
    """
    Gera um novo layout trocando as posições físicas dos departamentos i e j.

    Args:
        layout : layout atual (lista de índices de departamentos)
        i, j   : índices das posições físicas a serem trocadas

    Returns:
        list : novo layout com a troca aplicada
    """
    novo_layout = layout[:]
    novo_layout[i], novo_layout[j] = novo_layout[j], novo_layout[i]
    return novo_layout


# ──────────────────────────────────────────────
# FUNÇÃO 3: Execução do Algoritmo CRAFT
# ──────────────────────────────────────────────

def executar_craft(fluxo: list, distancias: list, departamentos: list) -> dict:
    """
    Executa o algoritmo CRAFT simplificado até convergência.

    Lógica:
        1. Parte do layout inicial (ordem natural: 0, 1, 2, ..., n-1)
        2. Testa todas as trocas de pares de posições
        3. Adota a troca que reduzir mais o custo
        4. Repete até nenhuma troca melhorar o custo

    Args:
        fluxo        : matriz de fluxo entre departamentos
        distancias   : matriz de distâncias entre posições físicas
        departamentos: lista com os nomes dos departamentos

    Returns:
        dict : resultados contendo custo inicial, custo final, layout otimizado
               e histórico de melhorias por iteração
    """
    n = len(departamentos)

    # Layout inicial: departamento k ocupa a posição física k
    layout_atual = list(range(n))
    custo_inicial = calcular_custo(layout_atual, fluxo, distancias)

    print("\n" + "═" * 60)
    print("  CRAFT — Iniciando Otimização de Layout Industrial")
    print("═" * 60)
    print(f"\n  Layout inicial : {[departamentos[d] for d in layout_atual]}")
    print(f"  Custo inicial  : {custo_inicial:.2f}")

    historico = []
    iteracao = 0

    while True:
        iteracao += 1
        melhor_custo = calcular_custo(layout_atual, fluxo, distancias)
        melhor_troca = None
        melhor_layout = layout_atual[:]

        # Testa todas as combinações de trocas de pares (i, j)
        for i, j in itertools.combinations(range(n), 2):
            layout_teste = trocar_departamentos(layout_atual, i, j)
            custo_teste = calcular_custo(layout_teste, fluxo, distancias)

            if custo_teste < melhor_custo:
                melhor_custo = custo_teste
                melhor_troca = (i, j)
                melhor_layout = layout_teste[:]

        custo_antes = calcular_custo(layout_atual, fluxo, distancias)

        if melhor_troca is None:
            # Nenhuma troca melhorou — convergência atingida
            print(f"\n  Iteração {iteracao}: Nenhuma melhoria encontrada. Convergindo.")
            break

        # Aplica a melhor troca encontrada nesta iteração
        i, j = melhor_troca
        reducao = custo_antes - melhor_custo
        print(f"\n  Iteração {iteracao}:")
        print(f"    Troca: posição {i} ({departamentos[layout_atual[i]]}) "
              f"↔ posição {j} ({departamentos[layout_atual[j]]})")
        print(f"    Custo anterior : {custo_antes:.2f}")
        print(f"    Custo após     : {melhor_custo:.2f}  (↓ {reducao:.2f})")

        historico.append({
            "iteracao": iteracao,
            "troca": (departamentos[layout_atual[i]], departamentos[layout_atual[j]]),
            "custo_antes": custo_antes,
            "custo_depois": melhor_custo,
            "reducao": reducao,
        })

        layout_atual = melhor_layout

    custo_final = calcular_custo(layout_atual, fluxo, distancias)
    layout_nomes = [departamentos[d] for d in layout_atual]

    return {
        "custo_inicial": custo_inicial,
        "custo_final": custo_final,
        "reducao_total": custo_inicial - custo_final,
        "percentual_reducao": ((custo_inicial - custo_final) / custo_inicial) * 100,
        "layout_inicial": list(range(n)),
        "layout_otimizado": layout_atual,
        "layout_nomes": layout_nomes,
        "historico": historico,
        "iteracoes": iteracao - 1,
    }


# ──────────────────────────────────────────────
# FUNÇÃO 4: Exibição do Relatório Final
# ──────────────────────────────────────────────

def exibir_relatorio(resultado: dict, departamentos: list) -> None:
    """
    Exibe o relatório final formatado com os resultados da otimização.

    Args:
        resultado    : dicionário retornado por executar_craft()
        departamentos: lista com os nomes dos departamentos
    """
    print("\n" + "═" * 60)
    print("  RELATÓRIO FINAL — CRAFT")
    print("═" * 60)

    print(f"\n  Custo Inicial         : {resultado['custo_inicial']:.2f}")
    print(f"  Melhor Custo Encontrado: {resultado['custo_final']:.2f}")
    print(f"  Redução Total         : {resultado['reducao_total']:.2f}")
    print(f"  Redução Percentual    : {resultado['percentual_reducao']:.1f}%")
    print(f"  Iterações realizadas  : {resultado['iteracoes']}")

    print("\n  Layout Final Otimizado:")
    print("  " + "─" * 50)
    for pos, dep_idx in enumerate(resultado['layout_otimizado']):
        print(f"    Posição {pos + 1} → {departamentos[dep_idx]}")
    print("  " + "─" * 50)

    if resultado['historico']:
        print("\n  Histórico de Melhorias:")
        for h in resultado['historico']:
            print(f"    Iteração {h['iteracao']}: {h['troca'][0]} ↔ {h['troca'][1]}"
                  f"  |  {h['custo_antes']:.0f} → {h['custo_depois']:.0f}"
                  f"  (↓{h['reducao']:.0f})")

    print("\n" + "═" * 60)
    print("  Otimização concluída com sucesso!")
    print("═" * 60 + "\n")


# ──────────────────────────────────────────────
# PONTO DE ENTRADA PRINCIPAL
# ──────────────────────────────────────────────

if __name__ == "__main__":
    resultado = executar_craft(MATRIZ_FLUXO, MATRIZ_DISTANCIAS, DEPARTAMENTOS)
    exibir_relatorio(resultado, DEPARTAMENTOS)
