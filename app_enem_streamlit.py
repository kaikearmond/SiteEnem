import os
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title='Dashboard ENEM 2024',
    page_icon='📘',
    layout='wide',
    initial_sidebar_state='expanded'
)

CORES = {
    'primaria':   '#123C73',
    'secundaria': '#0E7490',
    'destaque':   '#F59E0B',
    'sucesso':    '#16A34A',
    'fundo':      '#F4F7FB',
    'card':       '#FFFFFF',
    'texto':      '#0F172A',
    'texto_suave':'#475569',
    'borda':      '#D9E2F1',
}

COR_REGIAO = {
    'Norte':        '#1D4ED8',
    'Nordeste':     '#F97316',
    'Centro-Oeste': '#16A34A',
    'Sudeste':      '#DC2626',
    'Sul':          '#7C3AED',
}

NOTAS_COLS = {
    'Ciências da Natureza': 'NOTA_CN_CIENCIAS_DA_NATUREZA',
    'Ciências Humanas':     'NOTA_CH_CIENCIAS_HUMANAS',
    'Linguagens e Códigos': 'NOTA_LC_LINGUAGENS_E_CODIGOS',
    'Matemática':           'NOTA_MT_MATEMATICA',
    'Redação':              'NOTA_REDACAO',
    'Média Geral':          'NOTA_MEDIA_5_NOTAS',
}

CAMINHO_DADOS = 'Enem_2024_Amostra_Perfeita.xlsx'

