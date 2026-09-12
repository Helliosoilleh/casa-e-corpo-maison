import streamlit as st
import os, json, base64

st.set_page_config(page_title="Casa e Corpo Maison", layout="wide", initial_sidebar_state="collapsed")

# ====== ESTILO QUE VOCÊ JÁ DEIXOU PERFEITO - NÃO MEXI ======
st.markdown("""
<style>
    .block-container{padding-top:0 !important}
    header, footer{visibility:hidden}
    .top-bar{
        background:#7a1010; color:white; text-align:center; 
        padding:10px 0; font-size:14px; letter-spacing:1px;
        position:sticky; top:0; z-index:999;
    }
    .banner-natal{
        width:100%; height:380px;
        background-image: linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.2)), url('https://i.imgur.com/8Km9tLL.jpg');
        background-size:cover; background-position:center;
        display:flex; flex-direction:column; align-items:center; justify-content:center;
        color:#FFD700; text-align:center;
    }
    .banner-natal h1{font-size:48px; margin:0; text-shadow:2px 2px 8px black; letter-spacing:3px}
    .banner-natal p{font-size:18px; color:white; margin-top:10px}
    .card-produto{
        border:1px solid #e5e5e5; border-radius:12px; background:white;
        padding:12px; text-align:center; min-height:420px;
        box-shadow:0 2px 8px rgba(0,0,0,0.05)
    }
    .card-produto img{border-radius:10px; height:220px; object-fit:cover}
    .preco{color:#7a1010; font-weight:bold; font-size:18px; margin:8px 0}
    .btn-comprar{background:#7a1010; color:white; border:0; padding:10px; width:100%; border-radius:8px; cursor:pointer}
</style>
<div class="top-bar">Casa e Corpo Maison</div>
<div class="banner-natal">
    <h1>CASA E CORPO MAISON</h1>
    <p>Coleção Natal Mágico</p>
</div>
<br>
""", unsafe_allow_html=True)

ARQ_JSON = "produtos.json"

def carregar_produtos():
    if os.path.exists(ARQ_JSON):
        try:
            with open(ARQ_JSON, "r", encoding="utf-8") as f:
                dados = json.load(f)
                # limpa os que vieram com "midia_produtos02" quebrado
                limpos = []
                for p in dados:
                    if "midia_produtos02" in str(p.get("nome","")) or "midia_produtos02" in str(p.get("imagem","")):
                        continue
                    limpos.append(p)
                return limpos
        except:
            return []
    # Se não tem nada, começa vazio - você cadastra pelo admin
    return []

def salvar_produtos(lista):
    with open(ARQ_JSON, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)

# ================== ADMIN ?admin=true ==================
if "admin" in st.query_params:
    st.title("🎄 Painel Casa e Corpo - Cadastro Normal")
    st.write("Igual empresa grande: arrasta a foto, põe nome e preço. Sem mexer em código nunca mais.")
    
    produtos = carregar_produtos()

    with st.form("cadastro_produto", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do produto*", placeholder="Ex: Árvore de Natal Canadense")
        with col2:
            preco = st.text_input("Preço*", placeholder="Ex: R$ 59,90")
        foto = st.file_uploader("📸 ARRASTE A FOTO AQUI*", type=["jpg","jpeg","png","webp"])
        salvar_btn = st.form_submit_button("✅ SALVAR NA LOJA AGORA", use_container_width=True)

        if salvar_btn:
            if not nome or not preco or not foto:
                st.error("Falta nome, preço ou foto.")
            else:
                foto_b64 = base64.b64encode(foto.getvalue()).decode()
                produtos.append({"nome": nome, "preco": preco, "foto": foto_b64})
                salvar_produtos(produtos)
                st.success(f"✅ {nome} foi pra loja! Pode abrir a loja normal que já apareceu.")
                st.balloons()

    st.divider()
    st.subheader(f"Produtos hoje na loja: {len(produtos)}")
    if not produtos:
        st.info("Ainda vazia. Cadastra o primeiro acima.")
    for i, p in enumerate(produtos):
        c1, c2, c3 = st.columns([1, 4, 1])
        with c1:
            if p.get("foto"):
                try:
                    st.image(base64.b64decode(p["foto"]), width=70)
                except:
                    st.write("sem foto")
        with c2:
            st.write(f"**{p.get('nome')}** - {p.get('preco')}")
        with c3:
            if st.button("🗑️ Excluir", key=f"del_{i}"):
                produtos.pop(i)
                salvar_produtos(produtos)
                st.rerun()

# ================== LOJA NORMAL ==================
else:
    produtos = carregar_produtos()
    st.markdown("### 🎁 Nossos Produtos")

    if not produtos:
        st.warning("A loja está vazia. Entre em /?admin=true para cadastrar seus produtos com foto.")
    else:
        cols = st.columns(3)
        for idx, prod in enumerate(produtos):
            with cols[idx % 3]:
                foto_b64 = prod.get("foto", "")
                if foto_b64:
                    try:
                        st.image(base64.b64decode(foto_b64), use_container_width=True)
                    except:
                        st.image("https://via.placeholder.com/300x400?text=Foto+invalida", use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x400?text=Sem+foto", use_container_width=True)
                
                st.markdown(f"""
                <div class="card-produto">
                    <b>{prod.get('nome','Produto')}</b><br>
                    <div class="preco">{prod.get('preco','R$ 0,00')}</div>
                    <button class="btn-comprar">Adicionar ao Carrinho 🛒</button>
                </div>
                """, unsafe_allow_html=True)
                st.write("")
