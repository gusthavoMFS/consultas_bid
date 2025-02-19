import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import locale
from bid_pagina import PageBidContratos
from google.oauth2 import service_account
import gspread
from concurrent.futures import ThreadPoolExecutor


# Configuração inicial
st.set_page_config('Consulta Bid', layout='wide', page_icon='jogador.ico')

# Definir senha correta
SENHA_DE_ACESSO = st.secrets['SENHA_TOKEN']


def ler_arquivo_nuvem(gc, nome_arquivo: str):
    print('Lendo:', nome_arquivo)
    
    worksheet = gc.open(nome_arquivo).sheet1
    rows = worksheet.get_all_values()

    # Criar DataFrame e remover cabeçalho duplicado
    leia = pd.DataFrame.from_records(rows, columns=rows[0])
    leia.drop(0, axis=0, inplace=True)

    print('Terminei de ler:', nome_arquivo)
    return leia


# 🔹 Função para carregar todos os arquivos em paralelo
def carrega_arquivos_nuvem(gc):

    planilhas: str = st.secrets['planilhas_contratos']

    planilhas = planilhas.split(';')

    # Criar um pool de threads para executar as tarefas em paralelo
    with ThreadPoolExecutor() as executor:
        resultados = executor.map(lambda nome: ler_arquivo_nuvem(gc, nome), planilhas)

    return pd.concat(resultados).reset_index(drop=True)



# Função para carregar dados

@st.cache_data
def read_bid() -> pd.DataFrame:

    secrets = st.secrets["gdrive"]

    # Credenciais
    credentials = service_account.Credentials.from_service_account_info(secrets, scopes=["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"])

    # Conectar ao Google Drive
    gc = gspread.authorize(credentials)

    leia = carrega_arquivos_nuvem(gc)

    return leia


@st.cache_resource
def logado():
    st.session_state['logado'] = True
    return


def get_pages():
    the_pages = {
    'Bid': PageBidContratos()
    }
    return the_pages



# Páginas do dashboard
the_pages = get_pages()

# Função para exibir a tela de login
def login_page():
    placeholder1 = st.empty()
    placeholder2 = st.empty()

    placeholder1.markdown(
        """
        <h1 style='text-align: center; color: white;font-size: 40px;'>
        Senha de acesso
        </h1>
        """,
        unsafe_allow_html=True
    )

    senha_de_acesso = placeholder2.text_input('', placeholder='Senha', key='senha_acesso', type='password')

    if senha_de_acesso == SENHA_DE_ACESSO:
        logado()
        st.session_state['senha_verificada'] = True
        placeholder1.empty()
        placeholder2.empty()
        st.rerun()
        #st.switch_page('bid_pagina.py')
    elif senha_de_acesso != '':
        st.error('🛈 Senha de acesso incorreta!')



# Função para exibir a página principal


def pagina_bid():

    if 'bid_contratos' not in st.session_state:
        leia = read_bid()

        leia = leia.sort_values('Nome').reset_index(drop=True)
        leia_ordenado_por_clube = leia.sort_values('Clube').reset_index(drop=True)


        nomes_jogadores = list(leia['Nome'].unique())
        nomes_jogadores = [str(nome) for nome in nomes_jogadores].sort(key=locale.strxfrm)
        
        anos = ['Todos'] + sorted(list(leia['Ano de Publicação do contrato'].unique()))
        equipes = ['Todas'] + list(leia_ordenado_por_clube['Clube'].unique())
        st.session_state['bid_contratos'] = leia
        st.session_state['nomes_jogadores'] = nomes_jogadores
        st.session_state['anos'] = anos
        st.session_state['equipes'] = equipes

    # Barra de navegação
    with st.sidebar:
        pagina = option_menu(
            "Consultas Bid", ["Bid"],
            icons=['journal-text'],
            menu_icon="award", default_index=0
        )

    the_pages[pagina].run_page()


if 'senha_verificada' not in st.session_state:
    st.session_state['senha_verificada'] = False


# Lógica principal
if st.session_state['senha_verificada'] or 'logado' in st.session_state:
    pagina_bid()
else:
    login_page()


