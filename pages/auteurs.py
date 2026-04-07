import dash
from dash import html, dcc, Input, Output, callback, dash_table
from src.db import query
import pandas as pd

dash.register_page(__name__, path="/auteurs")

TITLE_FONT = "Cinzel, Georgia, serif"      
BODY_FONT = "Lora, Georgia, serif" 
GOLD = "#D4AF37"
BERRY = "#4A1942"
MARRON = "rgba(141, 73, 37, 0.85)"

nationalites = query("SELECT DISTINCT nationalite FROM livres WHERE nationalite IS NOT NULL ORDER BY nationalite")
options_nationalites = [{"label": l, "value": l} for l in nationalites["nationalite"]]

options_emergence = [
    {"label": "Signal faible — très emergent", "value": "Signal faible — tres emergent"},
    {"label": "Signal moyen — emergent confirme", "value": "Signal moyen — emergent confirme"},
    {"label": "Signal fort — commence a percer", "value": "Signal fort — commence a percer"},
]

layout = html.Div(
    children=[
        html.H2(
            [
                html.Span("✨", style={"marginRight": "8px"}),
                "Retrouvez vos auteurs Emergents !",
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

        html.Div(
            children=[
                html.Span("Filtres:", style={"color": "white", "fontFamily": "Georgia, serif", "fontSize": "25px", "marginRight": "15px"}),
                dcc.Dropdown(id="filtre-nationalite", options=options_nationalites, placeholder="Nationalité", clearable=True, style={"width": "250px", "fontSize": "20px"}),
                dcc.Dropdown(id="filtre-emergence", options=options_emergence, placeholder="Niveau d'émergence", clearable=True, style={"width": "300px", "fontSize": "20px"}),
            ],
            style={
                "display": "flex", "alignItems": "center", "gap": "15px", "flexWrap": "wrap",
                "backgroundColor": MARRON, "padding": "15px 25px", "borderRadius": "10px",
                "marginBottom": "25px", "boxShadow": "0px 4px 10px rgba(0,0,0,0.3)"
            }
        ),

        html.Div(
            id="tableau-auteurs",
            style={
                "backgroundColor": "rgba(255, 248, 235, 0.9)",
                "borderRadius": "10px", "padding": "20px",
                "boxShadow": "0px 4px 12px rgba(0,0,0,0.2)",
                "marginBottom": "25px", "backdropFilter": "blur(4px)",
            }
        ),

        html.Div(
            children=[
                html.Button("Exporter CSV", id="btn-export", n_clicks=0, style={
                    "backgroundColor": MARRON, "color": "white", "border": "none",
                    "padding": "10px 20px", "borderRadius": "8px", "cursor": "pointer",
                    "fontSize": "16px", "fontFamily": "Georgia, serif",
                }),
                dcc.Download(id="download-csv")
            ],
            style={"textAlign": "center", "marginBottom": "30px"}
        )
    ],
    style={"padding": "40px 30px", "minHeight": "100vh"}
)


def get_df(nationalite, emergence):
    sql = """
        SELECT 
            l.auteurs, l.nationalite, l.langue,
            MAX(l.date) as dernier_livre,
            COUNT(*) as nb_livres,
            ROUND(AVG(l.note)::numeric, 2) as note_moyenne,
            SUM(l.nb_avis) as total_avis,
            ROUND((AVG(l.note) * LOG(SUM(l.nb_avis) + 1) / COUNT(*))::numeric, 2) as score_emergence,
            CASE WHEN l.nationalite IS NOT NULL THEN 'Reference Wikidata' ELSE 'Non reference Wikidata' END as statut_wikidata,
            CASE
                WHEN SUM(l.nb_avis) < 100 THEN 'Signal faible — tres emergent'
                WHEN SUM(l.nb_avis) BETWEEN 100 AND 300 THEN 'Signal moyen — emergent confirme'
                ELSE 'Signal fort — commence a percer'
            END as niveau_emergence
        FROM livres l
        WHERE l.note IS NOT NULL AND l.date >= '2023'
        GROUP BY l.auteurs, l.nationalite, l.langue
        HAVING COUNT(*) <= 2 AND SUM(l.nb_avis) BETWEEN 30 AND 300 AND AVG(l.note) >= 4.2
        ORDER BY score_emergence DESC
        LIMIT 50
    """
    df = query(sql)
    if nationalite:
        df = df[df["nationalite"] == nationalite]
    if emergence:
        df = df[df["niveau_emergence"] == emergence]
    return df


@callback(
    Output("tableau-auteurs", "children"),
    Input("filtre-nationalite", "value"),
    Input("filtre-emergence", "value")
)
def afficher_auteurs(nationalite, emergence):
    df = get_df(nationalite, emergence)
    return dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[
            {"name": "Auteur", "id": "auteurs"},
            {"name": "Nationalité", "id": "nationalite"},
            {"name": "Dernier livre", "id": "dernier_livre"},
            {"name": "Nb livres", "id": "nb_livres"},
            {"name": "Note moy.", "id": "note_moyenne"},
            {"name": "Total avis", "id": "total_avis"},
            {"name": "Score", "id": "score_emergence"},
            {"name": "Statut Wikidata", "id": "statut_wikidata"},
            {"name": "Niveau émergence", "id": "niveau_emergence"},
        ],
        style_table={"overflowX": "auto", "width": "100%"},
        style_header={
            "backgroundColor": BERRY, "color": "white",
            "fontFamily": "Georgia, serif", "fontSize": "20px",
            "fontWeight": "bold", "textAlign": "center", "padding": "12px"
        },
        style_cell={
            "backgroundColor": "rgba(255, 248, 235, 0.0)", "color": BERRY,
            "fontFamily": "Calibri, sans-serif", "fontSize": "19px",
            "textAlign": "center", "padding": "10px",
            "border": "1px solid rgba(196, 149, 106, 0.3)",
            "minWidth": "100px", "maxWidth": "200px", "whiteSpace": "normal",
        },
style_data_conditional=[
    {
        "if": {
            "filter_query": '{niveau_emergence} = "Signal faible — tres emergent"',
            "column_id": "niveau_emergence"
        },
        "backgroundColor": "#6B8F71",
        "color": "white",
        "fontWeight": "bold",
        "borderRadius": "8px",
    },
    {
        "if": {
            "filter_query": '{niveau_emergence} = "Signal moyen — emergent confirme"',
            "column_id": "niveau_emergence"
        },
        "backgroundColor": "#C4956A",
        "color": "white",
        "fontWeight": "bold",
        "borderRadius": "8px",
    },
    {
        "if": {
            "filter_query": '{niveau_emergence} = "Signal fort — commence a percer"',
            "column_id": "niveau_emergence"
        },
        "backgroundColor": "#A26769",
        "color": "white",
        "fontWeight": "bold",
        "borderRadius": "8px",
    },
],
        page_size=20,
        sort_action="native",
    )


@callback(
    Output("download-csv", "data"),
    Input("btn-export", "n_clicks"),
    Input("filtre-nationalite", "value"),
    Input("filtre-emergence", "value"),
    prevent_initial_call=True
)
def exporter_csv(n_clicks, nationalite, emergence):
    df = get_df(nationalite, emergence)
    return dcc.send_data_frame(df.to_csv, "auteurs_emergents.csv", index=False)