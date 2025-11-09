from transform_data import merge_sus_ibge_data
import streamlit as st
import plotly.express as px
import pandas as pd

@st.cache_data
def load_data():
    df = merge_sus_ibge_data()
    return df

def main():
    df = load_data()

    st.set_page_config(
        layout="wide" 
    )
    st.title("Integração de Dados SUS e IBGE - Municípios do Ceará")

    st.markdown("""
        ### Pré-processamento dos dados em DADOS.txt

        1. Ausência de dados sobre os estados relativos a cada cidade impede qualquer conclusão sobre a análise, já que pode haver cidades com nomes iguais em estados diferentes. Foi necessário presumir que todas as cidades listadas eram no Ceará.
        2. Ajuste de "Itapagé" para "Itapajé".
        3. Remoção de espaços em excesso após os nomes das cidades.
        4. Não há registro sobre período em que esses dados foram coletados. Conclusões quanto a, por exemplo, quantidade de atendimentos por 100 mil habitantes podem ser referentes a um ou vários anos.
        5. Os nomes contidos no arquivo não parecem contribuir para uma interpretação aprofundada dos dados.

        ### Outras fontes de dados

        1. IBGE (IDH 2010, área, população e coordenadas das cidades cearenses, código dos municípios)
        2. IPECE (regiões de planejamento do estado do Ceará)
        """)
    
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

    #comparação entre regiões de planejamento
    df['atendimentos_por_100k'] = (df['n_atendimentos'] / df['populacao']) * 100_000

    # Adiciona cálculo da média de IDH para cada região
    df_regiao = df.groupby('regiao_planejamento').agg(
        total_atendimentos=('n_atendimentos', 'sum'),
        media_por_100k=('atendimentos_por_100k', 'mean'),
        media_idh=('idh_2010', 'mean')
    ).reset_index()
    fig_media = px.bar(
        df_regiao.sort_values('media_por_100k', ascending=False),
        x='regiao_planejamento',
        y='media_por_100k',
        text='media_por_100k',
        labels={'regiao_planejamento': 'Região', 'media_por_100k': 'Atendimentos por 100 mil hab.'}
    )
    fig_media.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_media.update_layout(xaxis_tickangle=-45)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Atendimentos por município")
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown("""
        - Predomínio de atendimentos nas maiores cidades (RMF, Sobral, Quixadá, Juazeiro do Norte), que centralizam serviços de saúde.
        - Quantidade inesperadamente grande em Itapipoca.
        """)

    with col2:
        st.subheader("Média de atendimentos por 100 mil habitantes por região de planejamento")
        st.plotly_chart(fig_media, use_container_width=True)
        st.markdown("""
        - Grande Fortaleza com menor atendimento à população.
        - Pode indicar desequilíbrio territorial na oferta e demanda de serviços de saúde, com sobrecarga dos grandes centros e maior dependência do SUS em localidades com menor densidade populacional.
        """)

    #IDH
    st.subheader("Distribuição do IDH por região de planejamento")

    fig_box_idh = px.box(
        df,
        x='regiao_planejamento',
        y='idh_2010',
        color='regiao_planejamento',
        points='all',  
        labels={
            'regiao_planejamento': 'Região de Planejamento',
            'idh_2010': 'IDH (2010)'
        },
        # title='Distribuição do IDH por Região de Planejamento'
    )
    fig_box_idh.update_layout(
        showlegend=False,
        xaxis_tickangle=-45,
        template='plotly_white'
    )

    st.plotly_chart(fig_box_idh, use_container_width=True)
    st.markdown("""
       - Este gráfico mostra a variação do Índice de Desenvolvimento Humano (IDH) entre os municípios de cada região de planejamento. Regiões com faixas mais estreitas e medianas mais altas indicam maior homogeneidade e desenvolvimento humano médio mais elevado.
        - Ausência de dados mais recentes.
        """)

    #Ranking de Municípios por Atendimentos Proporcionais
    df_rank = df[['municipio_title', 'regiao_planejamento', 'atendimentos_por_100k']].sort_values('atendimentos_por_100k', ascending=False)
    df_rank.rename(columns={'municipio_title': 'Município', 'regiao_planejamento': 'Região de Planejamento', 'atendimentos_por_100k': 'Atendimentos por 100000 habitantes'}, inplace=True)
    top10 = df_rank.head(10).reset_index(drop=True)
    top10.index = top10.index + 1
    top10.index.name = 'Ranking'
    bottom10 = df_rank.tail(10).reset_index(drop=True)
    bottom10.index = bottom10.index + 1
    bottom10.index.name = 'Ranking'

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("10 municípios com maior número de atendimentos por 100 mil habitantes")
        st.dataframe(top10.style.format({'atendimentos_por_100k': '{:.1f}'}), use_container_width=True)

    with col2:
        st.subheader("10 municípios com menor número de atendimentos por 100 mil habitantes")
        st.dataframe(bottom10.style.format({'atendimentos_por_100k': '{:.1f}'}), use_container_width=True)
    
    st.markdown("""
    O ranking apresenta os municípios com maior e menor número de atendimentos do SUS em proporção à população.  
    Valores mais altos podem indicar maior dependência dos serviços públicos de saúde ou melhor capacidade de atendimento local.  Já valores baixos, observados em grandes centros urbanos, costumam refletir diluição da demanda devido à alta população, possível maior presença da rede privada, ou centralização dos atendimentos regionais.

    - Municípios pequenos, mas com alta taxa proporcional, podem estar com serviços do SUS sobrecarregados.  
    - Municípios grandes, com taxa proporcional menor, tendem a concentrar volume absoluto, mas menor cobertura relativa.
    """)
    
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

    st.subheader("Distribuição e tendência por região")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
        - Quanto maior o IDH, menor a quantidade de atendimentos per capita.
        - Cidades com maior IDH também têm maiores populações, impactando a estimativa.
        - Reforça hipótese de maior dependência do SUS em áreas de menor IDH (que acabam tendo menor disponibilidade de serviços de saúde também).
        """)
    
    st.subheader("Correlação entre IDH médio e média de atendimentos por 100 mil habitantes (por região)")

    corr_value = df_regiao['media_idh'].corr(df_regiao['media_por_100k'])
        # Interpretação textual do coeficiente
    if corr_value > 0.7:
        interpretacao = "Correlação positiva forte"
        cor = "green"
    elif corr_value > 0.3:
        interpretacao = "Correlação positiva moderada"
        cor = "lightgreen"
    elif corr_value > -0.3:
        interpretacao = "Correlação fraca ou inexistente"
        cor = "gray"
    elif corr_value > -0.7:
        interpretacao = "Correlação negativa moderada"
        cor = "orange"
    else:
        interpretacao = "Correlação negativa forte"
        cor = "red"

    st.markdown(
        f"""
        <div style='text-align:center; padding:15px; border-radius:10px; background-color:{cor}; color:white'>
            <h3>Coeficiente de Correlação (Pearson): {corr_value:.3f}</h3>
            <p>{interpretacao}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
        - Observa-se uma correlação negativa entre o IDH médio da região e a quantidade média de atendimentos por 100 mil habitantes.
        - Regiões com **menor IDH** apresentam **maior média de atendimentos proporcionais**, indicando maior dependência do SUS.
        - O coeficiente de correlação mostra a **intensidade e direção** dessa relação.
        """)
    
    st.subheader("Conclusão")
    
    st.markdown("""
        Por fim, além de todas as indicações já demonstradas anteriormente, percebe-se que há uma correlação negativa moderada entre IDH e quantidade média de atendimentos. Podemos ter isso como um indicativo que o IDH, por si só, não é o único indicador do aumento de atendimentos, como é o caso do aumento populacional, que também tende a aumentar essa média. 
                
        Além disso, a base de dados com o nome dos municípios e nomes não parece ter nenhuma relação forte ou indicativo que auxilie na interpretação das informações, não havendo como realizar um cruzamento entre esses dados.
    """)

if __name__ == "__main__":
    main()
