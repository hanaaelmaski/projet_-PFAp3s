"""
Service Qualite Intelligent — Systeme d'aide a la decision (P3S)
SEWS CABIND MAROC — Application interne

Lancer :  streamlit run app.py
"""
import os
import datetime
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils.theme import (injecter_css, carte_kpi, bandeau_kpi, navbar,
                         kpi_metrique, bloc,
                         zone_bleue, jauge_anneau, style_fig,
                         BLEU, BLEU_FONCE, BLEU_NUIT, BLEU_CLAIR, BLANC, ENCRE,
                         GRIS, GRIS_CLAIR, VERT, ORANGE, ROUGE, PALETTE)
from utils.data import (charger_donnees, charger_kpi, entrainer_modele,
                        lire_fichier_importe, lister_feuilles,
                        fusionner_feuilles, actions_pour,
                        defaut_le_plus_probable, sauvegarder_donnees,
                        lire_historique, donnees_importees_actives,
                        restaurer_reference, lire_index_archives,
                        charger_archive, archiver_reference, ASSETS)

st.set_page_config(page_title="Service Qualite Intelligent — P3S",
                   layout="wide", initial_sidebar_state="expanded")
injecter_css()

IDENTIFIANTS = {"admin": "p3s2024"}     # DEMO uniquement


# ===========================================================================
# 1. PAGE DE CONNEXION
# ===========================================================================
def page_login() -> bool:
    """
    Ecran de connexion : panneau sombre (identite) + panneau clair (formulaire).
    Les deux colonnes ont la meme hauteur (Flexbox via CSS) et le contenu est
    centre verticalement. Aucun style n'est applique aux champs eux-memes afin
    de preserver le fonctionnement natif (notamment le bouton oeil du mot de passe).
    """
    if st.session_state.get("connecte"):
        return True

    gauche, droite = st.columns([1.05, 1], gap="small")

    # ---------- Panneau sombre : identite ----------
    with gauche:
        st.markdown("<span class='mk-login'></span>", unsafe_allow_html=True)

        logo = os.path.join(ASSETS, "logo_nav.png")
        if not os.path.exists(logo):
            logo = os.path.join(ASSETS, "logo.png")
        if os.path.exists(logo):
            l1, l2, l3 = st.columns([1, 3, 1])
            with l2:
                st.image(logo, use_container_width=True)

        st.markdown("""
            <div class='lg-titre'>Systeme intelligent<br>d'aide a la decision</div>
            <div class='lg-trait'></div>
            <div class='lg-sous'>Analyse predictive des non-conformites
            des cables Renault (P3S)</div>
            <div class='lg-arg'>
              <div class='ic'><i class='bi bi-graph-up-arrow'></i></div>
              <div><div class='t'>Analyse predictive</div>
                   <div class='d'>Anticipez les non-conformites</div></div>
            </div>
            <div class='lg-arg'>
              <div class='ic'><i class='bi bi-shield-check'></i></div>
              <div><div class='t'>Aide a la decision</div>
                   <div class='d'>Prenez des decisions eclairees</div></div>
            </div>
            <div class='lg-arg'>
              <div class='ic'><i class='bi bi-bell'></i></div>
              <div><div class='t'>Alertes intelligentes</div>
                   <div class='d'>Soyez informe en continu</div></div>
            </div>
        """, unsafe_allow_html=True)

    # ---------- Panneau clair : formulaire ----------
    with droite:
        # centrage horizontal du formulaire
        m1, centre, m2 = st.columns([0.12, 1, 0.12])
        with centre:
            st.markdown(
                "<div class='lg-avatar'><i class='bi bi-person-badge'></i></div>"
                "<div class='lg-bv'>Bienvenue</div>"
                "<div class='lg-bv-s'>Connectez-vous a votre espace</div>",
                unsafe_allow_html=True)

            with st.form("login"):
                u = st.text_input("Nom d'utilisateur",
                                  placeholder="Entrez votre nom d'utilisateur")
                p = st.text_input("Mot de passe", type="password",
                                  placeholder="Entrez votre mot de passe")
                ok = st.form_submit_button("Connexion", use_container_width=True)

            if ok:
                if IDENTIFIANTS.get(u) == p:
                    st.session_state["connecte"] = True
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")

            st.markdown("<div class='lg-pied'>Acces securise — "
                        "vos donnees sont protegees</div>", unsafe_allow_html=True)

    return False


if not page_login():
    st.stop()


# ===========================================================================
# 2. DONNEES (avec gestion de version pour le bouton Actualiser)
# ===========================================================================
if "version" not in st.session_state:
    st.session_state["version"] = 0
version = st.session_state["version"]

# Les donnees importees sont lues depuis le disque -> elles persistent
df = charger_donnees(version)
kpi_mois = charger_kpi(version)

res = entrainer_modele(df, version)
metriques = res["metriques"]
dpred = res["df"]


# ===========================================================================
# 3. SIDEBAR (profil + navigation + donnees)
# ===========================================================================
# Import de fichier : gere dans l'onglet Parametres
fichier = st.session_state.get("_fichier")

navbar()

onglets = st.tabs(["Dashboard", "Analyse", "Prediction IA", "Aide a la decision",
                   "Alertes", "Suivi des performances", "Donnees", "Rapports",
                   "Parametres"])

# Indicateurs communs
total = int(df["Nombre_Defauts"].sum())
mach_crit = df.groupby("Machine")["Nombre_Defauts"].sum().idxmax()
sect_crit = df.groupby("Section")["Nombre_Defauts"].sum().idxmax()
defaut_freq = df.groupby("Type_Defaut")["Nombre_Defauts"].sum().idxmax()
nb_risque = int((dpred["risque_predit"] == 1).sum())
proba_moy = round(dpred.loc[dpred["risque_predit"] == 1, "probabilite"].mean() * 100, 1) \
    if nb_risque else 0.0


