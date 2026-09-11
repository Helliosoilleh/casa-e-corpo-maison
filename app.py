import streamlit as st
import os
import json
import base64

st.set_page_config(page_title="Casa e Corpo Maison", layout="wide")

PASTA_PRODUTOS = "midia_produtos"
PASTA_BANNERS = "midia_banners"
ARQUIVO_PRODUTOS = "produtos.json"
ARQUIVO_CONFIG = "config_loja.json"

for p in [PASTA_PRODUTOS, PASTA_BANNERS]:
    if not os.path.exists(p):
        os.makedirs(p)

def carregar_produtos():
    if os.path.exists(ARQUIVO_PRODUTOS):
        try:
            with open(ARQUIVO_PRODUTOS, "r", encoding="utf-8") as f:
                dados = json.load(f)
                # garante que sempre é lista
                if isinstance(dados, list):
                    return dados
                return []
        except:
            return []
    return []

def salvar_produtos(lista):
    with open(ARQUIVO_PRODUTOS, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)

def carregar_config():
    if os.path.exists(ARQUIVO_CONFIG):
        try:
            with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

# --- CARRINHO ---
if "carrinho" not in st.session_state:
    st.session_state["carrinho"] = []
if "admin_logado" not in st.session_state:
    st.session_state["admin_logado"] = False
if "tentou_acessar_admin" not in st.session_state:
    st.session_state["tentou_acessar_admin"] = False

# LINK ADMIN ?admin=maison123
try:
    qp = st.query_params
    if qp.get("admin") == "maison123" or "maison123" in str(qp):
        st.session_state["tentou_acessar_admin"] = True
except:
    pass

# --- LOGIN ADMIN ---
if st.session_state.get("tentou_acessar_admin") and not st.session_state.get("admin_logado"):
    st.markdown("""
    <style>header,#MainMenu,footer{visibility:hidden;}</style>
    <div style='text-align:center;padding:30px;background:#000;border:3px solid #B38728;border-radius:15px;margin-top:30px;'>
        <div style='font-size:40px;'>🏠</div>
        <div style='color:#B38728;font-size:22px;font-weight:900;'>BEM VINDO AO PAINEL ADMINISTRATIVO</div>
        <div style='color:white;font-size:13px;letter-spacing:3px;'>CASA E CORPO MAISON</div>
    </div>""", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,1.5,1])
    with c2:
        u = st.text_input("Usuario", placeholder="maison")
        s = st.text_input("Senha", type="password", placeholder="maison123")
        if st.button("ENTRAR", use_container_width=True):
            if u == "maison" and s == "maison123":
                st.session_state["admin_logado"] = True
                st.rerun()
            else:
                st.error("Usuario ou senha incorretos")
        if st.button("Voltar a loja", use_container_width=True):
            st.session_state["tentou_acessar_admin"] = False
            st.query_params.clear()
            st.rerun()
    st.stop()

# --- PAINEL ADMIN CORRIGIDO - AGORA MOSTRA PRODUTOS ---
if st.session_state.get("admin_logado"):
    st.sidebar.title("PAINEL DE CONTROLE")
    if st.sidebar.button("Sair da loja"):
        st.session_state["admin_logado"] = False
        st.session_state["tentou_acessar_admin"] = False
        st.query_params.clear()
        st.rerun()

    st.title("PRODUTOS")
    tab1, tab2, tab3 = st.tabs(["CADASTRAR PRODUTO", "PESQUISAR PRODUTO", "EDITAR/EXCLUIR PRODUTOS"])
    
    produtos = carregar_produtos()

    with tab1:
        st.subheader("Cadastrar novo produto")
        with st.form("cad"):
            codigo = st.text_input("Nome do Produto")
            preco = st.text_input("Preço (ex: 99.90)")
            foto = st.file_uploader("Foto do Produto", type=["png","jpg","jpeg","webp"])
            if st.form_submit_button("Salvar produto"):
                caminho = ""
                if foto:
                    caminho = os.path.join(PASTA_PRODUTOS, foto.name)
                    with open(caminho, "wb") as f:
                        f.write(foto.getbuffer())
                novo = {"codigo": codigo, "descricao": codigo, "valor": preco, "preco": preco, "foto": caminho, "nome": codigo}
                produtos.append(novo)
                salvar_produtos(produtos)
                st.success(f"Produto {codigo} salvo! Já aparece na loja.")
                st.rerun()

    with tab2:
        st.subheader(f"Produtos cadastrados: {len(produtos)}")
        busca = st.text_input("Pesquisar")
        for p in produtos:
            if busca.lower() in p.get("codigo","").lower() or busca.lower() in p.get("nome","").lower():
                col1, col2 = st.columns([1,3])
                with col1:
                    if p.get("foto") and os.path.exists(p.get("foto")):
                        st.image(p.get("foto"), width=100)
                    else:
                        st.warning("Sem foto")
                with col2:
                    st.write(f"**{p.get('codigo')}** - R$ {p.get('valor', p.get('preco',''))}")
                    st.write(f"Foto: {p.get('foto','vazia')}")

    with tab3:
        st.subheader("Editar / Excluir")
        for i, p in enumerate(produtos):
            c1, c2, c3 = st.columns([3,1,1])
            with c1:
                st.write(f"{i+1}. {p.get('codigo')} - R$ {p.get('valor')}")
            with c2:
                if st.button("Excluir", key=f"del_{i}"):
                    produtos.pop(i)
                    salvar_produtos(produtos)
                    st.rerun()
    st.stop()

