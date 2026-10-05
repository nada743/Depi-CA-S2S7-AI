# ============================================================
# FORD GOBIKE | ANALYTICS PLATFORM
# Supabase + Dash Dashboard
# ============================================================

import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psycopg2

from dotenv import load_dotenv
from dash import Dash, dcc, html, Input, Output, ctx


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ============================================================
# DATABASE CONNECTION
# ============================================================

try:

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )

    print("Connected to Supabase successfully!")

except Exception as e:

    print("Database connection failed:")
    print(e)

    raise


# ============================================================
# LOAD DATA FROM SUPABASE VIEW
# ============================================================

df = pd.read_sql_query(
    "SELECT * FROM vw_fordgobike_analysis;",
    conn
)

conn.close()

print(f"Loaded {len(df):,} rows from Supabase.")


# ============================================================
# DATA PREPARATION
# ============================================================

# Convert datetime columns
df["start_time"] = pd.to_datetime(
    df["start_time"],
    errors="coerce",
    utc=True
).dt.tz_localize(None)

df["end_time"] = pd.to_datetime(
    df["end_time"],
    errors="coerce",
    utc=True
).dt.tz_localize(None)


# ============================================================
# FEBRUARY 2019 ONLY
# ============================================================

MIN_DATE = pd.Timestamp("2019-02-01")
MAX_DATE = pd.Timestamp("2019-02-28")

df = df[
    (df["start_time"] >= MIN_DATE)
    &
    (df["start_time"] < MAX_DATE + pd.Timedelta(days=1))
].copy()


# ============================================================
# NUMERIC CLEANING
# ============================================================

numeric_columns = [
    "duration_sec",
    "duration_min",
    "duration_hour",
    "member_age",
    "start_station_latitude",
    "start_station_longitude",
    "end_station_latitude",
    "end_station_longitude",
]

for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


# ============================================================
# AGE CLEANING
# ============================================================

df["member_age"] = pd.to_numeric(
    df["member_age"],
    errors="coerce"
)

df.loc[
    (df["member_age"] < 18) |
    (df["member_age"] > 100),
    "member_age"
] = np.nan


# ============================================================
# AGE GROUP
# ============================================================

def create_age_group(age):

    if pd.isna(age):
        return "Unknown"

    if 18 <= age <= 24:
        return "18-24"

    elif 25 <= age <= 34:
        return "25-34"

    elif 35 <= age <= 44:
        return "35-44"

    elif 45 <= age <= 54:
        return "45-54"

    elif 55 <= age <= 64:
        return "55-64"

    elif age >= 65:
        return "65+"

    return "Unknown"


df["age_group"] = df["member_age"].apply(create_age_group)


# ============================================================
# GENDER CLEANING
# ============================================================

df["member_gender"] = (
    df["member_gender"]
    .fillna("Other")
    .astype(str)
    .str.strip()
)

df["member_gender"] = df["member_gender"].replace(
    {
        "": "Other",
        "nan": "Other",
        "None": "Other",
    }
)


# ============================================================
# USER TYPE
# ============================================================

df["user_type"] = (
    df["user_type"]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
)


# ============================================================
# TIME FEATURES
# ============================================================

df["hour"] = df["start_time"].dt.hour

df["day_name"] = df["start_time"].dt.day_name()

df["trip_date"] = df["start_time"].dt.date


# ============================================================
# PEAK PERIOD
# ============================================================

def get_peak_period(hour):

    if 7 <= hour <= 9:

        return "Morning Peak"

    elif 16 <= hour <= 18:

        return "Evening Peak"

    elif 10 <= hour <= 15:

        return "Midday"

    else:

        return "Off-Peak"


df["peak_period"] = df["hour"].apply(get_peak_period)


# ============================================================
# DURATION CLEANING
# ============================================================

if "duration_min" not in df.columns:

    df["duration_min"] = df["duration_sec"] / 60


if "duration_hour" not in df.columns:

    df["duration_hour"] = df["duration_sec"] / 3600


# ============================================================
# COLORS
# ============================================================

PRIMARY_BLUE = "#0B5A82"
PRIMARY_DARK = "#084866"

LIGHT_BLUE = "#EAF6FF"
SOFT_BLUE = "#F4FAFE"

TEXT = "#243B53"
MUTED = "#718096"

WHITE = "#FFFFFF"
BACKGROUND = "#F6FAFD"
BORDER = "#E1EAF2"

GOLD = "#F4B942"
SUCCESS = "#36A269"


# ============================================================
# DASH APP
# ============================================================

app = Dash(
    __name__,
    suppress_callback_exceptions=True
)

app.title = "Ford GoBike | Analytics Platform"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def empty_figure(message="No data available"):

    fig = go.Figure()

    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(
            size=16,
            color=MUTED
        )
    )

    fig.update_layout(
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        xaxis=dict(
            visible=False
        ),
        yaxis=dict(
            visible=False
        ),
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        )
    )

    return fig