# ===========================================================================
# 5. PAGE DASHBOARD
# ===========================================================================
with onglets[0]:
    # Defaut le plus probable sur la combinaison la plus critique
    defaut_pred, part = defaut_le_plus_probable(df, mach_crit, sect_crit)
    if defaut_pred is None:
        defaut_pred, part = defaut_freq, 0.0
    part_pct = round(part * 100, 1)

    if nb_risque == 0:
        alerte, coul_alerte, etat = "Faible", VERT, "Bon"
    elif nb_risque <= 50:
        alerte, coul_alerte, etat = "Moyen", ORANGE, "Moyen"
    else:
        alerte, coul_alerte, etat = "Eleve", ROUGE, "Critique"

    # --- Zone bleue : titre + bandeau KPI (prolonge la navbar) ---
    zone_bleue("Smart Quality Dashboard", [
        {"libelle": "Total des non-conformites", "valeur": f"{total:,}".replace(",", " "),
         "icone": "box-seam"},
        {"libelle": "Machine la plus critique", "valeur": mach_crit,
         "icone": "hdd-stack", "texte": True},
        {"libelle": "Section la plus critique", "valeur": sect_crit,
         "icone": "geo-alt", "texte": True},
        {"libelle": "Combinaisons a risque (IA)", "valeur": nb_risque,
         "icone": "exclamation-triangle"},
    ])

    # --- Ligne 1 : repartition + prediction IA ---
    g1, g2 = st.columns([1.25, 1])
    with g1:
        st.markdown("#### Repartition des non-conformites")
        cc1, cc2 = st.columns([1, 1.15])
        with cc1:
            top3 = (df.groupby("Type_Defaut")["Nombre_Defauts"].sum()
                    .sort_values(ascending=False).head(3))
            part3 = round(top3.sum() / total * 100)
            st.markdown(
                f"<div class='encadre'>"
                f"<div class='p'>Total des defauts</div>"
                f"<div class='gros'>{total:,}</div>".replace(",", " ") +
                f"<div class='p' style='margin-bottom:12px;'>"
                f"{len(df)} combinaisons analysees</div>"
                f"<div class='p'><b>Top 3 defauts</b> : {part3} % du total</div>"
                f"</div>", unsafe_allow_html=True)
        with cc2:
            d = df.groupby("Machine")["Nombre_Defauts"].sum().sort_values(ascending=False)
            fig = px.pie(names=d.index, values=d.values, hole=0.62,
                         color_discrete_sequence=PALETTE)
            fig.update_traces(textinfo="percent")
            st.plotly_chart(style_fig(fig, 240), use_container_width=True)

    with g2:
        st.markdown("#### Prediction IA")
        st.markdown(
            f"<div class='encadre'>"
            f"<div class='p'>Defaut predit</div>"
            f"<div class='gros' style='font-size:22px;'>{defaut_pred}</div>"
            f"<div class='p' style='margin-bottom:10px;'>Sur {mach_crit} / {sect_crit}</div>"
            f"<div class='p'>Probabilite du defaut predit</div>"
            f"<div class='gros'>{part_pct} %</div>"
            f"<div style='margin-top:10px;'>"
            f"<span class='puce' style='background:{coul_alerte};'>Alerte : {alerte}</span>"
            f"</div></div>", unsafe_allow_html=True)

    # --- Ligne 2 : anneaux de synthese ---
    a1, a2, a3 = st.columns(3)
    taux_conf = round((1 - nb_risque / len(df)) * 100)
    part_top = round(df.groupby("Type_Defaut")["Nombre_Defauts"].sum()
                     .sort_values(ascending=False).head(3).sum() / total * 100)
    part_mach = round(int(df[df.Machine == mach_crit]["Nombre_Defauts"].sum()) / total * 100)
    for col, titre_c, val, coul, etiq, coul_e in [
        (a1, "Taux de conformite estime", taux_conf, VERT, "Bon" if taux_conf >= 70 else "Moyen",
         VERT if taux_conf >= 70 else ORANGE),
        (a2, "Concentration Top 3 defauts", part_top, BLEU, "Pareto", BLEU),
        (a3, f"Part de {mach_crit}", part_mach, ROUGE, "Critique", ROUGE)]:
        with col:
            st.markdown(f"#### {titre_c}")
            st.markdown(f"<span class='puce' style='background:{coul_e};'>{etiq}</span>",
                        unsafe_allow_html=True)
            st.plotly_chart(jauge_anneau(val, coul), use_container_width=True)

    st.markdown("**Defauts par section**")
    d = df.groupby("Section")["Nombre_Defauts"].sum().sort_values(ascending=True)
    fig = px.bar(d, orientation="h", color_discrete_sequence=[BLEU_CLAIR])
    fig.update_layout(showlegend=False, xaxis_title="Defauts", yaxis_title="")
    st.plotly_chart(style_fig(fig, 340), use_container_width=True)

    st.markdown("**Synthese pour le service qualite**")
    top = df.groupby("Type_Defaut")["Nombre_Defauts"].sum().sort_values(ascending=False)
    trois = ", ".join(top.head(3).index.tolist())
    part = round(top.head(3).sum() / top.sum() * 100)
    st.markdown(
        f"- **Volume** : {total} defauts sur {len(df)} combinaisons analysees.\n"
        f"- **Machine critique** : {mach_crit} — inspection prioritaire.\n"
        f"- **Section critique** : {sect_crit}.\n"
        f"- **Defauts dominants** : {trois} ({part} % du total) — agir ici donne le meilleur retour.\n"
        f"- **Detection IA** : {nb_risque} combinaisons a risque, a traiter en prevention.")


