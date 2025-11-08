from transform_data import merge_sus_ibge_data
import streamlit as st
import plotly.express as px
import pandas as pd

def main():
    df = merge_sus_ibge_data()

    st.set_page_config(
        layout="wide" 
    )
    st.title("Integração de Dados SUS e IBGE - Municípios do Ceará")
    
    #Qtd de atendimentos por município
    df['municipio_title'] = df['municipio'].str.title()
    fig_map = px.scatter_map(
        df,
        lat="latitude",
        lon="longitude",
        size="n_atendimentos",
        color="n_atendimentos",
        zoom=5,
        custom_data=["municipio_title", "n_atendimentos"],
        labels={"n_atendimentos": "Atendimentos"}
    )
    fig_map.update_traces(
        hovertemplate="%{customdata[0]}<br>Atendimentos = %{customdata[1]}<extra></extra>"
    )
    fig_map.update_layout(
        legend_title_font=dict(size=18)
    )

    #Atendimentos por 100 mil hab
    df['atendimentos_por_100k'] = (df['n_atendimentos'] / df['populacao']) * 100_000
    fig_bar = px.bar(
        df.sort_values('atendimentos_por_100k', ascending=False),
        x='municipio_title',
        y='atendimentos_por_100k',
        labels={'atendimentos_por_100k': 'Qtd por 100 mil habitantes', 'municipio_title': 'Município'},
        text='atendimentos_por_100k'
    )

    fig_bar.update_traces(texttemplate='%{text:.1f}', 
                          textposition='outside',
                          textfont_size=14)
    fig_bar.update_layout(
        xaxis_tickangle=-45,
        xaxis_title_font=dict(size=16),   
        yaxis_title_font=dict(size=16),        
        xaxis_tickfont=dict(size=12),     
        yaxis_tickfont=dict(size=12)
    )

    col1, col2 = st.columns(2)

    with col1:
        st.header("Atendimentos por Município")
        st.plotly_chart(fig_map, use_container_width=True)

    with col2:
        st.header("Atendimentos por 100 mil habitantes")
        st.plotly_chart(fig_bar, use_container_width=True)

    #comparação entre regiões de planejamento
    df_regiao = df.groupby('regiao_planejamento').agg(
        total_atendimentos=('n_atendimentos', 'sum'),
        media_por_100k=('atendimentos_por_100k', 'mean')
    ).reset_index()
    st.title("Comparação de Atendimentos por Região de Planejamento")
   
    fig_total = px.bar(
        df_regiao.sort_values('total_atendimentos', ascending=False),
        x='regiao_planejamento',
        y='total_atendimentos',
        text='total_atendimentos',
        labels={'regiao_planejamento': 'Região', 'total_atendimentos': 'Total de Atendimentos'}
    )
    fig_total.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    fig_total.update_layout(title_text='Total de Atendimentos por Região', xaxis_tickangle=-45)

    fig_media = px.bar(
        df_regiao.sort_values('media_por_100k', ascending=False),
        x='regiao_planejamento',
        y='media_por_100k',
        text='media_por_100k',
        labels={'regiao_planejamento': 'Região', 'media_por_100k': 'Atendimentos por 100 mil hab.'}
    )
    fig_media.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_media.update_layout(title_text='Média de Atendimentos por 100 mil habitantes por Região', xaxis_tickangle=-45)

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_total, use_container_width=True)

    with col2:
        st.plotly_chart(fig_media, use_container_width=True)
    
    #correlação socioeconômica
    regioes = df['regiao_planejamento'].unique()
    selected_regioes = st.multiselect("Selecione regiões", options=regioes, default=regioes)
    df_filtrado = df[df['regiao_planejamento'].isin(selected_regioes)]
    df['idh_2010'] = pd.to_numeric(df['idh_2010'], errors='coerce')
    df['atendimentos_por_100k'] = pd.to_numeric(df['atendimentos_por_100k'], errors='coerce')
    
    fig = px.scatter(
        df_filtrado,
        x='idh_2010',
        y='atendimentos_por_100k',
        size='populacao',
        color='regiao_planejamento',
        hover_name='municipio_title',
        hover_data={
            'n_atendimentos': True,
            'populacao': True,
            'atendimentos_por_100k': ':.1f',
            'idh_2010': ':.3f'
        },
        labels={
            'idh_2010': 'IDH 2010',
            'atendimentos_por_100k': 'Atendimentos por 100 mil habitantes',
            'regiao_planejamento': 'Região'
        },
        trendline="ols",    
        trendline_scope="overall",
        template='plotly_white'
    )

    st.subheader("Distribuição e Tendência por Região")
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
