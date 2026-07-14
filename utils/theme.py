"""theme.py — Charte graphique SEWS, CSS premium et composants d'interface."""
import streamlit as st

# ---- Couleurs SEWS (pas de pastel) ----
BLEU = "#0057B8"           # bleu SEWS
BLEU_FONCE = "#003A7D"
BLEU_NUIT = "#002B5C"      # sidebar
BLEU_CLAIR = "#2E8BE0"
BLANC = "#FFFFFF"
GRIS_BG = "#F2F5F9"
GRIS = "#5C6B7A"
GRIS_CLAIR = "#8795A3"
ENCRE = "#14243A"
VERT = "#00A65A"
ORANGE = "#F08C00"
ROUGE = "#D32F2F"
PALETTE = [BLEU, BLEU_CLAIR, "#4FA3E8", BLEU_FONCE, "#7FBEF0", "#1E6FC4"]

RAYON = "18px"             # rayon unique pour toutes les bordures
OMBRE = "0 4px 16px rgba(20,36,58,.08)"
OMBRE_HOVER = "0 10px 28px rgba(20,36,58,.16)"


def injecter_css():
    """Style SaaS industriel : sidebar masquee, navbar fixe, pleine largeur."""
    st.markdown(f"""
    <style>
    @import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{ font-family:'Inter', sans-serif; }}
    .stApp {{ background:{GRIS_BG}; }}
    #MainMenu, footer {{ visibility:hidden; }}

    /* Sidebar Streamlit COMPLETEMENT masquee */
    section[data-testid="stSidebar"] {{ display:none !important; }}
    div[data-testid="stSidebarCollapsedControl"] {{ display:none !important; }}
    header[data-testid="stHeader"] {{ display:none !important; }}

    /* Pleine largeur */
    .block-container {{ padding:0.6rem 2.4rem 1.4rem !important; max-width:100% !important; }}

    h1,h2,h3,h4 {{ color:{ENCRE}; font-weight:700; letter-spacing:-.2px; }}

    /* ---------- NAVBAR FIXE ---------- */
    .navbar {{ position:sticky; top:0; z-index:998;
               background:{BLEU_NUIT}; margin:0 -2.4rem;
               padding:0 30px; display:flex; align-items:center;
               box-shadow:0 2px 14px rgba(0,43,92,.22); }}
    .navbar .marque {{ display:flex; align-items:center; gap:11px; padding:14px 0;
                       color:#FFFFFF; font-weight:800; font-size:14.5px;
                       letter-spacing:.5px; line-height:1.2; white-space:nowrap; }}
    .navbar .marque .sous {{ font-weight:600; font-size:11px; color:#8FB4DA; }}
    .navbar .logo-nav {{ padding:10px 0; margin:4px 0;
                         display:flex; align-items:center; }}
    .navbar .logo-nav img {{ height:46px; display:block; }}

    /* Onglets = menu horizontal dans la navbar */
    .stTabs [data-baseweb="tab-list"] {{
        position:sticky; top:58px; z-index:997;
        background:{BLEU_NUIT}; gap:2px; padding:0 30px;
        margin:0 -2.4rem 0; border-bottom:none;
        box-shadow:0 2px 14px rgba(0,43,92,.18); }}
    .stTabs [data-baseweb="tab"] {{
        color:#A9C4E2; font-weight:600; font-size:14px;
        padding:13px 20px; background:transparent;
        border-bottom:3px solid transparent; transition:color .15s ease; }}
    .stTabs [data-baseweb="tab"]:hover {{ color:#FFFFFF; }}
    .stTabs [aria-selected="true"] {{
        color:#FFFFFF !important;
        background:{BLEU} !important;
        border-radius:10px 10px 0 0;
        border-bottom:3px solid {BLEU_CLAIR} !important;
        font-weight:700 !important; }}
    .stTabs [aria-selected="true"] p {{ color:#FFFFFF !important; font-weight:700 !important; }}
    .stTabs [data-baseweb="tab"] p {{ color:inherit !important; font-size:14px; margin:0; }}
    .stTabs [data-baseweb="tab-highlight"] {{ display:none; }}
    .stTabs [data-baseweb="tab-panel"] {{ padding-top:26px; }}

    /* ---------- ZONE BLEUE (bandeau KPI) ---------- */
    .zone-bleue {{ background:linear-gradient(120deg,{BLEU_NUIT} 0%,{BLEU_FONCE} 100%);
                   margin:-26px -2.4rem 28px; padding:24px 30px 30px; }}
    .zone-bleue .titre {{ color:#FFFFFF; font-size:21px; font-weight:700;
                          margin-bottom:16px; }}
    .bandeau2 {{ background:rgba(255,255,255,.07); border-radius:16px;
                 padding:18px 8px; display:flex; align-items:stretch;
                 border:1px solid rgba(255,255,255,.10); }}
    .bandeau2 .item {{ flex:1; padding:4px 22px; display:flex; align-items:center;
                       gap:15px; border-right:1px solid rgba(255,255,255,.14); }}
    .bandeau2 .item:last-child {{ border-right:none; }}
    .bandeau2 .ic {{ width:48px; height:48px; border-radius:13px; flex-shrink:0;
                     background:rgba(255,255,255,.13); color:#FFFFFF;
                     display:flex; align-items:center; justify-content:center;
                     font-size:20px; }}
    .bandeau2 .lb {{ font-size:12.5px; color:#BDD5EE; font-weight:500; }}
    .bandeau2 .vl {{ font-size:25px; font-weight:800; color:#FFFFFF; line-height:1.25;
                     white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
    .bandeau2 .vl.txt {{ font-size:19px; }}

    /* ---------- CARTES KPI ---------- */
    .kpi {{ background:{BLANC}; border-radius:{RAYON}; padding:16px 18px 14px;
            box-shadow:{OMBRE}; border:1px solid #E7EDF4; height:126px;
            position:relative; overflow:hidden;
            display:flex; flex-direction:column; justify-content:center;
            transition:transform .18s ease, box-shadow .18s ease; }}
    .kpi:hover {{ transform:translateY(-4px); box-shadow:{OMBRE_HOVER}; }}
    .kpi .bar {{ position:absolute; top:0; left:0; width:100%; height:4px; }}
    .kpi .haut {{ display:flex; align-items:center; gap:11px; }}
    .kpi .cercle {{ width:36px; height:36px; border-radius:50%; flex-shrink:0;
                    display:flex; align-items:center; justify-content:center;
                    font-size:16px; }}
    .kpi .val {{ font-size:27px; font-weight:800; color:{ENCRE}; line-height:1.15;
                 white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
    .kpi .val.txt {{ font-size:19px; }}
    .kpi .lib {{ font-size:11px; color:{GRIS_CLAIR}; font-weight:600;
                 text-transform:uppercase; letter-spacing:.5px; margin-top:3px; }}
    .kpi .sec {{ font-size:11.5px; color:{GRIS}; margin-top:7px; }}

    /* ---------- CARTE METRIQUE IA ---------- */
    .kpi-m {{ background:{BLANC}; border-radius:{RAYON}; padding:18px 20px 16px;
              box-shadow:{OMBRE}; border:1px solid #E7EDF4; height:172px;
              position:relative; overflow:hidden;
              transition:transform .18s ease, box-shadow .18s ease; }}
    .kpi-m:hover {{ transform:translateY(-4px); box-shadow:{OMBRE_HOVER}; }}
    .kpi-m .bar {{ position:absolute; top:0; left:0; width:100%; height:4px; }}
    .kpi-m .haut {{ display:flex; align-items:center; gap:12px; }}
    .kpi-m .cercle {{ width:38px; height:38px; border-radius:50%; flex-shrink:0;
                      display:flex; align-items:center; justify-content:center;
                      font-size:17px; }}
    .kpi-m .vl {{ font-size:30px; font-weight:800; color:{ENCRE}; line-height:1; }}
    .kpi-m .lib {{ font-size:13px; color:{ENCRE}; font-weight:700; margin-top:12px; }}
    .kpi-m .desc {{ font-size:11.5px; color:{GRIS}; margin-top:5px; line-height:1.45; }}

    /* ---------- CARTES ---------- */
    .card {{ background:{BLANC}; border-radius:{RAYON}; padding:24px 26px;
             box-shadow:{OMBRE}; border:1px solid #E7EDF4; margin-bottom:22px;
             transition:box-shadow .18s ease; }}
    .card:hover {{ box-shadow:{OMBRE_HOVER}; }}
    .card h4 {{ margin:0 0 14px; font-size:16px; }}

    .encadre {{ background:#F4F8FC; border-radius:14px; padding:18px 20px; }}
    .encadre .gros {{ font-size:30px; font-weight:800; color:{ENCRE}; }}
    .encadre .p {{ font-size:12.5px; color:{GRIS}; }}

    .badge {{ display:inline-block; padding:5px 15px; border-radius:20px;
              color:#FFFFFF; font-size:12px; font-weight:600; }}
    .puce {{ display:inline-block; padding:3px 12px; border-radius:8px;
             font-size:11.5px; font-weight:700; color:#FFFFFF; }}

    /* Conteneurs Streamlit stylises en cartes (remplace les div manuels) */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background:{BLANC}; border-radius:{RAYON};
        box-shadow:{OMBRE}; border:1px solid #E7EDF4; }}

    /* Boutons */
    .stButton > button {{ border-radius:12px; font-weight:600; }}

    /* ---------- PAGE DE CONNEXION ---------- */
    /* IMPORTANT : on ne touche PAS aux input eux-memes (sinon le bouton oeil du
       champ mot de passe se casse). On style uniquement le conteneur. */

    /* Colonnes de meme hauteur, alignement vertical centre (Flexbox) */
    div[data-testid="stHorizontalBlock"]:has(.mk-login) {{
        min-height:640px; align-items:stretch; gap:0 !important; }}

    /* Panneau sombre (gauche) */
    div[data-testid="stHorizontalBlock"]:has(.mk-login)
        > div[data-testid="stColumn"]:first-child {{
        background:linear-gradient(160deg,{BLEU_NUIT} 0%,#04213F 55%,#01152A 100%);
        border-radius:18px 0 0 18px; padding:44px 42px !important;
        display:flex; flex-direction:column; justify-content:center; }}

    /* Panneau clair (droite) */
    div[data-testid="stHorizontalBlock"]:has(.mk-login)
        > div[data-testid="stColumn"]:last-child {{
        background:#FFFFFF; border-radius:0 18px 18px 0;
        padding:44px 52px !important;
        display:flex; flex-direction:column; justify-content:center;
        box-shadow:0 10px 34px rgba(20,36,58,.10); }}

    /* Textes du panneau sombre */
    .lg-titre {{ color:#FFFFFF; font-size:26px; font-weight:800; line-height:1.28;
                 margin:22px 0 0; }}
    .lg-trait {{ height:4px; width:60px; background:{BLEU_CLAIR};
                 border-radius:3px; margin:14px 0 16px; }}
    .lg-sous {{ color:#9FBEDF; font-size:13.5px; line-height:1.6; margin-bottom:26px; }}
    .lg-arg {{ display:flex; align-items:center; gap:13px; margin-bottom:14px; }}
    .lg-arg .ic {{ width:40px; height:40px; border-radius:11px; flex-shrink:0;
                   background:rgba(46,139,224,.16); color:{BLEU_CLAIR};
                   display:flex; align-items:center; justify-content:center;
                   font-size:17px; }}
    .lg-arg .t {{ color:#FFFFFF; font-size:13.5px; font-weight:700; }}
    .lg-arg .d {{ color:#8FAECF; font-size:11.5px; }}

    /* En-tete du formulaire */
    .lg-avatar {{ width:58px; height:58px; border-radius:50%; margin:0 auto;
                  background:#E8F1FB; color:{BLEU};
                  display:flex; align-items:center; justify-content:center;
                  font-size:25px; }}
    .lg-bv {{ text-align:center; font-size:25px; font-weight:800;
              color:{BLEU_NUIT}; margin-top:12px; }}
    .lg-bv-s {{ text-align:center; font-size:13px; color:{GRIS}; margin:3px 0 4px; }}
    .lg-pied {{ text-align:center; font-size:11.5px; color:{GRIS_CLAIR};
                margin-top:14px; }}

    /* Formulaire : uniquement le conteneur et le bouton (PAS les input) */
    div[data-testid="stHorizontalBlock"]:has(.mk-login)
        [data-testid="stForm"] {{
        border:none !important; padding:0 !important;
        background:transparent !important; }}
    div[data-testid="stHorizontalBlock"]:has(.mk-login)
        [data-testid="stForm"] label p {{
        color:{ENCRE} !important; font-size:12.5px !important;
        font-weight:700 !important; }}
    div[data-testid="stHorizontalBlock"]:has(.mk-login)
        [data-testid="stForm"] button {{
        background:linear-gradient(120deg,{BLEU},{BLEU_FONCE}) !important;
        color:#FFFFFF !important; border:none !important;
        border-radius:12px !important; padding:11px 0 !important;
        font-weight:700 !important; font-size:15px !important;
        box-shadow:0 6px 18px rgba(0,87,184,.28) !important; }}
    div[data-testid="stHorizontalBlock"]:has(.mk-login)
        [data-testid="stForm"] button:hover {{ filter:brightness(1.08); }}

    /* Responsive */
    @media (max-width:1200px) {{
        .bandeau2 {{ flex-wrap:wrap; }}
        .bandeau2 .item {{ flex:1 1 45%; border-right:none;
                           border-bottom:1px solid rgba(255,255,255,.12);
                           padding:12px 16px; }}
    }}
    @media (max-width:820px) {{
        .bandeau2 .item {{ flex:1 1 100%; }}
        .block-container {{ padding:0 1rem 2rem !important; }}
        .navbar, .zone-bleue, .stTabs [data-baseweb="tab-list"] {{ margin-left:-1rem;
                                                                   margin-right:-1rem; }}
    }}
    </style>
    """, unsafe_allow_html=True)


