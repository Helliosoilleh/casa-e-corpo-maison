import streamlit as st, json, os, base64, requests
from datetime import datetime

st.set_page_config(page_title="Painel ADM - MAISON", layout="wide", page_icon="🏠")

def salvar_no_github(caminho_arquivo, conteudo_bytes, mensagem_commit):
    try:
        TOKEN = st.secrets["GITHUB_TOKEN"]
        REPO = st.secrets["GITHUB_REPO"]
        url = f"https://api.github.com/repos/{REPO}/contents/{caminho_arquivo}"
        headers = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github.v3+json"}
        r_get = requests.get(url, headers=headers)
        sha = r_get.json().get("sha") if r_get.status_code == 200 else None
        conteudo_b64 = base64.b64encode(conteudo_bytes).decode("utf-8")
        dados = {"message": mensagem_commit, "content": conteudo_b64, "branch": "main"}
        if sha: dados["sha"] = sha
        r_put = requests.put(url, headers=headers, json=dados)
        return (True, "OK") if r_put.status_code in [200, 201] else (False, r_put.text)
    except Exception as e:
        return False, str(e)

def get_senha():
    try:
        return json.load(open("senha.json", "r", encoding="utf-8"))["senha"]
    except:
        return "maison123"
SENHA_ADMIN = get_senha()

