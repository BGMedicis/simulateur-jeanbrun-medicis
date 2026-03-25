"""
SIMULATEUR JEANBRUN — Dispositif art. 31-I-1° CGI (Loi de Finances 2026)
Réplique fidèle du modèle Excel Simulation_JEANBRUN_V10
© Médicis Immobilier Neuf — Simulation personnalisée non contractuelle
"""

import streamlit as st
import numpy as np
import numpy_financial as npf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Simulateur Jeanbrun — Médicis Immobilier Neuf",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Couleurs Médicis
BLEU = "#3761AD"
ORANGE = "#F57E63"
TEAL = "#009FA3"
VERT = "#E2DE3E"

# ─────────────────────────────────────────────
# DONNÉES FISCALES (Barème fiscal)
# ─────────────────────────────────────────────
BAREME_IR = [
    (0, 11600, 0.00, 0),
    (11600, 29579, 0.11, 1276),
    (29579, 84577, 0.30, 6896.01),
    (84577, 181917, 0.41, 16199.48),
    (181917, 1e12, 0.45, 23476.16),
]
PLAFOND_QF = 1759
PLAFOND_DEFICIT_RG = 10700
TAUX_CSG_DED = 0.068

# Plafonds loyers (€/m²/mois)
PLAFONDS_LOYERS = {
    "A Bis": {"Loyer intermédiaire": 19.51, "Loyer social": 15.61, "Loyer très social": 11.71},
    "A":     {"Loyer intermédiaire": 14.49, "Loyer social": 11.59, "Loyer très social": 8.69},
    "B1":    {"Loyer intermédiaire": 11.68, "Loyer social": 9.34,  "Loyer très social": 7.01},
    "B2/C":  {"Loyer intermédiaire": 10.15, "Loyer social": 8.12,  "Loyer très social": 6.09},
}

# Plafonds amortissement annuel par foyer fiscal
PLAFONDS_AMT = {"Loyer intermédiaire": 8000, "Loyer social": 10000, "Loyer très social": 12000}

# Abattements salaires / pensions
PLAFOND_ABATT_10_DECLARANT = 14171
PLANCHER_ABATT_10_DECLARANT = 504
PLAFOND_ABATT_PENSIONS_DECLARANT = 4321
PLANCHER_ABATT_PENSIONS_DECLARANT = 442

# Surtaxe PV
SURTAXE_TRANCHES = [
    (0, 50000, 0, None),
    (50001, 60000, 0.02, lambda pv: pv*0.02 - (60000-pv)/20),
    (60001, 100000, 0.02, None),
    (100001, 110000, 0.03, lambda pv: pv*0.03 - (110000-pv)/10),
    (110001, 150000, 0.03, None),
    (150001, 160000, 0.04, lambda pv: pv*0.04 - (160000-pv)*3/20),
    (160001, 200000, 0.04, None),
    (200001, 210000, 0.05, lambda pv: pv*0.05 - (210000-pv)/5),
    (210001, 250000, 0.05, None),
    (250001, 260000, 0.06, lambda pv: pv*0.06 - (260000-pv)/4),
    (260001, 1e12, 0.06, None),
]

# ─────────────────────────────────────────────
# FONCTIONS DE CALCUL
# ─────────────────────────────────────────────

def calc_ir_bareme(revenu_total, nb_parts):
    """Calcul IR avec barème progressif et plafonnement QF (art. 197 CGI)."""
    if revenu_total <= 0:
        return 0, 0, 0  # IR, TMI, taux_moyen
    quotient = revenu_total / nb_parts
    # IR au quotient
    ir_quotient = 0
    tmi = 0
    for seuil_bas, seuil_haut, taux, reduction in BAREME_IR:
        if quotient > seuil_bas:
            tmi = taux
    for seuil_bas, seuil_haut, taux, reduction in BAREME_IR:
        if revenu_total / 2 <= seuil_haut:
            ir_2parts = max(0, revenu_total * taux - reduction * 2)
            break
    else:
        ir_2parts = max(0, revenu_total * 0.45 - 23476.16 * 2)
    for seuil_bas, seuil_haut, taux, reduction in BAREME_IR:
        if quotient <= seuil_haut:
            ir_quotient = max(0, revenu_total * taux - reduction * nb_parts)
            break
    # Plafonnement QF
    if nb_parts > 2:
        ir_1part = ir_2parts
        avantage_qf = ir_1part - ir_quotient
        plafond = (nb_parts - 2) * PLAFOND_QF
        if avantage_qf > plafond:
            ir_final = ir_1part - plafond
        else:
            ir_final = ir_quotient
    elif nb_parts < 2:
        ir_final = ir_quotient
    else:
        ir_final = ir_2parts
    ir_final = max(0, ir_final)
    taux_moyen = ir_final / revenu_total if revenu_total > 0 else 0
    return ir_final, tmi, taux_moyen