def base_figure(fig):

    fig.update_layout(
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(
            family="Arial",
            color=TEXT
        ),
        margin=dict(
            l=45,
            r=25,
            t=45,
            b=45
        ),
        hoverlabel=dict(
            bgcolor=WHITE,
            font_color=TEXT
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0)"
        )
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor=BORDER
    )

    fig.update_yaxes(
        gridcolor="#EDF2F7",
        zeroline=False
    )

    return fig


def filter_data(
    data,
    user_type="All",
    gender="All",
    age_group="All",
    start_date=None,
    end_date=None
):

    filtered = data.copy()

    if user_type != "All":

        filtered = filtered[
            filtered["user_type"] == user_type
        ]

    if gender != "All":

        filtered = filtered[
            filtered["member_gender"] == gender
        ]

    if age_group != "All":

        filtered = filtered[
            filtered["age_group"] == age_group
        ]

    if start_date:

        filtered = filtered[
            filtered["start_time"].dt.date >= pd.to_datetime(
                start_date
            ).date()
        ]

    if end_date:

        filtered = filtered[
            filtered["start_time"].dt.date <= pd.to_datetime(
                end_date
            ).date()
        ]

    return filtered


def card_title(title):

    return html.Div(
        title,
        style={
            "fontSize": "15px",
            "fontWeight": "700",
            "color": TEXT,
            "marginBottom": "12px"
        }
    )


def kpi_card(title, value, subtitle=""):

    return html.Div(
        [

            html.Div(
                title,
                style={
                    "fontSize": "13px",
                    "fontWeight": "600",
                    "color": MUTED,
                    "marginBottom": "8px"
                }
            ),

            html.Div(
                value,
                style={
                    "fontSize": "28px",
                    "fontWeight": "700",
                    "color": PRIMARY_BLUE,
                    "marginBottom": "4px"
                }
            ),

            html.Div(
                subtitle,
                style={
                    "fontSize": "12px",
                    "color": MUTED
                }
            )

        ],
        style={
            "backgroundColor": WHITE,
            "border": f"1px solid {BORDER}",
            "borderRadius": "12px",
            "padding": "18px",
            "minHeight": "105px",
            "boxShadow": "0 2px 8px rgba(15, 50, 70, 0.04)"
        }
    )


def insight_card(title, text):

    return html.Div(
        [

            html.Div(
                title,
                style={
                    "fontSize": "14px",
                    "fontWeight": "700",
                    "color": PRIMARY_BLUE,
                    "marginBottom": "7px"
                }
            ),

            html.Div(
                text,
                style={
                    "fontSize": "13px",
                    "lineHeight": "1.6",
                    "color": TEXT
                }
            )

        ],
        style={
            "backgroundColor": SOFT_BLUE,
            "borderLeft": f"4px solid {PRIMARY_BLUE}",
            "borderRadius": "8px",
            "padding": "15px",
            "marginBottom": "10px"
        }
    )


# ============================================================
# SIDEBAR
# ============================================================

sidebar = html.Div(

    [

        html.Div(
            [

                html.Div(
                    "Ford GoBike",
                    style={
                        "fontSize": "23px",
                        "fontWeight": "800",
                        "color": WHITE
                    }
                ),

                html.Div(
                    "Analytics Platform",
                    style={
                        "fontSize": "12px",
                        "color": "#CFE8F5",
                        "marginTop": "3px"
                    }
                )

            ],
            style={
                "marginBottom": "32px"
            }
        ),


        html.Div(
            "FILTERS",
            style={
                "fontSize": "11px",
                "fontWeight": "700",
                "letterSpacing": "1px",
                "color": "#A9D0E2",
                "marginBottom": "14px"
            }
        ),


        html.Label(
            "User Type",
            style={
                "fontSize": "12px",
                "fontWeight": "600",
                "color": WHITE
            }
        ),

        dcc.Dropdown(
            id="filter-user-type",
            options=[
                {
                    "label": "All",
                    "value": "All"
                }
            ] + [
                {
                    "label": value,
                    "value": value
                }
                for value in sorted(
                    df["user_type"].dropna().unique()
                )
            ],
            value="All",
            clearable=False,
            style={
                "marginBottom": "18px",
                "color": TEXT
            }
        ),


        html.Label(
            "Gender",
            style={
                "fontSize": "12px",
                "fontWeight": "600",
                "color": WHITE
            }
        ),

        dcc.Dropdown(
            id="filter-gender",
            options=[
                {
                    "label": "All",
                    "value": "All"
                }
            ] + [
                {
                    "label": value,
                    "value": value
                }
                for value in sorted(
                    df["member_gender"].dropna().unique()
                )
            ],
            value="All",
            clearable=False,
            style={
                "marginBottom": "18px",
                "color": TEXT
            }
        ),


        html.Label(
            "Age Group",
            style={
                "fontSize": "12px",
                "fontWeight": "600",
                "color": WHITE
            }
        ),

        dcc.Dropdown(
            id="filter-age-group",
            options=[
                {
                    "label": "All",
                    "value": "All"
                }
            ] + [
                {
                    "label": value,
                    "value": value
                }
                for value in [
                    "18-24",
                    "25-34",
                    "35-44",
                    "45-54",
                    "55-64",
                    "65+",
                    "Unknown"
                ]
                if value in df["age_group"].unique()
            ],
            value="All",
            clearable=False,
            style={
                "marginBottom": "18px",
                "color": TEXT
            }
        ),


        html.Label(
            "Date Range",
            style={
                "fontSize": "12px",
                "fontWeight": "600",
                "color": WHITE
            }
        ),

        dcc.DatePickerRange(
            id="filter-date",
            min_date_allowed="2019-02-01",
            max_date_allowed="2019-02-28",
            start_date="2019-02-01",
            end_date="2019-02-28",
            display_format="DD MMM",
            style={
                "marginBottom": "20px"
            }
        ),

    ],

    style={
        "position": "fixed",
        "left": "0",
        "top": "0",
        "bottom": "0",
        "width": "240px",
        "backgroundColor": PRIMARY_DARK,
        "padding": "28px 20px",
        "boxSizing": "border-box",
        "overflowY": "auto"
    }
)


