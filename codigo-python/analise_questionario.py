# import os
import glob
import textwrap
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# ==============================================================================
# 1. CONFIGURAÇÕES E GABARITO DO QUESTIONÁRIO
# ==============================================================================
URL_PLANILHA = (
    "https://docs.google.com/spreadsheets/d/"
    "1cOSK931Vzqdd6KEfSojSYd84hi-o9Jg7NBarFwThRng"
    "/export?format=csv&gid=1673126086"
)

PASTA_SAIDA = "resultados"
PASTA_GRAFICOS = os.path.join(PASTA_SAIDA, "graficos")

# Gabarito oficial das questões de conhecimento (colunas 2 a 9)
GABARITO = {
    2: "Conferir informações do destinatário",
    3: "Usar autenticação de dois fatores (2FA)",
    4: "Sim",
    5: "Verificar quem enviou e acessar o site oficial diretamente",
    6: "Guardar prints e comprovantes",
    7: "Uma técnica usada por criminosos para tentar roubar informações ou dinheiro.",
    8: "Uma mensagem dizendo que sua conta será bloqueada e pedindo uma ação urgente",
    9: "Localização em tempo real",
}

TEMAS_CURTOS = {
    2: "Q2: Cuidados antes do PIX",
    3: "Q3: Proteção de contas (2FA)",
    4: "Q4: Fontes confiáveis de apps",
    5: "Q5: Conduta com link suspeito",
    6: "Q6: Atitude após cair em golpe",
    7: "Q7: Conceito de Phishing",
    8: "Q8: Sinais de tentativa de golpe",
    9: "Q9: Privacidade nas redes sociais",
}

COR_CORRETA = "#2A9D8F"
COR_INCORRETA = "#E76F51"
COR_DUVIDA = "#E9C46A"
COR_PADRAO = "#3B6E8C"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.edgecolor": "#CCCCCC",
    "axes.linewidth": 0.8,
})


# ==============================================================================
# 2. CARREGAMENTO DOS DADOS (LOCAL OU ONLINE)
# ==============================================================================
def carregar_dados():
    """Lê um CSV local se existir na pasta; senão, lê direto do Google Planilhas."""
    arquivos = [f for f in glob.glob("*.csv") if not f.startswith("tabela_")]
    if arquivos:
        nome = arquivos[0]
        df = pd.read_csv(nome, encoding="utf-8").dropna(how="all")
        return df, f"Arquivo local ({nome})"

    try:
        df = pd.read_csv(URL_PLANILHA).dropna(how="all")
    except Exception as erro:
        raise RuntimeError(
            "Não foi possível acessar a planilha online. "
            "Verifique se ela está compartilhada como 'Qualquer pessoa com o link'."
        ) from erro

    if len(df.columns) < 5:
        raise RuntimeError(
            "A planilha parece estar privada (o Google retornou uma página de login). "
            "Mude o compartilhamento para 'Qualquer pessoa com o link' e tente novamente."
        )

    return df, "Google Planilhas (online)"


# ==============================================================================
# 3. FUNÇÕES AUXILIARES E GRÁFICOS
# ==============================================================================
def quebrar_texto(texto, largura=60):
    return "\n".join(textwrap.wrap(str(texto).strip(), width=largura))


