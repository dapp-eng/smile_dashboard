# chart factory - thin wrappers around plotly express

import plotly.express as px
import pandas as pd


def bar(df: pd.DataFrame, x: str, y: str = None, title: str = "", text: str = None,
        width: int = None, height: int = 400, **kwargs):
    fig = px.bar(df, x=x, y=y, title=title, text=text, width=width, height=height, **kwargs)
    if text:
        fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_tickangle=-30)
    return fig


def grouped_bar(df: pd.DataFrame, x: str, y_cols: list, title: str = "",
                 width: int = None, height: int = 400, **kwargs):
    fig = px.bar(df, x=x, y=y_cols, title=title, barmode="group", width=width, height=height, **kwargs)
    fig.update_layout(xaxis_tickangle=-30)
    return fig


def histogram(df: pd.DataFrame, x: str, title: str = "",
              width: int = None, height: int = 400, **kwargs):
    fig = px.histogram(df, x=x, title=title, width=width, height=height, **kwargs)
    return fig


def line(df: pd.DataFrame, x: str, y: str, title: str = "",
         width: int = None, height: int = 400, **kwargs):
    fig = px.line(df, x=x, y=y, markers=True, title=title, width=width, height=height, **kwargs)
    return fig


def multi_line(df: pd.DataFrame, x: str, y_cols: list, title: str = "",
                width: int = None, height: int = 400, **kwargs):
    fig = px.line(df, x=x, y=y_cols, markers=True, title=title, width=width, height=height, **kwargs)
    return fig


def pie(df: pd.DataFrame, names: str, values: str, title: str = "",
        width: int = None, height: int = 400, **kwargs):
    fig = px.pie(df, names=names, values=values, title=title, width=width, height=height, **kwargs)
    return fig


def donut(df: pd.DataFrame, names: str, values: str, title: str = "",
          width: int = None, height: int = 400, **kwargs):
    # use kwarg hole if provided, else default to 0.5
    hole = kwargs.pop("hole", 0.5)
    fig = px.pie(df, names=names, values=values, title=title, hole=hole,
                 width=width, height=height, **kwargs)
    return fig


def scatter(df: pd.DataFrame, x: str, y: str, color: str = None, title: str = "",
            width: int = None, height: int = 400, **kwargs):
    fig = px.scatter(df, x=x, y=y, color=color, title=title, width=width, height=height, **kwargs)
    return fig


def heatmap(df: pd.DataFrame, x: str, y: str, z: str, title: str = "",
            width: int = None, height: int = 400, **kwargs):
    pivot = df.pivot(index=y, columns=x, values=z)
    fig = px.imshow(pivot, title=title, width=width, height=height, text_auto=True, **kwargs)
    return fig


def pivot(df: pd.DataFrame, index_col: str, value_col: str, agg: str = "count"):
    return df.groupby(index_col)[value_col].agg(agg).reset_index()