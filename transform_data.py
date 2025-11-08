import pandas as pd
from unidecode import unidecode

def generate_geo_df():
    df1 = pd.read_csv('data/mapa_populacao.csv')
    df1['UF'] = 'CE'

    df2 = pd.read_csv('data/mapa_area.csv')

    df3 = pd.merge(df1, df2, on='Local', how='inner')
    df3['Densidade (pessoas/km²)'] = round(df3[' "População no último censo"'] / df3[' "Área da unidade territorial"'], 2)

    df4 = pd.read_excel('data\\RELATORIO_DTB_BRASIL_2024_MUNICIPIOS.xls')
    df4 = df4[df4['Unnamed: 1'] == 'Ceará'][['Unnamed: 7', 'Unnamed: 8']]
    df4.rename(columns={'Unnamed: 7': 'cod_muni_completo', 'Unnamed: 8': 'nome_muni'}, inplace=True)
    df4.reset_index(drop=True)

    df5 = pd.merge(df3, df4, left_on='Local', right_on='nome_muni', how='inner')
    df5.drop(columns=['nome_muni'], inplace=True)

    df6 = pd.read_excel('data\\IDH2010.xls')

    df7 = pd.merge(df5, df6, left_on='Local', right_on='Índice de Desenvolvimento Humano', how='left')
    df7.drop(columns=['Unnamed: 1', 'Índice de Desenvolvimento Humano'], inplace=True)
    df7.rename(columns={'Unnamed: 2': 'IDH 2010'}, inplace=True)

    df8 = pd.read_excel('data\\Lista_Regioes_Planejamento_Ceara.xlsx')
    df8['Código do município (IBGE)'] = df8['Código do município (IBGE)'].astype(str)

    df9 = pd.merge(df7, df8, left_on='cod_muni_completo', right_on='Código do município (IBGE)', how='inner')
    df9.drop(columns=['cod_muni_completo', 'Nome do município'], inplace=True)
    df9 = df9.sort_values(by='Local', ascending=True).reset_index(drop=True)

    df10 = pd.read_csv('data\\municipios_lat_long.csv')
    df10['codigo_ibge'] = df10['codigo_ibge'].astype(str)
    df10 = df10[['codigo_ibge', 'latitude', 'longitude', 'codigo_uf', 'nome']]
    df_final = pd.merge(df9, df10, left_on='Código do município (IBGE)', right_on='codigo_ibge', how='inner')
    df_final.drop(columns=['codigo_ibge', 'nome', 'codigo_uf'], inplace=True)

    return df_final

def merge_sus_ibge_data():
    df_geo = generate_geo_df()

    df_group = pd.read_csv('data/DADOS.txt', sep=',', dtype={'MUNICÍPIO': str}, index_col=0).reset_index(drop=True)

    df_group = df_group.groupby('MUNICÍPIO').count().reset_index()

    def normalizar(nome):
        nome = nome.strip()
        nome = unidecode(nome)
        nome = nome.lower()
        return nome

    df_geo['Local'] = df_geo['Local'].apply(normalizar)
    df_group['MUNICÍPIO'] = df_group['MUNICÍPIO'].apply(normalizar)
    df_group['MUNICÍPIO'] = df_group['MUNICÍPIO'].str.replace('itapage', 'itapaje')

    df_merged = pd.merge(df_geo, df_group, left_on='Local', right_on='MUNICÍPIO', how='inner')
    df_merged = df_merged.drop(columns=['MUNICÍPIO']).rename(columns={
        'PRIMEIRO_NOME': 'n_atendimentos',
        'Local': 'municipio',
        ' "População no último censo"': 'populacao',
        ' "Área da unidade territorial"': 'area_km2',
        'Densidade (pessoas/km²)': 'densidade_pessoas_km2',
        'IDH 2010': 'idh_2010',
        'Código do município (IBGE)': 'codigo_muni_ibge',
        'Região de Planejamento': 'regiao_planejamento',
        'UF': 'uf'
    })

    return df_merged

# print(merge_sus_ibge_data().head(5))