# ===========================================================================
# 6. PAGE ANALYSE
# ===========================================================================
with onglets[1]:
    st.markdown("**Diagramme de Pareto des defauts**")
    p = df.groupby("Type_Defaut")["Nombre_Defauts"].sum().sort_values(ascending=False)
    p = p[p > 0]; cum = p.cumsum() / p.sum() * 100
    fig = go.Figure()
    fig.add_bar(x=p.index, y=p.values, marker_color=BLEU, name="Defauts")
    fig.add_scatter(x=p.index, y=cum.values, yaxis="y2", mode="lines+markers",
                    line=dict(color=ROUGE), name="% cumule")
    fig.add_hline(y=80, line_dash="dash", line_color="grey", yref="y2")
    fig.update_layout(yaxis=dict(title="Defauts"),
                      yaxis2=dict(title="% cumule", overlaying="y", side="right",
                                  range=[0, 105]),
                      legend=dict(orientation="h", y=1.14))
    st.plotly_chart(style_fig(fig, 440), use_container_width=True)

    # Interpretation automatique du Pareto
    seuil80 = cum[cum <= 80]
    n80 = max(len(seuil80), 1)
    liste80 = ", ".join(p.index[:n80])
    part80 = round(p.iloc[:n80].sum() / p.sum() * 100)
    bloc("Comment lire ce graphique", f"""
        <p style='font-size:13.5px; color:{ENCRE}; line-height:1.7;'>
        Les barres montrent le nombre de defauts par type, du plus frequent au moins
        frequent. La courbe rouge indique le pourcentage cumule : elle permet de voir
        combien de types de defauts suffisent a expliquer la majorite des non-conformites.
        <br><br>
        <b>Ce que disent vos donnees</b> : {n80} type(s) de defaut sur {len(p)} representent
        deja <b>{part80} %</b> du total des non-conformites, a savoir : {liste80}.
        <br><br>
        <b>Decision pour le service Qualite</b> : concentrer les actions correctives sur
        ces defauts prioritaires produit le meilleur retour. Traiter les defauts rares
        situes a droite du graphique aurait un impact marginal.</p>""", BLEU)

    if "Defect ratio (%)" in kpi_mois.columns:
        st.markdown("**Evolution mensuelle du taux de defauts**")
        fig = go.Figure()
        fig.add_scatter(x=kpi_mois["Mois"], y=kpi_mois["Defect ratio (%)"],
                        mode="lines+markers", name="Taux reel", line=dict(color=BLEU))
        fig.add_scatter(x=kpi_mois["Mois"], y=kpi_mois["Target (%)"], mode="lines",
                        name="Cible", line=dict(color=ROUGE, dash="dash"))
        fig.update_layout(yaxis_title="Taux (%)", legend=dict(orientation="h", y=1.14))
        st.plotly_chart(style_fig(fig, 320), use_container_width=True)

        # Interpretation automatique de l'evolution
        taux = kpi_mois["Defect ratio (%)"]
        cible = float(kpi_mois["Target (%)"].iloc[0])
        depassements = int((taux > cible).sum())
        pire_mois = kpi_mois.loc[taux.idxmax(), "Mois"]
        pire_val = round(float(taux.max()), 3)
        tendance = ("en hausse" if float(taux.iloc[-1]) > float(taux.iloc[0])
                    else "en baisse")
        bloc("Comment lire ce graphique", f"""
            <p style='font-size:13.5px; color:{ENCRE}; line-height:1.7;'>
            La courbe bleue represente le taux de defauts reellement observe chaque mois.
            La ligne rouge en pointilles est l'objectif fixe par l'entreprise ({cible} %).
            Chaque point situe au-dessus de la ligne rouge signale un mois hors objectif.
            <br><br>
            <b>Ce que disent vos donnees</b> : l'objectif est depasse sur
            <b>{depassements} mois sur {len(taux)}</b>. Le pic est atteint en
            <b>{pire_mois}</b> ({pire_val} %). La tendance generale est {tendance}.
            <br><br>
            <b>Decision pour le service Qualite</b> : les mois de depassement doivent etre
            analyses (changement de serie, maintenance, matiere premiere). Un suivi mensuel
            permet de verifier si les actions correctives ramenent le taux sous l'objectif.
            <br><br>
            <i>Limite : ce suivi repose sur 7 points mensuels agreges ; les defauts detailles
            ne sont pas horodates dans la base.</i></p>""", ORANGE)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Heatmap Machine x Type de defaut**")
        piv = df.pivot_table(index="Type_Defaut", columns="Machine",
                             values="Nombre_Defauts", aggfunc="sum", fill_value=0)
        st.plotly_chart(style_fig(px.imshow(piv, text_auto=True, aspect="auto",
                        color_continuous_scale="Blues"), 520), use_container_width=True)
    with c2:
        st.markdown("**Heatmap Section x Type de defaut**")
        piv = df.pivot_table(index="Type_Defaut", columns="Section",
                             values="Nombre_Defauts", aggfunc="sum", fill_value=0)
        st.plotly_chart(style_fig(px.imshow(piv, text_auto=True, aspect="auto",
                        color_continuous_scale="Blues"), 520), use_container_width=True)

    # Interpretation automatique des heatmaps
    pivm = df.pivot_table(index="Type_Defaut", columns="Machine",
                          values="Nombre_Defauts", aggfunc="sum", fill_value=0)
    if pivm.size:
        val_max = int(pivm.values.max())
        pos = pivm.stack().idxmax()
        defaut_max, machine_max = pos[0], pos[1]
        bloc("Comment lire ces cartes de chaleur", f"""
            <p style='font-size:13.5px; color:{ENCRE}; line-height:1.7;'>
            Chaque case croise un type de defaut (en ligne) avec une machine ou une section
            (en colonne). Plus la case est <b>foncee</b>, plus ce defaut est frequent sur cet
            equipement. Les cases claires signalent des situations maitrisees.
            <br><br>
            <b>Ce que disent vos donnees</b> : le point le plus critique est le defaut
            <b>{defaut_max}</b> sur la machine <b>{machine_max}</b> ({val_max} occurrences).
            <br><br>
            <b>Decision pour le service Qualite</b> : ces cartes montrent que les defauts ne
            sont pas repartis au hasard mais <b>localises</b> sur certains couples
            machine / defaut. L'action corrective doit donc etre ciblee sur ces couples
            precis plutot que generalisee a toute la ligne de production. C'est exactement
            ce que le modele IA exploite pour predire le risque.</p>""", ROUGE)


