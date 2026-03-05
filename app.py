"""
Simulateur Jeanbrun – Streamlit App
Moteur de calcul entièrement en Python (réimplémentation fidèle des formules Excel V9)
"""
import streamlit as st
import pandas as pd
import math
import io

st.set_page_config(page_title="Simulateur Jeanbrun", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
.header-band{background:linear-gradient(135deg,#13415B 0%,#3761AD 100%);color:white;padding:1.2rem 2rem;border-radius:10px;margin-bottom:1.5rem;}
.header-band h1{margin:0;font-size:1.6rem;}.header-band p{margin:.3rem 0 0;opacity:.8;font-size:.9rem;}
.kpi-card{background:#EEF2FB;border-left:4px solid #3761AD;border-radius:8px;padding:.9rem 1.1rem;margin-bottom:.4rem;}
.kpi-card.teal{background:#E5F6F6;border-color:#009FA3;}.kpi-card.orange{background:#FFF3EE;border-color:#EA653D;}
.kpi-card.dark{background:#E8EDF4;border-color:#13415B;}
.kpi-label{font-size:.75rem;color:#555;text-transform:uppercase;letter-spacing:.05em;}
.kpi-value{font-size:1.4rem;font-weight:700;color:#13415B;margin-top:.2rem;}
.kpi-sub{font-size:.75rem;color:#777;margin-top:.1rem;}
.section-header{background:#13415B;color:white;padding:.5rem 1rem;border-radius:6px;font-weight:600;margin:1.2rem 0 .6rem;}
</style>""", unsafe_allow_html=True)

# ── Auth ──
def check_password():
    if st.session_state.get("auth"): return True
    c1,c2,c3 = st.columns([1,1.5,1])
    with c2:
        st.markdown("""<div style="text-align:center;padding:2rem;background:white;border-radius:12px;
        box-shadow:0 4px 24px rgba(19,65,91,.12);margin-top:4rem;">
        <h2 style="color:#13415B;margin-top:0">🏠 Simulateur<br>Dispositif Jeanbrun</h2>
        <p style="color:#555">Outil réservé aux conseillers</p></div>""", unsafe_allow_html=True)
        pwd = st.text_input("", type="password", label_visibility="collapsed", placeholder="Mot de passe")
        if st.button("🔓 Se connecter", use_container_width=True):
            if pwd == st.secrets.get("password","jeanbrun2025"):
                st.session_state.auth = True; st.rerun()
            else: st.error("Mot de passe incorrect")
    return False

if not check_password(): st.stop()

# ── Tables de référence ──
PLAFONDS = {
    "A bis":{"Loyer intermédiaire":19.51,"Loyer social":15.61,"Loyer très social":11.71},
    "A":    {"Loyer intermédiaire":14.49,"Loyer social":11.59,"Loyer très social": 8.69},
    "B1":   {"Loyer intermédiaire":11.68,"Loyer social": 9.34,"Loyer très social": 7.01},
    "B2":   {"Loyer intermédiaire":10.15,"Loyer social": 8.12,"Loyer très social": 6.09},
    "C":    {"Loyer intermédiaire":10.15,"Loyer social": 8.12,"Loyer très social": 6.09},
}
PLAF_AMT = {"Loyer intermédiaire":8000,"Loyer social":10000,"Loyer très social":12000}
TAUX_AMT = {"Loyer intermédiaire":0.035,"Loyer social":0.045,"Loyer très social":0.055}
BAREME = [(0,11600,0.0,0),(11600,29579,0.11,1276),(29579,84577,0.30,6896.01),(84577,181917,0.41,16199.48),(181917,9e9,0.45,23476.16)]
PLAF_AB10=14171; PLAN_AB10=504; PLAF_DEF=10700; CSG_DED=0.068

def ir(rev, parts):
    if rev<=0: return 0.0
    qf=rev/parts; t=0.0
    for inf,sup,taux,_ in BAREME:
        if qf>inf: t=max(0,rev*taux - next(d for a,b,c,d in BAREME if qf<=b)*parts)
    return max(0.0,t)

def ir_correct(rev, parts):
    if rev<=0: return 0.0
    qf=rev/parts; ir_qf=0.0
    for inf,sup,taux,_ in BAREME:
        if qf<=inf: break
        ir_qf += (min(qf,sup)-inf)*taux
    return max(0.0, ir_qf*parts)

def tmi_calc(rev, parts):
    qf=rev/parts
    for inf,sup,taux,_ in BAREME:
        if qf<=sup: return taux
    return 0.45

def abatt10(rev, nd, typ):
    if "Salaires" in typ:
        return max(PLAN_AB10*nd, min(rev*0.1, PLAF_AB10*nd))
    if "Pensions" in typ:
        return max(442*nd, min(rev*0.1, 4321*nd))
    return 0.0

def abatt_ir_pv(n): return 0.0 if n<=5 else min((n-5)*0.06, 1.0)
def abatt_ps_pv(n):
    if n<=5: return 0.0
    if n<=21: return (n-5)*0.0165
    if n==22: return 16*0.0165+0.016
    if n<=30: return 16*0.0165+0.016+(n-22)*0.09
    return 1.0

def surtaxe(pv):
    if pv<=50000: return 0.0
    if pv<=60000: return pv*0.02-(60000-pv)/20
    if pv<=100000: return pv*0.02
    if pv<=110000: return pv*0.03-(110000-pv)/10
    if pv<=150000: return pv*0.03
    if pv<=160000: return pv*0.04-(160000-pv)*3/20
    if pv<=200000: return pv*0.04
    if pv<=210000: return pv*0.05-(210000-pv)/5
    if pv<=250000: return pv*0.05
    if pv<=260000: return pv*0.06-(260000-pv)/4
    return pv*0.06

def amt_table(capital, taux_an, duree_an):
    r = taux_an/12; n = duree_an*12
    mens = capital*r*(1+r)**n/((1+r)**n-1) if r>0 else capital/n
    tab=[]; crd=capital
    for _ in range(duree_an):
        int_a=princ_a=0
        for _ in range(12):
            im=crd*r; pm=mens-im; int_a+=im; princ_a+=pm; crd=max(0,crd-pm)
        tab.append({"int":int_a,"princ":princ_a,"crd":max(0,crd)})
    return mens, tab

# ── Moteur ──
@st.cache_data(show_spinner=False)
def simulate(prix,frais,surf,zone,rdc,balcon,terrasse,apport,ti,ta,duree,fg,tl,ls,il,cp,tr,rev,rfa,parts,nd):
    cout=prix*(1+frais)
    # Surface pondérée
    if rdc=="OUI": sp=surf+min(balcon,16)/2
    else: sp=surf+min(balcon+terrasse,16)/2
    plm2=PLAFONDS.get(zone,PLAFONDS["A"]).get(tl,14.49)
    coeff=math.trunc(min(max(0,0.7+19/sp),1.2)*100)/100 if sp>0 else 1.0
    lmax=plm2*sp*coeff
    lmens=min(ls,lmax); lann=lmens*12
    mempr=cout-apport
    mens,amttab=amt_table(mempr,ti,duree)
    ass_mens=mempr*ta/12; ass_ann=ass_mens*12
    mens_tot=mens+ass_mens
    base_a=prix*0.8; taux_a=TAUX_AMT[tl]; plaf_a=PLAF_AMT[tl]
    amort_an=min(plaf_a,base_a*taux_a)
    ab=abatt10(rev,nd,tr); rn=rev-ab
    
    annees=[]; amt_cum=0.0; stock_def=0.0; csg_prec=0.0
    for an in range(1,26):
        idx=an-1
        lo=lann*(1+il)**idx
        ch=lo*cp
        if idx<len(amttab): int_a=amttab[idx]["int"]; ass_a=ass_ann; crd=amttab[idx]["crd"]; remb=(mens+ass_mens)*12
        else: int_a=ass_a=crd=remb=0.0
        vb=prix*(1+il)**idx
        rfb=lo+rfa; cf=int_a+ass_a+(fg if an==1 else 0); cnf=ch+amort_an
        rfn=rfb-cf-cnf
        # Déduction RG et report
        if rfn>=0: ded_rg=0.0; def_gen=0.0
        elif rfb>=cf: ded_rg=max(rfn,-PLAF_DEF); def_gen=max(0,-rfn-PLAF_DEF)
        else: ded_rg=max(-cnf,-PLAF_DEF); def_gen=(cf-rfb)+max(0,cnf-PLAF_DEF)
        if an==1: stock_def=def_gen
        else: stock_def=stock_def+def_gen-min(stock_def,max(0,rfn))
        def_imp=min(stock_def-def_gen,rfn) if rfn>0 else 0.0
        rfnt=max(0,rfn-def_imp)
        rev_ap=rn+rfnt+ded_rg-csg_prec
        ir_av=ir_correct(rn+rfa,parts); ps_av=max(0,rfa)*0.172; tot_av=ir_av+ps_av
        ir_ap=ir_correct(max(0,rev_ap),parts); ps_ap=rfnt*0.172; tot_ap=ir_ap+ps_ap
        eco=tot_av-tot_ap
        csg_prec=rfnt*CSG_DED
        amt_cum+=amort_an
        # PV
        fac=max(prix*frais,prix*0.075); ftv=prix*0.15 if an>5 else 0
        pr=prix+fac+ftv-amt_cum
        pv0=prix-pr; pv15=vb-pr
        ab_ir=abatt_ir_pv(an); ab_ps=abatt_ps_pv(an)
        pvi0=max(0,pv0*(1-ab_ir)); pps0=max(0,pv0*(1-ab_ps))
        ipv=pvi0*0.19+pps0*0.172+max(0,surtaxe(pvi0))
        enrichissement=vb-crd-max(0,ipv)
        effort=(lo-remb-ch+eco)/12
        annees.append(dict(an=an,lo=lo,ch=ch,int_a=int_a,ass_a=ass_a,amort=amort_an,crd=crd,vb=vb,rfn=rfn,ded_rg=ded_rg,def_gen=def_gen,stock_def=stock_def,def_imp=def_imp,rfnt=rfnt,ir_av=ir_av,ps_av=ps_av,tot_av=tot_av,ir_ap=ir_ap,ps_ap=ps_ap,tot_ap=tot_ap,eco=eco,enrichissement=enrichissement,effort=effort,remb=remb,amt_cum=amt_cum,pv0=pv0,pv15=pv15,ab_ir=ab_ir,ab_ps=ab_ps,pvi0=pvi0,ipv=ipv,pr=pr))

    def hor(n):
        t=annees[:n]
        lm=sum(a["lo"] for a in t)/n/12; gm=sum(a["eco"] for a in t)/n/12
        cm=mens_tot; chm=sum(a["ch"] for a in t)/n/12
        te=lm+gm; ts=cm+chm; ef=te-ts
        return dict(lm=lm,gm=gm,cm=cm,chm=chm,te=te,ts=ts,ef=ef,cap=t[-1]["enrichissement"],gft=sum(a["eco"] for a in t))

    return dict(annees=annees,h9=hor(9),h15=hor(15),h25=hor(25),lmax=lmax,lmens=lmens,sp=sp,coeff=coeff,
                mempr=mempr,mens_tot=mens_tot,amort_an=amort_an,eco1=annees[0]["eco"],
                ir_av1=annees[0]["ir_av"],ir_ap1=annees[0]["ir_ap"],tmi=tmi_calc(rn+rfa,parts),
                rn=rn,ab=ab,amttab=amttab,lann=lann,cout=cout)

# ── Formatage ──
def fe(v,d=0):
    if v is None: return "—"
    try:
        s=f"{abs(float(v)):,.{d}f}".replace(",","  ")
        return ("−" if float(v)<0 else "")+s+" €"
    except: return str(v)
def fp(v,d=1):
    if v is None: return "—"
    try: return f"{float(v)*100:.{d}f} %"
    except: return str(v)
def fn(v,d=0):
    if v is None: return "—"
    try: return f"{float(v):,.{d}f}".replace(",","  ")
    except: return str(v)

# ── Header ──
st.markdown("""<div class="header-band"><h1>🏠 Simulateur — Dispositif Jeanbrun</h1>
<p>Outil de projection fiscale · Réservé aux conseillers · Document non contractuel</p></div>""", unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("## ✏️ Paramètres conseiller")
    st.caption("Modifiez uniquement ces champs")
    st.markdown("### 🏠 Bien immobilier")
    prix     = st.number_input("Prix d'acquisition (€)",50000,5000000,260000,1000,format="%d")
    frais    = st.number_input("Frais de notaire (%)",0.0,15.0,3.0,0.1,format="%.1f")/100
    surf     = st.number_input("Surface habitable (m²)",5.0,500.0,40.0,0.5,format="%.1f")
    zone     = st.selectbox("Zone d'acquisition",["A bis","A","B1","B2","C"],index=1)
    rdc      = st.selectbox("Rez-de-chaussée ?",["NON","OUI"],index=0)
    balcon   = st.number_input("Surface balcon (m²)",0.0,100.0,15.0,0.5,format="%.1f")
    terrasse = st.number_input("Surface terrasse (m²)",0.0,300.0,0.0,0.5,format="%.1f")
    st.markdown("### 💳 Financement")
    apport   = st.number_input("Apport personnel (€)",0,2000000,15000,500,format="%d")
    ti       = st.number_input("Taux d'intérêt annuel (%)",0.0,10.0,3.3,0.05,format="%.2f")/100
    ta       = st.number_input("Taux assurance emprunteur (%)",0.0,3.0,0.35,0.01,format="%.2f")/100
    duree    = st.number_input("Durée du financement (ans)",5,30,25,1)
    fg       = st.number_input("Frais garantie + dossier (€)",0,20000,4000,100,format="%d")
    st.markdown("### 🏘️ Revenus locatifs")
    tl       = st.selectbox("Type de loyer",["Loyer intermédiaire","Loyer social","Loyer très social"])
    ls       = st.number_input("Loyer souhaité (€/mois)",100,5000,750,10,format="%d")
    il       = st.number_input("Indexation loyers (%/an)",0.0,5.0,1.5,0.1,format="%.1f")/100
    cp       = st.number_input("Charges + taxe foncière (% loyers)",0.0,60.0,30.0,1.0,format="%.0f")/100
    st.markdown("### 👤 Situation fiscale")
    tr       = st.selectbox("Type de revenus",["Salaires (abatt. 10%)","Pensions / Retraites (abatt. 10%)","BNC / BIC / autres"])
    rev      = st.number_input("Revenus annuels déclarés (€)",0,2000000,95000,1000,format="%d")
    rfa      = st.number_input("Revenus fonciers autres biens (€/an)",0,500000,5000,500,format="%d")
    parts    = st.number_input("Nombre de parts fiscales",1.0,10.0,2.5,0.5,format="%.1f")
    nd       = st.number_input("Nombre de déclarants",1,2,2,1)
    st.divider()
    go = st.button("🚀 Lancer la simulation",use_container_width=True,type="primary")

if "res" not in st.session_state: st.session_state.res=None
if go:
    with st.spinner("⚙️ Calcul en cours…"):
        st.session_state.res=simulate(prix,frais,surf,zone,rdc,balcon,terrasse,apport,ti,ta,duree,fg,tl,ls,il,cp,tr,rev,rfa,parts,nd)
    st.success("✅ Simulation calculée avec succès !")

res=st.session_state.res
if res is None:
    st.info("👈 Renseignez les paramètres dans la barre latérale puis cliquez sur **Lancer la simulation**.")
    st.stop()

ann=res["annees"]

# ── Onglets ──
t1,t2,t3,t4,t5=st.tabs(["📊 Synthèse Visuelle","📋 Synthèse Simplifiée","📈 Synthèse Détaillée","🏦 Revente & Plus-value","⬇️ Télécharger"])

with t1:
    c1,c2,c3,c4,c5=st.columns(5)
    with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Revenus déclarés</div><div class="kpi-value">{fe(rev)}</div><div class="kpi-sub">{fn(parts,1)} parts</div></div>',unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi-card teal"><div class="kpi-label">Tranche Marginale</div><div class="kpi-value">{fp(res["tmi"])}</div><div class="kpi-sub">avant opération</div></div>',unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Prix d\'acquisition</div><div class="kpi-value">{fe(prix)}</div><div class="kpi-sub">{tl}</div></div>',unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="kpi-card dark"><div class="kpi-label">Loyer mensuel initial</div><div class="kpi-value">{fe(res["lmens"])}</div><div class="kpi-sub">Zone {zone} · {fn(res["sp"],1)} m² pond.</div></div>',unsafe_allow_html=True)
    with c5: st.markdown(f'<div class="kpi-card orange"><div class="kpi-label">Économie fiscale an 1</div><div class="kpi-value">{fe(res["eco1"])}</div><div class="kpi-sub">déficit + Jeanbrun</div></div>',unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📊 Compte en T — Moyennes mensuelles par horizon")

    def render_h(h,label,yrs,bg,bc):
        ef=h["ef"]; col="#EA653D" if ef<0 else "#009FA3"
        return f"""<div style="background:{bg};border-left:4px solid {bc};border-radius:10px;padding:1.2rem;height:100%;">
        <div style="font-weight:700;color:#13415B;font-size:1rem;margin-bottom:.8rem;">{label} — <span style="color:{bc};">{yrs}</span></div>
        <table style="width:100%;border-collapse:collapse;font-size:.87rem;">
        <tr><td style="color:#009FA3;font-weight:600;padding:.25rem .3rem;">✚ CE QUI RENTRE</td><td style="color:#EA653D;font-weight:600;padding:.25rem .3rem;">— CE QUI SORT</td></tr>
        <tr><td style="padding:.2rem .3rem;">Loyers moy. : <b>{fe(h['lm'])}/mois</b></td><td style="padding:.2rem .3rem;">Crédit : <b>{fe(h['cm'])}/mois</b></td></tr>
        <tr><td style="padding:.2rem .3rem;">Gain fiscal moy. : <b>{fe(h['gm'])}/mois</b></td><td style="padding:.2rem .3rem;">Charges : <b>{fe(h['chm'])}/mois</b></td></tr>
        <tr style="border-top:1px solid #ddd;font-weight:600;"><td style="padding:.3rem;">Total : <b>{fe(h['te'])}/mois</b></td><td style="padding:.3rem;">Total : <b>{fe(h['ts'])}/mois</b></td></tr>
        </table>
        <div style="margin-top:.8rem;text-align:center;"><div style="font-size:.78rem;color:#555;">Effort d'investissement mensuel moyen</div>
        <div style="font-size:1.3rem;font-weight:700;color:{col};">{fe(abs(ef))}/mois</div></div>
        <div style="margin-top:.6rem;background:white;border-radius:6px;padding:.6rem;font-size:.82rem;">
        <b>Capital net constitué :</b> {fe(h['cap'])}<br><b>Gain fiscal total :</b> {fe(h['gft'])}</div></div>"""

    c9,c15,c25=st.columns(3)
    with c9: st.markdown(render_h(res["h9"],"🔹 Fin d'engagement","9 ans","#EEF2FB","#3761AD"),unsafe_allow_html=True)
    with c15: st.markdown(render_h(res["h15"],"🔸 Horizon de référence","15 ans","#E5F6F6","#009FA3"),unsafe_allow_html=True)
    with c25: st.markdown(render_h(res["h25"],"⭐ Financement soldé","25 ans","#FFF3EE","#EA653D"),unsafe_allow_html=True)

with t2:
    st.markdown('<div class="section-header">📋 PROJECTION SIMPLIFIÉE — Dispositif Jeanbrun · Document non contractuel</div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        st.markdown("**Situation du foyer**")
        st.dataframe(pd.DataFrame({"Paramètre":["Revenus déclarés","TMI","Mensualité crédit","Apport"],"Valeur":[fe(rev),fp(res["tmi"]),fe(res["mens_tot"]),fe(apport)]}),hide_index=True,use_container_width=True)
    with c2:
        st.markdown("**Opération immobilière**")
        st.dataframe(pd.DataFrame({"Paramètre":["Prix d'acquisition","Surface pondérée","Loyer mensuel initial","Économie fiscale an 1"],"Valeur":[fe(prix),f"{fn(res['sp'],1)} m²",fe(res["lmens"]),fe(res["eco1"])]}),hide_index=True,use_container_width=True)
    for label,hk,n in [("🔹 Horizon 9 ans","h9",9),("🔸 Horizon 15 ans","h15",15),("⭐ Horizon 25 ans","h25",25)]:
        st.markdown(f"### {label}")
        h=res[hk]; ca,cb,cc=st.columns([2,2,1])
        with ca:
            st.markdown("**✚ Ce qui rentre**")
            st.dataframe(pd.DataFrame({"":["Loyer mensuel moyen","Gain fiscal / mois","Total entrées"],"€/mois":[fe(h["lm"]),fe(h["gm"]),fe(h["te"])]}),hide_index=True,use_container_width=True)
        with cb:
            st.markdown("**— Ce qui sort**")
            st.dataframe(pd.DataFrame({"":["Mensualité de crédit","Charges exploitation","Total sorties"],"€/mois":[fe(h["cm"]),fe(h["chm"]),fe(h["ts"])]}),hide_index=True,use_container_width=True)
        with cc:
            ef=h["ef"]; col="#EA653D" if ef<0 else "#009FA3"
            st.markdown(f"""<div style="text-align:center;padding:1rem;background:#F4F6F9;border-radius:8px;">
            <div style="font-size:.78rem;color:#555;">Effort mensuel</div><div style="font-size:1.3rem;font-weight:700;color:{col};">{fe(abs(ef))}</div>
            <hr style="margin:.4rem 0;"><div style="font-size:.78rem;color:#555;">Capital constitué</div>
            <div style="font-weight:600;color:#13415B;">{fe(h['cap'])}</div>
            <div style="font-size:.78rem;color:#555;margin-top:.3rem;">Gain fiscal total</div>
            <div style="font-weight:600;color:#3761AD;">{fe(h['gft'])}</div></div>""",unsafe_allow_html=True)

with t3:
    st.markdown('<div class="section-header">📈 PROJECTION FINANCIÈRE ANNUELLE — Document non contractuel</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1: st.metric("Revenus déclarés",fe(rev)); st.metric("TMI",fp(res["tmi"]))
    with c2: st.metric("Impôt avant (an 1)",fe(res["ir_av1"])); st.metric("Impôt après (an 1)",fe(res["ir_ap1"]))
    with c3: st.metric("Économie fiscale an 1",fe(res["eco1"])); st.metric("Loyer mensuel initial",fe(res["lmens"]))
    st.markdown("---")
    rows=[]
    for a in ann:
        rows.append({"An":a["an"],"Loyers (€)":fe(a["lo"]),"Remb. (€)":fe(a["remb"]),"Charges (€)":fe(a["ch"]),"Amort. JB (€)":fe(a["amort"]),"RF net (€)":fe(a["rfn"]),"Déd. RG (€)":fe(a["ded_rg"]),"Stock déf. (€)":fe(a["stock_def"]),"IR avant (€)":fe(a["ir_av"]),"IR après (€)":fe(a["ir_ap"]),"Éco. fisc. (€)":fe(a["eco"]),"Effort mois (€)":fe(a["effort"]),"Capital net (€)":fe(a["enrichissement"]),"Amt cumulé (€)":fe(a["amt_cum"])})
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True,height=580)

with t4:
    st.markdown('<div class="section-header">🏦 SIMULATION DE REVENTE — Plus-value et enrichissement net · Document non contractuel</div>',unsafe_allow_html=True)
    cols=st.columns(3)
    for col,(anr,label) in zip(cols,[(9,"🔹 Revente à 9 ans"),(15,"🔸 Revente à 15 ans"),(25,"⭐ Revente à 25 ans")]):
        a=ann[anr-1]
        with col:
            st.markdown(f"#### {label}")
            pv0=prix; pv15=prix*(1.015**anr); pr=a["pr"]
            pb0=pv0-pr; pb15=pv15-pr
            ab_ir=a["ab_ir"]; ab_ps=a["ab_ps"]
            pi0=max(0,pb0*(1-ab_ir)); pp0=max(0,pb0*(1-ab_ps))
            pi15=max(0,pb15*(1-ab_ir)); pp15=max(0,pb15*(1-ab_ps))
            ip0=pi0*0.19+pp0*0.172+max(0,surtaxe(pi0))
            ip15=pi15*0.19+pp15*0.172+max(0,surtaxe(pi15))
            cn0=pv0-a["crd"]-max(0,ip0); cn15=pv15-a["crd"]-max(0,ip15)
            st.dataframe(pd.DataFrame({"":["Prix de vente (0%)","Prix de vente (+1,5%/an)","—","Prix d'acquisition","+ Forfait frais acq. (7,5%)","+ Forfait travaux (15%)","− Amt réintégrés","= Prix de revient","—","PV brute (0%)","PV brute (+1,5%)","—",f"Abatt. IR ({fp(ab_ir)})",f"Abatt. PS ({fp(ab_ps)})","PV imposable IR (0%)","PV imposable IR (+1,5%)","—","Impôt PV total (0%)","Impôt PV total (+1,5%)","—","Capital net (0%)","Capital net (+1,5%)"],"Valeur":[fe(pv0),fe(pv15),"",fe(prix),fe(max(prix*frais,prix*0.075)),fe(prix*0.15 if anr>5 else 0),fe(a["amt_cum"]),fe(pr),"",fe(pb0),fe(pb15),"",fp(ab_ir),fp(ab_ps),fe(pi0),fe(pi15),"",fe(max(0,ip0)),fe(max(0,ip15)),"",fe(cn0),fe(cn15)]}),hide_index=True,use_container_width=True)

with t5:
    st.markdown("### ⬇️ Export des résultats (Excel)")
    buf=io.BytesIO()
    with pd.ExcelWriter(buf,engine="openpyxl") as writer:
        pd.DataFrame({"Paramètre":["Prix d'acquisition","Frais notaire","Surface","Zone","Apport","Taux intérêt","Taux assurance","Durée","Type loyer","Loyer souhaité","Revenus","Parts"],"Valeur":[fe(prix),fp(frais),f"{surf} m²",zone,fe(apport),fp(ti),fp(ta),f"{duree} ans",tl,fe(ls),fe(rev),fn(parts,1)]}).to_excel(writer,sheet_name="Hypothèses",index=False)
        pd.DataFrame([{"Année":a["an"],"Loyers":round(a["lo"],2),"Charges":round(a["ch"],2),"Intérêts":round(a["int_a"],2),"Amort.JB":round(a["amort"],2),"RF net":round(a["rfn"],2),"IR avant":round(a["ir_av"],2),"IR après":round(a["ir_ap"],2),"Éco.fiscale":round(a["eco"],2),"Effort/mois":round(a["effort"],2),"Capital net":round(a["enrichissement"],2)} for a in ann]).to_excel(writer,sheet_name="Projection annuelle",index=False)
        pd.DataFrame([{"Horizon":lb,"Loyers moy./mois":round(res[hk]["lm"],2),"Gain fiscal/mois":round(res[hk]["gm"],2),"Crédit/mois":round(res[hk]["cm"],2),"Charges/mois":round(res[hk]["chm"],2),"Effort mensuel":round(res[hk]["ef"],2),"Capital net":round(res[hk]["cap"],2),"Gain fiscal total":round(res[hk]["gft"],2)} for lb,hk in [("9 ans","h9"),("15 ans","h15"),("25 ans","h25")]]).to_excel(writer,sheet_name="Synthèse",index=False)
    buf.seek(0)
    st.download_button("📥 Télécharger la simulation (Excel)",data=buf.read(),file_name=f"Simulation_Jeanbrun_{prix//1000}k_Zone{zone}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
    st.info("**Document non contractuel** — Moteur de calcul Python · Réimplémentation des formules Excel V9")
