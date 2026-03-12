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

/* Masquer l'icône keyboard_double_arrow résiduelle */
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
button[kind="headerNoPadding"],
[data-testid="stSidebar"] button[aria-label*="Collapse"],
[data-testid="stSidebar"] button[aria-label*="Close"]{
  color:transparent!important;-webkit-text-fill-color:transparent!important;
}
[data-testid="stSidebar"] button[aria-label*="Collapse"] svg,
[data-testid="stSidebar"] button[aria-label*="Close"] svg,
[data-testid="collapsedControl"] svg{
  fill:rgba(255,255,255,.5)!important;stroke:rgba(255,255,255,.5)!important;
}
/* Masquer les textes keyboard_double parasites */
[data-testid="stSidebar"] span.material-symbols-outlined,
[data-testid="stSidebar"] .material-icons{
  font-size:0!important;color:transparent!important;-webkit-text-fill-color:transparent!important;
}
button[kind="headerNoPadding"] span{color:transparent!important;-webkit-text-fill-color:transparent!important;font-size:0!important}

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
  background:rgba(234,101,61,.18)!important;
  border:1px solid rgba(234,101,61,.35)!important;
  border-radius:8px!important;
  padding:.55rem .8rem!important;
  margin:.6rem 0 .4rem!important;
  font-weight:700!important;
  font-size:.82rem!important;
  color:#EA653D!important;
  -webkit-text-fill-color:#EA653D!important;
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

/* ══════ SCREEN-ONLY / PRINT-ONLY ══════ */
.screen-only{display:block}
.print-only{display:none}

/* ══════ LOGIN ══════ */
.login-card{background:#fff;border-radius:16px;box-shadow:0 8px 40px rgba(20,65,92,.15);
  padding:2.2rem 2rem;text-align:center;margin-top:4rem}

