import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import locale
from bid_pagina import PageBidContratos
from google.oauth2 import service_account
import gspread
from concurrent.futures import ThreadPoolExecutor
import io


# Configuração inicial
st.set_page_config('Consulta Bid', layout='wide', page_icon='jogador.ico')

# Definir senha correta
SENHA_DE_ACESSO = st.secrets['SENHA_TOKEN']

# Credenciais
GDRIVE_AUTHENTICATION = st.secrets["gdrive"]

CREDENTIALS = service_account.Credentials.from_service_account_info(GDRIVE_AUTHENTICATION, scopes=["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"])

# Conectar ao Google Drive
GDRIVE = gspread.authorize(CREDENTIALS)


def ler_arquivo_nuvem(
        file_id: str, 
        folder_id: str = None
    ):

    try:
        
        download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"

        # Fazer download do arquivo CSV
        response = GDRIVE.request('get',download_url)

        response.raise_for_status()  # Levanta um erro se o download falhar
        
        # Ler o conteúdo do CSV em um DataFrame
        csv_content = response.content.decode('utf-8')
        leia = pd.read_csv(io.StringIO(csv_content))
        
        print('Terminei de ler:', file_id)
        return leia
    except Exception as e:
        st.error(f"Erro ao ler {file_id}: {e}")



def carrega_arquivos_nuvem():
    folder_id = st.secrets['folder_id']

    # URL do Google Drive API para listar arquivos na pasta
    url = f"https://www.googleapis.com/drive/v3/files?q='{folder_id}'+in+parents"

    # Faça a requisição para listar os arquivos na pasta
    response = GDRIVE.request('get', url)

    if response.status_code != 200:
        raise Exception(f"Erro ao listar arquivos: {response.content.decode('utf-8')}")

    files = response.json()['files']

    file_ids = [file['id'] for file in files]
    
    # Criar um pool de threads para executar as tarefas em paralelo
    with ThreadPoolExecutor() as executor:
        resultados = executor.map(lambda file_id: ler_arquivo_nuvem(file_id, folder_id), file_ids)

    return pd.concat(resultados).reset_index(drop=True)




# Função para carregar dados

@st.cache_data
def read_bid() -> pd.DataFrame:
    leia = carrega_arquivos_nuvem()
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