# ============================================================
# HEADER
# ============================================================

header = html.Div(

    [

        html.Div(
            [

                html.Div(
                    "Ford GoBike",
                    style={
                        "fontSize": "25px",
                        "fontWeight": "800",
                        "color": PRIMARY_BLUE,
                        "display": "inline-block",
                        "marginRight": "8px"
                    }
                ),

                html.Div(
                    "Analytics Platform",
                    style={
                        "fontSize": "25px",
                        "fontWeight": "500",
                        "color": TEXT,
                        "display": "inline-block"
                    }
                ),

            ]
        ),

        html.Div(
            "February 2019",
            style={
                "fontSize": "13px",
                "color": MUTED,
                "marginTop": "6px"
            }
        )

    ],

    style={
        "marginBottom": "22px"
    }
)


# ============================================================
# NAVIGATION
# ============================================================

nav_button_style = {
    "border": "none",
    "backgroundColor": WHITE,
    "color": MUTED,
    "padding": "10px 18px",
    "borderRadius": "8px",
    "fontWeight": "600",
    "cursor": "pointer",
    "marginRight": "8px"
}


navigation = html.Div(

    [

        html.Button(
            "Overview",
            id="nav-overview",
            n_clicks=0,
            style={
                **nav_button_style,
                "backgroundColor": PRIMARY_BLUE,
                "color": WHITE
            }
        ),

        html.Button(
            "Time Analysis",
            id="nav-time",
            n_clicks=0,
            style=nav_button_style
        ),

        html.Button(
            "User Analysis",
            id="nav-user",
            n_clicks=0,
            style=nav_button_style
        ),

        html.Button(
            "Duration Analysis",
            id="nav-duration",
            n_clicks=0,
            style=nav_button_style
        ),

        html.Button(
            "Stations",
            id="nav-stations",
            n_clicks=0,
            style=nav_button_style
        ),

    ],

    style={
        "backgroundColor": WHITE,
        "padding": "10px",
        "borderRadius": "10px",
        "border": f"1px solid {BORDER}",
        "marginBottom": "22px"
    }
)


# ============================================================
# PAGE 1 - OVERVIEW
# ============================================================

overview_page = html.Div(

    id="page-overview",

    children=[

        html.Div(
            id="overview-kpis",
            style={
                "display": "grid",
                "gridTemplateColumns":
                    "repeat(4, minmax(0, 1fr))",
                "gap": "14px",
                "marginBottom": "18px"
            }
        ),

        html.Div(
            [

                html.Div(
                    [

                        card_title(
                            "Daily Trips"
                        ),

                        dcc.Graph(
                            id="overview-daily-chart",
                            config={
                                "displayModeBar": False
                            }
                        )

                    ],
                    style={
                        "backgroundColor": WHITE,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "12px",
                        "padding": "15px"
                    }
                ),

                html.Div(
                    [

                        card_title(
                            "User Type Distribution"
                        ),

                        dcc.Graph(
                            id="overview-user-type-chart",
                            config={
                                "displayModeBar": False
                            }
                        )

                    ],
                    style={
                        "backgroundColor": WHITE,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "12px",
                        "padding": "15px"
                    }
                )

            ],

            style={
                "display": "grid",
                "gridTemplateColumns":
                    "2fr 1fr",
                "gap": "14px",
                "marginBottom": "18px"
            }
        ),

        html.Div(
            [

                html.Div(
                    "Key Insights",
                    style={
                        "fontSize": "17px",
                        "fontWeight": "700",
                        "color": TEXT,
                        "marginBottom": "12px"
                    }
                ),

                html.Div(
                    id="overview-insights"
                )

            ],

            style={
                "backgroundColor": WHITE,
                "border": f"1px solid {BORDER}",
                "borderRadius": "12px",
                "padding": "18px"
            }
        )

    ],

    style={
        "display": "block"
    }
)


# ============================================================
# PAGE 2 - TIME ANALYSIS
# ============================================================

