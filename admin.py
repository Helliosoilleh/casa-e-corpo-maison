import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Admin - Casa e Corpo Maison", layout="wide")

ARQUIVO_CSV = "produtos.csv"

# Carrega produtos
def carregar_produtos():
    if os.path.exists(ARQUIVO_CSV):
        return pd.read_csv(ARQUIVO_CSV)
    else:
        return pd.DataFrame(columns=["id", "nome", "categoria", "preco", "estoque", "descricao", "imagem"])

def salvar_produtos(df):
    df.to_csv(ARQUIVO_CSV, index=False)

df = carregar_produtos()

st.title("🛍️ Administrativo - Casa e Corpo Maison")

aba1, aba2 = st.tabs(["📦 Gerenciar Produtos", "➕ Cadastrar Novo"])

with aba1:
    st.subheader("Pesquisar, Editar e Excluir")

    # --- PESQUISAR (QUE TINHA SUMIDO) ---
    busca = st.text_input("🔍 Pesquisar produto por nome", placeholder="Digite o nome...")

    if busca:
        df_filtrado = df[df["nome"].str.contains(busca, case=False, na=False)]
    else:
        df_filtrado = df

    st.write(f"Encontrados: {len(df_filtrado)} produtos")

    # Lista produtos com botões
    for index, row in df_filtrado.iterrows():
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(f"**{row['nome']}** - R$ {row['preco']} | Estoque: {row['estoque']}")
                st.caption(f"{row['categoria']} | ID: {row['id']}")
            with col2:
                # --- EDITAR (QUE TINHA SUMIDO) ---
                if st.button("✏️ Editar", key=f"edit_{row['id']}"):
                    st.session_state["edit_id"] = row["id"]
            with col3:
                # --- EXCLUIR (QUE TINHA SUMIDO) ---
                if st.button("🗑️ Excluir", key=f"del_{row['id']}", type="primary"):
                    st.session_state["delete_id"] = row["id"]

    # Lógica de Excluir com confirmação
    if "delete_id" in st.session_state:
        id_del = st.session_state["delete_id"]
        produto_del = df[df["id"] == id_del].iloc[0]
        st.warning(f"Tem certeza que quer excluir **{produto_del['nome']}**?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Sim, excluir agora"):
                df = df[df["id"]!= id_del]
                salvar_produtos(df)
                del st.session_state["delete_id"]
                st.success("Produto excluído!")
                st.rerun()
        with c2:
            if st.button("Cancelar"):
                del st.session_state["delete_id"]
                st.rerun()

    # Lógica de Editar
    if "edit_id" in st.session_state:
        id_edit = st.session_state["edit_id"]
        dados = df[df["id"] == id_edit].iloc[0]
        st.divider()
        st.subheader(f"Editando: {dados['nome']}")
        with st.form("form_editar"):
            nome = st.text_input("Nome", value=dados["nome"])
            categoria = st.text_input("Categoria", value=dados["categoria"])
            preco = st.number_input("Preço", value=float(dados["preco"]))
            estoque = st.number_input("Estoque", value=int(dados["estoque"]))
            descricao = st.text_area("Descrição", value=dados["descricao"])

            if st.form_submit_button("Salvar Edição"):
                df.loc[df["id"] == id_edit, ["nome", "categoria", "preco", "estoque", "descricao"]] = [nome, categoria, preco, estoque, descricao]
                salvar_produtos(df)
                del st.session_state["edit_id"]
                st.success("Editado com sucesso!")
                st.rerun()

with aba2:
    st.subheader("Cadastrar Novo Produto")
    with st.form("form_cadastro"):
        nome = st.text_input("Nome do produto")
        categoria = st.text_input("Categoria")
        preco = st.number_input("Preço", min_value=0.0)
        estoque = st.number_input("Estoque", min_value=0)
        descricao = st.text_area("Descrição")
        imagem = st.text_input("Link da imagem")

        if st.form_submit_button("Cadastrar"):
            novo_id = int(df["id"].max() + 1) if not df.empty else 1
            novo = pd.DataFrame([[novo_id, nome, categoria, preco, estoque, descricao, imagem]], columns=df.columns)
            df = pd.concat([df, novo], ignore_index=True)
            salvar_produtos(df)
            st.success(f"Produto {nome} cadastrado!")
            st.rerun()