/* ══════ ALTERNANCE COULEURS TABLEAU (Moteur) ══════ */
.alt-table{width:100%;border-collapse:collapse;font-size:.75rem}
.alt-table th{background:var(--dark);color:#fff;padding:.3rem .4rem;text-align:left;position:sticky;top:0;font-size:.68rem}
.alt-table td{padding:.25rem .4rem;border-bottom:1px solid #eee}
.alt-table tr:nth-child(even){background:#f7f9fc}
.alt-table tr:nth-child(odd){background:#ffffff}
.alt-table tr:hover{background:#e8f0fe}

/* ══════ PRINT A4 PORTRAIT — 1 page par onglet ══════ */
@media print{
  /* Masquer sidebar, toolbar, tabs, boutons */
  [data-testid="stSidebar"],
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"],
  .stTabs [data-baseweb="tab-list"],
  button,.stDownloadButton,.no-print,
  .stExpander,
  [data-testid="collapsedControl"]
    {display:none!important;visibility:hidden!important}

  /* Masquer uniquement les iframes du bouton imprimer (components.html), pas les graphiques */
  .element-container:has(iframe[height="70"]),
  .element-container iframe[height="70"]{display:none!important}

  html,body,.stApp{background:#fff!important;margin:0!important;padding:0!important}
  .main .block-container{padding:0 .5cm!important;max-width:100%!important;margin:0!important}

  /* N'afficher QUE le tab panel actif — Streamlit met aria-selected sur l'onglet actif
     et le panel correspondant a display:block, les autres display:none.
     On renforce cette logique : */
  [data-baseweb="tab-panel"]{overflow:visible!important}
  [data-baseweb="tab-panel"][aria-hidden="true"],
  [data-baseweb="tab-panel"][hidden]{display:none!important}

  /* Force tout sur 1 page A4 */
  @page{size:A4 portrait;margin:6mm}

  .print-page{
    page-break-inside:avoid!important;
    max-height:277mm!important;
    overflow:hidden!important;
    transform-origin:top left;
  }

  /* Réduction compacte pour synthèses */
  *{font-size:90%!important;line-height:1.3!important}
  .hdr{padding:.35rem .7rem!important;border-radius:3px!important;margin-bottom:.15rem!important}
  .hdr-logo{font-size:.95rem!important}
  .hdr-title{font-size:.7rem!important}
  .hdr-sub{font-size:.55rem!important}
  .accent{margin-bottom:.2rem!important;height:2px!important}
  .sec{padding:.2rem .5rem!important;margin:.25rem 0 .15rem!important;font-size:.62rem!important}
  .sec.sm{font-size:.58rem!important;padding:.12rem .4rem!important}
  .kpi{padding:.3rem .4rem!important}
  .kpi-val{font-size:.8rem!important}
  .kpi-lbl{font-size:.5rem!important}
  .kpi-sub{font-size:.48rem!important}
  .cnt{padding:.4rem .5rem!important}
  .cnt-tbl{font-size:.62rem!important}
  .cnt-tbl td{padding:.1rem .12rem!important}
  .cnt-bil{font-size:.58rem!important;padding:.2rem .3rem!important;line-height:1.4!important}
  .cnt-tot{padding:.25rem .35rem!important}
  .ped{display:none!important}
  .ped-ico{font-size:1rem!important;margin-bottom:.1rem!important}
  .ped-tit{font-size:.7rem!important;margin-bottom:.1rem!important}
  .ped-txt{font-size:.58rem!important}
  .footer{margin-top:.2rem!important;padding:.15rem 0!important;font-size:.5rem!important}
  table{font-size:.62rem!important}
  td,th{padding:.12rem .2rem!important}

  /* Graphiques : Plotly (screen-only) masqué, matplotlib (print-only) affiché */
  .screen-only,.stPlotlyChart{display:none!important}
  .print-only{display:block!important}
  .stPyplot{max-height:180px!important;overflow:hidden!important}
  .stPyplot img{max-height:180px!important;width:100%!important}

  /* Couleurs préservées */
  *{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}
  .hdr,.sec,.kpi,.cnt,.ped,.alt-table th,
  [style*="background"]
    {-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}
  .alt-table tr:nth-child(even){background:#f7f9fc!important;-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}

  /* Onglets non-synthèse : permettre multi-pages */
  .alt-table{page-break-inside:auto!important}
  .alt-table tr{page-break-inside:avoid!important}
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
    prix      = st.number_input("Prix d'acquisition (€)", min_value=0, max_value=5_000_000, value=None, step=1_000, format="%d", placeholder="Ex : 260 000")
    frais_pct = st.number_input("Frais d'acquisition (%)", 0.0, 15.0, 3.0, 0.1, format="%.1f") / 100
    surf      = st.number_input("Surface habitable (m²)", min_value=0.0, max_value=500.0, value=None, step=0.5, format="%.1f", placeholder="Ex : 40")
    zone      = st.selectbox("Zone Jeanbrun", ["A bis", "A", "B1", "B2", "C"], index=1)
    rdc       = st.selectbox("Rez-de-chaussée ?", ["NON", "OUI"])
    balcon    = st.number_input("Surface balcon (m²)", 0.0, 200.0, 0.0, 0.5, format="%.1f")
    terrasse  = st.number_input("Surface terrasse (m²)", 0.0, 300.0, 0.0, 0.5, format="%.1f")

    # ── SECTION 2 : Financement ──
    st.markdown('<div class="sidebar-section">💳 FINANCEMENT</div>', unsafe_allow_html=True)
    apport = st.number_input("Apport (€)", min_value=0, max_value=2_000_000, value=None, step=500, format="%d", placeholder="Ex : 15 000")
    ti     = st.number_input("Taux intérêt (%/an)", 0.0, 10.0, 3.3, 0.05, format="%.2f") / 100
    ta     = st.number_input("Taux assurance (%/an)", 0.0, 3.0, 0.35, 0.01, format="%.2f") / 100
    duree  = st.number_input("Durée crédit (ans)", 5, 30, 25, 1)
    fg     = st.number_input("Frais garantie + dossier (€)", 0, 20_000, 0, 100, format="%d")

    # ── SECTION 3 : Revenus locatifs ──
    st.markdown('<div class="sidebar-section">🏘️ REVENUS LOCATIFS</div>', unsafe_allow_html=True)
    type_loyer = st.selectbox("Type de loyer", ["Loyer intermédiaire", "Loyer social", "Loyer très social"])
    ls         = st.number_input("Loyer souhaité (€/mois)", min_value=0, max_value=5_000, value=None, step=10, format="%d", placeholder="Ex : 750")
    il         = st.number_input("Indexation loyers (%/an)", 0.0, 1.5, 1.5, 0.1, format="%.1f",
                                   help="Plafonnée à 1,5 %/an (hypothèse prudente)") / 100
    cp         = st.number_input("Charges + TF (% loyers bruts)", 30.0, 60.0, 30.0, 1.0, format="%.0f",
                                   help="Minimum 30 % — inclut gestion, GLI, TF, PNO, menus travaux") / 100
    duree_amort = st.number_input("Durée amortissement JB (ans)", 1, 25, 25, 1,
                                   help="25 ans = modèle Excel V9. Engagement initial = 9 ans.")

    # ── SECTION 4 : Situation fiscale ──
    st.markdown('<div class="sidebar-section">👤 SITUATION FISCALE</div>', unsafe_allow_html=True)
    type_rev = st.selectbox("Type de revenus principaux",
        ["Salaires (abatt. 10%)", "Pensions / Retraites (abatt. 10%)", "BNC / BIC / autres"])
    rev   = st.number_input("Revenus déclarés (€/an)", min_value=0, max_value=2_000_000, value=None, step=1_000, format="%d", placeholder="Ex : 95 000")
    rfa   = st.number_input("RF autres biens (€/an)", 0, 500_000, 0, 500, format="%d")
    parts = st.number_input("Parts fiscales", 1.0, 10.0, 2.5, 0.5, format="%.1f")
    nd    = st.number_input("Nb déclarants", 1, 2, 2, 1)

    st.divider()
    go = st.button("🚀 Lancer la simulation", use_container_width=True, type="primary")


# ── Calcul
if "res" not in st.session_state:
    st.session_state.res = None

# Normaliser les champs None → 0 pour la simulation
prix_v = prix if prix is not None else 0
surf_v = surf if surf is not None else 0.0
apport_v = apport if apport is not None else 0
ls_v = ls if ls is not None else 0
rev_v = rev if rev is not None else 0

if go:
    # Validation des champs obligatoires
    champs_manquants = []
    if prix_v <= 0: champs_manquants.append("Prix d'acquisition")
    if surf_v <= 0: champs_manquants.append("Surface habitable")
    if ls_v <= 0:   champs_manquants.append("Loyer souhaité")
    if rev_v <= 0:  champs_manquants.append("Revenus déclarés")
    if champs_manquants:
        st.error(f"⚠️ Veuillez renseigner : **{', '.join(champs_manquants)}**")
    else:
        with st.spinner("⚙️ Calcul en cours…"):
            st.session_state.res = run(
                prix_v, frais_pct, surf_v, zone, rdc, balcon, terrasse,
                apport_v, ti, ta, duree, fg,
                type_loyer, ls_v, il, cp, type_rev, rev_v, rfa, parts, nd,
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
#  GRAPHIQUES — PLOTLY (interactif) + MATPLOTLIB (fallback)
# ══════════════════════════════════════════════════════════════════
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

COLORS = {"blue": "#3761AD", "teal": "#009FA3", "ora": "#EA653D",
          "dark": "#14415C", "sal": "#F57E63", "lime": "#9a9b1a"}

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


_chart_counter = [0]   # mutable counter for unique keys

def chart_capital_net(ann_data):
    """Graphique capital net (0 % et +1,5 %) — interactif écran + statique impression."""
    _chart_counter[0] += 1
    uid = f"cap_{_chart_counter[0]}"
    xs = [a["an"] for a in ann_data]
    y0 = [a["cap0"] for a in ann_data]
    y15 = [a["cap15"] for a in ann_data]

    # ── Version interactive (écran) — Plotly ou Matplotlib
    if HAS_PLOTLY:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xs, y=y0, mode="lines+markers", name="0 % (prix stable)",
            line=dict(color=COLORS["blue"], width=2.5), marker=dict(size=5)))
        fig.add_trace(go.Scatter(x=xs, y=y15, mode="lines+markers", name="+1,5 %/an",
            line=dict(color=COLORS["teal"], width=2.5), marker=dict(size=5)))
        for vx, vl, vc in [(9, "9 ans", COLORS["blue"]), (15, "15 ans", COLORS["teal"]), (25, "25 ans", COLORS["ora"])]:
            fig.add_vline(x=vx, line_dash="dot", line_color=vc, opacity=.55,
                annotation_text=vl, annotation_position="top", annotation_font=dict(color=vc, size=10))
        fig.add_hline(y=0, line_dash="dash", line_color="#e0e0e0", opacity=.6)
        fig.update_layout(height=280, margin=dict(l=8, r=8, t=8, b=8),
            legend=dict(orientation="h", y=-.22), yaxis=dict(tickformat=",.0f"),
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Poppins,sans-serif", size=10),
            xaxis=dict(tickmode="linear", tick0=1, dtick=2, gridcolor="#f0f0f0", title="Année"),
            yaxis_gridcolor="#f0f0f0", yaxis_title="€")
        st.plotly_chart(fig, use_container_width=True, key=uid)
    else:
        fig, ax = plt.subplots(figsize=(10, 3.2), dpi=100)
        ax.plot(xs, y0, "-o", color=COLORS["blue"], lw=2, ms=3.5, label="0 % (prix stable)")
        ax.plot(xs, y15, "-o", color=COLORS["teal"], lw=2, ms=3.5, label="+1,5 %/an")
        for vx, lbl, vc in [(9, "9 ans", COLORS["blue"]), (15, "15 ans", COLORS["teal"]), (25, "25 ans", COLORS["ora"])]:
            ax.axvline(vx, ls="--", color=vc, alpha=.45, lw=1)
        ax.axhline(0, ls="--", color="#ddd", lw=.8)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", "\u202f")))
        ax.set_xticks(range(1, 26, 2)); ax.set_xlabel("Année"); ax.set_ylabel("€")
        ax.legend(loc="upper left", fontsize=8); ax.grid(axis="y", alpha=.25)
        fig.patch.set_facecolor("white"); ax.set_facecolor("white"); fig.tight_layout()
        st.pyplot(fig, key=uid+"_mpl")

    # ── Version statique pour impression (print-only) — toujours matplotlib
    _chart_static_capital_net(xs, y0, y15, uid)


def _chart_static_capital_net(xs, y0, y15, uid):
    """Génère une image matplotlib statique base64 pour impression A4."""
    import base64
    fig, ax = plt.subplots(figsize=(10, 2.4), dpi=120)
    ax.plot(xs, y0, "-o", color=COLORS["blue"], lw=1.8, ms=3, label="0 % (prix stable)")
    ax.plot(xs, y15, "-o", color=COLORS["teal"], lw=1.8, ms=3, label="+1,5 %/an")
    for vx, lbl, vc in [(9, "9 ans", COLORS["blue"]), (15, "15 ans", COLORS["teal"]), (25, "25 ans", COLORS["ora"])]:
        ax.axvline(vx, ls="--", color=vc, alpha=.4, lw=.8)
        ax.text(vx, ax.get_ylim()[1] * 0.95, lbl, ha="center", fontsize=7, color=vc)
    ax.axhline(0, ls="--", color="#ddd", lw=.8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", "\u202f")))
    ax.set_xticks(range(1, 26, 2)); ax.set_xlabel("Année", fontsize=8); ax.set_ylabel("€", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.legend(loc="upper left", fontsize=7); ax.grid(axis="y", alpha=.2)
    fig.patch.set_facecolor("white"); ax.set_facecolor("white"); fig.tight_layout(pad=.5)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=120)
    plt.close(fig)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    st.markdown(f'<div class="print-only"><img src="data:image/png;base64,{b64}" '
                f'style="width:100%;max-height:170px;display:block;margin:0 auto" /></div>',
                unsafe_allow_html=True)


def chart_amort_pret(amttab_data, mempr_val, ta_val):
    """Graphique amortissement du prêt — stacked bar + CRD."""
    _chart_counter[0] += 1
    uid = f"amt_{_chart_counter[0]}"
    xs = list(range(1, len(amttab_data) + 1))
    ints = [r["int"] for r in amttab_data]
    princs = [r["princ"] for r in amttab_data]
    crds = [r["crd"] for r in amttab_data]
    if HAS_PLOTLY:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=xs, y=ints, name="Intérêts", marker_color=COLORS["ora"], opacity=.85))
        fig.add_trace(go.Bar(x=xs, y=princs, name="Capital", marker_color=COLORS["blue"], opacity=.85))
        fig.add_trace(go.Scatter(x=xs, y=crds, name="CRD €", yaxis="y2",
            line=dict(color=COLORS["teal"], width=2.5), mode="lines"))
        fig.update_layout(barmode="stack", height=250, margin=dict(l=8, r=8, t=8, b=8),
            yaxis2=dict(overlaying="y", side="right", tickformat=",.0f"),
            legend=dict(orientation="h", y=-.3), plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Poppins,sans-serif", size=10),
            xaxis=dict(title="Année", gridcolor="#f0f0f0"), yaxis=dict(title="€/an", gridcolor="#f0f0f0"))
        st.plotly_chart(fig, use_container_width=True, key=uid)
    else:
        fig, ax1 = plt.subplots(figsize=(10, 2.8), dpi=100)
        ax1.bar(xs, ints, color=COLORS["ora"], alpha=.85, label="Intérêts")
        ax1.bar(xs, princs, bottom=ints, color=COLORS["blue"], alpha=.85, label="Capital")
        ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", "\u202f")))
        ax2 = ax1.twinx()
        ax2.plot(xs, crds, color=COLORS["teal"], lw=2.5, label="CRD €")
        ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", "\u202f")))
        h1, l1 = ax1.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
        ax1.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8)
        ax1.set_xlabel("Année"); fig.patch.set_facecolor("white"); ax1.set_facecolor("white"); fig.tight_layout()
        st.pyplot(fig, key=uid+"_mpl")


# ══════════════════════════════════════════════════════════════════
#  ONGLETS
# ══════════════════════════════════════════════════════════════════
t1, t2, t3, t4, t5, t6, t7, t8, t9, t10 = st.tabs([
    "👁️ Synthèse visuelle", "📋 Synthèse simplifiée", "📈 Synthèse détaillée",
    "🏦 Revente & Plus-value", "⚙️ Moteur", "📐 Règles fiscales",
    "🏘️ Plafonds loyers", "📊 Barème fiscal", "💰 Tableau d'amortissement", "🖨️ Imprimer",
])

# ─────────────────────────────────────────────────────────────────
# ONGLET 1 — SYNTHÈSE VISUELLE (fidèle au layout Excel)
# ─────────────────────────────────────────────────────────────────
with t1:
    st.markdown('<div class="sec">▸ DISPOSITIF JEANBRUN — Projection simplifiée · Simulation personnalisée</div>', unsafe_allow_html=True)

    # ── KPI Cards (row 4-7 Excel)
    kpis = [
        ("REVENUS DÉCLARÉS", fe(rev), f"{fn(parts,1)} parts fiscales", ""),
        ("TRANCHE MARGINALE", fp(res["tmi_v"]), "", "t"),
        ("PRIX D'ACQUISITION", fe(prix), f"{type_loyer}", "o"),
        ("LOYER INITIAL", fe(res["lmens"]), "/ mois retenu", "d"),
        ("SURFACE / ZONE", f"{fn(res['sp'],1)} m²  ·  Zone {zone}", f"Coeff. {fn(res['coeff'],2)}", "l"),
        ("ÉCONOMIE FISCALE AN 1", fe(res["eco1"]), "", "t"),
    ]
    cols_k = st.columns(6)
    for col, (lbl, val, sub, cls) in zip(cols_k, kpis):
        with col:
            st.markdown(f'<div class="kpi {cls}"><div class="kpi-lbl">{lbl}</div>'
                        f'<div class="kpi-val">{val}</div>'
                        f'<div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

    # ── Comptes en T (fidèle layout Excel — gros chiffres + tableau structuré)
    st.markdown('<div class="sec">📊 COMPTE EN T · Moyennes mensuelles calculées sur chaque horizon</div>', unsafe_allow_html=True)

    def cnt_html(h, n_ans, subtitle, bg, bc, bc_light, icon):
        ef = h["ef"]; ec = "#EA653D" if ef < 0 else "#009FA3"
        return f"""<div style="border-radius:10px;overflow:hidden;border:1px solid #d0d0d0;height:100%;box-shadow:0 2px 8px rgba(0,0,0,.06)">
          <!-- HEADER gradient -->
          <div style="background:linear-gradient(135deg,{bc} 0%,{bc_light} 100%);padding:.65rem .9rem;text-align:center">
            <div style="display:flex;align-items:baseline;justify-content:center;gap:.3rem">
              <span style="font-size:2.4rem;font-weight:800;color:#fff;text-shadow:0 1px 3px rgba(0,0,0,.15)">{n_ans}</span>
              <span style="font-size:1rem;font-weight:700;color:rgba(255,255,255,.9)">ans</span>
            </div>
            <div style="font-size:.78rem;color:rgba(255,255,255,.85);font-weight:500">{subtitle}</div>
          </div>
          <!-- TABLEAU -->
          <div style="padding:.55rem .75rem .25rem">
            <table style="width:100%;border-collapse:collapse;font-size:.84rem">
              <tr>
                <td colspan="2" style="font-weight:700;color:#2e7d32;font-size:.72rem;padding-bottom:.3rem;letter-spacing:.04em;text-align:center">+ CE QUI RENTRE</td>
                <td colspan="2" style="font-weight:700;color:#c62828;font-size:.72rem;padding-bottom:.3rem;letter-spacing:.04em;text-align:center">− CE QUI SORT</td>
              </tr>
              <tr style="border-bottom:1px solid #ebebeb">
                <td style="padding:.2rem .15rem;color:#444">Loyers moy.</td>
                <td style="padding:.2rem .15rem;font-weight:800;color:#2e7d32;text-align:center">{fe(h['lm'])}</td>
                <td style="padding:.2rem .15rem;color:#444">Crédit</td>
                <td style="padding:.2rem .15rem;font-weight:800;color:#c62828;text-align:center">{fe(h['cm'])}</td>
              </tr>
              <tr style="border-bottom:1px solid #ebebeb">
                <td style="padding:.2rem .15rem;color:#444">Gain fiscal</td>
                <td style="padding:.2rem .15rem;font-weight:800;color:#2e7d32;text-align:center">{fe(h['gm'])}</td>
                <td style="padding:.2rem .15rem;color:#444">Charges</td>
                <td style="padding:.2rem .15rem;font-weight:800;color:#c62828;text-align:center">{fe(h['chm'])}</td>
              </tr>
              <tr style="background:rgba(0,0,0,.04);border-top:2.5px solid {bc}">
                <td style="padding:.3rem .15rem;font-weight:700;color:{bc}">Total</td>
                <td style="padding:.3rem .15rem;font-weight:800;color:#2e7d32;text-align:center;font-size:.9rem">{fe(h['te'])}</td>
                <td style="padding:.3rem .15rem;font-weight:700;color:{bc}">Total</td>
                <td style="padding:.3rem .15rem;font-weight:800;color:#c62828;text-align:center;font-size:.9rem">{fe(h['ts'])}</td>
              </tr>
            </table>
          </div>
          <!-- EFFORT + AVANTAGES FISCAUX -->
          <div style="background:{bg};margin:.25rem .65rem;border-radius:8px;padding:.55rem .6rem;text-align:center;border:1px solid rgba(0,0,0,.05)">
            <div style="display:flex;justify-content:center;align-items:flex-start;gap:.8rem">
              <div style="flex:1">
                <div style="font-size:.6rem;color:#888;text-transform:uppercase;letter-spacing:.07em;font-weight:600">Effort d'épargne mensuel moyen</div>
                <div style="font-size:1.55rem;font-weight:800;color:{ec};line-height:1.2;margin:.1rem 0">{fe(abs(ef))}<span style="font-size:.8rem;font-weight:600">/mois</span></div>
                <div style="font-size:.63rem;color:#aaa;font-style:italic">← Reste à charge réel après loyers et économie fiscale</div>
              </div>
              <div style="width:1px;background:rgba(0,0,0,.12);align-self:stretch;margin:.1rem 0"></div>
              <div style="flex:1">
                <div style="font-size:.6rem;color:#888;text-transform:uppercase;letter-spacing:.07em;font-weight:600">Avantages fiscaux cumulés</div>
                <div style="font-size:1.55rem;font-weight:800;color:#3761AD;line-height:1.2;margin:.1rem 0">{fe(h['gft'])}</div>
                <div style="font-size:.63rem;color:#aaa;font-style:italic">dont <b style="color:#3761AD">{fe(h['dont_j'])}</b> via Jeanbrun</div>
              </div>
            </div>
          </div>
          <!-- CAPITAL NET -->
          <div style="padding:.45rem .7rem .7rem;text-align:center">
            <div style="font-size:.73rem;color:#555;line-height:1.5">
              Capital net si prix vente = prix d'achat
            </div>
            <div style="font-size:1.6rem;font-weight:800;color:{bc};margin-top:.15rem;text-shadow:0 1px 2px rgba(0,0,0,.05)">{fe(h['cap0'])}</div>
          </div>
        </div>"""

    c9, c15, c25 = st.columns(3)
    with c9:  st.markdown(cnt_html(res["h9"], 9, "Fin durée d'engagement", "#EEF2FB", "#3761AD", "#5a8ad4", "🔹"), unsafe_allow_html=True)
    with c15: st.markdown(cnt_html(res["h15"], 15, "★ Horizon de référence", "#E4F5F5", "#009FA3", "#33c2c5", "🔸"), unsafe_allow_html=True)
    with c25: st.markdown(cnt_html(res["h25"], 25, "Financement soldé · Pleine propriété", "#FEF0EC", "#EA653D", "#f5916e", "⭐"), unsafe_allow_html=True)

    # ── Graphique interactif capital net (rows 23-38 Excel = chart)
    st.markdown('<div class="sec no-print">📈 Capital net constitué par année de détention (Valeur revente − CRD − impôt PV) · 0% et 1,5%</div>', unsafe_allow_html=True)
    chart_capital_net(ann)

    # ── Pédagogie (rows 39-40 Excel)
    p1, p2, p3 = st.columns(3)
    with p1: st.markdown("""<div class="ped" style="background:#EAF6EE">
      <div class="ped-ico">💶</div><div class="ped-tit" style="color:#009FA3">Le côté vert (+)</div>
      <div class="ped-txt">Ce que vous percevez : loyers encaissés + économie d'impôt grâce au dispositif Jeanbrun.</div></div>""", unsafe_allow_html=True)
    with p2: st.markdown("""<div class="ped" style="background:#FEF0EC">
      <div class="ped-ico">🏦</div><div class="ped-tit" style="color:#EA653D">Le côté rouge (−)</div>
      <div class="ped-txt">Ce que vous déboursez : mensualité de crédit + charges d'exploitation annuelles (gestion / GLI / taxe foncière / assurance PNO / provisions menus travaux ; ces charges sont estimées).</div></div>""", unsafe_allow_html=True)
    with p3: st.markdown("""<div class="ped" style="background:#EEF2FB">
      <div class="ped-ico">📊</div><div class="ped-tit" style="color:#3761AD">Le gain fiscal — 2 composantes</div>
      <div class="ped-txt">Déficit naturel (acquis sans Jeanbrun) + avantage lié à l'amortissement Jeanbrun. Les deux s'additionnent.</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · www.medicis-immobilier-neuf.fr · Simulation personnalisée non contractuelle · Hypothèses d\'indexation et fiscalité constantes · Tout investissement locatif comporte des risques (location / impayés / travaux / baisse de valeur)</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ONGLET 2 — SYNTHÈSE SIMPLIFIÉE (fidèle Excel : layout tabulaire HTML pur)
# ─────────────────────────────────────────────────────────────────
with t2:
    st.markdown('<div class="sec">PROJECTION SIMPLIFIÉE — DISPOSITIF JEANBRUN</div>', unsafe_allow_html=True)
    st.caption("Compte en T • Moyennes mensuelles • Document non contractuel")

    # ── En-tête récap (rows 4-7 Excel) — HTML pur
    st.markdown(f"""
    <div style="display:flex;gap:1.2rem;margin-bottom:.8rem">
      <div style="flex:1">
        <div class="sec blue sm" style="margin-top:0">SITUATION DU FOYER</div>
        <table style="width:100%;font-size:.85rem;border-collapse:collapse">
          <tr><td style="padding:.3rem .4rem">Revenus déclarés</td><td style="padding:.3rem .4rem;font-weight:700">{fe(rev)}</td>
              <td style="padding:.3rem .4rem">Parts</td><td style="padding:.3rem .4rem;font-weight:700">{fn(parts,1)}</td></tr>
          <tr><td style="padding:.3rem .4rem">TMI</td><td style="padding:.3rem .4rem;font-weight:700">{fp(res["tmi_v"])}</td>
              <td style="padding:.3rem .4rem">Éco. fiscale an 1</td><td style="padding:.3rem .4rem;font-weight:700">{fe(res["eco1"])}</td></tr>
          <tr><td style="padding:.3rem .4rem">Mensualité crédit</td><td style="padding:.3rem .4rem;font-weight:700">{fe(res["mens_tot"])}</td>
              <td style="padding:.3rem .4rem">Apport</td><td style="padding:.3rem .4rem;font-weight:700">{fe(apport)}</td></tr>
        </table>
      </div>
      <div style="flex:1">
        <div class="sec teal sm" style="margin-top:0">OPÉRATION IMMOBILIÈRE</div>
        <table style="width:100%;font-size:.85rem;border-collapse:collapse">
          <tr><td style="padding:.3rem .4rem">Prix d'acquisition</td><td style="padding:.3rem .4rem;font-weight:700">{fe(prix)}</td>
              <td style="padding:.3rem .4rem">Zone</td><td style="padding:.3rem .4rem;font-weight:700">{zone}</td></tr>
          <tr><td style="padding:.3rem .4rem">Surface pondérée</td><td style="padding:.3rem .4rem;font-weight:700">{fn(res['sp'],1)} m²</td>
              <td colspan="2"></td></tr>
          <tr><td style="padding:.3rem .4rem">Loyer mensuel initial</td><td style="padding:.3rem .4rem;font-weight:700">{fe(res["lmens"])}</td>
              <td colspan="2" style="padding:.3rem .4rem;font-weight:600;color:#888">{type_loyer}</td></tr>
        </table>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Les 3 horizons — HTML pur (fidèle rows 11-33 Excel)
    def horizon_html(h, label, n, bc, bg, icon):
        ef = h["ef"]; ec = "#EA653D" if ef < 0 else "#009FA3"
        return f"""
        <div class="sec" style="background:{bc}">{icon} {label}</div>
        <div style="font-size:.78rem;color:#888;margin-bottom:.5rem">Moyennes mensuelles calculées sur {n} ans ({n*12} mois)</div>
        <div style="display:flex;gap:1rem;align-items:flex-start">
          <!-- CE QUI RENTRE -->
          <div style="flex:2.5">
            <div style="color:#2e7d32;font-weight:700;font-size:.8rem;margin-bottom:.35rem;text-align:center">✚ CE QUI RENTRE (+)</div>
            <table style="width:100%;border-collapse:collapse;font-size:.85rem">
              <tr style="border-bottom:1px solid #eee"><td style="padding:.35rem .4rem">Loyer mensuel moyen</td>
                  <td style="padding:.35rem .4rem;text-align:center;font-weight:700;color:#2e7d32">{fe(h['lm'])}</td></tr>
              <tr style="border-bottom:1px solid #eee"><td style="padding:.35rem .4rem">Gain fiscal à réinvestir / mois</td>
                  <td style="padding:.35rem .4rem;text-align:center;font-weight:700;color:#2e7d32">{fe(h['gm'])}</td></tr>
              <tr style="border-top:2px solid #2e7d32"><td style="padding:.4rem;font-weight:700;color:#2e7d32">TOTAL ENTRÉES</td>
                  <td style="padding:.4rem;text-align:center;font-weight:700;color:#2e7d32">{fe(h['te'])}</td></tr>
            </table>
          </div>
          <!-- CE QUI SORT -->
          <div style="flex:2.5">
            <div style="color:#c62828;font-weight:700;font-size:.8rem;margin-bottom:.35rem;text-align:center">− CE QUI SORT (−)</div>
            <table style="width:100%;border-collapse:collapse;font-size:.85rem">
              <tr style="border-bottom:1px solid #eee"><td style="padding:.35rem .4rem">Mensualité de crédit</td>
                  <td style="padding:.35rem .4rem;text-align:center;font-weight:700;color:#c62828">{fe(h['cm'])}</td></tr>
              <tr style="border-bottom:1px solid #eee"><td style="padding:.35rem .4rem">Charges d'exploitation / mois</td>
                  <td style="padding:.35rem .4rem;text-align:center;font-weight:700;color:#c62828">{fe(h['chm'])}</td></tr>
              <tr style="border-top:2px solid #c62828"><td style="padding:.4rem;font-weight:700;color:#c62828">TOTAL SORTIES</td>
                  <td style="padding:.4rem;text-align:center;font-weight:700;color:#c62828">{fe(h['ts'])}</td></tr>
            </table>
          </div>
          <!-- EFFORT + BILAN -->
          <div style="flex:3;background:{bg};border-radius:9px;padding:.85rem;border-top:4px solid {bc}">
            <div style="display:flex;gap:.6rem;align-items:flex-start;margin-bottom:.4rem">
              <div style="flex:1">
                <div style="font-size:.65rem;color:#888;text-transform:uppercase;letter-spacing:.04em">EFFORT D'INVESTISSEMENT MENSUEL MOYEN</div>
                <div style="font-size:1.3rem;font-weight:800;color:{ec};margin:.15rem 0">{fe(abs(ef))}</div>
                <div style="font-size:.72rem;color:#888">← Reste à charge mensuel réel</div>
              </div>
              <div style="width:1px;background:rgba(0,0,0,.12);align-self:stretch"></div>
              <div style="flex:1">
                <div style="font-size:.65rem;color:#888;text-transform:uppercase;letter-spacing:.04em">AVANTAGES FISCAUX CUMULÉS</div>
                <div style="font-size:1.3rem;font-weight:800;color:#3761AD;margin:.15rem 0">{fe(h['gft'])}</div>
                <div style="font-size:.72rem;color:#888">dont <b style="color:#3761AD">{fe(h['dont_j'])}</b> Jeanbrun</div>
              </div>
            </div>
            <hr style="margin:.3rem 0;border:none;border-top:1px solid #ddd">
            <div style="font-size:.77rem;line-height:1.9">
              <b>Capital constitué (net PV)</b> : {fe(h['cap0'])}<br>
              <span style="color:#888">dont déficit naturel (intérêts) : {fe(h['dont_d'])}</span><br>
              <span style="color:#3761AD">dont Jeanbrun (amortissement) : {fe(h['dont_j'])}</span>
            </div>
          </div>
        </div>
        """

    for lbl, hk, n, bc, bg, icon in [
        ("HORIZON 9 ANS — COMPTE EN T", "h9", 9, "#3761AD", "#EEF2FB", "🔹"),
        ("HORIZON 15 ANS — COMPTE EN T", "h15", 15, "#009FA3", "#E4F5F5", "🔸"),
        ("HORIZON 25 ANS — COMPTE EN T", "h25", 25, "#EA653D", "#FEF0EC", "⭐"),
    ]:
        st.markdown(horizon_html(res[hk], lbl, n, bc, bg, icon), unsafe_allow_html=True)

    # ── Pédagogie (rows 36-43 Excel)
    st.markdown("""<hr style="margin:1.2rem 0">
    <div style="font-size:.82rem;line-height:1.8;padding:.6rem .8rem;background:#f9f9f9;border-radius:8px;border-left:4px solid #14415C">
      <b style="color:#14415C">COMMENT LIRE CE TABLEAU</b><br>
      ▸ Le côté <b style="color:#009FA3">VERT (+)</b> = ce que vous percevez : loyers + économie d'impôt grâce au dispositif Jeanbrun.<br>
      ▸ Le côté <b style="color:#EA653D">ROUGE (−)</b> = ce que vous déboursez : mensualité de crédit + charges d'exploitation.<br>
      ▸ L'<b>EFFORT D'ÉPARGNE</b> = reste à charge réel. Un chiffre négatif = complément mensuel à prévoir.<br>
      ▸ Le « Gain fiscal total » se décompose en deux parties qui s'additionnent :<br>
      <span style="margin-left:1.2rem">– « dont déficit naturel » : l'économie liée aux intérêts d'emprunt, acquise même sans le Jeanbrun.</span><br>
      <span style="margin-left:1.2rem">– « dont Jeanbrun » : l'économie supplémentaire apportée par l'amortissement du dispositif.</span><br>
      ▸ Ce document est une simulation non contractuelle. Hypothèses d'indexation et fiscalité constantes.
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · www.medicis-immobilier-neuf.fr</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ONGLET 3 — SYNTHÈSE DÉTAILLÉE (fidèle Excel)
# ─────────────────────────────────────────────────────────────────
with t3:
    st.markdown('<div class="sec">PROJECTION FINANCIÈRE — DISPOSITIF JEANBRUN</div>', unsafe_allow_html=True)

    # ── En-tête compact : 1 seule bande de KPIs (HTML)
    st.markdown(f"""<div style="display:flex;flex-wrap:wrap;gap:.4rem .6rem;margin:.3rem 0 .6rem;font-size:.72rem">
      <div style="background:#EEF2FB;border-left:3px solid #3761AD;border-radius:4px;padding:.3rem .55rem;flex:1;min-width:110px">
        <span style="color:#888">Revenus</span> <b style="color:#14415C">{fe(rev)}</b> · <span style="color:#888">TMI</span> <b style="color:#14415C">{fp(res['tmi_v'])}</b> · <span style="color:#888">Parts</span> <b style="color:#14415C">{fn(parts,1)}</b></div>
      <div style="background:#E4F5F5;border-left:3px solid #009FA3;border-radius:4px;padding:.3rem .55rem;flex:1;min-width:110px">
        <span style="color:#888">Prix</span> <b style="color:#14415C">{fe(prix)}</b> · <span style="color:#888">Zone</span> <b style="color:#14415C">{zone}</b> · <span style="color:#888">Loyer</span> <b style="color:#14415C">{fe(res['lmens'])}/m</b></div>
      <div style="background:#FEF0EC;border-left:3px solid #EA653D;border-radius:4px;padding:.3rem .55rem;flex:1;min-width:110px">
        <span style="color:#888">Empr.</span> <b style="color:#14415C">{fe(res['mempr'])}</b> · <span style="color:#888">Mens.</span> <b style="color:#14415C">{fe(res['mens_tot'])}</b> · <span style="color:#888">Apport</span> <b style="color:#14415C">{fe(apport_v)}</b></div>
      <div style="background:#E3EAF0;border-left:3px solid #14415C;border-radius:4px;padding:.3rem .55rem;flex:1;min-width:110px">
        <span style="color:#888">Amt.</span> <b style="color:#14415C">{fe(res['amort_an'])}/an</b> · <span style="color:#888">Base</span> <b style="color:#14415C">{fe(res['base_a'])}</b> · <span style="color:#888">Éco.an1</span> <b style="color:#009FA3">{fe(res['eco1'])}</b></div>
    </div>""", unsafe_allow_html=True)

    # ── Tableau 25 ans — HTML pur, compact, alternance couleurs, format €
    st.markdown('<div class="sec ora" style="margin-top:0">PROJECTION ANNUELLE — 25 ANS</div>', unsafe_allow_html=True)

    det_cols = ["An", "Loyers", "Remb. prêt", "Charges", "Amt. JB", "RF net imp.", "Impôt av.", "Impôt ap.", "Éco. fisc.", "Effort/m", "Cap. 0%", "Cap. 1,5%", "Amt. rest."]
    ths_det = "".join(f'<th style="padding:.22rem .3rem;white-space:nowrap">{c}</th>' for c in det_cols)

    rows_det_html = ""
    for i, a in enumerate(ann):
        bg_row = "#f7f9fc" if i % 2 == 0 else "#ffffff"
        # Highlight years 9, 15, 25
        if a["an"] == 9:
            bg_row = "#dce6f7"
        elif a["an"] == 15:
            bg_row = "#d4efef"
        elif a["an"] == 25:
            bg_row = "#fde3da"
        vals = [
            a["an"],
            fe(a["lo"]), fe(a["remb"]), fe(a["ch"]), fe(a["amort_yr"]),
            fe(a["rfn"] + a["ded"]),
            fe(a["ir_av"] + a["ps_av"]), fe(a["ir_ap"] + a["ps_ap"]),
            fe(a["eco"]), fe(a["effort"]),
            fe(a["cap0"]), fe(a["cap15"]),
            fe(res["base_a"] - a["amt_cum"]),
        ]
        tds = f'<td style="padding:.2rem .3rem;font-weight:700;text-align:center">{vals[0]}</td>'
        tds += "".join(f'<td style="padding:.2rem .3rem;text-align:right;white-space:nowrap">{v}</td>' for v in vals[1:])
        rows_det_html += f'<tr style="background:{bg_row}">{tds}</tr>\n'

    # TOTAL row
    tot_vals = [
        "TOT",
        fe(sum(a["lo"] for a in ann)), fe(sum(a["remb"] for a in ann)),
        fe(sum(a["ch"] for a in ann)), fe(sum(a["amort_yr"] for a in ann)),
        "", "", "",
        fe(sum(a["eco"] for a in ann)), "", "", "", "",
    ]
    tds_tot = f'<td style="padding:.25rem .3rem;font-weight:800;text-align:center">{tot_vals[0]}</td>'
    tds_tot += "".join(f'<td style="padding:.25rem .3rem;text-align:right;font-weight:700;white-space:nowrap">{v}</td>' for v in tot_vals[1:])
    rows_det_html += f'<tr style="background:#14415C;color:#fff;font-weight:700">{tds_tot}</tr>\n'

    det_table_html = f"""<div style="overflow-x:auto">
    <table style="width:100%;border-collapse:collapse;font-size:.7rem;font-family:Poppins,sans-serif">
      <thead><tr style="background:#14415C;color:#fff;font-size:.62rem;text-transform:uppercase;letter-spacing:.03em">{ths_det}</tr></thead>
      <tbody>{rows_det_html}</tbody>
    </table></div>"""
    st.markdown(det_table_html, unsafe_allow_html=True)

    # ── Graphique capital net
    st.markdown('<div class="sec blue sm no-print">📈 Capital net constitué par année</div>', unsafe_allow_html=True)
    chart_capital_net(ann)

    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · Simulation personnalisée non contractuelle · Hypothèses d\'indexation et fiscalité constantes</div>', unsafe_allow_html=True)



# ─────────────────────────────────────────────────────────────────
# ONGLET 4 — REVENTE & PLUS-VALUE (fidèle Excel : tableau structuré)
# ─────────────────────────────────────────────────────────────────
with t4:
    st.markdown('<div class="sec">SIMULATION DE REVENTE — DISPOSITIF JEANBRUN</div>', unsafe_allow_html=True)
    st.caption("Calcul pédagogique de la plus-value et de votre enrichissement net à la revente")

    def revente_col_html(an_r, lbl, bc, bg, icon):
        """Génère le HTML d'une colonne Revente fidèle Excel."""
        a = ann[an_r - 1]
        vb0 = prix; vb15 = prix * (1.015 ** an_r)
        pv0 = a["pv0"]; pv15 = a["pv15"]
        pvi0 = a["pvi0"]; pps0 = a["pps0"]; pvi15 = a["pvi15"]; pps15 = a["pps15"]
        ir0 = pvi0 * TAUX_IR_PV; ps0 = pps0 * TAUX_PS_PV
        ir15 = pvi15 * TAUX_IR_PV; ps15 = pps15 * TAUX_PS_PV
        s0 = max(0., surtaxe(pvi0)); s15 = max(0., surtaxe(pvi15))
        ipv0 = a["ipv0"]; ipv15 = a["ipv15"]
        cap0 = a["cap0"]; cap15 = a["cap15"]
        cap0c = "#009FA3" if cap0 > 0 else "#EA653D"
        cap15c = "#009FA3" if cap15 > 0 else "#EA653D"
        return f"""<div style="flex:1">
        <div class="sec" style="background:{bc};margin-top:0">{icon} {lbl}</div>
        <table style="width:100%;border-collapse:collapse;font-size:.78rem">
          <tr><td colspan="3" style="padding:.4rem .3rem;font-weight:700;color:{bc};border-bottom:2px solid {bc}">PRIX DE VENTE</td></tr>
          <tr><td style="padding:.25rem .3rem">Prix vente (0%)</td><td style="text-align:right;font-weight:700">{fe(vb0)}</td><td></td></tr>
          <tr style="border-bottom:1px solid #eee"><td style="padding:.25rem .3rem">Prix vente (1,5%/an)</td><td style="text-align:right;font-weight:700">{fe(vb15)}</td><td></td></tr>
          <tr><td colspan="3" style="padding:.4rem .3rem;font-weight:700;color:{bc};border-bottom:2px solid {bc}">CALCUL DE LA PLUS-VALUE</td></tr>
          <tr><td style="padding:.2rem .3rem">Prix d'acquisition</td><td style="text-align:right">{fe(prix)}</td><td></td></tr>
          <tr><td style="padding:.2rem .3rem">+ Forfait frais acq. (7,5%)</td><td style="text-align:right">{fe(a['fac'])}</td><td></td></tr>
          <tr><td style="padding:.2rem .3rem">+ Forfait travaux 15% (si > 5 ans)</td><td style="text-align:right">{fe(a['ftv'])}</td><td></td></tr>
          <tr><td style="padding:.2rem .3rem">– Amortissements réintégrés</td><td style="text-align:right">{fe(a['amt_cum'])}</td><td></td></tr>
          <tr style="border-bottom:1px solid #eee"><td style="padding:.25rem .3rem;font-weight:700">= Prix de revient corrigé</td><td style="text-align:right;font-weight:700">{fe(a['pr'])}</td><td></td></tr>
          <tr><td style="padding:.25rem .3rem">➜ PV brute (0%)</td><td style="text-align:right;font-weight:700;color:{bc}">{fe(pv0)}</td><td></td></tr>
          <tr style="border-bottom:1px solid #eee"><td style="padding:.25rem .3rem">➜ PV brute (1,5%)</td><td style="text-align:right;font-weight:700;color:{bc}">{fe(pv15)}</td><td></td></tr>
          <tr><td colspan="3" style="padding:.35rem .3rem;font-weight:700;color:{bc};border-bottom:2px solid {bc}">ABATTEMENTS DURÉE DE DÉTENTION</td></tr>
          <tr><td style="padding:.2rem .3rem">Abattement IR (%)</td><td style="text-align:right">{fp(a['ai'],1)}</td><td></td></tr>
          <tr><td style="padding:.15rem .3rem;font-size:.72rem">   PV imposable IR</td><td style="text-align:right;font-size:.72rem">(0%) {fe(pvi0)}</td><td style="text-align:right;font-size:.72rem">(1,5%) {fe(pvi15)}</td></tr>
          <tr><td style="padding:.2rem .3rem">Abattement PS (%)</td><td style="text-align:right">{fp(a['ap'],1)}</td><td></td></tr>
          <tr style="border-bottom:1px solid #eee"><td style="padding:.15rem .3rem;font-size:.72rem">   PV imposable PS</td><td style="text-align:right;font-size:.72rem">(0%) {fe(pps0)}</td><td style="text-align:right;font-size:.72rem">(1,5%) {fe(pps15)}</td></tr>
          <tr><td colspan="3" style="padding:.35rem .3rem;font-weight:700;color:{bc};border-bottom:2px solid {bc}">IMPÔT SUR LA PLUS-VALUE</td></tr>
          <tr><td style="padding:.15rem .3rem;font-size:.72rem">IR (19%)</td><td style="text-align:right;font-size:.72rem">(0%) {fe(ir0)}</td><td style="text-align:right;font-size:.72rem">(1,5%) {fe(ir15)}</td></tr>
          <tr><td style="padding:.15rem .3rem;font-size:.72rem">PS (17,2%)</td><td style="text-align:right;font-size:.72rem">(0%) {fe(ps0)}</td><td style="text-align:right;font-size:.72rem">(1,5%) {fe(ps15)}</td></tr>
          <tr><td style="padding:.15rem .3rem;font-size:.72rem">Surtaxe</td><td style="text-align:right;font-size:.72rem">(0%) {fe(s0)}</td><td style="text-align:right;font-size:.72rem">(1,5%) {fe(s15)}</td></tr>
          <tr style="border-bottom:1px solid #eee"><td style="padding:.25rem .3rem;font-weight:700">= TOTAL IMPÔT PV</td><td style="text-align:right;font-weight:700;color:#EA653D">(0%) {fe(ipv0)}</td><td style="text-align:right;font-weight:700;color:#EA653D">(1,5%) {fe(ipv15)}</td></tr>
          <tr><td colspan="3" style="padding:.35rem .3rem;font-weight:700;color:{bc};border-bottom:2px solid {bc}">CAPITAL RESTANT DÛ</td></tr>
          <tr style="border-bottom:1px solid #eee"><td style="padding:.25rem .3rem">CRD à la date de revente</td><td style="text-align:right;font-weight:700" colspan="2">{fe(a['crd'])}</td></tr>
          <tr><td colspan="3" style="padding:.35rem .3rem;font-weight:700;color:{bc};border-bottom:2px solid {bc}">CAPITAL CONSTITUÉ NET</td></tr>
          <tr><td style="padding:.25rem .3rem">= Prix vente – CRD – Impôt PV (0%)</td><td style="text-align:right;font-weight:800;color:{cap0c}" colspan="2">{fe(cap0)}</td></tr>
          <tr><td style="padding:.25rem .3rem">= Prix vente – CRD – Impôt PV (1,5%)</td><td style="text-align:right;font-weight:800;color:{cap15c}" colspan="2">{fe(cap15)}</td></tr>
        </table></div>"""

    st.markdown(f"""<div style="display:flex;gap:.8rem">
    {revente_col_html(9, "REVENTE À 9 ANS", "#3761AD", "#EEF2FB", "🔹")}
    {revente_col_html(15, "REVENTE À 15 ANS", "#009FA3", "#E4F5F5", "🔸")}
    {revente_col_html(25, "REVENTE À 25 ANS", "#EA653D", "#FEF0EC", "⭐")}
    </div>""", unsafe_allow_html=True)

    # ── Pédagogie (fidèle Excel rows 45-49)
    st.markdown("""<div style="margin-top:.8rem;padding:.7rem .9rem;background:#f9f9f9;border-radius:8px;border-left:4px solid #14415C;font-size:.8rem;line-height:1.7">
      <b style="color:#14415C">💡 COMPRENDRE VOTRE ENRICHISSEMENT</b><br>
      ▸ Le capital constitué net = ce qui vous reste en poche après avoir soldé votre crédit et payé l'impôt sur la plus-value.<br>
      ▸ Plus vous détenez longtemps, plus les abattements pour durée de détention réduisent l'impôt PV : exonération totale d'IR à 22 ans, de PS à 30 ans.<br>
      ▸ L'amortissement Jeanbrun est réintégré dans la plus-value à la revente, mais l'économie d'impôt réalisée chaque année (déficit foncier) vous a déjà profité.<br>
      ▸ Le scénario 0% est conservateur (pas de hausse des prix). Le +1,5%/an reflète l'évolution historique moyenne du marché immobilier français.
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · Simulation personnalisée non contractuelle</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ONGLET 5 — MOTEUR (alternance couleurs)
# ─────────────────────────────────────────────────────────────────
with t5:
    st.markdown('<div class="sec">⚙️ MOTEUR — Données brutes · Colonnes Excel V9</div>', unsafe_allow_html=True)

    # Construire le HTML du tableau avec alternance
    header_cols = ["An","Loyers","Charges","Intérêts","Assur.","Amt.JB","CRD",
        "RF aut.","Tot.av.","IR av.","PS av.",
        "RF bruts","Ch.fin.","Ch.nf","RF net","Déd.RG","Déf.gén","Stock d.","Déf.imp","RF tax.",
        "Rev.ap.","IR ap.","PS ap.","Éco.","Enrich.",
        "Eff/m","CF cum","Amt.cum","PV br.","Ab.IR","PV i.IR","Ab.PS","PV i.PS","Imp.PV",
        "TRI","CSG av","CSG ap","Cap.0%","Cap.1,5%"]

    def fmt(v, d=0):
        try:
            return f"{float(v):,.{d}f}".replace(",", "\u202f")
        except:
            return str(v) if v is not None else ""

    rows_html = ""
    for a in ann:
        tri_str = fp(a["tri"]) if a["tri"] is not None else "—"
        vals = [
            a["an"], fmt(a["lo"],0), fmt(a["ch"],0), fmt(a["int_a"],0), fmt(a["ass_a"],0),
            fmt(a["amort_yr"],0), fmt(a["crd"],0),
            fmt(rfa,0), fmt(a["tot_av"],0), fmt(a["ir_av"],0), fmt(a["ps_av"],0),
            fmt(a["rf_b"],0), fmt(a["ch_f"],0), fmt(a["ch_nf"],0), fmt(a["rfn"],0),
            fmt(a["ded"],0), fmt(a["def_g"],0), fmt(a["stock_def"],0), fmt(a["def_imp"],0), fmt(a["rfnt"],0),
            fmt(a["rev_ap"],0), fmt(a["ir_ap"],0), fmt(a["ps_ap"],0), fmt(a["eco"],0), fmt(a["enrichissement"],0),
            fmt(a["effort"],0), fmt(a["cashflow_cum"],0), fmt(a["amt_cum"],0),
            fmt(a["pv0"],0), fp(a["ai"]), fmt(a["pvi0"],0), fp(a["ap"]), fmt(a["pps0"],0), fmt(a["ipv0"],0),
            tri_str, fmt(a["csg_ded_av"],0), fmt(a["csg_ded_ap"],0), fmt(a["cap0"],0), fmt(a["cap15"],0),
        ]
        tds = "".join(f"<td>{v}</td>" for v in vals)
        rows_html += f"<tr>{tds}</tr>\n"

    ths = "".join(f"<th>{h}</th>" for h in header_cols)
    moteur_html = f"""<div style="overflow-x:auto;max-height:620px;overflow-y:auto">
    <table class="alt-table"><thead><tr>{ths}</tr></thead><tbody>{rows_html}</tbody></table></div>"""
    st.markdown(moteur_html, unsafe_allow_html=True)

    st.markdown("""<div style="font-size:.75rem;margin-top:.5rem;color:#888;line-height:1.6">
    <b>Colonnes clés :</b> RF net = RF bruts − Ch.fin − Ch.nf · Déd.RG = déficit imputable RG (plaf. 10 700 €) ·
    Stock d. = report 10 ans · TRI = taux de rentabilité interne si revente · CSG = CSG déductible 6,8 %
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · Document de travail interne</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ONGLET 6 — RÈGLES FISCALES (copie mot pour mot de l'Excel)
# ─────────────────────────────────────────────────────────────────
with t6:

    def rule_block(icon, title, body, formula, ref):
        """Bloc de règle fiscale fidèle au format Excel."""
        body_html = body.replace("\n", "<br>")
        return f"""<div style="display:flex;gap:.7rem;margin:.5rem 0 .8rem;align-items:flex-start">
          <div style="font-size:1.3rem;min-width:1.8rem;text-align:center">{icon}</div>
          <div style="flex:1">
            <div style="font-weight:700;font-size:.85rem;margin-bottom:.3rem;color:#14415C">{title}</div>
            <div style="font-size:.78rem;line-height:1.65;color:#333">{body_html}</div>
            <div style="font-size:.75rem;margin-top:.3rem;color:#555"><b>Formule :</b> <code style="background:#f4f4f4;padding:.1rem .3rem;border-radius:3px">{formula}</code></div>
            <div style="font-size:.72rem;color:#888;margin-top:.15rem">{ref}</div>
          </div></div>"""

    st.markdown('<div class="sec">RÈGLES FISCALES DU SIMULATEUR JEANBRUN</div>', unsafe_allow_html=True)
    st.caption("Synthèse des mécaniques fiscales intégrées au modèle • Document pédagogique")

    # ── 1️⃣ IR
    st.markdown('<div class="sec blue">1️⃣ IMPÔT SUR LE REVENU — Barème progressif 2026</div>', unsafe_allow_html=True)
    st.markdown(rule_block("📊", "Barème progressif par tranches",
        "L'IR est calculé par application du barème progressif au quotient familial (revenu / nb parts), puis multiplié par le nombre de parts.\nTranches : 0 % → 11 % → 30 % → 41 % → 45 %.",
        "IR = Rev × Taux_tranche − Réduction × Nb_parts",
        "📖 Art. 197 du CGI • Barème applicable aux revenus 2025 (déclarés en 2026)"), unsafe_allow_html=True)
    st.markdown(rule_block("👨‍👩‍👧", "Plafonnement du quotient familial",
        "L'avantage fiscal procuré par chaque demi-part supplémentaire au-delà de 2 parts est plafonné à 1 759 € par demi-part.\nLe simulateur compare l'IR « avec QF » et l'IR « sur 2 parts plafonné » et retient le plus élevé.",
        "IR = MAX(IR_QF, IR_1part − (N−1) × Plafond_QF)",
        "📖 Art. 197-I-2 du CGI • Plafond 2026 : 1 759 €/demi-part"), unsafe_allow_html=True)
    st.markdown(rule_block("💶", "CSG déductible (en N+1)",
        "La CSG payée sur les revenus fonciers est partiellement déductible du revenu global de l'année suivante, au taux de 6,8 % de la base soumise aux prélèvements sociaux.\nLe modèle calcule cette déduction tant pour la situation « avant opération » (sur les RF autres) que pour la situation « après opération » (sur le RF net taxable global).",
        "CSG_déd(N) = RF_net_taxable(N) × 6,8 % → déduite du revenu global en N+1",
        "📖 Art. 154 quinquies du CGI • Taux : 6,8 % (fraction déductible de la CSG à 9,2 %)"), unsafe_allow_html=True)

    # ── 2️⃣ RF
    st.markdown('<div class="sec teal">2️⃣ REVENUS FONCIERS — Globalisation & déficit (2044)</div>', unsafe_allow_html=True)
    st.markdown(rule_block("🔗", "Globalisation obligatoire des revenus fonciers",
        "Le résultat foncier se calcule GLOBALEMENT pour l'ensemble du patrimoine locatif du foyer, et non bien par bien. Le simulateur additionne donc les loyers Jeanbrun ET les RF d'autres biens avant d'imputer les charges financières.\nC'est cette globalisation qui permet aux RF existants d'absorber les intérêts d'emprunt, évitant la constitution de déficits d'intérêts fictifs.",
        "RF_bruts_globaux = Loyers_Jeanbrun + RF_autres",
        "📖 Art. 28 à 31 du CGI • Formulaire 2044 ligne 420"), unsafe_allow_html=True)
    st.markdown(rule_block("⚖️", "Partition charges financières / non-financières",
        "En cas de déficit foncier global, le traitement diffère selon la nature des charges excédentaires :\n• Si les RF globaux couvrent les charges financières (Q ≥ R) : le déficit provient des charges non-financières → déductible du revenu global (plafond 10 700 €).\n• Si les RF globaux ne couvrent PAS les charges financières (Q < R) : l'excédent d'intérêts est reportable sur les RF futurs (10 ans), les charges non-fin. restent déductibles du RG.",
        "Déd_RG = MIN(Déficit_charges_non_fin, 10 700)",
        "📖 Art. 156-I-3° du CGI • BOI-RFPI-BASE-30-20"), unsafe_allow_html=True)
    st.markdown(rule_block("🔄", "Déficit reportable sur 10 ans",
        "L'excédent de déficit non imputable sur le revenu global (au-delà de 10 700 €) ainsi que les déficits d'intérêts sont reportables sur les revenus fonciers positifs des 10 années suivantes.\nLe stock est géré année par année avec péremption automatique à 10 ans.",
        "Stock(N) = Stock(N−1) + Généré(N) − Imputé(N−1) − Périmé(>10 ans)",
        "📖 Art. 156-I-3° alinéa 4 du CGI"), unsafe_allow_html=True)
    st.markdown(rule_block("💰", "Prélèvements sociaux sur RF nets",
        "Les prélèvements sociaux (17,2 %) s'appliquent sur le revenu foncier net taxable positif.\nEn phase de déficit foncier (RF net ≤ 0), les PS sont nuls — y compris sur les RF d'autres biens, car la base est le résultat foncier GLOBAL, pas bien par bien.",
        "PS = RF_net_taxable × 17,2 % (si positif, sinon 0)",
        "📖 Art. L. 136-6 du CSS • Taux 2026 : 9,2 % CSG + 0,5 % CRDS + 7,5 % PS"), unsafe_allow_html=True)

    # ── 3️⃣ Jeanbrun
    st.markdown('<div class="sec ora">3️⃣ DISPOSITIF JEANBRUN — Amortissement déductible</div>', unsafe_allow_html=True)
    st.markdown(rule_block("🏗️", "Base et taux d'amortissement",
        "L'amortissement Jeanbrun porte sur 80 % du prix d'acquisition (hors terrain) à un taux qui dépend du type de loyer pratiqué :\n• Intermédiaire : 3,5 % → plafond 8 000 €/an\n• Social : 4,5 % → plafond 10 000 €/an\n• Très social : 5,5 % → plafond 12 000 €/an\nLe plafond est global (tous biens Jeanbrun confondus pour le foyer).",
        "Amt = MIN(Base_80% × Taux, Plafond_annuel)",
        "📖 Art. 12 octies de la LF 2026, créant le i du 1° du I de l'art. 31 du CGI • Plafonds par foyer fiscal"), unsafe_allow_html=True)
    st.markdown(rule_block("⚡", "L'amortissement crée du déficit foncier",
        "C'est le premier dispositif fiscal permettant l'amortissement en location NUE. Jusqu'ici, seul le LMNP (location meublée) offrait cette possibilité.\nL'amortissement Jeanbrun est une charge déductible des revenus fonciers et PEUT générer du déficit foncier imputable sur le revenu global (dans la limite de 10 700 €).\nC'est le principal levier fiscal du dispositif : il transforme un revenu foncier positif en déficit.",
        "RF_net = Loyers + RF_autres − Charges_fin − Charges_non_fin − Amort_JB",
        "📖 Art. 12 octies LF 2026 (i et j du 1° du I de l'art. 31) combiné avec art. 156-I-3° du CGI"), unsafe_allow_html=True)
    st.markdown(rule_block("📋", "Engagement locatif",
        "L'investisseur s'engage à louer le bien nu, à titre de résidence principale du locataire, pendant une durée fixe de 9 ans (non modulable).\nLe loyer est plafonné selon le type de loyer choisi : intermédiaire (−15 % vs marché), social (−30 %) ou très social (−45 %). Des plafonds de ressources du locataire s'appliquent.\nPas de zonage géographique : tout le territoire français est éligible.\nSeuls les appartements en immeubles collectifs sont éligibles (maisons individuelles exclues).\nInterdiction de louer à un membre du foyer fiscal ou à un ascendant/descendant.\nLogement neuf : RE2020 + DPE classe A ou B exigés. Ancien : travaux ≥ 30 % du prix d'acquisition.\nAcquisitions éligibles : entre la publication de la LFI 2026 et le 31 décembre 2028.",
        "Engagement = 9 ans fermes · Loyer ≤ Plafond × SP × Coeff",
        "📖 Art. 12 octies de la LF 2026 • Engagement 9 ans • Plafonds de loyers par type (décret à paraître)"), unsafe_allow_html=True)

    # ── 4️⃣ Charges
    st.markdown('<div class="sec blue">4️⃣ CHARGES DÉDUCTIBLES — Frais de financement</div>', unsafe_allow_html=True)
    st.markdown(rule_block("🏦", "Frais initiaux de financement (Année 1)",
        "Les frais de dossier bancaire, de garantie (ex: Crédit Logement) et de courtage sont des charges financières intégralement déductibles, l'année de leur paiement (Année 1 uniquement).\nLe simulateur les ajoute aux charges financières de l'Année 1, ce qui augmente le déficit initial.",
        "R(An 1) = Intérêts + Assurance + Frais_garantie_dossier_courtage",
        "📖 Art. 31-I-1°-d du CGI • BOI-RFPI-BASE-20-10 §30 à §60"), unsafe_allow_html=True)
    st.markdown(rule_block("📈", "Intérêts d'emprunt et assurance",
        "Les intérêts d'emprunt et les primes d'assurance emprunteur constituent les charges financières récurrentes, déductibles chaque année pendant toute la durée du prêt.\nEn cas de déficit, les intérêts excédentaires (non couverts par les loyers globaux) sont reportables sur les RF futurs, tandis que les charges non-financières sont déductibles du RG.",
        "Charges_fin(N) = Intérêts(N) + Assurance(N)",
        "📖 Art. 31-I-1°-d du CGI"), unsafe_allow_html=True)

    # ── 5️⃣ PV
    st.markdown('<div class="sec teal">5️⃣ PLUS-VALUE IMMOBILIÈRE — Revente du bien</div>', unsafe_allow_html=True)
    st.markdown(rule_block("🔴", "Réintégration de l'amortissement Jeanbrun",
        "Lors de la revente, l'amortissement cumulé déduit via le Jeanbrun vient MAJORER la plus-value brute (il est soustrait du prix d'acquisition). C'est le « coût de sortie » du dispositif.\nL'art. 12 octies modifie l'art. 150 VB du CGI pour y intégrer explicitement les amortissements déduits au titre des i et j du 1° du I de l'art. 31.\n⚠️ Note : certaines sources contestent cette lecture. La doctrine administrative (BOFiP) n'est pas encore publiée. Le simulateur retient l'hypothèse prudente de la réintégration, conformément au texte voté.",
        "PV_brute = Prix_vente − (Prix_achat + Frais_forfaitaires − Amt_cumulé)",
        "📖 Art. 150 VB III du CGI (modifié par art. 12 octies LF 2026) • Décrets d'application attendus"), unsafe_allow_html=True)
    st.markdown(rule_block("📉", "Abattements pour durée de détention",
        "La PV brute bénéficie d'abattements progressifs selon la durée de détention, avec des barèmes distincts pour l'IR et les PS :\n• IR : 6 %/an de la 6e à la 21e année, 4 % la 22e → exonération totale à 22 ans.\n• PS : 1,65 %/an de la 6e à la 21e, 1,60 % la 22e, 9 %/an de la 23e à la 30e → exo à 30 ans.",
        "PV_nette_IR = PV_brute × (1 − Abatt_IR%)",
        "📖 Art. 150 VC du CGI • Barèmes détaillés dans l'onglet « Barème fiscal »"), unsafe_allow_html=True)
    st.markdown(rule_block("💸", "Imposition : IR 19 % + PS 17,2 % + Surtaxe",
        "La plus-value nette est soumise à :\n• IR au taux forfaitaire de 19 % (sur PV nette après abattement IR).\n• PS au taux de 17,2 % (sur PV nette après abattement PS).\n• Surtaxe progressive si la PV nette IR dépasse 50 000 € (de 2 % à 6 % selon barème).",
        "Impôt_PV = PV_IR × 19 % + PV_PS × 17,2 % + Surtaxe(PV_IR)",
        "📖 Art. 200 B et 1609 nonies G du CGI"), unsafe_allow_html=True)
    st.markdown(rule_block("📐", "Barème de la surtaxe PV (> 50 000 €)",
        "Tranches de la surtaxe sur PV nette imposable IR :\n• 50 001 → 60 000 € : 2 % avec lissage (60 000−PV) × 1/20\n• 60 001 → 100 000 € : 2 %\n• 100 001 → 110 000 € : 3 % avec lissage (110 000−PV) × 1/10\n• 110 001 → 150 000 € : 3 %\n• 150 001 → 160 000 € : 4 % avec lissage (160 000−PV) × 3/20\n• 160 001 → 200 000 € : 4 %\n• 200 001 → 210 000 € : 5 % avec lissage (210 000−PV) × 1/5\n• 210 001 → 250 000 € : 5 %\n• 250 001 → 260 000 € : 6 % avec lissage (260 000−PV) × 1/4\n• Au-delà de 260 000 € : 6 %",
        "Surtaxe = PV × Taux − Lissage",
        "📖 Art. 1609 nonies G du CGI • Barème dans l'onglet « Barème fiscal »"), unsafe_allow_html=True)

    # ── 6️⃣ Abattement
    st.markdown('<div class="sec ora">6️⃣ ABATTEMENT 10 % — Frais professionnels</div>', unsafe_allow_html=True)
    st.markdown(rule_block("📊", "Déduction forfaitaire de 10 % pour frais professionnels",
        "La déduction forfaitaire de 10 % s'applique aux traitements & salaires (Art. 83-3° CGI) et aux pensions de retraite (Art. 158-5-a CGI), avec des plafonds distincts. Elle ne s'applique pas aux revenus des travailleurs non-salariés (BIC/BNC), qui déduisent leurs frais réels.",
        "Salaires : Abatt = MAX(504 × N, MIN(Rev × 10 %, 14 171 × N))\nPensions : Abatt = MAX(442 × N, MIN(Rev × 10 %, 4 321 × N))\nTNS / Indépendants : Abatt = 0  [N = nb déclarants]",
        "📖 Art. 83-3° du CGI (salaires) • Art. 158-5-a du CGI (pensions) • Plafonds applicables aux revenus 2025 (déclarés en 2026)"), unsafe_allow_html=True)

    # ── 7️⃣ Surface pondérée
    st.markdown('<div class="sec blue">7️⃣ SURFACE PONDÉRÉE & PLAFOND DE LOYER</div>', unsafe_allow_html=True)
    st.markdown(rule_block("📐", "Calcul de la surface pondérée (surface utile)",
        "Le plafond de loyer s'applique à la surface pondérée (« surface utile »), qui comprend la surface habitable augmentée de la moitié des surfaces annexes (balcons, loggias, caves... et terrasses dans la limite de 9 m²), le tout plafonné à 16 m² de surfaces annexes brutes (soit 8 m² après division par 2).\nLes jardins privatifs ne sont PAS des annexes : seules les terrasses accessibles en étage ou aménagées sur ouvrage enterré sont retenues.\n⚠️ Si le logement est en RDC, la terrasse est automatiquement exclue du calcul (présumée reposer sur le sol naturel et non sur du bâti).",
        "SP = S_hab + MIN(Balcon + IF(RDC, 0, MIN(Terrasse, 9)), 16) ÷ 2",
        "📖 Art. R. 353-16 du CCH (annexes) • Décret n° 2002-120 (surface utile) • Art. 2 terdecies D annexe III CGI"), unsafe_allow_html=True)
    st.markdown(rule_block("🔢", "Coefficient multiplicateur de loyer",
        "Un coefficient multiplicateur est appliqué au plafond de loyer par m² pour tenir compte de la taille du logement. Il avantage les petites surfaces.\nLe coefficient est plafonné à 1,2.\n⚠️ Ce coefficient est repris par analogie avec le dispositif Pinel. Les décrets d'application du Jeanbrun confirmeront ou ajusteront cette règle.",
        "Coeff = TRUNC(MIN(0,7 + 19 ÷ SP, 1,2), 2) → Loyer max = Plafond/m² × SP × Coeff",
        "📖 Art. 2 terdecies D de l'annexe III au CGI (coefficient Pinel) • Décrets Jeanbrun à paraître"), unsafe_allow_html=True)

    # ── Disclaimer
    st.markdown("""<div style="margin-top:.8rem;padding:.5rem .7rem;background:#fff3cd;border-radius:6px;border-left:4px solid #EA653D;font-size:.73rem;color:#555;line-height:1.6">
    ⚠️ Ce document est fourni à titre pédagogique et ne constitue ni un conseil fiscal ni un conseil en investissement.
    Les règles fiscales sont susceptibles d'évoluer. Consultez un professionnel habilité avant toute décision d'investissement.
    Références législatives vérifiées au 02/2026.
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · www.medicis-immobilier-neuf.fr · Osez dire OUI à l\'immobilier neuf !</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# ONGLET 7 — PLAFONDS LOYERS (fidèle Excel)
# ─────────────────────────────────────────────────────────────────
with t7:
    st.markdown('<div class="sec">PLAFONDS DE LOYERS JEANBRUN (€/m²/mois)</div>', unsafe_allow_html=True)

    st.dataframe(pd.DataFrame([
        {"Zone": "A bis", "Loyer intermédiaire": 19.51, "Loyer social": 15.61, "Loyer très social": 11.71},
        {"Zone": "A",     "Loyer intermédiaire": 14.49, "Loyer social": 11.59, "Loyer très social":  8.69},
        {"Zone": "B1",    "Loyer intermédiaire": 11.68, "Loyer social":  9.34, "Loyer très social":  7.01},
        {"Zone": "B2/C",  "Loyer intermédiaire": 10.15, "Loyer social":  8.12, "Loyer très social":  6.09},
    ]), hide_index=True, use_container_width=True)

    st.markdown(f"""
> **Loyer max légal** = Plafond €/m²/mois × Surface pondérée × Coefficient multiplicateur
> 
> **Votre bien :** Surface pondérée = **{fn(res["sp"],1)} m²** · Coefficient = **{fn(res["coeff"],2)}** · Zone = **{zone}** · Type = **{type_loyer}**
> 
> **Loyer max légal = {fe(res["lmax"])}/mois** · Loyer retenu = **{fe(res["lmens"])}/mois**
""")

    st.markdown('<div class="sec teal sm">PLAFONDS D\'AMORTISSEMENT</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([
        {"Type": "Intermédiaire", "Taux": "3,5 %", "Plafond/an": "8 000 €", "Base": "80 % prix acq."},
        {"Type": "Social",        "Taux": "4,5 %", "Plafond/an": "10 000 €", "Base": "80 % prix acq."},
        {"Type": "Très social",   "Taux": "5,5 %", "Plafond/an": "12 000 €", "Base": "80 % prix acq."},
    ]), hide_index=True, use_container_width=True)

    st.markdown('<div class="sec blue sm">COEFFICIENT MULTIPLICATEUR — Art. 2 terdecies D</div>', unsafe_allow_html=True)
    st.markdown("`Coefficient = TRUNC((0,7 + 19/SP) × 100) / 100` — plafonné à **1,20**")
    st.markdown(f"> Pour SP = {fn(res['sp'],1)} m² : Coefficient = **{fn(res['coeff'],2)}**")

    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · Art. 2 terdecies D ann. III CGI · Plafonds 2025/2026</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ONGLET 8 — BARÈME FISCAL (fidèle Excel)
# ─────────────────────────────────────────────────────────────────
with t8:
    st.markdown('<div class="sec">BARÈME IMPÔT SUR LE REVENU 2026</div>', unsafe_allow_html=True)

    b8a, b8b = st.columns([1.5, 2])
    with b8a:
        st.markdown('<div class="sec blue sm">TRANCHES IR</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame([
            {"Limite inf": "0 €", "Limite sup": "11 600 €", "Taux": "0 %", "Réduction": "0 €"},
            {"Limite inf": "11 600 €", "Limite sup": "29 579 €", "Taux": "11 %", "Réduction": "1 276 €"},
            {"Limite inf": "29 579 €", "Limite sup": "84 577 €", "Taux": "30 %", "Réduction": "6 896 €"},
            {"Limite inf": "84 577 €", "Limite sup": "181 917 €", "Taux": "41 %", "Réduction": "16 199 €"},
            {"Limite inf": "181 917 €", "Limite sup": "∞", "Taux": "45 %", "Réduction": "23 476 €"},
        ]), hide_index=True, use_container_width=True)

        st.markdown(f"""
| Paramètre | Valeur |
|---|---|
| Plafond QF (€/demi-part) | **1 759 €** |
| Plafond déficit foncier RG | **10 700 €** |
| Taux CSG déductible | **6,8 %** |
| Plafond abatt. 10 % salaires | **14 171 €/déclarant** |
| Plancher abatt. 10 % salaires | **504 €/déclarant** |
| Plafond abatt. 10 % pensions | **4 321 €/déclarant** |
| Plancher abatt. 10 % pensions | **442 €/déclarant** |
""")

    with b8b:
        st.markdown('<div class="sec ora sm">SURTAXE PLUS-VALUE IMMOBILIÈRE</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame([
            {"PV nette IR min": "0 €", "PV nette IR max": "50 000 €", "Taux": "0 %", "Lissage": "—"},
            {"PV nette IR min": "50 001 €", "PV nette IR max": "60 000 €", "Taux": "2 %", "Lissage": "(60000−PV)×1/20"},
            {"PV nette IR min": "60 001 €", "PV nette IR max": "100 000 €", "Taux": "2 %", "Lissage": "—"},
            {"PV nette IR min": "100 001 €", "PV nette IR max": "110 000 €", "Taux": "3 %", "Lissage": "(110000−PV)×1/10"},
            {"PV nette IR min": "110 001 €", "PV nette IR max": "150 000 €", "Taux": "3 %", "Lissage": "—"},
            {"PV nette IR min": "150 001 €", "PV nette IR max": "160 000 €", "Taux": "4 %", "Lissage": "(160000−PV)×3/20"},
            {"PV nette IR min": "160 001 €", "PV nette IR max": "200 000 €", "Taux": "4 %", "Lissage": "—"},
            {"PV nette IR min": "200 001 €", "PV nette IR max": "210 000 €", "Taux": "5 %", "Lissage": "(210000−PV)×1/5"},
            {"PV nette IR min": "210 001 €", "PV nette IR max": "250 000 €", "Taux": "5 %", "Lissage": "—"},
            {"PV nette IR min": "250 001 €", "PV nette IR max": "260 000 €", "Taux": "6 %", "Lissage": "(260000−PV)×1/4"},
            {"PV nette IR min": "260 001 €", "PV nette IR max": "∞", "Taux": "6 %", "Lissage": "—"},
        ]), hide_index=True, use_container_width=True)

        st.markdown('<div class="sec teal sm">ABATTEMENTS DURÉE DE DÉTENTION (IR / PS)</div>', unsafe_allow_html=True)
        abr = []
        for yr in range(1, 31):
            ai_v = abatt_ir_pv(yr); ap_v = abatt_ps_pv(yr)
            abr.append({"An": yr, "Abatt. IR": fp(ai_v), "IR résiduel": fp(1 - ai_v),
                         "Abatt. PS": fp(ap_v), "PS résiduelle": fp(1 - ap_v)})
        st.dataframe(pd.DataFrame(abr), hide_index=True, use_container_width=True, height=400)

    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · Art. 197, 200 B, 1609 nonies G du CGI</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ONGLET 9 — TABLEAU D'AMORTISSEMENT (fidèle Excel)
# ─────────────────────────────────────────────────────────────────
with t9:
    st.markdown('<div class="sec">TABLEAU D\'AMORTISSEMENT FINANCIER</div>', unsafe_allow_html=True)

    ta1, ta2 = st.columns([2.5, 1.5])
    with ta2:
        st.markdown('<div class="sec blue sm">PARAMÈTRES DU FINANCEMENT</div>', unsafe_allow_html=True)
        st.markdown(f"""
| Paramètre | Valeur |
|---|---|
| Montant emprunté | **{fe(res["mempr"])}** |
| Taux nominal annuel | **{fp(ti)}** |
| Durée | **{duree} ans** |
| Taux assurance annuel | **{fp(ta)}** |
""")
        st.markdown('<div class="sec teal sm">RÉSULTATS CLÉS</div>', unsafe_allow_html=True)
        cout_credit = res["mens_tot"] * duree * 12 - res["mempr"]
        cout_int = sum(r["int"] for r in res["amttab"])
        cout_ass = res["mempr"] * ta / 12 * 12 * duree
        st.markdown(f"""
| Résultat | Valeur |
|---|---|
| Mensualité hors assurance | **{fe(res["mens_tot"] - res["mempr"]*ta/12)}** |
| Mensualité assurance | **{fe(res["mempr"]*ta/12)}** |
| **Mensualité totale** | **{fe(res["mens_tot"])}** |
| Coût total du crédit | **{fe(cout_credit)}** |
| Coût total intérêts | **{fe(cout_int)}** |
| Coût total assurance | **{fe(cout_ass)}** |
""")

    with ta1:
        st.markdown('<div class="sec blue sm">TABLEAU D\'AMORTISSEMENT ANNUEL</div>', unsafe_allow_html=True)
        ar = []
        for i, row in enumerate(res["amttab"]):
            ass_an = res["mempr"] * ta / 12 * 12
            ar.append({
                "N°": i + 1,
                "Année": i + 1,
                "Principal (€)": round(row["princ"], 2),
                "Intérêts (€)": round(row["int"], 2),
                "Assurance (€)": round(ass_an, 2),
                "Annuité totale (€)": round(row["princ"] + row["int"] + ass_an, 2),
                "CRD (€)": round(row["crd"], 2),
            })
        df_amt = pd.DataFrame(ar)
        # Totaux
        totals_amt = {
            "N°": "", "Année": "TOTAUX",
            "Principal (€)": round(sum(r["princ"] for r in res["amttab"]), 2),
            "Intérêts (€)": round(cout_int, 2),
            "Assurance (€)": round(cout_ass, 2),
            "Annuité totale (€)": round(sum(r["princ"] + r["int"] for r in res["amttab"]) + cout_ass, 2),
        }
        df_amt_show = pd.concat([df_amt, pd.DataFrame([totals_amt])], ignore_index=True)
        st.dataframe(df_amt_show, hide_index=True, use_container_width=True, height=560)

        # Graphique amortissement
        st.markdown('<div class="sec teal sm no-print">📊 DÉCOMPOSITION ANNUELLE</div>', unsafe_allow_html=True)
        chart_amort_pret(res["amttab"], res["mempr"], ta)

    # Vue mensuelle optionnelle
    with st.expander("📋 Tableau mensuel (3 premières années)"):
        mr = []
        for r_m in res["rows_m"][:36]:
            mr.append({
                "Mois": r_m["mois"],
                "Intérêts": round(r_m["im"], 2),
                "Capital": round(r_m["pm"], 2),
                "Assurance": round(res["mempr"] * ta / 12, 2),
                "Total": round(r_m["im"] + r_m["pm"] + res["mempr"] * ta / 12, 2),
                "CRD": round(r_m["crd"], 2),
            })
        st.dataframe(pd.DataFrame(mr), hide_index=True, use_container_width=True, height=520)

    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · Calcul mensuel exact agrégé annuellement</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ONGLET 10 — IMPRIMER
# ─────────────────────────────────────────────────────────────────
with t10:
    st.markdown('<div class="sec">🖨️ IMPRESSION A4 PORTRAIT</div>', unsafe_allow_html=True)
    st.markdown("""
**Procédure d'impression :**
1. Allez sur l'onglet souhaité
2. Cliquez sur le bouton ci-dessous (ou **Ctrl+P** / **Cmd+P**)
3. Sélectionnez **Format : A4 · Orientation : Portrait**
4. Cochez « Graphiques d'arrière-plan » pour conserver les couleurs
5. Décochez les en-têtes/pieds de page du navigateur
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
    st.caption(f"**Moteur V11 :** Python natif · Fidélité Excel V9 · 49 colonnes · "
               f"Amortissement Jeanbrun sur {duree_amort} ans · "
               "Barème IR 2026 · QF 1 759 €/demi-part · Déficits art. 156-I-3 CGI · TRI · CSG déd. N+1 · "
               "Document non contractuel")
    st.markdown('<div class="footer"><b>médicis Immobilier Neuf</b> · www.medicis-immobilier-neuf.fr · Outil réservé aux conseillers</div>', unsafe_allow_html=True)
