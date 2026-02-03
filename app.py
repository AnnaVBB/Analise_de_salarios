import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página --- #
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard de Salários em Dados",
    page_icon="📊",
    layout="wide"
)

# ======================================================
# CSS PERSONALIZADO
# ======================================================
st.markdown("""
<style>
/* Fundo da sidebar */
section[data-testid="stSidebar"] {
    background-color: #2b2b2b;
}

/* Títulos da sidebar */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
    color: #ffffff !important;
}

/* Labels dos filtros */
section[data-testid="stSidebar"] label {
    color: white !important;
    font-weight: 600;
}

/* Caixa dos multisets */
div[data-baseweb="select"] > div {
    background-color: #2b2b2b;
    border-radius: 8px;
}

/* Texto dentro dos filtros */
div[data-baseweb="select"] span {
    color: #f2f2f2;
}

/* Itens selecionados (tags) */
div[data-baseweb="tag"] {
    background-color: #b1123b !important;
    color: white !important;
    border-radius: 6px;
}

/* Hover dos itens selecionados*/
div[data-baseweb="tag"]:hover {
    background-color: #d6406f !important;
}
</style>
""", unsafe_allow_html=True)

# --- Configuração da paleta de cores --- #
COLOR_MAP_SENIORIDADE = {
    'Junior': '#d6406f',
    'Pleno': '#8b1e3f',
    'Senior': '#b1123b',
    'Executivo': '#5a1027'
}

COLOR_MAP_REMOTO = {
    'presencial': '#5e616a',
    'remoto': '#b1123b',
    'hibrido': '#944459'
}

COLOR_MAP_CONTRATO = {
    'integral': '#36454F',
    'contrato': '#708090',
    'parcial': '#A9A9A9',
    'freelancer': '#D3D3D3'
}

WINE_SCALE = ['#5A1027', '#8B1E3F', '#B1123B', '#D6406F', '#FF6B8B', '#FF9AA2']

# ===========================================================================================================#
# --- Carregamento dos dados ---
df = pd.read_csv("dados-imersao-final.csv")
df['senioridade'] = df['senioridade'].str.capitalize()

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de ano
anos = st.sidebar.multiselect(
    "Ano",
    sorted(df['ano'].unique()),
    default=sorted(df['ano'].unique())
)

# Filtro de Senioridade
senioridades = st.sidebar.multiselect(
    "Senioridade",
    sorted(df['senioridade'].unique()),
    default=sorted(df['senioridade'].unique())
)

# Filtro de tipo de contrato
contratos = st.sidebar.multiselect(
    "Tipo de contrato",
    sorted(df['contrato'].unique()),
    default=sorted(df['contrato'].unique())
)

# Filtragem do DataFrame
df_filtrado = df[  # Criamos um novo DataFrame somente com as linhas que obedecem todos os filtros selecionados
    (df['ano'].isin(anos)) &  # mantém apenas os anos escolhidos
    # mantém apenas as senioridades escolhidas
    (df['senioridade'].isin(senioridades)) &
    (df['contrato'].isin(contratos))  # mantém apenas os contratos escolhidos
]  # todos os gráficos, KPIs e tabelas usam ess df_filtrado, garantindo que o dashboard se torne reativo e interativo

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
# ======================
# TÍTULO PRINCIPAL
# ======================
st.title("📊 Dashboard Salarial — Área de Dados")
st.markdown(
    "Análise interativa dos salários na área de dados, "
    "com foco em senioridade, tipo de trabalho e distribuição global."
)

st.markdown("---")

# ======================
# Métricas principais (KPIs)
# ======================
# Criar as variáveis
salario_medio = df_filtrado['usd'].mean()
salario_maximo = df_filtrado['usd'].max()
total_registros = len(df_filtrado)
cargo_mais_frequente = df_filtrado['cargo'].mode()[0]


# Definir as métricas
col1, col2 = st.columns(2)

with col1:
    st.metric("💰 Salário médio", f"${salario_medio:,.0f}")
    st.metric("👥 Total de registros", f"{total_registros:,}")

with col2:
    st.metric("📈 Salário máximo", f"${salario_maximo:,.0f}")
    st.metric("🧑‍💻 Cargo mais comum", cargo_mais_frequente)

st.markdown("---")
# ======================
# LINHA 1 — SENIORIDADE e salário
# ======================
# cria duas colunas lado a lado, cada coluna recebe um gráfico, facilitando a comparação
col_1, col_2 = st.columns(2)

# Salário médio por senioridade
with col_1:
    ordem_senioridade = ['Junior', 'Pleno', 'Senior', 'Executivo']
    media_senioridade = (
        df_filtrado
        .groupby('senioridade', as_index=False)['usd']
        .mean()
        .sort_values('usd', ascending=False)
    )

    fig_media = px.bar(
        media_senioridade,
        x='senioridade',
        y='usd',
        color='senioridade',
        color_discrete_map=COLOR_MAP_SENIORIDADE,
        title="💼 Salário médio por senioridade",
        labels={'usd': 'Salário médio anual (USD)', 'senioridade': ''}
    )

    fig_media.update_layout(plot_bgcolor='rgba(0,0,0,0)', title_x=0.05)
    st.plotly_chart(fig_media, use_container_width=True)

