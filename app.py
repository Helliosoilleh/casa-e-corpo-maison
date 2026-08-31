import streamlit as st
import os, json, base64
from PIL import Image
import streamlit.components.v1 as components

st.set_page_config(page_title="CASA E CORPO MAISON", layout="wide")
SEU_NUMERO_WHATSAPP = "5511999999999"

# BARRA DOURADA + SETA
components.html("""
<script>
const parentDoc = window.parent.document;
let style = parentDoc.getElementById('estilo-maison-dourado');
if (!style) {
    style = parentDoc.createElement('style');
    style.id = 'estilo-maison-dourado';
    style.innerHTML = `
        ::-webkit-scrollbar { width: 14px!important; }
        ::-webkit-scrollbar-track { background: #2E2E2E!important; }
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #BF953F 0%, #FCF6BA 50%, #B38728 100%)!important;
            border-radius: 10px!important;
            border: 2px solid #2E2E2E!important;
        }
    `;
    parentDoc.head.appendChild(style);
}
if (!parentDoc.getElementById('btnTopoMaison')) {
    const btn = parentDoc.createElement('div');
    btn.id = 'btnTopoMaison';
    btn.innerText = '↑';
    btn.style.cssText = `position: fixed; width: 50px; height: 50px; bottom: 100px; right: 25px; background: linear-gradient(145deg, #BF953F, #FCF6BA, #B38728); color: #2E2E2E; border-radius: 50%; font-size: 30px; font-weight: 900; line-height: 50px; text-align: center; cursor: pointer; box-shadow: 0 5px 20px rgba(0,0,0,0.5); z-index: 9999999; border: 1.5px solid #B38728;`;
    btn.onclick = () => {
        const main = parentDoc.querySelector('[data-testid="stAppViewContainer"]');
        if (main) main.scrollTo({top: 0, behavior: 'smooth'});
        window.scrollTo({top:0, behavior:'smooth'});
    };
    parentDoc.body.appendChild(btn);
}
</script>
""", height=0)

st.markdown(f"""
<style>
.stAppDeployButton, header, #MainMenu, footer {{display:none!important;}}
.stApp, [data-testid="stAppViewContainer"] {{ background-color: #2E2E2E!important; }}
[data-testid="stSidebar"] {{ background-color: #252525!important; }}
[data-testid="stSidebar"] * {{ color: #E0E0E0!important; }}
h1,h2,h3,p,label {{ color: #F5F5F5!important; }}
.stButton > button {{
    background: linear-gradient(90deg, #BF953F 0%, #FCF6BA 25%, #B38728 50%, #FBF5B7 75%, #AA771C 100%)!important;
    color: #2E2E2E!important; border: 1px solid #B38728!important; font-weight: 900!important; border-radius: 25px!important;
}}
.whatsapp-float {{ position: fixed; width: 180px; height: 55px; bottom: 25px; right: 25px; background-color: #25D366; color: white!important; border-radius: 50px; text-align: center; font-size: 16px; font-weight: 700; box-shadow: 0 6px 20px rgba(0,0,0,0.4); z-index: 9999; display: flex; align-items: center; justify-content: center; gap: 8px; text-decoration: none!important;}}
.product-card {{ border: 1px solid #e9e9e9; border-radius: 16px; padding: 12px; height: 560px; display: flex; flex-direction: column; justify-content: space-between; background: white!important; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }}
.img-box {{ height: 300px; width: 100%; background: #FFFFFF!important; border-radius: 12px; display: flex; align-items: center; justify-content: center; overflow: hidden; }}
.img-box img {{ max-height: 100%; max-width: 100%; object-fit: contain; }}
.product-title {{ font-size: 14px; font-weight: 600; min-height: 40px; margin-top: 8px; color: #222!important; }}
.price-tag {{ color: #D50000; font-size: 24px; font-weight: 900; margin: 5px 0; }}
.cat-badge {{ background: linear-gradient(90deg, #BF953F, #FCF6BA, #B38728); color: #2E2E2E; padding: 3px 10px; border-radius: 10px; font-size: 11px; font-weight: 900; display: inline-block; margin-bottom: 5px; border: 1px solid #B38728; }}
.banner-wrapper {{ position: relative; width: 100%; height: 600px; overflow: hidden; display: flex; justify-content: center; align-items: center; }}
.banner-wrapper img,.banner-wrapper video {{ position: absolute; top:0; left:0; width:100%; height:100%; object-fit: cover; }}
.nome-centro {{ position: relative; z-index:10; font-family: 'Great Vibes', cursive; font-size: 5.5vw; background: linear-gradient(90deg, #BF953F 0%, #FCF6BA 20%, #B38728 40%, #FBF5B7 60%, #AA771C 80%, #FCF6BA 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; filter: drop-shadow(0 2px 5px rgba(0,0,0,0.8)); font-weight: 900; }}
.colecao-titulo {{ text-align:center; margin-top:30px; font-family:serif; color: #F5F5F5!important; font-size: 32px; }}
</style>
<link href="https://fonts.googleapis.com/css2?family=Great+Vibes&display=swap" rel="stylesheet">
<a href="https://wa.me/{SEU_NUMERO_WHATSAPP}?text=Olá! Vim pela loja Casa e Corpo Maison 💛" target="_blank" class="whatsapp-float">💬 Fale conosco</a>
""", unsafe_allow_html=True)

