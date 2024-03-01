import streamlit as st
import requests
import pandas as pd
import time

@st.cache_data # para não fazer a criação de arquivo toda vez, caso não mude os filtros
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')
    
def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso', icon = "✅")
    time.sleep(5)
    sucesso.empty()

# DCOUMENTAÇÃO DO STREAMLIT
# https://docs.streamlit.io/


st.set_page_config(layout = 'wide') # configurando o formato de tela

st.title('DADOS BRUTOS')


#Leitura dos dados da API
url = 'https://labdados.com/produtos'
#url = 'https://labdados.com/produtos?regiao=sul?ano=2021' # exemplo de url completa com os valores dos filtros disponíveis na mesma

response = requests.get(url) 
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y') #converte a data str para datetime


### CONSTRUÇÃO DOS FILTROS
with st.expander('Colunas'): # objeto expander
    # vamos criar um filtro para seleção de colunas a serem exibidas. Passamos a lista de opções e a lista de opções que vem previamente marcadas
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

st.sidebar.title('Filtros')# uma barra lateral
with st.sidebar.expander('Nome do Produto'): # expander na barra lateral
    #vamos criar um filtro de produtos no expader da barra lateral
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())

with st.sidebar.expander('Preço do Produto'): # expander na barra lateral
    #vamos criar um filtro de preço de produtos no expader da barra lateral
    preco = st.slider('Selecione o preço', 0, 5000, (0,5000)) # nesse slider, além dos limites min e max, passamos um parametro de tupla. Dessa forma nesse slider poderemos selecionar uma faixa de valores

with st.sidebar.expander('Data da Compra'): # expander na barra lateral
    #vamos criar um filtro de data no expader da barra lateral
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))


### AQUI PODERÍAMOS FAZER UM FILTRO PARA CADA CAMPO. ERA SÓ USAR OS MODELOS ACIMA
with st.sidebar.expander('Categoria do Produto'): # expander na barra lateral
    #vamos criar um filtro de categorias no expader da barra lateral
    categorias = st.multiselect('Selecione as categorias', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())

with st.sidebar.expander('Frete'): # expander na barra lateral
    #vamos criar um filtro de frete de produtos no expader da barra lateral
    frete = st.slider('Selecione o valor do frete', 0, int(dados['Frete'].max()) + 1,  (0,int(dados['Frete'].max()) + 1))

with st.sidebar.expander('Vendedor'): # expander na barra lateral
    #vamos criar um filtro de vendedores no expander da barra lateral
    vendedores = st.multiselect('Selecione as categorias', dados['Vendedor'].unique(), dados['Vendedor'].unique())

with st.sidebar.expander('Local da compra'): # expander na barra lateral
    #vamos criar um filtro de estados no expander da barra lateral
    estados = st.multiselect('Selecione os Locais da Compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())

with st.sidebar.expander('Avaliação da compra'): # expander na barra lateral
    #vamos criar um filtro de avaliações no expader da barra lateral
    avaliacoes = st.slider('Selecione o valor da avaliação', 1, int(dados['Avaliação da compra'].max()) ,  (1, int(dados['Avaliação da compra'].max()) ))

with st.sidebar.expander('Tipo de pagamento'): # expander na barra lateral
    #vamos criar um filtro de tipos de pagamentos no expander da barra lateral
    tipo_pagamento = st.multiselect('Selecione os tipos de pagamentos', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())

with st.sidebar.expander('Quantidade de parcelas'): # expander na barra lateral
    #vamos criar um filtro de qtd de parcelas no expader da barra lateral
    qtd_parcelas = st.slider('Selecione o valor da avaliação', 1, int(dados['Quantidade de parcelas'].max()),  (1, int(dados['Quantidade de parcelas'].max()) ))


### APLICAÇÃO DOS FILTROS SELECIONADOS
# uma query string do pandas. @ referencia a variável(que utizamos para guardr o valor dos filtros)
# Data de compra, por conter espaços, colocamos enre crases dentrro da string
# \ é apenas para pular de linha
query = '''
Produto in @produtos and \
@preco[0] <= Preço <= @preco[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1]
'''

## Acrescentando os outros atributos na filtragem 
query = '''
Produto in @produtos and \
@preco[0] <= Preço <= @preco[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1]  and \
`Categoria do Produto` in @categorias and \
@frete[0] <= Frete <= @frete[1] and \
Vendedor in @vendedores and \
`Local da compra` in @estados and \
@avaliacoes[0] <= `Avaliação da compra` <= @avaliacoes[1] and \
`Tipo de pagamento` in @tipo_pagamento and \
@qtd_parcelas[0] <= `Quantidade de parcelas` <= @qtd_parcelas[1]
'''


###efetivando a filtragem
## linhas
dados_filtrados = dados.query(query)
## colunas
dados_filtrados = dados_filtrados[colunas]


#st.dataframe(dados)
st.dataframe(dados_filtrados)

# um markdown (para saída de texto formatado)
# informando numero de linhas e colunas
st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input(' ', label_visibility = 'collapsed', value = 'dados') # o label já esta no markdown
    nome_arquivo += '.csv'
with coluna2:
    st.download_button('Fazer o donwload da tabela em csv', data = converte_csv(dados_filtrados), file_name=nome_arquivo, mime='text/csv', on_click = mensagem_sucesso)
