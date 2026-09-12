import streamlit as st, json, os, glob, base64, requests
import streamlit.components.v1 as components
st.set_page_config(page_title="Casa e Corpo Maison", layout="wide")

if "carrinho" not in st.session_state: st.session_state.carrinho = {}
if "pagina" not in st.session_state: st.session_state.pagina = "loja"
if "tipo_entrega" not in st.session_state: st.session_state.tipo_entrega = "entrega"
if "cep_cliente" not in st.session_state: st.session_state.cep_cliente = ""
if "frete_valor" not in st.session_state: st.session_state.frete_valor = 0.0

frete_gratis_liberado = False
try:
    qp = st.query_params
    if qp.get("fretegratis") == "1" or qp.get("cupom") == "MAISONFRETE":
        frete_gratis_liberado = True
except: pass

def carregar_json(arq, padrao):
    try:
        if os.path.exists(arq):
            with open(arq, "r", encoding="utf-8") as f:
                dados = json.load(f)
                # se vier dict com chave produtos
                if isinstance(dados, dict) and "produtos" in dados:
                    return dados["produtos"]
                return dados
    except: pass
    return padrao

def img_para_base64(caminho):
    try:
        if caminho and os.path.exists(caminho):
            with open(caminho, "rb") as f:
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

def calcular_frete_por_regiao(cep, total):
    try:
        if frete_gratis_liberado or total >= 199: return 0.0, "GRÁTIS", "Frete Grátis"
        if not cep or len("".join(filter(str.isdigit, cep)))!= 8: return 19.90, "A calcular", "Digite CEP"
        prefix = int("".join(filter(str.isdigit, cep))[:2])
        if 20 <= prefix <= 28: return 15.00, "PAC 2 dias", "Rio"
        elif (1 <= prefix <= 19) or (29 <= prefix <= 39): return 25.00, "PAC 4 dias", "Sudeste"
        elif 80 <= prefix <= 91: return 35.00, "PAC 5 dias", "Sul"
        else: return 35.00, "PAC 7 dias", "Outros"
    except: return 19.90, "A calcular", ""

produtos = carregar_json("produtos.json", [])
if not produtos:
    # tenta outras pastas
    for p in ["produtos/produtos.json", "data/produtos.json"]:
        produtos = carregar_json(p, [])
        if produtos: break
if isinstance(produtos, dict): produtos = list(produtos.values())

total_itens = sum(st.session_state.carrinho.values()) if st.session_state.carrinho else 0

b64_topo = ""
for nome in ["topo_natal.png", "luxury_christmas_banner.webp", "banner_topo.png", "topo.png"]:
    if os.path.exists(nome):
        b64_topo = img_para_base64(nome)
        if b64_topo: break

# CSS BLINDADO
if b64_topo:
    topo_style = f"background: url(data:image/webp;base64,{b64_topo}) center/cover no-repeat;"
else:
    topo_style = "background: linear-gradient(90deg, #7f0000, #b00000);"

st.markdown(f"""
<style>
.block-container {{ padding-top: 90px!important; }}
header {{visibility: hidden;}}
.topo-natal-fino {{
    position: fixed; top: 0; left: 0; right: 0; height: 70px;
    {topo_style}
    z-index: 9999990; display: flex; align-items: center; justify-content: center;
    border-bottom: 2px solid #d4af37; color: #ffd700; font-weight:700;
}}
.foto-produto-fixa {{
    width: 100%!important; height: 280px!important;
    object-fit: contain!important; object-position: center center!important;
    border-radius: 12px!important; background: #ffffff!important; padding: 5px!important;
    display: block!important;
}}
</style>
<div class="topo-natal-fino">✨ NATAL MAGICO - CASA CORPO E MIMOS ✨</div>
""", unsafe_allow_html=True)

components.html("""
<script>
function moverCarrinho(){
  try{
    const parentDoc = window.parent.document;
    const botoes = parentDoc.querySelectorAll('button[kind="primary"]');
    botoes.forEach(btn => {
      if(btn.innerText.includes('CARRINHO') &&!btn.dataset.movido){
        btn.dataset.movido="1"; btn.style.position="fixed"; btn.style.top="14px"; btn.style.right="20px";
        btn.style.zIndex="9999999"; btn.style.width="180px"; btn.style.height="44px";
        btn.style.background="linear-gradient(145deg, #ff2222, #cc0000)"; btn.style.borderRadius="30px";
        btn.style.color="white"; btn.style.fontWeight="bold";
      }
    });
  }catch(e){}
}
setTimeout(moverCarrinho, 200); setInterval(moverCarrinho, 2000);
</script>
""", height=0)

if st.button(f"🛒 CARRINHO ({total_itens})", key="carrinho_real_fixo", type="primary"):
    st.session_state.pagina = "carrinho" if st.session_state.pagina == "loja" else "loja"; st.rerun()