st.markdown(
    f"""
    <style>
    .stApp {{
        background: {CORES['fundo']};
    }}
    .bloco-topo {{
        background: linear-gradient(90deg, {CORES['primaria']} 0%, #2563EB 100%);
        padding: 22px 26px;
        border-radius: 22px;
        color: white;
        box-shadow: 0 16px 40px rgba(37, 99, 235, 0.18);
        margin-bottom: 1rem;
    }}
    .kpi-card {{
        background: white;
        border-radius: 18px;
        padding: 18px 18px 14px 18px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
        border: 1px solid rgba(217, 226, 241, 0.4);
        min-height: 118px;
    }}
    .kpi-title {{
        text-transform: uppercase;
        font-size: 0.74rem;
        letter-spacing: 0.08em;
        color: {CORES['texto_suave']};
        font-weight: 700;
        margin-bottom: 8px;
    }}
    .kpi-value {{
        font-size: 1.9rem;
        font-weight: 800;
        line-height: 1.05;
        color: {CORES['primaria']};
    }}
    .secao-card {{
        background: white;
        border-radius: 20px;
        padding: 18px 18px 10px 18px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
        border: 1px solid rgba(217, 226, 241, 0.4);
        margin-bottom: 1rem;
    }}
    .secao-titulo {{
        font-size: 1.15rem;
        font-weight: 800;
        color: {CORES['texto']};
        margin-bottom: 4px;
    }}
    .secao-subtitulo {{
        color: {CORES['texto_suave']};
        font-size: 0.95rem;
        margin-bottom: 12px;
    }}
    .sidebar-info {{
        background: linear-gradient(180deg, {CORES['primaria']} 0%, #0B2447 100%);
        color: white;
        border-radius: 18px;
        padding: 14px 16px;
        margin-bottom: 1rem;
    }}
    div[data-testid="stSidebar"] > div:first-child {{
        background: linear-gradient(180deg, {CORES['primaria']} 0%, #0B2447 100%);
    }}
    div[data-testid="stSidebar"] label, div[data-testid="stSidebar"] .stMarkdown, div[data-testid="stSidebar"] p {{
        color: white !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def carregar_dados(caminho: str) -> pd.DataFrame:
    return pd.read_excel(caminho)


def estilizar_figura(fig: go.Figure, altura: int = 360) -> go.Figure:
    fig.update_layout(
        template='plotly_white',
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=20, b=20),
        hoverlabel=dict(bgcolor='white', font_size=12, font_family='Arial'),
        font=dict(color=CORES['texto']),
        height=altura,
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor='rgba(148, 163, 184, 0.18)', zeroline=False)
    return fig


def figura_vazia(mensagem='Sem dados para o filtro selecionado') -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=mensagem,
        x=0.5, y=0.5, xref='paper', yref='paper',
        showarrow=False,
        font=dict(size=16, color=CORES['texto_suave'])
    )
    fig.update_layout(
        template='plotly_white',
        xaxis={'visible': False},
        yaxis={'visible': False},
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(l=10, r=10, t=10, b=10),
        height=360,
    )
    return fig


def kpi_card(titulo: str, valor: str, cor: str):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{titulo}</div>
            <div class="kpi-value" style="color:{cor};">{valor}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def secao_abertura(titulo: str, subtitulo: str):
    st.markdown(
        f"""
        <div class="secao-card">
            <div class="secao-titulo">{titulo}</div>
            <div class="secao-subtitulo">{subtitulo}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if not os.path.exists(CAMINHO_DADOS):
    st.error(
        f"Arquivo não encontrado em: {CAMINHO_DADOS}. Coloque a planilha na mesma pasta do app ou ajuste CAMINHO_DADOS."
    )
    st.stop()


df = carregar_dados(CAMINHO_DADOS)

UFS = sorted(df['SG_UF_PROVA'].dropna().unique().tolist())
REGIOES = sorted(df['Regiao_Nome_Prova'].dropna().unique().tolist())
nota_min = int(df['NOTA_MEDIA_5_NOTAS'].min())
nota_max = int(df['NOTA_MEDIA_5_NOTAS'].max())

# ============================================================
# BARRA LATERAL
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-info">
            <div style="font-size:1.35rem;font-weight:800;">ENEM 2024</div>
            <div style="font-size:0.95rem;opacity:0.85;">Filtros interativos do painel</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    regiao = st.selectbox('🗺️ Região', ['TODAS'] + REGIOES, format_func=lambda x: 'Todas as regiões' if x == 'TODAS' else x)

    if regiao == 'TODAS':
        ufs_filtradas = UFS
    else:
        ufs_filtradas = sorted(df[df['Regiao_Nome_Prova'] == regiao]['SG_UF_PROVA'].dropna().unique().tolist())

    uf = st.selectbox('🏛️ Estado (UF)', ['TODAS'] + ufs_filtradas, format_func=lambda x: 'Todos os estados' if x == 'TODAS' else x)
    nota_label = st.selectbox('📘 Nota em destaque', list(NOTAS_COLS.keys()), index=list(NOTAS_COLS.keys()).index('Média Geral'))
    col_nota = NOTAS_COLS[nota_label]

    faixa_nota = st.slider(
        '🎯 Faixa de nota (Média Geral)',
        min_value=nota_min,
        max_value=nota_max,
        value=(nota_min, nota_max),
        step=10,
    )

    sexo = st.multiselect('👤 Sexo', ['Feminino', 'Masculino'], default=['Feminino', 'Masculino'])

    racas = sorted(df['TP_COR_RACA'].dropna().unique().tolist())
    raca = st.selectbox('🎨 Cor/Raça', ['TODAS'] + racas, format_func=lambda x: 'Todas' if x == 'TODAS' else x)

# ============================================================
# FILTROS
# ============================================================
d = df.copy()
if regiao != 'TODAS':
    d = d[d['Regiao_Nome_Prova'] == regiao]
if uf != 'TODAS':
    d = d[d['SG_UF_PROVA'] == uf]
d = d[d['NOTA_MEDIA_5_NOTAS'].between(faixa_nota[0], faixa_nota[1])]
if sexo:
    d = d[d['TP_Sexo'].isin(sexo)]
else:
    d = d.iloc[0:0]
if raca != 'TODAS':
    d = d[d['TP_COR_RACA'] == raca]

# ============================================================
# TOPO
# ============================================================
st.markdown(
    """
    <div class="bloco-topo">
        <div style="font-size:1.85rem;font-weight:800;">Dashboard Interativo do ENEM 2024</div>
        <div style="font-size:1rem;opacity:0.88;">Análise visual com foco em distribuição, comparação regional e ranking por UF.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if d.empty:
    st.warning('Nenhum registro encontrado para o filtro selecionado.')
    st.plotly_chart(figura_vazia(), use_container_width=True)
    st.stop()

serie = d[col_nota].dropna()
contagem = f"🔎 {len(d):,} candidatos no recorte selecionado".replace(',', '.')
st.caption(contagem)

# ============================================================
# KPIS
# ============================================================
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1.25])
with col1:
    kpi_card('Total de candidatos', f"{len(d):,}".replace(',', '.'), CORES['primaria'])
with col2:
    kpi_card('Média', f"{serie.mean():.1f}", CORES['secundaria'])
with col3:
    kpi_card('Mediana', f"{serie.median():.1f}", CORES['destaque'])
with col4:
    kpi_card('Maior nota', f"{serie.max():.1f}", '#7C3AED')
with col5:
    kpi_card('% acima de 600', f"{(serie >= 600).mean() * 100:.1f}%", CORES['sucesso'])

st.write('')

# ============================================================
# GRÁFICOS
# ============================================================
# Histograma
fig_hist = px.histogram(
    d,
    x=col_nota,
    nbins=45,
    color_discrete_sequence=[CORES['primaria']],
    opacity=0.92,
    labels={col_nota: nota_label},
)
fig_hist.add_vline(
    x=serie.mean(), line_dash='dash', line_color=CORES['destaque'], line_width=2,
    annotation_text=f'Média: {serie.mean():.1f}', annotation_position='top right'
)
fig_hist.add_vline(
    x=serie.median(), line_dash='dot', line_color=CORES['secundaria'], line_width=2,
    annotation_text=f'Mediana: {serie.median():.1f}', annotation_position='top left'
)
fig_hist.update_traces(hovertemplate='Nota: %{x:.1f}<br>Quantidade: %{y}<extra></extra>')
fig_hist.update_layout(bargap=0.04, xaxis_title=nota_label, yaxis_title='Quantidade de candidatos')
fig_hist = estilizar_figura(fig_hist, altura=420)

# Boxplot por região
ordem_regioes = [r for r in ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul'] if r in d['Regiao_Nome_Prova'].dropna().unique()]
fig_box = px.box(
    d,
    x='Regiao_Nome_Prova',
    y=col_nota,
    color='Regiao_Nome_Prova',
    category_orders={'Regiao_Nome_Prova': ordem_regioes},
    color_discrete_map=COR_REGIAO,
    points=False,
    labels={'Regiao_Nome_Prova': 'Região', col_nota: nota_label},
)
fig_box.update_traces(quartilemethod='exclusive', line_width=2)
fig_box.update_layout(showlegend=False, xaxis_title='', yaxis_title='Nota')
fig_box = estilizar_figura(fig_box, altura=420)

# Ranking UF
media_uf = (
    d.groupby('SG_UF_PROVA')[col_nota]
     .agg(['mean', 'count'])
     .reset_index()
     .sort_values('mean', ascending=False)
)
media_uf.columns = ['UF', 'Média', 'Quantidade']
fig_uf = px.bar(
    media_uf.head(15).sort_values('Média'),
    x='Média', y='UF', orientation='h',
    text='Média',
    color='Média',
    color_continuous_scale=['#DBEAFE', '#2563EB'],
    custom_data=['Quantidade'],
)
fig_uf.update_traces(
    texttemplate='%{text:.1f}',
    textposition='outside',
    hovertemplate='UF: %{y}<br>Média: %{x:.1f}<br>Candidatos: %{customdata[0]:,}<extra></extra>'
)
fig_uf.update_layout(coloraxis_showscale=False, xaxis_title='Nota média', yaxis_title='')
fig_uf = estilizar_figura(fig_uf, altura=460)

# Panorama regional
resumo_regiao = (
    d.groupby('Regiao_Nome_Prova')[col_nota]
     .agg(['mean', 'count'])
     .reset_index()
)
resumo_regiao.columns = ['Região', 'Média', 'Quantidade']
resumo_regiao['Região'] = pd.Categorical(resumo_regiao['Região'], categories=ordem_regioes, ordered=True)
resumo_regiao = resumo_regiao.sort_values('Região')
fig_regioes = make_subplots(specs=[[{'secondary_y': True}]])
fig_regioes.add_trace(
    go.Bar(
        x=resumo_regiao['Região'], y=resumo_regiao['Média'],
        name='Média', marker_color=CORES['primaria'],
        hovertemplate='Região: %{x}<br>Média: %{y:.1f}<extra></extra>'
    ),
    secondary_y=False,
)
fig_regioes.add_trace(
    go.Scatter(
        x=resumo_regiao['Região'], y=resumo_regiao['Quantidade'],
        name='Candidatos', mode='lines+markers+text',
        text=[f"{v:,.0f}".replace(',', '.') for v in resumo_regiao['Quantidade']],
        textposition='top center',
        line=dict(color=CORES['destaque'], width=3),
        marker=dict(size=8),
        hovertemplate='Região: %{x}<br>Candidatos: %{y:,.0f}<extra></extra>'
    ),
    secondary_y=True,
)
fig_regioes.update_yaxes(title_text='Nota média', secondary_y=False)
fig_regioes.update_yaxes(title_text='Quantidade de candidatos', secondary_y=True, showgrid=False)
fig_regioes.update_layout(
    template='plotly_white',
    paper_bgcolor='white',
    plot_bgcolor='white',
    margin=dict(l=20, r=20, t=20, b=20),
    hoverlabel=dict(bgcolor='white', font_size=12),
    font=dict(color=CORES['texto']),
    legend=dict(orientation='h', y=1.08, x=0),
    height=460,
)

# Faixas
bins = [0, 450, 550, 650, 750, 1000]
labels = ['Até 450', '451–550', '551–650', '651–750', 'Acima de 750']
faixas = pd.cut(serie, bins=bins, labels=labels, include_lowest=True)
resumo_faixas = faixas.value_counts().reindex(labels, fill_value=0).reset_index()
resumo_faixas.columns = ['Faixa', 'Quantidade']
fig_faixas = px.pie(
    resumo_faixas,
    names='Faixa',
    values='Quantidade',
    hole=0.56,
    color='Faixa',
    color_discrete_sequence=['#DBEAFE', '#93C5FD', '#60A5FA', '#2563EB', '#1D4ED8'],
)
fig_faixas.update_traces(
    textposition='inside',
    textinfo='percent+label',
    hovertemplate='Faixa: %{label}<br>Quantidade: %{value:,.0f}<br>Percentual: %{percent}<extra></extra>'
)
fig_faixas.update_layout(showlegend=False)
fig_faixas = estilizar_figura(fig_faixas, altura=420)

# Tabela resumo
tabela = (
    media_uf[['UF', 'Média', 'Quantidade']]
    .assign(**{
        'Média': media_uf['Média'].round(1),
        'Quantidade': media_uf['Quantidade'].map(lambda x: f"{x:,.0f}".replace(',', '.'))
    })
    .head(10)
)

# ============================================================
# RENDERIZAÇÃO
# ============================================================
col_a, col_b = st.columns([1.75, 1])
with col_a:
    st.markdown('<div class="secao-card"><div class="secao-titulo">Distribuição das notas</div><div class="secao-subtitulo">Visualize a concentração dos candidatos, a média e a mediana do recorte selecionado.</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_hist, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with col_b:
    st.markdown('<div class="secao-card"><div class="secao-titulo">Desempenho por região</div><div class="secao-subtitulo">Compare a dispersão das notas entre as grandes regiões do país.</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_box, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

col_c, col_d = st.columns([1.4, 1])
with col_c:
    st.markdown('<div class="secao-card"><div class="secao-titulo">Ranking das UFs</div><div class="secao-subtitulo">Estados ordenados pela média da nota escolhida no filtro lateral.</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_uf, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with col_d:
    st.markdown('<div class="secao-card"><div class="secao-titulo">Panorama regional</div><div class="secao-subtitulo">Média da nota e volume de participantes por região, no mesmo painel.</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_regioes, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

col_e, col_f = st.columns([1, 1.65])
with col_e:
    st.markdown('<div class="secao-card"><div class="secao-titulo">Faixas de desempenho</div><div class="secao-subtitulo">Participação percentual dos candidatos em cada intervalo de nota.</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_faixas, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with col_f:
    st.markdown('<div class="secao-card"><div class="secao-titulo">Resumo dos melhores desempenhos</div><div class="secao-subtitulo">Tabela consolidada com volume, média e mediana dos estados com maior média.</div>', unsafe_allow_html=True)
    st.dataframe(tabela, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
