import dash
from dash import html, dcc, Input, Output, callback
from src.db import query
import pandas as pd

dash.register_page(__name__, path="/catalogue")

BERRY = "#4A1942"
GOLD = "#C4956A"
MARRON = "rgba(141, 73, 37, 0.85)"

CARD_STYLE = {
    "backgroundColor": "rgba(255, 248, 235, 0.95)",
    "borderRadius": "10px",
    "padding": "10px",
    "boxShadow": "0px 4px 12px rgba(0,0,0,0.2)",
    "border": "1px solid rgba(196, 149, 106, 0.4)",
    "width": "210px",
    "flexGrow": "1",
    "flexBasis": "180px",
    "maxWidth": "210px",
    "textAlign": "center",
}

MAPPING_LANGUES = {
    "en": "Anglais", "eng": "Anglais", "fr": "Français", "fre": "Français",
    "ja": "Japonais", "it": "Italien", "es": "Espagnol", "spa": "Espagnol",
    "nl": "Néerlandais", "dut": "Néerlandais", "de": "Allemand", "ger": "Allemand",
    "pt": "Portugais", "por": "Portugais", "pt-BR": "Portugais (Brésil)",
    "ar": "Arabe", "ara": "Arabe", "tr": "Turc", "tur": "Turc", "sv": "Suédois"
}

PLACEHOLDER = "/assets/no_cover.png"

layout = html.Div(
    children=[
        html.H2(
            [
                html.Span("✨", style={"marginRight": "8px"}),
                "Explorer votre catalogue:",
                html.Span("✨", style={"marginLeft": "8px"})
            ],
            style={
                "color": BERRY,
                "fontFamily": "Georgia, serif",
                "marginBottom": "25px",
                "textAlign": "center",
                "fontSize": "45px"
            }
        ),

        # Je construis le bandeau de filtres
        html.Div(
            children=[
                html.Span("Filtres:", style={"color": "white", "fontFamily": "Georgia, serif", "fontSize": "25px", "marginRight": "15px"}),
                dcc.Dropdown(id="filtre-langue", options=[], placeholder="Langue", clearable=True, style={"width": "250px", "fontSize": "20px"}),
                dcc.Dropdown(id="filtre-annee", options=[], placeholder="Année", clearable=True, style={"width": "250px", "fontSize": "20px"}),
                html.Div(
                    children=[
                        html.Span("Note minimale", style={"color": "white", "fontSize": "20px", "marginRight": "10px", "fontFamily": "Georgia, serif"}),
                        html.Div(
                            children=[
                                dcc.Slider(
                                    id="filtre-note", min=0, max=5, step=0.5, value=0,
                                    marks={
                                        0: {"label": "0", "style": {"color": "white"}},
                                        1: {"label": "1⭐", "style": {"color": "white", "fontSize": "20px"}},
                                        2: {"label": "2⭐", "style": {"color": "white", "fontSize": "20px"}},
                                        3: {"label": "3⭐", "style": {"color": "white", "fontSize": "20px"}},
                                        4: {"label": "4⭐", "style": {"color": "white", "fontSize": "20px"}},
                                        5: {"label": "5⭐", "style": {"color": "white", "fontSize": "20px"}},
                                    }
                                )
                            ],
                            style={"flex": "1", "minWidth": "200px", "backgroundColor": "rgba(255,248,235,0.12)", "padding": "8px 12px", "borderRadius": "10px"}
                        )
                    ],
                    style={"display": "flex", "alignItems": "center", "gap": "12px", "flex": "1", "minWidth": "350px"}
                ),
            ],
            style={
                "display": "flex", "alignItems": "center", "gap": "15px", "flexWrap": "wrap",
                "backgroundColor": MARRON, "padding": "15px 25px", "borderRadius": "10px",
                "marginBottom": "25px", "boxShadow": "0px 4px 10px rgba(0,0,0,0.3)"
            }
        ),

        # Je construis la grille de livres
        html.Div(
            id="grille-livres",
            style={
                "display": "flex",
                "flexWrap": "wrap",
                "justifyContent": "space-between",
                "backgroundColor": "rgba(255,255,255,0.6)",
                "padding": "20px 25px",
                "borderRadius": "10px",
                "marginBottom": "15px",
                "backdropFilter": "blur(4px)",
                "gap": "20px",
            }
        ),

        # Je construis la pagination
        html.Div(
            children=[
                html.Button("◀ Précédent", id="btn-precedent", n_clicks=0, style={"backgroundColor": MARRON, "color": "white", "border": "none", "padding": "10px 20px", "borderRadius": "8px", "cursor": "pointer", "fontSize": "16px", "fontFamily": "Georgia, serif"}),
                html.Span(id="numero-page", style={"margin": "0 25px", "color": BERRY, "fontFamily": "Georgia, serif", "fontSize": "18px", "fontWeight": "bold"}),
                html.Button("Suivant ▶", id="btn-suivant", n_clicks=0, style={"backgroundColor": MARRON, "color": "white", "border": "none", "padding": "10px 20px", "borderRadius": "8px", "cursor": "pointer", "fontSize": "16px", "fontFamily": "Georgia, serif"}),
            ],
            style={"textAlign": "center", "marginTop": "20px", "marginBottom": "40px", "display": "flex", "justifyContent": "center", "alignItems": "center"}
        ),

        dcc.Store(id="page-courante", data=0)
    ],
    style={"padding": "40px 30px", "minHeight": "100vh"}
)