def gerar_grafico_pergunta(serie, idx, titulo, resposta_correta=None):
    dados = serie.dropna().astype(str).str.strip()
    total = len(dados)
    contagem = dados.value_counts()
    porcentagens = (contagem / total) * 100

    cores = []
    for opcao in contagem.index:
        if resposta_correta is not None:
            cores.append(COR_CORRETA if opcao == resposta_correta else COR_INCORRETA)
        else:
            if opcao == "Sim":
                cores.append(COR_CORRETA)
            elif opcao == "Não":
                cores.append(COR_INCORRETA)
            elif "dúvida" in opcao.lower():
                cores.append(COR_DUVIDA)
            else:
                cores.append(COR_PADRAO)

    altura_fig = max(3.2, len(contagem) * 0.85 + 1.5)
    fig, ax = plt.subplots(figsize=(9, altura_fig))

    y_pos = range(len(contagem))
    barras = ax.barh(y_pos, contagem.values, color=cores, height=0.55)

    ax.set_yticks(y_pos)
    ax.set_yticklabels([quebrar_texto(op, 38) for op in contagem.index], fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlabel("Quantidade de Respostas")

    pad_titulo = 28 if resposta_correta is not None else 12
    ax.set_title(
        f"Questão {idx}: {quebrar_texto(titulo, 65)}",
        fontsize=11,
        fontweight="bold",
        loc="left",
        pad=pad_titulo,
    )

    if resposta_correta is not None:
        legenda = [
            Patch(facecolor=COR_CORRETA, label="Resposta Correta"),
            Patch(facecolor=COR_INCORRETA, label="Resposta Incorreta"),
        ]
        ax.legend(
            handles=legenda,
            bbox_to_anchor=(0.0, 1.01),
            loc="lower left",
            ncol=2,
            frameon=False,
            fontsize=9,
        )

    max_val = max(contagem.values, default=1)
    ax.set_xlim(0, max_val * 1.28)
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for barra, qtd in zip(barras, contagem.values):
        pct = (qtd / total) * 100
        ax.text(
            barra.get_width() + (max_val * 0.02),
            barra.get_y() + barra.get_height() / 2,
            f"{qtd} ({pct:.1f}%)",
            va="center",
            fontsize=9.5,
            fontweight="bold" if len(contagem) <= 3 else "normal",
        )

    caminho = os.path.join(PASTA_GRAFICOS, f"{idx:02d}_pergunta.png")
    plt.savefig(caminho, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    return total, contagem, porcentagens


def gerar_grafico_taxa_acertos(taxas_acertos):
    indices = list(taxas_acertos.keys())
    rotulos = [TEMAS_CURTOS[i] for i in indices]
    valores = [taxas_acertos[i] for i in indices]
    media_geral = sum(valores) / len(valores)

    cores = [COR_CORRETA if v >= 70 else (COR_DUVIDA if v >= 50 else COR_INCORRETA) for v in valores]

    fig, ax = plt.subplots(figsize=(9, 5))
    y_pos = range(len(rotulos))
    barras = ax.barh(y_pos, valores, color=cores, height=0.6)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(rotulos, fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 115)
    ax.set_xlabel("Taxa de Acertos (%)")
    ax.set_title(
        "Desempenho Geral: Porcentagem de Acertos por Questão (Q2 a Q9)",
        fontsize=11.5,
        fontweight="bold",
        loc="left",
        pad=14,
    )

    ax.axvline(media_geral, color="#333333", linestyle="--", linewidth=1.2)
    ax.text(
        media_geral + 1.5,
        len(rotulos) - 0.3,
        f"Média: {media_geral:.1f}%",
        color="#333333",
        fontsize=9,
        fontweight="bold",
    )

    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for barra, val in zip(barras, valores):
        ax.text(
            barra.get_width() + 1.5,
            barra.get_y() + barra.get_height() / 2,
            f"{val:.1f}%",
            va="center",
            fontsize=9.5,
            fontweight="bold",
        )

    caminho = os.path.join(PASTA_GRAFICOS, "11_taxa_acerto_por_questao.png")
    plt.savefig(caminho, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def gerar_grafico_pontuacao(pontuacoes):
    contagem = pontuacoes.value_counts().reindex(range(0, 9), fill_value=0)
    media = pontuacoes.mean()
    mediana = pontuacoes.median()

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    x_labels = [f"{i}/8" for i in contagem.index]
    barras = ax.bar(x_labels, contagem.values, color=COR_PADRAO, width=0.6)

    ax.set_xlabel("Pontuação Obtida (Acertos nas 8 questões de conhecimento)")
    ax.set_ylabel("Quantidade de Participantes")
    ax.set_title(
        "Distribuição de Acertos por Participante",
        fontsize=11.5,
        fontweight="bold",
        loc="left",
        pad=22,
    )
    ax.text(
        0,
        1.02,
        f"Média de acertos: {media:.2f} de 8 ({(media/8)*100:.1f}%)  |  Mediana: {mediana:.1f}  |  N = {len(pontuacoes)}",
        transform=ax.transAxes,
        fontsize=9,
        color="#444444",
    )

    max_val = max(contagem.values, default=1)
    ax.set_ylim(0, max_val * 1.25)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for barra, qtd in zip(barras, contagem.values):
        if qtd > 0:
            pct = (qtd / len(pontuacoes)) * 100
            ax.text(
                barra.get_x() + barra.get_width() / 2,
                barra.get_height() + (max_val * 0.02),
                f"{qtd}\n({pct:.1f}%)",
                ha="center",
                va="bottom",
                fontsize=8.5,
            )

    caminho = os.path.join(PASTA_GRAFICOS, "12_distribuicao_notas.png")
    plt.savefig(caminho, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ==============================================================================
# 4. EXECUÇÃO PRINCIPAL
# ==============================================================================
def main():
    os.makedirs(PASTA_GRAFICOS, exist_ok=True)
    df, origem = carregar_dados()
    total_participantes = len(df)

    linhas_relatorio = [
        "======================================================================\n",
        "RELATÓRIO DE RESULTADOS - QUESTIONÁRIO DE SEGURANÇA DIGITAL\n",
        f"Fonte analisada: {origem}\n",
        f"Total de participantes: {total_participantes}\n",
        "======================================================================\n",
    ]
    linhas_tabela_csv = []
    taxas_acertos = {}
    pontuacoes = pd.Series(0, index=df.index)

    for idx in range(1, min(11, len(df.columns))):
        titulo = df.columns[idx]
        serie = df.iloc[:, idx]
        correta = GABARITO.get(idx)

        total, contagem, porcentagens = gerar_grafico_pergunta(
            serie, idx, titulo, resposta_correta=correta
        )

        linhas_relatorio.append(f"\n[Questão {idx}] {titulo} (N={total})\n")
        for opcao, qtd in contagem.items():
            pct = porcentagens[opcao]
            status = ""
            if correta is not None:
                status = " [CORRETA]" if opcao == correta else " [INCORRETA]"
            linhas_relatorio.append(f"  - {opcao}: {qtd} ({pct:.1f}%){status}\n")
            linhas_tabela_csv.append({
                "Questao": f"Q{idx}",
                "Pergunta": titulo,
                "Resposta": opcao,
                "Quantidade": int(qtd),
                "Porcentagem (%)": round(pct, 1),
                "Status": status.strip(" []") if status else "Opiniao/Habito",
            })

        if correta is not None:
            respostas_limpas = serie.fillna("").astype(str).str.strip()
            acertos_questao = (respostas_limpas == correta).astype(int)
            pontuacoes += acertos_questao
            taxas_acertos[idx] = (acertos_questao.sum() / total) * 100

    gerar_grafico_taxa_acertos(taxas_acertos)
    gerar_grafico_pontuacao(pontuacoes)

    linhas_relatorio.extend([
        "\n======================================================================\n",
        "RESUMO DE DESEMPENHO NAS 8 QUESTÕES DE CONHECIMENTO (Q2 a Q9)\n",
        "======================================================================\n",
        f"Média de acertos por participante: {pontuacoes.mean():.2f} de 8 "
        f"({(pontuacoes.mean() / 8) * 100:.1f}%)\n",
        f"Mediana de acertos: {pontuacoes.median():.1f} de 8\n",
        f"Menor nota: {pontuacoes.min()} | Maior nota: {pontuacoes.max()}\n",
    ])

    caminho_txt = os.path.join(PASTA_SAIDA, "relatorio_resultados.txt")
    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.writelines(linhas_relatorio)

    caminho_csv = os.path.join(PASTA_SAIDA, "tabela_resumo.csv")
    pd.DataFrame(linhas_tabela_csv).to_csv(
        caminho_csv, index=False, sep=";", encoding="utf-8-sig"
    )

    # Mostra todo o resumo organizado na própria tela
    print("".join(linhas_relatorio))
    print(f"Arquivos gerados com sucesso dentro da pasta '{PASTA_SAIDA}/'!")


if __name__ == "__main__":
    main()https://www.google.com/url?q=https%3A%2F%2Fdocs.google.com%2Fspreadsheets%2Fd%2F1cOSK931Vzqdd6KEfSojSYd84hi-o9Jg7NBarFwThRng
import os
import glob
import textwrap
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# ==============================================================================
# 1. CONFIGURAÇÕES E GABARITO DO QUESTIONÁRIO
# ==============================================================================
URL_PLANILHA = (
    "https://docs.google.com/spreadsheets/d/"
    "1cOSK931Vzqdd6KEfSojSYd84hi-o9Jg7NBarFwThRng"
    "/export?format=csv&gid=1673126086"
)

PASTA_SAIDA = "resultados"
PASTA_GRAFICOS = os.path.join(PASTA_SAIDA, "graficos")

# Gabarito oficial das questões de conhecimento (colunas 2 a 9)
GABARITO = {
    2: "Conferir informações do destinatário",
    3: "Usar autenticação de dois fatores (2FA)",
    4: "Sim",
    5: "Verificar quem enviou e acessar o site oficial diretamente",
    6: "Guardar prints e comprovantes",
    7: "Uma técnica usada por criminosos para tentar roubar informações ou dinheiro.",
    8: "Uma mensagem dizendo que sua conta será bloqueada e pedindo uma ação urgente",
    9: "Localização em tempo real",
}

TEMAS_CURTOS = {
    2: "Q2: Cuidados antes do PIX",
    3: "Q3: Proteção de contas (2FA)",
    4: "Q4: Fontes confiáveis de apps",
    5: "Q5: Conduta com link suspeito",
    6: "Q6: Atitude após cair em golpe",
    7: "Q7: Conceito de Phishing",
    8: "Q8: Sinais de tentativa de golpe",
    9: "Q9: Privacidade nas redes sociais",
}

COR_CORRETA = "#2A9D8F"
COR_INCORRETA = "#E76F51"
COR_DUVIDA = "#E9C46A"
COR_PADRAO = "#3B6E8C"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.edgecolor": "#CCCCCC",
    "axes.linewidth": 0.8,
})


# ==============================================================================
# 2. CARREGAMENTO DOS DADOS (LOCAL OU ONLINE)
# ==============================================================================
def carregar_dados():
    """Lê um CSV local se existir na pasta; senão, lê direto do Google Planilhas."""
    arquivos = [f for f in glob.glob("*.csv") if not f.startswith("tabela_")]
    if arquivos:
        nome = arquivos[0]
        df = pd.read_csv(nome, encoding="utf-8").dropna(how="all")
        return df, f"Arquivo local ({nome})"

    try:
        df = pd.read_csv(URL_PLANILHA).dropna(how="all")
    except Exception as erro:
        raise RuntimeError(
            "Não foi possível acessar a planilha online. "
            "Verifique se ela está compartilhada como 'Qualquer pessoa com o link'."
        ) from erro

    if len(df.columns) < 5:
        raise RuntimeError(
            "A planilha parece estar privada (o Google retornou uma página de login). "
            "Mude o compartilhamento para 'Qualquer pessoa com o link' e tente novamente."
        )

    return df, "Google Planilhas (online)"


# ==============================================================================
# 3. FUNÇÕES AUXILIARES E GRÁFICOS
# ==============================================================================
def quebrar_texto(texto, largura=60):
    return "\n".join(textwrap.wrap(str(texto).strip(), width=largura))


def gerar_grafico_pergunta(serie, idx, titulo, resposta_correta=None):
    dados = serie.dropna().astype(str).str.strip()
    total = len(dados)
    contagem = dados.value_counts()
    porcentagens = (contagem / total) * 100

    cores = []
    for opcao in contagem.index:
        if resposta_correta is not None:
            cores.append(COR_CORRETA if opcao == resposta_correta else COR_INCORRETA)
        else:
            if opcao == "Sim":
                cores.append(COR_CORRETA)
            elif opcao == "Não":
                cores.append(COR_INCORRETA)
            elif "dúvida" in opcao.lower():
                cores.append(COR_DUVIDA)
            else:
                cores.append(COR_PADRAO)

    altura_fig = max(3.2, len(contagem) * 0.85 + 1.5)
    fig, ax = plt.subplots(figsize=(9, altura_fig))

    y_pos = range(len(contagem))
    barras = ax.barh(y_pos, contagem.values, color=cores, height=0.55)

    ax.set_yticks(y_pos)
    ax.set_yticklabels([quebrar_texto(op, 38) for op in contagem.index], fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlabel("Quantidade de Respostas")

    pad_titulo = 28 if resposta_correta is not None else 12
    ax.set_title(
        f"Questão {idx}: {quebrar_texto(titulo, 65)}",
        fontsize=11,
        fontweight="bold",
        loc="left",
        pad=pad_titulo,
    )

    if resposta_correta is not None:
        legenda = [
            Patch(facecolor=COR_CORRETA, label="Resposta Correta"),
            Patch(facecolor=COR_INCORRETA, label="Resposta Incorreta"),
        ]
        ax.legend(
            handles=legenda,
            bbox_to_anchor=(0.0, 1.01),
            loc="lower left",
            ncol=2,
            frameon=False,
            fontsize=9,
        )

    max_val = max(contagem.values, default=1)
    ax.set_xlim(0, max_val * 1.28)
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for barra, qtd in zip(barras, contagem.values):
        pct = (qtd / total) * 100
        ax.text(
            barra.get_width() + (max_val * 0.02),
            barra.get_y() + barra.get_height() / 2,
            f"{qtd} ({pct:.1f}%)",
            va="center",
            fontsize=9.5,
            fontweight="bold" if len(contagem) <= 3 else "normal",
        )

    caminho = os.path.join(PASTA_GRAFICOS, f"{idx:02d}_pergunta.png")
    plt.savefig(caminho, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    return total, contagem, porcentagens


def gerar_grafico_taxa_acertos(taxas_acertos):
    indices = list(taxas_acertos.keys())
    rotulos = [TEMAS_CURTOS[i] for i in indices]
    valores = [taxas_acertos[i] for i in indices]
    media_geral = sum(valores) / len(valores)

    cores = [COR_CORRETA if v >= 70 else (COR_DUVIDA if v >= 50 else COR_INCORRETA) for v in valores]

    fig, ax = plt.subplots(figsize=(9, 5))
    y_pos = range(len(rotulos))
    barras = ax.barh(y_pos, valores, color=cores, height=0.6)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(rotulos, fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 115)
    ax.set_xlabel("Taxa de Acertos (%)")
    ax.set_title(
        "Desempenho Geral: Porcentagem de Acertos por Questão (Q2 a Q9)",
        fontsize=11.5,
        fontweight="bold",
        loc="left",
        pad=14,
    )

    ax.axvline(media_geral, color="#333333", linestyle="--", linewidth=1.2)
    ax.text(
        media_geral + 1.5,
        len(rotulos) - 0.3,
        f"Média: {media_geral:.1f}%",
        color="#333333",
        fontsize=9,
        fontweight="bold",
    )

    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for barra, val in zip(barras, valores):
        ax.text(
            barra.get_width() + 1.5,
            barra.get_y() + barra.get_height() / 2,
            f"{val:.1f}%",
            va="center",
            fontsize=9.5,
            fontweight="bold",
        )

    caminho = os.path.join(PASTA_GRAFICOS, "11_taxa_acerto_por_questao.png")
    plt.savefig(caminho, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def gerar_grafico_pontuacao(pontuacoes):
    contagem = pontuacoes.value_counts().reindex(range(0, 9), fill_value=0)
    media = pontuacoes.mean()
    mediana = pontuacoes.median()

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    x_labels = [f"{i}/8" for i in contagem.index]
    barras = ax.bar(x_labels, contagem.values, color=COR_PADRAO, width=0.6)

    ax.set_xlabel("Pontuação Obtida (Acertos nas 8 questões de conhecimento)")
    ax.set_ylabel("Quantidade de Participantes")
    ax.set_title(
        "Distribuição de Acertos por Participante",
        fontsize=11.5,
        fontweight="bold",
        loc="left",
        pad=22,
    )
    ax.text(
        0,
        1.02,
        f"Média de acertos: {media:.2f} de 8 ({(media/8)*100:.1f}%)  |  Mediana: {mediana:.1f}  |  N = {len(pontuacoes)}",
        transform=ax.transAxes,
        fontsize=9,
        color="#444444",
    )

    max_val = max(contagem.values, default=1)
    ax.set_ylim(0, max_val * 1.25)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for barra, qtd in zip(barras, contagem.values):
        if qtd > 0:
            pct = (qtd / len(pontuacoes)) * 100
            ax.text(
                barra.get_x() + barra.get_width() / 2,
                barra.get_height() + (max_val * 0.02),
                f"{qtd}\n({pct:.1f}%)",
                ha="center",
                va="bottom",
                fontsize=8.5,
            )

    caminho = os.path.join(PASTA_GRAFICOS, "12_distribuicao_notas.png")
    plt.savefig(caminho, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ==============================================================================
# 4. EXECUÇÃO PRINCIPAL
# ==============================================================================
def main():
    os.makedirs(PASTA_GRAFICOS, exist_ok=True)
    df, origem = carregar_dados()
    total_participantes = len(df)

    linhas_relatorio = [
        "======================================================================\n",
        "RELATÓRIO DE RESULTADOS - QUESTIONÁRIO DE SEGURANÇA DIGITAL\n",
        f"Fonte analisada: {origem}\n",
        f"Total de participantes: {total_participantes}\n",
        "======================================================================\n",
    ]
    linhas_tabela_csv = []
    taxas_acertos = {}
    pontuacoes = pd.Series(0, index=df.index)

    for idx in range(1, min(11, len(df.columns))):
        titulo = df.columns[idx]
        serie = df.iloc[:, idx]
        correta = GABARITO.get(idx)

        total, contagem, porcentagens = gerar_grafico_pergunta(
            serie, idx, titulo, resposta_correta=correta
        )

        linhas_relatorio.append(f"\n[Questão {idx}] {titulo} (N={total})\n")
        for opcao, qtd in contagem.items():
            pct = porcentagens[opcao]
            status = ""
            if correta is not None:
                status = " [CORRETA]" if opcao == correta else " [INCORRETA]"
            linhas_relatorio.append(f"  - {opcao}: {qtd} ({pct:.1f}%){status}\n")
            linhas_tabela_csv.append({
                "Questao": f"Q{idx}",
                "Pergunta": titulo,
                "Resposta": opcao,
                "Quantidade": int(qtd),
                "Porcentagem (%)": round(pct, 1),
                "Status": status.strip(" []") if status else "Opiniao/Habito",
            })

        if correta is not None:
            respostas_limpas = serie.fillna("").astype(str).str.strip()
            acertos_questao = (respostas_limpas == correta).astype(int)
            pontuacoes += acertos_questao
            taxas_acertos[idx] = (acertos_questao.sum() / total) * 100

    gerar_grafico_taxa_acertos(taxas_acertos)
    gerar_grafico_pontuacao(pontuacoes)

    linhas_relatorio.extend([
        "\n======================================================================\n",
        "RESUMO DE DESEMPENHO NAS 8 QUESTÕES DE CONHECIMENTO (Q2 a Q9)\n",
        "======================================================================\n",
        f"Média de acertos por participante: {pontuacoes.mean():.2f} de 8 "
        f"({(pontuacoes.mean() / 8) * 100:.1f}%)\n",
        f"Mediana de acertos: {pontuacoes.median():.1f} de 8\n",
        f"Menor nota: {pontuacoes.min()} | Maior nota: {pontuacoes.max()}\n",
    ])

    caminho_txt = os.path.join(PASTA_SAIDA, "relatorio_resultados.txt")
    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.writelines(linhas_relatorio)

    caminho_csv = os.path.join(PASTA_SAIDA, "tabela_resumo.csv")
    pd.DataFrame(linhas_tabela_csv).to_csv(
        caminho_csv, index=False, sep=";", encoding="utf-8-sig"
    )

    # Mostra todo o resumo organizado na própria tela
    print("".join(linhas_relatorio))
    print(f"Arquivos gerados com sucesso dentro da pasta '{PASTA_SAIDA}/'!")


if __name__ == "__main__":
    main()