def carte_kpi(col, libelle, valeur, icone, couleur, secondaire="", texte=False):
    """
    Carte KPI industrielle : barre coloree en haut, icone en cercle discret,
    valeur, titre, information secondaire. Hierarchie : icone -> valeur -> titre -> info.
    """
    classe = "val txt" if texte else "val"
    info = f"<div class='sec'>{secondaire}</div>" if secondaire else ""
    col.markdown(f"""<div class="kpi">
        <div class="bar" style="background:{couleur};"></div>
        <div class="haut">
            <div class="cercle" style="background:{couleur}1A; color:{couleur};">
                <i class="bi bi-{icone}"></i></div>
            <div>
                <div class="{classe}">{valeur}</div>
                <div class="lib">{libelle}</div>
            </div>
        </div>
        {info}
    </div>""", unsafe_allow_html=True)


def bandeau_kpi(items):
    """
    Bandeau KPI horizontal sur fond bleu (style logiciel industriel).
    items : liste de dicts {libelle, valeur, icone, secondaire, texte}
    """
    html = "<div class='bandeau'>"
    for it in items:
        cls = "vl txt" if it.get("texte") else "vl"
        sec = f"<div class='sc'>{it['secondaire']}</div>" if it.get("secondaire") else ""
        html += (f"<div class='item'>"
                 f"<div class='ic'><i class='bi bi-{it['icone']}'></i></div>"
                 f"<div><div class='lb'>{it['libelle']}</div>"
                 f"<div class='{cls}'>{it['valeur']}</div>{sec}</div></div>")
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _logo_base64():
    """Encode le logo en base64 pour l'inserer dans la navbar HTML."""
    import base64, os
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chemin = os.path.join(base, "assets", "logo_nav.png")
    if not os.path.exists(chemin):
        chemin = os.path.join(base, "assets", "logo.png")
    if not os.path.exists(chemin):
        return None
    with open(chemin, "rb") as f:
        return base64.b64encode(f.read()).decode()