def calc_abattement(type_revenus, revenus_bruts, nb_declarants):
    """Calcul de l'abattement selon type de revenus."""
    if type_revenus == "Salaires (abatt. 10%)":
        return max(PLANCHER_ABATT_10_DECLARANT * nb_declarants,
                   min(revenus_bruts * 0.1, PLAFOND_ABATT_10_DECLARANT * nb_declarants))
    elif type_revenus == "Pensions (abatt. 10%)":
        return max(PLANCHER_ABATT_PENSIONS_DECLARANT * nb_declarants,
                   min(revenus_bruts * 0.1, PLAFOND_ABATT_PENSIONS_DECLARANT * nb_declarants))
    elif type_revenus == "BIC / BNC (micro)":
        return revenus_bruts * 0.34
    else:
        return 0


def calc_surface_ponderee(surface_hab, surface_terrasse, surface_balcon, rdc):
    """Surface pondérée pour plafond loyer Jeanbrun."""
    if rdc:
        annexes = min(surface_balcon, 16) / 2
    else:
        annexes = min(surface_terrasse + min(surface_balcon, 16), 16) / 2
    return surface_hab + annexes


def calc_coeff_multiplicateur(surface_ponderee):
    """Coefficient multiplicateur loyer."""
    return math.trunc(min(0.7 + 19 / surface_ponderee, 1.2) * 100) / 100


def calc_surtaxe_pv(pv_nette_ir):
    """Surtaxe PV immobilière (art. 1609 nonies G CGI)."""
    if pv_nette_ir <= 50000:
        return 0
    for seuil_bas, seuil_haut, taux, lissage in SURTAXE_TRANCHES:
        if seuil_bas <= pv_nette_ir <= seuil_haut:
            if lissage is not None:
                return lissage(pv_nette_ir)
            return pv_nette_ir * taux
    return pv_nette_ir * 0.06


def calc_abattement_pv_ir(annee):
    """Abattement PV pour durée de détention - IR (6%/an de 6 à 21 ans, exonéré après 22)."""
    if annee <= 5: return 0
    if annee <= 21: return (annee - 5) * 0.06
    return 1.0


def calc_abattement_pv_ps(annee):
    """Abattement PV pour durée de détention - PS."""
    if annee <= 5: return 0
    if annee <= 21: return (annee - 5) * 0.0165
    if annee == 22: return (21 - 5) * 0.0165 + 0.016
    if annee <= 30: return (21 - 5) * 0.0165 + 0.016 + (annee - 22) * 0.09
    return 1.0


def calc_loan_schedule(montant, taux_annuel, duree_ans, taux_assurance):
    """Tableau d'amortissement annuel."""
    if montant <= 0 or taux_annuel <= 0 or duree_ans <= 0:
        return pd.DataFrame()
    mensualite_ht = -npf.pmt(taux_annuel / 12, duree_ans * 12, montant)
    assurance_annuelle = montant * taux_assurance
    rows = []
    for y in range(1, duree_ans + 1):
        principal = -npf.ppmt(taux_annuel / 12, np.arange((y-1)*12+1, y*12+1), duree_ans*12, montant).sum()
        interets = -npf.ipmt(taux_annuel / 12, np.arange((y-1)*12+1, y*12+1), duree_ans*12, montant).sum()
        crd = montant + npf.ppmt(taux_annuel / 12, np.arange(1, y*12+1), duree_ans*12, montant).sum()
        annuite_totale = principal + interets + assurance_annuelle
        rows.append({
            "annee": y, "principal": principal, "interets": interets,
            "assurance": assurance_annuelle, "annuite": annuite_totale, "crd": max(0, crd)
        })
    return pd.DataFrame(rows)


