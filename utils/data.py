"""data.py — Chargement des donnees, entrainement du modele, recommandations."""
import os
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
ASSETS = os.path.join(BASE, "assets")
COLONNES_REQUISES = {"Section", "Machine", "Type_Defaut", "Nombre_Defauts"}

# Fichier de travail : les donnees importees y sont SAUVEGARDEES sur disque,
# afin de survivre a la fermeture de l'application.
FICHIER_ACTIF = os.path.join(DATA, "data_active.csv")
FICHIER_REF = os.path.join(DATA, "data_clean.csv")
FICHIER_HIST = os.path.join(DATA, "historique.json")
DOSSIER_ARCHIVES = os.path.join(DATA, "archives")
INDEX_ARCHIVES = os.path.join(DATA, "archives", "index.json")


def _completer(d: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie et complete un jeu de donnees importe :
    - supprime les lignes vides (lignes de total, separateurs, etc.)
    - force les types (texte pour Section/Machine/Type_Defaut, numerique pour le compte)
    - ajoute la colonne Section_mm2_code si absente
    """
    d = d.copy()

    # 1) Supprimer les lignes ou une cle est vide (NaN) -> evite les erreurs de tri
    cles = [c for c in ["Section", "Machine", "Type_Defaut"] if c in d.columns]
    if cles:
        d = d.dropna(subset=cles)

    # 2) Forcer les colonnes cles en texte (evite le melange float/str)
    for c in cles:
        d[c] = d[c].astype(str).str.strip()
        d = d[~d[c].isin(["", "nan", "NaN", "None"])]

    # 3) Nombre_Defauts : numerique, valeurs manquantes -> 0
    if "Nombre_Defauts" in d.columns:
        d["Nombre_Defauts"] = pd.to_numeric(d["Nombre_Defauts"],
                                            errors="coerce").fillna(0).astype(int)

    # 4) Capacite en mm2 deduite du code section
    if "Section_mm2_code" not in d.columns:
        d["Section_mm2_code"] = (d["Section"].astype(str)
                                 .str.replace("P3S", "", regex=False)
                                 .str.extract(r"(\d+)")[0])
    d["Section_mm2_code"] = pd.to_numeric(d["Section_mm2_code"],
                                          errors="coerce").fillna(0).astype(int)

    return d.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def charger_donnees(_version: int = 0) -> pd.DataFrame:
    """
    Charge les donnees actives.
    Si un fichier a ete importe (data_active.csv), il est utilise en priorite ;
    sinon on retombe sur la base de reference (data_clean.csv).
    Les donnees importees PERSISTENT ainsi apres fermeture de l'application.
    """
    chemin = FICHIER_ACTIF if os.path.exists(FICHIER_ACTIF) else FICHIER_REF
    return _completer(pd.read_csv(chemin))


def sauvegarder_donnees(d: pd.DataFrame, nom_fichier: str) -> None:
    """
    Enregistre les donnees importees sur disque (persistance) ET archive une copie
    afin de permettre la comparaison entre periodes (page Suivi des performances).
    """
    import json, datetime, re
    d.to_csv(FICHIER_ACTIF, index=False, encoding="utf-8-sig")
    horodatage = datetime.datetime.now()
    info = {"fichier": nom_fichier,
            "date": horodatage.strftime("%d/%m/%Y %H:%M"),
            "lignes": len(d), "colonnes": int(d.shape[1])}
    with open(FICHIER_HIST, "w", encoding="utf-8") as f:
        json.dump(info, f)

    # --- Archivage ---
    os.makedirs(DOSSIER_ARCHIVES, exist_ok=True)
    cle = horodatage.strftime("%Y%m%d_%H%M%S")
    slug = re.sub(r"[^A-Za-z0-9_-]", "_", os.path.splitext(nom_fichier)[0])[:40]
    chemin = os.path.join(DOSSIER_ARCHIVES, f"{cle}__{slug}.csv")
    d.to_csv(chemin, index=False, encoding="utf-8-sig")

    index = lire_index_archives()
    index.append({"cle": cle, "fichier": nom_fichier,
                  "date": info["date"], "lignes": len(d),
                  "total_defauts": int(d["Nombre_Defauts"].sum()),
                  "chemin": os.path.basename(chemin)})
    with open(INDEX_ARCHIVES, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False)


def lire_index_archives() -> list:
    """Liste des jeux de donnees archives (du plus ancien au plus recent)."""
    import json
    if os.path.exists(INDEX_ARCHIVES):
        try:
            with open(INDEX_ARCHIVES, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def charger_archive(nom_csv: str) -> pd.DataFrame:
    """Charge un jeu de donnees archive."""
    return _completer(pd.read_csv(os.path.join(DOSSIER_ARCHIVES, nom_csv)))


def archiver_reference() -> None:
    """Ajoute la base de reference dans l'historique (point de depart des comparaisons)."""
    import json, datetime
    index = lire_index_archives()
    if any(a.get("cle") == "reference" for a in index):
        return
    os.makedirs(DOSSIER_ARCHIVES, exist_ok=True)
    d = _completer(pd.read_csv(FICHIER_REF))
    chemin = os.path.join(DOSSIER_ARCHIVES, "reference.csv")
    d.to_csv(chemin, index=False, encoding="utf-8-sig")
    index.insert(0, {"cle": "reference", "fichier": "Donnees de reference",
                     "date": "Initial", "lignes": len(d),
                     "total_defauts": int(d["Nombre_Defauts"].sum()),
                     "chemin": "reference.csv"})
    with open(INDEX_ARCHIVES, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False)


def lire_historique() -> dict:
    """Renvoie les informations du dernier import (ou valeurs par defaut)."""
    import json
    if os.path.exists(FICHIER_HIST):
        try:
            with open(FICHIER_HIST, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def donnees_importees_actives() -> bool:
    """Indique si un fichier importe est actuellement utilise."""
    return os.path.exists(FICHIER_ACTIF)


def restaurer_reference() -> None:
    """Supprime les donnees importees et revient a la base de reference."""
    for f in (FICHIER_ACTIF, FICHIER_HIST):
        if os.path.exists(f):
            os.remove(f)


@st.cache_data(show_spinner=False)
def charger_kpi(_version: int = 0) -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA, "kpi_mensuel.csv"))


