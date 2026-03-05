# -*- coding: utf-8 -*-
#
# Simulateur Jeanbrun V11 — médicis Immobilier Neuf
# Moteur Python fidèle à 100 % au modèle Excel V9
# ─────────────────────────────────────────────────
# Corrections et ajouts V11 :
#   ✓ Sidebar : sections visibles via titres HTML inline (plus d'expander cassé)
#   ✓ Graphiques : matplotlib natif (fonctionne sans plotly)
#   ✓ Moteur complet : 49 colonnes Excel reproduites
#       – IR avant variable par année (CSG déductible N-1)
#       – TRI investisseur (si revente) par année
#       – Cash‑flow cumulé avec apport
#       – Enrichissement patrimoine net PV
#       – Effort d'épargne moyen par phase
#       – CSG déductible avant / après
#       – Déficit périmé (> 10 ans)
#       – Stock report amortissement
#   ✓ Synthèse visuelle : graphique capital net intégré
#   ✓ Synthèse détaillée : Bilan global + colonne Amt restant + TOTAL
#   ✓ Charte Médicis 2024 · Impression A4 portrait
#
import streamlit as st
import pandas as pd
import numpy as np
import math
import io
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Simulateur Jeanbrun — médicis",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════
#  CSS  —  CHARTE MÉDICIS 2024  +  PRINT A4 PORTRAIT
# ══════════════════════════════════════════════════════════════════
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

/* ── Variables charte ── */
:root{
  --blue:#3761AD; --dark:#14415C; --ora:#EA653D; --sal:#F57E63;
  --teal:#009FA3; --lime:#E2DE3E; --limed:#9a9b1a;
  --lb:#EEF2FB; --lt:#E4F5F5; --lo:#FEF0EC; --ll:#FAFAD0; --gray:#F4F6F9;
}

/* ── Typographie ── */
*,html,body,[class*="css"],.stApp,button,input,select,textarea
  {font-family:'Poppins',sans-serif!important}

/* ══════ SIDEBAR ══════ */
[data-testid="stSidebar"]{background:var(--dark)!important}
[data-testid="stSidebar"] [data-testid="stSidebarContent"]{background:var(--dark)!important}

/* Tous les textes en blanc */
[data-testid="stSidebar"] *{
  color:#ffffff!important;
  -webkit-text-fill-color:#ffffff!important;
}

/* Inputs : fond blanc, texte sombre */
[data-testid="stSidebar"] input{
  background:#ffffff!important;
  color:#14415C!important;
  -webkit-text-fill-color:#14415C!important;
  caret-color:#14415C!important;
  border:2px solid rgba(255,255,255,.6)!important;
  border-radius:6px!important;
  font-weight:600!important;
}
[data-testid="stSidebar"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-baseweb="base-input"]{
  background:#ffffff!important;
  border-radius:6px!important;
  border:2px solid rgba(255,255,255,.5)!important;
}

/* Selectbox : fond blanc, texte sombre */
[data-testid="stSidebar"] [data-baseweb="select"]>div{
  background:#ffffff!important;
  border:2px solid rgba(255,255,255,.5)!important;
  border-radius:6px!important;
}
[data-testid="stSidebar"] [data-baseweb="select"] *{
  color:#14415C!important;
  -webkit-text-fill-color:#14415C!important;
  background:transparent!important;
  font-weight:600!important;
}
[data-testid="stSidebar"] [data-baseweb="select"]>div>div{
  background:#ffffff!important;
}

/* Labels blanc */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] label *{
  color:#ffffff!important;
  -webkit-text-fill-color:#ffffff!important;
  font-weight:500!important;
}

/* ── Section headers dans sidebar (markdown HTML) ── */
[data-testid="stSidebar"] .sidebar-section{
  background:rgba(255,255,255,.10)!important;
  border:1px solid rgba(255,255,255,.20)!important;
  border-radius:8px!important;
  padding:.55rem .8rem!important;
  margin:.6rem 0 .4rem!important;
  font-weight:700!important;
  font-size:.82rem!important;
  color:#ffffff!important;
  -webkit-text-fill-color:#ffffff!important;
  letter-spacing:.02em;
}

/* ── Expanders (si utilisés — renforcement) ── */
[data-testid="stSidebar"] details{
  background:rgba(255,255,255,.07)!important;
  border:1px solid rgba(255,255,255,.18)!important;
  border-radius:8px!important;
  margin-bottom:.4rem!important;
}
[data-testid="stSidebar"] details summary span,
[data-testid="stSidebar"] details summary p,
[data-testid="stSidebar"] details summary{
  color:#ffffff!important;
  -webkit-text-fill-color:#ffffff!important;
  font-weight:600!important;
  font-size:.82rem!important;
}
[data-testid="stSidebar"] details summary svg{
  fill:#ffffff!important;stroke:#ffffff!important;
}

/* Bouton principal */
[data-testid="stSidebar"] .stButton>button{
  background:var(--ora)!important;color:#fff!important;border:none!important;
  font-weight:700!important;border-radius:8px!important;
  box-shadow:0 4px 12px rgba(234,101,61,.4)!important;
}
[data-testid="stSidebar"] .stButton>button:hover{background:#d4582f!important}
[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.2)!important}

