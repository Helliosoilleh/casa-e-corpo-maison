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

frete_gratis_liberado = False
try:
    if st.query_params.get("freteGratis") == "1" or st.query_params.get("cupom") == "MAISONFRETE":
        frete_gratis_liberado = True
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

# --- HEADER COM TARJA DE VOLTA (ONDE FICA O CARRINHO) ---
topo_natal_path = None
header_bg_b64 = ""
for p in ["topo_natal.png", "banner_topo.png", "topo.png", "midia/topo_natal.png", "midia/banners_da_loja/topo_natal.png"]:
    if os.path.exists(p):
        topo_natal_path = p
        header_bg_b64 = path_to_base64(p)
        break

if header_bg_b64:
    st.markdown(f"""
    <style>
    header[data-testid="stHeader"] {{
        background: url("data:image/png;base64,{header_bg_b64}") !important;
        background-size: cover !important;
        background-position: center !important;
        height: 85px !important;
    }}
    .block-container {{ padding-top: 90px !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- BANNER QUE VOCE TROCA NO GESTAO - SÓ PAPAI NOEL ---
cfg_loja = carregar_json("config_loja.json", {})
banner_atual = cfg_loja.get("banner_atual")

if banner_atual and os.path.exists(banner_atual):
    if banner_atual.lower().endswith((".mp4",".mov",".webm")):
        st.video(banner_atual)
    else:
        st.image(banner_atual, use_container_width=True)

st.divider()
st.title("Nossos Produtos")

produtos = carregar_json("produtos.json", [])
cols = st.columns(3)
for idx, prod in enumerate(produtos):
    with cols[idx % 3]:
        with st.container(border=True):
            foto = prod.get("foto") or prod.get("imagem") or ""
            if foto and os.path.exists(foto):
                st.image(foto, use_container_width=True)
            st.subheader(prod.get("nome","Produto"))
            st.write(f"R$ {float(prod.get('preco',0)):.2f}")
            if st.button("Adicionar ao Carrinho", key=f"add_{idx}"):
                st.session_state.carrinho.append(prod)
                st.toast("Adicionado!")
                st.rerun()
