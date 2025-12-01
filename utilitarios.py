import pandas as pd
import io 
import xlsxwriter
import streamlit as st

@st.cache_data
def load_data(file_path_or_buffer):
    try:
        df = pd.read_excel(file_path_or_buffer)
        return df
    except Exception as e:
        return None

def tratar_dados(df_raw):
    if df_raw is None:
        return None
    
    df = df_raw.copy()
    cols_str = ['Segurado','Seguradora','Ramo', 'Descrição do Seguro', 'Produtor']
    for col in cols_str:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    if 'Final de Vigência' in df.columns:
        df['Final de Vigência'] = pd.to_datetime(df['Final de Vigência'], errors='coerce')
        df['Mensal'] = df['Final de Vigência'].dt.strftime('%m')
    
    return df

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Relatorio')
    return output.getvalue()

