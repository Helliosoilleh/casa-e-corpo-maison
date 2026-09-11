import streamlit as st, json, os, glob, base64, requests

st.set_page_config(page_title="Casa e Corpo Maison", layout="wide")

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []
if "pagina" not in st.session_state:
    st.session_state.pagina = "loja"
if "tipo_entrega" not in st.session_state:
    st.session_state.tipo_entrega = "entrega"
if "cep_cliente" not in st.session_state:
    st.session_state.cep_cliente = ""
if "frete_valor" not in st.session_state:
    st.session_state.frete_valor = 0.0
if "frete_gratis_liberado" not in st.session_state:
    st.session_state.frete_gratis_liberado = False

try:
    if st.query_params.get("freteGratis") == "1" or st.query_params.get("cupom") == "MAISONFRETE":
        st.session_state.frete_gratis_liberado = True
except:
    pass

def carregar_json(nome, padrao):
    if os.path.exists(nome):
        try:
            with open(nome, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return padrao
    return padrao

def path_to_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

# --- TARJA NO TOPO ---
topo_b64 = ""
for p in ["topo_natal.png", "midia/topo_natal.png", "topo.png", "banner_topo.png"]:
    if os.path.exists(p):
        topo_b64 = path_to_base64(p)
        break

if topo_b64:
    st.markdown(f"""
    <style>
    header[data-testid="stHeader"] {{
        background: url("data:image/png;base64,{topo_b64}") !important;
        background-size: cover !important;
        background-position: center !important;
        height: 80px !important;
    }}
    .block-container {{ padding-top: 95px !important; }}
    .foto-produto img {{
        height: 280px !important;
        object-fit: cover !important;
        border-radius: 12px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- CARRINHO FLUTUANTE DE VOLTA ---
total_itens = len(st.session_state.carrinho)
total_valor_carrinho = sum([float(p.get("preco",0)) for p in st.session_state.carrinho])

if st.button(f"🛒 CARRINHO ({total_itens}) - R$ {total_valor_carrinho:.2f}", key="carrinho_topo_real", type="primary"):
    st.session_state.pagina = "carrinho"
    st.rerun()

# --- PAGINA CARRINHO ---
if st.session_state.pagina == "carrinho":
    st.title("Seu Carrinho")
    if st.button("← Voltar a Loja"):
        st.session_state.pagina = "loja"
        st.rerun()
    st.divider()
    if not st.session_state.carrinho:
        st.info("Carrinho vazio")
    else:
        for i, prod in enumerate(list(st.session_state.carrinho)):
            c1,c2,c3 = st.columns([1,2,1])
            with c1:
                foto = prod.get("foto") or prod.get("imagem") or ""
                if foto and os.path.exists(foto):
                    st.image(foto, width=120)
            with c2:
                st.write(f"**{prod.get('nome')}**")
                st.write(f"R$ {float(prod.get('preco',0)):.2f}")
            with c3:
                if st.button("Remover", key=f"rem_{i}"):
                    st.session_state.carrinho.pop(i)
                    st.rerun()
            st.divider()
        st.write(f"### Total: R$ {total_valor_carrinho:.2f}")
    st.stop()

# --- BANNER DO PAPAI NOEL (VOCE TROCA NO GESTAO) ---
cfg_loja = carregar_json("config_loja.json", {})
banner_atual = cfg_loja.get("banner_atual")
if banner_atual and os.path.exists(banner_atual):
    if banner_atual.lower().endswith((".mp4",".mov",".webm")):
        st.video(banner_atual)
    else:
        st.image(banner_atual, use_container_width=True)

st.divider()
st.subheader("Nossos Produtos")
produtos = carregar_json("produtos.json", [])

cols = st.columns(3)
for idx, prod in enumerate(produtos):
    with cols[idx % 3]:
        with st.container(border=True):
            foto = prod.get("foto") or prod.get("imagem") or prod.get("img") or ""
            if foto and os.path.exists(foto):
                st.markdown('<div class="foto-produto">', unsafe_allow_html=True)
                st.image(foto, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.image(foto, use_container_width=True) if foto else st.write("Sem foto")
            
            st.write(f"**{prod.get('nome','Produto')}**")
            preco = float(prod.get('preco', prod.get('valor', 0)))
            st.write(f"R$ {preco:.2f}")
            if st.button("Adicionar ao Carrinho", key=f"add_{idx}"):
                st.session_state.carrinho.append(prod)
                st.toast("Adicionado ao carrinho!")
                st.rerun()
