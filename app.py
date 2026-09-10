import zipfile, os, shutil, pathlib, json, glob, base64, requests
import streamlit as st
import streamlit.components.v1 as components

if os.path.exists("midia_marketing.zip"):
    with zipfile.ZipFile("midia_marketing.zip", 'r') as z:
        z.extractall(".")
    # pega o produtos.json GRANDE (o seu de Natal)
    for p in pathlib.Path(".").rglob("produtos.json"):
        if p.stat().st_size > 5000:
            shutil.copy(p, "produtos.json")
            break
    # pega banner e fotos
    for p in pathlib.Path(".").rglob("banner_loja*"):
        shutil.copy(p, pathlib.Path(".") / p.name)
    pathlib.Path("midia_produtos").mkdir(exist_ok=True)
    for p in pathlib.Path(".").rglob("*.jpg"):
        if "midia_produtos" in str(p).lower():
            try:
                shutil.copy(p, pathlib.Path("midia_produtos") / p.name)
            except: pass
                
st.set_page_config(page_title="Casa e Corpo Maison", layout="wide")

if "carrinho" not in st.session_state:
    st.session_state.carrinho = {}
if "pagina" not in st.session_state:
    st.session_state.pagina = "loja"
if "tipo_entrega" not in st.session_state:
    st.session_state.tipo_entrega = "entrega"
if "cep_cliente" not in st.session_state:
    st.session_state.cep_cliente = ""
if "frete_valor" not in st.session_state:
    st.session_state.frete_valor = 0.0

# --- LIBERACAO MANUAL DE FRETE POR VOCE ---
frete_gratis_liberado = False
try:
    if st.query_params.get("fretegratis") == "1" or st.query_params.get("cupom") == "MAISONFRETE":
        frete_gratis_liberado = True
except:
    pass

