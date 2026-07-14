# Service Qualite Intelligent — Systeme d'aide a la decision (P3S)
SEWS CABIND MAROC — Projet de Fin d'Etudes

## Lancer (dans le dossier contenant app.py)
    pip install -r requirements.txt
    streamlit run app.py

## Connexion (DEMONSTRATION)
    admin / p3s2024
Authentification de demonstration : mot de passe en clair dans le code.
Ne constitue PAS une securite reelle — a preciser dans le rapport.

## Structure
    app.py                  application principale
    utils/theme.py          charte graphique SEWS + composants UI
    utils/data.py           chargement, modele Random Forest, actions preventives
    data/                   data_clean.csv, kpi_mensuel.csv
    assets/logo.png         logo SEWS (fond transparent)
    .streamlit/config.toml  theme

## Pages
    Dashboard            6 KPI premium + graphiques + synthese qualite
    Analyse              Pareto, evolution mensuelle, 2 heatmaps
    Prediction IA        metriques, matrice de confusion, importance des variables
    Aide a la decision   jauge de risque + ACTIONS PREVENTIVES
    Alertes              etat des machines (Critique / Moyen / Faible)
    Rapports             export CSV
    A propos             presentation et limites

## Mise a jour des donnees
- Bouton "Actualiser les donnees" : vide le cache, recharge data/data_clean.csv,
  recalcule les KPI, reentraine le modele, rafraichit les graphiques.
- Import de fichier (.xlsx / .csv) : colonnes requises
  Section, Machine, Type_Defaut, Nombre_Defauts
  -> le modele est reentraine automatiquement sur les nouvelles donnees.

## Limites (a citer dans le rapport)
Jeu de donnees limite et desequilibre. Le modele est une PREUVE DE CONCEPT
demontrant la faisabilite, non un outil industriel pret a deployer.

## CORRECTIONS METHODOLOGIQUES (analyse critique)

1. FUITE DE DONNEES CORRIGEE
   Type_Defaut a ete RETIRE des predicteurs. L'inclure faisait capter au modele la
   frequence intrinseque de chaque type de defaut plutot que le risque reel de la
   combinaison Section/Machine.
   Predicteurs retenus : Section, Machine, capacite (mm2).
   -> Un modele statistique SEPARE (defaut_le_plus_probable) predit le type de
      defaut le plus probable, sans contaminer le modele de risque.

2. SEUIL DE DECISION OPTIMISE
   Le seuil n'est plus 0.5 par defaut mais optimise (0.45) pour maximiser le F1.
   En qualite, un faux negatif (defaut non detecte) coute plus cher qu'une fausse
   alerte -> on privilegie le RAPPEL.
   Resultat : recall passe de 0.44 a 0.78.

3. VALIDATION CROISEE STRATIFIEE (K=5)
   Ajoutee pour une estimation robuste : F1 = 0.418 (+/- 0.050).

IMPACT ASSUME : le F1 baisse (0.562 -> 0.478) car le modele ne peut plus "tricher".
C'est le prix de la rigueur methodologique. Le recall, metrique la plus utile en
qualite, s'ameliore fortement.

PISTE NON IMPLEMENTEE (a citer comme perspective) : classification a 4 niveaux
(Aucun/Faible/Moyen/Eleve) au lieu du binaire, pour une priorisation plus fine.
