import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="Casa e Corpo Maison", page_icon="🕯️", layout="wide")

# --- CONFIG ---
PRODUTOS_FILE = Path("produtos.json")
PASTA_FOTOS = Path("midia_produtos")
PASTA_FOTOS.mkdir(exist_ok=True)

def carregar_produtos():
    if PRODUTOS_FILE.exists():
        try:
            with open(PRODUTOS_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
                if isinstance(dados, list):
                    return dados
        except:
            pass
    # Se não tiver arquivo, cria com os seus produtos atuais
    return [
        {"nome": "Camiseta Premium", "preco": "79.90", "foto": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400", "descricao": "100% algodão"},
        {"nome": "Moletom", "preco": "99.90", "foto": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400", "descricao": "Moletom unissex"},
        {"nome": "Boné", "preco": "59.90", "foto": "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=400", "descricao": "Boné trucker"},
        {"nome": "ÁRVORE DE NATAL CANADENSE", "preco": "99.90", "foto": "", "descricao": "Árvore aromática 30cm"},
        {"nome": "GUIRLANDA NATALINA 30CM", "preco": "40.00", "foto": "", "descricao": "Guirlanda com aroma de pinheiro"},
    ]

def salvar_produtos(lista):
    with open(PRODUTOS_FILE, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)

produtos = carregar_produtos()
# Garante que o arquivo exista no GitHub
if not PRODUTOS_FILE.exists():
    salvar_produtos(produtos)

# --- VERIFICA SE É ADMIN ---
is_admin = st.query_params.get("admin", "") == "true"

if is_admin:
    # ================== ÁREA DO ADMINISTRADOR ==================
    st.title("🔧 Administrador - Casa e Corpo Maison")
    st.info("Só você vê essa página. Link: ?admin=true")

    tab1, tab2 = st.tabs(["🖼️ Banner da Loja", "🕯️ Produtos"])

    with tab1:
        st.subheader("Trocar Banner do Topo")
        st.write("O banner aparece no topo da loja. Envie uma imagem deitada (ex: 1200x400).")
        banner_up = st.file_uploader("Escolher novo banner", type=["jpg","jpeg","png","webp"])
        if banner_up:
            # apaga banner antigo
            for old in Path(".").glob("banner.*"):
                old.unlink()
            ext = banner_up.name.split(".")[-1]
            Path(f"banner.{ext}").write_bytes(banner_up.getbuffer())
            st.success("Banner trocado! Volta na loja pra ver.")
            st.image(banner_up, use_container_width=True)
        
        st.write("Banner atual:")
        achou = False
        for b in Path(".").glob("banner.*"):
            st.image(str(b), use_container_width=True)
            achou = True
        if not achou:
            st.warning("Nenhum banner cadastrado ainda. A loja está sem banner no topo.")

    with tab2:
        st.subheader("Adicionar Novo Produto")
        with st.form("add_prod", clear_on_submit=True):
            nome = st.text_input("Nome do produto*")
            preco = st.text_input("Preço* (ex: 99.90)")
            desc = st.text_area("Descrição")
            foto = st.file_uploader("Foto do produto (opcional)", type=["jpg","jpeg","png","webp"])
            if st.form_submit_button("Salvar Produto"):
                foto_path = ""
                if foto:
                    foto_path = str(PASTA_FOTOS / foto.name)
                    Path(foto_path).write_bytes(foto.getbuffer())
                novo = {"nome": nome, "preco": preco, "foto": foto_path, "descricao": desc}
                produtos.append(novo)
                salvar_produtos(produtos)
                st.success(f"{nome} salvo!")
                st.rerun()

        st.divider()
        st.subheader(f"Produtos na loja ({len(produtos)}) - Você pode excluir")
        for i, p in enumerate(produtos):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                foto = p.get("foto","")
                if foto:
                    if foto.startswith("http"):
                        st.image(foto, width=80)
                    elif Path(foto).exists():
                        st.image(foto, width=80)
            with c2:
                st.write(f"**{p['nome']}** - R$ {p['preco']}")
                st.caption(p.get("descricao",""))
            with c3:
                if st.button("Excluir", key=f"del_{i}"):
                    produtos.pop(i)
                    salvar_produtos(produtos)
                    st.rerun()

    st.divider()
    if st.button("← Sair do Admin e ver Loja"):
        st.query_params.clear()
        st.rerun()

else:
    # ================== LOJA PARA CLIENTES ==================
    if "carrinho" not in st.session_state:
        st.session_state.carrinho = []

    # Topo
    col_logo, col_cart = st.columns([4,1])
    with col_logo:
        st.markdown("### 🕯️ Casa e Corpo Maison")
    with col_cart:
        st.button(f"🛒 CARRINHO ({len(st.session_state.carrinho)})", use_container_width=True)

    # Banner
    banner_mostrado = False
    for b in Path(".").glob("banner.*"):
        st.image(str(b), use_container_width=True)
        banner_mostrado = True
        break
    
    st.markdown("## Nossos Produtos")
    
    if not produtos:
        st.info("Nenhum produto cadastrado.")
    else:
        cols = st.columns(3)
        for idx, prod in enumerate(produtos):
            with cols[idx % 3]:
                with st.container(border=True):
                    foto = prod.get("foto","")
                    if foto:
                        try:
                            if foto.startswith("http"):
                                st.image(foto, use_container_width=True)
                            elif Path(foto).exists():
                                st.image(foto, use_container_width=True)
                            else:
                                st.write("🖼️ Sem foto")
                        except:
                            st.write("🖼️ Foto não encontrada")
                    else:
                        st.write("🖼️ Sem foto - cadastre no admin")

                    st.write(f"**{prod['nome']}**")
                    st.write(f"R$ {prod['preco']}")
                    
                    if st.button("Adicionar ao carrinho 🛒", key=f"add_{idx}", use_container_width=True):
                        st.session_state.carrinho.append(prod)
                        st.toast(f"{prod['nome']} adicionado!")
                        st.rerun()

    st.markdown("---")
    st.caption("© Casa e Corpo Maison - Loja oficial | Entrega para todo Brasil")