# ===========================================================================
# 7. PAGE PREDICTION IA (performances du modele)
# ===========================================================================
with onglets[2]:
    m = metriques
    cm = res["cm"]
    tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])

    # ---- Performances (cartes pedagogiques) ----
    st.markdown("### Performance du modele IA")
    c = st.columns(4)
    kpi_metrique(c[0], "Accuracy", m["accuracy"], "bullseye", BLEU,
                 "Pourcentage global de bonnes predictions.")
    kpi_metrique(c[1], "Precision", m["precision"], "check2-circle", VERT,
                 "Fiabilite des defauts detectes : quand l'IA alerte, a-t-elle raison ?")
    kpi_metrique(c[2], "Recall", m["recall"], "search", ORANGE,
                 "Capacite du modele a detecter les vrais defauts.")
    kpi_metrique(c[3], "F1-score", m["f1"], "star", BLEU_FONCE,
                 "Equilibre entre Precision et Recall.")
    st.write("")

    # ---- Informations sur le modele ----
    bloc("Informations sur le modele", f"""
        <table style='width:100%; font-size:13.5px;'>
        <tr><td style='padding:7px 0; color:{GRIS};'>Algorithme</td>
            <td style='text-align:right; font-weight:700; color:{ENCRE};'>Random Forest</td></tr>
        <tr><td style='padding:7px 0; color:{GRIS};'>Nombre d'arbres</td>
            <td style='text-align:right; font-weight:700; color:{ENCRE};'>200</td></tr>
        <tr><td style='padding:7px 0; color:{GRIS};'>Variables utilisees</td>
            <td style='text-align:right; font-weight:700; color:{ENCRE};'>
            Machine, Section, Capacite (mm2)</td></tr>
        <tr><td style='padding:7px 0; color:{GRIS};'>Validation croisee (K=5)</td>
            <td style='text-align:right; font-weight:700; color:{ENCRE};'>
            F1 = {m['cv_f1']} (+/- {m['cv_std']})</td></tr>
        <tr><td style='padding:7px 0; color:{GRIS};'>Seuil de decision</td>
            <td style='text-align:right; font-weight:700; color:{ENCRE};'>{m['seuil']}</td></tr>
        </table>
        <p style='font-size:12px; color:{GRIS}; margin-top:12px;'>
        Le type de defaut est volontairement exclu des variables afin d'eviter une fuite
        de donnees. Le seuil de decision est optimise pour privilegier la detection des
        defauts plutot que le seuil standard de 0,5.</p>""", BLEU)

    # ---- Matrice de confusion + interpretation automatique ----
    g1, g2 = st.columns([1, 1])
    with g1:
        st.markdown("#### Matrice de confusion")
        lab = ["Pas a risque", "A risque"]
        fig = px.imshow(cm, x=lab, y=lab, text_auto=True,
                        color_continuous_scale="Blues", aspect="auto")
        fig.update_layout(xaxis_title="Prediction du modele", yaxis_title="Realite")
        st.plotly_chart(style_fig(fig, 380), use_container_width=True)

    with g2:
        # Interpretation generee automatiquement
        total_reels = tp + fn
        taux_detect = round(tp / total_reels * 100) if total_reels else 0
        if taux_detect >= 70:
            juge = ("Le modele detecte correctement la majorite des non-conformites. "
                    "Les faux negatifs restent limites, ce qui est essentiel en controle "
                    "qualite : un defaut non detecte peut entrainer des couts eleves.")
        elif taux_detect >= 50:
            juge = ("Le modele detecte plus de la moitie des non-conformites reelles. "
                    "Le nombre de defauts non detectes reste toutefois notable et doit "
                    "etre surveille, un faux negatif etant plus couteux qu'une fausse alerte.")
        else:
            juge = ("Le modele laisse passer une part importante des non-conformites. "
                    "En controle qualite, ce niveau de detection est insuffisant : "
                    "il conviendrait d'enrichir les donnees ou d'abaisser le seuil de decision.")

        bloc("Analyse de la matrice de confusion", f"""
            <table style='width:100%; font-size:13px;'>
            <tr><td style='padding:6px 0;'><b style='color:{VERT};'>Vrais negatifs (TN) : {tn}</b><br>
                <span style='color:{GRIS};'>Cas sains correctement identifies.</span></td></tr>
            <tr><td style='padding:6px 0;'><b style='color:{VERT};'>Vrais positifs (TP) : {tp}</b><br>
                <span style='color:{GRIS};'>Defauts correctement detectes.</span></td></tr>
            <tr><td style='padding:6px 0;'><b style='color:{ORANGE};'>Faux positifs (FP) : {fp}</b><br>
                <span style='color:{GRIS};'>Fausses alertes : un controle inutile est declenche.</span></td></tr>
            <tr><td style='padding:6px 0;'><b style='color:{ROUGE};'>Faux negatifs (FN) : {fn}</b><br>
                <span style='color:{GRIS};'>Defauts non detectes : le cas le plus couteux.</span></td></tr>
            </table>
            <p style='font-size:13px; color:{ENCRE}; margin-top:14px;
                      background:#F4F8FC; padding:12px 14px; border-radius:12px;'>
            <b>Interpretation ({taux_detect} % des defauts reels detectes)</b><br>{juge}</p>""",
            BLEU_FONCE)

    # ---- Facteurs influencant les predictions ----
    st.markdown("#### Facteurs influencant les predictions de l'IA")
    imp = res["importance"].copy()

    def _famille(v):
        if v.startswith("Machine_"):
            return "Machine"
        if v.startswith("Section_"):
            return "Section"
        return "Capacite (mm2)"

    imp["famille"] = imp["variable"].apply(_famille)
    par_famille = (imp.groupby("famille")["importance"].sum()
                   .sort_values(ascending=False))

    gg1, gg2 = st.columns([1.3, 1])
    with gg1:
        top = imp.head(12).sort_values("importance", ascending=True)
        fig = px.bar(top, x="importance", y="variable", orientation="h",
                     color_discrete_sequence=[BLEU])
        fig.update_layout(xaxis_title="Importance", yaxis_title="")
        st.plotly_chart(style_fig(fig, 400), use_container_width=True)
    with gg2:
        classement = "".join(
            f"<tr><td style='padding:8px 0;'><b>{i}. {nom}</b></td>"
            f"<td style='text-align:right; color:{BLEU}; font-weight:700;'>"
            f"{round(v * 100, 1)} %</td></tr>"
            for i, (nom, v) in enumerate(par_famille.items(), 1))
        premier = par_famille.index[0]
        suite = ", suivie de " + " et de ".join(par_famille.index[1:]) \
            if len(par_famille) > 1 else ""
        bloc("Variables les plus influentes", f"""
            <p style='font-size:12.5px; color:{GRIS};'>
            Le modele Random Forest calcule l'importance de chaque variable.
            Plus cette importance est elevee, plus la variable influence la prediction.</p>
            <table style='width:100%; font-size:13.5px;'>{classement}</table>
            <p style='font-size:13px; color:{ENCRE}; margin-top:12px;
                      background:#F4F8FC; padding:12px 14px; border-radius:12px;'>
            <b>Conclusion</b><br>La variable <b>{premier}</b> a le plus d'influence sur la
            prediction des non-conformites{suite}.</p>""", BLEU)

    # ---- Conclusion IA (generee automatiquement) ----
    if m["f1"] >= 0.6:
        fiabilite = "satisfaisante pour une aide a la decision"
    elif m["f1"] >= 0.45:
        fiabilite = ("moderee : le modele apporte une aide utile en appui du jugement "
                     "des equipes qualite, sans s'y substituer")
    else:
        fiabilite = "insuffisante pour un usage autonome ; il doit rester un outil d'alerte"

    bloc("Conclusion du modele IA", f"""
        <p style='font-size:13.5px; color:{ENCRE}; line-height:1.7;'>
        Le modele Random Forest atteint une <b>accuracy de {m['accuracy']}</b>, une
        <b>precision de {m['precision']}</b> et un <b>recall de {m['recall']}</b>
        (F1-score : {m['f1']}). Il detecte {taux_detect} % des non-conformites reelles
        de l'echantillon de test.<br><br>
        Les predictions sont principalement influencees par la variable
        <b>{par_famille.index[0]}</b>, ce qui confirme les constats de l'analyse Pareto :
        certaines machines et sections concentrent l'essentiel des defauts.<br><br>
        <b>Fiabilite</b> : la performance est {fiabilite}.<br><br>
        <b>Utilisation par le service Qualite</b> : le modele permet d'identifier en amont
        les combinaisons machine / section les plus a risque, de cibler les inspections
        preventives et de prioriser les actions correctives sur les configurations
        signalees, avant l'apparition du defaut.</p>""", VERT)