def carregar_json(arq, padrao):
    if os.path.exists(arq):
        try:
            with open(arq, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return padrao
    return padrao

def img_para_base64(caminho):
    try:
        if os.path.exists(caminho):
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
            if "erro" not in j:
                return j
    except:
        return None
    return None

def calcular_frete_por_regiao(cep, total):
    if frete_gratis_liberado or total >= 199:
        return 0.0, "GRÁTIS", "Frete Grátis liberado"
    if not cep or len("".join(filter(str.isdigit, cep)))!= 8:
        return 19.90, "A calcular", "Digite seu CEP"

    cep_n = "".join(filter(str.isdigit, cep))
    prefix = int(cep_n[:2])

    # RJ 20-28
    if 20 <= prefix <= 28:
        return 15.00, "PAC 2 dias úteis", "Rio de Janeiro"
    # Sudeste SP/MG/ES 01-19, 29-39
    elif (1 <= prefix <= 19) or (29 <= prefix <= 39):
        return 25.00, "PAC 4 dias / SEDEX R$35 1 dia", "Sudeste"
    elif 80 <= prefix <= 91:
        return 35.00, "PAC 5 dias", "Sul"
    else:
        return 35.00, "PAC 7 dias", "Demais regiões"

produtos = carregar_json("produtos.json", [])
total_itens = sum(st.session_state.carrinho.values())

b64_topo = ""
for nome in ["topo_natal.png", "luxury_christmas_banner.webp", "banner_topo.png", "topo.png"]:
    if os.path.exists(nome):
        with open(nome, "rb") as f:
            b64_topo = base64.b64encode(f.read()).decode()
        break

st.markdown(f"""
<style>
.block-container {{ padding-top: 90px!important; }}
header {{visibility: hidden;}}
.topo-natal-fino {{
    position: fixed; top: 0; left: 0; right: 0; height: 70px;
    background: url(data:image/webp;base64,{b64_topo}) center/cover no-repeat, #1e1e1e;
    z-index: 9999990; display: flex; align-items: center; justify-content: flex-end;
    padding-right: 20px; border-bottom: 2px solid #d4af37;
}}
[data-testid="stVerticalBlockBorderWrapper"] {{
    border: 1px solid #f0e0a0!important;
    padding: 12px!important;
}}
.foto-produto-fixa {{
    width: 100%!important;
    height: 280px!important;
    min-height: 280px!important;
    max-height: 280px!important;
    object-fit: contain!important;
    object-position: center center!important;
    border-radius: 12px!important;
    display: block!important;
    background: #ffffff!important;
    padding: 5px!important;
}}
.badge-reserva {{ height: 42px!important; display: flex; align-items: center; justify-content: center; margin: 8px 0px!important; }}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stButton"] button {{
    background: linear-gradient(145deg, #ff2a2a, #cc0000, #8B0000)!important;
    color: white!important; border: 1px solid #ff9999!important; border-radius: 10px!important; font-weight: 700!important;
}}
</style>
<div class="topo-natal-fino"></div>
""", unsafe_allow_html=True)

# --- CORREÇÃO DO CARRINHO NA TARJA FLUTUANTE - NÃO MEXE EM MAIS NADA ---
components.html("""
<script>
function moverCarrinho() {
  const parentDoc = window.parent.document;
  const botoes = parentDoc.querySelectorAll('button[kind="primary"]');
  botoes.forEach(btn => {
    if(btn.innerText.includes('CARRINHO') &&!btn.dataset.movido){
      btn.dataset.movido="1";
      btn.style.position="fixed";
      btn.style.top="14px";
      btn.style.right="20px";
      btn.style.zIndex="9999999";
      btn.style.width="180px";
      btn.style.height="44px";
      btn.style.background="linear-gradient(145deg, #ff2222, #cc0000, #8B0000)";
      btn.style.border="1px solid #ff9999";
      btn.style.borderRadius="30px";
      btn.style.boxShadow="0 0 15px rgba(255,0,0,0.7)";
      btn.style.color="white";
      btn.style.fontWeight="bold";
    }
  });
}
setTimeout(moverCarrinho, 100);
setTimeout(moverCarrinho, 500);
setTimeout(moverCarrinho, 1500);
setInterval(moverCarrinho, 2000);
</script>
""", height=0)

if st.button(f"🛒 CARRINHO ({total_itens})", key="carrinho_real_fixo", type="primary"):
    st.session_state.pagina = "carrinho" if st.session_state.pagina == "loja" else "loja"
    st.rerun()

if st.session_state.pagina == "carrinho":
    if st.button("← Voltar à loja"): st.session_state.pagina="loja"; st.rerun()
    st.subheader(f"🛒 Seu Carrinho - {total_itens} itens"); st.divider()
    total_valor=0
    for id_prod,qtd in list(st.session_state.carrinho.items()):
        if id_prod < len(produtos):
            p=produtos[id_prod]; preco=float(p.get('preco',0)); total_valor+=preco*qtd
            c_img,c_info,c_qtd=st.columns([1,3,2])
            with c_img:
                b64 = img_para_base64(p.get("img",""))
                if b64: st.markdown(f'<img src="data:image/jpeg;base64,{b64}" style="width:90px;height:90px;object-fit:contain;background:white;border-radius:8px">', unsafe_allow_html=True)
            with c_info: st.write(f"**{p.get('nome')}**"); st.write(f"R$ {preco:.2f} x {qtd} = **R$ {preco*qtd:.2f}**")
            with c_qtd:
                a,b,c=st.columns(3)
                with a:
                    if st.button("➖", key=f"menos_{id_prod}"):
                        if qtd>1: st.session_state.carrinho[id_prod]-=1
                        else: del st.session_state.carrinho[id_prod]
                        st.rerun()
                with b: st.write(f"**{qtd}**")
                with c:
                    if st.button("➕", key=f"mais_{id_prod}"): st.session_state.carrinho[id_prod]+=1; st.rerun()
            st.divider()

    # ===== OPÇÃO 3 + 4 - FRETE =====
    st.subheader("📦 Como quer receber?")
    opcao = st.radio("Escolha:", ["🚚 Entregar no meu endereço - Calcular por CEP", "🏠 Retirar no Rio - GRÁTIS"], index=0 if st.session_state.tipo_entrega=="entrega" else 1)

    if "Retirar" in opcao:
        st.session_state.tipo_entrega = "retirada"
        frete = 0.0
        st.session_state.frete_valor = frete
        st.success("🏠 Retirada no Rio - Frete GRÁTIS!")
        st.info("📍 Endereço de retirada será enviado no seu WhatsApp após pagamento. Barra da Tijuca - RJ")
    else:
        st.session_state.tipo_entrega = "entrega"
        cep_input = st.text_input("Digite seu CEP", value=st.session_state.cep_cliente, placeholder="Ex: 22071-060", key="cep_carrinho")
        st.session_state.cep_cliente = cep_input

        endereco = None
        if cep_input and len("".join(filter(str.isdigit, cep_input))) == 8:
            endereco = buscar_cep(cep_input)
            if endereco:
                st.write(f"📍 {endereco.get('logradouro','')} - {endereco.get('bairro','')} - {endereco.get('localidade','')}/{endereco.get('uf','')}")

        frete, prazo, regiao = calcular_frete_por_regiao(cep_input, total_valor)
        st.session_state.frete_valor = frete

        if frete_gratis_liberado:
            st.success("🎉 FRETE GRÁTIS LIBERADO por você no WhatsApp!")
        elif frete == 0:
            st.success(f"🎉 FRETE GRÁTIS! Pedido acima de R$ 199 - {regiao}")
        else:
            if not cep_input:
                st.warning(f"📦 Frete estimado: R$ {frete:.2f} - Digite seu CEP para calcular exato")
            else:
                st.info(f"📦 Frete: R$ {frete:.2f} | {prazo} | {regiao}")
                if 150 <= total_valor < 199:
                    st.markdown(f"💛 Falta R$ {199-total_valor:.2f} para frete grátis! [Negociar no WhatsApp](https://wa.me/5521982210843?text=Tenho R$ {total_valor:.2f} no carrinho, libera frete grátis? CEP {cep_input})")

    st.divider()
    st.metric("Subtotal Produtos", f"R$ {total_valor:.2f}")
    st.metric("Frete", f"{'GRÁTIS' if st.session_state.frete_valor==0 else f'R$ {st.session_state.frete_valor:.2f}'}")
    st.metric("TOTAL FINAL", f"R$ {total_valor + st.session_state.frete_valor:.2f}")

    if st.button("✅ Seguir para pagamento", type="primary", use_container_width=True):
        st.session_state.pagina="checkout"; st.rerun()
    st.stop()

if st.session_state.pagina == "checkout":
    if st.button("← Voltar ao carrinho"): st.session_state.pagina="carrinho"; st.rerun()
    st.title("🎄 Finalizar Compra"); st.divider()
    col_esq,col_dir=st.columns([1.2,1], gap="large")
    with col_esq:
        st.subheader("📦 Dados para Entrega")
        with st.container(border=True):
            nome=st.text_input("Nome completo *"); tel=st.text_input("WhatsApp *")
            cpf=st.text_input("CPF *"); email=st.text_input("E-mail *")

            if st.session_state.tipo_entrega == "retirada":
                st.success("🏠 Retirada no Rio - Não precisa preencher endereço")
                cep=st.session_state.cep_cliente
                rua="RETIRADA NO RIO"; numero=""; bairro=""
            else:
                cep=st.text_input("CEP *", value=st.session_state.cep_cliente)
                end_auto = buscar_cep(cep) if cep else None
                rua_val = end_auto.get('logradouro','') if end_auto else ""
                bairro_val = end_auto.get('bairro','') if end_auto else ""
                rua=st.text_input("Rua *", value=rua_val)
                c1,c2=st.columns(2)
                with c1: numero=st.text_input("Número *")
                with c2: bairro=st.text_input("Bairro *", value=bairro_val)
                if end_auto:
                    st.caption(f"Cidade: {end_auto.get('localidade','')}/{end_auto.get('uf','')}")

        st.subheader("💳 Pagamento")
        forma=st.radio("Escolha:", ["💠 Pix (10% OFF)", "💳 Cartão"], horizontal=True)
        with st.container(border=True):
            if "Pix" in forma:
                st.success("10% OFF no Pix!"); st.image("https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=PIX-CASA-CORPO", width=180)
                st.code("casaecorpomaison@email.com")
            else:
                st.text_input("Número do cartão"); st.text_input("Nome no cartão")
                c1,c2,c3=st.columns(3)
                with c1: st.text_input("Validade");
                with c2: st.text_input("CVV");
                with c3: st.selectbox("Parcelas", ["1x","2x","3x","6x","12x"])
    with col_dir:
        st.subheader("🛍️ Resumo")
        with st.container(border=True):
            total=0
            for id_prod,qtd in st.session_state.carrinho.items():
                if id_prod < len(produtos):
                    p=produtos[id_prod]; preco=float(p.get('preco',0)); total+=preco*qtd
                    b64 = img_para_base64(p.get("img",""))
                    cc1,cc2=st.columns([1,2.5])
                    with cc1:
                        if b64: st.markdown(f'<img src="data:image/jpeg;base64,{b64}" style="width:70px;height:70px;object-fit:contain;background:white;border-radius:8px">', unsafe_allow_html=True)
                    with cc2: st.write(f"**{p.get('nome')}** x{qtd} - R$ {preco*qtd:.2f}")
                    st.divider()
            frete_checkout = st.session_state.frete_valor
            if st.session_state.tipo_entrega == "retirada":
                frete_checkout = 0.0
            else:
                f,pz,rg = calcular_frete_por_regiao(st.session_state.cep_cliente, total)
                frete_checkout = f

            st.write(f"Entrega: {'🏠 Retirada RJ - GRÁTIS' if st.session_state.tipo_entrega=='retirada' else f'🚚 {st.session_state.cep_cliente}'}")
            st.write(f"Subtotal: R$ {total:.2f}")
            st.write(f"Frete: {'GRÁTIS' if frete_checkout==0 else f'R$ {frete_checkout:.2f}'}")
            total_final = (total + frete_checkout) * (0.9 if 'Pix' in forma else 1)
            st.metric("TOTAL FINAL", f"R$ {total_final:.2f}")
            if st.button("🎄 FINALIZAR PEDIDO", type="primary", use_container_width=True):
                st.balloons(); st.success(f"Pedido confirmado! {'Retirada no Rio' if st.session_state.tipo_entrega=='retirada' else f'Entrega para CEP {st.session_state.cep_cliente}'}"); st.session_state.carrinho={}
    st.stop()

# LOJA - AGORA COM FOTO INTEIRA
pastas=["midia_loja","midia","banners_da_loja"]
todos=[]
for p in pastas:
    if os.path.exists(p): todos.extend(glob.glob(f"{p}/*"))
if todos:
    validos=[a for a in todos if a.lower().endswith((".png",".jpg",".jpeg",".webp",".mp4",".mov",".webm"))]
    if validos:
        mais_novo=sorted(validos, key=os.path.getmtime, reverse=True)[0]
        if mais_novo.lower().endswith((".mp4",".mov",".webm")): st.video(mais_novo, autoplay=True, loop=True, muted=True)
        else: st.image(mais_novo, use_container_width=True)

st.title("Nossos Produtos"); st.divider()
if produtos:
    cols=st.columns(3, gap="large")
    for i,p in enumerate(produtos):
        with cols[i%3]:
            with st.container(border=True):
                b64 = img_para_base64(p.get("img",""))
                if b64:
                    st.markdown(f'<img src="data:image/jpeg;base64,{b64}" class="foto-produto-fixa">', unsafe_allow_html=True)
                elif p.get("img"):
                    st.markdown(f'<img src="{p.get("img")}" class="foto-produto-fixa">', unsafe_allow_html=True)
                st.write(f"**{p.get('nome')}**")
                st.write(f"**R$ {float(p.get('preco',0)):.2f}**")
                qtd=st.session_state.carrinho.get(i,0)
                if qtd>0:
                    st.markdown(f'<div class="badge-reserva"><div style="background:#d4edda;color:#155724;padding:6px 12px;border-radius:8px;width:100%;text-align:center">✅ {qtd} no carrinho</div></div>', unsafe_allow_html=True)
                else: st.markdown('<div class="badge-reserva"></div>', unsafe_allow_html=True)
                if st.button("Acrescentar ao carrinho 🛒", key=f"add_{i}", use_container_width=True):
                    st.session_state.carrinho[i]=st.session_state.carrinho.get(i,0)+1; st.rerun()