def run_simulation(params):
    """Moteur de simulation complet — réplique fidèle du Moteur V10."""
    N = 25  # années
    p = params

    # Hypothèses dérivées
    cout_total = p["prix"] * (1 + p["frais_acq"])
    montant_emprunte = cout_total - p["apport"]
    base_amt = p["prix"] * 0.8
    taux_amt = {"Loyer intermédiaire": 0.035, "Loyer social": 0.045, "Loyer très social": 0.055}[p["type_loyer"]]
    plafond_amt = PLAFONDS_AMT[p["type_loyer"]]
    amt_annuel = min(plafond_amt, base_amt * taux_amt)

    # Surface pondérée et loyer max
    surf_pond = calc_surface_ponderee(p["surface"], p["terrasse"], p["balcon"], p["rdc"])
    coeff = calc_coeff_multiplicateur(surf_pond)
    plafond_loyer_m2 = PLAFONDS_LOYERS[p["zone"]][p["type_loyer"]]
    loyer_max = plafond_loyer_m2 * surf_pond * coeff
    loyer_mensuel = min(p["loyer_souhaite"], loyer_max)
    loyer_annuel_base = loyer_mensuel * 12

    # Abattement revenus
    abattement = calc_abattement(p["type_revenus"], p["revenus"], p["nb_declarants"])
    revenus_nets = p["revenus"] - abattement

    # Tableau d'amortissement prêt
    loan = calc_loan_schedule(montant_emprunte, p["taux_interet"], p["duree_pret"], p["taux_assurance"])
    mensualite_ht = -npf.pmt(p["taux_interet"] / 12, p["duree_pret"] * 12, montant_emprunte) if montant_emprunte > 0 else 0
    assurance_mensuelle = montant_emprunte * p["taux_assurance"] / 12

    # Résultats année par année
    results = []
    amt_cumule = 0
    stock_deficit = 0
    stock_deficit_sans_jb = 0
    prev_csg_ded_avant = 0
    prev_csg_ded_apres = 0
    prev_csg_ded_sans_jb = 0
    # Pour péremption 10 ans, on stocke les déficits générés par année
    deficits_generes = [0] * N
    deficits_generes_sans_jb = [0] * N

    for y in range(1, N + 1):
        idx = y - 1  # 0-based
        nb_parts = p["parts_par_annee"][idx] if idx < len(p["parts_par_annee"]) else p["nb_parts"]

        # Loyers indexés
        loyer_annuel = loyer_annuel_base * (1 + p["indexation_loyers"]) ** (y - 1)
        charges = loyer_annuel * p["charges_pct"]

        # Prêt
        if y <= p["duree_pret"] and not loan.empty:
            lr = loan.iloc[idx]
            interets = lr["interets"]
            assurance = lr["assurance"]
            annuite = lr["annuite"]
            crd = lr["crd"]
        else:
            interets = 0
            assurance = 0
            annuite = 0
            crd = 0

        # Amortissement Jeanbrun
        amt_restant = max(0, base_amt - amt_cumule)
        amt_year = min(amt_annuel, amt_restant)
        amt_cumule += amt_year

        # Valeur bien et RF autres (indexés)
        valeur_bien = p["prix"] * (1 + p["indexation_bien"]) ** (y - 1)
        rf_autres = p["rf_autres"] * (1 + p["indexation_bien"]) ** (y - 1)

        # ═══ IMPÔT AVANT OPÉRATION ═══
        rev_total_avant = revenus_nets + rf_autres - prev_csg_ded_avant
        if y == 1:
            rev_total_avant = revenus_nets + rf_autres  # pas de CSG déd en année 1
        ir_avant, tmi_avant, taux_moy_avant = calc_ir_bareme(rev_total_avant, nb_parts)
        ps_avant = max(0, rf_autres) * p["taux_ps"]
        total_avant = ir_avant + ps_avant

        # ═══ REVENUS FONCIERS AVEC JEANBRUN ═══
        rf_bruts_globaux = loyer_annuel + rf_autres
        charges_financieres = interets + assurance + (p["frais_garantie"] if y == 1 else 0)
        charges_non_fin = charges + amt_year
        rf_net = rf_bruts_globaux - charges_financieres - charges_non_fin

        # Déficit foncier (art. 156-I-3° CGI)
        if rf_net >= 0:
            deduction_rg = 0
            deficit_genere = 0
        elif rf_bruts_globaux >= charges_financieres:
            # Déficit vient des charges non-financières
            deduction_rg = max(rf_net, -PLAFOND_DEFICIT_RG)
            deficit_genere = max(0, -rf_net - PLAFOND_DEFICIT_RG)
        else:
            # RF < charges financières → charges non-fin déductibles du RG
            deduction_rg = max(-charges_non_fin, -PLAFOND_DEFICIT_RG)
            deficit_genere = (charges_financieres - rf_bruts_globaux) + max(0, charges_non_fin - PLAFOND_DEFICIT_RG)

        deficits_generes[idx] = deficit_genere

        # Péremption 10 ans
        perime = deficits_generes[idx - 10] if idx >= 10 else 0

        # Stock reportable
        if y == 1:
            stock_deficit = deficit_genere
        else:
            stock_deficit = stock_deficit + deficit_genere - prev_impute - perime

        # Imputation déficit reportable
        impute = min(stock_deficit, rf_net) if rf_net > 0 else 0

        # RF net taxable
        rf_net_taxable = max(0, rf_net - impute)

        # CSG déductible
        csg_ded_avant = max(0, rf_autres) * TAUX_CSG_DED
        csg_ded_apres = rf_net_taxable * TAUX_CSG_DED

        # ═══ IMPÔT APRÈS OPÉRATION ═══
        rev_total_apres = revenus_nets + rf_net_taxable + deduction_rg
        if y > 1:
            rev_total_apres -= prev_csg_ded_apres
        ir_apres, tmi_apres, taux_moy_apres = calc_ir_bareme(rev_total_apres, nb_parts)
        ps_apres = rf_net_taxable * p["taux_ps"]
        total_apres = ir_apres + ps_apres

        # Économie fiscale
        economie = total_avant - total_apres

        # ═══ SCÉNARIO SANS JEANBRUN (pour isoler l'éco JB) ═══
        rf_net_sans_jb = rf_net + amt_year  # on rajoute l'amort
        if rf_net_sans_jb >= 0:
            ded_rg_sans_jb = 0
            def_gen_sans_jb = 0
        elif rf_bruts_globaux >= charges_financieres:
            ded_rg_sans_jb = max(rf_net_sans_jb, -PLAFOND_DEFICIT_RG)
            def_gen_sans_jb = max(0, -rf_net_sans_jb - PLAFOND_DEFICIT_RG)
        else:
            ded_rg_sans_jb = max(-charges, -PLAFOND_DEFICIT_RG)
            def_gen_sans_jb = (charges_financieres - rf_bruts_globaux) + max(0, charges - PLAFOND_DEFICIT_RG)

        deficits_generes_sans_jb[idx] = def_gen_sans_jb
        perime_sans_jb = deficits_generes_sans_jb[idx - 10] if idx >= 10 else 0
        if y == 1:
            stock_deficit_sans_jb = def_gen_sans_jb
        else:
            stock_deficit_sans_jb = stock_deficit_sans_jb + def_gen_sans_jb - prev_impute_sans_jb - perime_sans_jb

        impute_sans_jb = min(stock_deficit_sans_jb, rf_net_sans_jb) if rf_net_sans_jb > 0 else 0
        rf_taxable_sans_jb = max(0, rf_net_sans_jb - impute_sans_jb)
        csg_ded_sans_jb = rf_taxable_sans_jb * TAUX_CSG_DED

        rev_total_sans_jb = revenus_nets + rf_taxable_sans_jb + ded_rg_sans_jb
        if y > 1:
            rev_total_sans_jb -= prev_csg_ded_sans_jb
        ir_sans_jb, _, _ = calc_ir_bareme(rev_total_sans_jb, nb_parts)
        ps_sans_jb = rf_taxable_sans_jb * p["taux_ps"]
        total_sans_jb = ir_sans_jb + ps_sans_jb
        eco_jb = total_sans_jb - total_apres  # économie spécifiquement JB

        # ═══ PLUS-VALUE ═══
        prix_revient_0 = (p["prix"] + max(p["prix"] * p["frais_acq"], p["prix"] * p["forfait_frais_pv"])
                          + (p["prix"] * p["forfait_travaux"] if y > 5 else 0) - amt_cumule)
        pv_brute_0 = p["prix"] - prix_revient_0  # scénario 0%

        prix_vente_15 = p["prix"] * 1.015 ** y
        pv_brute_15 = prix_vente_15 - prix_revient_0  # scénario 1.5%

        abatt_ir = calc_abattement_pv_ir(y)
        abatt_ps = calc_abattement_pv_ps(y)

        pv_imp_ir_0 = max(0, pv_brute_0 * (1 - abatt_ir))
        pv_imp_ps_0 = max(0, pv_brute_0 * (1 - abatt_ps))
        impot_pv_0 = 0
        if pv_brute_0 > 0:
            impot_pv_0 = (pv_imp_ir_0 * p["taux_ir_pv"] + pv_imp_ps_0 * p["taux_ps"]
                          + calc_surtaxe_pv(pv_imp_ir_0))

        pv_imp_ir_15 = max(0, pv_brute_15 * (1 - abatt_ir))
        pv_imp_ps_15 = max(0, pv_brute_15 * (1 - abatt_ps))
        impot_pv_15 = 0
        if pv_brute_15 > 0:
            impot_pv_15 = (pv_imp_ir_15 * p["taux_ir_pv"] + pv_imp_ps_15 * p["taux_ps"]
                           + calc_surtaxe_pv(pv_imp_ir_15))

        # Capital net constitué
        capital_net_0 = p["prix"] - crd - impot_pv_0
        capital_net_15 = prix_vente_15 - crd - impot_pv_15

        # Effort d'épargne mensuel
        effort = (loyer_annuel - annuite - charges + economie) / 12

        results.append({
            "annee": y,
            "loyers": loyer_annuel,
            "charges": charges,
            "interets": interets,
            "assurance": assurance,
            "amt_jb": amt_year,
            "annuite": annuite,
            "crd": crd,
            "valeur_bien": valeur_bien,
            "rf_net": rf_net,
            "rf_net_taxable": rf_net_taxable,
            "deduction_rg": deduction_rg,
            "deficit_genere": deficit_genere,
            "stock_deficit": stock_deficit,
            "impute": impute,
            "total_avant": total_avant,
            "total_apres": total_apres,
            "economie": economie,
            "eco_jb": eco_jb,
            "tmi_avant": tmi_avant,
            "tmi_apres": tmi_apres,
            "effort_mensuel": effort,
            "capital_net_0": capital_net_0,
            "capital_net_15": capital_net_15,
            "amt_cumule": amt_cumule,
            "abatt_ir_pv": abatt_ir,
            "abatt_ps_pv": abatt_ps,
            "pv_brute_0": pv_brute_0,
            "pv_brute_15": pv_brute_15,
            "impot_pv_0": impot_pv_0,
            "impot_pv_15": impot_pv_15,
            "nb_parts": nb_parts,
        })

        # Mémoire pour N+1
        prev_impute = impute
        prev_impute_sans_jb = impute_sans_jb
        prev_csg_ded_avant = csg_ded_avant
        prev_csg_ded_apres = csg_ded_apres
        prev_csg_ded_sans_jb = csg_ded_sans_jb

    df = pd.DataFrame(results)

    # Infos complémentaires
    info = {
        "cout_total": cout_total,
        "montant_emprunte": montant_emprunte,
        "base_amt": base_amt,
        "taux_amt": taux_amt,
        "plafond_amt": plafond_amt,
        "amt_annuel": amt_annuel,
        "surf_pond": surf_pond,
        "coeff": coeff,
        "loyer_max": loyer_max,
        "loyer_mensuel": loyer_mensuel,
        "mensualite_totale": mensualite_ht + assurance_mensuelle,
        "loan": loan,
        "revenus_nets": revenus_nets,
        "abattement": abattement,
    }
    return df, info