# Crescimento % do salário médio por senioridade
with col_2:
    ordem_senioridade = ['Junior', 'Pleno', 'Senior', 'Executivo']

    media = (
        df_filtrado
        .groupby('senioridade')['usd']
        .mean()
        .reindex(ordem_senioridade)
        .reset_index()
    )

    media['crescimento_%'] = media['usd'].pct_change() * 100

    fig_growth = px.bar(
        media,
        x='senioridade',
        y='crescimento_%',
        color='senioridade',
        color_discrete_map=COLOR_MAP_SENIORIDADE,
        title="📊 Crescimento % do salário médio por senioridade"
    )

    fig_growth.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title_x=0.05,
        yaxis_title='% de crescimento'
    )

    st.plotly_chart(fig_growth, use_container_width=True)

# ======================
# LINHA 2 — Boxplot _ distruibuição salarial
# ======================
col_3, col_4 = st.columns(2)

# Distribuição salarial por senioridade
with col_3:
    fig_box = px.box(
        df_filtrado,
        x='senioridade',
        y='usd',
        color='senioridade',
        category_orders={'senioridade': [
            'Junior', 'Pleno', 'Senior', 'Executivo']},
        color_discrete_map=COLOR_MAP_SENIORIDADE,
        title="📊 Distribuição salarial por senioridade"
    )

    fig_box.update_layout(plot_bgcolor='rgba(0,0,0,0)', title_x=0.05)
    st.plotly_chart(fig_box, use_container_width=True)

# Distribuição salarial
with col_4:
    fig_hist = px.histogram(
        df_filtrado,
        x='usd',
        nbins=30,
        opacity=0.75,
        title="💵 Distribuição salarial",
        labels={'usd': 'Salário anual (USD)'}
    )

    fig_hist.update_traces(
        marker_color="#8b1e3f",
        marker_line_color="black",
        marker_line_width=1,
        opacity=0.85
    )

    fig_hist.update_layout(plot_bgcolor='rgba(0,0,0,0)', title_x=0.05)
    st.plotly_chart(fig_hist, use_container_width=True)

# ======================
# LINHA 3 — Proporções
# ======================
col5, col6 = st.columns(2)

# Proporção tipos de trabalho
ordem_remoto = ['presencial', 'remoto', 'hibrido']

df_remoto = (
    df_filtrado['remoto']
    .value_counts()
    .reset_index()
)

df_remoto.columns = ['tipo', 'quantidade']

# aplica ordem SEM forçar categorias inexistentes
df_remoto['tipo'] = pd.Categorical(
    df_remoto['tipo'],
    categories=ordem_remoto,
    ordered=True
)

df_remoto = df_remoto.sort_values('tipo')

with col5:
    if df_remoto['quantidade'].sum() > 0:
        fig_remoto = px.pie(
            df_remoto,
            names='tipo',
            values='quantidade',
            hole=0.5,
            color='tipo',
            color_discrete_map=COLOR_MAP_REMOTO,
            title="👔 Proporção dos tipos de trabalho"
        )

        fig_remoto.update_traces(textinfo='percent+label')
        fig_remoto.update_layout(title_x=0.05)
        st.plotly_chart(fig_remoto, use_container_width=True)
    else:
        st.info("Sem dados disponíveis para tipos de trabalho.")

# Proporção de média salarial por tipo de contrato
# ======================
# Proporção média salarial por tipo de contrato
# ======================

ordem_contrato = [
    'integral',
    'contrato',
    'parcial',
    'freelancer'
]

df_contrato = (
    df_filtrado
    .groupby('contrato')['usd']
    .mean()
    .reset_index()
)

df_contrato['contrato'] = pd.Categorical(
    df_contrato['contrato'],
    categories=ordem_contrato,
    ordered=True
)

df_contrato = df_contrato.sort_values('contrato')

with col6:
    if df_contrato['usd'].sum() > 0:
        fig_contrato = px.pie(
            df_contrato,
            names='contrato',
            values='usd',
            hole=0.5,
            color='contrato',
            color_discrete_map=COLOR_MAP_CONTRATO,
            title="💲 Proporção da média salarial por tipo de contrato"
        )

        fig_contrato.update_traces(textinfo='percent+label')
        fig_contrato.update_layout(title_x=0.05)
        st.plotly_chart(fig_contrato, use_container_width=True)
    else:
        st.info("Sem dados disponíveis para tipos de contrato.")

# ======================
# Linha 7- Mapa de distribuição salarial de DataScientist por país
# ======================
st.markdown("---")

df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
media_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()

fig_mapa = px.choropleth(
    media_pais,
    locations='residencia_iso3',
    color='usd',
    color_continuous_scale=WINE_SCALE,
    title="🌍 Salário médio de Cientista de Dados por país",
    labels={'usd': 'Salário médio (USD)'}
)

fig_mapa.update_layout(height=600, title_x=0.02)
st.plotly_chart(fig_mapa, use_container_width=True)

# ======================
# TABELA FINAL
# ======================
st.markdown("---")
st.subheader("📄 Dados detalhados")
st.dataframe(df_filtrado, use_container_width=True)
