import plotly.express as px
import pandas as pd


def bar(df: pd.DataFrame, x: str, y: str, title: str = "", text: str = None,
        width: int = None, height: int = 400):
    fig = px.bar(df, x=x, y=y, title=title, text=text, width=width, height=height)
    if text:
        fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_tickangle=-30)
    return fig


def grouped_bar(df: pd.DataFrame, x: str, y_cols: list, title: str = "",
                 width: int = None, height: int = 400):
    fig = px.bar(df, x=x, y=y_cols, title=title, barmode="group", width=width, height=height)
    fig.update_layout(xaxis_tickangle=-30)
    return fig


def line(df: pd.DataFrame, x: str, y: str, title: str = "",
         width: int = None, height: int = 400):
    fig = px.line(df, x=x, y=y, markers=True, title=title, width=width, height=height)
    return fig


def multi_line(df: pd.DataFrame, x: str, y_cols: list, title: str = "",
                width: int = None, height: int = 400):
    fig = px.line(df, x=x, y=y_cols, markers=True, title=title, width=width, height=height)
    return fig


def pie(df: pd.DataFrame, names: str, values: str, title: str = "",
        width: int = None, height: int = 400):
    fig = px.pie(df, names=names, values=values, title=title, width=width, height=height)
    return fig


def donut(df: pd.DataFrame, names: str, values: str, title: str = "",
          width: int = None, height: int = 400):
    fig = px.pie(df, names=names, values=values, title=title, hole=0.5,
                 width=width, height=height)
    return fig


def scatter(df: pd.DataFrame, x: str, y: str, color: str = None, title: str = "",
            width: int = None, height: int = 400):
    fig = px.scatter(df, x=x, y=y, color=color, title=title, width=width, height=height)
    return fig


def heatmap(df: pd.DataFrame, x: str, y: str, z: str, title: str = "",
            width: int = None, height: int = 400):
    pivot = df.pivot(index=y, columns=x, values=z)
    fig = px.imshow(pivot, title=title, width=width, height=height, text_auto=True)
    return fig


def pivot(df: pd.DataFrame, index_col: str, value_col: str, agg: str = "count"):
    return df.groupby(index_col)[value_col].agg(agg).reset_index()