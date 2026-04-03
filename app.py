import dash
from dash import Dash, html,dcc
from dotenv import load_dotenv
import os

load_dotenv()


DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
app = Dash(__name__, use_pages=True)
html.Link(
    rel="stylesheet",
    href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Lora:ital,wght@0,400;0,600;1,400&display=swap"
),
app.layout = html.Div(
    style={
        "backgroundImage": "url('/assets/background_biblio.png')",
        "backgroundSize": "cover",
        "backgroundPosition": "center",
        "backgroundAttachment": "fixed",
        "minHeight": "100vh",
        "display": "flex",
        "overflowY":"auto"
    },
    children=[

        html.Div(
            style={
                "width": "250px",
                "backgroundColor": "rgba(141, 73, 37, 0.9)",
                "color": "white",
                "padding": "20px",
                "boxShadow": "4px 0px 10px rgba(0,0,0,0.3)"
            },
            children=[
                html.H2("L'Oracle des Plumes", style={"color": "#ecc400", "font-size": "30px"}),
                html.Hr(style={"borderColor": "#ecc400"}),

                dcc.Link("Accueil", href="/", style={"display": "block", "color": "white", "marginBottom": "10px", "textDecoration": "none", "font-size": "22px"}),
                dcc.Link("Catalogue", href="/catalogue", style={"display": "block", "color": "white", "marginBottom": "10px", "textDecoration": "none", "font-size": "22px"}),
                dcc.Link("Auteurs", href="/auteurs", style={"display": "block", "color": "white", "marginBottom": "10px", "textDecoration": "none", "font-size": "22px"}),
                dcc.Link("Guide d’utilisation", href="/guide", style={"display": "block", "color": "white", "marginBottom": "10px", "textDecoration": "none", "font-size": "22px"}),
            ]
        ),

        html.Div(
            dash.page_container,
            style={"flex": "1"}
        )
    ]
)

if __name__ == "__main__":
    app.run(debug=True)