import dash
from dash import html

dash.register_page(__name__, path="/")

layout = html.Div(
    style={
        "display": "flex",
        "flexDirection": "column",
        "justifyContent": "flex-start",
        "alignItems": "center",
        "paddingTop": "50px"
    },
    children=[

        html.H2(
            "Vue d'ensemble du catalogue",
            style={
                "color": "#5a3b2a",
                "marginBottom": "30px"
            }
        ),

        html.Div(
            style={
                "width": "900px",
                "display": "flex",
                "justifyContent": "space-between",
                "color": "#5a3b2a"
            },
            children=[

                html.Div(
                    style={
                        "width": "200px",
                        "backgroundColor": "rgba(255, 248, 235, 0.9)",
                        "padding": "20px",
                        "borderRadius": "10px",
                        "textAlign": "center",
                        "boxShadow": "0px 4px 10px rgba(0,0,0,0.2)"
                    },
                    children=[
                        html.H4("📚 Livres"),
                        html.H2("1395")
                    ]
                ),

                html.Div(
                    style={
                        "width": "200px",
                        "backgroundColor": "rgba(255, 248, 235, 0.9)",
                        "padding": "20px",
                        "borderRadius": "10px",
                        "textAlign": "center",
                        "boxShadow": "0px 4px 10px rgba(0,0,0,0.2)"
                    },
                    children=[
                        html.H4("✍️ Auteurs"),
                        html.H2("1132")
                    ]
                ),

                html.Div(
                    style={
                        "width": "200px",
                        "backgroundColor": "rgba(255, 248, 235, 0.9)",
                        "padding": "20px",
                        "borderRadius": "10px",
                        "textAlign": "center",
                        "boxShadow": "0px 4px 10px rgba(0,0,0,0.2)"
                    },
                    children=[
                        html.H4("🌍 Nationalités"),
                        html.H2("30")
                    ]
                ),

                html.Div(
                    style={
                        "width": "200px",
                        "backgroundColor": "rgba(255, 248, 235, 0.9)",
                        "padding": "20px",
                        "borderRadius": "10px",
                        "textAlign": "center",
                        "boxShadow": "0px 4px 10px rgba(0,0,0,0.2)"
                    },
                    children=[
                        html.H4("⭐ Note moyenne"),
                        html.H2("4.3")
                    ]
                ),
            ]
        )
    ]
)