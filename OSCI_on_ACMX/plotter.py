"""
Module to plot measurement results
"""

import os
import sys
import random
import logging
from typing import List

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set up logging
logger = logging.getLogger(__name__)


def _get_random_color() -> tuple[str, str]:
    """Return a random color from a predefined palette."""
    colors = ["black", "mediumpurple", "orangered", "firebrick", "teal", "olive"]
    color1, color2 = random.choice(colors), random.choice(colors)
    while color2 == color1:
        # Ensure two different colors are chosen
        color1, color2 = random.choice(colors), random.choice(colors)

    return color1, color2


def _load_csv_file(filepath: str) -> pd.DataFrame:
    """Load a CSV file into a DataFrame and ensure content validity."""
    df = pd.read_csv(filepath)
    if df.empty or len(df.columns) < 1:
        raise ValueError(f"CSV file '{filepath}' is empty or has no columns.")
    return df


def check_df_consistency(dataframes: List[pd.DataFrame], filenames: List[str]) -> None:
    """Ensure all DataFrames have the same structure."""
    reference_columns = dataframes[0].columns
    for i, df in enumerate(dataframes[1:], start=1):
        if not reference_columns.equals(df.columns):
            logger.error("Inconsistent columns in file: %s", filenames[i])
            sys.exit(-1)


def build_figure(dataframes, filenames, marker1_ns=None, marker2_ns=None) -> go.Figure:
    """Create and return a plotly figure with subplots for each column of the dataframes."""
    column_names = dataframes[0].columns.tolist()
    fig = make_subplots(
        rows=len(column_names),
        cols=1,
        shared_xaxes=False,
        subplot_titles=column_names,
        vertical_spacing=0.06,
    )

    for index, df in enumerate(dataframes):
        filename = filenames[index].removesuffix(".csv")
        colors = _get_random_color()

        for row, col_name in enumerate(column_names[1:], start=1):  # Skip 'Timestamp'
            fig.add_trace(
                go.Scatter(
                    x=df["Timestamp"],
                    y=df[col_name],
                    name=f"{col_name} - {filename}, measure {index}",
                    line=dict(color=colors.index(index)),
                ),
                row=row,
                col=1,
            )

    if marker1_ns is not None:
        fig.add_vline(
            x=marker1_ns,
            line=dict(color="grey", dash="dash"),
            annotation_text=f"{marker1_ns} ns",
            annotation_position="top left",
        )
    if marker2_ns is not None:
        fig.add_vline(
            x=marker2_ns,
            line=dict(color="grey", dash="dash"),
            annotation_text=f"{marker2_ns} ns",
            annotation_position="top right",
        )

    fig.update_layout(
        margin=dict(l=30, r=30),
        template="ggplot2",
        height=1000,
        title_text="Measurements",
    )
    return fig


def plot_collected_data(
    folder: str,
    filenames: List[str],
    html_name: str = None,
    marker1_ns: float = None,
    marker2_ns: float = None,
) -> None:
    """
    Plot measurements from CSV files in subplots.
    Each subplot corresponds to a column in the data (excluding 'Timestamp').
    """
    logger.info("Plotting data from folder: %s", folder)
    csv_paths = []
    for file in filenames:
        if not file.endswith(".csv"):
            logger.error(
                "File:'%s' is not a CSV file.",file
            )
            sys.exit(-1)
        csv_paths.append(os.path.join(folder, file))

    dataframes = [_load_csv_file(path) for path in csv_paths]
    check_df_consistency(dataframes, filenames)

    logger.info("Data loaded successfully. Building figure...")
    fig = build_figure(dataframes, filenames, marker1_ns, marker2_ns)
    fig.show()

    logger.info("Figure built successfully. Saving to HTML...")
    if html_name is not None:
        if not html_name.endswith(".html"):
            logger.error("File:'%s' is not an html file.", html_name)
            sys.exit(-1)
        fig.write_html(os.path.join(folder, html_name))