def navbar():
    """Barre de navigation fixe avec le logo SEWS original."""
    b64 = _logo_base64()
    if b64:
        contenu = (f"<div class='logo-nav'>"
                   f"<img src='data:image/png;base64,{b64}'/></div>")
    else:
        contenu = ("<div class='marque'>SEWS CABIND"
                   "<br><span class='sous'>MAROC S.A.S.</span></div>")
    st.markdown(f"<div class='navbar'>{contenu}</div>", unsafe_allow_html=True)


def zone_bleue(titre, items):
    """Zone bleue : titre + bandeau KPI horizontal (prolonge la navbar)."""
    html = f"<div class='zone-bleue'><div class='titre'>{titre}</div><div class='bandeau2'>"
    for it in items:
        cls = "vl txt" if it.get("texte") else "vl"
        html += (f"<div class='item'>"
                 f"<div class='ic'><i class='bi bi-{it['icone']}'></i></div>"
                 f"<div><div class='lb'>{it['libelle']}</div>"
                 f"<div class='{cls}'>{it['valeur']}</div></div></div>")
    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)


def jauge_anneau(valeur, couleur, libelle=""):
    """Anneau de progression (style Network Availability)."""
    import plotly.graph_objects as go
    fig = go.Figure(go.Pie(
        values=[valeur, 100 - valeur], hole=0.72, sort=False,
        marker=dict(colors=[couleur, "#E6ECF2"]),
        textinfo="none", hoverinfo="skip"))
    fig.update_layout(
        height=170, margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(text=f"<b>{valeur}%</b>", x=0.5, y=0.5,
                          font=dict(size=22, color=ENCRE), showarrow=False)])
    return fig


def kpi_metrique(col, libelle, valeur, icone, couleur, description):
    """Carte metrique IA : icone, valeur, libelle, description pedagogique."""
    col.markdown(f"""<div class="kpi-m">
        <div class="bar" style="background:{couleur};"></div>
        <div class="haut">
            <div class="cercle" style="background:{couleur}1A; color:{couleur};">
                <i class="bi bi-{icone}"></i></div>
            <div class="vl">{valeur}</div>
        </div>
        <div class="lib">{libelle}</div>
        <div class="desc">{description}</div>
    </div>""", unsafe_allow_html=True)


def bloc(titre, contenu_html, couleur=None):
    """Carte auto-fermante : evite les balises </div> orphelines."""
    barre = f"<div class='bar' style='background:{couleur};'></div>" if couleur else ""
    st.markdown(f"<div class='card' style='position:relative; overflow:hidden;'>{barre}"
                f"<h4>{titre}</h4>{contenu_html}</div>", unsafe_allow_html=True)


def style_fig(fig, hauteur=340):
    """Style commun des figures Plotly."""
    fig.update_layout(height=hauteur, template="plotly_white",
                      font=dict(color=ENCRE, size=12),
                      margin=dict(l=10, r=10, t=40, b=10),
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)")
    return fig