with onglets[3]:
    # --- Vue generale : defaut le plus probable par machine ---
    st.markdown("#### Type de defaut le plus probable par machine")
    lignes = []
    for mach in sorted(df["Machine"].dropna().astype(str).unique()):
        sub = df[(df["Machine"] == mach) & (df["Nombre_Defauts"] > 0)]
        if sub.empty:
            continue
        tot = sub.groupby("Type_Defaut")["Nombre_Defauts"].sum().sort_values(ascending=False)
        lignes.append({"Machine": mach,
                       "Defaut le plus probable": tot.index[0],
                       "Part": f"{round(tot.iloc[0] / tot.sum() * 100, 1)} %",
                       "Total defauts": int(tot.sum())})
    st.dataframe(pd.DataFrame(lignes), use_container_width=True, hide_index=True)
    st.caption("Vue generale : defaut dominant observe sur chaque machine, toutes sections confondues.")

    st.markdown("**Estimer le risque d'une configuration**")
    c1, c2, c3 = st.columns(3)
    machine = c1.selectbox("Machine", sorted(df["Machine"].dropna().astype(str).unique()))
    section = c2.selectbox("Section", sorted(df["Section"].dropna().astype(str).unique()))
    typ = c3.selectbox("Type de defaut", sorted(df["Type_Defaut"].dropna().astype(str).unique()))
    lancer = st.button("Predire", type="primary")

    if lancer:
        sub = dpred[(dpred["Machine"] == machine) & (dpred["Section"] == section)
                    & (dpred["Type_Defaut"] == typ)]
        if len(sub):
            proba = float(sub["probabilite"].iloc[0])
            classe = int(sub["risque_predit"].iloc[0])
        else:
            proba, classe = 0.0, 0
        pct = round(proba * 100, 1)
        if pct < 34:
            couleur, niveau = VERT, "Faible"
        elif pct < 67:
            couleur, niveau = ORANGE, "Moyen"
        else:
            couleur, niveau = ROUGE, "Eleve"

        a, b = st.columns(2)
        with a:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=pct, number={"suffix": " %"},
                title={"text": "Probabilite de non-conformite"},
                gauge={"axis": {"range": [0, 100]}, "bar": {"color": couleur},
                       "steps": [{"range": [0, 34], "color": "#E8F6EF"},
                                 {"range": [34, 67], "color": "#FDF0DC"},
                                 {"range": [67, 100], "color": "#FBE6E6"}]}))
            st.plotly_chart(style_fig(fig, 340), use_container_width=True)
        with b:
            st.markdown(
                f"<div class='card'>"
                f"<h3 style='color:{couleur}; margin-top:0;'>Risque {niveau}</h3>"
                f"<p><b>Machine</b> : {machine}<br>"
                f"<b>Section</b> : {section}<br>"
                f"<b>Type de defaut</b> : {typ}<br>"
                f"<b>Probabilite</b> : {pct} %<br>"
                f"<b>Decision du modele</b> : "
                f"{'A RISQUE' if classe == 1 else 'PAS A RISQUE'}</p></div>",
                unsafe_allow_html=True)

        d_prob, part_prob = defaut_le_plus_probable(df, machine, section)
        if d_prob:
            st.markdown(
                f"<div class='card'><b>Defaut le plus probable sur cette combinaison</b> : "
                f"{d_prob} ({round(part_prob * 100, 1)} % des defauts observes sur "
                f"{machine} / {section})</div>", unsafe_allow_html=True)

        st.markdown("**Actions preventives recommandees** (avant apparition du defaut)")
        for action in actions_pour(typ):
            st.markdown(f"- {action}")


# ===========================================================================
# 9. PAGE ALERTES
# ===========================================================================
with onglets[4]:
    st.markdown("**Etat des machines**")
    alertes = (dpred[dpred["risque_predit"] == 1].groupby("Machine").size()
               .reindex(sorted(df["Machine"].dropna().astype(str).unique()), fill_value=0)
               .sort_values(ascending=False))
    for machine, nb in alertes.items():
        nb = int(nb)
        sub = dpred[(dpred["Machine"] == machine) & (dpred["risque_predit"] == 1)]
        pire = sub.sort_values("probabilite", ascending=False)["Type_Defaut"].iloc[0] \
            if len(sub) else "-"
        pmax = round(sub["probabilite"].max() * 100, 1) if len(sub) else 0.0
        if nb == 0:
            coul, lib, act = VERT, "Faible", "Situation normale — suivi habituel"
        elif nb <= 5:
            coul, lib, act = ORANGE, "Moyen", "Surveillance renforcee"
        else:
            coul, lib, act = ROUGE, "Critique", "Inspection immediate"
        st.markdown(
            f"<div style='padding:8px 0; border-bottom:1px solid #EEF3F7;'>"
            f"<span class='badge' style='background:{coul};'>{lib}</span> "
            f"&nbsp;<b>{machine}</b> — {nb} combinaison(s) a risque<br>"
            f"<span style='color:{GRIS}; font-size:13px;'>"
            f"Defaut le plus probable : {pire} ({pmax} %) — Action : {act}</span></div>",
            unsafe_allow_html=True)