# ─────────────────────────────────────────────
# INTERFACE STREAMLIT
# ─────────────────────────────────────────────

st.markdown(
    f"""<div style='text-align:center;padding:1rem;background:linear-gradient(135deg,{BLEU},{TEAL});border-radius:10px;margin-bottom:1.5rem'>
    <h1 style='color:white;margin:0;font-family:Poppins,sans-serif'>🏠 Simulateur Jeanbrun</h1>
    <p style='color:rgba(255,255,255,.85);margin:.3rem 0 0'>Dispositif art. 31-I-1° CGI — Loi de Finances 2026 · médicis IMMOBILIER NEUF</p>
    </div>""",
    unsafe_allow_html=True,
)

# ── SIDEBAR : Saisie des hypothèses ──

with st.sidebar:
    st.markdown(f"### ✏️ Hypothèses d'investissement")

    st.markdown("#### 🏠 Bien immobilier")
    prix = st.number_input("Prix d'acquisition (€)", 50000, 2000000, 205000, 5000)
    frais_acq = st.number_input("Frais d'acquisition (%)", 0.0, 15.0, 2.0, 0.5) / 100
    surface = st.number_input("Surface habitable (m²)", 10.0, 300.0, 40.0, 1.0)
    zone = st.selectbox("Zone", ["A Bis", "A", "B1", "B2/C"], index=1)

    with st.expander("📐 Surface pondérée (annexes)"):
        rdc = st.checkbox("RDC (exclut terrasse)")
        terrasse = st.number_input("Surface terrasse (m²)", 0.0, 50.0, 0.0, 0.5)
        balcon = st.number_input("Surface balcon (m²)", 0.0, 50.0, 4.0, 0.5)

    indexation_bien = st.number_input("Indexation annuelle revenus/bien (%)", 0.0, 5.0, 0.0, 0.5) / 100

    st.markdown("#### 💳 Financement")
    apport = st.number_input("Apport personnel (€)", 0, 2000000, 80000, 5000)
    taux_interet = st.number_input("Taux d'intérêt annuel (%)", 0.5, 10.0, 3.5, 0.1) / 100
    taux_assurance = st.number_input("Taux assurance emprunteur (%)", 0.0, 2.0, 0.36, 0.01) / 100
    duree_pret = st.slider("Durée du prêt (ans)", 5, 25, 20)
    frais_garantie = st.number_input("Frais garantie/dossier/courtage (€)", 0, 50000, 5000, 500)

    st.markdown("#### 🏘 Revenus locatifs")
    type_loyer = st.selectbox("Type de loyer", ["Loyer intermédiaire", "Loyer social", "Loyer très social"])
    loyer_souhaite = st.number_input("Loyer mensuel souhaité (€)", 100, 5000, 699, 10)
    indexation_loyers = st.number_input("Indexation loyers (%/an)", 0.0, 5.0, 1.5, 0.5) / 100
    charges_pct = st.number_input("Charges exploitation (% loyers)", 0.0, 50.0, 30.0, 5.0) / 100

    st.markdown("#### 👤 Situation fiscale")
    type_revenus = st.selectbox("Type de revenus", ["Salaires (abatt. 10%)", "Pensions (abatt. 10%)", "BIC / BNC (micro)", "Revenus nets (sans abatt.)"])
    revenus = st.number_input("Revenus annuels déclarés (€)", 0, 1000000, 107000, 1000)
    rf_autres = st.number_input("Revenus fonciers — autres biens (€/an)", 0, 200000, 0, 500)
    nb_parts = st.number_input("Parts fiscales", 1.0, 10.0, 4.0, 0.5)
    nb_declarants = st.number_input("Nombre de déclarants", 1, 3, 3)
    taux_ps = st.number_input("Taux prélèvements sociaux (%)", 0.0, 25.0, 17.2, 0.1) / 100

    with st.expander("📅 Parts fiscales par année (optionnel)"):
        st.caption("Modifier pour anticiper arrivée/départ d'un enfant")
        parts_par_annee = []
        for i in range(25):
            v = st.number_input(f"Année {i+1}", 1.0, 10.0, nb_parts, 0.5, key=f"part_{i}")
            parts_par_annee.append(v)

    st.markdown("#### 💹 Plus-value à la revente")
    forfait_frais_pv = st.number_input("Forfait frais d'acquisition PV (%)", 0.0, 15.0, 7.5, 0.5) / 100
    forfait_travaux = st.number_input("Forfait travaux (>5 ans, %)", 0.0, 20.0, 15.0, 1.0) / 100
    taux_ir_pv = st.number_input("Taux IR plus-value (%)", 0.0, 30.0, 19.0, 0.5) / 100