if st.session_state.pagina == "carrinho":
    if st.button("← Voltar à loja"): st.session_state.pagina="loja"; st.rerun()
    st.subheader(f"🛒 Seu Carrinho - {total_itens} itens"); st.divider()
    total_valor=0
    for id_prod,qtd in list(st.session_state.carrinho.items()):
        if id_prod < len(produtos):
            p=produtos[id_prod]; preco=float(p.get('preco',0) or 0); total_valor+=preco*qtd
            c_img,c_info,c_qtd=st.columns([1,3,2])
            with c_img:
                b64 = img_para_base64(p.get("img","") or p.get("foto",""))
                if b64: st.markdown(f'<img src="data:image/jpeg;base64,{b64}" style="width:90px;height:90px;object-fit:contain;background:white;border-radius:8px">', unsafe_allow_html=True)
            with c_info: st.write(f"**{p.get('nome','')}**"); st.write(f"R$ {preco:.2f} x {qtd}")
            with c_qtd:
                a,b,c=st.columns(3)
                if a.button("➖", key=f"menos_{id_prod}"):
                    if qtd>1: st.session_state.carrinho[id_prod]-=1
                    else: del st.session_state.carrinho[id_prod]
                    st.rerun()
                b.write(f"**{qtd}**")
                if c.button("➕", key=f"mais_{id_prod}"): st.session_state.carrinho[id_prod]+=1; st.rerun()
            st.divider()
    st.subheader("📦 Como quer receber?")
    opcao = st.radio("Escolha:", ["🚚 Entregar - Calcular por CEP", "🏠 Retirar no Rio - GRÁTIS"], index=0 if st.session_state.tipo_entrega=="entrega" else 1)
    if "Retirar" in opcao:
        st.session_state.tipo_entrega="retirada"; st.session_state.frete_valor=0.0
        st.success("🏠 Retirada - Frete GRÁTIS!")
    else:
        st.session_state.tipo_entrega="entrega"
        cep_input = st.text_input("CEP", value=st.session_state.cep_cliente, placeholder="22071-060", key="cep_carrinho")
        st.session_state.cep_cliente=cep_input
        frete,prazo,regiao=calcular_frete_por_regiao(cep_input, total_valor)
        st.session_state.frete_valor=frete
        st.info(f"Frete: R$ {frete:.2f} | {prazo}" if frete>0 else "🎉 FRETE GRÁTIS!")
    st.divider()
    st.metric("TOTAL FINAL", f"R$ {total_valor + st.session_state.frete_valor:.2f}")
    if st.button("✅ Seguir para pagamento", type="primary", use_container_width=True):
        st.session_state.pagina="checkout"; st.rerun()
    st.stop()

if st.session_state.pagina == "checkout":
    if st.button("← Voltar"): st.session_state.pagina="carrinho"; st.rerun()
    st.title("🎄 Finalizar Compra")
    total = sum([float(produtos[i].get('preco',0) or 0)*q for i,q in st.session_state.carrinho.items() if i < len(produtos)])
    st.metric("TOTAL", f"R$ {total + st.session_state.frete_valor:.2f}")
    if st.button("🎄 FINALIZAR PEDIDO", type="primary"): st.balloons(); st.success("Pedido confirmado!"); st.session_state.carrinho={}; st.session_state.pagina="loja"; st.rerun()
    st.stop()

cfg_loja = carregar_json("config_loja.json", {})
banner_atual = cfg_loja.get("banner_atual") if isinstance(cfg_loja, dict) else None
if banner_atual and os.path.exists(banner_atual):
    if banner_atual.lower().endswith((".mp4",".mov",".webm")): st.video(banner_atual, autoplay=True, loop=True, muted=True)
    else: st.image(banner_atual, use_container_width=True)

st.title("Nossos Produtos"); st.divider()
if not produtos:
    st.warning("Nenhum produto em produtos.json - adicione pelo ADMIN")
else:
    cols=st.columns(3, gap="large")
    for i,p in enumerate(produtos):
        with cols[i%3]:
            with st.container(border=True):
                b64 = img_para_base64(p.get("img","") or p.get("foto",""))
                if b64: st.markdown(f'<img src="data:image/jpeg;base64,{b64}" class="foto-produto-fixa">', unsafe_allow_html=True)
                else: st.markdown(f'<div class="foto-produto-fixa">📷 {p.get("nome","")}</div>', unsafe_allow_html=True)
                st.write(f"**{p.get('nome','')}**"); st.write(f"**R$ {float(p.get('preco',0) or 0):.2f}**")
                qtd=st.session_state.carrinho.get(i,0)
                if qtd>0: st.success(f"✅ {qtd} no carrinho")
                if st.button("Acrescentar ao carrinho 🛒", key=f"add_{i}", use_container_width=True):
                    st.session_state.carrinho[i]=st.session_state.carrinho.get(i,0)+1; st.rerun()