# --- LOJA CLIENTE ---
produtos = carregar_produtos()
total_qtd = sum([1 for _ in st.session_state["carrinho"]])
total_val = sum([float(str(p.get("valor", p.get("preco","0")).replace(",","."))) for p in st.session_state["carrinho"]])

# TARJA BONITA + CARRINHO FLUTUANTE SOBRE ELA
st.markdown(f"""
<div style="position:fixed; top:0; left:0; width:100%; background:linear-gradient(90deg,#4A0000,#8B0000); color:#FFD700; text-align:center; padding:14px; z-index:999998; font-weight:bold; letter-spacing:2px; border-bottom:2px solid #FFD700;">
Casa e Corpo Maison
</div>
<style>
.block-container{{padding-top:70px !important;}}
.wrap-carrinho-topo{{position:fixed !important; top:8px !important; right:20px !important; z-index:9999999 !important;}}
.wrap-carrinho-topo button{{background:#FFD700 !important; color:#4A0000 !important; border:none !important; border-radius:25px !important; font-weight:900 !important;}}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="wrap-carrinho-topo">', unsafe_allow_html=True)
if st.button(f"🛒 CARRINHO ({total_qtd})", key="carrinho_topo", type="primary"):
    st.toast(f"Carrinho com {total_qtd} itens - R$ {total_val:.2f}")
st.markdown('</div>', unsafe_allow_html=True)

# BANNER PAPAI NOEL EDITAVEL - SÓ 1 BANNER
if os.path.exists("topo_natal.png"):
    st.image("topo_natal.png", use_container_width=True)
elif os.path.exists(os.path.join(PASTA_BANNERS, "topo_natal.png")):
    st.image(os.path.join(PASTA_BANNERS, "topo_natal.png"), use_container_width=True)
else:
    st.markdown("""
    <div style='width:100%;height:280px;background:linear-gradient(90deg,#0A0A0A,#1A1A1A);border:3px solid #B38728;border-radius:12px;display:flex;align-items:center;justify-content:center;color:#B38728;font-size:28px;font-weight:900;'>
    CASA E CORPO MAISON - Troque a imagem topo_natal.png
    </div>""", unsafe_allow_html=True)

st.subheader("Nossos Produtos")
if not produtos:
    st.warning("Nenhum produto cadastrado ainda. Acesse ?admin=maison123 para cadastrar.")
else:
    cols = st.columns(3)
    for idx, prod in enumerate(produtos):
        with cols[idx % 3]:
            with st.container(border=True):
                foto = prod.get("foto","")
                if foto and os.path.exists(foto):
                    st.image(foto, use_container_width=True)
                else:
                    # tenta achar por nome parecido
                    st.markdown(f"<div style='height:250px;background:#f5f5f5;display:flex;align-items:center;justify-content:center;border-radius:8px;'>📷<br>{prod.get('codigo','')}</div>", unsafe_allow_html=True)
                    st.caption(f"Foto não encontrada: {foto}. Cadastre de novo no ADM.")
                
                st.markdown(f"**{prod.get('codigo', prod.get('nome',''))}**")
                st.markdown(f"<span style='color:#C00000;font-weight:bold;'>R$ {prod.get('valor', prod.get('preco','0'))}</span>", unsafe_allow_html=True)
                if st.button("Adicionar ao carrinho 🛒", key=f"add_{idx}_{prod.get('codigo')}"):
                    st.session_state["carrinho"].append(prod)
                    st.toast(f"{prod.get('codigo')} adicionado!")
                    st.rerun()