# ── CALCUL ──

params = {
    "prix": prix, "frais_acq": frais_acq, "surface": surface, "zone": zone,
    "rdc": rdc, "terrasse": terrasse, "balcon": balcon,
    "indexation_bien": indexation_bien,
    "apport": apport, "taux_interet": taux_interet, "taux_assurance": taux_assurance,
    "duree_pret": duree_pret, "frais_garantie": frais_garantie,
    "type_loyer": type_loyer, "loyer_souhaite": loyer_souhaite,
    "indexation_loyers": indexation_loyers, "charges_pct": charges_pct,
    "type_revenus": type_revenus, "revenus": revenus, "rf_autres": rf_autres,
    "nb_parts": nb_parts, "nb_declarants": nb_declarants, "taux_ps": taux_ps,
    "parts_par_annee": parts_par_annee,
    "forfait_frais_pv": forfait_frais_pv, "forfait_travaux": forfait_travaux,
    "taux_ir_pv": taux_ir_pv,
}

df, info = run_simulation(params)

# ── AFFICHAGE : KPI PRINCIPAUX ──

st.markdown("### 📊 Synthèse de l'opération")

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Revenus déclarés", f"{revenus:,.0f} €")
c2.metric("TMI", f"{df.iloc[0]['tmi_avant']:.0%}")
c3.metric("Prix d'acquisition", f"{prix:,.0f} €")
c4.metric("Loyer mensuel", f"{info['loyer_mensuel']:,.0f} €")
c5.metric("Surface / Zone", f"{info['surf_pond']:.1f} m² · {zone}")
c6.metric("Économie fiscale an 1", f"{df.iloc[0]['economie']:,.0f} €")