time_page = html.Div(

    id="page-time",

    children=[

        html.Div(
            [

                html.Div(
                    [

                        card_title(
                            "Trips by Hour"
                        ),

                        dcc.Graph(
                            id="time-hour-chart",
                            config={
                                "displayModeBar": False
                            }
                        )

                    ],
                    style={
                        "backgroundColor": WHITE,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "12px",
                        "padding": "15px"
                    }
                ),

                html.Div(
                    [

                        card_title(
                            "Trips by Weekday"
                        ),

                        dcc.Graph(
                            id="time-weekday-chart",
                            config={
                                "displayModeBar": False
                            }
                        )

                    ],
                    style={
                        "backgroundColor": WHITE,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "12px",
                        "padding": "15px"
                    }
                )

            ],

            style={
                "display": "grid",
                "gridTemplateColumns":
                    "1fr 1fr",
                "gap": "14px",
                "marginBottom": "18px"
            }
        ),

        html.Div(
            [

                card_title(
                    "Peak Period Distribution"
                ),

                dcc.Graph(
                    id="time-peak-chart",
                    config={
                        "displayModeBar": False
                    }
                )

            ],

            style={
                "backgroundColor": WHITE,
                "border": f"1px solid {BORDER}",
                "borderRadius": "12px",
                "padding": "15px"
            }
        )

    ],

    style={
        "display": "none"
    }
)


# ============================================================
# PAGE 3 - USER ANALYSIS
# ============================================================

user_page = html.Div(

    id="page-user",

    children=[

        html.Div(
            [

                html.Div(
                    [

                        card_title(
                            "Gender Distribution"
                        ),

                        dcc.Graph(
                            id="user-gender-chart",
                            config={
                                "displayModeBar": False
                            }
                        )

                    ],
                    style={
                        "backgroundColor": WHITE,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "12px",
                        "padding": "15px"
                    }
                ),

                html.Div(
                    [

                        card_title(
                            "Age Group Distribution"
                        ),

                        dcc.Graph(
                            id="user-age-chart",
                            config={
                                "displayModeBar": False
                            }
                        )

                    ],
                    style={
                        "backgroundColor": WHITE,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "12px",
                        "padding": "15px"
                    }
                )

            ],

            style={
                "display": "grid",
                "gridTemplateColumns":
                    "1fr 1fr",
                "gap": "14px",
                "marginBottom": "18px"
            }
        ),

        html.Div(
            [

                card_title(
                    "User Composition"
                ),

                dcc.Graph(
                    id="user-composition-chart",
                    config={
                        "displayModeBar": False
                    }
                )

            ],

            style={
                "backgroundColor": WHITE,
                "border": f"1px solid {BORDER}",
                "borderRadius": "12px",
                "padding": "15px"
            }
        )

    ],

    style={
        "display": "none"
    }
)


# ============================================================
# PAGE 4 - DURATION ANALYSIS
# ============================================================

duration_page = html.Div(

    id="page-duration",

    children=[

        html.Div(
            [

                html.Div(
                    [

                        card_title(
                            "Average Duration by User Type"
                        ),

                        dcc.Graph(
                            id="duration-user-chart",
                            config={
                                "displayModeBar": False
                            }
                        )

                    ],
                    style={
                        "backgroundColor": WHITE,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "12px",
                        "padding": "15px"
                    }
                ),

                html.Div(
                    [

                        card_title(
                            "Average Duration by Gender"
                        ),

                        dcc.Graph(
                            id="duration-gender-chart",
                            config={
                                "displayModeBar": False
                            }
                        )

                    ],
                    style={
                        "backgroundColor": WHITE,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "12px",
                        "padding": "15px"
                    }
                )

            ],

            style={
                "display": "grid",
                "gridTemplateColumns":
                    "1fr 1fr",
                "gap": "14px",
                "marginBottom": "18px"
            }
        ),

        html.Div(
            [

                html.Div(
                    [

                        card_title(
                            "Average Duration by Age Group"
                        ),

                        dcc.Graph(
                            id="duration-age-chart",
                            config={
                                "displayModeBar": False
                            }
                        )

                    ],
                    style={
                        "backgroundColor": WHITE,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "12px",
                        "padding": "15px"
                    }
                ),

                html.Div(
                    [

                        card_title(
                            "Trip Duration Distribution"
                        ),

                        dcc.Graph(
                            id="duration-histogram",
                            config={
                                "displayModeBar": False
                            }
                        )

                    ],
                    style={
                        "backgroundColor": WHITE,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "12px",
                        "padding": "15px"
                    }
                )

            ],

            style={
                "display": "grid",
                "gridTemplateColumns":
                    "1fr 1fr",
                "gap": "14px"
            }
        )

    ],

    style={
        "display": "none"
    }
)


# ============================================================
# PAGE 5 - STATIONS
# ============================================================

