import streamlit as st
import utilitarios as ut
import analise as an


st.set_page_config(page_title="Corretora Rio do A - Big Data", layout="wide")
st.title("📊 Sistema de Análise - Corretora Rio do A")
st.markdown("---")


st.sidebar.header("📂 1. Carregar Dados")


path_2024 = r"D:\projeto_bigdata_2025\Document2024.xls"
path_2025 = r"D:\projeto_bigdata_2025\Document2025.xls"


upload_2024 = st.sidebar.file_uploader("Upload Planilha 2024 (XLS/XLSX)", type=["xls", "xlsx"])
upload_2025 = st.sidebar.file_uploader("Upload Planilha 2025 (XLS/XLSX)", type=["xls", "xlsx"])


df1_raw = ut.load_data(upload_2024) if upload_2024 else ut.load_data(path_2024)
df2_raw = ut.load_data(upload_2025) if upload_2025 else ut.load_data(path_2025)

if df1_raw is None or df2_raw is None:
    st.error("❌ Erro: Arquivos não carregados.")
    st.stop

try:
    df1 = ut.tratar_dados(df1_raw)
    df2 = ut.tratar_dados(df2_raw)
    st.toast("Dados processados!", icon="✅")
except Exception as e:
    st.error(f"Erro ao tratar: {e}")
    st.stop()

st.sidebar.header("🔍 2. Filtros")
ramos_unicos = sorted(list(set(df1['Ramo'].unique()) | set(df2['Ramo'].unique())))
ramos_padrao = ['AUTOMÓVEL', 'RESIDÊNCIA', 'EMPRESA']
ramos_padrao_validos = [r for r in ramos_padrao if r in ramos_unicos]
ramos_sel = st.sidebar.multiselect("Selecione os Ramos:", ramos_unicos, default=ramos_padrao_validos)

# Aplicar filtros
df1_f = df1[df1['Ramo'].isin(ramos_sel)].copy()
df2_f = df2[df2['Ramo'].isin(ramos_sel)].copy()

# navegação
st.sidebar.header("📊 3. Escolha a Análise")
opcao = st.sidebar.radio(
    "Menu:",
    [
        "1. Clientes que Saíram",
        "2. Clientes Novos",
        "3. Comparativo Entradas vs Saídas",
        "4. Quantitativo por Seguradora",
        "5. Migração (Troca de Seguradora)",
        "6. Novos Seguros (Apólices)",
        "7. Quantitativo por Produtor"
    ]
)
if "1" in opcao:
    an.relatorio_saidas(df1_f,df2_f)
elif "2" in opcao:
    an.relatorio_entradas(df1_f,df2_f)
elif "3" in opcao: 
    an.comparativo_ent_sai(df1_f,df2_f)
elif "4" in opcao or "7" in opcao:
    coluna_selecionada = "Seguradora" if "4" in opcao else "Produtor"
    an.comparacoes(df2_f,coluna_selecionada)
elif "5" in opcao:
    an.migracoes(df1_f,df2_f)
elif "6" in opcao:
    an.novos_seguros(df1_f,df2_f)

st.markdown("---")
st.caption("Painel desenvolvido para Corretora Rio do A")