# ── COMPTE EN T (3 horizons) ──

st.markdown("---")
st.markdown("### 📋 Compte en T — Moyennes mensuelles")

def render_compte_t(horizon, label, emoji):
    data = df.iloc[:horizon]
    loyer_moy = data["loyers"].mean() / 12
    gain_fiscal_mois = data["economie"].sum() / (horizon * 12)
    charges_mois = data["charges"].mean() / 12
    credit_mois = info["mensualite_totale"] if horizon <= duree_pret else info["mensualite_totale"] * min(duree_pret, horizon) / horizon
    total_entrees = loyer_moy + gain_fiscal_mois
    total_sorties = credit_mois + charges_mois
    effort = total_entrees - total_sorties
    capital_net = data.iloc[-1]["capital_net_0"]
    eco_jb_total = data["eco_jb"].sum()

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown(f"**✚ CE QUI RENTRE (+)**")
        st.markdown(f"Loyer moyen : **{loyer_moy:,.0f} €/mois**")
        st.markdown(f"Gain fiscal : **{gain_fiscal_mois:,.0f} €/mois**")
        st.markdown(f"**TOTAL : {total_entrees:,.0f} €/mois**")
    with col_r:
        st.markdown(f"**− CE QUI SORT (−)**")
        st.markdown(f"Crédit : **{credit_mois:,.0f} €/mois**")
        st.markdown(f"Charges : **{charges_mois:,.0f} €/mois**")
        st.markdown(f"**TOTAL : {total_sorties:,.0f} €/mois**")

    color = "green" if effort >= 0 else "red"
    st.markdown(f"**Effort d'épargne mensuel moyen : "
                f"<span style='color:{color};font-size:1.3em'>{effort:,.0f} €/mois</span>**",
                unsafe_allow_html=True)
    st.caption(f"Capital net constitué (prix constant) : **{capital_net:,.0f} €** · "
               f"Gain fiscal total : {data['economie'].sum():,.0f} € (dont JB : {eco_jb_total:,.0f} €)")

