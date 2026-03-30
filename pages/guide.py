import dash
from dash import html

dash.register_page(__name__, path="/guide")

TITLE_FONT = "Cinzel, Georgia, serif"      
BODY_FONT = "Lora, Georgia, serif" 

CARD_STYLE = {
    "backgroundColor": "rgba(255,255,255,0.6)",
    "padding": "20px 25px",
    "borderRadius": "10px",
    "marginBottom": "15px",
    "backdropFilter": "blur(4px)",
}

GOLD = "#D4AF37"
BERRY = "#4A1942"

layout = html.Div(
    children=[

        html.H2([
            html.Span("✨", style={"marginRight": "8px"}),
            "Comment utiliser l'Oracle des Plumes ?",
            html.Span("✨", style={"marginLeft": "8px"})
        ], style={
            "color": BERRY,
            "fontFamily": "Georgia, serif",
            "marginBottom": "25px"
        }),

        # Bloc 1
        html.Div([
            html.H3("✨ À quoi sert l'outil ?", style={"color": BERRY, "fontFamily": TITLE_FONT, "fontSize":"22px"}),
            html.P("Cet outil permet d'identifier des auteurs émergents à fort potentiel pour faciliter la sélection de nouveaux talents à éditer.")
        ], style=CARD_STYLE),

        # Bloc 2
        html.Div([
            html.H3("✨ Comment sont identifiés les auteurs émergents ?", style={"color": BERRY, "fontFamily": TITLE_FONT, "fontSize":"22px"}),
            html.P("Le score d'un auteur émergent est calculé à partir de plusieurs indicateurs combinés, afin d'évaluer son potentiel éditorial."),
            html.P("Il prend en compte :"),
            html.Ul([
                html.Li("la note moyenne des ouvrages"),
                html.Li("le nombre d'avis du public"),
                html.Li("le nombre de livres publiés (rareté)")
            ]),
            html.Div(
                "Score = AVG(note) × LOG(SUM(nb_avis) + 1) / COUNT(livres)",
                style={
                    "backgroundColor": "rgba(255, 248, 235, 0.9)",
                    "padding": "15px",
                    "borderRadius": "8px",
                    "fontWeight": "bold",
                    "color": "#5a3b2a",
                    "fontFamily": "Georgia, serif",
                    "marginTop": "10px",
                    "marginBottom": "15px"
                }
            ),
            html.P("Un score élevé signifie que l'auteur présente un fort potentiel, avec une bonne réception du public et un positionnement encore émergent."),
            html.P("Un nombre faible de livres indique que l'auteur est encore peu publié, ce qui renforce son caractère émergent."),
            html.P("Une note élevée traduit une réception positive des ouvrages auprès des lecteurs.")
        ], style=CARD_STYLE),

        # Bloc 3
        html.Div([
            html.H3("✨ Comment utiliser la page Auteurs ?", style={"color": BERRY, "fontFamily": TITLE_FONT, "fontSize":"22px"}),
            html.P("Utilisez les filtres en haut de la page pour affiner le classement selon la nationalité ou le niveau d'émergence. Chaque ligne représente un auteur à potentiel — vous pouvez exporter la sélection en CSV pour un suivi editorial.")
        ], style=CARD_STYLE),

        # Bloc 4
        html.Div([
            html.H3("✨ Limites à garder en tête :", style={"color": BERRY, "fontFamily": TITLE_FONT, "fontSize":"22px"}),
            html.Ul([
                html.Li("Biais anglophone — les APIs referencent majoritairement des contenus en anglais."),
                html.Li("69% des auteurs non enrichis par Wikidata — coherent avec leur caractere emergent."),
                html.Li("Dataset non exhaustif — echantillon des APIs disponibles sur la periode 2023-2025."),
                html.Li("Un auteur emergent peut deja etre sous contrat — ces données ne le reflètent pas.")
            ])
        ], style=CARD_STYLE),

    ],
    style={
        "maxWidth": "860px",
        "margin": "0 auto",
        "padding": "40px 30px",
        "fontFamily": BODY_FONT,
        "fontSize":"16px",
        "color": "#1E1E1E",
        "minHeight":"100vh",
    }
)
    
    