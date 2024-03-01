import streamlit as st
import requests
import pandas as pd
import plotly.express as px


# DCOUMENTAÇÃO DO STREAMLIT
# https://docs.streamlit.io/


st.set_page_config(layout = 'wide') # configurando o formato de tela

def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor <1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

st.title('DASHBOARD DE VENDAS :shopping_trolley:')

#Leitura dos dados da API
url = 'https://labdados.com/produtos'
#url = 'https://labdados.com/produtos?regiao=sul?ano=2021' # exemplo de url completa com os valores dos filtros disponíveis na mesma

### Vamos filtrar Região e Ano, direto na leitura da API
## Região
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']
st.sidebar.title('Filtros') # Acrescentando barra lateral para os filtros
regiao = st.sidebar.selectbox('Região', regioes) #label e opções
# a primeira opção (Brasil) não é uma opção da API (url). Apenas a colocamos para representar a opção "Todos"
# então vamos tratar isso
if regiao == 'Brasil':
    regiao = ''

## Ano
todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True) #value determina o default, ou seja vem marcado
#mas caso fique desmarcado, então exibe o slider para seleção do ano
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023) #label, e a faixa do slider


## passando os valores dos filtros paa a API, (a url irá ser composta com o valor dos filtros)
query_string = {'regiao': regiao.lower(), 'ano': ano}  #dicionário com os valores a serem passados
response = requests.get(url, params = query_string) #a função compoe a url com os parametros
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y') #converte a data str para datetime

### O filtro vendedores fazemos após a leitura dados (API), no DF
## Vendedores
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique()) #as opções do multiselect são os valores existentes na coluna Vendedor (distinct = unique)
if filtro_vendedores:  #caso pelo menos uma opção esteja selecionada no multiselect
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)] # filtra o dataframe pelos valores selecionados

#caso nenhum valor esteja selecionado (seria o else do if acima), então não fz nada
#todo o restante do cófigo já trabalhará sobre o DF dados já filtrado


## Tabelas (DFs)
### Tabelas de Receitas
#primeiro pegamos o valor total de compras por estado 
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
#Em seguida, fazemos um merge dela com um outra tabela, para pegar os campos lat e long, e já ordenamos pelo preço do maior para o menor
# right_index = True, pq o DF gerado pelo groupby anterior terá o Local da compra como índice
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

#Muda o indix para o atributo Data, e faz um agrupamento pelo mês ('M'), somando os preços. No final reseta o indice para a Data voltr a ser coluna
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'ME'))['Preço'].sum().reset_index()
#Craindo dois novos campos, ano e mês
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()


receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending = False)

### Tabelas de quantidade de vendas
#primeiro pegamos qtd total de vendas por estado 
vendas_estados = pd.DataFrame( dados.groupby('Local da compra')[['Preço']].count() )
#Em seguida, fazemos um merge dela com um outra tabela, para pegar os campos lat e long, e já ordenamos pelo preço do maior para o menor
# right_index = True, pq o DF gerado pelo groupby anterior terá o Local da compra como índice
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)
0
#Muda o indix para o atributo Data, e faz um agrupamento pelo mês ('M'), somando os preços. No final reseta o indice para a Data voltr a ser coluna
vendas_mensal = pd.DataFrame(  dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'ME'))['Preço'].count().reset_index() )
#Craindo dois novos campos, ano e mês
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()


vendas_categorias = pd.DataFrame( dados.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending = False) )

### Tabelas de vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))



## Gráficos
# Aqui vamos usar o Plotly, mas poderíamos usar qualquer bilbioteca, ou mesmo os próprios gráfcos do streamlit (ver documentação)

#gráfico de mapa para receita por estados
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america', #escopo do mapa na visualização
                                  size = 'Preço', # os pontos no mapa terão tamnho de acordo com o valor de 'Preço'
                                  template = 'seaborn',
                                  hover_name = 'Local da compra', # Ao passar o mouse, ele mostrará o atributo Local da compra
                                  hover_data = {'lat': False, 'lon': False}, #por padraão ele mostraria no passar do mouse lat e lon. Estamos tirando (para ele não mostrar)
                                  title = 'Receita por Estado')

#gráfico de linha para receita mensal por ano
fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers = True,
                             range_y = (0, receita_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita') # Mudano o label do eixo y (senão colocaria Preço, que é o nome do campo)


fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top estados (receita)'
                             )
fig_receita_estados.update_layout(yaxis_title = 'Receita')


fig_receita_categorias = px.bar(receita_categorias,
                                text_auto = True,
                                title = 'Receita pro Categoria'
                                )
fig_receita_categorias.update_layout(yaxis_title = 'Receita')




#gráfico de mapa para qtd vendas por estados
fig_mapa_vendas = px.scatter_geo(vendas_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america', #escopo do mapa na visualização
                                  size = 'Preço', # os pontos no mapa terão tamnho de acordo com o valor de 'Preço'
                                  template = 'seaborn',
                                  hover_name = 'Local da compra', # Ao passar o mouse, ele mostrará o atributo Local da compra
                                  hover_data = {'lat': False, 'lon': False}, #por padraão ele mostraria no passar do mouse lat e lon. Estamos tirando (para ele não mostrar)
                                  title = 'Vendas por Estado')

#gráfico de linha para qtd vendas mensal por ano
fig_vendas_mensal = px.line(vendas_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers = True,
                             range_y = (0, vendas_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Qtd. Vendas Mensal')
fig_vendas_mensal.update_layout(yaxis_title = 'Qtd. Vendas') # Mudano o label do eixo y (senão colocaria Preço, que é o nome do campo)


fig_vendas_estados = px.bar(vendas_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top estados (vendas)'
                             )
fig_vendas_estados.update_layout(yaxis_title = 'Qtd. Vendas')


fig_vendas_categorias = px.bar(vendas_categorias,
                                text_auto = True,
                                title = 'Vendas por Categoria'
                                )
fig_vendas_categorias.update_layout(showlegend=False, yaxis_title = 'Qtd. Vendas')

## Visualização no Streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])

with aba1:
    coluna1, coluna2 = st.columns(2)
    #Métricas
    #coluna1.metric('Receita', dados['Preço'].sum())
    #coluna2.metric('Quantidade de Vendas', dados.shape[0])  #pegando a quatidade de linhas do DF

    #coluna1.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
    #coluna2.metric('Quantidade de vendas', formata_numero(dados.shape[0]))

    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True) # mostrando o gráfico que definimos acima. use_container_width=True para ficar nos limites da coluna
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)
    #st.dataframe(dados)
    #st.write(dados)
        
with aba2:
    coluna1, coluna2 = st.columns(2)
    
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width=True) # mostrando o gráfico que definimos acima. use_container_width=True para ficar nos limites da coluna
        st.plotly_chart(fig_vendas_estados, use_container_width=True)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width=True)
        st.plotly_chart(fig_vendas_categorias, use_container_width=True)
    #st.dataframe(dados)
    #st.write(dados)
        
with aba3:
    qtd_vendedores = st.number_input('Quantidade de Vendedores:', 2, 10, 5) # min, max, default (2,10,5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        #fazemos a figura aqui, pois precisamos da qtd_vendedores para passar
        #pegamos a somda receirta por vendedor, obtendo somente os n maiores valores
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        
        fig_receita_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                        x = 'count',
                                        y = vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_receita_vendedores)