def carregar_json(nome, padrao):
    if os.path.exists(nome):
        try:
            with open(nome, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return padrao
    return padrao

def salvar_json(nome, dados):
    with open(nome, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
    try:
        b = json.dumps(dados, indent=4, ensure_ascii=False).encode("utf-8")
        salvar_no_github(nome, b, f"Atualiza {nome}")
    except: pass

st.markdown("""<style>#MainMenu, header, footer{display:none!important}</style>""", unsafe_allow_html=True)
if "logado" not in st.session_state: st.session_state.logado = False
if not st.session_state.logado:
    st.title("Painel Casa e Corpo Maison - ADMIN (MESTRE)")
    senha = st.text_input("Senha de Administrador", type="password")
    if st.button("Entrar no Painel"):
        if senha == SENHA_ADMIN: st.session_state.logado = True; st.rerun()
        else: st.error("Senha Incorreta!")
    st.stop()

st.sidebar.title("PAINEL DE CONTROLE CASA E CORPO MAISON")
menu = st.sidebar.radio("Ir para:", ["MARKETING", "FINANCEIRO", "PRODUTOS", "CLIENTES", "FORNECEDORES", "CONFIGURAÇÃO"])
if st.sidebar.button("Sair do Painel"): st.session_state.logado = False; st.rerun()

if menu == "MARKETING":
    st.header("MARKETING")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("TARJA FINA DO TOPO (70px)")
        topo = st.file_uploader("Enviar nova tarja topo_natal.png", type=["png","jpg","webp","jpeg"], key="topo")
        if topo:
            st.image(topo, width=300)
            if st.button("💾 ATUALIZAR TARJA NA LOJA", type="primary", key="btn_topo"):
                with open("topo_natal.png","wb") as f: f.write(topo.getvalue())
                salvar_no_github("topo_natal.png", topo.getvalue(), "Atualiza topo_natal.png")
                st.success("✅ Tarja foi pra loja! (sem nome por cima)")
                st.balloons()
        st.divider()
        st.subheader("BANNER GRANDE DA LOJA")
        banner = st.file_uploader("Mídia Banner Novo", type=["jpg", "jpeg", "png", "webp", "mp4"])
        if banner:
            os.makedirs("midia_banners", exist_ok=True)
            if banner.type.startswith("image"): st.image(banner, width=300)
            else: st.video(banner)
            if st.button("💾 SALVAR E ATUALIZAR NA LOJA", type="primary"):
                nome_limpo = banner.name.replace(" ", "_")
                caminho_midia = f"midia_banners/{nome_limpo}"
                with open(caminho_midia,"wb") as f: f.write(banner.getvalue())
                salvar_no_github(caminho_midia, banner.getvalue(), f"Novo banner {nome_limpo}")
                cfg_atual = carregar_json("config_loja.json", {})
                cfg_atual["banner_atual"] = caminho_midia
                cfg_atual["banner_atualizado_em"] = datetime.now().isoformat()
                salvar_json("config_loja.json", cfg_atual)
                st.balloons()
                st.success("✅ BANNER FOI PARA A LOJA!")
    with col2:
        cfg_promo = carregar_json("config_loja.json", {})
        st.subheader("PROMOÇÕES - Texto")
        promo = st.text_area("Texto da Promoção da Semana", cfg_promo.get("promocao",""))
        if st.button("Salvar Promoção"):
            cfg_promo["promocao"] = promo
            salvar_json("config_loja.json", cfg_promo)
            st.success("Promoção salva!")

elif menu == "FINANCEIRO":
    st.header("FINANCEIRO")
    cfg = carregar_json("config_loja.json", {})
    with st.form("fin"):
        c1, c2 = st.columns(2)
        with c1:
            nome_pix = st.text_input("Nome Chave Pix", cfg.get("nome_pix","Casa e Corpo Maison"))
            chave_pix = st.text_input("Chave Pix", cfg.get("chave_pix",""))
            taxa = st.number_input("Taxa de entrega", value=float(cfg.get("taxa", 15.0)))
        with c2:
            tel = st.text_input("Telefone/WhatsApp", cfg.get("telefone",""))
            prazo = st.text_input("Prazo entrega", cfg.get("prazo",""))
        if st.form_submit_button("Salvar Financeiro", type="primary"):
            cfg.update({"nome_pix": nome_pix, "chave_pix": chave_pix, "taxa": taxa, "telefone": tel, "prazo": prazo})
            salvar_json("config_loja.json", cfg)
            st.success("Salvo!")

# ========= AQUI ESTÃO AS 3 ABAS DE VOLTA =========
elif menu == "PRODUTOS":
    st.header("PRODUTOS")
    produtos = carregar_json("produtos.json", [])
    if isinstance(produtos, dict): produtos = list(produtos.values())

    abas = st.tabs(["CADASTRO DE PRODUTO", "PESQUISA DE PRODUTO", "EDITAR OU EXCLUIR PRODUTOS"])

    # ABA 1 - CADASTRO
    with abas[0]:
        st.subheader("Cadastrar Novo Produto")
        nome = st.text_input("Nome do Produto *", key="nome_cad")
        preco = st.number_input("Preço R$ *", min_value=0.0, format="%.2f", key="preco_cad")
        foto_prod = st.file_uploader("Foto do Produto *", type=["jpg","jpeg","png","webp"], key="foto_cad")
        link_img = st.text_input("Ou Link da Imagem (opcional)", key="link_cad")
        if st.button("✅ Cadastrar e Enviar pra Loja", type="primary"):
            if not nome:
                st.error("Digite o nome!")
            else:
                if foto_prod:
                    os.makedirs("midia_produtos", exist_ok=True)
                    caminho = f"midia_produtos/{foto_prod.name.replace(' ','_')}"
                    with open(caminho, "wb") as f:
                        f.write(foto_prod.getbuffer())
                    salvar_no_github(caminho, foto_prod.getvalue(), f"Foto {nome}")
                    img_final = caminho
                else:
                    img_final = link_img
                produtos.append({"nome": nome, "preco": float(preco), "img": img_final, "foto": img_final, "imagem": img_final})
                salvar_json("produtos.json", produtos)
                st.balloons()
                st.success(f"✅ {nome} cadastrado e já na loja!")

    # ABA 2 - PESQUISA DE PRODUTO (VOLTOU)
    with abas[1]:
        st.subheader("Pesquisar Produto")
        busca = st.text_input("Digite o nome para pesquisar", key="busca_prod")
        if busca:
            encontrados = [p for p in produtos if busca.lower() in p.get("nome","").lower()]
            st.write(f"Encontrados: {len(encontrados)}")
            for p in encontrados:
                with st.container(border=True):
                    c1, c2 = st.columns([1, 3])
                    with c1:
                        img = p.get("img") or p.get("foto")
                        if img and os.path.exists(img): st.image(img, width=80)
                        elif img and img.startswith("http"): st.image(img, width=80)
                    with c2:
                        st.write(f"**{p.get('nome')}** - R$ {p.get('preco')}")
                        st.caption(p.get("img",""))
        else:
            st.info("Digite algo para pesquisar")
            for p in produtos:
                st.write(f"- {p.get('nome')} - R$ {p.get('preco')}")

    # ABA 3 - EDITAR OU EXCLUIR (VOLTOU)
    with abas[2]:
        st.subheader("Editar ou Excluir Produtos")
        st.write(f"Total: {len(produtos)} produtos")
        for i, p in enumerate(produtos):
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
                with c1:
                    img = p.get("img") or p.get("foto")
                    if img and os.path.exists(img): st.image(img, width=80)
                    elif img and img.startswith("http"): st.image(img, width=80)
                    else: st.write("📷 sem foto")
                with c2:
                    novo_nome = st.text_input("Nome", value=p.get("nome",""), key=f"edit_nome_{i}")
                    novo_preco = st.number_input("Preço", value=float(p.get("preco",0) or 0), format="%.2f", key=f"edit_preco_{i}")
                with c3:
                    nova_foto = st.file_uploader("Nova foto (opcional)", type=["jpg","jpeg","png","webp"], key=f"edit_foto_{i}")
                    novo_link = st.text_input("Ou novo link", value=p.get("img","") if p.get("img","").startswith("http") else "", key=f"edit_link_{i}")
                with c4:
                    st.write("")
                    if st.button("💾 Salvar", key=f"save_{i}"):
                        # atualiza nome e preco
                        produtos[i]["nome"] = novo_nome
                        produtos[i]["preco"] = float(novo_preco)
                        # se trocou foto
                        if nova_foto:
                            os.makedirs("midia_produtos", exist_ok=True)
                            caminho = f"midia_produtos/{nova_foto.name.replace(' ','_')}"
                            with open(caminho, "wb") as f: f.write(nova_foto.getbuffer())
                            salvar_no_github(caminho, nova_foto.getvalue(), f"Atualiza foto {novo_nome}")
                            produtos[i]["img"] = caminho
                            produtos[i]["foto"] = caminho
                        elif novo_link:
                            produtos[i]["img"] = novo_link
                            produtos[i]["foto"] = novo_link
                        salvar_json("produtos.json", produtos)
                        st.success("Atualizado!")
                        st.rerun()
                    if st.button("🗑️ Excluir", key=f"del_{i}", type="primary"):
                        produtos.pop(i)
                        salvar_json("produtos.json", produtos)
                        st.success("Excluído!")
                        st.rerun()

elif menu == "CLIENTES":
    st.header("CLIENTES")
    clientes = carregar_json("clientes.json", [])
    with st.form("cli"):
        nome_c = st.text_input("Nome do Cliente")
        zap = st.text_input("WhatsApp")
        end = st.text_input("Endereço")
        if st.form_submit_button("Cadastrar Cliente"):
            clientes.append({"nome": nome_c, "zap": zap, "end": end})
            salvar_json("clientes.json", clientes)
            st.success("Cliente cadastrado!")
    st.divider()
    st.write("Clientes cadastrados:")
    for c in clientes:
        st.write(f"- {c.get('nome')} - {c.get('zap')}")

elif menu == "FORNECEDORES":
    st.header("FORNECEDORES")
    fornecedores = carregar_json("fornecedores.json", [])
    with st.form("for"):
        nome_f = st.text_input("Nome do Fornecedor")
        prod_f = st.text_input("O que fornece")
        contato = st.text_input("Contato")
        if st.form_submit_button("Cadastrar"):
            fornecedores.append({"nome": nome_f, "produto": prod_f, "contato": contato})
            salvar_json("fornecedores.json", fornecedores)
            st.success("Fornecedor cadastrado!")
    st.divider()
    for f in fornecedores:
        st.write(f"- {f.get('nome')} - {f.get('produto')}")

elif menu == "CONFIGURAÇÃO":
    st.header("CONFIGURAÇÃO")
    st.write("Troca de senha")
    atual = st.text_input("Senha atual", type="password")
    nova = st.text_input("Nova senha", type="password")
    nova2 = st.text_input("Confirme a nova senha", type="password")
    if st.button("Salvar nova senha", type="primary"):
        if atual!= SENHA_ADMIN:
            st.error("Senha atual errada!")
        elif nova!= nova2:
            st.error("Senhas não conferem!")
        elif len(nova) < 4:
            st.error("Senha muito curta!")
        else:
            salvar_json("senha.json", {"senha": nova})
            st.success("Senha trocada! Nova senha: " + nova)
            st.balloons()
