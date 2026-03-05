"""
Simulateur Jeanbrun V9 — Streamlit App
Moteur de calcul Python 100% conforme aux formules Excel V9
Charte graphique Médicis Immobilier Neuf 2024
"""
import streamlit as st
import pandas as pd
import math
import io

st.set_page_config(
    page_title="Simulateur Jeanbrun — médicis",
    page_icon="🏠", layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════
# CSS GLOBAL — CHARTE MÉDICIS 2024
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

:root {
  --blue:    #3761AD;
  --dark:    #14415C;
  --orange:  #EA653D;
  --salmon:  #F57E63;
  --teal:    #009FA3;
  --lime:    #E2DE3E;
  --white:   #FFFFFF;
  --lb:      #EEF2FB;
  --lt:      #E4F5F5;
  --lo:      #FEF0EC;
  --ll:      #F9F8D6;
  --gray:    #F4F6F9;
}

html, body, [class*="css"], .stApp, button, input, select, textarea {
  font-family: 'Poppins', sans-serif !important;
}

[data-testid="stSidebar"] { background: var(--dark) !important; }
[data-testid="stSidebar"] * { color: #ffffff !important; font-family: 'Poppins', sans-serif !important; }
[data-testid="stSidebar"] input, [data-testid="stSidebar"] select {
  background: rgba(255,255,255,.12) !important; color:#fff !important;
  border:1px solid rgba(255,255,255,.25) !important; border-radius:6px !important;
}
[data-testid="stSidebar"] .stButton button {
  background: var(--orange) !important; color:white !important;
  border:none !important; font-weight:700 !important; font-family:'Poppins',sans-serif !important;
}
[data-testid="stSidebar"] hr { border-color:rgba(255,255,255,.2) !important; }

.hdr {
  background:linear-gradient(135deg,var(--dark) 0%,var(--blue) 100%);
  color:white; padding:1.2rem 2rem; border-radius:12px;
  margin-bottom:.8rem; display:flex; align-items:center; gap:1.5rem;
}
.hdr-logo { font-weight:800; font-size:1.7rem; color:white; letter-spacing:-.02em; }
.hdr-logo span { color:var(--orange); }
.hdr-right { margin-left:auto; text-align:right; }
.hdr-title { font-size:1.1rem; font-weight:600; }
.hdr-sub { font-size:.75rem; opacity:.7; }
.accent-bar {
  height:4px;
  background:linear-gradient(90deg,var(--orange) 0%,var(--salmon) 40%,var(--teal) 80%,var(--lime) 100%);
  border-radius:2px; margin-bottom:1.1rem;
}

.sec {
  background:var(--dark); color:white; padding:.48rem 1rem; border-radius:7px;
  font-weight:600; margin:1.2rem 0 .6rem; font-size:.9rem; letter-spacing:.02em;
}
.sec.blue   { background:var(--blue); }
.sec.teal   { background:var(--teal); }
.sec.orange { background:var(--orange); }
.sec.salmon { background:var(--salmon); }
.sec.lime   { background:#9a9b1a; }

.kpi { background:var(--lb); border-left:4px solid var(--blue); border-radius:9px; padding:.9rem 1.1rem; }
.kpi.t { background:var(--lt); border-color:var(--teal); }
.kpi.o { background:var(--lo); border-color:var(--orange); }
.kpi.d { background:#E3EAF0;   border-color:var(--dark); }
.kpi.l { background:var(--ll); border-color:#9a9b1a; }
.kpi.s { background:#FEF5F3;   border-color:var(--salmon); }
.kpi-lbl { font-size:.67rem; color:#666; text-transform:uppercase; letter-spacing:.07em; font-weight:600; }
.kpi-val { font-size:1.3rem; font-weight:700; color:var(--dark); margin-top:.18rem; }
.kpi-sub { font-size:.7rem; color:#888; margin-top:.08rem; }

.cnt-card { border-radius:10px; padding:1.1rem 1.15rem; border-top:5px solid var(--blue); }
.cnt-tbl { width:100%; border-collapse:collapse; font-size:.84rem; }
.cnt-tbl td { padding:.23rem .3rem; }
.cnt-tbl .hd { color:#888; font-size:.68rem; font-weight:700; text-transform:uppercase; padding-bottom:.3rem; }
.cnt-tbl .sep { border-top:1.5px solid #ddd; font-weight:700; padding-top:.35rem; }
.cnt-bilan { background:white; border-radius:6px; padding:.6rem .7rem; font-size:.79rem; margin-top:.5rem; line-height:1.75; }

.ped { border-radius:10px; padding:1.1rem 1.2rem; height:100%; }
.ped-icon { font-size:1.55rem; margin-bottom:.4rem; }
.ped-title { font-weight:700; margin-bottom:.35rem; font-size:.93rem; }
.ped-text { font-size:.82rem; line-height:1.55; }

.footer {
  margin-top:2rem; padding:.7rem 0 .3rem;
  border-top:2px solid var(--orange);
  font-size:.7rem; color:#999; text-align:center; font-style:italic;
}
.footer b { color:var(--blue); }

.login-card {
  background:white; border-radius:16px;
  box-shadow:0 8px 40px rgba(20,65,92,.15);
  padding:2.5rem 2.2rem; text-align:center; margin-top:5rem;
}

@media print {
  [data-testid="stSidebar"],[data-testid="stToolbar"],
  .stTabs [data-baseweb="tab-list"],button,.stDownloadButton,
  [data-testid="stDecoration"] { display:none !important; }
  .stApp { background:white !important; }
  .main .block-container { padding:0 !important; max-width:100% !important; }
  .hdr,.sec,.kpi,.cnt-card,.ped { -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  @page { size:A4 landscape; margin:1.2cm; }
}
</style>
""", unsafe_allow_html=True)

# ═══ AUTH ═══
def check_password():
    if st.session_state.get("auth"): return True
    _, c, _ = st.columns([1, 1.2, 1])
    with c:
        st.markdown("""<div class="login-card">
        <div style="font-family:Poppins,sans-serif;font-weight:800;font-size:2rem;color:#3761AD;letter-spacing:-.02em;">m<span style="color:#EA653D;">é</span>dicis</div>
        <div style="font-size:.65rem;color:#aaa;letter-spacing:.12em;text-transform:uppercase;margin-bottom:1rem;">IMMOBILIER NEUF</div>
        <div style="width:40px;height:4px;background:linear-gradient(90deg,#EA653D,#009FA3);border-radius:2px;margin:0 auto .8rem;"></div>
        <h3 style="color:#14415C;margin:.5rem 0 .3rem;">Simulateur Jeanbrun</h3>
        <p style="color:#888;font-size:.85rem;margin-bottom:1.5rem;">Outil réservé aux conseillers</p>
        </div>""", unsafe_allow_html=True)
        pwd = st.text_input("", type="password", label_visibility="collapsed", placeholder="🔑  Mot de passe conseiller")
        if st.button("Se connecter →", use_container_width=True, type="primary"):
            if pwd == st.secrets.get("password", "jeanbrun2025"):
                st.session_state.auth = True; st.rerun()
            else:
                st.error("Mot de passe incorrect")
    return False

if not check_password(): st.stop()

# ═══ CONSTANTES ═══
PLAFOND_QF = 1759.0; PLAFOND_DEF_RG = 10700.0
CSG_DED = 0.068; TAUX_PS = 0.172; TAUX_IR_PV = 0.19; TAUX_PS_PV = 0.172
BAREME = [(0,11600,.0),(11600,29579,.11),(29579,84577,.30),(84577,181917,.41),(181917,9e9,.45)]
PLAFONDS_LOYERS = {
    "A bis": {"Loyer intermédiaire":19.51,"Loyer social":15.61,"Loyer très social":11.71},
    "A":     {"Loyer intermédiaire":14.49,"Loyer social":11.59,"Loyer très social": 8.69},
    "B1":    {"Loyer intermédiaire":11.68,"Loyer social": 9.34,"Loyer très social": 7.01},
    "B2":    {"Loyer intermédiaire":10.15,"Loyer social": 8.12,"Loyer très social": 6.09},
    "C":     {"Loyer intermédiaire":10.15,"Loyer social": 8.12,"Loyer très social": 6.09},
}
PLAF_AMT = {"Loyer intermédiaire":8000,"Loyer social":10000,"Loyer très social":12000}
TAUX_AMT = {"Loyer intermédiaire":.035,"Loyer social":.045,"Loyer très social":.055}

# ═══ FONCTIONS FISCALES ═══
def ir_brut(qf):
    t=0.0
    for inf,sup,tx in BAREME:
        if qf<=inf: break
        t+=(min(qf,sup)-inf)*tx
    return t

def calcul_ir(rev, parts):
    if rev<=0: return 0.0
    it=ir_brut(rev/parts)*parts
    pr=2.0 if parts>=2.0 else 1.0
    ir=ir_brut(rev/pr)*pr
    ds=max(0.,(parts-pr)*2)
    return max(0., max(it, ir-ds*PLAFOND_QF))

def get_tmi(rev, parts):
    qf=rev/parts if parts>0 else 0
    for inf,sup,tx in BAREME:
        if qf<=sup: return tx
    return .45

def abatt10(rev, nd, typ):
    if "Salaires" in typ: return max(504.*nd, min(rev*.10, 14171.*nd))
    if "Pensions" in typ: return max(442.*nd, min(rev*.10, 4321.*nd))
    return 0.0

def abatt_ir(n):
    if n<6: return 0.
    if n<22: return (n-5)*.06
    return 1.

def abatt_ps(n):
    if n<6: return 0.
    if n<22: return (n-5)*.0165
    if n==22: return 16*.0165+.016
    if n<30: return 16*.0165+.016+(n-22)*.09
    return 1.

def surtaxe(pv):
    if pv<=50000: return 0.
    if pv<=60000:  return pv*.02-(60000-pv)*.05
    if pv<=100000: return pv*.02
    if pv<=110000: return pv*.03-(110000-pv)*.10
    if pv<=150000: return pv*.03
    if pv<=160000: return pv*.04-(160000-pv)*.15
    if pv<=200000: return pv*.04
    if pv<=210000: return pv*.05-(210000-pv)*.20
    if pv<=250000: return pv*.05
    if pv<=260000: return pv*.06-(260000-pv)*.25
    return pv*.06

def amort_tab(capital, taux_an, duree_an):
    r=taux_an/12; n=duree_an*12
    mens=capital*r*(1+r)**n/((1+r)**n-1) if r>0 else capital/n
    rows_m=[]; crd=capital
    for m in range(1,n+1):
        im=crd*r; pm=mens-im
        rows_m.append({"mois":m,"im":im,"pm":pm,"crd":max(0.,crd-pm)})
        crd=max(0.,crd-pm)
    tab=[]
    for an in range(duree_an):
        b=rows_m[an*12:(an+1)*12]
        tab.append({"int":sum(x["im"] for x in b),"princ":sum(x["pm"] for x in b),"crd":max(0.,b[-1]["crd"])})
    return mens, tab, rows_m


# ═══ MOTEUR PRINCIPAL ═══
@st.cache_data(show_spinner=False)
def run(prix, frais_pct, surf, zone, rdc, balcon, terrasse,
        apport, ti, ta, duree, fg,
        type_loyer, ls, il, cp,
        type_rev, rev, rfa, parts, nd):

    cout = prix*(1+frais_pct)
    sp = surf + min(balcon, 16.)/2 if rdc=="OUI" else surf+min(balcon+terrasse,16.)/2
    coeff = math.trunc(min(.7+19./sp,1.2)*100)/100 if sp>0 else 1.2
    plm2  = PLAFONDS_LOYERS.get(zone,PLAFONDS_LOYERS["A"]).get(type_loyer,14.49)
    lmax  = plm2*sp*coeff
    lmens = min(ls, lmax)
    lann0 = lmens*12

    mempr = cout-apport
    mens, amttab, rows_m = amort_tab(mempr, ti, duree)
    ass_m = mempr*ta/12; ass_a = ass_m*12; mens_tot = mens+ass_m

    base_a   = prix*.80
    amort_an = min(PLAF_AMT[type_loyer], base_a*TAUX_AMT[type_loyer])

    ab   = abatt10(rev, nd, type_rev)
    rn   = rev-ab
    tmi_v= get_tmi(rn+rfa, parts)

    annees=[]; stock_def=0.; csg_p=0.
    for an in range(1,26):
        i=an-1
        lo = lann0*(1+il)**i; ch = lo*cp
        if i<len(amttab):
            int_a=amttab[i]["int"]; crd=amttab[i]["crd"]; remb=(mens+ass_m)*12
        else:
            int_a=crd=remb=0.
        ass_a2 = ass_a if i<len(amttab) else 0.

        rf_b  = lo+rfa
        ch_f  = int_a+ass_a2+(fg if an==1 else 0.)
        ch_nf = ch+amort_an
        rfn   = rf_b-ch_f-ch_nf

        if rfn>=0:
            ded=0.; def_g=0.
        elif rf_b>=ch_f:
            ded=max(rfn,-PLAFOND_DEF_RG); def_g=max(0.,-rfn-PLAFOND_DEF_RG)
        else:
            ded=max(-ch_nf,-PLAFOND_DEF_RG); def_g=(ch_f-rf_b)+max(0.,ch_nf-PLAFOND_DEF_RG)

        prev_imp = annees[-1]["def_imp"] if an>1 else 0.
        stock_def = stock_def+def_g-prev_imp
        def_imp = min(stock_def-def_g, rfn) if rfn>0 else 0.
        rfnt    = max(0., rfn-def_imp)
        rev_ap  = rn+rfnt+ded-csg_p

        ir_av=calcul_ir(rn+rfa, parts); ps_av=max(0.,rfa)*TAUX_PS; tot_av=ir_av+ps_av
        ir_ap=calcul_ir(max(0.,rev_ap), parts); ps_ap=rfnt*TAUX_PS; tot_ap=ir_ap+ps_ap
        eco=tot_av-tot_ap
        csg_p=rfnt*CSG_DED

        amt_cum=amort_an*an
        vb15=prix*(1.015)**an
        fac=max(prix*frais_pct, prix*.075); ftv=prix*.15 if an>5 else 0.
        pr=prix+fac+ftv-amt_cum

        pv0=prix-pr; pv15=vb15-pr
        ai=abatt_ir(an); ap=abatt_ps(an)
        pvi0=max(0.,pv0*(1-ai)); pps0=max(0.,pv0*(1-ap))
        pvi15=max(0.,pv15*(1-ai)); pps15=max(0.,pv15*(1-ap))
        ipv0 =pvi0*TAUX_IR_PV+pps0*TAUX_PS_PV+max(0.,surtaxe(pvi0))
        ipv15=pvi15*TAUX_IR_PV+pps15*TAUX_PS_PV+max(0.,surtaxe(pvi15))
        cap0 =prix-crd-max(0.,ipv0)
        cap15=vb15-crd-max(0.,ipv15)
        effort=(lo-remb-ch+eco)/12

        annees.append(dict(
            an=an,lo=lo,ch=ch,int_a=int_a,ass_a=ass_a2,amort=amort_an,
            crd=crd,vb15=vb15,rf_b=rf_b,ch_f=ch_f,ch_nf=ch_nf,rfn=rfn,
            ded=ded,def_g=def_g,stock_def=stock_def,def_imp=def_imp,rfnt=rfnt,
            rev_ap=rev_ap,ir_av=ir_av,ps_av=ps_av,tot_av=tot_av,
            ir_ap=ir_ap,ps_ap=ps_ap,tot_ap=tot_ap,eco=eco,
            cap0=cap0,cap15=cap15,effort=effort,remb=remb,
            amt_cum=amt_cum,pr=pr,pv0=pv0,pv15=pv15,
            ai=ai,ap=ap,ipv0=ipv0,ipv15=ipv15,fac=fac,ftv=ftv,
        ))

    def hor(n):
        t=annees[:n]
        lm=sum(a["lo"] for a in t)/n/12; gm=sum(a["eco"] for a in t)/n/12
        cm=mens_tot; chm=sum(a["ch"] for a in t)/n/12; gft=sum(a["eco"] for a in t)
        esj=[]
        for a in t:
            rfn_sj=a["rf_b"]-a["ch_f"]-a["ch"]
            ded_sj=max(rfn_sj,-PLAFOND_DEF_RG) if rfn_sj<0 else 0.
            rfnt_sj=max(0.,rfn_sj)
            esj.append(a["tot_av"]-(calcul_ir(max(0.,rn+rfnt_sj+ded_sj),parts)+rfnt_sj*TAUX_PS))
        dd=sum(esj); dj=gft-dd
        return dict(lm=lm,gm=gm,cm=cm,chm=chm,te=lm+gm,ts=cm+chm,ef=(lm+gm)-(cm+chm),
                    cap0=t[-1]["cap0"],cap15=t[-1]["cap15"],gft=gft,dont_d=dd,dont_j=dj)

    h9,h15,h25=hor(9),hor(15),hor(25)
    return dict(annees=annees,h9=h9,h15=h15,h25=h25,
                lmax=lmax,lmens=lmens,sp=sp,coeff=coeff,
                mempr=mempr,mens_tot=mens_tot,amort_an=amort_an,base_a=base_a,
                eco1=annees[0]["eco"],ir_av1=annees[0]["ir_av"],ir_ap1=annees[0]["ir_ap"],
                tmi_av=tmi_v,rn=rn,ab=ab,lann0=lann0,cout=cout,
                amttab=amttab,rows_m=rows_m)


# ═══ FORMAT ═══
def fe(v,d=0):
    if v is None: return "—"
    try:
        s=f"{abs(float(v)):,.{d}f}".replace(",","\u202f")
        return ("−\u202f" if float(v)<0 else "")+s+"\u202f€"
    except: return str(v)
def fp(v,d=1):
    try: return f"{float(v)*100:.{d}f}\u202f%"
    except: return "—"
def fn(v,d=1):
    try: return f"{float(v):,.{d}f}".replace(",","\u202f")
    except: return "—"

# ═══ SIDEBAR ═══
with st.sidebar:
    st.markdown("""<div style="text-align:center;padding:.5rem 0 .8rem;">
      <div style="font-family:Poppins,sans-serif;font-weight:800;font-size:1.5rem;color:white;letter-spacing:-.02em;">m<span style="color:#EA653D;">é</span>dicis</div>
      <div style="font-size:.6rem;letter-spacing:.12em;opacity:.6;color:white;margin-top:.1rem;">IMMOBILIER NEUF</div>
      <div style="height:3px;background:linear-gradient(90deg,#EA653D,#009FA3);border-radius:2px;margin:.5rem 0;"></div>
    </div>""", unsafe_allow_html=True)
    st.markdown("### ✏️ Hypothèses")
    st.markdown("#### 🏠 Bien immobilier")
    prix      = st.number_input("Prix d'acquisition (€)", 50_000, 5_000_000, 260_000, 1_000, format="%d")
    frais_pct = st.number_input("Frais d'acquisition (%)", 0.0, 15.0, 3.0, 0.1, format="%.1f") / 100
    surf      = st.number_input("Surface habitable (m²)", 5.0, 500.0, 40.0, 0.5, format="%.1f")
    zone      = st.selectbox("Zone", ["A bis","A","B1","B2","C"], index=1)
    rdc       = st.selectbox("Rez-de-chaussée ?", ["NON","OUI"])
    balcon    = st.number_input("Surface balcon (m²)", 0.0, 200.0, 15.0, 0.5, format="%.1f")
    terrasse  = st.number_input("Surface terrasse (m²)", 0.0, 300.0, 0.0, 0.5, format="%.1f")
    st.markdown("#### 💳 Financement")
    apport  = st.number_input("Apport (€)", 0, 2_000_000, 15_000, 500, format="%d")
    ti      = st.number_input("Taux intérêt (%)", 0.0, 10.0, 3.3, 0.05, format="%.2f") / 100
    ta      = st.number_input("Taux assurance (%)", 0.0, 3.0, 0.35, 0.01, format="%.2f") / 100
    duree   = st.number_input("Durée (ans)", 5, 30, 25, 1)
    fg      = st.number_input("Frais garantie + dossier (€)", 0, 20_000, 4_000, 100, format="%d")
    st.markdown("#### 🏘️ Revenus locatifs")
    type_loyer = st.selectbox("Type de loyer", ["Loyer intermédiaire","Loyer social","Loyer très social"])
    ls         = st.number_input("Loyer souhaité (€/mois)", 100, 5_000, 750, 10, format="%d")
    il         = st.number_input("Indexation loyers (%/an)", 0.0, 5.0, 1.5, 0.1, format="%.1f") / 100
    cp         = st.number_input("Charges + TF (% loyers)", 0.0, 60.0, 30.0, 1.0, format="%.0f") / 100
    st.markdown("#### 👤 Situation fiscale")
    type_rev = st.selectbox("Type de revenus", ["Salaires (abatt. 10%)","Pensions / Retraites (abatt. 10%)","BNC / BIC / autres"])
    rev      = st.number_input("Revenus déclarés (€/an)", 0, 2_000_000, 95_000, 1_000, format="%d")
    rfa      = st.number_input("RF autres biens (€/an)", 0, 500_000, 5_000, 500, format="%d")
    parts    = st.number_input("Parts fiscales", 1.0, 10.0, 2.5, 0.5, format="%.1f")
    nd       = st.number_input("Nb déclarants", 1, 2, 2, 1)
    st.divider()
    go = st.button("🚀 Lancer la simulation", use_container_width=True, type="primary")

if "res" not in st.session_state: st.session_state.res = None
if go:
    with st.spinner("⚙️ Calcul en cours…"):
        st.session_state.res = run(prix,frais_pct,surf,zone,rdc,balcon,terrasse,
                                    apport,ti,ta,duree,fg,type_loyer,ls,il,cp,
                                    type_rev,rev,rfa,parts,nd)

res = st.session_state.res

st.markdown(f"""<div class="hdr">
  <div>
    <div class="hdr-logo">m<span>é</span>dicis <span style="font-size:.75rem;font-weight:400;opacity:.65;letter-spacing:.09em;">IMMOBILIER NEUF</span></div>
    <div class="hdr-sub">Outil réservé aux conseillers · Document non contractuel</div>
  </div>
  <div class="hdr-right">
    <div class="hdr-title">Simulateur — Dispositif Jeanbrun</div>
    <div class="hdr-sub">Barème IR 2026 · Déficit foncier art. 156-I-3 CGI · Amortissement art. 2 quindecies B</div>
  </div>
</div><div class="accent-bar"></div>""", unsafe_allow_html=True)

if res is None:
    st.info("👈 Renseignez les paramètres dans la barre latérale puis cliquez sur **Lancer la simulation**.")
    st.stop()

ann = res["annees"]


# ═══ ONGLETS ═══
t1,t2,t3,t4,t5,t6,t7,t8,t9,t10 = st.tabs([
    "👁️ Synthèse Visuelle","📋 Synthèse Simplifiée","📈 Synthèse Détaillée",
    "🏦 Revente & Plus-value","⚙️ Moteur","📐 Règles fiscales",
    "🏘️ Plafonds loyers","📊 Barème fiscal","💰 Tableau d'amortissement","🖨️ Imprimer",
])

# ─── T1 SYNTHÈSE VISUELLE ───
with t1:
    kols = st.columns(6)
    kdata = [
        ("Revenus déclarés",      fe(rev),            f"{fn(parts,1)} parts",""),
        ("Tranche Marginale",     fp(res["tmi_av"]),  "avant opération","t"),
        ("Prix d'acquisition",    fe(prix),           type_loyer,""),
        ("Loyer initial retenu",  fe(res["lmens"]),   f"Zone {zone} · {fn(res['sp'],1)} m² pond.","d"),
        ("Économie fiscale an 1", fe(res["eco1"]),    "déficit + Jeanbrun","o"),
        ("Amortissement annuel",  fe(res["amort_an"]),f"Base {fe(res['base_a'])} · {fp(TAUX_AMT[type_loyer])}","l"),
    ]
    for col,(lbl,val,sub,cls) in zip(kols,kdata):
        with col:
            st.markdown(f'<div class="kpi {cls}"><div class="kpi-lbl">{lbl}</div><div class="kpi-val">{val}</div><div class="kpi-sub">{sub}</div></div>',unsafe_allow_html=True)

    st.markdown('<div class="sec">📊 COMPTE EN T — Moyennes mensuelles calculées sur chaque horizon</div>',unsafe_allow_html=True)

    def cnt(h,label,yrs,bg,bc,icon):
        ef=h["ef"]; ec="#EA653D" if ef<0 else "#009FA3"; le="Reste à charge" if ef<0 else "Cashflow positif"
        return f"""<div class="cnt-card" style="background:{bg};border-top-color:{bc};">
          <div style="font-weight:700;color:#14415C;font-size:.9rem;margin-bottom:.75rem;">{icon} {label} — <span style="color:{bc};">{yrs}</span></div>
          <table class="cnt-tbl">
            <tr><td class="hd" style="color:#009FA3;">✚ CE QUI RENTRE</td><td class="hd" style="color:#EA653D;">− CE QUI SORT</td></tr>
            <tr><td>Loyers moy. <b>{fe(h["lm"])}</b></td><td>Crédit <b>{fe(h["cm"])}</b></td></tr>
            <tr><td>Gain fiscal moy. <b>{fe(h["gm"])}</b></td><td>Charges <b>{fe(h["chm"])}</b></td></tr>
            <tr class="sep"><td>Total <b>{fe(h["te"])}</b></td><td>Total <b>{fe(h["ts"])}</b></td></tr>
          </table>
          <div style="background:white;border-radius:7px;margin-top:.55rem;padding:.5rem .6rem;text-align:center;">
            <div style="font-size:.66rem;color:#888;text-transform:uppercase;letter-spacing:.06em;">{le} / mois</div>
            <div style="font-size:1.3rem;font-weight:800;color:{ec};">{fe(abs(ef))}/mois</div>
          </div>
          <div class="cnt-bilan">
            <b>Capital net (0%)</b> : {fe(h["cap0"])} · <b>(+1,5%)</b> : {fe(h["cap15"])}<br>
            <b>Gain fiscal total</b> : {fe(h["gft"])}<br>
            <span style="color:#777;"><em>dont déficit naturel</em> : {fe(h["dont_d"])} · <em>dont Jeanbrun</em> : {fe(h["dont_j"])}</span>
          </div>
        </div>"""

    c9,c15,c25=st.columns(3)
    with c9:  st.markdown(cnt(res["h9"],"Fin d'engagement","9 ans","#EEF2FB","#3761AD","🔹"),unsafe_allow_html=True)
    with c15: st.markdown(cnt(res["h15"],"Horizon de référence","15 ans","#E4F5F5","#009FA3","🔸"),unsafe_allow_html=True)
    with c25: st.markdown(cnt(res["h25"],"Financement soldé","25 ans","#FEF0EC","#EA653D","⭐"),unsafe_allow_html=True)

    st.markdown('<div class="sec teal">📈 Capital net constitué par année de détention — 0% et +1,5%/an de revalorisation</div>',unsafe_allow_html=True)
    try:
        import plotly.graph_objects as gof
        xs=[a["an"] for a in ann]; y0=[a["cap0"] for a in ann]; y15=[a["cap15"] for a in ann]
        fig=gof.Figure()
        fig.add_trace(gof.Scatter(x=xs,y=y0,mode="lines+markers",name="0% (prix stable)",line=dict(color="#3761AD",width=2.5),marker=dict(size=6)))
        fig.add_trace(gof.Scatter(x=xs,y=y15,mode="lines+markers",name="+1,5%/an",line=dict(color="#009FA3",width=2.5),marker=dict(size=6)))
        for vx,vl,vc in [(9,"9 ans","#3761AD"),(15,"15 ans","#009FA3"),(25,"25 ans","#EA653D")]:
            fig.add_vline(x=vx,line_dash="dot",line_color=vc,opacity=.6,annotation_text=vl,annotation_position="top",annotation_font=dict(color=vc,size=11))
        fig.add_hline(y=0,line_dash="dash",line_color="#ddd",opacity=.5)
        fig.update_layout(height=290,margin=dict(l=10,r=10,t=15,b=10),
            legend=dict(orientation="h",y=-.25),yaxis=dict(tickformat=",.0f"),
            plot_bgcolor="white",paper_bgcolor="white",
            font=dict(family="Poppins,sans-serif",size=11),
            xaxis=dict(tickmode="linear",tick0=1,dtick=2,gridcolor="#f0f0f0"),yaxis_gridcolor="#f0f0f0")
        st.plotly_chart(fig,use_container_width=True)
    except ImportError:
        df_g=pd.DataFrame({"0%(€)":[round(a["cap0"],0) for a in ann],"+1,5%(€)":[round(a["cap15"],0) for a in ann]},index=[a["an"] for a in ann])
        df_g.index.name="Année"; st.line_chart(df_g)

    st.markdown('<div class="sec blue">💡 COMPRENDRE VOTRE SIMULATION</div>',unsafe_allow_html=True)
    p1,p2,p3=st.columns(3)
    with p1: st.markdown("""<div class="ped" style="background:#EAF6EE;"><div class="ped-icon">💶</div><div class="ped-title" style="color:#009FA3;">Le côté vert (+)</div><div class="ped-text">Ce que vous <b>percevez</b> : loyers encaissés + économie d'impôt grâce au dispositif Jeanbrun. Ces flux viennent réduire votre effort mensuel.</div></div>""",unsafe_allow_html=True)
    with p2: st.markdown("""<div class="ped" style="background:#FEF0EC;"><div class="ped-icon">🏦</div><div class="ped-title" style="color:#EA653D;">Le côté rouge (−)</div><div class="ped-text">Ce que vous <b>déboursez</b> : mensualité de crédit + charges d'exploitation (gestion, GLI, taxe foncière, assurance PNO, provisions travaux).</div></div>""",unsafe_allow_html=True)
    with p3: st.markdown("""<div class="ped" style="background:#EEF2FB;"><div class="ped-icon">📊</div><div class="ped-title" style="color:#3761AD;">Le gain fiscal — 2 composantes</div><div class="ped-text"><b>Déficit naturel</b> (intérêts, acquis même sans Jeanbrun) + <b>avantage Jeanbrun</b> (amortissement du bien). Les deux s'additionnent.</div></div>""",unsafe_allow_html=True)
    st.markdown('<div class="footer"><b>www.medicis-immobilier-neuf.fr</b> · Simulation personnalisée non contractuelle · Hypothèses d\'indexation et fiscalité constantes</div>',unsafe_allow_html=True)


# ─── T2 SYNTHÈSE SIMPLIFIÉE ───
with t2:
    st.markdown('<div class="sec">PROJECTION SIMPLIFIÉE — Compte en T · Moyennes mensuelles</div>',unsafe_allow_html=True)
    ca,cb=st.columns(2)
    with ca:
        st.markdown('<div class="sec blue" style="font-size:.82rem;">SITUATION DU FOYER</div>',unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({"Paramètre":["Revenus déclarés","Parts fiscales","TMI","Mensualité crédit","Économie fiscale an 1","Apport"],
            "Valeur":[fe(rev),fn(parts,1),fp(res["tmi_av"]),fe(res["mens_tot"]),fe(res["eco1"]),fe(apport)]}),hide_index=True,use_container_width=True)
    with cb:
        st.markdown('<div class="sec teal" style="font-size:.82rem;">OPÉRATION IMMOBILIÈRE</div>',unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({"Paramètre":["Prix d'acquisition","Zone / Surface pondérée","Loyer mensuel initial",f"Type : {type_loyer}","Amortissement annuel","Base amortissable (80%)"],
            "Valeur":[fe(prix),f"Zone {zone} · {fn(res['sp'],1)} m²",fe(res["lmens"]),fp(TAUX_AMT[type_loyer]),fe(res["amort_an"]),fe(res["base_a"])]}),hide_index=True,use_container_width=True)
    st.markdown("---")
    for lbl,hk,n,bc,bg,icon in [
        ("HORIZON 9 ANS — Fin durée d'engagement","h9",9,"#3761AD","#EEF2FB","🔹"),
        ("HORIZON 15 ANS — Horizon de référence","h15",15,"#009FA3","#E4F5F5","🔸"),
        ("HORIZON 25 ANS — Financement soldé · Pleine propriété","h25",25,"#EA653D","#FEF0EC","⭐"),
    ]:
        h=res[hk]
        st.markdown(f'<div class="sec" style="background:{bc};">{icon} {lbl}</div>',unsafe_allow_html=True)
        st.caption(f"Moyennes mensuelles calculées sur {n} ans ({n*12} mois)")
        ca2,cb2,cc2=st.columns([2.5,2.5,2])
        with ca2:
            st.markdown(f'<div style="color:#009FA3;font-weight:700;font-size:.85rem;margin-bottom:.3rem;">✚ CE QUI RENTRE (+)</div>',unsafe_allow_html=True)
            st.dataframe(pd.DataFrame({"":["Loyer mensuel moyen","Gain fiscal/mois","TOTAL ENTRÉES"],"€/mois":[fe(h["lm"]),fe(h["gm"]),fe(h["te"])]}),hide_index=True,use_container_width=True)
        with cb2:
            st.markdown(f'<div style="color:#EA653D;font-weight:700;font-size:.85rem;margin-bottom:.3rem;">− CE QUI SORT (−)</div>',unsafe_allow_html=True)
            st.dataframe(pd.DataFrame({"":["Mensualité de crédit","Charges/mois","TOTAL SORTIES"],"€/mois":[fe(h["cm"]),fe(h["chm"]),fe(h["ts"])]}),hide_index=True,use_container_width=True)
        with cc2:
            ef=h["ef"]; ec="#EA653D" if ef<0 else "#009FA3"
            st.markdown(f"""<div style="background:{bg};border-radius:9px;padding:1rem;text-align:center;border-top:4px solid {bc};">
            <div style="font-size:.67rem;color:#888;text-transform:uppercase;letter-spacing:.06em;">Effort d'investissement mensuel</div>
            <div style="font-size:1.3rem;font-weight:800;color:{ec};margin:.3rem 0;">{fe(abs(ef))}</div>
            <hr style="margin:.35rem 0;border-color:#ddd;">
            <div style="font-size:.77rem;text-align:left;line-height:1.85;">
              <b>Capital net (0%)</b> : {fe(h["cap0"])}<br><b>Capital net (+1,5%)</b> : {fe(h["cap15"])}<br>
              <b>Gain fiscal total</b> : {fe(h["gft"])}<br>
              <span style="color:#888;"><em>dont déficit</em> : {fe(h["dont_d"])} · <em>dont Jeanbrun</em> : {fe(h["dont_j"])}</span>
            </div></div>""",unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="sec blue">📖 COMMENT LIRE CE TABLEAU</div>',unsafe_allow_html=True)
    st.markdown("- ▸ Le côté **VERT (+)** = loyers + économie d'impôt Jeanbrun.\n- ▸ Le côté **ROUGE (−)** = mensualité de crédit + charges d'exploitation.\n- ▸ L'**EFFORT D'ÉPARGNE** = reste à charge réel. Négatif = complément mensuel à prévoir.\n- ▸ Gain fiscal = **déficit naturel** (intérêts, même sans Jeanbrun) + **Jeanbrun** (amortissement supplémentaire).\n- ▸ Document non contractuel. Hypothèses d'indexation et fiscalité constantes.")
    st.markdown('<div class="footer"><b>médicis IMMOBILIER NEUF</b> — www.medicis-immobilier-neuf.fr · Simulation personnalisée non contractuelle</div>',unsafe_allow_html=True)


# ─── T3 DÉTAILLÉE ───
with t3:
    st.markdown('<div class="sec">PROJECTION FINANCIÈRE ANNUELLE — DISPOSITIF JEANBRUN · 25 ans</div>',unsafe_allow_html=True)
    ca,cb,cc=st.columns(3)
    with ca:
        st.markdown('<div class="sec blue" style="font-size:.82rem;">SITUATION DU FOYER</div>',unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({"":["Revenus déclarés","Impôt avant opération","Impôt après (an 1)","TMI","Parts fiscales"],
            "Valeur":[fe(rev),fe(res["ir_av1"]+max(0,rfa)*TAUX_PS),fe(res["ir_ap1"]),fp(res["tmi_av"]),fn(parts,1)]}),hide_index=True,use_container_width=True)
    with cb:
        st.markdown('<div class="sec teal" style="font-size:.82rem;">FINANCEMENT</div>',unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({"":["Apport","Montant emprunté","Taux nominal","Mensualité totale","Coût total acquisition"],
            "Valeur":[fe(apport),fe(res["mempr"]),fp(ti),fe(res["mens_tot"]),fe(res["cout"])]}),hide_index=True,use_container_width=True)
    with cc:
        st.markdown('<div class="sec orange" style="font-size:.82rem;">DISPOSITIF JEANBRUN</div>',unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({"":["Base amortissable (80%)","Taux d'amortissement","Amortissement annuel","Plafond annuel","Charges exploitation","Éco. fiscale an 1"],
            "Valeur":[fe(res["base_a"]),fp(TAUX_AMT[type_loyer]),fe(res["amort_an"]),fe(PLAF_AMT[type_loyer]),fp(cp),fe(res["eco1"])]}),hide_index=True,use_container_width=True)
    st.markdown('<div class="sec blue">PROJECTION ANNUELLE 25 ANS</div>',unsafe_allow_html=True)
    rows=[]
    for a in ann:
        rows.append({"An":a["an"],"Loyers (€)":round(a["lo"],0),"Remb. prêt (€)":round(a["remb"],0),
            "Charges (€)":round(a["ch"],0),"Amort. JB (€)":round(a["amort"],0),
            "RF net (€)":round(a["rfn"],0),"Déd. RG (€)":round(a["ded"],0),
            "Stock déf. (€)":round(a["stock_def"],0),"IR avant (€)":round(a["ir_av"],0),
            "IR après (€)":round(a["ir_ap"],0),"Éco. fisc. (€)":round(a["eco"],0),
            "Effort/mois (€)":round(a["effort"],0),"Cap. net 0% (€)":round(a["cap0"],0),
            "Cap. net +1,5% (€)":round(a["cap15"],0),"Amt. cumulé (€)":round(a["amt_cum"],0)})
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True,height=560)
    st.markdown('<div class="footer"><b>médicis IMMOBILIER NEUF</b> — www.medicis-immobilier-neuf.fr · Document non contractuel</div>',unsafe_allow_html=True)

# ─── T4 REVENTE ───
with t4:
    st.markdown('<div class="sec">SIMULATION DE REVENTE — Calcul pédagogique de la plus-value et de l\'enrichissement net</div>',unsafe_allow_html=True)
    cols=st.columns(3)
    for col,(an_r,lbl,bc,bg,icon) in zip(cols,[(9,"REVENTE À 9 ANS","#3761AD","#EEF2FB","🔹"),(15,"REVENTE À 15 ANS","#009FA3","#E4F5F5","🔸"),(25,"REVENTE À 25 ANS","#EA653D","#FEF0EC","⭐")]):
        a=ann[an_r-1]; pv0=prix; pv15=prix*(1.015**an_r)
        with col:
            st.markdown(f"<h4 style='color:{bc};font-family:Poppins,sans-serif;margin-bottom:.6rem;'>{icon} {lbl}</h4>",unsafe_allow_html=True)
            for titre,pv_v,pv_b,ipv,cap in [("0% — prix stable",pv0,a["pv0"],a["ipv0"],a["cap0"]),("+1,5%/an",pv15,a["pv15"],a["ipv15"],a["cap15"])]:
                pvi=max(0,pv_b*(1-a["ai"])); pps=max(0,pv_b*(1-a["ap"]))
                cap_col="#009FA3" if cap>0 else "#EA653D"
                st.markdown(f"""<div style="background:{bg};border-radius:9px;padding:.85rem 1rem;margin-bottom:.65rem;border-left:4px solid {bc};">
                <div style="font-weight:700;font-size:.8rem;color:{bc};margin-bottom:.45rem;">Scénario {titre}</div>
                <div style="font-size:.78rem;line-height:2.0;">
                Prix de vente : <b>{fe(pv_v)}</b><br>
                + Frais acq. 7,5% : +{fe(a["fac"])} · Travaux 15% : +{fe(a["ftv"])}<br>
                − Amort. réintégrés : −{fe(a["amt_cum"])}<br>
                <b>= Prix de revient : {fe(a["pr"])}</b><br>
                <span style="color:{bc};font-weight:700;">➜ PV brute : {fe(pv_b)}</span><br>
                Abatt. IR {fp(a["ai"])} / PS {fp(a["ap"])}<br>
                IR 19% : {fe(pvi*TAUX_IR_PV)} · PS 17,2% : {fe(pps*TAUX_PS_PV)} · Surtaxe : {fe(max(0.,surtaxe(pvi)))}<br>
                <b>Total impôt PV : <span style="color:#EA653D;">{fe(ipv)}</span></b><br>
                CRD : {fe(a["crd"])}<br>
                <span style="color:{cap_col};font-weight:800;font-size:.95rem;">✅ Capital net : {fe(cap)}</span>
                </div></div>""",unsafe_allow_html=True)
    st.markdown('<div class="sec blue">💡 COMPRENDRE VOTRE ENRICHISSEMENT</div>',unsafe_allow_html=True)
    st.markdown("- ▸ Capital net = ce qui reste **en poche** après crédit soldé et impôt sur la plus-value.\n- ▸ Exonération totale d'IR à **22 ans**, de PS à **30 ans**.\n- ▸ L'amortissement Jeanbrun est réintégré dans la PV, mais l'économie d'impôt annuelle vous a déjà enrichi.\n- ▸ Le scénario 0% est conservateur. Le +1,5%/an reflète l'évolution historique moyenne du marché.\n- ▸ À 25 ans, crédit soldé (CRD = 0) : capital net = valeur du bien − impôt PV uniquement.")
    st.markdown('<div class="footer"><b>médicis IMMOBILIER NEUF</b> — www.medicis-immobilier-neuf.fr · Simulation personnalisée non contractuelle</div>',unsafe_allow_html=True)


# ─── T5 MOTEUR ───
with t5:
    st.markdown('<div class="sec">⚙️ MOTEUR — Données annuelles complètes · Colonnes A à AW de la feuille Excel V9</div>',unsafe_allow_html=True)
    st.caption("Toutes les valeurs intermédiaires de calcul sur 25 ans. Lecture fidèle à la feuille « Moteur » du fichier Excel.")
    rows=[]
    for a in ann:
        rows.append({"An":a["an"],"B·Loyers":round(a["lo"],2),"C·Charges":round(a["ch"],2),
            "D·Intérêts":round(a["int_a"],2),"E·Assurance":round(a["ass_a"],2),"F·Amort.JB":round(a["amort"],2),
            "G·CRD":round(a["crd"],2),"H·Val.bien":prix,"I·RF autres":rfa,
            "Q·RF bruts":round(a["rf_b"],2),"R·Ch.fin.":round(a["ch_f"],2),"S·Ch.non-fin":round(a["ch_nf"],2),
            "T·RF net gl.":round(a["rfn"],2),"U·Déd.RG":round(a["ded"],2),
            "V·Déf.généré":round(a["def_g"],2),"W·Stock déf.":round(a["stock_def"],2),
            "X·Déf.imputé":round(a["def_imp"],2),"Y·RF net tax.":round(a["rfnt"],2),
            "Z·Rev.après":round(a["rev_ap"],2),
            "AB·TMI après":fp(get_tmi(max(0,a["rev_ap"]),parts)),
            "AD·IR après":round(a["ir_ap"],2),"AE·PS après":round(a["ps_ap"],2),
            "AF·Tot.après":round(a["tot_ap"],2),"AG·Éco.fisc.":round(a["eco"],2),
            "AI·Eff./mois":round(a["effort"],2),"AL·Amt.cum.":round(a["amt_cum"],2),
            "AN·PV brute 0%":round(a["pv0"],2),"AO·Abatt.IR":fp(a["ai"]),"AQ·Abatt.PS":fp(a["ap"]),
            "AS·Impôt PV":round(a["ipv0"],2),"AU·Cap.net 0%":round(a["cap0"],2),"AU+·Cap.+1,5%":round(a["cap15"],2)})
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True,height=560)
    st.markdown("""
**Légende :**
- **T · RF net global** = RF bruts − charges financières − charges non-financières (dont amortissement Jeanbrun)
- **U · Déd. RG** = part du déficit imputable sur le revenu global (plafond 10 700 €/an, art. 156-I-3 CGI)
- **W · Stock déficit** = cumul reportable sur RF sur 10 ans
- **AG · Éco. fiscale** = (IR + PS) avant opération − (IR + PS) après opération
""")
    st.markdown('<div class="footer"><b>médicis IMMOBILIER NEUF</b> — Document de travail interne non contractuel</div>',unsafe_allow_html=True)

# ─── T6 RÈGLES FISCALES ───
with t6:
    st.markdown('<div class="sec">📐 RÈGLES FISCALES — Références législatives dispositif Jeanbrun</div>',unsafe_allow_html=True)
    col1,col2=st.columns(2)
    with col1:
        st.markdown('<div class="sec blue" style="font-size:.82rem;">DISPOSITIF JEANBRUN — PRINCIPES</div>',unsafe_allow_html=True)
        st.markdown(f"""
| Paramètre | Valeur | Référence |
|---|---|---|
| Base amortissable | 80% du prix d'acquisition | Art. 2 quindecies B ann. III CGI |
| Taux — Loyer intermédiaire | **3,5 %** | Art. 2 quindecies B |
| Taux — Loyer social | **4,5 %** | Art. 2 quindecies B |
| Taux — Loyer très social | **5,5 %** | Art. 2 quindecies B |
| Plafond annuel — Intermédiaire | **8 000 €** | Art. 2 quindecies B |
| Plafond annuel — Social | **10 000 €** | Art. 2 quindecies B |
| Plafond annuel — Très social | **12 000 €** | Art. 2 quindecies B |
| Durée d'engagement minimale | 9 ans | Art. 199 novovicies CGI |
| Réintégration à la revente | Amortissements déduits | Art. 150 VB CGI |
| Coefficient multiplicateur | TRUNC((0,7 + 19/SP) × 100)/100 | Art. 2 terdecies D |
""")
        st.markdown('<div class="sec teal" style="font-size:.82rem;">DÉFICIT FONCIER — ART. 156-I-3 CGI</div>',unsafe_allow_html=True)
        st.markdown(f"""
| Règle | Valeur |
|---|---|
| Plafond d'imputation sur le revenu global | **10 700 €/an** |
| Déficit lié aux intérêts d'emprunt | Non imputable sur RG → reportable sur RF seulement |
| Déficit lié aux charges non-financières | Imputable sur RG dans la limite de 10 700 € |
| Report du déficit excédentaire | **10 ans** (droit commun) |
| Engagement de location après imputation | **3 ans** minimum |
""")
        st.markdown('<div class="sec orange" style="font-size:.82rem;">PLUS-VALUE IMMOBILIÈRE — ART. 150 U CGI</div>',unsafe_allow_html=True)
        st.markdown(f"""
| Paramètre | Valeur |
|---|---|
| Forfait frais d'acquisition | **7,5 %** du prix d'achat |
| Forfait travaux (si > 5 ans détenus) | **15 %** du prix d'achat |
| Taux IR plus-value | **19 %** |
| Taux PS plus-value | **17,2 %** |
| Exonération totale IR | **22 ans** de détention |
| Exonération totale PS | **30 ans** de détention |
""")
    with col2:
        st.markdown('<div class="sec blue" style="font-size:.82rem;">ABATTEMENTS POUR DURÉE DE DÉTENTION (années 1→25)</div>',unsafe_allow_html=True)
        abr=[]
        for yr in range(1,26):
            abr.append({"Année":yr,"Abatt. IR":fp(abatt_ir(yr)),"Abatt. PS":fp(abatt_ps(yr)),"IR résiduel":fp(1-abatt_ir(yr)),"PS résiduelle":fp(1-abatt_ps(yr))})
        st.dataframe(pd.DataFrame(abr),hide_index=True,use_container_width=True,height=470)
        st.markdown(f"""
> **Votre simulation :** Frais acq. retenus = **{fe(ann[0]["fac"])}** · Travaux = **{fe(ann[8]["ftv"])}** (à 9 ans)
""")
        st.markdown('<div class="sec teal" style="font-size:.82rem;">SURFACE PONDÉRÉE — ART. 2 TERDECIES D</div>',unsafe_allow_html=True)
        st.markdown(f"""
| Cas | Formule |
|---|---|
| RDC = NON | SP = Surf. hab. + min(Balcon + Terrasse, 16) / 2 |
| RDC = OUI | SP = Surf. hab. + min(Balcon, 16) / 2 (terrasse exclue) |
| Coefficient | TRUNC(min(0,7 + 19/SP ; 1,2) × 100) / 100 |
| Cap coefficient | **1,20 maximum** |
| Loyer max légal | Plafond €/m²/mois × SP × Coefficient |

> **Votre bien :** SP = **{fn(res['sp'],1)} m²** · Coeff = **{fn(res['coeff'],2)}** · Loyer max = **{fe(res['lmax'])}/mois**

> **Abattement revenus :** {type_rev} → {fe(res["ab"])} → Revenus nets = {fe(res["rn"])}
""")
    st.markdown('<div class="footer"><b>médicis IMMOBILIER NEUF</b> — Sources : CGI, Francis Lefebvre, Legifrance — Document interne non contractuel</div>',unsafe_allow_html=True)


# ─── T7 PLAFONDS LOYERS ───
with t7:
    st.markdown('<div class="sec">🏘️ PLAFONDS DE LOYERS — Art. 2 terdecies D ann. III CGI — Dispositif Jeanbrun 2025/2026</div>',unsafe_allow_html=True)
    col1,col2=st.columns([2.5,1.5])
    with col1:
        st.markdown('<div class="sec blue" style="font-size:.82rem;">TABLEAU DES PLAFONDS €/m²/MOIS (hors charges) — Par zone et type</div>',unsafe_allow_html=True)
        plaf_rows=[]
        for z,v in PLAFONDS_LOYERS.items():
            plaf_rows.append({"Zone":z,"Loyer intermédiaire":f"{v['Loyer intermédiaire']} €/m²/mois",
                "Loyer social":f"{v['Loyer social']} €/m²/mois","Loyer très social":f"{v['Loyer très social']} €/m²/mois"})
        st.dataframe(pd.DataFrame(plaf_rows),hide_index=True,use_container_width=True)
        st.markdown("> **Loyer max légal** = Plafond €/m²/mois × **Surface pondérée** × **Coefficient multiplicateur**")
        st.markdown('<div class="sec teal" style="font-size:.82rem;">SIMULATION LOYER MAX LÉGAL — VOTRE BIEN (SP = {0} m² · Coeff = {1})</div>'.format(fn(res["sp"],1),fn(res["coeff"],2)),unsafe_allow_html=True)
        sim_r=[]
        for z,v in PLAFONDS_LOYERS.items():
            for tl,plm2 in v.items():
                lm=plm2*res["sp"]*res["coeff"]
                sim_r.append({"Zone":z,"Type":tl,f"€/m²":{v[tl]},"Loyer max légal":fe(lm),"Votre loyer OK ?":"✅" if ls<=lm else "❌ Dépasse"})
        st.dataframe(pd.DataFrame(sim_r),hide_index=True,use_container_width=True)
    with col2:
        st.markdown('<div class="sec orange" style="font-size:.82rem;">PLAFONDS D\'AMORTISSEMENT ANNUEL</div>',unsafe_allow_html=True)
        st.markdown("""
| Type de loyer | Taux | Plafond/an |
|---|---|---|
| Intermédiaire | **3,5 %** | **8 000 €** |
| Social | **4,5 %** | **10 000 €** |
| Très social | **5,5 %** | **12 000 €** |

_Appliqué sur **80%** du prix d'acquisition_
""")
        st.markdown('<div class="sec blue" style="font-size:.82rem;">GÉOGRAPHIE DES ZONES</div>',unsafe_allow_html=True)
        st.markdown("""
| Zone | Périmètre |
|---|---|
| **A bis** | Paris + 76 communes limitrophes |
| **A** | Île-de-France (hors A bis), Côte d'Azur, Genevois français |
| **B1** | Agglomérations > 250 000 hab., grande couronne |
| **B2** | 50–250 000 hab. (sur agrément préfectoral) |
| **C** | Reste du territoire |
""")
        st.markdown('<div class="sec teal" style="font-size:.82rem;">VOTRE SIMULATION</div>',unsafe_allow_html=True)
        st.markdown(f"""
| Paramètre | Valeur |
|---|---|
| Zone | **{zone}** · Type : **{type_loyer}** |
| Surface hab. | **{surf} m²** |
| Balcon / Terrasse | {balcon} m² / {terrasse} m² |
| RDC | **{rdc}** |
| **Surface pondérée** | **{fn(res["sp"],1)} m²** |
| **Coefficient** | **{fn(res["coeff"],2)}** |
| **Loyer max légal** | **{fe(res["lmax"])}/mois** |
| **Loyer retenu** | **{fe(res["lmens"])}/mois** |
""")
    st.markdown('<div class="footer"><b>médicis IMMOBILIER NEUF</b> — Source : art. 2 terdecies D ann. III CGI — Plafonds 2025/2026</div>',unsafe_allow_html=True)

# ─── T8 BARÈME FISCAL ───
with t8:
    st.markdown('<div class="sec">📊 BARÈME FISCAL IR 2026 — Art. 197 CGI · Prélèvements sociaux · Simulation personnalisée</div>',unsafe_allow_html=True)
    col1,col2=st.columns([1.5,2])
    with col1:
        st.markdown('<div class="sec blue" style="font-size:.82rem;">TRANCHES IR 2026 (par part de QF)</div>',unsafe_allow_html=True)
        st.dataframe(pd.DataFrame([
            {"Tranche":"Jusqu'à 11 600 €","Taux":"0 %"},
            {"Tranche":"11 601 € à 29 579 €","Taux":"11 %"},
            {"Tranche":"29 580 € à 84 577 €","Taux":"30 %"},
            {"Tranche":"84 578 € à 181 917 €","Taux":"41 %"},
            {"Tranche":"Au-delà de 181 917 €","Taux":"45 %"},
        ]),hide_index=True,use_container_width=True)
        st.markdown('<div class="sec teal" style="font-size:.82rem;">PLAFONNEMENT QUOTIENT FAMILIAL</div>',unsafe_allow_html=True)
        st.markdown(f"""
| Règle | Valeur |
|---|---|
| Plafond par demi-part | **1 759 €** |
| Parts de référence couple | 2,0 parts |
| Parts de référence célibataire | 1,0 part |

> Vos {fn(parts,1)} parts → économie max QF = **{fe(max(0.,(parts-(2. if parts>=2. else 1.))*2*PLAFOND_QF))}**
""")
        st.markdown('<div class="sec orange" style="font-size:.82rem;">PRÉLÈVEMENTS SOCIAUX — 17,2%</div>',unsafe_allow_html=True)
        st.markdown("""
| Prélèvement | Taux |
|---|---|
| CSG | 9,2 % |
| CRDS | 0,5 % |
| Prélèvement solidarité | 7,5 % |
| **Total PS** | **17,2 %** |
| dont CSG déductible (N+1) | **6,8 %** |
""")
    with col2:
        st.markdown('<div class="sec blue" style="font-size:.82rem;">SIMULATION IR COMPARÉE — AVANT / APRÈS OPÉRATION</div>',unsafe_allow_html=True)
        avap=[]
        for an_d in [1,2,3,5,9,12,15,20,25]:
            a=ann[an_d-1]
            avap.append({"An":an_d,"Revenus nets avant":fe(res["rn"]+rfa),"IR avant":fe(a["ir_av"]),
                "Base après":fe(a["rev_ap"]),"IR après":fe(a["ir_ap"]),"PS après":fe(a["ps_ap"]),
                "Économie fiscale":fe(a["eco"]),"TMI après":fp(get_tmi(max(0,a["rev_ap"]),parts))})
        st.dataframe(pd.DataFrame(avap),hide_index=True,use_container_width=True)
        st.markdown('<div class="sec teal" style="font-size:.82rem;">CALCUL DÉTAILLÉ ANNÉE 1</div>',unsafe_allow_html=True)
        a1=ann[0]
        st.markdown(f"""
| Étape | Montant |
|---|---|
| Revenus déclarés | {fe(rev)} |
| − Abattement ({type_rev}) | −{fe(res["ab"])} |
| = Revenus nets | **{fe(res["rn"])}** |
| + RF autres biens | +{fe(rfa)} |
| + Déduction RG (déficit foncier) | {fe(a1["ded"])} |
| − CSG déductible N-1 | 0 € (an 1) |
| **= Base imposable après** | **{fe(a1["rev_ap"])}** |
| IR avant | {fe(a1["ir_av"])} |
| IR après | {fe(a1["ir_ap"])} |
| PS avant (sur RF autres) | {fe(max(0.,rfa)*TAUX_PS)} |
| PS après (sur RF net taxable) | {fe(a1["ps_ap"])} |
| **Économie fiscale totale an 1** | **{fe(a1["eco"])}** |
""")
    st.markdown('<div class="footer"><b>médicis IMMOBILIER NEUF</b> — Barème IR 2026 (art. 197 CGI) · Plafonnement QF 1 759 €/demi-part</div>',unsafe_allow_html=True)


# ─── T9 TABLEAU D'AMORTISSEMENT ───
with t9:
    st.markdown('<div class="sec">💰 TABLEAU D\'AMORTISSEMENT FINANCIER — Prêt immobilier</div>',unsafe_allow_html=True)
    col1,col2=st.columns([2.5,1.5])
    with col2:
        st.markdown('<div class="sec blue" style="font-size:.82rem;">CARACTÉRISTIQUES DU PRÊT</div>',unsafe_allow_html=True)
        st.markdown(f"""
| Paramètre | Valeur |
|---|---|
| Capital emprunté | **{fe(res["mempr"])}** |
| Taux nominal annuel | **{fp(ti)}** |
| Durée | **{duree} ans ({duree*12} mois)** |
| **Mensualité (hors assurance)** | **{fe(res["mens_tot"]-res["mempr"]*ta/12)}** |
| Assurance mensuelle | {fe(res["mempr"]*ta/12)} |
| **Mensualité totale** | **{fe(res["mens_tot"])}** |
| Coût total du crédit | {fe(res["mens_tot"]*duree*12-res["mempr"])} |
""")
        st.markdown('<div class="sec teal" style="font-size:.82rem;">AMORTISSEMENT JEANBRUN</div>',unsafe_allow_html=True)
        st.markdown(f"""
| Paramètre | Valeur |
|---|---|
| Base (80% prix acq.) | **{fe(res["base_a"])}** |
| Taux d'amortissement | **{fp(TAUX_AMT[type_loyer])}** |
| Plafond annuel | **{fe(PLAF_AMT[type_loyer])}** |
| **Amortissement retenu** | **{fe(res["amort_an"])}/an** |
| Cumul 9 ans | {fe(res["amort_an"]*9)} |
| Cumul 15 ans | {fe(res["amort_an"]*15)} |
| Cumul 25 ans | {fe(res["amort_an"]*25)} |
""")
    with col1:
        view=st.radio("Afficher :",["Tableau annuel","Tableau mensuel (3 premières années)"],horizontal=True)
        if view=="Tableau annuel":
            st.markdown('<div class="sec blue" style="font-size:.82rem;">AMORTISSEMENT ANNUEL</div>',unsafe_allow_html=True)
            ar=[]
            for i,row in enumerate(res["amttab"]):
                ic=sum(r["int"] for r in res["amttab"][:i+1])
                pc=sum(r["princ"] for r in res["amttab"][:i+1])
                ar.append({"An":i+1,"Capital amorti":fe(row["princ"]),"Intérêts":fe(row["int"]),
                    "Assurance":fe(res["mempr"]*ta/12*12),"Total remboursé":fe(row["princ"]+row["int"]+res["mempr"]*ta/12*12),
                    "CRD fin d'année":fe(row["crd"]),"Intérêts cumulés":fe(ic),"Capital remb. %":fp(pc/res["mempr"])})
            st.dataframe(pd.DataFrame(ar),hide_index=True,use_container_width=True,height=520)
        else:
            st.markdown('<div class="sec teal" style="font-size:.82rem;">TABLEAU MENSUEL — 3 PREMIÈRES ANNÉES (36 mois)</div>',unsafe_allow_html=True)
            mr=[]
            for r in res["rows_m"][:36]:
                mr.append({"Mois":r["mois"],"Intérêts":fe(r["im"]),"Capital amorti":fe(r["pm"]),
                    "Assurance":fe(res["mempr"]*ta/12),"Total mensualité":fe(r["im"]+r["pm"]+res["mempr"]*ta/12),"CRD":fe(r["crd"])})
            st.dataframe(pd.DataFrame(mr),hide_index=True,use_container_width=True,height=520)
        try:
            import plotly.graph_objects as gof2
            xs_a=list(range(1,len(res["amttab"])+1))
            fig2=gof2.Figure()
            fig2.add_trace(gof2.Bar(x=xs_a,y=[r["int"] for r in res["amttab"]],name="Intérêts",marker_color="#EA653D"))
            fig2.add_trace(gof2.Bar(x=xs_a,y=[r["princ"] for r in res["amttab"]],name="Capital",marker_color="#3761AD"))
            fig2.add_trace(gof2.Scatter(x=xs_a,y=[r["crd"] for r in res["amttab"]],name="CRD (€)",yaxis="y2",
                line=dict(color="#009FA3",width=2.5),mode="lines"))
            fig2.update_layout(barmode="stack",height=240,margin=dict(l=10,r=10,t=15,b=10),
                yaxis2=dict(overlaying="y",side="right",tickformat=",.0f"),
                legend=dict(orientation="h",y=-.3),plot_bgcolor="white",paper_bgcolor="white",
                font=dict(family="Poppins,sans-serif",size=10),
                xaxis=dict(title="Année",gridcolor="#f0f0f0"),yaxis=dict(title="€/an",gridcolor="#f0f0f0"))
            st.plotly_chart(fig2,use_container_width=True)
        except ImportError:
            pass
    st.markdown('<div class="footer"><b>médicis IMMOBILIER NEUF</b> — Calcul mensuel exact, agrégé annuellement</div>',unsafe_allow_html=True)

# ─── T10 IMPRIMER ───
with t10:
    st.markdown('<div class="sec">🖨️ IMPRESSION A4</div>',unsafe_allow_html=True)
    st.markdown("""
Pour imprimer une synthèse en format A4 :
1. Allez sur l'onglet souhaité (**Synthèse Visuelle**, **Simplifiée** ou **Revente & Plus-value**)
2. Cliquez sur le bouton ci-dessous — ou faites **Ctrl+P** (Cmd+P sur Mac)
3. Choisissez **Format A4 Paysage** dans les options du navigateur
4. Désactivez les en-têtes/pieds de page du navigateur si besoin
""")
    import streamlit.components.v1 as components
    components.html("""<button onclick="window.parent.print();" style="
        padding:.8rem 2.5rem;font-size:1rem;cursor:pointer;
        background:#EA653D;color:white;border:none;border-radius:8px;
        font-weight:600;letter-spacing:.04em;display:block;margin:1.2rem auto;
        font-family:Poppins,sans-serif;box-shadow:0 4px 12px rgba(234,101,61,.3);">
        🖨️ Imprimer cette page (A4 Paysage)
    </button>""",height=75)
    st.markdown("---")
    st.caption("**Moteur de calcul** : Python natif · Fidélité totale aux formules Excel V9 · Barème IR 2026 avec plafonnement QF (1 759 €/demi-part) · Déficits fonciers art. 156-I-3 CGI · Document non contractuel")
    st.markdown('<div class="footer"><b>médicis IMMOBILIER NEUF</b> — www.medicis-immobilier-neuf.fr · Outil réservé aux conseillers</div>',unsafe_allow_html=True)

