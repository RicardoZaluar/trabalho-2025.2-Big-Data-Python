import streamlit as st 
import pandas as pd
import plotly.express as px
from utilitarios import to_excel

def relatorio_saidas(df1,df2):
    st.header("📉 Relatório de Saídas")
    st.info("Lista de Segurados que tinham seguro em 2023 e NÃO renovaram em 2024.")


    df_merge = df1.merge(df2, on='Segurado', how='left', indicator=True, suffixes=('_2024', '_2025'))
    
    df_saidos = df_merge[df_merge['_merge'] == 'left_only'].copy()

    cols_view = ['Segurado', 'Final de Vigência_2024', 'Seguradora_2024', 'Ramo_2024']
    
    cols_existentes = [c for c in cols_view if c in df_saidos.columns]
    
    if not df_saidos.empty:
        resultado = df_saidos[cols_existentes].drop_duplicates(subset=['Segurado'])
        
        
        resultado = resultado.rename(columns={
            'Final de Vigência_2024': 'Fim Vigência',
            'Seguradora_2024': 'Seguradora (Anterior)',
            'Ramo_2024': 'Ramo'
        })
        
        colunas_ordenadas = ['Segurado', 'Seguradora (Anterior)','Ramo','Fim Vigência',]

        resultado=resultado[colunas_ordenadas]

        if 'Fim Vigência' in resultado.columns:
            resultado['Fim Vigência'] = resultado['Fim Vigência'].dt.strftime('%d/%m/%Y')

        st.metric("Total de Clientes Perdidos", len(resultado))
        st.dataframe(resultado, use_container_width=True, hide_index=True)
        
        st.download_button("💾 Baixar Lista de Saídas", data=to_excel(resultado),file_name="Clientes_Saida.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.success("Nenhum cliente saiu neste período (com base nos filtros atuais).")

def relatorio_entradas(df1,df2):
    st.header("📈 Relatório de Novos Clientes")
    st.info("Lista de Segurados que estão em 2024 mas NÃO estavam em 2025.")

    
    df_merge = df2.merge(df1, on='Segurado', how='left', indicator=True, suffixes=('_2025', '_2024'))
    
    df_entradas = df_merge[df_merge['_merge'] == 'left_only'].copy()

    cols_view = ['Segurado', 'Final de Vigência_2025', 'Seguradora_2025', 'Ramo_2025']
    cols_existentes = [c for c in cols_view if c in df_entradas.columns]

    if not df_entradas.empty:
        resultado = df_entradas[cols_existentes].drop_duplicates(subset=['Segurado'])
        
        resultado = resultado.rename(columns={
            'Final de Vigência_2025': 'Fim Vigência',
            'Seguradora_2025': 'Seguradora (Atual)',
            'Ramo_2025': 'Ramo'
        })

        colunas_ordenadas = ['Segurado', 'Seguradora (Atual)','Ramo','Fim Vigência',]

        resultado=resultado[colunas_ordenadas]

        if 'Fim Vigência' in resultado.columns:
            resultado['Fim Vigência'] = resultado['Fim Vigência'].dt.strftime('%d/%m/%Y')

        st.metric("Total de Novos Clientes", len(resultado))
        st.dataframe(resultado, use_container_width=True, hide_index=True)
        
        st.download_button("💾 Baixar Lista de Entradas", data=to_excel(resultado), file_name="Clientes_Novos.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.warning("Nenhum cliente novo encontrado.")


def comparativo_ent_sai(df1,df2):
    st.header("📊 Comparativo Entradas vs Saídas")
    
    m1 = df1.merge(df2, on='Segurado', how='left', indicator=True)
    qtd_saidas = m1[m1['_merge'] == 'left_only']['Segurado'].nunique()
    
    m2 = df2.merge(df1, on='Segurado', how='left', indicator=True)
    qtd_entradas = m2[m2['_merge'] == 'left_only']['Segurado'].nunique()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        df_chart = pd.DataFrame({
            'Tipo': ['Saída (Perda)', 'Entrada (Ganho)'],
            'Quantidade': [qtd_saidas, qtd_entradas],
            'Cor': ['#cf0606', '#0617cf'] 
        })
        fig = px.bar(df_chart, x='Tipo', y='Quantidade', color='Tipo', 
                     color_discrete_map={'Saída (Perda)': '#cf0606', 'Entrada (Ganho)': '#0617cf'},
                     text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        saldo = qtd_entradas - qtd_saidas
        st.metric("Saldo Líquido", saldo, delta=saldo)


def comparacoes(df,target_col):
    st.header(f"📋 Quantitativo por {target_col}")
    
    tipo = st.radio("Visualização:", ["Total Anual (2024)", "Mensal (2024)"], horizontal=True, key=f"radio_{target_col}")
    
    df_view = df.copy()
    
    if "Mensal" in tipo:
        meses = sorted(df_view['Mensal'].dropna().unique())
        mes = st.selectbox("Selecione o Mês:", meses, key=f"sel_{target_col}")
        df_view = df_view[df_view['Mensal'] == mes]
        st.caption(f"Exibindo dados do mês {mes}")
    
    if not df_view.empty:
        
        counts = df_view[target_col].value_counts().reset_index()
        counts.columns = [target_col, 'Apólices']
        
        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(counts, x=target_col, y='Apólices', text_auto=True, title=f"Distribuição por {target_col}")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.dataframe(counts, use_container_width=True)
            st.download_button(f"💾 Baixar Excel {target_col}", data=to_excel(counts),file_name=f"Quantidade_por_{target_col}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def migracoes(df1,df2):
    st.header("🔀 Migração entre Seguradoras")
    st.info("Clientes que continuam na corretora, mas mudaram de Seguradora.")
    
    tipo_chave = st.radio(
        "Critério de Comparação:",
        ["Apenas por Nome do Segurado (Padrão)", "Nome + Descrição do Seguro (Restrito)"],
        help="Use 'Nome + Descrição' se quiser diferenciar apólices (ex: Carro 1 vs Carro 2)."
    )
    
    merge_keys = ['Segurado']
    if "Descrição" in tipo_chave:
        merge_keys = ['Segurado', 'Descrição do Seguro']

    df_mig = df1.merge(df2, on=merge_keys, how='inner', suffixes=('_2024', '_2025'))
    
    df_trocas = df_mig[df_mig['Seguradora_2024'] != df_mig['Seguradora_2025']].copy()
    
    if not df_trocas.empty:
        view_mode = st.selectbox("Visualizar:", ["Para onde foram? (Destino)", "De onde saíram? (Origem)"])
        
        if "Destino" in view_mode:
            col_analise = 'Seguradora_2025'
            titulo_chart = "Seguradoras que GANHARAM migrações"
        else:
            col_analise = 'Seguradora_2024'
            titulo_chart = "Seguradoras que PERDERAM migrações"
            
        counts = df_trocas[col_analise].value_counts().reset_index()
        counts.columns = ['Seguradora', 'Qtd Trocas']
        
        st.plotly_chart(px.bar(counts, x='Seguradora', y='Qtd Trocas', title=titulo_chart, color='Qtd Trocas'), use_container_width=True)
        
        with st.expander("Ver Tabela Detalhada"):
            cols_detalhe = ['Segurado', 'Seguradora_2024', 'Seguradora_2025', 'Ramo_2024']
            st.dataframe(df_trocas[cols_detalhe].drop_duplicates(), use_container_width=True)
            
            st.download_button("💾 Baixar Relatório de Migração", data=to_excel(df_trocas[cols_detalhe]),file_name="Migrações.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("Nenhuma troca de seguradora detectada para os clientes filtrados.")


def novos_seguros(df1,df2):

    st.header("🆕 Novos Seguros (Por Descrição)")
    

    df1['Descrição do Seguro'] = df1['Descrição do Seguro'].astype(str).str.strip()
    df2['Descrição do Seguro'] = df2['Descrição do Seguro'].astype(str).str.strip()
    
    df_merge = df2.merge(df1, on=['Descrição do Seguro'], how='left', indicator=True, suffixes=('_2025', '_2024'))
    df_novos = df_merge[df_merge['_merge'] == 'left_only'].copy()
    
    if not df_novos.empty:
        cols_show = ['Segurado_2025', 'Descrição do Seguro', 'Seguradora_2025', 'Final de Vigência_2025']
        
        if 'Segurado_2025' not in df_novos.columns and 'Segurado' in df_novos.columns:
            df_novos.rename(columns={'Segurado': 'Segurado_2025'}, inplace=True)
            
        final_view = df_novos[cols_show].drop_duplicates(subset=['Descrição do Seguro'])
        
        if 'Final de Vigência_2025' in final_view.columns:
            final_view['Final de Vigência_2025'] = final_view['Final de Vigência_2025'].dt.strftime('%d/%m/%Y')

        st.metric("Total Novas Apólices", len(final_view))
        st.dataframe(final_view, use_container_width=True)
        st.download_button("💾 Baixar Novos Seguros", data=to_excel(final_view),file_name="Novos_Seguros.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("Nenhuma nova apólice encontrada com descrição diferente das anteriores.")