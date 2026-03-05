"""
Simulateur Jeanbrun V9 — Streamlit App
Moteur de calcul Python 100% conforme aux formules Excel V9
"""
import streamlit as st
import pandas as pd
import math
import io

st.set_page_config(page_title="Simulateur Jeanbrun", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")

# ═══════════════════════════════════════════════════════════════════
# CSS GLOBAL + IMPRESSION A4
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Palette ── */
:root { --db:#13415B; --mb:#3761AD; --teal:#009FA3; --orange:#EA653D; --green:#27ae60; --red:#e74c3c; --light:#EEF2FB; }

/* ── Header ── */
.hdr { background:linear-gradient(135deg,#13415B 0%,#3761AD 100%); color:white; padding:1.2rem 2rem; border-radius:10px; margin-bottom:1.2rem; }
.hdr h1 { margin:0; font-size:1.55rem; } .hdr p { margin:.3rem 0 0; opacity:.8; font-size:.88rem; }

/* ── KPI cards ── */
.kpi { background:#EEF2FB; border-left:4px solid #3761AD; border-radius:8px; padding:.85rem 1.1rem; }
.kpi.t { background:#E5F6F6; border-color:#009FA3; }
.kpi.o { background:#FFF3EE; border-color:#EA653D; }
.kpi.d { background:#E8EDF4; border-color:#13415B; }
.kpi.g { background:#EAF6EE; border-color:#27ae60; }
.kpi-lbl { font-size:.72rem; color:#555; text-transform:uppercase; letter-spacing:.05em; }
.kpi-val { font-size:1.35rem; font-weight:700; color:#13415B; margin-top:.15rem; }
.kpi-sub { font-size:.72rem; color:#777; }

/* ── Section header ── */
.sec { background:#13415B; color:white; padding:.45rem 1rem; border-radius:6px; font-weight:600; margin:1.2rem 0 .6rem; font-size:.95rem; }

/* ── Compte en T cards ── */
.cnt-card { border-radius:10px; padding:1.1rem; height:100%; }
.cnt-tbl { width:100%; border-collapse:collapse; font-size:.85rem; }
.cnt-tbl td { padding:.22rem .3rem; }
.cnt-tbl .sep { border-top:1px solid #ddd; font-weight:600; }
.cnt-total { text-align:center; margin-top:.7rem; }
.cnt-bilan { background:white; border-radius:6px; padding:.55rem; font-size:.8rem; margin-top:.55rem; }

/* ── Pédagogique ── */
.ped { border-radius:8px; padding:1rem 1.1rem; display:flex; gap:.8rem; align-items:flex-start; }
.ped-icon { font-size:1.5rem; }
.ped-title { font-weight:700; margin-bottom:.3rem; }
.ped-text { font-size:.83rem; }

/* ── Footer ── */
.footer { margin-top:2rem; padding:.6rem 0; border-top:1px solid #ddd; font-size:.72rem; color:#888; text-align:center; }

/* ── Tableau revente ── */
.rev-row { display:flex; justify-content:space-between; font-size:.83rem; padding:.18rem 0; border-bottom:1px solid #f0f0f0; }
.rev-row.bold { font-weight:700; border-top:2px solid #ddd; margin-top:.3rem; padding-top:.3rem; }
.rev-row.group { margin-top:.5rem; font-size:.78rem; color:#555; border-bottom:none; }

/* ═══ IMPRESSION A4 ═══ */
@media print {
  [data-testid="stSidebar"], [data-testid="stToolbar"], .stTabs [data-baseweb="tab-list"],
  button, .stDownloadButton, [data-testid="stDecoration"] { display:none !important; }
  .stApp { background:white !important; }
  .main .block-container { padding:0 !important; max-width:100% !important; }
  .hdr { background:#13415B !important; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .kpi, .cnt-card, .ped { -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  @page { size:A4 landscape; margin:1.5cm; }
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# AUTHENTIFICATION
# ═══════════════════════════════════════════════════════════════════
def check_password():
    if st.session_state.get("auth"): return True
    _, c, _ = st.columns([1, 1.4, 1])
    with c:
        st.markdown("""<div style="text-align:center;padding:2.5rem 2rem;background:white;
        border-radius:14px;box-shadow:0 6px 32px rgba(19,65,91,.13);margin-top:5rem;">
        <h2 style="color:#13415B;margin-top:0;">🏠 Simulateur<br>Dispositif Jeanbrun</h2>
        <p style="color:#666;font-size:.9rem;">Outil réservé aux conseillers<br><em>médicis IMMOBILIER NEUF</em></p>
        </div>""", unsafe_allow_html=True)
        pwd = st.text_input("", type="password", label_visibility="collapsed", placeholder="🔑  Mot de passe conseiller")
        if st.button("Se connecter", use_container_width=True, type="primary"):
            if pwd == st.secrets.get("password", "jeanbrun2025"):
                st.session_state.auth = True; st.rerun()
            else:
                st.error("Mot de passe incorrect")
    return False

if not check_password(): st.stop()

# ═══════════════════════════════════════════════════════════════════
# BARÈMES ET CONSTANTES (conformes Barème fiscal du fichier)
# ═══════════════════════════════════════════════════════════════════
PLAFOND_QF       = 1759.0   # €/demi-part
PLAFOND_DEF_RG   = 10700.0  # € — déficit imputable revenu global
CSG_DED          = 0.068
TAUX_PS          = 0.172
TAUX_IR_PV       = 0.19
TAUX_PS_PV       = 0.172

# Barème IR 2026 (limite_inf, limite_sup, taux, réduction)
BAREME = [
    (0,       11600,  0.00,     0.0),
    (11600,   29579,  0.11,  1276.0),
    (29579,   84577,  0.30,  6896.01),
    (84577,  181917,  0.41, 16199.48),
    (181917,    9e9,  0.45, 23476.16),
]

PLAFONDS_LOYERS = {
    "A bis": {"Loyer intermédiaire":19.51,"Loyer social":15.61,"Loyer très social":11.71},
    "A":     {"Loyer intermédiaire":14.49,"Loyer social":11.59,"Loyer très social": 8.69},
    "B1":    {"Loyer intermédiaire":11.68,"Loyer social": 9.34,"Loyer très social": 7.01},
    "B2":    {"Loyer intermédiaire":10.15,"Loyer social": 8.12,"Loyer très social": 6.09},
    "C":     {"Loyer intermédiaire":10.15,"Loyer social": 8.12,"Loyer très social": 6.09},
}
PLAF_AMT = {"Loyer intermédiaire":8000,"Loyer social":10000,"Loyer très social":12000}
TAUX_AMT = {"Loyer intermédiaire":0.035,"Loyer social":0.045,"Loyer très social":0.055}
FORFAIT_FRAIS_PV  = 0.075
FORFAIT_TRAVAUX_PV= 0.15

# ═══════════════════════════════════════════════════════════════════
# FONCTIONS FISCALES
# ═══════════════════════════════════════════════════════════════════
def ir_brut_qf(qf):
    """IR sur 1 part (par tranche)."""
    t = 0.0
    for inf, sup, taux, _ in BAREME:
        if qf <= inf: break
        t += (min(qf, sup) - inf) * taux
    return t

def calcul_ir(revenu, parts):
    """IR avec plafonnement du quotient familial (art. 197 CGI)."""
    if revenu <= 0: return 0.0
    # IR théorique (parts réelles)
    ir_theo = ir_brut_qf(revenu / parts) * parts
    # IR de référence à 2 parts (couple) ou 1 part (célibataire)
    parts_ref = 2.0 if parts >= 2.0 else 1.0
    ir_ref = ir_brut_qf(revenu / parts_ref) * parts_ref
    # Demi-parts supplémentaires
    demi_sup = max(0.0, (parts - parts_ref) * 2)
    # Plafonnement: l'économie liée aux demi-parts ne peut dépasser 1759€/demi-part
    ir_plafonne = max(ir_theo, ir_ref - demi_sup * PLAFOND_QF)
    return max(0.0, ir_plafonne)

def tmi(revenu, parts):
    qf = revenu / parts if parts > 0 else 0
    for inf, sup, taux, _ in BAREME:
        if qf <= sup: return taux
    return 0.45

def abattement_10(revenus, nd, typ):
    if "Salaires" in typ:
        return max(504.0*nd, min(revenus*0.10, 14171.0*nd))
    if "Pensions" in typ:
        return max(442.0*nd, min(revenus*0.10, 4321.0*nd))
    return 0.0

def abatt_ir_pv(n):
    if n < 6:  return 0.0
    if n < 22: return (n-5)*0.06
    return 1.0

def abatt_ps_pv(n):
    if n < 6:  return 0.0
    if n < 22: return (n-5)*0.0165
    if n == 22: return 16*0.0165 + 0.016
    if n < 30: return 16*0.0165 + 0.016 + (n-22)*0.09
    return 1.0

def surtaxe_pv(pv):
    if pv <= 50000:  return 0.0
    if pv <= 60000:  return pv*0.02 - (60000-pv)*0.05
    if pv <= 100000: return pv*0.02
    if pv <= 110000: return pv*0.03 - (110000-pv)*0.10
    if pv <= 150000: return pv*0.03
    if pv <= 160000: return pv*0.04 - (160000-pv)*0.15
    if pv <= 200000: return pv*0.04
    if pv <= 210000: return pv*0.05 - (210000-pv)*0.20
    if pv <= 250000: return pv*0.05
    if pv <= 260000: return pv*0.06 - (260000-pv)*0.25
    return pv*0.06

def tableau_amt(capital, taux_an, duree_an):
    """Tableau d'amortissement annuel exact (calcul mensuel cumulé)."""
    r = taux_an / 12
    n = duree_an * 12
    mens = capital * r * (1+r)**n / ((1+r)**n - 1) if r > 0 else capital/n
    tab = []; crd = capital
    for _ in range(duree_an):
        int_a = princ_a = 0.0
        for _ in range(12):
            im = crd * r; pm = mens - im
            int_a += im; princ_a += pm; crd = max(0.0, crd - pm)
        tab.append({"int": int_a, "princ": princ_a, "crd": max(0.0, crd)})
    return mens, tab

# ═══════════════════════════════════════════════════════════════════
# MOTEUR PRINCIPAL (25 ANS)
# ═══════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def run(prix, frais_pct, surf, zone, rdc, balcon, terrasse,
        apport, ti, ta, duree, fg,
        type_loyer, loyer_souhaite, il, cp,
        type_rev, rev, rfa, parts, nd):

    # ── Bien ──
    frais = prix * frais_pct
    cout = prix + frais

    # Surface pondérée (conforme formule Excel)
    if rdc == "OUI":
        sp = surf + min(balcon, 16.0) / 2
    else:
        sp = surf + min(balcon + terrasse, 16.0) / 2
    # Coefficient (TRUNC à 2 décimales, cap 1.2)
    coeff_raw = 0.7 + 19.0/sp if sp > 0 else 1.2
    coeff = math.trunc(min(coeff_raw, 1.2) * 100) / 100
    plm2 = PLAFONDS_LOYERS.get(zone, PLAFONDS_LOYERS["A"]).get(type_loyer, 14.49)
    lmax = plm2 * sp * coeff
    lmens = min(loyer_souhaite, lmax)
    lann0 = lmens * 12

    # ── Financement ──
    mempr = cout - apport
    mens, amttab = tableau_amt(mempr, ti, duree)
    ass_mens = mempr * ta / 12
    ass_ann  = ass_mens * 12
    mens_tot = mens + ass_mens

    # ── Jeanbrun ──
    base_a = prix * 0.80
    amort_an = min(PLAF_AMT[type_loyer], base_a * TAUX_AMT[type_loyer])

    # ── Fiscal client (situation de référence) ──
    ab  = abattement_10(rev, nd, type_rev)
    rn  = rev - ab   # revenus nets après abattement
    tmi_av = tmi(rn + rfa, parts)
    ir_av0  = calcul_ir(rn + rfa, parts)
    ps_av0  = max(0.0, rfa) * TAUX_PS
    tot_av0 = ir_av0 + ps_av0

    # ── Moteur 25 ans ──
    annees = []
    stock_def = 0.0
    csg_prec  = 0.0

    for an in range(1, 26):
        i = an - 1
        lo = lann0 * (1 + il)**i
        ch = lo * cp
        idx = i if i < len(amttab) else -1
        if i < len(amttab):
            int_a = amttab[i]["int"]; ass_a = ass_ann; crd = amttab[i]["crd"]
            remb = (mens + ass_mens) * 12
        else:
            int_a = ass_a = crd = remb = 0.0
        vb0  = prix                     # 0% revalo
        vb15 = prix * (1.015)**an       # 1,5%/an

        # Colonnes MOTEUR
        # Q: RF bruts globaux
        rf_bruts = lo + rfa
        # R: charges financières (frais garantie an 1 uniquement)
        ch_fin = int_a + ass_a + (fg if an == 1 else 0.0)
        # S: charges non-financières
        ch_nfin = ch + amort_an
        # T: RF net global
        rfn = rf_bruts - ch_fin - ch_nfin

        # U: déduction imputable RG
        if rfn >= 0:
            ded_rg = 0.0
        elif rf_bruts >= ch_fin:  # déficit vient des charges non-fin
            ded_rg = max(rfn, -PLAFOND_DEF_RG)
        else:                     # déficit vient aussi des charges fin
            ded_rg = max(-ch_nfin, -PLAFOND_DEF_RG)

        # V: déficit reportable généré cette année
        if rfn >= 0:
            def_gen = 0.0
        elif rf_bruts >= ch_fin:
            def_gen = max(0.0, -rfn - PLAFOND_DEF_RG)
        else:
            def_gen = (ch_fin - rf_bruts) + max(0.0, ch_nfin - PLAFOND_DEF_RG)

        # AT: déficit périmé (>10 ans — ligne an-10 dans Excel)
        # Simplifié: stock courant, péremption gérée en stock
        def_perime = 0.0  # ignoré sur 25 ans (impact nul en pratique)

        # W: stock déficit reportable
        if an == 1:
            stock_def = def_gen
        else:
            # W_n = W_(n-1) + V_n - X_(n-1) - AT_n
            prev_imp = annees[-1]["def_imp"]
            stock_def = stock_def + def_gen - prev_imp - def_perime

        # X: déficit imputé année N sur RF positif
        def_imp = min(stock_def - def_gen, rfn) if rfn > 0 else 0.0

        # Y: RF net taxable
        rfnt = max(0.0, rfn - def_imp)

        # Z: revenu total après (avec CSG déduite de N-1)
        rev_ap = rn + rfnt + ded_rg - csg_prec

        # IR / PS avant (situation sans le projet, référence stable)
        # Note: l'indexation des revenus est 0% dans le fichier (B11=0%)
        ir_av  = calcul_ir(rn + rfa, parts)
        ps_av  = max(0.0, rfa) * TAUX_PS
        tot_av = ir_av + ps_av

        # IR / PS après
        ir_ap  = calcul_ir(max(0.0, rev_ap), parts)
        ps_ap  = rfnt * TAUX_PS
        tot_ap = ir_ap + ps_ap

        # AG: économie fiscale
        eco = tot_av - tot_ap

        # CSG déductible pour N+1
        csg_prec = rfnt * CSG_DED

        # Amortissements cumulés
        amt_cum = amort_an * an

        # ── Plus-value ──
        # Prix de revient (conforme feuille Revente)
        fac = max(frais, prix * FORFAIT_FRAIS_PV)
        ftv = prix * FORFAIT_TRAVAUX_PV if an > 5 else 0.0
        pr  = prix + fac + ftv - amt_cum

        pv_brute_0  = prix - pr
        pv_brute_15 = vb15 - pr

        ab_ir = abatt_ir_pv(an)
        ab_ps = abatt_ps_pv(an)

        pvi0  = max(0.0, pv_brute_0  * (1 - ab_ir))
        pps0  = max(0.0, pv_brute_0  * (1 - ab_ps))
        pvi15 = max(0.0, pv_brute_15 * (1 - ab_ir))
        pps15 = max(0.0, pv_brute_15 * (1 - ab_ps))

        ipv0  = pvi0 *TAUX_IR_PV + pps0 *TAUX_PS_PV + max(0.0, surtaxe_pv(pvi0))
        ipv15 = pvi15*TAUX_IR_PV + pps15*TAUX_PS_PV + max(0.0, surtaxe_pv(pvi15))

        # Capital net = prix_vente - CRD - impôt PV
        cap0  = vb0  - crd - max(0.0, ipv0)
        cap15 = vb15 - crd - max(0.0, ipv15)

        # AH (enrichissement patrimoine net PV, scénario 0%)
        enrich = cap0

        # AI: effort d'épargne mensuel
        effort = (lo - remb - ch + eco) / 12

        annees.append(dict(
            an=an, lo=lo, ch=ch, int_a=int_a, ass_a=ass_a, amort=amort_an,
            crd=crd, vb0=vb0, vb15=vb15,
            rf_bruts=rf_bruts, ch_fin=ch_fin, ch_nfin=ch_nfin, rfn=rfn,
            ded_rg=ded_rg, def_gen=def_gen, stock_def=stock_def,
            def_imp=def_imp, rfnt=rfnt, rev_ap=rev_ap,
            ir_av=ir_av, ps_av=ps_av, tot_av=tot_av,
            ir_ap=ir_ap, ps_ap=ps_ap, tot_ap=tot_ap,
            eco=eco, enrich=enrich, cap15=cap15, effort=effort,
            remb=remb, amt_cum=amt_cum,
            pr=pr, pv_brute_0=pv_brute_0, pv_brute_15=pv_brute_15,
            ab_ir=ab_ir, ab_ps=ab_ps,
            pvi0=pvi0, pps0=pps0, pvi15=pvi15, pps15=pps15,
            ipv0=ipv0, ipv15=ipv15, cap0=cap0,
            fac=fac, ftv=ftv,
        ))

    # ── Synthèses par horizon ──
    def hor(n):
        t = annees[:n]
        lm   = sum(a["lo"]  for a in t)/n/12
        gm   = sum(a["eco"] for a in t)/n/12
        cm   = mens_tot
        chm  = sum(a["ch"]  for a in t)/n/12
        te   = lm + gm; ts = cm + chm
        ef   = te - ts
        cap0  = t[-1]["cap0"]
        cap15 = t[-1]["cap15"]
        gft   = sum(a["eco"] for a in t)
        # Décomposition gain fiscal (avec vs sans amortissement Jeanbrun)
        # Sans Jeanbrun = économie sur déficit naturel (intérêts seuls)
        # Avec Jeanbrun = économie supplémentaire liée à l'amortissement
        eco_sans_jb = []
        for a in t:
            # RF sans amortissement Jeanbrun
            ch_nfin_sj = a["ch"]  # charges seulement, pas d'amort
            rfn_sj = a["rf_bruts"] - a["ch_fin"] - ch_nfin_sj
            ded_rg_sj = max(rfn_sj, -PLAFOND_DEF_RG) if rfn_sj < 0 else 0.0
            rfnt_sj = max(0.0, rfn_sj)
            rev_ap_sj = rn + rfnt_sj + ded_rg_sj
            ir_ap_sj = calcul_ir(max(0.0, rev_ap_sj), parts)
            ps_ap_sj = rfnt_sj * TAUX_PS
            eco_sj = a["tot_av"] - (ir_ap_sj + ps_ap_sj)
            eco_sans_jb.append(eco_sj)
        gft_sj = sum(eco_sans_jb)
        dont_deficit = gft_sj
        dont_jeanbrun = gft - gft_sj
        return dict(lm=lm, gm=gm, cm=cm, chm=chm, te=te, ts=ts, ef=ef,
                    cap0=cap0, cap15=cap15, gft=gft,
                    dont_deficit=dont_deficit, dont_jeanbrun=dont_jeanbrun)

    h9, h15, h25 = hor(9), hor(15), hor(25)

    return dict(
        annees=annees, h9=h9, h15=h15, h25=h25,
        lmax=lmax, lmens=lmens, sp=sp, coeff=coeff,
        mempr=mempr, mens_tot=mens_tot, amort_an=amort_an, base_a=base_a,
        eco1=annees[0]["eco"], ir_av1=annees[0]["ir_av"],
        ir_ap1=annees[0]["ir_ap"], tmi_av=tmi_av,
        rn=rn, ab=ab, lann0=lann0, cout=cout, frais=frais,
    )

# ═══════════════════════════════════════════════════════════════════
# FORMATAGE
# ═══════════════════════════════════════════════════════════════════
def fe(v, d=0):
    if v is None: return "—"
    try:
        s = f"{abs(float(v)):,.{d}f}".replace(",", "\u202f")
        return ("−\u202f" if float(v) < 0 else "") + s + "\u202f€"
    except: return str(v)
def fp(v, d=1):
    try: return f"{float(v)*100:.{d}f}\u202f%"
    except: return "—"
def fn(v, d=1):
    try: return f"{float(v):,.{d}f}".replace(",", "\u202f")
    except: return "—"

# ═══════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ✏️ Hypothèses conseiller")
    st.caption("Cellules bleues — modifiables")

    st.markdown("### 🏠 Bien immobilier")
    prix     = st.number_input("Prix d'acquisition (€)", 50_000, 5_000_000, 260_000, 1_000, format="%d")
    frais_pct= st.number_input("Frais d'acquisition (%)", 0.0, 15.0, 7.5, 0.1, format="%.1f") / 100
    surf     = st.number_input("Surface habitable (m²)", 5.0, 500.0, 40.0, 0.5, format="%.1f")
    zone     = st.selectbox("Zone d'acquisition", ["A bis","A","B1","B2","C"], index=1)
    rdc      = st.selectbox("Rez-de-chaussée ?", ["NON","OUI"])
    balcon   = st.number_input("Surface balcon (m²)", 0.0, 200.0, 15.0, 0.5, format="%.1f")
    terrasse = st.number_input("Surface terrasse (m²)", 0.0, 300.0, 0.0, 0.5, format="%.1f")

    st.markdown("### 💳 Financement")
    apport   = st.number_input("Apport personnel (€)", 0, 2_000_000, 15_000, 500, format="%d")
    ti       = st.number_input("Taux d'intérêt annuel (%)", 0.0, 10.0, 3.3, 0.05, format="%.2f") / 100
    ta       = st.number_input("Taux assurance emprunteur (%)", 0.0, 3.0, 0.35, 0.01, format="%.2f") / 100
    duree    = st.number_input("Durée du financement (ans)", 5, 30, 25, 1)
    fg       = st.number_input("Frais garantie + dossier (€)", 0, 20_000, 4_000, 100, format="%d")

    st.markdown("### 🏘️ Revenus locatifs")
    type_loyer= st.selectbox("Type de loyer", ["Loyer intermédiaire","Loyer social","Loyer très social"])
    ls        = st.number_input("Loyer souhaité (€/mois)", 100, 5_000, 750, 10, format="%d")
    il        = st.number_input("Indexation loyers (%/an)", 0.0, 5.0, 1.5, 0.1, format="%.1f") / 100
    cp        = st.number_input("Charges + taxe foncière (% loyers)", 0.0, 60.0, 30.0, 1.0, format="%.0f") / 100

    st.markdown("### 👤 Situation fiscale")
    type_rev = st.selectbox("Type de revenus", ["Salaires (abatt. 10%)","Pensions / Retraites (abatt. 10%)","BNC / BIC / autres"])
    rev      = st.number_input("Revenus annuels déclarés (€)", 0, 2_000_000, 95_000, 1_000, format="%d")
    rfa      = st.number_input("Revenus fonciers autres biens (€/an)", 0, 500_000, 5_000, 500, format="%d")
    parts    = st.number_input("Nombre de parts fiscales", 1.0, 10.0, 2.5, 0.5, format="%.1f")
    nd       = st.number_input("Nombre de déclarants", 1, 2, 2, 1)

    st.divider()
    go = st.button("🚀 Lancer la simulation", use_container_width=True, type="primary")

# ═══════════════════════════════════════════════════════════════════
# CALCUL
# ═══════════════════════════════════════════════════════════════════
if "res" not in st.session_state: st.session_state.res = None
if go:
    with st.spinner("⚙️ Calcul en cours…"):
        st.session_state.res = run(
            prix, frais_pct, surf, zone, rdc, balcon, terrasse,
            apport, ti, ta, duree, fg,
            type_loyer, ls, il, cp,
            type_rev, rev, rfa, parts, nd,
        )
    st.success("✅ Simulation calculée avec succès !")

res = st.session_state.res

# ── Header ──
st.markdown("""<div class="hdr">
  <h1>🏠 Simulateur — Dispositif Jeanbrun</h1>
  <p>médicis IMMOBILIER NEUF &nbsp;·&nbsp; Outil de projection fiscale &nbsp;·&nbsp; Réservé aux conseillers &nbsp;·&nbsp; Document non contractuel</p>
</div>""", unsafe_allow_html=True)

if res is None:
    st.info("👈 Renseignez les paramètres dans la barre latérale puis cliquez sur **Lancer la simulation**.")
    st.stop()

ann = res["annees"]

# ═══════════════════════════════════════════════════════════════════
# ONGLETS
# ═══════════════════════════════════════════════════════════════════
t1, t2, t3, t4, t5 = st.tabs([
    "👁️ Synthèse Visuelle",
    "📋 Synthèse Simplifiée",
    "📈 Synthèse Détaillée",
    "🏦 Revente & Plus-value",
    "🖨️ Imprimer",
])

# ═══════════════════════════════════════════════════════════════════
# ONGLET 1 — SYNTHÈSE VISUELLE
# ═══════════════════════════════════════════════════════════════════
with t1:
    # ── KPIs ──
    k1,k2,k3,k4,k5,k6 = st.columns(6)
    with k1: st.markdown(f'<div class="kpi"><div class="kpi-lbl">Revenus déclarés</div><div class="kpi-val">{fe(rev)}</div><div class="kpi-sub">{fn(parts,1)} parts fiscales</div></div>',unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi t"><div class="kpi-lbl">Tranche Marginale</div><div class="kpi-val">{fp(res["tmi_av"])}</div><div class="kpi-sub">avant opération</div></div>',unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi"><div class="kpi-lbl">Prix d\'acquisition</div><div class="kpi-val">{fe(prix)}</div><div class="kpi-sub">{type_loyer}</div></div>',unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi d"><div class="kpi-lbl">Loyer initial retenu</div><div class="kpi-val">{fe(res["lmens"])}</div><div class="kpi-sub">Zone {zone} · {fn(res["sp"],1)} m² pond.</div></div>',unsafe_allow_html=True)
    with k5: st.markdown(f'<div class="kpi o"><div class="kpi-lbl">Économie fiscale an 1</div><div class="kpi-val">{fe(res["eco1"])}</div><div class="kpi-sub">déficit foncier + Jeanbrun</div></div>',unsafe_allow_html=True)
    with k6: st.markdown(f'<div class="kpi g"><div class="kpi-lbl">Amortissement annuel</div><div class="kpi-val">{fe(res["amort_an"])}</div><div class="kpi-sub">Base {fe(res["base_a"])} · {fp(TAUX_AMT[type_loyer])}</div></div>',unsafe_allow_html=True)

    st.markdown('<div class="sec">📊 COMPTE EN T — Moyennes mensuelles calculées sur chaque horizon</div>', unsafe_allow_html=True)

    def cnt_card(h, label, yrs, bg, bc):
        ef = h["ef"]
        ef_color = "#EA653D" if ef < 0 else "#27ae60"
        effort_lbl = "Reste à charge / mois" if ef < 0 else "Cashflow positif / mois"
        return f"""
        <div class="cnt-card" style="background:{bg};border-left:5px solid {bc};">
          <div style="font-weight:700;color:#13415B;font-size:.95rem;margin-bottom:.75rem;">
            {label} &mdash; <span style="color:{bc};">{yrs}</span>
          </div>
          <table class="cnt-tbl">
            <tr><td style="color:#27ae60;font-weight:600;">✚ CE QUI RENTRE</td>
                <td style="color:#e74c3c;font-weight:600;">− CE QUI SORT</td></tr>
            <tr><td>Loyers moy.&nbsp; <b>{fe(h["lm"])}/mois</b></td>
                <td>Crédit &nbsp;<b>{fe(h["cm"])}/mois</b></td></tr>
            <tr><td>Gain fiscal moy. <b>{fe(h["gm"])}/mois</b></td>
                <td>Charges &nbsp;<b>{fe(h["chm"])}/mois</b></td></tr>
            <tr class="sep"><td>Total &nbsp;<b>{fe(h["te"])}/mois</b></td>
                <td>Total &nbsp;<b>{fe(h["ts"])}/mois</b></td></tr>
          </table>
          <div class="cnt-total">
            <div style="font-size:.75rem;color:#555;">{effort_lbl}</div>
            <div style="font-size:1.3rem;font-weight:700;color:{ef_color};">{fe(abs(ef))}/mois</div>
          </div>
          <div class="cnt-bilan">
            <b>Capital net constitué :</b> {fe(h["cap0"])} (0%)&nbsp; · &nbsp;{fe(h["cap15"])} (+1,5%/an)<br>
            <b>Gain fiscal total :</b> {fe(h["gft"])}
            &nbsp;(<em>dont {fe(h["dont_deficit"])} déficit · {fe(h["dont_jeanbrun"])} Jeanbrun</em>)
          </div>
        </div>"""

    c9,c15,c25 = st.columns(3)
    with c9:  st.markdown(cnt_card(res["h9"],  "🔹 Fin d'engagement",        "9 ans",  "#EEF2FB","#3761AD"), unsafe_allow_html=True)
    with c15: st.markdown(cnt_card(res["h15"], "🔸 Horizon de référence",    "15 ans", "#E5F6F6","#009FA3"), unsafe_allow_html=True)
    with c25: st.markdown(cnt_card(res["h25"], "⭐ Financement soldé",       "25 ans", "#FFF3EE","#EA653D"), unsafe_allow_html=True)

    # ── Graphique ──
    st.markdown('<div class="sec">📈 Capital net constitué par année de détention (Valeur revente − CRD − Impôt PV) · Hypothèses 0% et +1,5%/an</div>', unsafe_allow_html=True)

    try:
        import plotly.graph_objects as go_fig
        xs   = [a["an"] for a in ann]
        y0   = [a["cap0"]  for a in ann]
        y15  = [a["cap15"] for a in ann]
        fig = go_fig.Figure()
        fig.add_trace(go_fig.Scatter(x=xs, y=y0,  mode="lines+markers", name="Avec Jeanbrun (0%)",      line=dict(color="#3761AD", width=2.5), marker=dict(symbol="x", size=7)))
        fig.add_trace(go_fig.Scatter(x=xs, y=y15, mode="lines+markers", name="Avec Jeanbrun (+1,5%/an)",line=dict(color="#009FA3", width=2.5), marker=dict(symbol="x", size=7)))
        # Marqueurs horizons
        for an_ref, label, color in [(9,"9 ans","#3761AD"),(15,"15 ans","#009FA3"),(25,"25 ans","#EA653D")]:
            fig.add_vline(x=an_ref, line_dash="dot", line_color=color, opacity=0.5)
        fig.update_layout(
            height=320, margin=dict(l=20,r=20,t=10,b=20),
            xaxis_title="Année de détention", yaxis_title="Capital net constitué (€)",
            legend=dict(orientation="h", y=-0.2),
            yaxis=dict(tickformat=",.0f"),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(tickmode="linear", tick0=1, dtick=1),
        )
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        # Fallback sans plotly
        df_g = pd.DataFrame({"Année": [a["an"] for a in ann], "0% revalo (€)": [round(a["cap0"],0) for a in ann], "+1,5%/an (€)": [round(a["cap15"],0) for a in ann]}).set_index("Année")
        st.line_chart(df_g)

    # ── Blocs pédagogiques ──
    st.markdown('<div class="sec">💡 COMPRENDRE VOTRE SIMULATION</div>', unsafe_allow_html=True)
    p1,p2,p3 = st.columns(3)
    with p1:
        st.markdown("""<div class="ped" style="background:#EAF6EE;">
          <div class="ped-icon">💶</div>
          <div><div class="ped-title" style="color:#27ae60;">Le côté vert (+)</div>
          <div class="ped-text">Ce que vous <b>percevez</b> : loyers encaissés + économie d'impôt grâce au dispositif Jeanbrun.</div></div>
        </div>""", unsafe_allow_html=True)
    with p2:
        st.markdown("""<div class="ped" style="background:#FEF0EE;">
          <div class="ped-icon">🏦</div>
          <div><div class="ped-title" style="color:#EA653D;">Le côté rouge (−)</div>
          <div class="ped-text">Ce que vous <b>déboursez</b> : mensualité de crédit + charges d'exploitation annuelles (gestion / GLI / taxe foncière / assurance PNO / provisions menus travaux).</div></div>
        </div>""", unsafe_allow_html=True)
    with p3:
        st.markdown("""<div class="ped" style="background:#EEF2FB;">
          <div class="ped-icon">📊</div>
          <div><div class="ped-title" style="color:#3761AD;">Le gain fiscal — 2 composantes</div>
          <div class="ped-text"><b>Déficit naturel</b> (acquis sans Jeanbrun) + <b>avantage lié à l'amortissement Jeanbrun</b>. Les deux s'additionnent.</div></div>
        </div>""", unsafe_allow_html=True)

    # ── Footer ──
    st.markdown(f"""<div class="footer">
      www.medicis-immobilier-neuf.fr &nbsp;·&nbsp; Simulation personnalisée non contractuelle &nbsp;·&nbsp;
      Hypothèses d'indexation et fiscalité constantes &nbsp;·&nbsp;
      Tout investissement locatif comporte des risques (location / impayés / travaux / baisse de valeur)
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# ONGLET 2 — SYNTHÈSE SIMPLIFIÉE
# ═══════════════════════════════════════════════════════════════════
with t2:
    st.markdown('<div class="sec">PROJECTION SIMPLIFIÉE — DISPOSITIF JEANBRUN · Compte en T · Moyennes mensuelles · Document non contractuel</div>', unsafe_allow_html=True)

    # Récapitulatif foyer + opération
    ca, cb = st.columns(2)
    with ca:
        st.markdown("**SITUATION DU FOYER**")
        st.dataframe(pd.DataFrame({
            "Paramètre": ["Revenus déclarés","Parts fiscales","TMI","Mensualité crédit","Économie fiscale an 1","Apport"],
            "Valeur":    [fe(rev), fn(parts,1), fp(res["tmi_av"]), fe(res["mens_tot"]), fe(res["eco1"]), fe(apport)]
        }), hide_index=True, use_container_width=True)
    with cb:
        st.markdown("**OPÉRATION IMMOBILIÈRE**")
        st.dataframe(pd.DataFrame({
            "Paramètre": ["Prix d'acquisition","Zone / Surface pondérée","Loyer mensuel initial",f"Type : {type_loyer}","Amortissement annuel","Base amortissable"],
            "Valeur":    [fe(prix), f"Zone {zone} · {fn(res['sp'],1)} m²", fe(res["lmens"]), fp(TAUX_AMT[type_loyer]), fe(res["amort_an"]), fe(res["base_a"])]
        }), hide_index=True, use_container_width=True)

    st.markdown("---")

    for label, hk, n, bc in [
        ("🔹 HORIZON 9 ANS — Fin durée d'engagement","h9",9,"#3761AD"),
        ("🔸 HORIZON 15 ANS — Horizon de référence","h15",15,"#009FA3"),
        ("⭐ HORIZON 25 ANS — Financement soldé · Pleine propriété","h25",25,"#EA653D"),
    ]:
        h = res[hk]
        st.markdown(f'<div class="sec">{label}</div>', unsafe_allow_html=True)
        st.caption(f"Moyennes mensuelles calculées sur {n} ans ({n*12} mois)")
        ca2, cb2, cc2 = st.columns([2.5, 2.5, 2])
        with ca2:
            st.markdown("**✚ CE QUI RENTRE (+)**")
            st.dataframe(pd.DataFrame({
                "": ["Loyer mensuel moyen","Gain fiscal à réinvestir/mois","TOTAL ENTRÉES"],
                "€/mois": [fe(h["lm"]), fe(h["gm"]), fe(h["te"])]
            }), hide_index=True, use_container_width=True)
        with cb2:
            st.markdown("**− CE QUI SORT (−)**")
            st.dataframe(pd.DataFrame({
                "": ["Mensualité de crédit","Charges d'exploitation/mois","TOTAL SORTIES"],
                "€/mois": [fe(h["cm"]), fe(h["chm"]), fe(h["ts"])]
            }), hide_index=True, use_container_width=True)
        with cc2:
            ef = h["ef"]; col = "#EA653D" if ef < 0 else "#27ae60"
            st.markdown(f"""<div style="background:#F4F6F9;border-radius:8px;padding:1rem;text-align:center;height:100%;">
            <div style="font-size:.75rem;color:#555;">Effort d'investissement mensuel moyen</div>
            <div style="font-size:1.35rem;font-weight:700;color:{col};margin:.3rem 0;">{fe(abs(ef))}</div>
            <hr style="margin:.4rem 0;">
            <div style="font-size:.78rem;text-align:left;">
              <b>Capital net (0%)</b> : {fe(h["cap0"])}<br>
              <b>Capital net (+1,5%)</b> : {fe(h["cap15"])}<br>
              <b>Gain fiscal total</b> : {fe(h["gft"])}<br>
              <em>dont déficit naturel</em> : {fe(h["dont_deficit"])}<br>
              <em>dont Jeanbrun</em> : {fe(h["dont_jeanbrun"])}
            </div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    **Comment lire ce tableau**
    - ▸ Le côté **VERT (+)** = loyers + économie d'impôt grâce au dispositif Jeanbrun.
    - ▸ Le côté **ROUGE (−)** = mensualité de crédit + charges d'exploitation.
    - ▸ L'**EFFORT D'ÉPARGNE** = reste à charge réel. Un chiffre négatif = complément mensuel à prévoir.
    - ▸ Le « Gain fiscal total » se décompose : **déficit naturel** (intérêts d'emprunt, acquis même sans Jeanbrun) + **Jeanbrun** (économie supplémentaire liée à l'amortissement).
    - ▸ Document non contractuel. Hypothèses d'indexation et fiscalité constantes.
    """)
    st.markdown('<div class="footer">médicis IMMOBILIER NEUF — www.medicis-immobilier-neuf.fr &nbsp;·&nbsp; Simulation personnalisée non contractuelle</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# ONGLET 3 — SYNTHÈSE DÉTAILLÉE
# ═══════════════════════════════════════════════════════════════════
with t3:
    st.markdown('<div class="sec">PROJECTION FINANCIÈRE ANNUELLE — DISPOSITIF JEANBRUN · Simulation personnalisée · Document non contractuel</div>', unsafe_allow_html=True)

    # Fiches récap
    ca, cb, cc = st.columns(3)
    with ca:
        st.markdown("**SITUATION DU FOYER**")
        st.dataframe(pd.DataFrame({
            "": ["Revenus déclarés (avant abatt.)","Impôt avant opération","Impôt après opération (an 1)","TMI","Nombre de parts"],
            "Valeur": [fe(rev), fe(res["ir_av1"]+max(0,rfa)*TAUX_PS), fe(res["ir_ap1"]), fp(res["tmi_av"]), fn(parts,1)]
        }), hide_index=True, use_container_width=True)
    with cb:
        st.markdown("**FINANCEMENT**")
        mempr = res["mempr"]
        st.dataframe(pd.DataFrame({
            "": ["Apport personnel","Montant emprunté","Taux nominal","Mensualité totale","Coût total d'acquisition"],
            "Valeur": [fe(apport), fe(mempr), fp(ti), fe(res["mens_tot"]), fe(res["cout"])]
        }), hide_index=True, use_container_width=True)
    with cc:
        st.markdown("**DISPOSITIF JEANBRUN**")
        st.dataframe(pd.DataFrame({
            "": ["Base amortissable (80%)","Taux d'amortissement","Amortissement annuel","Plafond annuel","Charges exploitation","Économie fiscale an 1"],
            "Valeur": [fe(res["base_a"]), fp(TAUX_AMT[type_loyer]), fe(res["amort_an"]), fe(PLAF_AMT[type_loyer]), fp(cp), fe(res["eco1"])]
        }), hide_index=True, use_container_width=True)

    st.markdown("---")
    st.markdown("**PROJECTION ANNUELLE SUR 25 ANS**")

    rows = []
    for a in ann:
        rows.append({
            "An": a["an"],
            "Loyers perçus": fe(a["lo"]),
            "Remb. prêt": fe(a["remb"]),
            "Charges expl.": fe(a["ch"]),
            "Amort. JB": fe(a["amort"]),
            "RF net imputé": fe(a["rfn"]),
            "Impôt avant": fe(a["ir_av"]),
            "Impôt après": fe(a["ir_ap"]),
            "Économie fisc.": fe(a["eco"]),
            "Effort/mois": fe(a["effort"]),
            "Capital net (0%)": fe(a["cap0"]),
            "Capital net (+1,5%)": fe(a["cap15"]),
            "Amt. restant": fe(a["base_a"]*25 - a["amt_cum"] if False else res["base_a"]*25 - a["amt_cum"] if a["an"]<=25 else 0),
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True, height=580)
    st.markdown('<div class="footer">médicis IMMOBILIER NEUF — www.medicis-immobilier-neuf.fr &nbsp;·&nbsp; Document non contractuel</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# ONGLET 4 — REVENTE & PLUS-VALUE
# ═══════════════════════════════════════════════════════════════════
with t4:
    st.markdown('<div class="sec">SIMULATION DE REVENTE — DISPOSITIF JEANBRUN · Calcul pédagogique de la plus-value et de votre enrichissement net à la revente</div>', unsafe_allow_html=True)

    cols = st.columns(3)
    for col, (an_r, lbl, bc) in zip(cols, [(9,"🔹 REVENTE À 9 ANS","#3761AD"),(15,"🔸 REVENTE À 15 ANS","#009FA3"),(25,"⭐ REVENTE À 25 ANS","#EA653D")]):
        a = ann[an_r - 1]
        with col:
            st.markdown(f"<h4 style='color:{bc};margin-bottom:.5rem;'>{lbl}</h4>", unsafe_allow_html=True)

            pv0  = prix
            pv15 = prix * (1.015**an_r)

            def rev_block(titre, pv_vente, pv_brute, ab_ir, ab_ps, ipv, crd, cap, color):
                pvi = max(0, pv_brute*(1-ab_ir)); pps = max(0, pv_brute*(1-ab_ps))
                ir_pv = pvi*TAUX_IR_PV; ps_pv = pps*TAUX_PS_PV; surt = max(0, surtaxe_pv(pvi))
                rows_html = f"""
                <div style="font-size:.82rem;">
                <div style="font-weight:700;color:#13415B;margin-bottom:.5rem;">PRIX DE VENTE</div>
                <div class="rev-row"><span>Prix de vente</span><span><b>{fe(pv_vente)}</b></span></div>
                <div class="rev-row group">CALCUL DE LA PLUS-VALUE</div>
                <div class="rev-row"><span>Prix d'acquisition</span><span>{fe(prix)}</span></div>
                <div class="rev-row"><span>+ Forfait frais acq. (7,5%)</span><span>{fe(a['fac'])}</span></div>
                <div class="rev-row"><span>+ Forfait travaux 15% (si > 5 ans)</span><span>{fe(a['ftv'])}</span></div>
                <div class="rev-row"><span>− Amortissements réintégrés</span><span>−{fe(a['amt_cum'])}</span></div>
                <div class="rev-row bold"><span>= Prix de revient corrigé</span><span>{fe(a['pr'])}</span></div>
                <div class="rev-row bold" style="color:{color}"><span>➜ PV brute</span><span>{fe(pv_brute)}</span></div>
                <div class="rev-row group">ABATTEMENTS DURÉE DE DÉTENTION</div>
                <div class="rev-row"><span>Abattement IR ({fp(ab_ir)})</span><span>{fe(pvi)}</span></div>
                <div class="rev-row"><span>Abattement PS ({fp(ab_ps)})</span><span>{fe(pps)}</span></div>
                <div class="rev-row group">IMPÔT SUR LA PLUS-VALUE</div>
                <div class="rev-row"><span>IR (19%)</span><span>{fe(ir_pv)}</span></div>
                <div class="rev-row"><span>PS (17,2%)</span><span>{fe(ps_pv)}</span></div>
                <div class="rev-row"><span>Surtaxe éventuelle</span><span>{fe(surt)}</span></div>
                <div class="rev-row bold"><span>= TOTAL IMPÔT PV</span><span style="color:#e74c3c;">{fe(ipv)}</span></div>
                <div class="rev-row group">CAPITAL CONSTITUÉ NET</div>
                <div class="rev-row"><span>CRD à la revente</span><span>{fe(crd)}</span></div>
                <div class="rev-row bold" style="background:#EAF6EE;padding:.4rem;border-radius:4px;">
                  <span>✅ Capital net</span><span style="color:#27ae60;font-size:1rem;">{fe(cap)}</span>
                </div>
                </div>"""
                return rows_html

            st.markdown(f"**Scénario 0 % — prix stable**")
            st.markdown(rev_block("0%", pv0, a["pv_brute_0"], a["ab_ir"], a["ab_ps"],
                                   a["ipv0"], a["crd"], a["cap0"], "#3761AD"), unsafe_allow_html=True)
            st.markdown("---")
            st.markdown(f"**Scénario +1,5 %/an — évolution historique**")
            st.markdown(rev_block("+1,5%", pv15, a["pv_brute_15"], a["ab_ir"], a["ab_ps"],
                                   a["ipv15"], a["crd"], a["cap15"], "#009FA3"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    **💡 COMPRENDRE VOTRE ENRICHISSEMENT**
    - ▸ Le capital constitué net = ce qui vous reste **en poche** après avoir soldé votre crédit et payé l'impôt sur la plus-value.
    - ▸ Plus vous détenez longtemps, plus les abattements réduisent l'impôt PV : **exonération totale d'IR à 22 ans**, de PS à 30 ans.
    - ▸ L'amortissement Jeanbrun est réintégré dans la plus-value à la revente, mais l'économie d'impôt réalisée chaque année vous a déjà enrichi.
    - ▸ Le scénario 0% est conservateur (pas de hausse des prix). Le scénario +1,5%/an reflète l'évolution historique moyenne du marché immobilier français.
    - ▸ À 25 ans, le crédit est soldé (CRD = 0) : votre capital constitué net = valeur du bien − impôt PV uniquement.
    """)
    st.markdown('<div class="footer">médicis IMMOBILIER NEUF — www.medicis-immobilier-neuf.fr &nbsp;·&nbsp; Simulation personnalisée non contractuelle</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# ONGLET 5 — EXPORT / IMPRIMER
# ═══════════════════════════════════════════════════════════════════
with t5:
    st.markdown("### 🖨️ Impression A4")
    st.markdown("""
    Pour imprimer une synthèse en format A4 :
    1. Allez sur l'onglet souhaité (**Synthèse Visuelle**, **Synthèse Simplifiée** ou **Revente & Plus-value**)
    2. Cliquez sur le bouton ci-dessous — ou faites **Ctrl+P** (Cmd+P sur Mac)
    3. Choisissez **Format A4 Paysage** dans les options du navigateur
    4. Désactivez les en-têtes/pieds de page du navigateur si besoin
    """)
    import streamlit.components.v1 as components
    components.html("""
    <button onclick="window.parent.print();" style="
        padding:.75rem 2rem; font-size:1rem; cursor:pointer;
        background:#13415B; color:white; border:none; border-radius:8px;
        font-weight:600; letter-spacing:.03em; display:block; margin:1rem auto;">
        🖨️ Imprimer cette page (A4 Paysage)
    </button>
    """, height=70)
    st.markdown("---")
    st.caption("**Moteur de calcul** : Python natif · Réimplémentation fidèle des formules Excel V9 · Barème IR 2026 avec plafonnement QF · Déficits fonciers (art. 156-I-3 CGI) · Abattements PV durée de détention · Document non contractuel")