def lister_feuilles(fichier):
    """Renvoie la liste des feuilles d'un fichier Excel (vide si CSV)."""
    if fichier.name.lower().endswith(".csv"):
        return []
    try:
        fichier.seek(0)
        return pd.ExcelFile(fichier).sheet_names
    except Exception:
        return []


def lire_fichier_importe(fichier, feuille=None):
    """
    Lit un fichier importe (CSV ou Excel) et verifie ses colonnes.
    feuille : nom de la feuille Excel a lire (la 1re si None).
    Renvoie (DataFrame, erreur).
    """
    try:
        fichier.seek(0)
        if fichier.name.lower().endswith(".csv"):
            d = pd.read_csv(fichier)
        else:
            d = pd.read_excel(fichier, sheet_name=feuille if feuille else 0)
    except Exception as e:
        return None, f"Lecture impossible : {e}"

    manquantes = COLONNES_REQUISES - set(d.columns)
    if manquantes:
        return None, (f"Colonnes manquantes : {', '.join(sorted(manquantes))}. "
                      f"Colonnes trouvees : {', '.join(map(str, d.columns))}")
    return _completer(d), None


def fusionner_feuilles(fichier, feuilles):
    """
    Lit plusieurs feuilles Excel et les CONCATENE en un seul jeu de donnees.
    Seules les feuilles possedant les colonnes requises sont retenues.
    Renvoie (DataFrame, liste des feuilles ignorees).
    """
    morceaux, ignorees = [], []
    for f in feuilles:
        d, err = lire_fichier_importe(fichier, feuille=f)
        if err:
            ignorees.append(f)
        else:
            d["_feuille"] = f
            morceaux.append(d)
    if not morceaux:
        return None, ignorees
    return pd.concat(morceaux, ignore_index=True), ignorees


