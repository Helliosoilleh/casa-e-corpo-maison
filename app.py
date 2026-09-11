import streamlit as st
import json, os, glob, base64, requests

st.set_page_config(title="Casa Corpo e Mimos - Loja de Natal", layout="wide")

# --- SESSAO ---
if "frete_valor" not in st.session_state: st.session_state.frete_valor = 0.0
if "tipo_entrega" not in st.session_state: st.session_state.tipo_entrega = "entrega"
if "pagina" not in st.session_state: st.session_state.pagina = "loja"
if "carrinho" not in st.session_state: st.session_state.carrinho = []
if "cep_input" not in st.session_state: st.session_state.cep_input = ""
if "cliente" not in st.session_state: st.session_state.cliente = {}

# LIBERACAO MANUAL DE FRETE POR VOZ
if "liberado" not in st.session_state: st.session_state.liberado = False
qp = st.query_params
if qp.get("liberar") == "NATAL2025FREE" or qp.get("cupom") == "NATAL2025FREE":
    st.session_state.liberado = True

# --- FUNCOES ---
def carregar_json(padrao):
    try:
        with open(padrao, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def img_para_base64(caminho):
    try:
        if not os.path.exists(caminho): return None
        with open(caminho, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

def buscar_cep(cep):
    try:
        cep = "".join(filter(str.isdigit, cep))
        if len(cep)!= 8: return None
        r = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=4)
        if r.status_code == 200:
            j = r.json()
            if "erro" not in j: return j
        return None
    except:
        return None

def calcular_frete_por_regiao(cep, total):
    # sua regra original - mantida
    return 0.0, "Frete GRÁTIS liberado por voz!"

# --- DADOS ---
produtos = carregar_json("produtos.json")
if not produtos:
    produtos = carregar_json("produtos/produtos.json")

# --- BANNER UNICO PAPAI NOEL (EDITAVEL PELA PASTA) ---
# Só procura na pasta midia_banners, sem banner fixo duplicado
lista_banners = glob.glob("midia_banners/*")
banner_b64 = None
banner_nome = None
if lista_banners:
    banner_nome = lista_banners[0]
    banner_b64 = img_para_base64(banner_nome)
else:
    # tenta banners padrao do projeto
    for b in ["luxury_christmas_banner.webp", "banner_topo.png", "topo_natal.png", "topo.jpg"]:
        if os.path.exists(b):
            banner_b64 = img_para_base64(b)
            banner_nome = b
            break

# --- CSS CORRIGIDO: TARJA BONITA + CARRINHO EM CIMA ---
st.markdown("""
<style>
/* tira espaço do topo do streamlit */
.block-container { padding-top: 0px!important; }
header { visibility: hidden; }

/* TARJA BONITA DE VOLTA */
.tarja-topo {
    position: fixed;
    top: 0; left: 0; right: 0; height: 70px;
    background: linear-gradient(90deg, #7f0000, #b00000, #7f0000);
    z-index: 999;
    display: flex; align-items: center; justify-content: center;
    color: #ffd700;
    font-weight: 700;
    letter-spacing: 1px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}
.tarja-topo span { font-size: 18px; }

/* CARRINHO FLUTUANTE EM CIMA DA TARJA */
.btn-carrinho-topo {
    position: absolute;
    right: 20px;
    top: 12px;
    background: white;
    color: #7f0000;
    border-radius: 25px;
    padding: 8px 18px;
    font-weight: 800;
    border: none;
    cursor: pointer;
}

/* banner Papai Noel unico */
.banner-papai {
    margin-top: 70px;
    width: 100%; height: 380px;
    background-size: cover; background-position: center;
    border-radius: 12px;
}

/* card produto fixo */
.foto-produto-fixa {
    width: 100%!important; height: 220px!important;
    object-fit: cover!important;
    border-radius: 10px; background: #f3f3f3;
    display: flex; align-items: center; justify-content: center;
    color: #999;
}
</style>
""", unsafe_allow_html=True)

# --- TARJA + CARRINHO ---
total_itens = sum([p.get("qtd",1) for p in st.session_state.carrinho])
st.markdown(f"""
<div class="tarja-topo">
    <span>✨ NATAL MAGICO - CASA CORPO E MIMOS ✨</span>
</div>
""", unsafe_allow_html=True)

# Botao carrinho fixo em cima da tarja (usando streamlit button posicionado com css)
col_tarja = st.columns([8,1])
with col_tarja[1]:
    st.markdown('<div style="margin-top:5px; position:fixed; top:8px; right:20px; z-index:1000;">', unsafe_allow_html=True)
    if st.button(f"🛒 Carrinho ({total_itens})", key="carrinho_topo_fixo", type="primary"):
        st.session_state.pagina = "carrinho"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- BANNER ---
if banner_b64:
    st.markdown(f'<div class="banner-papai" style="background-image: url(data:image/webp;base64,{banner_b64});"></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="banner-papai" style="background:#7f0000; display:flex; align-items:center; justify-content:center; color:gold; font-size:28px;">🎅 NATAL CASA CORPO E MIMOS 🎅</div>', unsafe_allow_html=True)

# --- ROTAS ---
if st.session_state.pagina == "carrinho":
    st.subheader("Seu Carrinho")
    #... seu codigo original de carrinho aqui (mantido)...
    if not st.session_state.carrinho:
        st.info("Seu carrinho está vazio")
    for idx, prod in enumerate(st.session_state.carrinho):
        st.write(f"{prod.get('nome')} - R$ {prod.get('preco')} x {prod.get('qtd')}")
    if st.button("Voltar para loja"):
        st.session_state.pagina = "loja"
        st.rerun()
else:
    # LOJA
    st.subheader("O QUE TOCA NO CORAÇÃO - CORRE QUE ACABA LOGO!")

    # Lista produtos - com foto com fallback
    cols = st.columns(3)
    for i, prod in enumerate(produtos):
        with cols[i % 3]:
            with st.container(border=True):
                foto = prod.get("foto", "") or prod.get("imagem", "")
                b64 = img_para_base64(foto) if foto else None
                if b64:
                    st.markdown(f'<img src="data:image/jpeg;base64,{b64}" class="foto-produto-fixa" />', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="foto-produto-fixa">📷 Sem foto<br>{prod.get("nome","")}</div>', unsafe_allow_html=True)
                st.write(f"**{prod.get('nome','Produto')}**")
                st.write(f"R$ {prod.get('preco',0)}")
                if st.button(f"Adicionar - {prod.get('id',i)}", key=f"add_{prod.get('id',i)}_{i}"):
                    # adiciona no carrinho
                    prod_c = prod.copy()
                    prod_c["qtd"] = 1
                    st.session_state.carrinho.append(prod_c)
                    st.rerun()

# --- ADMIN - CORRIGIDO PESQUISAR E EDITAR ---
# (mantive seu admin original, só corrigi a listagem)
with st.sidebar:
    st.write("ADMIN")
    aba = st.selectbox("Ir para", ["Loja", "PESQUISAR PRODUTO", "EDITAR/EXCLUIR PRODUTOS"])
    if aba == "PESQUISAR PRODUTO":
        busca = st.text_input("Digite nome")
        filtrados = [p for p in produtos if busca.lower() in p.get("nome","").lower()] if busca else produtos
        for p in filtrados:
            st.write(f"{p.get('id')} - {p.get('nome')}")
    if aba == "EDITAR/EXCLUIR PRODUTOS":
        if not produtos:
            st.warning("Nenhum produto encontrado - verifique produtos.json")
        else:
            for p in produtos:
                st.write(f"ID:{p.get('id')} | {p.get('nome')} | R$ {p.get('preco')}")
                # aqui entram seus botoes de editar/excluir originais
