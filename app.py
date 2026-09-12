import streamlit as st, json, os, base64, requests, glob
import streamlit.components.v1 as components
st.set_page_config(page_title="Casa e Corpo Maison", layout="wide")

if "carrinho" not in st.session_state: st.session_state.carrinho = {}
if "pagina" not in st.session_state: st.session_state.pagina = "loja"
if "tipo_entrega" not in st.session_state: st.session_state.tipo_entrega = "entrega"
if "cep_cliente" not in st.session_state: st.session_state.cep_cliente = ""
if "frete_valor" not in st.session_state: st.session_state.frete_valor = 0.0

frete_gratis_liberado = False
try:
    if st.query_params.get("fretegratis") == "1" or st.query_params.get("cupom") == "MAISONFRETE":
        frete_gratis_liberado = True
except: pass

def carregar_json(arq, padrao):
    try:
        if os.path.exists(arq):
            with open(arq, "r", encoding="utf-8") as f:
                d = json.load(f)
                if isinstance(d, dict) and "produtos" in d: return d["produtos"]
                return d
    except: pass
    return padrao

def achar_imagem(caminho):
    # AGORA RECEBE COMANDOS DO ADMIN: procura onde o ADMIN salva
    if not caminho: return None
    if caminho.startswith("http"): return caminho
    if os.path.exists(caminho): return caminho
    nome = os.path.basename(caminho)
    # O admin salva aqui:
    for tentativa in [
        nome,
        f"midia_produtos/{nome}",
        f"midia_banners/{nome}",
        f"midia/{nome}",
        f"imagens/{nome}",
        f"./{caminho}",
        caminho
    ]:
        if os.path.exists(tentativa): return tentativa
    for g in glob.glob(f"**/{nome}", recursive=True):
        if os.path.exists(g): return g
    return None