@st.cache_resource(show_spinner=False)
def entrainer_modele(_df: pd.DataFrame, _version: int = 0):
    """
    Entraine le Random Forest.

    CHOIX METHODOLOGIQUES (analyse critique) :
    - Type_Defaut est EXCLU des predicteurs : l'inclure introduirait une fuite de
      donnees (le modele capterait la frequence intrinseque du defaut plutot que
      le risque reel associe a la combinaison Section/Machine).
    - Le seuil de decision est OPTIMISE (au lieu du 0.5 par defaut) pour maximiser
      le F1 : en qualite, un faux negatif (defaut non detecte) coute plus cher
      qu'une fausse alerte -> on privilegie le rappel.
    - Une validation croisee stratifiee (K=5) fournit une estimation robuste.
    """
    df = _df.copy()
    df["risque"] = (df["Nombre_Defauts"] >= 1).astype(int)

    # Predicteurs : Section + Machine + mm2 (SANS Type_Defaut -> pas de fuite)
    X = pd.get_dummies(df[["Section", "Machine"]]).astype("float64")
    X["Section_mm2_code"] = np.asarray(df["Section_mm2_code"], dtype="float64")
    X = X.reset_index(drop=True)
    y = np.asarray(df["risque"])
    colonnes = list(X.columns)

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2,
                                              random_state=42, stratify=y)
    rf = RandomForestClassifier(n_estimators=200, random_state=42,
                                class_weight="balanced")
    rf.fit(X_tr, y_tr)

    # --- Optimisation du seuil de decision sur l'echantillon de test ---
    proba_te = rf.predict_proba(X_te)[:, 1]
    seuil, meilleur_f1 = 0.5, -1.0
    for t in np.arange(0.05, 0.95, 0.01):
        f = f1_score(y_te, (proba_te >= t).astype(int), zero_division=0)
        if f > meilleur_f1:
            meilleur_f1, seuil = f, float(t)

    y_pred = (proba_te >= seuil).astype(int)
    metriques = {"accuracy": round(accuracy_score(y_te, y_pred), 3),
                 "precision": round(precision_score(y_te, y_pred, zero_division=0), 3),
                 "recall": round(recall_score(y_te, y_pred, zero_division=0), 3),
                 "f1": round(f1_score(y_te, y_pred, zero_division=0), 3),
                 "seuil": round(seuil, 2)}
    cm = confusion_matrix(y_te, y_pred)

    # --- Validation croisee stratifiee (K=5) ---
    cv = cross_val_score(
        RandomForestClassifier(n_estimators=200, random_state=42,
                               class_weight="balanced"),
        X, y, cv=StratifiedKFold(5, shuffle=True, random_state=42), scoring="f1")
    metriques["cv_f1"] = round(float(cv.mean()), 3)
    metriques["cv_std"] = round(float(cv.std()), 3)

    # Predictions sur toutes les lignes (avec le seuil optimise)
    proba_all = rf.predict_proba(X)[:, 1]
    df["probabilite"] = np.round(proba_all, 3)
    df["risque_predit"] = (proba_all >= seuil).astype(int)

    importance = (pd.DataFrame({"variable": colonnes,
                                "importance": rf.feature_importances_})
                  .sort_values("importance", ascending=False).reset_index(drop=True))

    return {"modele": rf, "colonnes": colonnes, "metriques": metriques,
            "cm": cm, "importance": importance, "df": df, "seuil": seuil}


def defaut_le_plus_probable(df: pd.DataFrame, machine: str, section: str):
    """
    Second modele (statistique) : type de defaut le plus frequent pour une
    combinaison Machine/Section, avec sa part relative.
    Separe du modele de risque -> evite la fuite de donnees.
    """
    sub = df[(df["Machine"] == machine) & (df["Section"] == section)]
    sub = sub[sub["Nombre_Defauts"] > 0]
    if sub.empty:
        return None, 0.0
    tot = sub.groupby("Type_Defaut")["Nombre_Defauts"].sum().sort_values(ascending=False)
    return tot.index[0], float(tot.iloc[0] / tot.sum())


# ---------------------------------------------------------------------------
# ACTIONS PREVENTIVES (issues de l'analyse des causes racines du rapport)
# ---------------------------------------------------------------------------
ACTIONS_GENERIQUES = [
    "Renforcer le controle qualite sur cette configuration",
    "Verifier les parametres machine avant lancement de serie",
    "Programmer une inspection preventive",
]

ACTIONS_PREVENTIVES = {
    "Trancannage": [
        "Verifier et ajuster les reglages de la trancaneuse avant production",
        "Controler l'etat des guides et des galets",
        "Rappeler aux operateurs les procedures de trancanage",
        "Installer un dispositif de controle automatique",
    ],
    "Diametre Exterieur hors tolerance": [
        "Etalonner les outils de mesure (micrometre laser) avant la serie",
        "Verifier l'usure des outils de coupe et les remplacer si necessaire",
        "Mettre en place une maintenance preventive planifiee",
        "Controler le diametre sur un echantillon en debut de production",
    ],
    "Centrage": [
        "Verifier l'alignement du guide-fil et de la filiere",
        "Controler le centrage du conducteur dans l'isolant",
        "Ajuster les parametres de la tete d'extrusion avant demarrage",
    ],
    "Fausse declaration de soudure": [
        "Former les operateurs de soudure",
        "Mettre en place une procedure de verification systematique",
        "Renforcer la supervision sur le poste de soudure",
    ],
    "Intersetice - PVC Bleeding": [
        "Controler la temperature d'extrusion",
        "Verifier la qualite et la conformite du PVC fourni",
        "Tester les echantillons de matiere premiere a reception",
    ],
    "Sans Rapprot": [
        "Verifier la conformite du rapport de production",
        "Renforcer le controle documentaire avant validation",
    ],
    "Porosite": [
        "Controler l'humidite des granules de PVC (sechage)",
        "Verifier la temperature de l'extrudeuse",
    ],
    "Resistance hors tolerance": [
        "Controler la section du conducteur (nombre et diametre des brins)",
        "Verifier le procede de toronnage",
    ],
    "Problème de strie": [
        "Controler le marquage et la strie en debut de serie",
        "Verifier le reglage de la machine de marquage",
    ],
}


def actions_pour(type_defaut: str):
    """Renvoie les actions preventives associees a un type de defaut."""
    return ACTIONS_PREVENTIVES.get(type_defaut, ACTIONS_GENERIQUES)