# ===========================================================================
# 10. PAGE RAPPORTS
# ===========================================================================
with onglets[5]:
    st.markdown("### Suivi des performances")
    archiver_reference()          # la base de reference sert de point de depart
    archives = lire_index_archives()

    if len(archives) < 2:
        st.info("Au moins deux jeux de donnees sont necessaires pour comparer. "
                "Importez un nouveau fichier depuis l'onglet Donnees : chaque import "
                "est archive automatiquement et pourra etre compare ici.")
        if archives:
            st.dataframe(pd.DataFrame(archives)[["fichier", "date", "lignes",
                                                 "total_defauts"]],
                         use_container_width=True, hide_index=True)
    else:
        libelles = {f"{a['fichier']} — {a['date']}": a for a in archives}
        c1, c2 = st.columns(2)
        avant_l = c1.selectbox("Periode de reference (avant)", list(libelles),
                               index=0, key="cmp_avant")
        apres_l = c2.selectbox("Periode a comparer (apres)", list(libelles),
                               index=len(libelles) - 1, key="cmp_apres")

        a_av, a_ap = libelles[avant_l], libelles[apres_l]
        d_av = charger_archive(a_av["chemin"])
        d_ap = charger_archive(a_ap["chemin"])

        def _synthese(d):
            tot = int(d["Nombre_Defauts"].sum())
            mach = d.groupby("Machine")["Nombre_Defauts"].sum()
            sect = d.groupby("Section")["Nombre_Defauts"].sum()
            typ = d.groupby("Type_Defaut")["Nombre_Defauts"].sum()
            return {"total": tot,
                    "machine": mach.idxmax() if len(mach) else "-",
                    "section": sect.idxmax() if len(sect) else "-",
                    "defaut": typ.idxmax() if len(typ) else "-",
                    "mach": mach, "sect": sect, "typ": typ}

        sav, sap = _synthese(d_av), _synthese(d_ap)
        evol = ((sap["total"] - sav["total"]) / sav["total"] * 100) if sav["total"] else 0
        evol = round(evol, 1)

        # --- KPI avant / apres ---
        st.markdown("#### Indicateurs avant / apres")
        k = st.columns(4)
        carte_kpi(k[0], "Total avant", sav["total"], "clock-history", GRIS)
        carte_kpi(k[1], "Total apres", sap["total"], "clipboard-data",
                  ROUGE if evol > 0 else VERT)
        carte_kpi(k[2], "Evolution", f"{evol:+.1f} %",
                  "graph-up-arrow" if evol > 0 else "graph-down-arrow",
                  ROUGE if evol > 0 else VERT)
        carte_kpi(k[3], "Machine critique", f"{sav['machine']} -> {sap['machine']}",
                  "hdd-stack", BLEU, texte=True)
        st.write("")

        # --- Comparaison par machine ---
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("#### Defauts par machine")
            machines = sorted(set(sav["mach"].index) | set(sap["mach"].index))
            cmp_m = pd.DataFrame({
                "Machine": machines,
                "Avant": [int(sav["mach"].get(m, 0)) for m in machines],
                "Apres": [int(sap["mach"].get(m, 0)) for m in machines]})
            fig = px.bar(cmp_m, x="Machine", y=["Avant", "Apres"], barmode="group",
                         color_discrete_sequence=[GRIS_CLAIR, BLEU])
            fig.update_layout(yaxis_title="Defauts", xaxis_title="",
                              legend_title_text="")
            st.plotly_chart(style_fig(fig, 340), use_container_width=True)
        with g2:
            st.markdown("#### Defauts par type (Top 8)")
            types = list(sap["typ"].sort_values(ascending=False).head(8).index)
            cmp_t = pd.DataFrame({
                "Type": types,
                "Avant": [int(sav["typ"].get(t, 0)) for t in types],
                "Apres": [int(sap["typ"].get(t, 0)) for t in types]})
            fig = px.bar(cmp_t, x="Type", y=["Avant", "Apres"], barmode="group",
                         color_discrete_sequence=[GRIS_CLAIR, BLEU])
            fig.update_layout(yaxis_title="Defauts", xaxis_title="",
                              legend_title_text="")
            st.plotly_chart(style_fig(fig, 340), use_container_width=True)

        # --- Courbe d'evolution sur tout l'historique ---
        st.markdown("#### Evolution du total de non-conformites")
        hist_df = pd.DataFrame(archives)
        fig = px.line(hist_df, x="date", y="total_defauts", markers=True,
                      color_discrete_sequence=[BLEU])
        fig.update_layout(yaxis_title="Total defauts", xaxis_title="Import")
        st.plotly_chart(style_fig(fig, 300), use_container_width=True)

        # --- Progression / regression par machine ---
        cmp_m["Ecart"] = cmp_m["Apres"] - cmp_m["Avant"]
        progres = cmp_m[cmp_m["Ecart"] < 0].sort_values("Ecart")
        regres = cmp_m[cmp_m["Ecart"] > 0].sort_values("Ecart", ascending=False)
        cmp_t["Ecart"] = cmp_t["Apres"] - cmp_t["Avant"]
        d_baisse = cmp_t[cmp_t["Ecart"] < 0]["Type"].tolist()
        d_hausse = cmp_t[cmp_t["Ecart"] > 0]["Type"].tolist()

        if evol < -5:
            verdict, coul = "Amelioration de la qualite", VERT
            texte = (f"Le nombre total de non-conformites a <b>diminue de "
                     f"{abs(evol)} %</b> entre les deux periodes.")
        elif evol > 5:
            verdict, coul = "Degradation de la qualite", ROUGE
            texte = (f"Le nombre total de non-conformites a <b>augmente de "
                     f"{evol} %</b> entre les deux periodes.")
        else:
            verdict, coul = "Qualite stable", ORANGE
            texte = (f"Le nombre total de non-conformites est <b>stable</b> "
                     f"({evol:+.1f} %).")

        reco = []
        if regres["Machine"].tolist():
            reco.append(f"Prioriser l'inspection des machines en regression : "
                        f"{', '.join(regres['Machine'].head(3))}.")
        if d_hausse:
            reco.append(f"Analyser les causes racines des defauts en hausse : "
                        f"{', '.join(d_hausse[:3])}.")
        if progres["Machine"].tolist():
            reco.append(f"Capitaliser sur les bonnes pratiques des machines en progres : "
                        f"{', '.join(progres['Machine'].head(3))}.")
        if not reco:
            reco.append("Maintenir le plan de surveillance actuel.")

        bloc("Conclusion automatique", f"""
            <p style='font-size:14px; color:{coul}; font-weight:700; margin-bottom:10px;'>
            {verdict}</p>
            <p style='font-size:13.5px; color:{ENCRE}; line-height:1.7;'>
            {texte}<br><br>
            <b>Machines en progres</b> (moins de defauts) :
            {', '.join(progres['Machine']) if len(progres) else 'aucune'}<br>
            <b>Machines en regression</b> (plus de defauts) :
            {', '.join(regres['Machine']) if len(regres) else 'aucune'}<br>
            <b>Defauts en diminution</b> : {', '.join(d_baisse) if d_baisse else 'aucun'}<br>
            <b>Defauts en augmentation</b> : {', '.join(d_hausse) if d_hausse else 'aucun'}
            <br><br>
            <b>Recommandations pour le service Qualite</b><br>
            """ + "<br>".join(f"- {r}" for r in reco) + "</p>", coul)

        st.markdown("#### Historique des imports")
        st.dataframe(hist_df[["fichier", "date", "lignes", "total_defauts"]],
                     use_container_width=True, hide_index=True)