tab1, tab2, tab3 = st.tabs(["🔹 9 ans — Fin engagement", "🔸 15 ans — Horizon référence", "⭐ 25 ans — Pleine propriété"])
with tab1:
    render_compte_t(9, "9 ans", "🔹")
with tab2:
    render_compte_t(15, "15 ans", "🔸")
with tab3:
    render_compte_t(25, "25 ans", "⭐")

# ── GRAPHIQUE CAPITAL NET ──

st.markdown("---")
st.markdown("### 📈 Capital net constitué par année de détention")

fig = go.Figure()
fig.add_trace(go.Scatter(x=df["annee"], y=df["capital_net_0"],
                         name="Prix constant (0%)", line=dict(color=BLEU, width=2)))
fig.add_trace(go.Scatter(x=df["annee"], y=df["capital_net_15"],
                         name="Revalorisation 1,5%/an", line=dict(color=TEAL, width=2)))
fig.add_trace(go.Scatter(x=df["annee"], y=df["crd"],
                         name="Capital restant dû", line=dict(color=ORANGE, width=2, dash="dot")))
fig.update_layout(
    yaxis_title="€", xaxis_title="Année de détention",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    height=400, margin=dict(l=50, r=20, t=30, b=50),
    hovermode="x unified",
)
for h in [9, 15, 20]:
    fig.add_vline(x=h, line_dash="dash", line_color="gray", opacity=0.5, annotation_text=f"{h} ans")
st.plotly_chart(fig, use_container_width=True)

# ── PROJECTION DÉTAILLÉE ──

st.markdown("---")
st.markdown("### 📋 Projection annuelle détaillée")

display_df = df[["annee", "loyers", "annuite", "charges", "amt_jb", "rf_net",
                  "total_avant", "total_apres", "economie", "effort_mensuel",
                  "capital_net_0", "capital_net_15", "nb_parts"]].copy()
display_df.columns = ["Année", "Loyers", "Remb. prêt", "Charges", "Amort. JB",
                       "RF net imputé", "Impôt avant", "Impôt après", "Économie fiscale",
                       "Effort mensuel", "Capital net (0%)", "Capital net (1,5%)", "Parts"]

st.dataframe(
    display_df.style.format({
        "Loyers": "{:,.0f}", "Remb. prêt": "{:,.0f}", "Charges": "{:,.0f}",
        "Amort. JB": "{:,.0f}", "RF net imputé": "{:,.0f}",
        "Impôt avant": "{:,.0f}", "Impôt après": "{:,.0f}", "Économie fiscale": "{:,.0f}",
        "Effort mensuel": "{:,.0f}", "Capital net (0%)": "{:,.0f}",
        "Capital net (1,5%)": "{:,.0f}", "Parts": "{:.1f}",
    }).background_gradient(subset=["Économie fiscale"], cmap="Greens"),
    use_container_width=True, height=600,
)

