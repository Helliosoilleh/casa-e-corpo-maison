import streamlit as st
import json, os

st.set_page_config(page_title="Painel Maison - ADMIN N1", layout="wide", page_icon="🏠")

# --- SENHA QUE PODE TROCAR - N1 ---
ARQ_SENHA = "senha_admin.json"
def get_senha():
    if os.path.exists(ARQ_SENHA):
        try: return json.load(open(ARQ_SENHA,"r",encoding="utf-8"))["senha"]
        except: return "maison123"
    return "maison123"
SENHA_ATUAL = get_senha()

st.markdown("""
<style>
.stAppDeployButton, header, #MainMenu, footer{display:none!important}
.stApp{background:#2E2E2E!important}
[data-testid="stSidebar"]{background:#1A1A1A!important;border-right:2px solid #B38728}
h1,h2,h3,p,label,div{color:#F5F5F5!important}
.stButton>button{background:linear-gradient(90deg,#BF953F,#FCF6BA,#B38728)!important;color:#2E2E2E!important;font-weight:900!important;border-radius:25px!important}
</style>
""", unsafe_allow_html=True)

if "logado" not in st.session_state: st.session_state.logado = False
if not st.session_state.logado:
    st.title("🔒 Painel Casa e Corpo Maison - ADMIN N1")
    senha = st.text_input("Senha de Administrador", type="password")
    if st.button("Entrar no Painel"):
        if senha == SENHA_ATUAL: st.session_state.logado = True; st.rerun()
        else: st.error("Senha incorreta")
    st.stop()

st.sidebar.title("PAINEL DE CONTROLE\nCASA E CORPO MAISON")
menu = st.sidebar.radio("Ir para:", ["MARKETING", "FINANCEIRO", "PRODUTOS", "CLIENTES", "FORNECEDORES", "CONFIGURAÇÕES"])
st.sidebar.divider()
if st.sidebar.button("Sair do Painel"): st.session_state.logado = False; st.rerun()

def carregar_json(arq, padrao=[]):
    if os.path.exists(arq):
        try:
            with open(arq, "r", encoding="utf-8") as f: return json.load(f)
        except: return padrao
    return padrao
def salvar_json(arq, dados):
    with open(arq, "w", encoding="utf-8") as f: json.dump(dados, f, indent=4, ensure_ascii=False)

if menu == "MARKETING":
    st.header("📣 MARKETING")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("IMAGEM DA LOJA")
        st.info("BANNERS / FOTOS / VIDEOS / AUDIOS")
        banner = st.file_uploader("Subir Banner Novo", type=["jpg","png","mp4","mp3"])
        if banner:
            os.makedirs("midia_loja", exist_ok=True)
            with open(os.path.join("midia_loja", banner.name), "wb") as f: f.write(banner.getbuffer())
            st.success(f"Salvo em midia_loja/{banner.name}")
            if banner.type.startswith("image"): st.image(banner, width=300)
    with col2:
        st.subheader("PROMOÇÕES")
        cfg_promo = carregar_json("config_loja.json", {})
        if not isinstance(cfg_promo, dict): cfg_promo = {}
        promo = st.text_area("Texto da Promoção da Semana", cfg_promo.get("promocao",""))
        if st.button("Salvar Promoção"):
            cfg_promo["promocao"] = promo
            salvar_json("config_loja.json", cfg_promo)
            st.success("Promoção salva!")

elif menu == "FINANCEIRO":
    st.header("💰 FINANCEIRO")
    cfg = carregar_json("config_loja.json", {})
    if not isinstance(cfg, dict): cfg = {}
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("CARTÕES")
        opcoes_validas = ["Crédito", "Débito", "Pix", "Parcelado em 3x", "Parcelado em 6x"]
        cartoes_salvos = cfg.get("cartoes", ["Crédito", "Pix"])
        cartoes_validos = [c for c in cartoes_salvos if c in opcoes_validas]
        cartoes = st.multiselect("Aceita:", opcoes_validas, default=cartoes_validos)
        taxa = st.number_input("Taxa da maquininha (%)", value=float(cfg.get("taxa",2.5)))
    with col2:
        st.subheader("PIX")
        chave_pix = st.text_input("Sua Chave PIX", cfg.get("pix",""))
        nome_pix = st.text_input("Nome no PIX", cfg.get("nome_pix","Casa e Corpo Maison"))
    if st.button("Salvar Financeiro", type="primary"):
        cfg["cartoes"] = cartoes; cfg["taxa"] = taxa; cfg["pix"] = chave_pix; cfg["nome_pix"] = nome_pix
        salvar_json("config_loja.json", cfg)
        st.success("Dados financeiros salvos!")