with onglets[6]:
    st.markdown("### Gestion des donnees")
    if donnees_importees_actives():
        h = lire_historique()
        st.success(f"Donnees importees actives : {h.get('fichier', '-')} "
                   f"({h.get('lignes', len(df))} lignes, importe le {h.get('date', '-')}). "
                   f"Ces donnees sont conservees apres fermeture de l'application.")

    hist = lire_historique()
    c1, c2 = st.columns([1.15, 1])

    with c1:
        st.markdown("#### Importer un fichier")
        st.caption("Colonnes requises : Section, Machine, Type_Defaut, Nombre_Defauts")
        f = st.file_uploader("Importer un fichier Excel ou CSV", type=["xlsx", "csv"],
                             key="upload_donnees")

        if f is not None:
            feuilles = lister_feuilles(f)
            d_imp, erreur = None, None

            # --- Fichier Excel a plusieurs feuilles : laisser le choix ---
            if len(feuilles) > 1:
                st.info(f"Ce fichier contient {len(feuilles)} feuilles : "
                        f"{', '.join(feuilles)}")
                mode = st.radio(
                    "Que faut-il importer ?",
                    ["Une seule feuille", "Fusionner plusieurs feuilles"],
                    horizontal=True, key="mode_feuille")

                if mode == "Une seule feuille":
                    choix_f = st.selectbox("Feuille a importer", feuilles,
                                           key="choix_feuille")
                    d_imp, erreur = lire_fichier_importe(f, feuille=choix_f)
                else:
                    choix_multi = st.multiselect(
                        "Feuilles a fusionner", feuilles, default=feuilles,
                        key="choix_multi")
                    if choix_multi:
                        d_imp, ignorees = fusionner_feuilles(f, choix_multi)
                        if ignorees:
                            st.warning("Feuilles ignorees (colonnes requises absentes) : "
                                       + ", ".join(ignorees))
                        if d_imp is None:
                            erreur = "Aucune feuille ne contient les colonnes requises."
                    else:
                        st.info("Selectionnez au moins une feuille.")
            else:
                d_imp, erreur = lire_fichier_importe(f)

            if erreur:
                st.error(f"Erreurs detectees : {erreur}")
            elif d_imp is not None:
                # --- Validation des donnees ---
                problemes = []
                nuls = int(d_imp[["Section", "Machine", "Type_Defaut",
                                  "Nombre_Defauts"]].isnull().sum().sum())
                if nuls:
                    problemes.append(f"{nuls} valeur(s) manquante(s)")
                doublons = int(d_imp.duplicated(
                    subset=["Section", "Machine", "Type_Defaut"]).sum())
                if doublons:
                    problemes.append(f"{doublons} doublon(s) sur Section/Machine/Type")
                if not pd.api.types.is_numeric_dtype(d_imp["Nombre_Defauts"]):
                    problemes.append("La colonne Nombre_Defauts n'est pas numerique")
                elif (d_imp["Nombre_Defauts"] < 0).any():
                    problemes.append("Valeurs negatives dans Nombre_Defauts")

                if problemes:
                    st.warning("Donnees importees avec reserves :")
                    for p in problemes:
                        st.markdown(f"- {p}")
                else:
                    st.success(f"Donnees valides : {len(d_imp)} lignes, "
                               f"aucune anomalie detectee.")

                st.dataframe(d_imp.head(10), use_container_width=True, hide_index=True)

                if st.button("Appliquer ce fichier et reentrainer le modele",
                             type="primary", use_container_width=True):
                    sauvegarder_donnees(d_imp, f.name)
                    st.cache_data.clear()
                    st.cache_resource.clear()
                    st.session_state["version"] += 1
                    st.rerun()

    with c2:
        st.markdown("#### Actions")
        if st.button("Actualiser les donnees", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.session_state["version"] += 1
            st.rerun()
        if st.button("Reentrainer le modele IA", use_container_width=True):
            st.cache_resource.clear()
            st.session_state["version"] += 1
            st.rerun()
        if donnees_importees_actives():
            if st.button("Revenir aux donnees de reference", use_container_width=True):
                restaurer_reference()
                st.cache_data.clear()
                st.cache_resource.clear()
                st.session_state["version"] += 1
                st.rerun()

    st.write("")
    d1, d2 = st.columns(2)
    with d1:
        source = hist.get("fichier", "data_clean.csv (reference)")
        maj = hist.get("date", "-")
        bloc("Historique des donnees", f"""
            <table style='width:100%; font-size:13.5px;'>
            <tr><td style='padding:7px 0; color:{GRIS};'>Dernier fichier</td>
                <td style='text-align:right; font-weight:700;'>{source}</td></tr>
            <tr><td style='padding:7px 0; color:{GRIS};'>Derniere mise a jour</td>
                <td style='text-align:right; font-weight:700;'>{maj}</td></tr>
            <tr><td style='padding:7px 0; color:{GRIS};'>Lignes</td>
                <td style='text-align:right; font-weight:700;'>{len(df)}</td></tr>
            <tr><td style='padding:7px 0; color:{GRIS};'>Colonnes</td>
                <td style='text-align:right; font-weight:700;'>{df.shape[1]}</td></tr>
            <tr><td style='padding:7px 0; color:{GRIS};'>Version</td>
                <td style='text-align:right; font-weight:700;'>
                {st.session_state.get('version', 0)}</td></tr>
            </table>""", BLEU)
    with d2:
        bloc("Performances du modele actuel", f"""
            <table style='width:100%; font-size:13.5px;'>
            <tr><td style='padding:7px 0; color:{GRIS};'>Accuracy</td>
                <td style='text-align:right; font-weight:700;'>{metriques['accuracy']}</td></tr>
            <tr><td style='padding:7px 0; color:{GRIS};'>Precision</td>
                <td style='text-align:right; font-weight:700;'>{metriques['precision']}</td></tr>
            <tr><td style='padding:7px 0; color:{GRIS};'>Recall</td>
                <td style='text-align:right; font-weight:700;'>{metriques['recall']}</td></tr>
            <tr><td style='padding:7px 0; color:{GRIS};'>F1-score</td>
                <td style='text-align:right; font-weight:700;'>{metriques['f1']}</td></tr>
            </table>
            <p style='font-size:12px; color:{GRIS}; margin-top:10px;'>
            Le modele est reentraine automatiquement a chaque import ou actualisation.</p>""",
            VERT)

    st.write("")
    st.markdown("#### Apercu des donnees")
    st.dataframe(df.head(50), use_container_width=True, hide_index=True)

with onglets[7]:
    st.markdown("**Export des donnees et resultats**")
    risques = dpred[dpred["risque_predit"] == 1][
        ["Section", "Machine", "Type_Defaut", "Nombre_Defauts", "probabilite"]
    ].sort_values("probabilite", ascending=False)
    c1, c2 = st.columns(2)
    c1.download_button("Telecharger les combinaisons a risque (CSV)",
                       risques.to_csv(index=False).encode("utf-8-sig"),
                       "combinaisons_a_risque.csv", "text/csv",
                       use_container_width=True)
    c2.download_button("Telecharger tous les resultats (CSV)",
                       dpred.to_csv(index=False).encode("utf-8-sig"),
                       "resultats_complets.csv", "text/csv",
                       use_container_width=True)
    st.dataframe(risques, use_container_width=True)


# ===========================================================================
# 11. PAGE A PROPOS
# ===========================================================================
with onglets[8]:
    st.markdown("### Parametres")

    c1, c2 = st.columns(2)

    with c1:
        bloc("Application", f"""
            <table style='width:100%; font-size:13.5px;'>
            <tr><td style='padding:7px 0; color:{GRIS};'>Nom</td>
                <td style='text-align:right; font-weight:700;'>Service Qualite</td></tr>
            <tr><td style='padding:7px 0; color:{GRIS};'>Version</td>
                <td style='text-align:right; font-weight:700;'>1.0</td></tr>
            <tr><td style='padding:7px 0; color:{GRIS};'>Site</td>
                <td style='text-align:right; font-weight:700;'>
                SEWS CABIND MAROC — Ain Harrouda</td></tr>
            <tr><td style='padding:7px 0; color:{GRIS};'>Perimetre</td>
                <td style='text-align:right; font-weight:700;'>Cables Renault P3S</td></tr>
            </table>""", BLEU)

        bloc("Donnees", f"""
            <table style='width:100%; font-size:13.5px;'>
            <tr><td style='padding:7px 0; color:{GRIS};'>Source active</td>
                <td style='text-align:right; font-weight:700;'>
                {'Fichier importe' if donnees_importees_actives() else 'Base de reference'}</td></tr>
            <tr><td style='padding:7px 0; color:{GRIS};'>Lignes chargees</td>
                <td style='text-align:right; font-weight:700;'>{len(df)}</td></tr>
            <tr><td style='padding:7px 0; color:{GRIS};'>Version des donnees</td>
                <td style='text-align:right; font-weight:700;'>
                {st.session_state.get('version', 0)}</td></tr>
            </table>
            <p style='font-size:12px; color:{GRIS}; margin-top:10px;'>
            La gestion des fichiers s'effectue depuis l'onglet Donnees.</p>""", BLEU_FONCE)

    with c2:
        bloc("Moteur de prediction", f"""
            <table style='width:100%; font-size:13.5px;'>
            <tr><td style='padding:7px 0; color:{GRIS};'>Statut</td>
                <td style='text-align:right; font-weight:700; color:{VERT};'>Actif</td></tr>
            <tr><td style='padding:7px 0; color:{GRIS};'>Fiabilite (F1-score)</td>
                <td style='text-align:right; font-weight:700;'>{metriques['f1']}</td></tr>
            <tr><td style='padding:7px 0; color:{GRIS};'>Taux de detection</td>
                <td style='text-align:right; font-weight:700;'>{metriques['recall']}</td></tr>
            </table>
            <p style='font-size:12px; color:{GRIS}; margin-top:10px;'>
            Le detail des performances est disponible dans l'onglet Prediction IA.</p>""", VERT)

        st.markdown("#### Session")
        st.info("Utilisateur connecte : admin — Service Qualite")
        if st.button("Deconnexion", type="primary", use_container_width=True):
            st.session_state.pop("connecte", None)
            st.rerun()