PASTA_MIDIA = "midia_loja"
PASTA_PRODUTOS = "midia_produtos"
ARQUIVO_CONFIG = "config_loja.json"
ARQUIVO_PRODUTOS = "produtos.json"
for p in [PASTA_MIDIA, PASTA_PRODUTOS]:
    if not os.path.exists(p): os.makedirs(p)
CATEGORIAS_PADRAO = ["🎄 Natal", "🏠 Casa", "🧴 Corpo", "🎁 Kits", "✨ Mais Vendidos"]

def carregar_config():
    if os.path.exists(ARQUIVO_CONFIG):
        with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
            d = json.load(f)
            if "banner_ativo" not in d: d["banner_ativo"] = None
            if "categorias" not in d: d["categorias"] = CATEGORIAS_PADRAO
            if "banners" not in d: d["banners"] = []
            return d
    return {"banners": [], "banner_ativo": None, "categorias": CATEGORIAS_PADRAO}

def salvar_config(d):
    with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f: json.dump(d, f, indent=2, ensure_ascii=False)

def get_base64(p):
    try:
        with open(p, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

def carregar_produtos():
    if os.path.exists(ARQUIVO_PRODUTOS):
        with open(ARQUIVO_PRODUTOS, "r", encoding="utf-8") as f: return json.load(f)
    return []

def salvar_produtos(lista):
    with open(ARQUIVO_PRODUTOS, "w", encoding="utf-8") as f: json.dump(lista, f, indent=2, ensure_ascii=False)

if "carrinho" not in st.session_state: st.session_state["carrinho"] = []
if "categoria_ativa" not in st.session_state: st.session_state["categoria_ativa"] = "Todas"

def add_carrinho(prod):
    for item in st.session_state["carrinho"]:
        if item["codigo"] == prod["codigo"]:
            item["qtd"] += 1
            return
    st.session_state["carrinho"].append({"codigo": prod["codigo"], "descricao": prod["descricao"], "valor": prod.get("valor","0"), "foto": prod.get("foto"), "qtd":1})

@st.dialog("🛒 Meu Carrinho", width="large")
def modal_carrinho():
    carrinho = st.session_state["carrinho"]
    if not carrinho: st.info("Seu carrinho está vazio!"); return
    total=0
    for i, item in enumerate(carrinho):
        c1,c2,c3,c4 = st.columns([1,2,1,1])
        with c1:
            if item.get("foto") and os.path.exists(item["foto"]): st.image(item["foto"], width=80)
        with c2:
            st.write(f"**{item['codigo']} - {item['descricao']}**")
            st.markdown(f"<span style='color:#D50000; font-weight:800;'>R$ {item['valor']} x {item['qtd']}</span>", unsafe_allow_html=True)
        with c3:
            if st.button("➖", key=f"menos_{i}"): item["qtd"]-=1; carrinho.pop(i) if item["qtd"]<=0 else None; st.rerun()
            if st.button("➕", key=f"mais_{i}"): item["qtd"]+=1; st.rerun()
        with c4:
            if st.button("🗑️", key=f"rem_{i}"): carrinho.pop(i); st.rerun()
        try: total+=float(item['valor'].replace(',','.'))*item['qtd']
        except: pass
        st.divider()
    st.markdown(f"<h2 style='color:#FFD700;'>Total: R$ {total:.2f}</h2>", unsafe_allow_html=True)
    if st.button("💬 Finalizar no WhatsApp", use_container_width=True):
        msg="Ola! Quero comprar:%0A"
        for it in carrinho: msg+=f"- {it['codigo']} {it['descricao']} x{it['qtd']} - R$ {it['valor']}%0A"
        msg+=f"%0ATotal: R$ {total:.2f}"
        link=f"https://wa.me/{SEU_NUMERO_WHATSAPP}?text={msg}"
        st.markdown(f'<a href="{link}" target="_blank" style="background:#25D366; color:white; padding:12px 20px; border-radius:25px; text-decoration:none; font-weight:800; display:block; text-align:center;">ABRIR WHATSAPP AGORA</a>', unsafe_allow_html=True)

@st.dialog("Detalhes do Produto", width="large")
def modal_produto(prod):
    col1,col2 = st.columns([1.2,1])
    with col1:
        if prod.get("foto") and os.path.exists(prod["foto"]): st.image(prod["foto"], use_container_width=True)
    with col2:
        st.markdown(f"<span class='cat-badge'>{prod.get('categoria','Sem categoria')}</span>", unsafe_allow_html=True)
        st.markdown(f"### {prod['descricao']}")
        st.write(f"**Código:** {prod['codigo']}")
        st.markdown(f"<h2 style='color:#D50000; font-weight:900;'>R$ {prod.get('valor','0,00')}</h2>", unsafe_allow_html=True)
        st.write(prod.get("info_adicional",""))
        if st.button("🛒 Adicionar ao Carrinho", key=f"add_modal_{prod['codigo']}", use_container_width=True, type="primary"):
            add_carrinho(prod); st.toast(f"{prod['codigo']} adicionado! 🛒")

config=carregar_config()
produtos=carregar_produtos()
qtd_carrinho=sum(item["qtd"] for item in st.session_state["carrinho"])
top_col1, top_col2 = st.columns([5,1])
with top_col1: st.markdown("<h3 style='color:#FFD700;'>CASA E CORPO MAISON</h3>", unsafe_allow_html=True)
with top_col2:
    if st.button(f"🛒 Carrinho ({qtd_carrinho})", use_container_width=True): modal_carrinho()

pagina = st.sidebar.radio("Ir para:", ["🏠 LOJA", "⚙️ BANNER", "📦 CADASTRO DE PRODUTOS"])

if pagina=="🏠 LOJA":
    banner=config.get("banner_ativo")
    html_banner=""
    if banner and os.path.exists(banner):
        b64=get_base64(banner)
        if banner.lower().endswith((".png",".jpg",".jpeg",".webp")): html_banner=f'<img src="data:image/jpeg;base64,{b64}" />'
        else: html_banner=f'<video autoplay loop muted playsinline><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video>'
    else: html_banner='<img src="https://via.placeholder.com/1200x600?text=SUA+CAPA+AQUI" />'
    st.markdown(f"""<div class="banner-wrapper">{html_banner}<div class="nome-centro">Casa e Corpo Maison</div></div>""", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#FFD700; text-align:center;'>✨ NOSSAS COLEÇÕES ✨</h4>", unsafe_allow_html=True)
    cats = ["Todas"] + config.get("categorias", CATEGORIAS_PADRAO)
    cols_cat = st.columns(len(cats))
    for i, cat in enumerate(cats):
        with cols_cat[i]:
            if st.button(cat, key=f"cat_{cat}", use_container_width=True, type="primary" if st.session_state["categoria_ativa"]==cat else "secondary"):
                st.session_state["categoria_ativa"]=cat; st.rerun()
    produtos_filtrados=produtos if st.session_state["categoria_ativa"]=="Todas" else [p for p in produtos if p.get("categoria")==st.session_state["categoria_ativa"]]
    st.markdown(f"<div class='colecao-titulo'> {st.session_state['categoria_ativa']} - {len(produtos_filtrados)} produtos</div>", unsafe_allow_html=True)
    if not produtos_filtrados: st.info(f"Nenhum produto na categoria {st.session_state['categoria_ativa']} ainda.")
    else:
        cols=st.columns(4)
        for i, prod in enumerate(produtos_filtrados):
            with cols[i%4]:
                foto_b64=get_base64(prod.get("foto","")) if prod.get("foto") and os.path.exists(prod.get("foto")) else ""
                img_tag = f'<img src="data:image/jpeg;base64,{foto_b64}" />' if foto_b64 else f'<img src="https://placehold.co/400x400?text={prod["codigo"]}" />'
                html_card=f"""<div class="product-card"><div><span class="cat-badge">{prod.get('categoria','')}</span></div><div class="img-box">{img_tag}</div><div class="product-title">{prod['codigo']} - {prod['descricao']}</div><div class="price-tag">R$ {prod.get('valor','0,00')}</div></div>"""
                st.markdown(html_card, unsafe_allow_html=True)
                if st.button(f"🔍 Ver", key=f"ver_loja_{i}_{prod['codigo']}", use_container_width=True): modal_produto(prod)
                if st.button("🛒 Adicionar", key=f"add_loja_{i}_{prod['codigo']}", use_container_width=True, type="primary"): add_carrinho(prod); st.toast("Adicionado! 🛒")

elif pagina=="⚙️ BANNER":
    st.title("⚙️ Banner da Loja")
    arqs=st.file_uploader("Arraste banner", accept_multiple_files=True, type=None, label_visibility="collapsed")
    if arqs:
        for arq in arqs:
            caminho=os.path.join(PASTA_MIDIA, arq.name)
            with open(caminho, "wb") as f: f.write(arq.getbuffer())
            if caminho not in config["banners"]: config["banners"].append(caminho)
        if config["banner_ativo"] is None and config["banners"]: config["banner_ativo"]=config["banners"][0]
        salvar_config(config); st.rerun()
    for i, item in enumerate(config["banners"]):
        c1,c2,c3=st.columns([3,1,1])
        c1.write(f"✅ {os.path.basename(item)} {'⭐ NA LOJA' if item==config['banner_ativo'] else ''}")
        if c2.button("Usar", key=f"usar_{i}"): config["banner_ativo"]=item; salvar_config(config); st.rerun()
        if c3.button("🗑️", key=f"del_b_{i}"):
            if os.path.exists(item): os.remove(item)
            config["banners"].remove(item); salvar_config(config); st.rerun()

else:
    st.title("📦 CADASTRO DE PRODUTOS")
    aba1, aba2, aba3 = st.tabs(["➕ CADASTRAR NOVO", "📋 VER / EDITAR", "🏷️ CATEGORIAS"])
    with aba1:
        with st.form("form_cadastro", clear_on_submit=True):
            codigo=st.text_input("CÓDIGO DO PRODUTO *")
            descricao=st.text_input("DESCRIÇÃO DO PRODUTO *")
            valor=st.text_input("VALOR DO PRODUTO * R$ (ex: 199,90)")
            categoria=st.selectbox("CATEGORIA *", options=config.get("categorias", CATEGORIAS_PADRAO))
            foto=st.file_uploader("FOTO DO PRODUTO *", type=["jpg","jpeg","png","webp","bmp","gif"])
            info_adicional=st.text_area("INFORMAÇÕES ADICIONAIS")
            if st.form_submit_button("💾 SALVAR PRODUTO", use_container_width=True):
                if not codigo or not descricao or not valor or not foto: st.error("Preencha Código, Descrição, VALOR e Foto!")
                elif any(p['codigo']==codigo for p in produtos): st.error("Já existe esse código!")
                else:
                    nome_foto=f"{codigo}_{foto.name}"
                    caminho_foto=os.path.join(PASTA_PRODUTOS, nome_foto)
                    with open(caminho_foto, "wb") as f: f.write(foto.getbuffer())
                    produtos.append({"codigo": codigo, "descricao": descricao, "valor": valor, "categoria": categoria, "foto": caminho_foto, "info_adicional": info_adicional})
                    salvar_produtos(produtos); st.success(f"Produto {codigo} cadastrado!"); st.rerun()
    with aba2:
        busca=st.text_input("🔍 PESQUISAR por NOME ou CÓDIGO")
        filtrados=[p for p in produtos if busca.lower() in p['codigo'].lower() or busca.lower() in p['descricao'].lower()] if busca else produtos
        st.write(f"Encontrados: {len(filtrados)}")
        for prod in filtrados:
            idx_real=produtos.index(prod)
            with st.container(border=True):
                c1,c2,c3=st.columns([1,2,1])
                with c1:
                    if prod.get("foto") and os.path.exists(prod["foto"]): st.image(prod["foto"], width=120)
                with c2:
                    st.write(f"**{prod['codigo']} | {prod.get('categoria','')}**")
                    st.write(f"{prod['descricao']}")
                    st.markdown(f"**R$ {prod.get('valor','0,00')}**")
                with c3:
                    if st.button("✏️ EDITAR", key=f"edit_{idx_real}"): st.session_state["editando"]=idx_real
                    if st.button("🗑️ EXCLUIR", key=f"del_{idx_real}"):
                        if os.path.exists(prod["foto"]): os.remove(prod["foto"])
                        produtos.pop(idx_real); salvar_produtos(produtos); st.rerun()
        if "editando" in st.session_state:
            idx_e=st.session_state["editando"]; prod_e=produtos[idx_e]
            st.divider(); st.subheader(f"✏️ Editando: {prod_e['codigo']}")
            with st.form("form_editar"):
                novo_codigo=st.text_input("Código", value=prod_e["codigo"])
                nova_desc=st.text_input("Descrição", value=prod_e["descricao"])
                novo_valor=st.text_input("Valor R$", value=prod_e.get("valor",""))
                nova_cat=st.selectbox("Categoria", options=config.get("categorias", CATEGORIAS_PADRAO))
                nova_info=st.text_area("Informações", value=prod_e.get("info_adicional",""))
                nova_foto=st.file_uploader("Trocar foto? (opcional)", type=["jpg","jpeg","png","webp"])
                c1,c2=st.columns(2)
                if c1.form_submit_button("💾 SALVAR"):
                    prod_e["codigo"]=novo_codigo; prod_e["descricao"]=nova_desc; prod_e["valor"]=novo_valor; prod_e["categoria"]=nova_cat; prod_e["info_adicional"]=nova_info
                    if nova_foto:
                        if os.path.exists(prod_e["foto"]): os.remove(prod_e["foto"])
                        caminho_nova=os.path.join(PASTA_PRODUTOS, f"{novo_codigo}_{nova_foto.name}")
                        with open(caminho_nova, "wb") as f: f.write(nova_foto.getbuffer())
                        prod_e["foto"]=caminho_nova
                    salvar_produtos(produtos); del st.session_state["editando"]; st.rerun()
                if c2.form_submit_button("Cancelar"): del st.session_state["editando"]; st.rerun()
    with aba3:
        st.write("Categorias:", config.get("categorias", CATEGORIAS_PADRAO))
        nova_cat_input=st.text_input("Criar nova categoria")
        if st.button("➕ Adicionar Categoria"):
            if nova_cat_input and nova_cat_input not in config["categorias"]:
                config["categorias"].append(nova_cat_input); salvar_config(config); st.rerun()
        cat_del=st.selectbox("Remover categoria:", options=config.get("categorias", CATEGORIAS_PADRAO))
        if st.button("🗑️ Remover"): config["categorias"].remove(cat_del); salvar_config(config); st.rerun()
