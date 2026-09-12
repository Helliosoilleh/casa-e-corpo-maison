import streamlit as st
import os, json, base64

st.set_page_config(page_title="Casa e Corpo Maison", layout="wide", initial_sidebar_state="collapsed")

# ===== CSS IGUAL AO SEU ORIGINAL - SEM IMAGEM DE BOCA =====
st.markdown("""
<style>
.block-container{padding:0 !important; max-width:100% !important}
header, footer{visibility:hidden}
.top-bar{background:#5c0a0a; color:#FFD700; text-align:center; padding:8px; font-weight:bold; letter-spacing:2px; font-size:13px}
.header-loja{background:#7a1010; color:white; padding:12px 25px; display:flex; justify-content:space-between}
.banner-original{
    background: linear-gradient(90deg, #7a1010 0%, #a31a1a 100%);
    height:300px; display:flex; flex-direction:column;
    align-items:center; justify-content:center; color:#FFD700;
    text-align:center; border-bottom:5px solid #FFD700;
}
.banner-original h1{font-size:42px; margin:0; letter-spacing:4px; color:#FFD700; text-shadow:0 2px 10px rgba(0,0,0,0.5)}
.banner-original p{color:white; font-size:16px; margin-top:8px; letter-spacing:2px}
.card{border:1px solid #eee; border-radius:12px; padding:10px; background:white; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.05)}
.preco{color:#7a1010; font-weight:bold; margin:6px 0}
</style>
<div class="top-bar">✨ NATAL MÁGICO - CASA E CORPO E MIMOS ✨</div>
<div class="banner-original">
    <h1>CASA E CORPO MAISON</h1>
    <p>Coleção Natal Mágico</p>
</div>
<br>
""", unsafe_allow_html=True)

ARQ = "produtos.json"

def carregar():
    if os.path.exists(ARQ):
        try:
            with open(ARQ, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def salvar(lista):
    with open(ARQ, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)

# ========== ADMIN ?admin=true - SOLUÇÃO DEFINITIVA ==========
if "admin" in st.query_params:
    st.title("Painel - Casa e Corpo Maison")
    st.caption("Aqui é igual empresa normal: cadastra com foto e já aparece na loja. Sem código.")
    produtos = carregar()

    # LIMPEZA: tira produtos quebrados e falsos de uma vez
    if st.button("🗑️ LIMPAR TUDO QUE ESTÁ QUEBRADO E COMEÇAR DO ZERO"):
        salvar([])
        st.success("Limpo! Agora cadastra de novo certo.")
        st.rerun()

    with st.form("novo", clear_on_submit=True):
        nome = st.text_input("Nome do produto")
        preco = st.text_input("Preço", placeholder="R$ 59,90")
        foto = st.file_uploader("Arraste a foto AQUI - Obrigatório", type=["jpg","jpeg","png","webp"])
        if st.form_submit_button("SALVAR NA LOJA", use_container_width=True):
            if foto and nome and preco:
                b64 = base64.b64encode(foto.getvalue()).decode()
                produtos.append({"nome": nome, "preco": preco, "foto": b64})
                salvar(produtos)
                st.success(f"{nome} já está na loja!")
                st.balloons()
            else:
                st.error("Preencha nome, preço e ARRASTE a foto.")

    st.divider()
    st.write(f"Produtos hoje: {len(produtos)}")
    for i, p in enumerate(produtos):
        c1,c2,c3 = st.columns([1,4,1])
        with c1:
            if p.get("foto"):
                st.image(base64.b64decode(p["foto"]), width=80)
        with c2:
            st.write(f"**{p.get('nome','')}** - {p.get('preco','')}")
        with c3:
            if st.button("Excluir", key=f"ex_{i}"):
                produtos.pop(i)
                salvar(produtos)
                st.rerun()

# ========== LOJA ==========
else:
    produtos = carregar()
    st.subheader("🎄 Nossos Produtos")
    if not produtos:
        st.info("Loja vazia no momento.")
    else:
        cols = st.columns(3)
        for idx, p in enumerate(produtos):
            with cols[idx % 3]:
                if p.get("foto"):
                    try:
                        st.image(base64.b64decode(p["foto"]), use_container_width=True)
                    except:
                        pass
                st.markdown(f'<div class="card"><b>{p.get("nome","")}</b><div class="preco">{p.get("preco","")}</div><button style="background:#7a1010;color:white;border:0;padding:8px;width:100%;border-radius:6px">Comprar</button></div>', unsafe_allow_html=True)
                st.write("")