def img_para_base64(caminho_real):
    try:
        if caminho_real and os.path.exists(caminho_real):
            with open(caminho_real, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: return ""
    return ""

def calcular_frete(cep, total, taxa_admin=15.0):
    if frete_gratis_liberado or total >= 199: return 0.0, "GRÁTIS"
    if not cep or len("".join(filter(str.isdigit, cep)))!=8: return float(taxa_admin), "Digite CEP"
    p = int("".join(filter(str.isdigit, cep))[:2])
    if 20 <= p <= 28: return 15.00, "Rio - 2 dias"
    elif 1 <= p <= 39: return 25.00, "Sudeste - 4 dias"
    elif 80 <= p <= 91: return 35.00, "Sul - 5 dias"
    else: return 35.00, "Demais - 7 dias"

# ===== RECEBE DADOS DO ADMIN =====
produtos = carregar_json("produtos.json", [])
cfg_loja = carregar_json("config_loja.json", {})
if isinstance(produtos, dict): produtos = list(produtos.values())

total_itens = sum(st.session_state.carrinho.values()) if st.session_state.carrinho else 0
taxa_entrega_admin = float(cfg_loja.get("taxa", 15.0))

# --- TARJA DO ADMIN: topo_natal.png ---
b64_topo = ""
for nome in ["topo_natal.png", "midia_banners/topo_natal.png", "banner_topo.png", "topo.png"]:
    real = achar_imagem(nome)
    if real and not real.startswith("http"):
        b64_topo = img_para_base64(real)
        if b64_topo: break

if b64_topo:
    topo_css = f"background: url(data:image/jpeg;base64,{b64_topo}) center/cover no-repeat;"
    topo_html = "" # SEM NOME POR CIMA - CORRIGIDO
else:
    topo_css = "background: linear-gradient(90deg, #7f0000, #b00000);"
    promo_txt = cfg_loja.get("promocao", "✨ NATAL MAGICO - CASA CORPO E MIMOS ✨")
    topo_html = promo_txt

st.markdown(f"""
<style>
.block-container {{ padding-top: 90px!important; }}
header {{visibility: hidden;}}
.topo-natal-fino {{
    position: fixed; top: 0; left: 0; right: 0; height: 70px;
    {topo_css}
    z-index: 9999990; display: flex; align-items: center; justify-content: center;
    border-bottom: 2px solid #d4af37; color: #ffd700; font-weight:700; font-size:18px;
}}
.foto-produto-fixa {{
    width: 100%!important; height: 280px!important;
    object-fit: contain!important; object-position: center!important;
    border-radius: 12px!important; background: #fff!important; padding: 5px!important;
    display: block!important;
}}
</style>
<div class="topo-natal-fino">{topo_html}</div>
""", unsafe_allow_html=True)

components.html("""
<script>
function moverCarrinho(){
  try{
    const pd = window.parent.document;
    pd.querySelectorAll('button[kind="primary"]').forEach(btn=>{
      if(btn.innerText.includes('CARRINHO') &&!btn.dataset.movido){
        btn.dataset.movido="1";
        btn.style.position="fixed"; btn.style.top="14px"; btn.style.right="20px";
        btn.style.zIndex="9999999"; btn.style.width="180px"; btn.style.height="44px";
        btn.style.background="linear-gradient(145deg, #ff2222, #cc0000)";
        btn.style.borderRadius="30px"; btn.style.color="white"; btn.style.fontWeight="bold";
      }
    });
  }catch(e){}
}
setTimeout(moverCarrinho, 300); setInterval(moverCarrinho, 2000);
</script>
""", height=0)

if st.button(f"🛒 CARRINHO ({total_itens})", key="carrinho_real_fixo", type="primary"):
    st.session_state.pagina = "carrinho" if st.session_state.pagina=="loja" else "loja"; st.rerun()

# CARRINHO
if st.session_state.pagina == "carrinho":
    if st.button("← Voltar à loja"): st.session_state.pagina="loja"; st.rerun()
    st.subheader(f"🛒 Carrinho - {total_itens} itens"); st.divider()
    total_valor=0
    for id_prod,qtd in list(st.session_state.carrinho.items()):
        if id_prod < len(produtos):
            p=produtos[id_prod]; preco=float(p.get('preco',0) or 0); total_valor+=preco*qtd
            c1,c2,c3=st.columns([1,3,2])
            with c1:
                path = achar_imagem(p.get("img","") or p.get("foto","") or p.get("imagem",""))
                if path: st.image(path, width=90)
            with c2: st.write(f"**{p.get('nome')}**"); st.write(f"R$ {preco:.2f} x {qtd}")
            with c3:
                a,b,c=st.columns(3)
                if a.button("➖", key=f"menos_{id_prod}"):
                    if qtd>1: st.session_state.carrinho[id_prod]-=1
                    else: del st.session_state.carrinho[id_prod]
                    st.rerun()
                b.write(f"{qtd}")
                if c.button("➕", key=f"mais_{id_prod}"): st.session_state.carrinho[id_prod]+=1; st.rerun()
            st.divider()
    opcao = st.radio("Entrega:", ["🚚 Entregar por CEP", "🏠 Retirar no Rio - GRÁTIS"], index=0 if st.session_state.tipo_entrega=="entrega" else 1)
    if "Retirar" in opcao:
        st.session_state.tipo_entrega="retirada"; st.session_state.frete_valor=0.0; st.success("Frete GRÁTIS!")
    else:
        st.session_state.tipo_entrega="entrega"
        cep = st.text_input("CEP", value=st.session_state.cep_cliente, placeholder="22071-060")
        st.session_state.cep_cliente=cep
        frete,info=calcular_frete(cep, total_valor, taxa_entrega_admin); st.session_state.frete_valor=frete
        st.info(f"Frete R$ {frete:.2f} - {info}" if frete>0 else "🎉 FRETE GRÁTIS!")
    st.metric("TOTAL", f"R$ {total_valor + st.session_state.frete_valor:.2f}")
    if st.button("✅ Pagamento", type="primary", use_container_width=True): st.session_state.pagina="checkout"; st.rerun()
    st.stop()

if st.session_state.pagina == "checkout":
    if st.button("← Voltar"): st.session_state.pagina="carrinho"; st.rerun()
    st.title("Finalizar");
    total=sum([float(produtos[i].get('preco',0) or 0)*q for i,q in st.session_state.carrinho.items() if i < len(produtos)])
    st.metric("TOTAL FINAL", f"R$ {total + st.session_state.frete_valor:.2f}")
    if cfg_loja.get("chave_pix"):
        st.info(f"PIX: {cfg_loja.get('nome_pix')} - {cfg_loja.get('chave_pix')}")
    if st.button("🎄 FINALIZAR", type="primary"): st.balloons(); st.success("Pedido feito!"); st.session_state.carrinho={}; st.session_state.pagina="loja"; st.rerun()
    st.stop()

# BANNER GRANDE QUE VEM DO ADMIN
ban = cfg_loja.get("banner_atual") if isinstance(cfg_loja, dict) else None
if ban:
    real_ban = achar_imagem(ban)
    if real_ban:
        if real_ban.lower().endswith((".mp4",".mov",".webm")): st.video(real_ban, autoplay=True, loop=True, muted=True)
        else: st.image(real_ban, use_container_width=True)

# PROMOÇÃO QUE VEM DO ADMIN
if cfg_loja.get("promocao") and not b64_topo:
    st.info(f"📢 {cfg_loja.get('promocao')}")

st.title("Nossos Produtos"); st.divider()
if not produtos: st.warning("Sem produtos em produtos.json - cadastre no ADMIN")
else:
    cols=st.columns(3, gap="large")
    for i,p in enumerate(produtos):
        with cols[i%3]:
            with st.container(border=True):
                caminho_original = p.get("img","") or p.get("foto","") or p.get("imagem","")
                caminho_real = achar_imagem(caminho_original)
                if caminho_real:
                    if caminho_real.startswith("http"):
                        st.markdown(f'<img src="{caminho_real}" class="foto-produto-fixa">', unsafe_allow_html=True)
                    else:
                        b64 = img_para_base64(caminho_real)
                        if b64: st.markdown(f'<img src="data:image/jpeg;base64,{b64}" class="foto-produto-fixa">', unsafe_allow_html=True)
                        else: st.image(caminho_real, use_container_width=True)
                else:
                    st.markdown(f'<div style="height:280px;background:#f5f5f5;display:flex;align-items:center;justify-content:center;border-radius:12px">📷 {p.get("nome","")}</div>', unsafe_allow_html=True)
                st.write(f"**{p.get('nome')}**"); st.write(f"**R$ {float(p.get('preco',0) or 0):.2f}**")
                if st.session_state.carrinho.get(i,0)>0: st.success(f"✅ {st.session_state.carrinho.get(i)} no carrinho")
                if st.button("Acrescentar 🛒", key=f"add_{i}", use_container_width=True):
                    st.session_state.carrinho[i]=st.session_state.carrinho.get(i,0)+1; st.rerun()