stations_page = html.Div(

    id="page-stations",

    children=[

        html.Div(
            [

                html.Div(
                    [

                        card_title(
                            "Top Start Stations"
                        ),

                        dcc.Graph(
                            id="stations-start-chart",
                            config={
                                "displayModeBar": False
                            }
                        )

                    ],
                    style={
                        "backgroundColor": WHITE,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "12px",
                        "padding": "15px"
                    }
                ),

                html.Div(
                    [

                        card_title(
                            "Top End Stations"
                        ),

                        dcc.Graph(
                            id="stations-end-chart",
                            config={
                                "displayModeBar": False
                            }
                        )

                    ],
                    style={
                        "backgroundColor": WHITE,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "12px",
                        "padding": "15px"
                    }
                )

            ],

            style={
                "display": "grid",
                "gridTemplateColumns":
                    "1fr 1fr",
                "gap": "14px",
                "marginBottom": "18px"
            }
        ),

        html.Div(
            [

                card_title(
                    "Station Activity Map"
                ),

                dcc.Graph(
                    id="stations-map",
                    config={
                        "displayModeBar": False
                    },
                    style={
                        "height": "600px"
                    }
                )

            ],

            style={
                "backgroundColor": WHITE,
                "border": f"1px solid {BORDER}",
                "borderRadius": "12px",
                "padding": "15px"
            }
        )

    ],

    style={
        "display": "none"
    }
)


# ============================================================
# MAIN LAYOUT
# ============================================================

app.layout = html.Div(

    [

        sidebar,

        html.Div(

            [

                header,

                navigation,

                overview_page,

                time_page,

                user_page,

                duration_page,

                stations_page

            ],

            style={
                "marginLeft": "240px",
                "padding": "28px 30px",
                "backgroundColor": BACKGROUND,
                "minHeight": "100vh",
                "boxSizing": "border-box"
            }
        )

    ]

)


# ============================================================
# NAVIGATION CALLBACK
# ============================================================

@app.callback(

    Output("page-overview", "style"),
    Output("page-time", "style"),
    Output("page-user", "style"),
    Output("page-duration", "style"),
    Output("page-stations", "style"),

    Output("nav-overview", "style"),
    Output("nav-time", "style"),
    Output("nav-user", "style"),
    Output("nav-duration", "style"),
    Output("nav-stations", "style"),

    Input("nav-overview", "n_clicks"),
    Input("nav-time", "n_clicks"),
    Input("nav-user", "n_clicks"),
    Input("nav-duration", "n_clicks"),
    Input("nav-stations", "n_clicks"),

)

def navigate(
    overview_clicks,
    time_clicks,
    user_clicks,
    duration_clicks,
    stations_clicks
):

    # --------------------------------------------------------
    # IMPORTANT:
    # ctx.triggered_id tells us which button was actually clicked.
    # This fixes the problem caused by comparing cumulative
    # n_clicks values.
    # --------------------------------------------------------

    triggered = ctx.triggered_id

    if triggered is None:

        active_page = "overview"

    elif triggered == "nav-overview":

        active_page = "overview"

    elif triggered == "nav-time":

        active_page = "time"

    elif triggered == "nav-user":

        active_page = "user"

    elif triggered == "nav-duration":

        active_page = "duration"

    elif triggered == "nav-stations":

        active_page = "stations"

    else:

        active_page = "overview"


    # --------------------------------------------------------
    # PAGE STYLES
    # --------------------------------------------------------

    page_styles = {

        "overview": {
            "display": "none"
        },

        "time": {
            "display": "none"
        },

        "user": {
            "display": "none"
        },

        "duration": {
            "display": "none"
        },

        "stations": {
            "display": "none"
        }

    }

    page_styles[active_page] = {
        "display": "block"
    }


    # --------------------------------------------------------
    # NAVIGATION BUTTON STYLES
    # --------------------------------------------------------

    active_nav = {

        "border": "none",

        "backgroundColor": PRIMARY_BLUE,

        "color": WHITE,

        "padding": "10px 18px",

        "borderRadius": "8px",

        "fontWeight": "600",

        "cursor": "pointer",

        "marginRight": "8px"

    }


    inactive_nav = {

        "border": "none",

        "backgroundColor": WHITE,

        "color": MUTED,

        "padding": "10px 18px",

        "borderRadius": "8px",

        "fontWeight": "600",

        "cursor": "pointer",

        "marginRight": "8px"

    }


    nav_styles = {

        "overview": inactive_nav.copy(),

        "time": inactive_nav.copy(),

        "user": inactive_nav.copy(),

        "duration": inactive_nav.copy(),

        "stations": inactive_nav.copy()

    }

    nav_styles[active_page] = active_nav.copy()


    return (

        page_styles["overview"],

        page_styles["time"],

        page_styles["user"],

        page_styles["duration"],

        page_styles["stations"],

        nav_styles["overview"],

        nav_styles["time"],

        nav_styles["user"],

        nav_styles["duration"],

        nav_styles["stations"]

    )


# ============================================================
# ANALYTICS CALLBACK
# ============================================================

