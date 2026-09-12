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
    # CORRECAO FOTO: procura em varios lugares + aceita URL
    if not caminho: return None
    if caminho.startswith("http"): return caminho # url direta
    if os.path.exists(caminho): return caminho
    # tenta sem pasta, com pastas comuns
    nome = os.path.basename(caminho)
    for tentativa in [nome, f"imagens/{nome}", f"midia_produtos/{nome}", f"fotos/{nome}", f"produtos/{nome}", f"midia_banners/{nome}", f"./{caminho}"]:
        if os.path.exists(tentativa): return tentativa
    # tenta glob por nome parecido
    for g in glob.glob(f"**/{nome}", recursive=True):
        return g
    return None

def img_para_base64(caminho_real):
    try:
        if caminho_real and os.path.exists(caminho_real):
            with open(caminho_real, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: return ""
    return ""

def buscar_cep(cep):
    try:
        cep_l = "".join(filter(str.isdigit, cep))
        if len(cep_l)!= 8: return None
        r = requests.get(f"https://viacep.com.br/ws/{cep_l}/json/", timeout=4)
        if r.status_code == 200:
            j = r.json()
            if "erro" not in j: return j
    except: return None
    return None

def calcular_frete(cep, total):
    if frete_gratis_liberado or total >= 199: return 0.0, "GRÁTIS"
    if not cep or len("".join(filter(str.isdigit, cep)))!=8: return 19.90, "Digite CEP"
    p = int("".join(filter(str.isdigit, cep))[:2])
    if 20 <= p <= 28: return 15.00, "Rio - 2 dias"
    elif 1 <= p <= 39: return 25.00, "Sudeste - 4 dias"
    elif 80 <= p <= 91: return 35.00, "Sul - 5 dias"
    else: return 35.00, "Demais - 7 dias"

produtos = carregar_json("produtos.json", [])
for alt in ["produtos/produtos.json", "data/produtos.json"]:
    if not produtos: produtos = carregar_json(alt, [])
if isinstance(produtos, dict): produtos = list(produtos.values())
total_itens = sum(st.session_state.carrinho.values()) if st.session_state.carrinho else 0

# --- TARJA CORRIGIDA: SEM NOME POR CIMA ---
b64_topo = ""
for nome in ["topo_natal.png", "luxury_christmas_banner.webp", "banner_topo.png", "topo.png"]:
    if os.path.exists(nome):
        b64_topo = img_para_base64(nome)
        if b64_topo: break

if b64_topo:
    topo_css = f"background: url(data:image/webp;base64,{b64_topo}) center/cover no-repeat;"
    topo_html = "" # SEM TEXTO POR CIMA QUANDO TEM IMAGEM
else:
    topo_css = "background: linear-gradient(90deg, #7f0000, #b00000);"
    topo_html = "✨ NATAL MAGICO - CASA CORPO E MIMOS ✨"

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
                if path:
                    if path.startswith("http"): st.image(path, width=90)
                    else: st.image(path, width=90)
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
        frete,info=calcular_frete(cep, total_valor); st.session_state.frete_valor=frete
        st.info(f"Frete R$ {frete:.2f} - {info}" if frete>0 else "🎉 FRETE GRÁTIS!")
    st.metric("TOTAL", f"R$ {total_valor + st.session_state.frete_valor:.2f}")
    if st.button("✅ Pagamento", type="primary", use_container_width=True): st.session_state.pagina="checkout"; st.rerun()
    st.stop()

if st.session_state.pagina == "checkout":
    if st.button("← Voltar"): st.session_state.pagina="carrinho"; st.rerun()
    st.title("Finalizar");
    total=sum([float(produtos[i].get('preco',0) or 0)*q for i,q in st.session_state.carrinho.items() if i < len(produtos)])
    st.metric("TOTAL FINAL", f"R$ {total + st.session_state.frete_valor:.2f}")
    if st.button("🎄 FINALIZAR", type="primary"): st.balloons(); st.success("Pedido feito!"); st.session_state.carrinho={}; st.session_state.pagina="loja"; st.rerun()
    st.stop()

# BANNER ADMIN
cfg = carregar_json("config_loja.json", {})
ban = cfg.get("banner_atual") if isinstance(cfg, dict) else None
if ban and os.path.exists(ban):
    if ban.lower().endswith((".mp4",".mov",".webm")): st.video(ban, autoplay=True, loop=True, muted=True)
    else: st.image(ban, use_container_width=True)

st.title("Nossos Produtos"); st.divider()
if not produtos: st.warning("Sem produtos em produtos.json")
else:
    cols=st.columns(3, gap="large")
    for i,p in enumerate(produtos):
        with cols[i%3]:
            with st.container(border=True):
                # CORRECAO FOTO PRODUTO
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
                    st.markdown(f'<div style="height:280px;background:#f5f5f5;display:flex;align-items:center;justify-content:center;border-radius:12px">📷 {p.get("nome","")}<br><small>{caminho_original}</small></div>', unsafe_allow_html=True)

                st.write(f"**{p.get('nome')}**"); st.write(f"**R$ {float(p.get('preco',0) or 0):.2f}**")
                if st.session_state.carrinho.get(i,0)>0: st.success(f"✅ {st.session_state.carrinho.get(i)} no carrinho")
                if st.button("Acrescentar 🛒", key=f"add_{i}", use_container_width=True):
                    st.session_state.carrinho[i]=st.session_state.carrinho.get(i,0)+1; st.rerun()
