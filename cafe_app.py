# ==============================================================================
# DOCUMENTAÇÃO: CAFÉ ANALYTICS & INVENTORY APP (Streamlit)
# Objetivo: Criar uma interface web interativa APENAS com Python para gestão de café.
# Linguagem: Python 3 (Streamlit, Pandas, JSON)
# ==============================================================================

import streamlit as st
import json
import os
import pandas as pd

# Nome do ficheiro onde os dados serão guardados (Persistência)
DATA_FILE = 'cafe_data_st.json'

# --- 1. GESTÃO DE DADOS PERSISTENTES ---

def carregar_dados_iniciais():
    """Define a estrutura inicial dos dados se o ficheiro não existir."""
    return {
        "vendas_diarias": {
            "Expresso": 15,
            "Cappuccino": 8,
            "Bolo de Cenoura": 4
        },
        "inventario": {
            # [Stock Atual, Preço de Custo, Nível Mínimo de Alerta]
            "Leite (Litros)": [50, 1.00, 10],   
            "Café (KG)": [15, 15.00, 3],
            "Pão (Unidades)": [3, 0.50, 5] # Exemplo de stock baixo
        },
        "precos_produtos": {
            "Expresso": 1.50,
            "Cappuccino": 3.00,
            "Bolo de Cenoura": 2.50
        }
    }

@st.cache_data
def carregar_dados():
    """Carrega os dados do ficheiro JSON ou cria dados iniciais. Usando cache do Streamlit."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return carregar_dados_iniciais()
    else:
        return carregar_dados_iniciais()

def guardar_dados(dados):
    """Guarda os dados atuais no ficheiro JSON."""
    with open(DATA_FILE, 'w') as f:
        json.dump(dados, f, indent=4)
    # Importante: Limpar o cache para garantir que a próxima leitura use os novos dados
    st.cache_data.clear()


# --- 2. FUNÇÕES DE LÓGICA DE NEGÓCIO ---

def registar_venda(dados, produto, quantidade=1):
    """Regista uma nova venda e guarda os dados."""
    vendas = dados["vendas_diarias"]
    if produto in vendas:
        vendas[produto] += quantidade
        guardar_dados(dados)
        st.success(f"✅ Venda de {quantidade}x {produto} registada e dados atualizados!")
    else:
        st.error(f"❌ Produto '{produto}' não encontrado.")

def analisar_vendas(dados):
    """Calcula a receita total e o produto mais vendido para exibição no Streamlit."""
    vendas = dados["vendas_diarias"]
    precos = dados["precos_produtos"]
    
    receita_total = 0
    for produto, quantidade in vendas.items():
        preco = precos.get(produto, 0)
        receita_total += quantidade * preco

    produto_mais_vendido = max(vendas, key=vendas.get)
    max_vendas = vendas[produto_mais_vendido]
    
    return receita_total, produto_mais_vendido, max_vendas, vendas

def verificar_inventario(dados):
    """Gera uma lista de alertas de stock baixo."""
    invent = dados["inventario"]
    alertas = []

    for item, detalhes in invent.items():
        stock_atual = detalhes[0]
        alerta_minimo = detalhes[2]

        if stock_atual < alerta_minimo:
            alertas.append(f"🚨 ALERTA BAIXO: {item}: {stock_atual} (Mínimo: {alerta_minimo})")
            
    return alertas, invent


# --- 3. INTERFACE STREAMLIT ---

def main():
    """Função principal para construir a interface Streamlit."""
    
    st.set_page_config(layout="wide") # Layout mais amplo para dashboards
    st.title("☕ Painel de Controlo do Café (Streamlit)")
    
    dados = carregar_dados()

    # --- TABELA DE VENDAS E INVENTÁRIO (MELHORAR VENDAS & DIMINUIR PERDAS) ---
    
    # Colunas para organizar o layout
    col1, col2 = st.columns(2)

    with col1:
        st.header("1. Registar Venda Rápida")
        
        produtos_disp = list(dados["vendas_diarias"].keys())
        
        # Widget de seleção
        produto_selecionado = st.selectbox(
            "Selecione o produto vendido:",
            produtos_disp,
            key='produto_venda'
        )
        
        # Botão para registar
        if st.button(f"Registar 1x {produto_selecionado}", type="primary"):
            registar_venda(dados, produto_selecionado, 1)

    with col2:
        st.header("2. Análise de Vendas e Inventário")
        
        receita, produto_mais_vendido, max_vendas, vendas_atuais = analisar_vendas(dados)
        alertas, inventario_atual = verificar_inventario(dados)

        # Exibir a Receita e o Produto Mais Vendido (Melhorar Vendas)
        st.metric(label="💰 Receita Bruta Total", value=f"{receita:.2f}€")
        st.markdown(f"**⭐ Produto Mais Vendido:** {produto_mais_vendido} ({max_vendas} unidades)")
        
        st.markdown("---")

        # Exibir Alertas de Inventário (Diminuir Perdas)
        st.subheader("⚠️ Alertas de Stock Baixo")
        if alertas:
            for alerta in alertas:
                st.warning(alerta)
        else:
            st.success("👍 Sem alertas de stock crítico.")

    # --- GRÁFICO DE VENDAS (Visualização Adicional) ---
    st.markdown("## 📊 Distribuição de Vendas")
    
    # Criar um DataFrame com Pandas para o gráfico
    df_vendas = pd.DataFrame(list(vendas_atuais.items()), columns=['Produto', 'Quantidade'])
    
    # Criar e mostrar o gráfico de barras
    st.bar_chart(df_vendas.set_index('Produto'))

    # --- VISUALIZAÇÃO DOS DADOS BRUTOS (Opcional) ---
    st.markdown("---")
    st.subheader("Dados Atuais (Persistentes)")
    st.dataframe(pd.DataFrame(dados["inventario"]).T.rename(columns={0: "Stock Atual", 1: "Preço Custo", 2: "Alerta Mínimo"}))


if __name__ == "__main__":
    main()