import streamlit as st
import pandas as pd

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Silv Store - Gestão", page_icon="💍")

# 1. CONEXÃO COM OS DADOS
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRMmO1Hb5_ZHF1derzBrM54WOoWqCbpdm6exOoRtMggjeMTM9DIgKoqBQziNLN1YBzXwPmX1rhfRcg9/pub?output=csv"


@st.cache_data
def carregar_dados():
    try:
        # Criamos um "disfarce" para o Google não bloquear a conexão
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # O Pandas tenta ler o link diretamente com o disfarce
        import requests
        from io import StringIO
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # Transforma o texto recebido em uma planilha
            dados = pd.read_csv(StringIO(response.text), sep=None, engine='python')
            dados.columns = dados.columns.str.strip().str.lower()
            return dados
        else:
            st.error(f"O Google retornou erro {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Erro técnico: {e}")
        return None
# INÍCIO DO BLOCO PRINCIPAL
df = carregar_dados()

if df is not None:
    st.title("💍 Silv Store: Gestão de Estoque")
    
    # 2. SISTEMA DE BUSCA
    busca = st.text_input("Pesquisar por nome da joia:", placeholder="Ex: Anel de Prata")

    # Identifica a coluna de nome (pode ser 'item', 'nome' ou 'joia')
    coluna_nome = next((c for c in df.columns if 'item' in c or 'nome' in c or 'joia' in c), df.columns[0])

    if busca:
        dados_filtrados = df[df[coluna_nome].str.contains(busca, case=False, na=False)]
    else:
        dados_filtrados = df

    # 3. EXIBIÇÃO DA TABELA (Sintaxe 2026)
    st.subheader("📋 Estoque Atual")
    st.dataframe(dados_filtrados, width="stretch")

    # 4. LÓGICA DE ALERTAS (REGRA DE NEGÓCIO)
    st.divider()
    st.subheader("⚠️ Status de Reposição")

    # Tenta encontrar a coluna de quantidade
    coluna_qtd = next((c for c in df.columns if 'quant' in c or 'qtd' in c), None)

    if coluna_qtd:
        # Converte para número para evitar erros de comparação
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

    # 5. BOTÃO DE VERIFICAÇÃO (EXTENSÃO UNOPAR)
    if st.button("Verificar Estado do Sistema"):
        st.write(f"Conexão com Google Sheets: OK")
        st.write(f"Total de itens catalogados: {len(df)}")

else:
    st.warning("Aguardando conexão com a planilha do Google Sheets...")