elif menu == "PRODUTOS":
    st.header("📦 PRODUTOS")
    aba1, aba2, aba3 = st.tabs(["CADASTRO DE PRODUTOS", "PESQUISA DE PRODUTOS", "EDITAR OU EXCLUIR PRODUTOS"])
    produtos = carregar_json("produtos.json")
    with aba1:
        with st.form("cad_prod", clear_on_submit=True):
            nome = st.text_input("Nome do Produto")
            preco = st.number_input("Preço R$", min_value=0.0, format="%.2f")
            st.markdown("**Foto do Produto (OBRIGATÓRIO)**")
            foto_prod = st.file_uploader("Subir Foto", type=["jpg","png","jpeg"], key="foto_cad")
            link_img = st.text_input("Ou Link da imagem (opcional)")
            enviar = st.form_submit_button("Cadastrar Produto")
            if enviar:
                img_final = link_img
                if foto_prod:
                    os.makedirs("midia_produtos", exist_ok=True)
                    caminho = os.path.join("midia_produtos", foto_prod.name)
                    with open(caminho, "wb") as f: f.write(foto_prod.getbuffer())
                    img_final = caminho
                if nome and preco > 0 and img_final:
                    produtos.append({"nome":nome, "preco":preco, "img":img_final})
                    salvar_json("produtos.json", produtos)
                    st.success(f"{nome} cadastrado com FOTO!")
                else: st.error("Preencha nome, preço e FOTO!")
    with aba2:
        busca = st.text_input("Pesquisar produto por nome")
        filtrados = [p for p in produtos if busca.lower() in p.get("nome","").lower()] if busca else produtos
        st.write(f"Encontrados: {len(filtrados)}")
        for p in filtrados:
            c1,c2 = st.columns([1,3])
            with c1:
                try: st.image(p.get('img'), width=80)
                except: st.caption("Sem foto")
            with c2: st.write(f"**{p.get('nome')}** - R$ {p.get('preco')}")
    with aba3:
        for i, p in enumerate(produtos):
            with st.expander(f"{i+1}. {p.get('nome')} - R$ {p.get('preco')}"):
                try: st.image(p.get('img'), width=150)
                except: pass
                produtos[i]["nome"] = st.text_input("Nome", p.get("nome",""), key=f"en_{i}")
                produtos[i]["preco"] = st.number_input("Preço", value=float(p.get("preco",0)), key=f"ep_{i}")
                nova_foto = st.file_uploader("Trocar Foto", type=["jpg","png","jpeg"], key=f"ef_{i}")
                if nova_foto:
                    os.makedirs("midia_produtos", exist_ok=True)
                    caminho = os.path.join("midia_produtos", nova_foto.name)
                    with open(caminho, "wb") as f: f.write(nova_foto.getbuffer())
                    produtos[i]["img"] = caminho
                    st.success("Foto trocada! Clique em Salvar")
                produtos[i]["img"] = st.text_input("Link Imagem", produtos[i].get("img",""), key=f"ei_{i}")
                c1,c2 = st.columns(2)
                if c1.button("Salvar Alteração", key=f"sal_{i}"): salvar_json("produtos.json", produtos); st.success("Salvo!"); st.rerun()
                if c2.button("❌ Excluir", key=f"del_{i}"): produtos.pop(i); salvar_json("produtos.json", produtos); st.warning("Excluído!"); st.rerun()

elif menu == "CLIENTES":
    st.header("👥 CLIENTES")
    aba1, aba2 = st.tabs(["CADASTRO", "EDITAR OU EXCLUIR"])
    clientes = carregar_json("clientes.json")
    with aba1:
        with st.form("cad_cli"):
            nome = st.text_input("Nome do Cliente"); zap = st.text_input("WhatsApp"); end = st.text_input("Endereço")
            if st.form_submit_button("Cadastrar Cliente"): clientes.append({"nome":nome,"zap":zap,"end":end}); salvar_json("clientes.json", clientes); st.success("Salvo!")
    with aba2:
        for i, c in enumerate(clientes):
            with st.expander(f"{c.get('nome')} - {c.get('zap')}"):
                if st.button("Excluir", key=f"dc_{i}"): clientes.pop(i); salvar_json("clientes.json", clientes); st.rerun()

elif menu == "FORNECEDORES":
    st.header("🚚 FORNECEDORES")
    aba1, aba2 = st.tabs(["CADASTRO", "EDITAR OU EXCLUIR"])
    fornecedores = carregar_json("fornecedores.json")
    with aba1:
        with st.form("cad_for"):
            nome = st.text_input("Nome do Fornecedor"); prod = st.text_input("O que fornece"); zap = st.text_input("Contato")
            if st.form_submit_button("Cadastrar Fornecedor"): fornecedores.append({"nome":nome,"produto":prod,"zap":zap}); salvar_json("fornecedores.json", fornecedores); st.success("Salvo!")
    with aba2:
        for i, f in enumerate(fornecedores):
            with st.expander(f"{f.get('nome')} - {f.get('produto')}"):
                if st.button("Excluir", key=f"df_{i}"): fornecedores.pop(i); salvar_json("fornecedores.json", fornecedores); st.rerun()

elif menu == "CONFIGURAÇÕES":
    st.header("⚙️ CONFIGURAÇÕES")
    st.write(f"Senha atual cadastrada: `{SENHA_ATUAL}`")
    atual = st.text_input("Senha atual", type="password")
    nova = st.text_input("Nova senha", type="password")
    nova2 = st.text_input("Confirme a nova senha", type="password")
    if st.button("Salvar nova senha", type="primary"):
        if atual!= SENHA_ATUAL: st.error("Senha atual errada!")
        elif nova!= nova2: st.error("Senhas não batem!")
        elif len(nova) < 4: st.error("Muito curta! Mínimo 4 letras")
        else:
            salvar_json(ARQ_SENHA, {"senha":nova})
            st.success(f"Senha trocada! Nova: {nova}"); st.balloons()