/* ══════ HEADER ══════ */
.hdr{
  background:linear-gradient(135deg,var(--dark) 0%,var(--blue) 100%);
  color:#fff;padding:1rem 1.8rem;border-radius:10px;margin-bottom:.4rem;
  display:flex;align-items:center;gap:1.5rem;
}
.hdr-logo{font-weight:800;font-size:1.6rem;color:#fff;letter-spacing:-.02em;line-height:1}
.hdr-logo em{color:var(--ora);font-style:normal}
.hdr-right{margin-left:auto;text-align:right}
.hdr-title{font-size:1rem;font-weight:600}
.hdr-sub{font-size:.73rem;opacity:.7}

.accent{height:3px;background:linear-gradient(90deg,var(--ora),var(--sal),var(--teal),var(--lime));
  border-radius:2px;margin-bottom:.9rem}

/* ══════ SECTION HEADERS ══════ */
.sec{
  color:#fff;padding:.4rem 1rem;border-radius:6px;font-weight:600;
  margin:1rem 0 .5rem;font-size:.85rem;letter-spacing:.02em;
  background:var(--dark)
}
.sec.blue  {background:var(--blue)}
.sec.teal  {background:var(--teal)}
.sec.ora   {background:var(--ora)}
.sec.sal   {background:var(--sal)}
.sec.sm    {font-size:.75rem;margin:.5rem 0 .3rem;padding:.3rem .8rem}

/* ══════ KPI CARDS ══════ */
.kpi{background:var(--lb);border-left:4px solid var(--blue);border-radius:8px;padding:.8rem 1rem}
.kpi.t{background:var(--lt);border-color:var(--teal)}
.kpi.o{background:var(--lo);border-color:var(--ora)}
.kpi.d{background:#E3EAF0;border-color:var(--dark)}
.kpi.l{background:var(--ll);border-color:var(--limed)}
.kpi-lbl{font-size:.65rem;color:#666;text-transform:uppercase;letter-spacing:.07em;font-weight:600}
.kpi-val{font-size:1.2rem;font-weight:700;color:var(--dark);margin-top:.15rem;line-height:1.2}
.kpi-sub{font-size:.68rem;color:#888;margin-top:.08rem}

/* ══════ COMPTE EN T ══════ */
.cnt{border-radius:9px;padding:1rem 1.1rem;border-top:4px solid var(--blue)}
.cnt-tbl{width:100%;border-collapse:collapse;font-size:.82rem}
.cnt-tbl td{padding:.22rem .25rem}
.cnt-tbl .hd{font-size:.67rem;font-weight:700;text-transform:uppercase;padding-bottom:.28rem;color:#888}
.cnt-tbl .sep{border-top:1.5px solid #ddd;font-weight:700;padding-top:.3rem}
.cnt-tot{text-align:center;margin-top:.5rem;padding:.5rem .6rem;border-radius:6px;background:#fff}
.cnt-bil{background:#fff;border-radius:6px;padding:.5rem .65rem;font-size:.77rem;margin-top:.4rem;line-height:1.75}

/* ══════ PÉDAGOGIE ══════ */
.ped{border-radius:9px;padding:.9rem 1rem;height:100%}
.ped-ico{font-size:1.4rem;margin-bottom:.3rem}
.ped-tit{font-weight:700;margin-bottom:.3rem;font-size:.88rem}
.ped-txt{font-size:.8rem;line-height:1.5}

/* ══════ FOOTER ══════ */
.footer{margin-top:1.5rem;padding:.6rem 0 .2rem;border-top:2px solid var(--ora);
  font-size:.68rem;color:#aaa;text-align:center;font-style:italic}
.footer b{color:var(--blue)}

/* ══════ LOGIN ══════ */
.login-card{background:#fff;border-radius:16px;box-shadow:0 8px 40px rgba(20,65,92,.15);
  padding:2.2rem 2rem;text-align:center;margin-top:4rem}

/* ══════ PRINT A4 PORTRAIT ══════ */
@media print{
  [data-testid="stSidebar"],
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  .stTabs [data-baseweb="tab-list"],
  button,.stDownloadButton,.no-print
    {display:none!important}

  html,body,.stApp{background:#fff!important;margin:0;padding:0}
  .main .block-container{padding:0!important;max-width:100%!important;margin:0!important}
  [data-baseweb="tab-panel"]{display:block!important}

  .hdr{padding:.5rem 1rem!important;border-radius:4px!important;margin-bottom:.3rem!important}
  .hdr-logo{font-size:1.2rem!important}
  .hdr-title{font-size:.85rem!important}
  .accent{margin-bottom:.4rem!important;height:2px!important}
  .sec{padding:.25rem .7rem!important;margin:.4rem 0 .3rem!important;font-size:.72rem!important}
  .kpi{padding:.5rem .7rem!important}
  .kpi-val{font-size:1rem!important}
  .cnt{padding:.7rem .8rem!important}
  .cnt-tbl{font-size:.73rem!important}
  .cnt-bil{font-size:.7rem!important}
  .ped{padding:.6rem .8rem!important}
  .ped-txt{font-size:.72rem!important}
  .footer{margin-top:.5rem!important;padding:.3rem 0!important;font-size:.62rem!important}
  @page{size:A4 portrait;margin:.8cm}
  .hdr,.sec,.kpi,.cnt,.ped
    {-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}
}
</style>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  AUTHENTIFICATION
# ══════════════════════════════════════════════════════════════════
def check_password():
    if st.session_state.get("auth"):
        return True
    _, c, _ = st.columns([1, 1.2, 1])
    with c:
        st.markdown("""<div class="login-card">
        <div style="font-weight:800;font-size:2rem;color:var(--blue,#3761AD);font-family:Poppins,sans-serif;">
          m<span style="color:#EA653D;">é</span>dicis</div>
        <div style="font-size:.62rem;color:#aaa;letter-spacing:.12em;text-transform:uppercase;margin-bottom:.8rem;">
          IMMOBILIER NEUF</div>
        <div style="width:36px;height:3px;background:linear-gradient(90deg,#EA653D,#009FA3);
          border-radius:2px;margin:0 auto .8rem;"></div>
        <h3 style="color:#14415C;margin:.4rem 0 .2rem;font-family:Poppins,sans-serif;">
          Simulateur Jeanbrun</h3>
        <p style="color:#999;font-size:.82rem;margin-bottom:1.3rem;">
          Outil réservé aux conseillers</p>
        </div>""", unsafe_allow_html=True)
        pwd = st.text_input("", type="password", label_visibility="collapsed",
                            placeholder="🔑  Mot de passe conseiller")
        if st.button("Se connecter →", use_container_width=True, type="primary"):
            if pwd == st.secrets.get("password", "jeanbrun2025"):
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect")
    return False


if not check_password():
    st.stop()


# ══════════════════════════════════════════════════════════════════
#  CONSTANTES & BARÈMES
# ══════════════════════════════════════════════════════════════════
PLAFOND_QF = 1759.0
PLAFOND_DEF_RG = 10700.0
CSG_DED = 0.068
TAUX_PS = 0.172
TAUX_IR_PV = 0.19
TAUX_PS_PV = 0.172

BAREME = [
    (0, 11600, 0.00),
    (11600, 29579, 0.11),
    (29579, 84577, 0.30),
    (84577, 181917, 0.41),
    (181917, 9e9, 0.45),
]

PLAFONDS_LOYERS = {
    "A bis": {"Loyer intermédiaire": 19.51, "Loyer social": 15.61, "Loyer très social": 11.71},
    "A":     {"Loyer intermédiaire": 14.49, "Loyer social": 11.59, "Loyer très social":  8.69},
    "B1":    {"Loyer intermédiaire": 11.68, "Loyer social":  9.34, "Loyer très social":  7.01},
    "B2":    {"Loyer intermédiaire": 10.15, "Loyer social":  8.12, "Loyer très social":  6.09},
    "C":     {"Loyer intermédiaire": 10.15, "Loyer social":  8.12, "Loyer très social":  6.09},
}
PLAF_AMT = {"Loyer intermédiaire": 8000, "Loyer social": 10000, "Loyer très social": 12000}
TAUX_AMT = {"Loyer intermédiaire": 0.035, "Loyer social": 0.045, "Loyer très social": 0.055}


# ══════════════════════════════════════════════════════════════════
#  FONCTIONS FISCALES
# ══════════════════════════════════════════════════════════════════
def ir_brut(qf):
    """IR brut pour un quotient familial donné."""
    t = 0.0
    for inf, sup, tx in BAREME:
        if qf <= inf:
            break
        t += (min(qf, sup) - inf) * tx
    return t


def calcul_ir(rev, parts):
    """IR net après plafonnement du quotient familial."""
    if rev <= 0:
        return 0.0
    it = ir_brut(rev / parts) * parts
    pr = 2.0 if parts >= 2.0 else 1.0
    ir = ir_brut(rev / pr) * pr
    ds = max(0.0, (parts - pr) * 2)
    return max(0.0, max(it, ir - ds * PLAFOND_QF))


def get_tmi(rev, parts):
    """Tranche marginale d'imposition."""
    qf = rev / parts if parts > 0 else 0
    for inf, sup, tx in BAREME:
        if qf <= sup:
            return tx
    return 0.45


def taux_moyen(rev, parts):
    """Taux moyen d'imposition."""
    if rev <= 0:
        return 0.0
    return calcul_ir(rev, parts) / rev


def abatt10(rev, nd, typ):
    """Abattement 10 % salaires/pensions — plafonné et plancher."""
    if "Salaires" in typ:
        return max(504.0 * nd, min(rev * 0.10, 14171.0 * nd))
    if "Pensions" in typ:
        return max(442.0 * nd, min(rev * 0.10, 4321.0 * nd))
    return 0.0


def abatt_ir_pv(n):
    """Abattement IR sur plus‑value immobilière — durée de détention."""
    if n < 6:
        return 0.0
    if n < 22:
        return (n - 5) * 0.06
    return 1.0


def abatt_ps_pv(n):
    """Abattement PS sur plus‑value immobilière — durée de détention."""
    if n < 6:
        return 0.0
    if n < 22:
        return (n - 5) * 0.0165
    if n == 22:
        return 16 * 0.0165 + 0.016
    if n < 30:
        return 16 * 0.0165 + 0.016 + (n - 22) * 0.09
    return 1.0


def surtaxe(pv):
    """Surtaxe sur PV > 50 000 € — barème progressif art. 1609 nonies G CGI."""
    if pv <= 50000:  return 0.0
    if pv <= 60000:  return pv * 0.02 - (60000 - pv) * 0.05
    if pv <= 100000: return pv * 0.02
    if pv <= 110000: return pv * 0.03 - (110000 - pv) * 0.10
    if pv <= 150000: return pv * 0.03
    if pv <= 160000: return pv * 0.04 - (160000 - pv) * 0.15
    if pv <= 200000: return pv * 0.04
    if pv <= 210000: return pv * 0.05 - (210000 - pv) * 0.20
    if pv <= 250000: return pv * 0.05
    if pv <= 260000: return pv * 0.06 - (260000 - pv) * 0.25
    return pv * 0.06


def amort_tab(capital, taux_an, duree_an):
    """Tableau d'amortissement financier mensuel puis agrégé annuel."""
    r = taux_an / 12
    n = duree_an * 12
    mens = capital * r * (1 + r) ** n / ((1 + r) ** n - 1) if r > 0 else capital / n
    rows_m = []
    crd = capital
    for m in range(1, n + 1):
        im = crd * r
        pm = mens - im
        crd = max(0.0, crd - pm)
        rows_m.append({"mois": m, "im": im, "pm": pm, "crd": crd})
    tab = []
    for an in range(duree_an):
        b = rows_m[an * 12:(an + 1) * 12]
        tab.append({
            "int": sum(x["im"] for x in b),
            "princ": sum(x["pm"] for x in b),
            "crd": max(0.0, b[-1]["crd"]),
        })
    return mens, tab, rows_m


def compute_irr(cashflows, guess=0.05, tol=1e-8, maxiter=200):
    """Calcul du TRI (taux de rentabilité interne) par Newton‑Raphson."""
    r = guess
    for _ in range(maxiter):
        npv = sum(cf / (1 + r) ** t for t, cf in enumerate(cashflows))
        dnpv = sum(-t * cf / (1 + r) ** (t + 1) for t, cf in enumerate(cashflows))
        if abs(dnpv) < 1e-14:
            return None
        r_new = r - npv / dnpv
        if abs(r_new - r) < tol:
            return r_new
        r = r_new
    return r if abs(sum(cf / (1 + r) ** t for t, cf in enumerate(cashflows))) < 1.0 else None


# ══════════════════════════════════════════════════════════════════
#  MOTEUR PRINCIPAL — COMPLET (49 colonnes Excel V9)
# ══════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def run(prix, frais_pct, surf, zone, rdc, balcon, terrasse,
        apport, ti, ta, duree, fg,
        type_loyer, ls, il, cp,
        type_rev, rev, rfa, parts, nd,
        duree_engagement=9):

    frais = prix * frais_pct
    cout = prix + frais

    # Surface pondérée — art. 2 terdecies D ann. III CGI
    sp = (surf + min(balcon, 16.0) / 2) if rdc == "OUI" else \
         (surf + min(balcon + terrasse, 16.0) / 2)
    coeff = math.trunc(min(0.7 + 19.0 / sp, 1.2) * 100) / 100 if sp > 0 else 1.2
    plm2 = PLAFONDS_LOYERS.get(zone, PLAFONDS_LOYERS["A"]).get(type_loyer, 14.49)
    lmax = plm2 * sp * coeff
    lmens = min(ls, lmax)
    lann0 = lmens * 12

    # Financement
    mempr = cout - apport
    mens, amttab, rows_m = amort_tab(mempr, ti, duree)
    ass_m = mempr * ta / 12
    mens_tot = mens + ass_m
    remb_an = (mens + ass_m) * 12   # remboursement annuel total

    # Amortissement Jeanbrun
    base_a = prix * 0.80
    amort_an = min(PLAF_AMT[type_loyer], base_a * TAUX_AMT[type_loyer])

    # Fiscal de référence (statique)
    ab = abatt10(rev, nd, type_rev)
    rn = rev - ab

    # ────────────────────────────────────────
    #  BOUCLE 25 ANS — toutes colonnes Excel
    # ────────────────────────────────────────
    annees = []
    stock_def = 0.0
    csg_ded_ap_prev = 0.0     # CSG déductible (après) de N-1
    csg_ded_av_prev = 0.0     # CSG déductible (avant) de N-1
    cashflow_cum = 0.0

    for an in range(1, 26):
        i = an - 1

        # ── Loyers et charges
        lo = lann0 * (1 + il) ** i
        ch = lo * cp

        # ── Crédit
        if i < len(amttab):
            int_a = amttab[i]["int"]
            crd = amttab[i]["crd"]
            remb = remb_an
        else:
            int_a = crd = remb = 0.0
        ass_a_yr = (ass_m * 12) if i < len(amttab) else 0.0

        # ── Amortissement Jeanbrun (limité à la durée d'engagement)
        amort_yr = amort_an if an <= duree_engagement else 0.0
        amt_cum = amort_an * min(an, duree_engagement)
        stock_rpt_amt = max(0.0, an * base_a * TAUX_AMT[type_loyer] - amt_cum)

        # ── AVANT OPÉRATION (variable chaque année via CSG déductible)
        rev_total_avant = rn + rfa - csg_ded_av_prev
        qf_avant = rev_total_avant / parts if parts > 0 else 0
        tmi_avant = get_tmi(max(0, rev_total_avant), parts)
        tx_moy_avant = taux_moyen(max(0, rev_total_avant), parts)
        ir_avant = calcul_ir(max(0, rev_total_avant), parts)
        ps_avant = max(0.0, rfa) * TAUX_PS
        tot_avant = ir_avant + ps_avant
        csg_ded_av_N = max(0.0, rfa) * CSG_DED

        # ── Revenus fonciers
        rf_b = lo + rfa                          # RF bruts globaux
        ch_f = int_a + ass_a_yr + (fg if an == 1 else 0.0)  # charges financières
        ch_nf = ch + amort_yr                    # charges non-financières (+ amort.)
        rfn = rf_b - ch_f - ch_nf                # RF net global

        # ── Déficit foncier — art. 156-I-3 CGI
        if rfn >= 0:
            ded = 0.0
            def_g = 0.0
        elif rf_b >= ch_f:
            ded = max(rfn, -PLAFOND_DEF_RG)
            def_g = max(0.0, -rfn - PLAFOND_DEF_RG)
        else:
            ded = max(-ch_nf, -PLAFOND_DEF_RG)
            def_g = (ch_f - rf_b) + max(0.0, ch_nf - PLAFOND_DEF_RG)

        # Déficit périmé (> 10 ans)
        def_perime = annees[an - 11]["def_g"] if an > 10 else 0.0

        prev_imp = annees[-1]["def_imp"] if an > 1 else 0.0
        stock_def = stock_def + def_g - prev_imp - def_perime
        def_imp = min(stock_def, rfn) if rfn > 0 else 0.0
        rfnt = max(0.0, rfn - def_imp)

        # ── APRÈS OPÉRATION
        rev_ap = rn + rfnt + ded - csg_ded_ap_prev
        qf_apres = rev_ap / parts if parts > 0 else 0
        tmi_apres = get_tmi(max(0, rev_ap), parts)
        tx_moy_apres = taux_moyen(max(0, rev_ap), parts)
        ir_ap = calcul_ir(max(0.0, rev_ap), parts)
        ps_ap = rfnt * TAUX_PS
        tot_ap = ir_ap + ps_ap
        eco = tot_avant - tot_ap
        csg_ded_ap_N = rfnt * CSG_DED

        # ── Plus-value (scénario 0 % et +1,5 %/an)
        vb15 = prix * (1.015) ** an
        fac = max(frais, prix * 0.075)
        ftv = prix * 0.15 if an > 5 else 0.0
        pr = prix + fac + ftv - amt_cum

        pv0 = prix - pr
        pv15 = vb15 - pr
        ai = abatt_ir_pv(an)
        ap = abatt_ps_pv(an)

        pvi0 = max(0.0, pv0 * (1 - ai))
        pps0 = max(0.0, pv0 * (1 - ap))
        pvi15 = max(0.0, pv15 * (1 - ai))
        pps15 = max(0.0, pv15 * (1 - ap))

        ipv0 = pvi0 * TAUX_IR_PV + pps0 * TAUX_PS_PV + max(0.0, surtaxe(pvi0))
        ipv15 = pvi15 * TAUX_IR_PV + pps15 * TAUX_PS_PV + max(0.0, surtaxe(pvi15))

        cap0 = prix - crd - max(0.0, ipv0)
        cap15 = vb15 - crd - max(0.0, ipv15)

        # ── Effort d'épargne mensuel et enrichissement
        effort = (lo - remb - ch + eco) / 12
        enrichissement = prix - crd - max(0.0, ipv0)  # = cap0
        cashflow_cum = cashflow_cum + effort * 12 if an > 1 else (-apport + effort * 12)

        # ── TRI investisseur (si revente à l'année N)
        cf_list = [-apport]
        for k in range(an):
            a_k = annees[k] if k < len(annees) else None
            if k < an - 1:
                # Année intermédiaire : cash flow opérationnel
                if a_k is not None:
                    cf_list.append(a_k["lo"] - a_k["remb"] - a_k["ch"] + a_k["eco"])
                else:
                    cf_list.append(lo - remb - ch + eco)
            else:
                # Dernière année : opérationnel + capital net
                cf_list.append(lo - remb - ch + eco + cap0)
        tri = compute_irr(cf_list)

        # ── Stocker pour N+1
        csg_ded_av_prev = csg_ded_av_N
        csg_ded_ap_prev = csg_ded_ap_N

        annees.append(dict(
            an=an, lo=lo, ch=ch, int_a=int_a, ass_a=ass_a_yr,
            amort_yr=amort_yr, amort_an=amort_an, amt_cum=amt_cum,
            crd=crd, vb15=vb15, remb=remb,
            # Avant opération
            rev_total_avant=rev_total_avant, qf_avant=qf_avant,
            tmi_avant=tmi_avant, tx_moy_avant=tx_moy_avant,
            ir_av=ir_avant, ps_av=ps_avant, tot_av=tot_avant,
            csg_ded_av=csg_ded_av_N,
            # Revenus fonciers
            rf_b=rf_b, ch_f=ch_f, ch_nf=ch_nf, rfn=rfn,
            ded=ded, def_g=def_g, stock_def=stock_def,
            def_imp=def_imp, def_perime=def_perime,
            rfnt=rfnt,
            # Après opération
            rev_ap=rev_ap, qf_apres=qf_apres,
            tmi_apres=tmi_apres, tx_moy_apres=tx_moy_apres,
            ir_ap=ir_ap, ps_ap=ps_ap, tot_ap=tot_ap,
            eco=eco, csg_ded_ap=csg_ded_ap_N,
            # Patrimoine
            cap0=cap0, cap15=cap15, effort=effort,
            enrichissement=enrichissement,
            cashflow_cum=cashflow_cum,
            stock_rpt_amt=stock_rpt_amt,
            # Plus-value
            pr=pr, pv0=pv0, pv15=pv15,
            ai=ai, ap=ap,
            pvi0=pvi0, pps0=pps0, pvi15=pvi15, pps15=pps15,
            ipv0=ipv0, ipv15=ipv15,
            fac=fac, ftv=ftv,
            # TRI
            tri=tri,
        ))

    # ── Agrégats par horizon
    def hor(n):
        t = annees[:n]
        lm = sum(a["lo"] for a in t) / n / 12
        gm = sum(a["eco"] for a in t) / n / 12
        cm = mens_tot
        chm = sum(a["ch"] for a in t) / n / 12
        gft = sum(a["eco"] for a in t)
        # Décomposition : sans Jeanbrun
        esj = []
        for a in t:
            rfn_sj = a["rf_b"] - a["ch_f"] - a["ch"]
            ded_sj = max(rfn_sj, -PLAFOND_DEF_RG) if rfn_sj < 0 else 0.0
            rfnt_sj = max(0.0, rfn_sj)
            ir_sj = calcul_ir(max(0.0, rn + rfnt_sj + ded_sj), parts)
            ps_sj = rfnt_sj * TAUX_PS
            esj.append(a["tot_av"] - (ir_sj + ps_sj))
        dont_d = sum(esj)
        dont_j = gft - dont_d
        return dict(lm=lm, gm=gm, cm=cm, chm=chm,
                    te=lm + gm, ts=cm + chm, ef=(lm + gm) - (cm + chm),
                    cap0=t[-1]["cap0"], cap15=t[-1]["cap15"],
                    gft=gft, dont_d=dont_d, dont_j=dont_j)

    h9, h15, h25 = hor(9), hor(15), hor(25)

    # Effort moyen par phase (Excel col 36)
    effort_moy_9 = sum(a["effort"] for a in annees[:9]) / 9
    effort_moy_post = sum(a["effort"] for a in annees[9:]) / 16 if len(annees) > 9 else 0

    return dict(
        annees=annees, h9=h9, h15=h15, h25=h25,
        lmax=lmax, lmens=lmens, sp=sp, coeff=coeff,
        mempr=mempr, mens_tot=mens_tot, amort_an=amort_an, base_a=base_a,
        eco1=annees[0]["eco"],
        ir_ref=annees[0]["ir_av"], ps_ref=annees[0]["ps_av"],
        tot_ref=annees[0]["tot_av"],
        ir_ap1=annees[0]["ir_ap"],
        tmi_v=annees[0]["tmi_avant"],
        rn=rn, ab=ab, lann0=lann0, cout=cout,
        amttab=amttab, rows_m=rows_m,
        effort_moy_9=effort_moy_9, effort_moy_post=effort_moy_post,
    )


# ══════════════════════════════════════════════════════════════════
#  FORMATAGE
# ══════════════════════════════════════════════════════════════════
def fe(v, d=0):
    if v is None:
        return "—"
    try:
        s = f"{abs(float(v)):,.{d}f}".replace(",", "\u202f")
        return ("−\u202f" if float(v) < 0 else "") + s + "\u202f€"
    except Exception:
        return str(v)


def fp(v, d=1):
    try:
        return f"{float(v) * 100:.{d}f}\u202f%"
    except Exception:
        return "—"


def fn(v, d=1):
    try:
        return f"{float(v):,.{d}f}".replace(",", "\u202f")
    except Exception:
        return "—"


# ══════════════════════════════════════════════════════════════════
#  SIDEBAR  —  Titres de section en HTML inline (anti‑bug)
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""<div style="text-align:center;padding:.4rem 0 .6rem">
      <div style="font-weight:800;font-size:1.45rem;color:#fff;font-family:Poppins,sans-serif;letter-spacing:-.02em">
        m<span style="color:#EA653D">é</span>dicis</div>
      <div style="font-size:.58rem;letter-spacing:.12em;opacity:.55;color:#fff;margin-top:.1rem">IMMOBILIER NEUF</div>
      <div style="height:2px;background:linear-gradient(90deg,#EA653D,#009FA3);border-radius:2px;margin:.4rem 0"></div>
    </div>""", unsafe_allow_html=True)

    # ── SECTION 1 : Bien immobilier ──
    st.markdown('<div class="sidebar-section">🏠 BIEN IMMOBILIER</div>', unsafe_allow_html=True)
    prix      = st.number_input("Prix d'acquisition (€)", 50_000, 5_000_000, 260_000, 1_000, format="%d")
    frais_pct = st.number_input("Frais d'acquisition (%)", 0.0, 15.0, 3.0, 0.1, format="%.1f") / 100
    surf      = st.number_input("Surface habitable (m²)", 5.0, 500.0, 40.0, 0.5, format="%.1f")
    zone      = st.selectbox("Zone Jeanbrun", ["A bis", "A", "B1", "B2", "C"], index=1)
    rdc       = st.selectbox("Rez-de-chaussée ?", ["NON", "OUI"])
    balcon    = st.number_input("Surface balcon (m²)", 0.0, 200.0, 15.0, 0.5, format="%.1f")
    terrasse  = st.number_input("Surface terrasse (m²)", 0.0, 300.0, 0.0, 0.5, format="%.1f")

    # ── SECTION 2 : Financement ──
    st.markdown('<div class="sidebar-section">💳 FINANCEMENT</div>', unsafe_allow_html=True)
    apport = st.number_input("Apport (€)", 0, 2_000_000, 15_000, 500, format="%d")
    ti     = st.number_input("Taux intérêt (%/an)", 0.0, 10.0, 3.3, 0.05, format="%.2f") / 100
    ta     = st.number_input("Taux assurance (%/an)", 0.0, 3.0, 0.35, 0.01, format="%.2f") / 100
    duree  = st.number_input("Durée crédit (ans)", 5, 30, 25, 1)
    fg     = st.number_input("Frais garantie + dossier (€)", 0, 20_000, 4_000, 100, format="%d")

    # ── SECTION 3 : Revenus locatifs ──
    st.markdown('<div class="sidebar-section">🏘️ REVENUS LOCATIFS</div>', unsafe_allow_html=True)
    type_loyer = st.selectbox("Type de loyer", ["Loyer intermédiaire", "Loyer social", "Loyer très social"])
    ls         = st.number_input("Loyer souhaité (€/mois)", 100, 5_000, 750, 10, format="%d")
    il         = st.number_input("Indexation loyers (%/an)", 0.0, 5.0, 1.5, 0.1, format="%.1f") / 100
    cp         = st.number_input("Charges + TF (% loyers bruts)", 0.0, 60.0, 30.0, 1.0, format="%.0f") / 100
    duree_amort = st.number_input("Durée amortissement JB (ans)", 1, 25, 25, 1,
                                   help="25 ans = modèle Excel V9. Engagement initial = 9 ans.")

    # ── SECTION 4 : Situation fiscale ──
    st.markdown('<div class="sidebar-section">👤 SITUATION FISCALE</div>', unsafe_allow_html=True)
    type_rev = st.selectbox("Type de revenus principaux",
        ["Salaires (abatt. 10%)", "Pensions / Retraites (abatt. 10%)", "BNC / BIC / autres"])
    rev   = st.number_input("Revenus déclarés (€/an)", 0, 2_000_000, 95_000, 1_000, format="%d")
    rfa   = st.number_input("RF autres biens (€/an)", 0, 500_000, 5_000, 500, format="%d")
    parts = st.number_input("Parts fiscales", 1.0, 10.0, 2.5, 0.5, format="%.1f")
    nd    = st.number_input("Nb déclarants", 1, 2, 2, 1)

    st.divider()
    go = st.button("🚀 Lancer la simulation", use_container_width=True, type="primary")


# ── Calcul
if "res" not in st.session_state:
    st.session_state.res = None
if go:
    with st.spinner("⚙️ Calcul en cours…"):
        st.session_state.res = run(
            prix, frais_pct, surf, zone, rdc, balcon, terrasse,
            apport, ti, ta, duree, fg,
            type_loyer, ls, il, cp, type_rev, rev, rfa, parts, nd,
            duree_engagement=duree_amort,
        )
res = st.session_state.res

# ── Header
st.markdown(f"""<div class="hdr">
  <div>
    <div class="hdr-logo">m<em>é</em>dicis
      <span style="font-size:.72rem;font-weight:400;opacity:.65;letter-spacing:.09em">IMMOBILIER NEUF</span></div>
    <div class="hdr-sub">Outil réservé aux conseillers · Document non contractuel</div>
  </div>
  <div class="hdr-right">
    <div class="hdr-title">Simulateur — Dispositif Jeanbrun V11</div>
    <div class="hdr-sub">Barème IR 2026 · Art. 156-I-3 CGI · Art. 2 quindecies B · Art. 2 terdecies D</div>
  </div>
</div><div class="accent"></div>""", unsafe_allow_html=True)

if res is None:
    st.info("👈 Renseignez les paramètres dans la barre latérale puis cliquez sur **Lancer la simulation**.")
    st.stop()

ann = res["annees"]


# ══════════════════════════════════════════════════════════════════
#  GRAPHIQUES — MATPLOTLIB (toujours disponible)
# ══════════════════════════════════════════════════════════════════
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

COLORS = {"blue": "#3761AD", "teal": "#009FA3", "ora": "#EA653D",
          "dark": "#14415C", "sal": "#F57E63", "lime": "#9a9b1a"}


def fig_capital_net(ann_data, title="Capital net constitué par année de détention"):
    """Graphique capital net (0 % et +1,5 %) avec lignes verticales aux horizons."""
    fig, ax = plt.subplots(figsize=(10, 3.2), dpi=100)
    xs = [a["an"] for a in ann_data]
    ax.plot(xs, [a["cap0"] for a in ann_data], "-o", color=COLORS["blue"],
            linewidth=2, markersize=3.5, label="0 % (prix stable)")
    ax.plot(xs, [a["cap15"] for a in ann_data], "-o", color=COLORS["teal"],
            linewidth=2, markersize=3.5, label="+1,5 %/an")
    for vx, lbl, vc in [(9, "9 ans", COLORS["blue"]),
                         (15, "15 ans", COLORS["teal"]),
                         (25, "25 ans", COLORS["ora"])]:
        ax.axvline(vx, ls="--", color=vc, alpha=.45, lw=1)
        ax.text(vx + .3, ax.get_ylim()[1] * .92 if ax.get_ylim()[1] > 0 else 0,
                lbl, fontsize=8, color=vc, fontweight="bold")
    ax.axhline(0, ls="--", color="#ddd", lw=.8)
    ax.set_xlabel("Année", fontsize=9)
    ax.set_ylabel("€", fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", "\u202f")))
    ax.set_xticks(range(1, 26, 2))
    ax.legend(loc="upper left", fontsize=8, framealpha=.8)
    ax.set_title(title, fontsize=10, fontweight="bold", color=COLORS["dark"])
    ax.grid(axis="y", alpha=.25)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    fig.tight_layout()
    return fig


def fig_amort_pret(amttab_data, mempr, ta):
    """Graphique amortissement du prêt (stacked bar + CRD)."""
    fig, ax1 = plt.subplots(figsize=(10, 2.8), dpi=100)
    xs = list(range(1, len(amttab_data) + 1))
    ints = [r["int"] for r in amttab_data]
    princs = [r["princ"] for r in amttab_data]
    crds = [r["crd"] for r in amttab_data]
    ax1.bar(xs, ints, color=COLORS["ora"], alpha=.85, label="Intérêts")
    ax1.bar(xs, princs, bottom=ints, color=COLORS["blue"], alpha=.85, label="Capital")
    ax1.set_ylabel("€/an", fontsize=9)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", "\u202f")))
    ax2 = ax1.twinx()
    ax2.plot(xs, crds, color=COLORS["teal"], lw=2.5, label="CRD €")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", "\u202f")))
    ax2.set_ylabel("CRD (€)", fontsize=9)
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8, framealpha=.8)
    ax1.set_xlabel("Année", fontsize=9)
    ax1.set_title("Amortissement du prêt", fontsize=10, fontweight="bold", color=COLORS["dark"])
    fig.patch.set_facecolor("white")
    ax1.set_facecolor("white")
    fig.tight_layout()
    return fig


def fig_effort_eco(ann_data):
    """Graphique effort mensuel + économie fiscale par année."""
    fig, ax = plt.subplots(figsize=(10, 3), dpi=100)
    xs = [a["an"] for a in ann_data]
    efforts = [a["effort"] for a in ann_data]
    ecos = [a["eco"] / 12 for a in ann_data]
    ax.bar(xs, ecos, color=COLORS["teal"], alpha=.75, label="Éco. fiscale/mois")
    ax.plot(xs, efforts, "-o", color=COLORS["ora"], lw=2, markersize=3, label="Effort/mois")
    ax.axhline(0, ls="--", color="#ddd", lw=.8)
    ax.set_xlabel("Année", fontsize=9)
    ax.set_ylabel("€/mois", fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", "\u202f")))
    ax.legend(fontsize=8, framealpha=.8)
    ax.set_title("Effort mensuel et économie fiscale", fontsize=10, fontweight="bold", color=COLORS["dark"])
    ax.grid(axis="y", alpha=.25)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    fig.tight_layout()
    return fig


# ══════════════════════════════════════════════════════════════════
#  ONGLETS
# ══════════════════════════════════════════════════════════════════
t1, t2, t3, t4, t5, t6, t7, t8, t9, t10 = st.tabs([
    "👁️ Synthèse visuelle",
    "📋 Synthèse simplifiée",
    "📈 Synthèse détaillée",
    "🏦 Revente & Plus-value",
    "⚙️ Moteur",
    "📐 Règles fiscales",
    "🏘️ Plafonds loyers",
    "📊 Barème fiscal",
    "💰 Tableau d'amortissement",
    "🖨️ Imprimer",
])


# ─────────────────────────────────────────────────────────────────
# ONGLET 1 — SYNTHÈSE VISUELLE
# ─────────────────────────────────────────────────────────────────
with t1:
    st.markdown('<div class="sec">▸ DISPOSITIF JEANBRUN — Projection simplifiée · Simulation personnalisée</div>', unsafe_allow_html=True)

    # ── KPI Cards
    kpis = [
        ("REVENUS DÉCLARÉS", fe(rev), f"{fn(parts,1)} parts fiscales", ""),
        ("TRANCHE MARGINALE", fp(res["tmi_v"]), f"Taux moy. {fp(ann[0]['tx_moy_avant'])}", "t"),
        ("PRIX D'ACQUISITION", fe(prix), f"{type_loyer}", "o"),
        ("LOYER INITIAL", fe(res["lmens"]), f"/ mois retenu", "d"),
        ("SURFACE / ZONE", f"{fn(res['sp'],1)} m²  ·  Zone {zone}", f"Coeff. {fn(res['coeff'],2)}", "l"),
        ("ÉCONOMIE FISCALE AN 1", fe(res["eco1"]), f"TMI après {fp(ann[0]['tmi_apres'])}", "t"),
    ]
    cols_k = st.columns(6)
    for col, (lbl, val, sub, cls) in zip(cols_k, kpis):
        with col:
            st.markdown(f'<div class="kpi {cls}"><div class="kpi-lbl">{lbl}</div>'
                        f'<div class="kpi-val">{val}</div>'
                        f'<div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

    # ── Comptes en T
    st.markdown('<div class="sec">📊 COMPTE EN T — Moyennes mensuelles calculées sur chaque horizon</div>', unsafe_allow_html=True)

    def cnt_html(h, label, yrs, bg, bc, icon):
        ef = h["ef"]
        ec = "#EA653D" if ef < 0 else "#009FA3"
        le = "Reste à charge / mois" if ef < 0 else "Cashflow positif / mois"
        return f"""<div class="cnt" style="background:{bg};border-top-color:{bc}">
          <div style="font-weight:700;color:#14415C;font-size:.88rem;margin-bottom:.6rem">
            {icon} {label} — <span style="color:{bc}">{yrs}</span></div>
          <table class="cnt-tbl">
            <tr><td class="hd" style="color:#009FA3">✚ CE QUI RENTRE</td>
                <td class="hd" style="color:#EA653D">− CE QUI SORT</td></tr>
            <tr><td>Loyers moy. <b>{fe(h['lm'])}</b></td><td>Crédit <b>{fe(h['cm'])}</b></td></tr>
            <tr><td>Gain fiscal moy. <b>{fe(h['gm'])}</b></td><td>Charges <b>{fe(h['chm'])}</b></td></tr>
            <tr class="sep"><td>Total <b>{fe(h['te'])}</b></td><td>Total <b>{fe(h['ts'])}</b></td></tr>
          </table>
          <div class="cnt-tot"><div style="font-size:.64rem;color:#888;text-transform:uppercase;letter-spacing:.06em">{le}</div>
            <div style="font-size:1.2rem;font-weight:800;color:{ec}">{fe(abs(ef))}/mois</div></div>
          <div class="cnt-bil">
            <b>Capital net (0%)</b> : {fe(h['cap0'])} · <b>(+1,5%)</b> : {fe(h['cap15'])}<br>
            <b>Gain fiscal total</b> : {fe(h['gft'])}<br>
            <span style="color:#888"><em>dont déficit naturel</em> : {fe(h['dont_d'])}</span><br>
            <span style="color:#3761AD"><em>dont Jeanbrun</em> : {fe(h['dont_j'])}</span>
          </div></div>"""

    c9, c15, c25 = st.columns(3)
    with c9:
        st.markdown(cnt_html(res["h9"], "Fin d'engagement", "9 ans", "#EEF2FB", "#3761AD", "🔹"), unsafe_allow_html=True)
    with c15:
        st.markdown(cnt_html(res["h15"], "Horizon de référence", "15 ans", "#E4F5F5", "#009FA3", "🔸"), unsafe_allow_html=True)
    with c25:
        st.markdown(cnt_html(res["h25"], "Financement soldé", "25 ans", "#FEF0EC", "#EA653D", "⭐"), unsafe_allow_html=True)

    # ── Graphique capital net — MATPLOTLIB (toujours rendu)
    st.markdown('<div class="sec no-print">📈 Capital net par année — 0% et +1,5%/an</div>', unsafe_allow_html=True)
    st.pyplot(fig_capital_net(ann))

    # ── Pédagogie
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown("""<div class="ped" style="background:#EAF6EE">
      <div class="ped-ico">💶</div><div class="ped-tit" style="color:#009FA3">Le côté vert (+)</div>
      <div class="ped-txt">Loyers encaissés + économie d'impôt Jeanbrun. Ces flux réduisent votre effort mensuel.</div>
      </div>""", unsafe_allow_html=True)
    with p2:
        st.markdown("""<div class="ped" style="background:#FEF0EC">
      <div class="ped-ico">🏦</div><div class="ped-tit" style="color:#EA653D">Le côté rouge (−)</div>
      <div class="ped-txt">Mensualité de crédit + charges d'exploitation (gestion, GLI, taxe foncière, PNO, travaux).</div>
      </div>""", unsafe_allow_html=True)
    with p3:
        st.markdown("""<div class="ped" style="background:#EEF2FB">
      <div class="ped-ico">📊</div><div class="ped-tit" style="color:#3761AD">Gain fiscal — 2 sources</div>
      <div class="ped-txt"><b>Déficit naturel</b> (intérêts d'emprunt, acquis sans Jeanbrun) + <b>Jeanbrun</b> (amortissement sur 9 ans).</div>
      </div>""", unsafe_allow_html=True)

    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · www.medicis-immobilier-neuf.fr · Document non contractuel · Hypothèses d\'indexation et fiscalité constantes</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ONGLET 2 — SYNTHÈSE SIMPLIFIÉE
# ─────────────────────────────────────────────────────────────────
with t2:
    st.markdown('<div class="sec">SYNTHÈSE — Compte en T · Moyennes mensuelles par horizon</div>', unsafe_allow_html=True)
    ea, eb = st.columns(2)
    with ea:
        st.markdown('<div class="sec blue sm">FOYER</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            "Paramètre": ["Revenus déclarés", "TMI", "Parts fiscales", "Mensualité totale", "Éco. fiscale an 1", "Apport"],
            "Valeur":    [fe(rev), fp(res["tmi_v"]), fn(parts, 1), fe(res["mens_tot"]), fe(res["eco1"]), fe(apport)],
        }), hide_index=True, use_container_width=True, height=240)
    with eb:
        st.markdown('<div class="sec teal sm">OPÉRATION</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            "Paramètre": ["Prix d'acquisition", "Frais acq.", "Zone / SP pondérée", "Loyer initial retenu",
                         "Type / amort. Jeanbrun", "Amortissement/an"],
            "Valeur":    [fe(prix), fp(frais_pct), f"Zone {zone} · {fn(res['sp'],1)} m²",
                         fe(res["lmens"]), f"{type_loyer} · {fp(TAUX_AMT[type_loyer])}",
                         fe(res["amort_an"])],
        }), hide_index=True, use_container_width=True, height=240)

    st.markdown("---")
    for lbl, hk, n, bc, bg, icon in [
        ("HORIZON 9 ANS — Fin durée d'engagement",              "h9",  9,  "#3761AD", "#EEF2FB", "🔹"),
        ("HORIZON 15 ANS — Horizon de référence",               "h15", 15, "#009FA3", "#E4F5F5", "🔸"),
        ("HORIZON 25 ANS — Financement soldé · Pleine propriété", "h25", 25, "#EA653D", "#FEF0EC", "⭐"),
    ]:
        h = res[hk]
        st.markdown(f'<div class="sec" style="background:{bc}">{icon} {lbl}</div>', unsafe_allow_html=True)
        st.caption(f"Moyennes mensuelles calculées sur {n} ans ({n*12} mois)")
        ca2, cb2, cc2 = st.columns([2.5, 2.5, 2])
        with ca2:
            st.markdown('<div style="color:#009FA3;font-weight:700;font-size:.82rem;margin-bottom:.25rem">✚ CE QUI RENTRE (+)</div>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame({
                "":       ["Loyer mensuel moyen", "Gain fiscal/mois", "TOTAL ENTRÉES"],
                "€/mois": [fe(h["lm"]), fe(h["gm"]), fe(h["te"])],
            }), hide_index=True, use_container_width=True, height=145)
        with cb2:
            st.markdown('<div style="color:#EA653D;font-weight:700;font-size:.82rem;margin-bottom:.25rem">− CE QUI SORT (−)</div>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame({
                "":       ["Mensualité de crédit", "Charges/mois", "TOTAL SORTIES"],
                "€/mois": [fe(h["cm"]), fe(h["chm"]), fe(h["ts"])],
            }), hide_index=True, use_container_width=True, height=145)
        with cc2:
            ef = h["ef"]
            ec = "#EA653D" if ef < 0 else "#009FA3"
            st.markdown(f"""<div style="background:{bg};border-radius:9px;padding:.85rem;text-align:center;border-top:4px solid {bc}">
              <div style="font-size:.64rem;color:#888;text-transform:uppercase;letter-spacing:.06em">Effort d'investissement mensuel</div>
              <div style="font-size:1.2rem;font-weight:800;color:{ec};margin:.25rem 0">{fe(abs(ef))}</div>
              <hr style="margin:.3rem 0;border-color:#ddd">
              <div style="font-size:.75rem;text-align:left;line-height:1.85">
                <b>Capital net (0%)</b> : {fe(h['cap0'])}<br>
                <b>Capital net (+1,5%)</b> : {fe(h['cap15'])}<br>
                <b>Gain fiscal total</b> : {fe(h['gft'])}<br>
                <em style="color:#888">dont déficit</em> : {fe(h['dont_d'])}<br>
                <em style="color:#3761AD">dont Jeanbrun</em> : {fe(h['dont_j'])}
              </div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""**Comment lire ce tableau :**
- ▸ Le côté **VERT (+)** = loyers + économie d'impôt Jeanbrun.
- ▸ Le côté **ROUGE (−)** = mensualité de crédit + charges.
- ▸ L'**EFFORT** = reste à charge réel. Négatif = complément mensuel à prévoir.
- ▸ Le gain fiscal se décompose : **déficit naturel** (intérêts, même sans Jeanbrun) + **Jeanbrun** (amortissement 9 ans).
""")
    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · www.medicis-immobilier-neuf.fr · Document non contractuel</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ONGLET 3 — SYNTHÈSE DÉTAILLÉE
# ─────────────────────────────────────────────────────────────────
with t3:
    st.markdown('<div class="sec">PROJECTION FINANCIÈRE — DISPOSITIF JEANBRUN</div>', unsafe_allow_html=True)
    st.caption("Simulation personnalisée • Document non contractuel")

    ca, cb, cc = st.columns(3)
    with ca:
        st.markdown('<div class="sec blue sm">SITUATION DU FOYER</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            "": ["Revenus déclarés", "Abattement", "Revenus nets", "RF autres biens",
                 "IR avant opération", "PS avant opération", "Total impôt avant", "TMI", "Parts"],
            "Valeur": [fe(rev), fe(res["ab"]), fe(res["rn"]), fe(rfa),
                       fe(res["ir_ref"]), fe(res["ps_ref"]), fe(res["tot_ref"]),
                       fp(res["tmi_v"]), fn(parts, 1)],
        }), hide_index=True, use_container_width=True, height=340)
    with cb:
        st.markdown('<div class="sec teal sm">FINANCEMENT</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            "": ["Prix d'acquisition", "Frais d'acquisition", "Coût total", "Apport", "Montant emprunté",
                 "Taux nominal", "Durée", "Mensualité hors assur.", "Assurance/mois", "Mensualité totale"],
            "Valeur": [fe(prix), fe(prix * frais_pct), fe(res["cout"]), fe(apport), fe(res["mempr"]),
                       fp(ti), f"{duree} ans", fe(res["mens_tot"] - res["mempr"] * ta / 12),
                       fe(res["mempr"] * ta / 12), fe(res["mens_tot"])],
        }), hide_index=True, use_container_width=True, height=380)
    with cc:
        st.markdown('<div class="sec ora sm">DISPOSITIF JEANBRUN</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            "": ["Zone / Surface pond.", "Loyer max légal", "Loyer retenu", "Coefficient",
                 "Type de loyer", "Base amortissable (80%)", "Taux d'amortissement", "Plafond annuel",
                 "▸ Amortissement retenu/an", "Durée engagement", f"Amort. total ({duree_amort} ans)", "Éco. fiscale an 1"],
            "Valeur": [f"Zone {zone} · {fn(res['sp'],1)} m²",
                       fe(res["lmax"]), fe(res["lmens"]), fn(res["coeff"], 2),
                       type_loyer, fe(res["base_a"]), fp(TAUX_AMT[type_loyer]),
                       fe(PLAF_AMT[type_loyer]), fe(res["amort_an"]),
                       f"{duree_amort} ans", fe(res["amort_an"] * duree_amort), fe(res["eco1"])],
        }), hide_index=True, use_container_width=True, height=440)

    # ── Projection 25 ans (toutes colonnes clés + TRI + Amt restant)
    st.markdown('<div class="sec blue">PROJECTION ANNUELLE 25 ANS</div>', unsafe_allow_html=True)
    rows3 = []
    for a in ann:
        amt_rest = res["base_a"] - a["amt_cum"]
        rows3.append({
            "An":          a["an"],
            "Loyers":      round(a["lo"], 0),
            "Rembours.":   round(a["remb"], 0),
            "Charges":     round(a["ch"], 0),
            "Amort. JB":   round(a["amort_yr"], 0),
            "RF net imputé": round(a["rfn"], 0),
            "IR avant":    round(a["ir_av"], 0),
            "IR après":    round(a["ir_ap"], 0),
            "Éco. fiscale": round(a["eco"], 0),
            "Effort/mois": round(a["effort"], 0),
            "Cap. net 0%": round(a["cap0"], 0),
            "Cap. +1,5%":  round(a["cap15"], 0),
            "Amt restant": round(amt_rest, 0),
        })
    df_det = pd.DataFrame(rows3)

    # Ligne totaux
    totals = {
        "An": "TOTAL",
        "Loyers": round(sum(a["lo"] for a in ann), 0),
        "Rembours.": round(sum(a["remb"] for a in ann), 0),
        "Charges": round(sum(a["ch"] for a in ann), 0),
        "Amort. JB": round(sum(a["amort_yr"] for a in ann), 0),
        "Éco. fiscale": round(sum(a["eco"] for a in ann), 0),
    }
    df_total = pd.DataFrame([totals])
    df_show = pd.concat([df_det, df_total], ignore_index=True)
    st.dataframe(df_show, hide_index=True, use_container_width=True, height=580)

    # ── Graphique effort + éco fiscale
    st.markdown('<div class="sec teal sm no-print">📉 EFFORT MENSUEL & ÉCONOMIE FISCALE</div>', unsafe_allow_html=True)
    st.pyplot(fig_effort_eco(ann))

    # ── Bilan global
    st.markdown('<div class="sec ora">BILAN GLOBAL DE L\'OPÉRATION</div>', unsafe_allow_html=True)
    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown(f"""
| Indicateur | Valeur |
|---|---|
| Total loyers perçus (25 ans) | **{fe(sum(a['lo'] for a in ann))}** |
| Total remboursements prêt | **{fe(sum(a['remb'] for a in ann))}** |
| Total charges exploitation | **{fe(sum(a['ch'] for a in ann))}** |
| Total amortissements Jeanbrun | **{fe(sum(a['amort_yr'] for a in ann))}** |
| **Total économie fiscale** | **{fe(sum(a['eco'] for a in ann))}** |
""")
    with b2:
        tri9 = ann[8]["tri"]
        tri15 = ann[14]["tri"]
        tri25 = ann[24]["tri"]
        st.markdown(f"""
| TRI investisseur (si revente) | Valeur |
|---|---|
| TRI à 9 ans | **{fp(tri9) if tri9 is not None else '—'}** |
| TRI à 15 ans | **{fp(tri15) if tri15 is not None else '—'}** |
| TRI à 25 ans | **{fp(tri25) if tri25 is not None else '—'}** |
""")
    with b3:
        st.markdown(f"""
| Cash‑flow cumulé | Valeur |
|---|---|
| CF cumulé à 9 ans | **{fe(ann[8]['cashflow_cum'])}** |
| CF cumulé à 15 ans | **{fe(ann[14]['cashflow_cum'])}** |
| CF cumulé à 25 ans | **{fe(ann[24]['cashflow_cum'])}** |
""")
    st.caption("Le TRI mesure la rentabilité annualisée si revente à la date indiquée, après impôt PV. "
               "L'effort d'épargne est le reste à charge mensuel réel après loyers et économie fiscale.")
    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · Document de travail interne non contractuel</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ONGLET 4 — REVENTE & PLUS-VALUE
# ─────────────────────────────────────────────────────────────────
with t4:
    st.markdown('<div class="sec">🏦 SIMULATION DE REVENTE — Calcul pédagogique de la plus-value nette</div>', unsafe_allow_html=True)
    cols3 = st.columns(3)
    for col, (an_r, lbl, bc, bg, icon) in zip(cols3, [
        (9,  "REVENTE À 9 ANS",  "#3761AD", "#EEF2FB", "🔹"),
        (15, "REVENTE À 15 ANS", "#009FA3", "#E4F5F5", "🔸"),
        (25, "REVENTE À 25 ANS", "#EA653D", "#FEF0EC", "⭐"),
    ]):
        a = ann[an_r - 1]
        with col:
            st.markdown(f"<div style='font-weight:700;font-size:.95rem;color:{bc};margin-bottom:.5rem'>{icon} {lbl}</div>", unsafe_allow_html=True)
            for titre, pv_v, pv_b, ipv, cap in [
                ("0% — prix stable",     prix,                 a["pv0"],  a["ipv0"],  a["cap0"]),
                ("+1,5%/an — historique", prix * (1.015 ** an_r), a["pv15"], a["ipv15"], a["cap15"]),
            ]:
                pvi = max(0, pv_b * (1 - a["ai"]))
                pps = max(0, pv_b * (1 - a["ap"]))
                ir_pv = pvi * TAUX_IR_PV
                ps_pv = pps * TAUX_PS_PV
                surt = max(0.0, surtaxe(pvi))
                cap_col = "#009FA3" if cap > 0 else "#EA653D"
                st.markdown(f"""<div style="background:{bg};border-radius:9px;padding:.85rem 1rem;
                  margin-bottom:.6rem;border-left:4px solid {bc}">
                  <div style="font-weight:700;font-size:.79rem;color:{bc};margin-bottom:.4rem">Scénario {titre}</div>
                  <div style="font-size:.78rem;line-height:1.95">
                  Prix de vente : <b>{fe(pv_v)}</b><br>
                  Prix d'acquisition : <b>{fe(prix)}</b><br>
                  + Frais acq. 7,5% (forfait) : +{fe(a['fac'])}<br>
                  + Travaux 15% (si > 5 ans) : +{fe(a['ftv'])}<br>
                  − Amort. réintégrés : −{fe(a['amt_cum'])}<br>
                  <b>= Prix de revient corrigé : {fe(a['pr'])}</b><br>
                  <b style="color:{bc}">➜ PV brute : {fe(pv_b)}</b><br>
                  Abatt. IR {fp(a['ai'],1)} → base imposable : {fe(pvi)}<br>
                  Abatt. PS {fp(a['ap'],1)} → base imposable : {fe(pps)}<br>
                  IR 19% : {fe(ir_pv)} · PS 17,2% : {fe(ps_pv)}<br>
                  Surtaxe : {fe(surt)}<br>
                  <b>Impôt PV total : <span style="color:#EA653D">{fe(ipv)}</span></b><br>
                  CRD à solder : −{fe(a['crd'])}<br>
                  <span style="color:{cap_col};font-weight:800;font-size:.95rem">✅ Capital net : {fe(cap)}</span>
                  </div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec blue">💡 COMPRENDRE CES CHIFFRES</div>', unsafe_allow_html=True)
    st.markdown("""
- ▸ Capital net = ce qui reste **en poche** après avoir soldé le crédit et payé l'impôt sur la plus-value.
- ▸ **Exonération totale IR** : à partir de **22 ans** de détention. **PS** : à partir de **30 ans**.
- ▸ L'amortissement Jeanbrun (9 ans) est réintégré dans le prix de revient — mais l'économie d'impôt réalisée chaque année vous a déjà enrichi durant la période locative.
- ▸ À 25 ans, le crédit est soldé (CRD = 0) : capital net = valeur du bien − impôt PV uniquement.
- ▸ Le scénario **0%** est conservateur. Le **+1,5%/an** reflète l'évolution historique moyenne du marché immobilier français.
""")
    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · www.medicis-immobilier-neuf.fr · Simulation personnalisée non contractuelle</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ONGLET 5 — MOTEUR (49 colonnes Excel)
# ─────────────────────────────────────────────────────────────────
with t5:
    st.markdown('<div class="sec">⚙️ MOTEUR — Données brutes · 49 colonnes Excel V9</div>', unsafe_allow_html=True)

    rows5 = []
    for a in ann:
        rows5.append({
            "An": a["an"],
            "Loyers": round(a["lo"], 2),
            "Charges": round(a["ch"], 2),
            "Intérêts": round(a["int_a"], 2),
            "Assurance": round(a["ass_a"], 2),
            "Amort.JB": round(a["amort_yr"], 2),
            "CRD": round(a["crd"], 2),
            "Val.bien": round(prix, 0),
            "RF autres": round(rfa, 0),
            "Rev.tot.av.": round(a["rev_total_avant"], 2),
            "QF av.": round(a["qf_avant"], 2),
            "TMI av.": fp(a["tmi_avant"]),
            "Tx moy av.": fp(a["tx_moy_avant"]),
            "IR av.": round(a["ir_av"], 2),
            "PS av.": round(a["ps_av"], 2),
            "Tot. av.": round(a["tot_av"], 2),
            "RF bruts": round(a["rf_b"], 2),
            "Ch.fin.": round(a["ch_f"], 2),
            "Ch.non-fin": round(a["ch_nf"], 2),
            "RF net gl.": round(a["rfn"], 2),
            "Déd.RG": round(a["ded"], 2),
            "Déf.gén.": round(a["def_g"], 2),
            "Stock déf.": round(a["stock_def"], 2),
            "Déf.imp.": round(a["def_imp"], 2),
            "RF net tax.": round(a["rfnt"], 2),
            "Rev.après": round(a["rev_ap"], 2),
            "QF ap.": round(a["qf_apres"], 2),
            "TMI ap.": fp(a["tmi_apres"]),
            "Tx moy ap.": fp(a["tx_moy_apres"]),
            "IR ap.": round(a["ir_ap"], 2),
            "PS ap.": round(a["ps_ap"], 2),
            "Tot. ap.": round(a["tot_ap"], 2),
            "Éco.fisc.": round(a["eco"], 2),
            "Enrichis.": round(a["enrichissement"], 2),
            "Eff./mois": round(a["effort"], 2),
            # Col 36 omitted (summary only)
            "CF cum.": round(a["cashflow_cum"], 2),
            "Amt.cum.": round(a["amt_cum"], 2),
            "Stock rpt": round(a["stock_rpt_amt"], 2),
            "PV brute 0%": round(a["pv0"], 2),
            "Ab.IR": fp(a["ai"]),
            "PV imp.IR": round(a["pvi0"], 2),
            "Ab.PS": fp(a["ap"]),
            "PV imp.PS": round(a["pps0"], 2),
            "Imp.PV": round(a["ipv0"], 2),
            "Déf.périmé": round(a["def_perime"], 2),
            "TRI": fp(a["tri"]) if a["tri"] is not None else "—",
            "CSG d.av.": round(a["csg_ded_av"], 2),
            "CSG d.ap.": round(a["csg_ded_ap"], 2),
            "Cap.0%": round(a["cap0"], 2),
            "Cap.+1,5%": round(a["cap15"], 2),
        })
    st.dataframe(pd.DataFrame(rows5), hide_index=True, use_container_width=True, height=600)
    st.markdown("""
**Colonnes clés :** · *RF net gl.* = RF bruts − Ch.fin − Ch.non-fin (dont amort. JB limité à 9 ans)  
· *Déd.RG* = déficit imputable RG (plaf. 10 700 €) · *Stock déf.* = report 10 ans  
· *Amt.cum.* = amortissements cumulés réellement déduits (figé après an 9) · *PR* = prix de revient pour PV  
· *TRI* = taux de rentabilité interne si revente à l'année N · *CF cum.* = cash‑flow cumulé avec apport  
· *CSG d.av./ap.* = CSG déductible avant/après (6,8% des RF, imputable N+1) · *Déf.périmé* = déficit périmé > 10 ans
""")
    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · Document de travail interne non contractuel</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ONGLET 6 — RÈGLES FISCALES
# ─────────────────────────────────────────────────────────────────
with t6:
    st.markdown('<div class="sec">📐 RÈGLES FISCALES — Références législatives dispositif Jeanbrun</div>', unsafe_allow_html=True)
    r1, r2 = st.columns(2)
    with r1:
        st.markdown('<div class="sec blue sm">DISPOSITIF JEANBRUN</div>', unsafe_allow_html=True)
        st.markdown("""
| Paramètre | Valeur | Référence |
|---|---|---|
| Base amortissable | 80% du prix | Art. 2 quindecies B ann. III CGI |
| Taux — Loyer intermédiaire | **3,5 %** | Art. 2 quindecies B |
| Taux — Loyer social | **4,5 %** | Art. 2 quindecies B |
| Taux — Loyer très social | **5,5 %** | Art. 2 quindecies B |
| Plafond — Intermédiaire | **8 000 €/an** | Art. 2 quindecies B |
| Plafond — Social | **10 000 €/an** | Art. 2 quindecies B |
| Plafond — Très social | **12 000 €/an** | Art. 2 quindecies B |
| Durée engagement initial | **9 ans** | Art. 199 novovicies CGI |
| Renouvellement possible | 2 × 3 ans (15 ans max) | Art. 199 novovicies |
| Réintégration à la revente | Amortissements déduits | Art. 150 VB CGI |
| Coefficient loyer | TRUNC((0,7+19/SP)×100)/100 | Art. 2 terdecies D |
""")
        st.markdown('<div class="sec teal sm">DÉFICIT FONCIER — ART. 156-I-3 CGI</div>', unsafe_allow_html=True)
        st.markdown(f"""
| Règle | Valeur |
|---|---|
| Plafond imputation revenu global | **10 700 €/an** |
| Déficit issu intérêts d'emprunt | Non imputable sur RG → report RF seulement |
| Déficit issu charges non-financières | Imputable RG (plaf. 10 700 €) |
| Report déficit excédentaire | **10 ans** |
| Engagement de location après imputation | **3 ans minimum** |

> **Votre simulation an 1 :** Déd. RG = **{fe(ann[0]["ded"])}** · Déficit généré = **{fe(ann[0]["def_g"])}**
""")
        st.markdown('<div class="sec ora sm">PLUS-VALUE IMMOBILIÈRE — ART. 150 U CGI</div>', unsafe_allow_html=True)
        st.markdown(f"""
| Paramètre | Valeur |
|---|---|
| Forfait frais acquisition | 7,5% du prix d'achat |
| Forfait travaux (si > 5 ans) | 15% du prix d'achat |
| Taux IR plus-value | **19 %** |
| Taux PS plus-value | **17,2 %** |
| Exonération totale IR | **22 ans** de détention |
| Exonération totale PS | **30 ans** de détention |
| Surtaxe | De 2% à 6% au-delà de 50 000 € de PV |
""")
    with r2:
        st.markdown('<div class="sec blue sm">ABATTEMENTS DURÉE DE DÉTENTION (abatt. IR / PS)</div>', unsafe_allow_html=True)
        abr = []
        for yr in range(1, 31):
            ai = abatt_ir_pv(yr)
            apv = abatt_ps_pv(yr)
            abr.append({"An": yr, "Abatt. IR": fp(ai), "IR résiduel": fp(1 - ai),
                         "Abatt. PS": fp(apv), "PS résiduelle": fp(1 - apv)})
        st.dataframe(pd.DataFrame(abr), hide_index=True, use_container_width=True, height=550)
        st.markdown("> Exonération IR complète : **an 22** · Exonération PS complète : **an 30**")
    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · CGI · Francis Lefebvre · Legifrance · Document interne non contractuel</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ONGLET 7 — PLAFONDS LOYERS
# ─────────────────────────────────────────────────────────────────
with t7:
    st.markdown('<div class="sec">🏘️ PLAFONDS DE LOYERS — Art. 2 terdecies D ann. III CGI · 2025/2026</div>', unsafe_allow_html=True)
    pl1, pl2 = st.columns([2.5, 1.5])
    with pl1:
        st.markdown('<div class="sec blue sm">PLAFONDS €/m²/MOIS — Par zone et type</div>', unsafe_allow_html=True)
        pd_rows = []
        for z, v in PLAFONDS_LOYERS.items():
            pd_rows.append({"Zone": z,
                            "Intermédiaire": f"{v['Loyer intermédiaire']} €/m²/mois",
                            "Social": f"{v['Loyer social']} €/m²/mois",
                            "Très social": f"{v['Loyer très social']} €/m²/mois"})
        st.dataframe(pd.DataFrame(pd_rows), hide_index=True, use_container_width=True)
        st.markdown("> **Loyer max légal** = Plafond €/m²/mois × **Surface pondérée** × **Coefficient**")
        st.markdown(f'<div class="sec teal sm">SIMULATION LOYER MAX — VOTRE BIEN ({fn(res["sp"],1)} m² · Coeff {fn(res["coeff"],2)})</div>', unsafe_allow_html=True)
        sim_r = []
        for z, v in PLAFONDS_LOYERS.items():
            for tl, plm2 in v.items():
                lm = plm2 * res["sp"] * res["coeff"]
                sim_r.append({"Zone": z, "Type": tl, "€/m²": f"{plm2}",
                              "Max légal": fe(lm),
                              f"Loyer {ls}€ ?": "✅ OK" if ls <= lm else "❌ Dépasse"})
        st.dataframe(pd.DataFrame(sim_r), hide_index=True, use_container_width=True)
    with pl2:
        st.markdown('<div class="sec ora sm">PLAFONDS D\'AMORTISSEMENT</div>', unsafe_allow_html=True)
        st.markdown("""
| Type | Taux | Plafond/an |
|---|---|---|
| Intermédiaire | **3,5 %** | **8 000 €** |
| Social | **4,5 %** | **10 000 €** |
| Très social | **5,5 %** | **12 000 €** |
_Base : 80% du prix d'acquisition_
""")
        st.markdown('<div class="sec blue sm">ZONES GÉOGRAPHIQUES</div>', unsafe_allow_html=True)
        st.markdown("""
| Zone | Périmètre |
|---|---|
| **A bis** | Paris + 76 communes |
| **A** | Île-de-France (hors A bis), Côte d'Azur, Genevois |
| **B1** | > 250 000 hab., grande couronne |
| **B2** | 50–250 000 hab. (sur agrément) |
| **C** | Reste du territoire |
""")
        st.markdown('<div class="sec teal sm">VOTRE SIMULATION</div>', unsafe_allow_html=True)
        st.markdown(f"""
| | |
|---|---|
| Zone | **{zone}** |
| Type | **{type_loyer}** |
| Surface hab. | **{surf} m²** |
| Balcon/Terrasse | {balcon}/{terrasse} m² |
| RDC | **{rdc}** |
| **SP pondérée** | **{fn(res["sp"],1)} m²** |
| **Coefficient** | **{fn(res["coeff"],2)}** |
| **Loyer max légal** | **{fe(res["lmax"])}/mois** |
| **Loyer retenu** | **{fe(res["lmens"])}/mois** |
""")
    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · Art. 2 terdecies D ann. III CGI · Plafonds 2025/2026</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ONGLET 8 — BARÈME FISCAL
# ─────────────────────────────────────────────────────────────────
with t8:
    st.markdown('<div class="sec">📊 BARÈME FISCAL IR 2026 — Art. 197 CGI · Prélèvements sociaux · Simulation</div>', unsafe_allow_html=True)
    b1, b2 = st.columns([1.5, 2])
    with b1:
        st.markdown('<div class="sec blue sm">TRANCHES IR 2026</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame([
            {"Tranche (€ / part QF)": "0 à 11 600 €", "Taux": "0 %"},
            {"Tranche (€ / part QF)": "11 601 à 29 579 €", "Taux": "11 %"},
            {"Tranche (€ / part QF)": "29 580 à 84 577 €", "Taux": "30 %"},
            {"Tranche (€ / part QF)": "84 578 à 181 917 €", "Taux": "41 %"},
            {"Tranche (€ / part QF)": "Au-delà de 181 917 €", "Taux": "45 %"},
        ]), hide_index=True, use_container_width=True)
        st.markdown('<div class="sec teal sm">PLAFONNEMENT QF</div>', unsafe_allow_html=True)
        pr_ref = 2.0 if parts >= 2.0 else 1.0
        st.markdown(f"""
| Règle | Valeur |
|---|---|
| Plafond par demi-part | **1 759 €** |
| Parts de référence (couple) | 2,0 parts |
| Parts de référence (célibataire) | 1,0 part |

> Vos **{fn(parts,1)} parts** → économie QF plafonnée à **{fe(max(0.0, (parts - pr_ref) * 2 * PLAFOND_QF))}**
""")
        st.markdown('<div class="sec ora sm">PRÉLÈVEMENTS SOCIAUX 17,2%</div>', unsafe_allow_html=True)
        st.markdown("""
| Prélèvement | Taux |
|---|---|
| CSG | 9,2 % |
| CRDS | 0,5 % |
| Prélèvement solidarité | 7,5 % |
| **Total PS** | **17,2 %** |
| dont CSG déductible (N+1) | **6,8 %** |
""")
    with b2:
        st.markdown('<div class="sec blue sm">AVANT / APRÈS OPÉRATION — ANNÉES CLÉS</div>', unsafe_allow_html=True)
        avap = []
        for ad in [1, 2, 3, 5, 9, 12, 15, 20, 25]:
            a = ann[ad - 1]
            avap.append({
                "An": ad,
                "RN avant": fe(a["rev_total_avant"]),
                "IR avant": fe(a["ir_av"]),
                "Base après": fe(a["rev_ap"]),
                "IR après": fe(a["ir_ap"]),
                "PS après": fe(a["ps_ap"]),
                "Éco. fisc.": fe(a["eco"]),
                "TMI après": fp(a["tmi_apres"]),
            })
        st.dataframe(pd.DataFrame(avap), hide_index=True, use_container_width=True)
        st.markdown('<div class="sec teal sm">CALCUL DÉTAILLÉ — ANNÉE 1</div>', unsafe_allow_html=True)
        a1 = ann[0]
        st.markdown(f"""
| Étape | Montant |
|---|---|
| Revenus déclarés | {fe(rev)} |
| − Abattement {type_rev} | −{fe(res["ab"])} |
| = Revenus nets | **{fe(res["rn"])}** |
| + RF autres biens | +{fe(rfa)} |
| + Déduction sur RG (déficit foncier) | {fe(a1["ded"])} |
| − CSG déductible N-1 | 0 € (an 1) |
| **= Base imposable après opération** | **{fe(a1["rev_ap"])}** |
| IR avant | {fe(a1["ir_av"])} |
| IR après | {fe(a1["ir_ap"])} |
| PS avant (sur RF autres biens) | {fe(max(0.0, rfa) * TAUX_PS)} |
| PS après (sur RF net taxable {fe(a1["rfnt"])}) | {fe(a1["ps_ap"])} |
| **Économie fiscale totale an 1** | **{fe(a1["eco"])}** |
""")
    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · Barème IR 2026 (art. 197 CGI) · Plafonnement QF 1 759 €/demi-part</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ONGLET 9 — TABLEAU D'AMORTISSEMENT
# ─────────────────────────────────────────────────────────────────
with t9:
    st.markdown('<div class="sec">💰 TABLEAU D\'AMORTISSEMENT FINANCIER — Prêt immobilier</div>', unsafe_allow_html=True)
    ta1, ta2 = st.columns([2.5, 1.5])
    with ta2:
        st.markdown('<div class="sec blue sm">CARACTÉRISTIQUES DU PRÊT</div>', unsafe_allow_html=True)
        st.markdown(f"""
| Paramètre | Valeur |
|---|---|
| Capital emprunté | **{fe(res["mempr"])}** |
| Taux nominal annuel | **{fp(ti)}** |
| Durée | **{duree} ans ({duree*12} mois)** |
| Mensualité (hors assurance) | **{fe(res["mens_tot"] - res["mempr"] * ta / 12)}** |
| Assurance mensuelle | {fe(res["mempr"] * ta / 12)} |
| **Mensualité totale** | **{fe(res["mens_tot"])}** |
| Coût total crédit | {fe(res["mens_tot"] * duree * 12 - res["mempr"])} |
""")
        st.markdown(f'<div class="sec teal sm">AMORTISSEMENT JEANBRUN ({duree_amort} ANS)</div>', unsafe_allow_html=True)
        st.markdown(f"""
| Paramètre | Valeur |
|---|---|
| Base (80% prix acq.) | **{fe(res["base_a"])}** |
| Type de loyer | **{type_loyer}** |
| Taux d'amortissement | **{fp(TAUX_AMT[type_loyer])}** |
| Plafond annuel | **{fe(PLAF_AMT[type_loyer])}** |
| **Amortissement retenu** | **{fe(res["amort_an"])}/an** |
| **Durée** | **{duree_amort} ans** |
| **Cumul total ({duree_amort} ans)** | **{fe(res["amort_an"] * duree_amort)}** |
| Économie fiscale an 1 | {fe(res["eco1"])} |
""")
    with ta1:
        vue = st.radio("Afficher :", ["Tableau annuel", "Tableau mensuel (3 premières années)"], horizontal=True)
        if vue == "Tableau annuel":
            st.markdown('<div class="sec blue sm">AMORTISSEMENT ANNUEL DU PRÊT</div>', unsafe_allow_html=True)
            ar = []
            for i, row in enumerate(res["amttab"]):
                ic = sum(r["int"] for r in res["amttab"][:i + 1])
                pc = sum(r["princ"] for r in res["amttab"][:i + 1])
                ar.append({
                    "An": i + 1,
                    "Capital amorti": fe(row["princ"]),
                    "Intérêts": fe(row["int"]),
                    "Assurance": fe(res["mempr"] * ta / 12 * 12),
                    "Total remboursé": fe(row["princ"] + row["int"] + res["mempr"] * ta / 12 * 12),
                    "CRD fin d'an": fe(row["crd"]),
                    "Intérêts cumulés": fe(ic),
                    "Capital remb. %": fp(pc / res["mempr"]),
                })
            st.dataframe(pd.DataFrame(ar), hide_index=True, use_container_width=True, height=520)
        else:
            st.markdown('<div class="sec teal sm">TABLEAU MENSUEL — 3 PREMIÈRES ANNÉES</div>', unsafe_allow_html=True)
            mr = []
            for r_m in res["rows_m"][:36]:
                mr.append({
                    "Mois": r_m["mois"],
                    "Intérêts": fe(r_m["im"]),
                    "Capital": fe(r_m["pm"]),
                    "Assurance": fe(res["mempr"] * ta / 12),
                    "Total": fe(r_m["im"] + r_m["pm"] + res["mempr"] * ta / 12),
                    "CRD": fe(r_m["crd"]),
                })
            st.dataframe(pd.DataFrame(mr), hide_index=True, use_container_width=True, height=520)

        # Graphique amortissement prêt
        st.markdown('<div class="sec teal sm no-print">📊 DÉCOMPOSITION ANNUELLE</div>', unsafe_allow_html=True)
        st.pyplot(fig_amort_pret(res["amttab"], res["mempr"], ta))

    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · Calcul mensuel exact agrégé annuellement</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ONGLET 10 — IMPRIMER
# ─────────────────────────────────────────────────────────────────
with t10:
    st.markdown('<div class="sec">🖨️ IMPRESSION A4 PORTRAIT</div>', unsafe_allow_html=True)
    st.markdown("""
**Procédure d'impression :**
1. Allez sur l'onglet souhaité — **Synthèse visuelle**, **Simplifiée**, **Détaillée** ou **Revente & Plus-value**
2. Cliquez sur le bouton ci-dessous (ou **Ctrl+P** / **Cmd+P**)
3. Sélectionnez **Format : A4 · Orientation : Portrait**
4. Cochez « Graphiques d'arrière-plan » pour conserver les couleurs
5. Décochez les en-têtes/pieds de page du navigateur

> **Note :** Les onglets de navigation, la barre latérale et les graphiques interactifs sont automatiquement masqués à l'impression. Le contenu de l'onglet actif s'imprime en A4 portrait compact.
""")
    components.html("""<style>@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap');</style>
    <button onclick="window.parent.print();" style="
      padding:.75rem 2.5rem;font-size:1rem;cursor:pointer;
      background:#EA653D;color:white;border:none;border-radius:8px;
      font-weight:600;letter-spacing:.04em;display:block;margin:1rem auto;
      font-family:Poppins,sans-serif;box-shadow:0 4px 14px rgba(234,101,61,.35);">
      🖨️ Imprimer cet onglet (A4 Portrait)
    </button>""", height=70)
    st.markdown("---")
    st.caption(f"**Moteur de calcul V11 :** Python natif · Fidélité Excel V9 · 49 colonnes · "
               f"Amortissement Jeanbrun sur {duree_amort} ans (art. 2 quindecies B) · "
               "Barème IR 2026 avec plafonnement QF (1 759 €/demi-part) · "
               "Déficits fonciers art. 156-I-3 CGI · TRI investisseur · CSG déductible N+1 · "
               "Document non contractuel")
    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · www.medicis-immobilier-neuf.fr · Outil réservé aux conseillers</div>', unsafe_allow_html=True)