@app.callback(

    Output("overview-kpis", "children"),
    Output("overview-daily-chart", "figure"),
    Output("overview-user-type-chart", "figure"),
    Output("overview-insights", "children"),

    Output("time-hour-chart", "figure"),
    Output("time-weekday-chart", "figure"),
    Output("time-peak-chart", "figure"),

    Output("user-gender-chart", "figure"),
    Output("user-age-chart", "figure"),
    Output("user-composition-chart", "figure"),

    Output("duration-user-chart", "figure"),
    Output("duration-gender-chart", "figure"),
    Output("duration-age-chart", "figure"),
    Output("duration-histogram", "figure"),

    Output("stations-start-chart", "figure"),
    Output("stations-end-chart", "figure"),
    Output("stations-map", "figure"),

    Input("filter-user-type", "value"),
    Input("filter-gender", "value"),
    Input("filter-age-group", "value"),
    Input("filter-date", "start_date"),
    Input("filter-date", "end_date")

)

def update_dashboard(
    user_type,
    gender,
    age_group,
    start_date,
    end_date
):

    filtered = filter_data(
        df,
        user_type,
        gender,
        age_group,
        start_date,
        end_date
    )


    # ========================================================
    # EMPTY DATA
    # ========================================================

    if filtered.empty:

        empty = empty_figure(
            "No data available for the selected filters"
        )

        empty_kpis = [

            kpi_card(
                "Total Trips",
                "0",
                "Selected period"
            ),

            kpi_card(
                "Average Duration",
                "0 min",
                "Per trip"
            ),

            kpi_card(
                "Active Bikes",
                "0",
                "Unique bikes"
            ),

            kpi_card(
                "Average Age",
                "0",
                "Members"
            )

        ]

        empty_insights = [

            insight_card(
                "No data",
                "No records match the selected filters."
            )

        ]

        return (

            empty_kpis,

            empty,
            empty,

            empty_insights,

            empty,
            empty,
            empty,

            empty,
            empty,
            empty,

            empty,
            empty,
            empty,
            empty,

            empty,
            empty,
            empty

        )


    # ========================================================
    # KPI VALUES
    # ========================================================

    total_trips = len(filtered)

    avg_duration = filtered["duration_min"].mean()

    active_bikes = filtered["bike_id"].nunique()

    avg_age = filtered["member_age"].mean()


    # ========================================================
    # KPI CARDS
    # ========================================================

    kpis = [

        kpi_card(
            "Total Trips",
            f"{total_trips:,}",
            "Selected period"
        ),

        kpi_card(
            "Average Duration",
            f"{avg_duration:.1f} min",
            "Per trip"
        ),

        kpi_card(
            "Active Bikes",
            f"{active_bikes:,}",
            "Unique bikes"
        ),

        kpi_card(
            "Average Age",
            f"{avg_age:.1f}",
            "Members"
        )

    ]


    # ========================================================
    # DAILY TRIPS
    # ========================================================

    daily = (

        filtered
        .groupby("trip_date")
        .size()
        .reset_index(name="trips")
    )

    daily["trip_date"] = pd.to_datetime(
        daily["trip_date"]
    )

    daily = daily.sort_values(
        "trip_date"
    )


    fig_daily = px.line(
        daily,
        x="trip_date",
        y="trips",
        markers=True
    )

    fig_daily.update_traces(
        line=dict(
            color=PRIMARY_BLUE,
            width=3
        ),
        marker=dict(
            size=6
        )
    )

    fig_daily.update_layout(
        xaxis_title="Date",
        yaxis_title="Trips"
    )

    fig_daily = base_figure(
        fig_daily
    )


    # ========================================================
    # USER TYPE PIE
    # ========================================================

    user_counts = (

        filtered["user_type"]
        .value_counts()
        .reset_index()
    )

    user_counts.columns = [
        "user_type",
        "count"
    ]


    fig_user_type = px.pie(
        user_counts,
        names="user_type",
        values="count",
        hole=0.55
    )

    fig_user_type.update_traces(
        textinfo="percent+label"
    )

    fig_user_type = base_figure(
        fig_user_type
    )


    # ========================================================
    # INSIGHTS
    # ========================================================

    most_common_user = (

        filtered["user_type"]
        .value_counts()
        .idxmax()
    )

    busiest_hour = (

        filtered["hour"]
        .value_counts()
        .idxmax()
    )

    most_common_gender = (

        filtered["member_gender"]
        .value_counts()
        .idxmax()
    )

    top_station_series = (

        filtered["start_station_name"]
        .dropna()
        .value_counts()
    )

    if not top_station_series.empty:

        top_station = top_station_series.index[0]

    else:

        top_station = "N/A"


    insights = [

        insight_card(
            "Most common user type",
            f"{most_common_user} accounts for the largest "
            f"share of trips in the selected data."
        ),

        insight_card(
            "Peak hour",
            f"The highest trip activity occurs around "
            f"{busiest_hour}:00."
        ),

        insight_card(
            "Gender distribution",
            f"{most_common_gender} is the most represented "
            f"gender category in the selected data."
        ),

        insight_card(
            "Top start station",
            f"{top_station} has the highest number of "
            f"recorded trip starts."
        )

    ]


    # ========================================================
    # TIME ANALYSIS
    # ========================================================

    hourly = (

        filtered
        .groupby("hour")
        .size()
        .reset_index(name="trips")
    )

    hourly = hourly.sort_values(
        "hour"
    )


    fig_hour = px.bar(
        hourly,
        x="hour",
        y="trips"
    )

    fig_hour.update_layout(
        xaxis_title="Hour of Day",
        yaxis_title="Trips"
    )

    fig_hour.update_traces(
        marker_color=PRIMARY_BLUE
    )

    fig_hour = base_figure(
        fig_hour
    )


    # ========================================================
    # WEEKDAY
    # ========================================================

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    weekday = (

        filtered
        .groupby("day_name")
        .size()
        .reindex(weekday_order)
        .fillna(0)
        .reset_index(name="trips")
    )


    fig_weekday = px.bar(
        weekday,
        x="day_name",
        y="trips"
    )

    fig_weekday.update_layout(
        xaxis_title="Day",
        yaxis_title="Trips"
    )

    fig_weekday.update_traces(
        marker_color=PRIMARY_BLUE
    )

    fig_weekday = base_figure(
        fig_weekday
    )


    # ========================================================
    # PEAK PERIOD
    # ========================================================

    peak_order = [
        "Morning Peak",
        "Midday",
        "Evening Peak",
        "Off-Peak"
    ]

    peak = (

        filtered
        .groupby("peak_period")
        .size()
        .reindex(peak_order)
        .fillna(0)
        .reset_index(name="trips")
    )


    fig_peak = px.bar(
        peak,
        x="peak_period",
        y="trips"
    )

    fig_peak.update_layout(
        xaxis_title="Period",
        yaxis_title="Trips"
    )

    fig_peak.update_traces(
        marker_color=PRIMARY_BLUE
    )

    fig_peak = base_figure(
        fig_peak
    )


    # ========================================================
    # USER ANALYSIS - GENDER
    # ========================================================

    gender_data = (

        filtered["member_gender"]
        .value_counts()
        .reset_index()
    )

    gender_data.columns = [
        "gender",
        "count"
    ]


    fig_gender = px.bar(
        gender_data,
        x="gender",
        y="count"
    )

    fig_gender.update_layout(
        xaxis_title="Gender",
        yaxis_title="Trips"
    )

    fig_gender.update_traces(
        marker_color=PRIMARY_BLUE
    )

    fig_gender = base_figure(
        fig_gender
    )


    # ========================================================
    # USER ANALYSIS - AGE
    # ========================================================

    age_order = [
        "18-24",
        "25-34",
        "35-44",
        "45-54",
        "55-64",
        "65+",
        "Unknown"
    ]

    age_data = (

        filtered
        .groupby("age_group")
        .size()
        .reindex(age_order)
        .fillna(0)
        .reset_index(name="count")
    )


    fig_age = px.bar(
        age_data,
        x="age_group",
        y="count"
    )

    fig_age.update_layout(
        xaxis_title="Age Group",
        yaxis_title="Trips"
    )

    fig_age.update_traces(
        marker_color=PRIMARY_BLUE
    )

    fig_age = base_figure(
        fig_age
    )


    # ========================================================
    # USER COMPOSITION
    # ========================================================

    composition = (

        filtered
        .groupby(
            [
                "user_type",
                "member_gender"
            ]
        )
        .size()
        .reset_index(name="count")
    )


    fig_composition = px.bar(
        composition,
        x="user_type",
        y="count",
        color="member_gender",
        barmode="group"
    )

    fig_composition.update_layout(
        xaxis_title="User Type",
        yaxis_title="Trips"
    )

    fig_composition = base_figure(
        fig_composition
    )


    # ========================================================
    # DURATION - USER TYPE
    # ========================================================

    duration_user = (

        filtered
        .groupby("user_type")["duration_min"]
        .mean()
        .reset_index()
    )


    fig_duration_user = px.bar(
        duration_user,
        x="user_type",
        y="duration_min"
    )

    fig_duration_user.update_layout(
        xaxis_title="User Type",
        yaxis_title="Average Duration (min)"
    )

    fig_duration_user.update_traces(
        marker_color=PRIMARY_BLUE
    )

    fig_duration_user = base_figure(
        fig_duration_user
    )


    # ========================================================
    # DURATION - GENDER
    # ========================================================

    duration_gender = (

        filtered
        .groupby("member_gender")["duration_min"]
        .mean()
        .reset_index()
    )


    fig_duration_gender = px.bar(
        duration_gender,
        x="member_gender",
        y="duration_min"
    )

    fig_duration_gender.update_layout(
        xaxis_title="Gender",
        yaxis_title="Average Duration (min)"
    )

    fig_duration_gender.update_traces(
        marker_color=PRIMARY_BLUE
    )

    fig_duration_gender = base_figure(
        fig_duration_gender
    )


    # ========================================================
    # DURATION - AGE GROUP
    # ========================================================

    duration_age = (

        filtered
        .groupby("age_group")["duration_min"]
        .mean()
        .reindex(age_order)
        .dropna()
        .reset_index()
    )


    fig_duration_age = px.bar(
        duration_age,
        x="age_group",
        y="duration_min"
    )

    fig_duration_age.update_layout(
        xaxis_title="Age Group",
        yaxis_title="Average Duration (min)"
    )

    fig_duration_age.update_traces(
        marker_color=PRIMARY_BLUE
    )

    fig_duration_age = base_figure(
        fig_duration_age
    )


    # ========================================================
    # DURATION HISTOGRAM
    # ========================================================

    histogram_data = filtered[
        filtered["duration_min"].between(
            0,
            120
        )
    ]


    fig_histogram = px.histogram(
        histogram_data,
        x="duration_min",
        nbins=40
    )

    fig_histogram.update_layout(
        xaxis_title="Duration (minutes)",
        yaxis_title="Trips"
    )

    fig_histogram.update_traces(
        marker_color=PRIMARY_BLUE
    )

    fig_histogram = base_figure(
        fig_histogram
    )


    # ========================================================
    # TOP START STATIONS
    # ========================================================

    start_stations = (

        filtered["start_station_name"]
        .dropna()
        .value_counts()
        .head(10)
        .sort_values()
        .reset_index()
    )

    start_stations.columns = [
        "station",
        "count"
    ]


    fig_start = px.bar(
        start_stations,
        x="count",
        y="station",
        orientation="h"
    )

    fig_start.update_layout(
        xaxis_title="Trips",
        yaxis_title="Start Station"
    )

    fig_start.update_traces(
        marker_color=PRIMARY_BLUE
    )

    fig_start = base_figure(
        fig_start
    )


    # ========================================================
    # TOP END STATIONS
    # ========================================================

    end_stations = (

        filtered["end_station_name"]
        .dropna()
        .value_counts()
        .head(10)
        .sort_values()
        .reset_index()
    )

    end_stations.columns = [
        "station",
        "count"
    ]


    fig_end = px.bar(
        end_stations,
        x="count",
        y="station",
        orientation="h"
    )

    fig_end.update_layout(
        xaxis_title="Trips",
        yaxis_title="End Station"
    )

    fig_end.update_traces(
        marker_color=PRIMARY_BLUE
    )

    fig_end = base_figure(
        fig_end
    )


    # ========================================================
    # STATION MAP
    # ========================================================

    map_data = filtered[
        [
            "start_station_name",
            "start_station_latitude",
            "start_station_longitude"
        ]
    ].dropna()


    map_data = (

        map_data
        .groupby(
            [
                "start_station_name",
                "start_station_latitude",
                "start_station_longitude"
            ]
        )
        .size()
        .reset_index(name="trips")
    )


    if map_data.empty:

        fig_map = empty_figure(
            "No station location data available"
        )

    else:

        try:

            fig_map = go.Figure()

            fig_map.add_trace(
                go.Scattermap(
                    lat=map_data[
                        "start_station_latitude"
                    ],

                    lon=map_data[
                        "start_station_longitude"
                    ],

                    mode="markers",

                    marker=dict(
                        size=10
                    ),

                    text=map_data[
                        "start_station_name"
                    ],

                    customdata=map_data[
                        ["trips"]
                    ],

                    hovertemplate=
                    "<b>%{text}</b><br>"
                    "Trips: %{customdata[0]}"
                    "<extra></extra>"
                )
            )

            fig_map.update_layout(

                map=dict(
                    style="open-street-map",

                    center=dict(
                        lat=map_data[
                            "start_station_latitude"
                        ].mean(),

                        lon=map_data[
                            "start_station_longitude"
                        ].mean()
                    ),

                    zoom=11
                ),

                margin=dict(
                    l=0,
                    r=0,
                    t=0,
                    b=0
                ),

                paper_bgcolor=WHITE

            )

        except AttributeError:

            fig_map = go.Figure()

            fig_map.add_trace(
                go.Scattermapbox(

                    lat=map_data[
                        "start_station_latitude"
                    ],

                    lon=map_data[
                        "start_station_longitude"
                    ],

                    mode="markers",

                    marker=dict(
                        size=10
                    ),

                    text=map_data[
                        "start_station_name"
                    ],

                    customdata=map_data[
                        ["trips"]
                    ],

                    hovertemplate=
                    "<b>%{text}</b><br>"
                    "Trips: %{customdata[0]}"
                    "<extra></extra>"
                )
            )

            fig_map.update_layout(

                mapbox=dict(

                    style="open-street-map",

                    center=dict(

                        lat=map_data[
                            "start_station_latitude"
                        ].mean(),

                        lon=map_data[
                            "start_station_longitude"
                        ].mean()

                    ),

                    zoom=11

                ),

                margin=dict(
                    l=0,
                    r=0,
                    t=0,
                    b=0
                ),

                paper_bgcolor=WHITE

            )


    # ========================================================
    # RETURN EVERYTHING
    # ========================================================

    return (

        kpis,

        fig_daily,
        fig_user_type,
        insights,

        fig_hour,
        fig_weekday,
        fig_peak,

        fig_gender,
        fig_age,
        fig_composition,

        fig_duration_user,
        fig_duration_gender,
        fig_duration_age,
        fig_histogram,

        fig_start,
        fig_end,
        fig_map

    )


# ============================================================
# RUN APP
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=8050
    )