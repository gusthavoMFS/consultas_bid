import pandas as pd
import streamlit as st

class PageBidContratos:

    def __init__(self) -> None:
        return
    


    def get_string_selecione_jogador(
            self,
            equipes_selecionado: str,
            anos_selecionado: str,
            letra_selecionada: str,
        ):

        string_selecione_jogador = 'Selecione um jogador ('
        
        if equipes_selecionado != 'Todas' and anos_selecionado != 'Todos':
            string_selecione_jogador += f' {equipes_selecionado} ; {anos_selecionado}'
        elif equipes_selecionado != 'Todas':
            string_selecione_jogador += f' {equipes_selecionado}'
        elif anos_selecionado != 'Todos':
            string_selecione_jogador += f' {anos_selecionado}'

        if letra_selecionada is not None:
            string_selecione_jogador += f' ; Inicial: {letra_selecionada}'
        
        string_selecione_jogador += ')'

        return string_selecione_jogador



    def run_page(self):

        icon_html = """
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
         <h1 style="display: flex; align-items: center;">
            Consulta Bid Contratos
            <span class="material-symbols-outlined">
                contract
            </span>
            </h1>
        """

        '''
        <span class="material-symbols-outlined">
            sports_soccer
        </span>
        '''
        
        st.markdown(icon_html,unsafe_allow_html=True)

        df_bid: pd.DataFrame = st.session_state['bid_contratos']
        
        nomes_jogadores : list = st.session_state['nomes_jogadores'] #list(df_bid['Nome'].unique())
        anos : list = st.session_state['anos'] #['Todos'] + list(df_bid['Ano de Publicação do contrato'].unique())
        equipes: list = st.session_state['equipes'] #['Todas'] + list(df_bid['Clube'].unique())

        lista_A_Z = [chr(i) for i in range(65,91)]


        with st.container():

            anos_selecionado = st.selectbox('Selecione um ano',anos,index=0,placeholder='Ano')

            # Filtro de ano
            if anos_selecionado != 'Todos':
                filtro_ano = df_bid.loc[df_bid['Ano de Publicação do contrato'] == anos_selecionado].reset_index(drop=True)
                nomes_jogadores_usar = filtro_ano
                equipes_usar = ['Todas'] + list(filtro_ano['Clube'].unique())
                letra_selecionado = None

            # Todos os anos
            else:
                equipes_usar = equipes.copy()
            

            # Selecionar equipe
            string_selecione_equipe = 'Selecione uma equipe' if anos_selecionado == 'Todos' else f'Selecione uma equipe (Ano {anos_selecionado})'
            #equipes_selecionado = st.multiselect(string_selecione_equipe,equipes_usar,placeholder='Equipe',max_selections=3)
            equipes_selecionado = st.selectbox(string_selecione_equipe,equipes_usar,index=0,placeholder='Equipe')


            # Filtro para Jogadores que começam com a letra x
            if anos_selecionado == 'Todos':

                lista_A_Z_usar = ['Todas'] + lista_A_Z if equipes_selecionado != 'Todas' else lista_A_Z

                letra_selecionado = st.selectbox('Selecione a inicial do nome de um jogador',lista_A_Z_usar,key='letra_selecionado',placeholder='Letra',index=0)
                
                filtro = df_bid['Nome'].str.startswith(letra_selecionado,na=False)
                
                nomes_jogadores_usar = df_bid if letra_selecionado == 'Todas' else df_bid[filtro].reset_index(drop=True)
                
                    
            # Filtro jogadores da equipe
            if equipes_selecionado != 'Todas':
                nomes_jogadores_usar = nomes_jogadores_usar.loc[nomes_jogadores_usar['Clube'] == equipes_selecionado].reset_index(drop=True)

            nomes_jogadores_usar = ['Todos'] + list(nomes_jogadores_usar['Nome'].unique()) #if anos_selecionado == 'Todos' else ['Todos'] + list(nomes_jogadores_usar['Nome'].unique())
            

            # Lógica para string de jogador (Ano-Clube)
            string_selecione_jogador = self.get_string_selecione_jogador(equipes_selecionado,anos_selecionado,letra_selecionado)

            
            # Filtro para jogadores
            jogador_selecionado = st.selectbox(string_selecione_jogador,nomes_jogadores_usar,index=None,placeholder='Jogador',key='jogadores_bid')


            if st.button('Consultar'):

                mostrar = df_bid.copy()
                
                if anos_selecionado != 'Todos':
                    mostrar = mostrar.loc[mostrar['Ano de Publicação do contrato'] == anos_selecionado].reset_index(drop=True)
                
                if letra_selecionado is not None:
                    if letra_selecionado != 'Todas':
                        mostrar = mostrar.loc[mostrar['Nome'].str.startswith(letra_selecionado,na=False)].reset_index(drop=True)

                if equipes_selecionado != 'Todas':
                    mostrar = mostrar.loc[mostrar['Clube'] == equipes_selecionado].reset_index(drop=True)

                if jogador_selecionado != 'Todos':
                    mostrar = mostrar.loc[mostrar['Nome'] == jogador_selecionado].reset_index(drop=True)

                # Mostrar o dataframe

                mostrar.sort_values('Data de Publicação do contrato',inplace=True)
                mostrar.reset_index(drop=True,inplace=True)
                
                st.dataframe(mostrar)
                print(anos_selecionado,letra_selecionado,equipes_selecionado,jogador_selecionado)

                if mostrar.empty:
                    st.error('🛈 Não foram encontrados contratos com os tipos de filtros selecionados!')

        return
    