@callback(
    Output("filtre-langue", "options"),
    Output("filtre-annee", "options"),
    Input("filtre-langue", "id")
)
def charger_options(_):
    # Je charge les options dynamiquement depuis la base à chaque chargement
    langues = query("SELECT DISTINCT langue FROM livres WHERE langue IS NOT NULL ORDER BY langue")
    options_langues = [{"label": MAPPING_LANGUES.get(l, l), "value": l} for l in langues["langue"]]

    dates = query("SELECT DISTINCT date FROM livres WHERE date IS NOT NULL ORDER BY date")
    options_dates = [{"label": l, "value": l} for l in dates["date"]]

    return options_langues, options_dates


@callback(
    Output("page-courante", "data"),
    Input("btn-precedent", "n_clicks"),
    Input("btn-suivant", "n_clicks"),
    Input("filtre-langue", "value"),
    Input("filtre-annee", "value"),
    Input("filtre-note", "value"),
)
def changer_page(precedent, suivant, langue, annee, note):
    from dash import ctx
    triggered = ctx.triggered_id
    if triggered == "btn-suivant":
        return suivant
    elif triggered == "btn-precedent":
        return max(0, precedent - 1)
    return 0


@callback(
    Output("grille-livres", "children"),
    Output("numero-page", "children"),
    Input("filtre-langue", "value"),
    Input("filtre-annee", "value"),
    Input("filtre-note", "value"),
    Input("page-courante", "data")
)
def afficher_livres(langue, annee, note, page):
    sql = """
        SELECT titre, auteurs, nationalite, date, editeur, cover_url, note, nb_avis
        FROM livres
        WHERE 1=1
    """
    if langue:
        sql += f" AND langue = '{langue}'"
    if annee:
        sql += f" AND date = '{annee}'"
    if note:
        sql += f" AND note >= {note}"

    # Je limite à 20 livres par page
    sql += f" ORDER BY RANDOM() LIMIT 20 OFFSET {page * 20}"

    df = query(sql)
    cartes = []

    for _, row in df.iterrows():
        cover = row["cover_url"] if pd.notna(row["cover_url"]) else PLACEHOLDER

        carte = html.Div(
            className="carte",
            children=[
                html.Img(
                    src=cover,
                    style={
                        "width": "100%",
                        "height": "220px",
                        "objectFit": "contain",
                        "borderRadius": "8px"
                    }
                ),
                html.Div(
                    className="tooltip",
                    children=[
                        html.P(row["titre"] or "Titre inconnu", className="tooltip-titre"),
                        html.P(row["auteurs"] or "Auteur inconnu", className="tooltip-auteur"),
                        html.P(f"⭐ {round(row['note'], 1)}" if pd.notna(row["note"]) else "Pas de note", className="tooltip-info"),
                        html.P(f"🌍 {row['nationalite']}" if pd.notna(row["nationalite"]) else "", className="tooltip-info"),
                        html.P(f"📅 {row['date']}" if pd.notna(row["date"]) else "", className="tooltip-info"),
                        html.P(f"💬 {int(row['nb_avis'])} avis" if pd.notna(row["nb_avis"]) else "", className="tooltip-info"),
                    ]
                )
            ],
            style=CARD_STYLE
        )
        cartes.append(carte)

    return cartes, f"Page {page + 1}"