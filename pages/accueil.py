import dash
from dash import html, dcc
import plotly.express as px
from src.db import query

dash.register_page(__name__, path="/")

# Requetes SQL
nb_livres = query("SELECT COUNT(*) as nb FROM livres")["nb"][0]
nb_auteurs = query("SELECT COUNT(DISTINCT auteurs) as nb FROM livres")["nb"][0]
nb_nationalites = query("SELECT COUNT(DISTINCT nationalite) as nb FROM livres WHERE nationalite IS NOT NULL")["nb"][0]
note_moyenne = query("SELECT ROUND(AVG(note)::numeric, 1) as nb FROM livres WHERE note IS NOT NULL")["nb"][0]

# Donnees graphiques
df_natio = query("""
    SELECT nationalite, COUNT(*) as nb_livres
    FROM livres
    WHERE nationalite IS NOT NULL
    GROUP BY nationalite
    ORDER BY nb_livres DESC
    LIMIT 10
""")

df_annee = query("""
    SELECT date, COUNT(*) as nb_livres
    FROM livres
    WHERE date BETWEEN 2023 AND 2026
    GROUP BY date
    ORDER BY date
""")

# Graphiques
fig_natio = px.bar(
    df_natio,
    x="nb_livres",
    y="nationalite",
    orientation="h",
    title="Top 10 nationalités",
    color_discrete_sequence=["#C4956A"],
    labels={"nb_livres": "Nombre de livres", "nationalite": "", "fontSize":"20px"}
)
fig_natio.update_layout(
    paper_bgcolor="rgba(255,248,235,0.85)",
    plot_bgcolor="rgba(255,248,235,0.0)",
    font=dict(family="Georgia, serif", color="#4A1942", size=16),
    title_font=dict(size=24),
    yaxis=dict(autorange="reversed", tickfont=dict(size=16)),
    xaxis=dict(tickfont=dict(size=16)),
    margin=dict(l=10, r=20, t=50, b=30)
)
fig_natio.update_traces(
    hoverlabel=dict(bgcolor="#D4AF37", font_color="white",font_size=18)
)

fig_annee = px.bar(
    df_annee,
    x="date",
    y="nb_livres",
    title="Livres par année",
    color_discrete_sequence=["#6D2E46"],
    labels={"nb_livres": "Nombre de livres", "date": "Année"}
)
fig_annee.update_layout(
    paper_bgcolor="rgba(255,248,235,0.85)",
    plot_bgcolor="rgba(255,248,235,0.0)",
    font=dict(family="Georgia, serif", color="#4A1942", size=18),
    title_font=dict(size=24),
    xaxis=dict(type="category",tickfont=dict(size=16)),
    yaxis=dict(tickfont=dict(size=16)),
    margin=dict(l=10, r=20, t=50, b=30)
)
fig_annee.update_traces(
    hoverlabel=dict(bgcolor="#D4AF37", font_color="white",font_size=18)
)

CARD_STYLE = {
    "backgroundColor": "rgba(255, 248, 235, 0.9)",
    "padding": "40px 20px",
    "borderRadius": "10px",
    "textAlign": "center",
    "boxShadow": "0px 8px 20px rgba(0,0,0,0.25), 0px 2px 4px rgba(0,0,0,0.15)",
    "border": "1px solid rgba(196, 149, 106, 0.5)",
    "flex": "1"
}

GRAPH_CONTAINER = {
    "flex": "1",
    "borderRadius": "10px",
    "overflow": "hidden",
    "boxShadow": "0px 4px 10px rgba(0,0,0,0.2)",
    "height": "40vh",  # Je réduis de 55vh à 40vh
}

BERRY = "#5a3b2a"

layout = html.Div(
    style={
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "center",
        "paddingTop": "50px",
        "minHeight": "100vh",
        "paddingBottom": "50px",
    },
    children=[

        html.H2([
            html.Span("✨", style={"marginLeft": "8px"}),
            "Vue d'ensemble du catalogue",
            html.Span("✨", style={"marginLeft": "8px"})],
            style={"color": BERRY, "marginBottom": "50px", "fontSize": "32px", "fontFamily": "Georgia, serif", "font-size":"45px"}),

        # KPIs
        html.Div(
            style={
                "width": "95%",
                "display": "flex",
                "justifyContent": "space-between",
                "gap": "20px",
                "color": BERRY
            },
            children=[
                html.Div(style=CARD_STYLE, children=[
                    html.H4("📚 Livres", style={"fontSize": "25px"}),
                    html.H2(str(nb_livres), style={"fontSize": "48px", "margin": "0"})
                ]),
                html.Div(style=CARD_STYLE, children=[
                    html.H4("✍️ Auteurs", style={"fontSize": "25px"}),
                    html.H2(str(nb_auteurs), style={"fontSize": "48px", "margin": "0"})
                ]),
                html.Div(style=CARD_STYLE, children=[
                    html.H4("🌍 Nationalités", style={"fontSize": "25px"}),
                    html.H2(str(nb_nationalites), style={"fontSize": "48px", "margin": "0"})
                ]),
                html.Div(style=CARD_STYLE, children=[
                    html.H4("⭐ Note moyenne", style={"fontSize": "25px"}),
                    html.H2(str(note_moyenne), style={"fontSize": "48px", "margin": "0"})
                ]),
            ]
        ),

        # Graphiques
        html.Div(
            style={
                "width": "95%",
                "display": "flex",
                "justifyContent": "space-between",
                "marginTop": "30px",
                "gap": "20px",
            },
            children=[
                html.Div(
                    dcc.Graph(figure=fig_natio, style={"height": "100%"}),
                    style=GRAPH_CONTAINER
                ),
                html.Div(
                    dcc.Graph(figure=fig_annee, style={"height": "100%"}),
                    style=GRAPH_CONTAINER
                ),
            ]
        )
    ]
)