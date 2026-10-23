from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------- CONFIGURAÇÃO E DESIGN ----------------
st.set_page_config(
    page_title="Orçamento 360 | Análise Orçamentária",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background: #0b1120; color: #e5e7eb; }
    [data-testid="stSidebar"] { background: #101a2c; border-right: 1px solid #263449; }
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #142238, #101a2c);
        border: 1px solid #293b55; padding: 18px; border-radius: 14px;
    }
    [data-testid="stMetricLabel"] { color: #9fb0c7; }
    [data-testid="stMetricValue"] { color: #f8fafc; }
    h1, h2, h3 { color: #f8fafc; }
    div[data-testid="stDataFrame"] { border: 1px solid #293b55; border-radius: 10px; }
    .subtitle { color: #9fb0c7; margin-top: -10px; }
    .small-note { color: #9fb0c7; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

ROOT = Path(__file__).parent
ORIGINAIS = ROOT / "dados_originais"
TRATADOS = ROOT / "dados_tratados"

def brl(valor):
    try:
        s = f"{float(valor):,.2f}"
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {s}"
    except (ValueError, TypeError):
        return "—"

def carregar_arquivo(arquivo):
    nome = arquivo.name.lower()
    if nome.endswith((".xlsx", ".xls")):
        excel = pd.ExcelFile(arquivo)
        aba = "Relatório de Despesas com Tecno" if "Relatório de Despesas com Tecno" in excel.sheet_names else excel.sheet_names[0]
        return pd.read_excel(arquivo, sheet_name=aba)
    if nome.endswith(".csv"):
        try:
            return pd.read_csv(arquivo, sep=None, engine="python", encoding="utf-8-sig")
        except UnicodeDecodeError:
            arquivo.seek(0)
            return pd.read_csv(arquivo, sep=None, engine="python", encoding="latin-1")
    raise ValueError("Formato não suportado. Use Excel (.xlsx/.xls) ou CSV.")

def converter_numero(valor):
    if pd.isna(valor):
        return pd.NA
    if isinstance(valor, (int, float)):
        return valor
    texto = str(valor).strip().replace("R$", "").replace("\u00a0", "").replace(" ", "")
    if not texto:
        return pd.NA
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return pd.NA

@st.cache_data(show_spinner=False)
def limpar_dados(df_entrada):
    df = df_entrada.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for coluna in df.select_dtypes(include="object").columns:
        df[coluna] = df[coluna].map(lambda x: x.strip() if isinstance(x, str) else x)
    for col in ["Projeto de Lei", "Empenhado", "Liquidado", "Pago"]:
        if col in df.columns:
            df[col] = df[col].map(converter_numero)
    if "Ano" in df.columns:
        df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce")
    return df

st.sidebar.markdown("# 📊 ORÇAMENTO **360**")
st.sidebar.caption("INTELLIGENCE • ANÁLISE ORÇAMENTÁRIA")
st.sidebar.markdown("---")
st.sidebar.markdown("### 1. Seus dados")
arquivo_upload = st.sidebar.file_uploader(
    "Envie a planilha de orçamento",
    type=["xlsx", "xls", "csv"],
    help="A planilha será lida nesta sessão. Para publicar com dados disponíveis a todos, inclua apenas dados públicos/autorizados no repositório."
)

df_bruto = None
origem_dados = None
if arquivo_upload is not None:
    try:
        df_bruto = carregar_arquivo(arquivo_upload)
        origem_dados = f"Arquivo enviado: {arquivo_upload.name}"
    except Exception as erro:
        st.sidebar.error(f"Não consegui ler o arquivo: {erro}")
else:
    candidatos = [
        TRATADOS / "orcamento_tratado.csv",
        ORIGINAIS / "Orcamento.xlsx",
        ORIGINAIS / "Orcamento.csv",
    ]
    for caminho in candidatos:
        if caminho.exists():
            try:
                df_bruto = carregar_arquivo(caminho)
                origem_dados = f"Arquivo do projeto: {caminho.name}"
                break
            except Exception as erro:
                st.sidebar.warning(f"Falha ao abrir {caminho.name}: {erro}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 2. Menu")
pagina = st.sidebar.radio(
    "Escolha uma área",
    ["Visão geral", "Órgãos", "Categorias", "Grupos de despesa", "Fontes", "Explorar dados"],
    format_func=lambda x: {
        "Visão geral": "🏠  Visão geral",
        "Órgãos": "🏛️  Órgãos",
        "Categorias": "🍩  Categorias",
        "Grupos de despesa": "🧩  Grupos de despesa",
        "Fontes": "🗂️  Fontes",
        "Explorar dados": "🔎  Explorar dados",
    }[x],
)
st.sidebar.markdown("---")
st.sidebar.caption("Projeto educacional de ETL • Python + Pandas + Plotly + Streamlit")

st.title("Orçamento 360")
st.markdown('<p class="subtitle">Painel de inteligência para explorar despesas orçamentárias.</p>', unsafe_allow_html=True)

if df_bruto is None:
    st.info(
        "Para começar, envie sua planilha pelo menu à esquerda. "
        "Ou coloque `Orcamento.xlsx` em `dados_originais/` ou `orcamento_tratado.csv` em `dados_tratados/`."
    )
    st.markdown("### O que este dashboard terá")
    c1, c2, c3 = st.columns(3)
    c1.metric("Indicadores", "KPIs", "Pago • Empenhado • Liquidado")
    c2.metric("Visualizações", "6 áreas", "Menu interativo")
    c3.metric("Publicação", "Web", "GitHub + Streamlit")
    st.stop()

df = limpar_dados(df_bruto)
if "Pago" not in df.columns:
    st.error("Não encontrei a coluna obrigatória `Pago`. Confira o nome das colunas da planilha.")
    st.write("Colunas encontradas:", df.columns.tolist())
    st.stop()

# Filtros globais
with st.expander("🎛️ Filtros do painel", expanded=True):
    f1, f2 = st.columns(2)
    if "Ano" in df.columns and df["Ano"].notna().any():
        anos = sorted(df["Ano"].dropna().unique().tolist())
        anos_escolhidos = f1.multiselect("Ano", anos, default=anos, format_func=lambda x: str(int(x)) if float(x).is_integer() else str(x))
    else:
        anos_escolhidos = None
        f1.caption("Coluna Ano não disponível.")
    if "Órgão" in df.columns:
        orgaos = sorted(df["Órgão"].dropna().astype(str).unique().tolist())
        orgaos_escolhidos = f2.multiselect("Órgão", orgaos, default=orgaos)
    else:
        orgaos_escolhidos = None
        f2.caption("Coluna Órgão não disponível.")

filtrado = df.copy()
if anos_escolhidos is not None:
    filtrado = filtrado[filtrado["Ano"].isin(anos_escolhidos)]
if orgaos_escolhidos is not None:
    filtrado = filtrado[filtrado["Órgão"].astype(str).isin(orgaos_escolhidos)]

# Indicadores
total_pago = filtrado["Pago"].fillna(0).sum()
total_empenhado = filtrado["Empenhado"].fillna(0).sum() if "Empenhado" in filtrado.columns else None
total_liquidado = filtrado["Liquidado"].fillna(0).sum() if "Liquidado" in filtrado.columns else None
qtd_orgaos = filtrado["Órgão"].nunique() if "Órgão" in filtrado.columns else None

if pagina == "Visão geral":
    st.subheader("Painel executivo")
    kpis = st.columns(4)
    kpis[0].metric("Total pago", brl(total_pago))
    kpis[1].metric("Total empenhado", brl(total_empenhado) if total_empenhado is not None else "Sem coluna")
    kpis[2].metric("Total liquidado", brl(total_liquidado) if total_liquidado is not None else "Sem coluna")
    kpis[3].metric("Órgãos distintos", f"{qtd_orgaos:,}".replace(",", ".") if qtd_orgaos is not None else "Sem coluna")

    left, right = st.columns((1.4, 1))
    if "Órgão" in filtrado.columns:
        orgao_sum = filtrado.groupby("Órgão", as_index=False)["Pago"].sum().sort_values("Pago", ascending=False).head(10).sort_values("Pago")
        fig = px.bar(orgao_sum, x="Pago", y="Órgão", orientation="h", title="Top 10 órgãos por valor pago", template="plotly_dark", color="Pago", color_continuous_scale="Blues")
        fig.update_layout(height=470, coloraxis_showscale=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        left.plotly_chart(fig, use_container_width=True)
    if "Categoria Econômica" in filtrado.columns:
        cat = filtrado.groupby("Categoria Econômica", as_index=False)["Pago"].sum().sort_values("Pago", ascending=False)
        fig = px.pie(cat, names="Categoria Econômica", values="Pago", hole=.55, title="Distribuição por categoria econômica", template="plotly_dark")
        fig.update_layout(height=470, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        right.plotly_chart(fig, use_container_width=True)
    if "Ano" in filtrado.columns:
        anual = filtrado.dropna(subset=["Ano"]).groupby("Ano", as_index=False)["Pago"].sum().sort_values("Ano")
        if len(anual) > 1:
            fig = px.line(anual, x="Ano", y="Pago", markers=True, title="Evolução anual do valor pago", template="plotly_dark")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

elif pagina == "Órgãos":
    st.subheader("🏛️ Análise por órgão")
    if "Órgão" not in filtrado.columns:
        st.warning("A planilha não contém a coluna `Órgão`.")
    else:
        resumo = filtrado.groupby("Órgão", as_index=False)["Pago"].sum().sort_values("Pago", ascending=False)
        fig = px.bar(resumo.head(20).sort_values("Pago"), x="Pago", y="Órgão", orientation="h", title="Até 20 órgãos por valor pago", template="plotly_dark", color="Pago", color_continuous_scale="Blues")
        fig.update_layout(height=max(450, min(850, len(resumo.head(20))*32)), coloraxis_showscale=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(resumo, use_container_width=True, hide_index=True)

elif pagina == "Categorias":
    st.subheader("🍩 Categorias econômicas")
    if "Categoria Econômica" not in filtrado.columns:
        st.warning("A planilha não contém a coluna `Categoria Econômica`.")
    else:
        resumo = filtrado.groupby("Categoria Econômica", as_index=False)["Pago"].sum().sort_values("Pago", ascending=False)
        a, b = st.columns(2)
        fig = px.pie(resumo, names="Categoria Econômica", values="Pago", hole=.48, title="Participação por categoria", template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        a.plotly_chart(fig, use_container_width=True)
        fig2 = px.bar(resumo, x="Categoria Econômica", y="Pago", title="Valor pago por categoria", template="plotly_dark")
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        b.plotly_chart(fig2, use_container_width=True)
        st.dataframe(resumo, use_container_width=True, hide_index=True)

elif pagina == "Grupos de despesa":
    st.subheader("🧩 Grupos e elementos de despesa")
    coluna = "Grupo Despesa" if "Grupo Despesa" in filtrado.columns else ("Elemento Despesa" if "Elemento Despesa" in filtrado.columns else None)
    if coluna is None:
        st.warning("Não encontrei `Grupo Despesa` nem `Elemento Despesa`.")
    else:
        resumo = filtrado.groupby(coluna, as_index=False)["Pago"].sum().sort_values("Pago", ascending=False)
        fig = px.treemap(resumo, path=[coluna], values="Pago", title=f"Participação por {coluna.lower()}", template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(resumo, use_container_width=True, hide_index=True)

elif pagina == "Fontes":
    st.subheader("🗂️ Análise por fonte de recursos")
    if "Fonte" not in filtrado.columns:
        st.warning("A planilha não contém a coluna `Fonte`.")
    else:
        resumo = filtrado.groupby("Fonte", as_index=False)["Pago"].sum().sort_values("Pago", ascending=False)
        fig = px.bar(resumo.head(20).sort_values("Pago"), x="Pago", y="Fonte", orientation="h", title="Valor pago por fonte", template="plotly_dark", color="Pago", color_continuous_scale="Teal")
        fig.update_layout(height=max(450, min(850, len(resumo.head(20))*32)), coloraxis_showscale=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(resumo, use_container_width=True, hide_index=True)

else:
    st.subheader("🔎 Explorador de dados")
    st.caption("Pesquise e filtre os registros; os filtros de Ano e Órgão acima também são aplicados.")
    termo = st.text_input("Buscar texto em qualquer coluna")
    tabela = filtrado.copy()
    if termo:
        mascara = tabela.astype(str).apply(lambda col: col.str.contains(termo, case=False, na=False)).any(axis=1)
        tabela = tabela[mascara]
    st.write(f"Registros encontrados: **{len(tabela):,}**".replace(",", "."))
    st.dataframe(tabela, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Baixar dados filtrados em CSV",
        data=tabela.to_csv(index=False).encode("utf-8-sig"),
        file_name="orcamento_filtrado.csv",
        mime="text/csv",
    )

st.markdown("---")
st.markdown('<p class="small-note">Orçamento 360 • Projeto educacional de análise de dados. Confira a qualidade e o significado dos dados de origem antes de tirar conclusões.</p>', unsafe_allow_html=True)
