import streamlit as st
import pandas as pd


st.set_page_config(page_title="Silv Store - Gestão", page_icon="💍")


url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRMmO1Hb5_ZHF1derzBrM54WOoWqCbpdm6exOoRtMggjeMTM9DIgKoqBQziNLN1YBzXwPmX1rhfRcg9/pub?output=csv"


@st.cache_data
def carregar_dados():
    try:
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        
        import requests
        from io import StringIO
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            
            dados = pd.read_csv(StringIO(response.text), sep=None, engine='python')
            dados.columns = dados.columns.str.strip().str.lower()
            return dados
        else:
            st.error(f"O Google retornou erro {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Erro técnico: {e}")
        return None

df = carregar_dados()

if df is not None:
    st.title("💍 Silv Store: Gestão de Estoque")
    
    
    busca = st.text_input("Pesquisar por nome da joia:", placeholder="Ex: Anel de Prata")

    
    coluna_nome = next((c for c in df.columns if 'item' in c or 'nome' in c or 'joia' in c), df.columns[0])

    if busca:
        dados_filtrados = df[df[coluna_nome].str.contains(busca, case=False, na=False)]
    else:
        dados_filtrados = df

    
    st.subheader("📋 Estoque Atual")
    st.dataframe(dados_filtrados, width="stretch")

    
    st.divider()
    st.subheader("⚠️ Status de Reposição")

   
    coluna_qtd = next((c for c in df.columns if 'quant' in c or 'qtd' in c), None)

    if coluna_qtd:
      
        df[coluna_qtd] = pd.to_numeric(df[coluna_qtd], errors='coerce').fillna(0)
        
        estoque_critico = df[df[coluna_qtd] < 2]

        if not estoque_critico.empty:
            for index, linha in estoque_critico.iterrows():
                nome_exibir = str(linha[coluna_nome]).title()
                st.warning(f"**Repor urgente:** {nome_exibir} (Restam {int(linha[coluna_qtd])} peças)")
        else:
            st.success("✅ Todas as peças estão com estoque em dia!")
    else:
        st.error("Coluna de quantidade não encontrada. Verifique os títulos da sua planilha.")

    
    if st.button("Verificar Estado do Sistema"):
        st.write(f"Conexão com Google Sheets: OK")
        st.write(f"Total de itens catalogados: {len(df)}")

else:
    st.warning("Aguardando conexão com a planilha do Google Sheets...")