# ── GRAPHIQUE DÉCOMPOSITION FISCALE ──

st.markdown("---")
st.markdown("### 🔍 Économie fiscale : décomposition par année")

fig2 = go.Figure()
eco_naturelle = df["economie"] - df["eco_jb"]
fig2.add_trace(go.Bar(x=df["annee"], y=eco_naturelle, name="Déficit naturel (intérêts)",
                       marker_color=BLEU))
fig2.add_trace(go.Bar(x=df["annee"], y=df["eco_jb"], name="Amortissement Jeanbrun",
                       marker_color=TEAL))
fig2.update_layout(
    barmode="stack", yaxis_title="€", xaxis_title="Année",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    height=350, margin=dict(l=50, r=20, t=30, b=50),
)
st.plotly_chart(fig2, use_container_width=True)

# ── REVENTE ──

st.markdown("---")
st.markdown("### 💰 Simulation de revente")

revente_tab1, revente_tab2, revente_tab3 = st.tabs(["🔹 Revente à 9 ans", "🔸 Revente à 15 ans", "⭐ Revente à 25 ans"])

def render_revente(horizon):
    r = df.iloc[horizon - 1]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Prix de vente**")
        st.metric("Scénario 0%", f"{prix:,.0f} €")
        st.metric("Scénario 1,5%/an", f"{prix * 1.015**horizon:,.0f} €")
    with col2:
        st.markdown("**Impôt plus-value**")
        st.metric("Abattement IR", f"{r['abatt_ir_pv']:.0%}")
        st.metric("Impôt PV (0%)", f"{r['impot_pv_0']:,.0f} €")
        st.metric("Impôt PV (1,5%)", f"{r['impot_pv_15']:,.0f} €")
    with col3:
        st.markdown("**Capital net**")
        st.metric("CRD", f"{r['crd']:,.0f} €")
        st.metric("Net (0%)", f"{r['capital_net_0']:,.0f} €", delta=f"{r['capital_net_0'] - apport:,.0f} € vs apport")
        st.metric("Net (1,5%)", f"{r['capital_net_15']:,.0f} €", delta=f"{r['capital_net_15'] - apport:,.0f} € vs apport")
    st.caption(f"Amortissements réintégrés dans la PV : {r['amt_cumule']:,.0f} €")

with revente_tab1: render_revente(9)
with revente_tab2: render_revente(15)
with revente_tab3: render_revente(25)

# ── BILAN GLOBAL ──

st.markdown("---")
st.markdown("### 📊 Bilan global de l'opération (25 ans)")

b1, b2, b3, b4 = st.columns(4)
b1.metric("Total loyers perçus", f"{df['loyers'].sum():,.0f} €")
b2.metric("Total charges", f"{df['charges'].sum():,.0f} €")
b3.metric("Économie fiscale totale", f"{df['economie'].sum():,.0f} €")
b4.metric("Capital net final (0%)", f"{df.iloc[-1]['capital_net_0']:,.0f} €")

# ── TABLEAU D'AMORTISSEMENT FINANCIER ──

with st.expander("🏦 Tableau d'amortissement du prêt"):
    if not info["loan"].empty:
        loan_display = info["loan"].copy()
        loan_display.columns = ["Année", "Principal", "Intérêts", "Assurance", "Annuité totale", "CRD"]
        st.dataframe(
            loan_display.style.format({
                "Principal": "{:,.0f}", "Intérêts": "{:,.0f}", "Assurance": "{:,.0f}",
                "Annuité totale": "{:,.0f}", "CRD": "{:,.0f}",
            }),
            use_container_width=True,
        )
        st.caption(f"Mensualité hors assurance : {-npf.pmt(taux_interet/12, duree_pret*12, info['montant_emprunte']):,.0f} € · "
                   f"Mensualité totale : {info['mensualite_totale']:,.0f} €")

# ── DISCLAIMER ──

st.markdown("---")
st.markdown(
    f"""<div style='text-align:center;padding:.8rem;background:#f8f9fa;border-radius:8px;font-size:.8em;color:#666'>
    <strong>médicis IMMOBILIER NEUF</strong> — www.medicis-immobilier-neuf.fr<br>
    Simulation personnalisée non contractuelle · Hypothèses d'indexation et fiscalité constantes<br>
    Barème IR 2026 (revenus 2025) · Dispositif Jeanbrun art. 31-I-1° i/j CGI (Loi de Finances 2026)
    </div>""",
    unsafe_allow_html=True,
)
