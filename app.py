import streamlit as st
import json, os, base64

st.set_page_config(page_title="Casa e Corpo Maison", layout="wide")

# --- TARJA QUE VOCÊ JÁ DEIXOU PERFEITA ---
st.markdown("""
<style>
.top-faixa{background:#5c0a0a;color:#FFD700;text-align:center;padding:7px;font-size:12px;letter-spacing:2px;font-weight:bold}
.header{background:#7a1010;color:white;padding:15px 30px;display:flex;justify-content:space-between;align-items:center}
.card{border:1px solid #eee;border-radius:14px;padding:12px;text-align:center;background:white}
</style>
<div class="top-faixa">✨ NATAL MÁGICO - CASA E CORPO E MIMOS ✨</div>
<div class="header"><div><b>Casa e Corpo Maison</b></div><div>🛒 CARRINHO</div></div>
<br>
""", unsafe_allow_html=True)

ARQ = "produtos.json"

def carregar():
    if os.path.exists(ARQ):
        try:
            with open(ARQ, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return []

def salvar(lista):
    with open(ARQ, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)

# ===== MODO ADMIN: ?admin=true =====
if st.query_params.get("admin") == "true":
    st.title("Painel da Loja - Cadastro de Produtos")
    st.write("Aqui você cadastra igual empresa normal. Sem código.")
    
    produtos = carregar()
    
    with st.form("cadastro", clear_on_submit=True):
        nome = st.text_input("Nome do produto *")
        preco = st.text_input("Preço *", placeholder="R$ 99,90")
        foto = st.file_uploader("Arraste a foto aqui *", type=["jpg","jpeg","png"])
        enviar = st.form_submit_button("SALVAR NA LOJA")
        
        if enviar:
            if not nome or not preco or not foto:
                st.error("Preenche tudo e arrasta a foto.")
            else:
                b64 = base64.b64encode(foto.getvalue()).decode()
                produtos.append({"nome": nome, "preco": preco, "foto": b64})
                salvar(produtos)
                st.success(f"{nome} cadastrado! Vai na loja que já apareceu.")

    st.divider()
    st.subheader(f"Produtos na loja hoje: {len(produtos)}")
    for i, p in enumerate(produtos):
        col1, col2, col3 = st.columns([1,3,1])
        with col1:
            if p.get("foto"): st.image(base64.b64decode(p["foto"]), width=80)
        with col2: st.write(f"**{p['nome']}** - {p['preco']}")
        with col3:
            if st.button("Excluir", key=f"del_{i}"):
                produtos.pop(i)
                salvar(produtos)
                st.rerun()

# ===== MODO LOJA NORMAL =====
else:
    produtos = carregar()
    st.subheader("Nossos Produtos")
    
    if not produtos:
        st.info("Nenhum produto cadastrado ainda. Entra em ?admin=true pra cadastrar.")
    else:
        cols = st.columns(3)
        for idx, p in enumerate(produtos):
            with cols[idx % 3]:
                if p.get("foto"):
                    st.image(base64.b64decode(p["foto"]), use_container_width=True)
                st.markdown(f'<div class="card"><b>{p["nome"]}</b><br>{p["preco"]}<br><br><button style="background:#7a1010;color:white;border:0;padding:8px 15px;border-radius:20px;width:100%">Comprar</button></div>', unsafe_allow_html=True)
                st.write("")
