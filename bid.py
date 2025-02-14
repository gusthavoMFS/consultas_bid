import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import locale
from bid_pagina import PageBidContratos

# Configuração inicial
st.set_page_config('Consulta Bid', layout='wide', page_icon='jogador.ico')

# Definir senha correta
SENHA_DE_ACESSO = st.secrets['SENHA_TOKEN']




# Função para carregar dados
@st.cache_data
def read_bid_cbf() -> pd.DataFrame:
    leia = pd.read_csv(rf'bid.csv')
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
        leia = read_bid_cbf()

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


#print(st.session_state)