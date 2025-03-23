import gradio as gr
import pandas as pd
from scripts.calculate import (
    twd,
    twa,
    vmg,
    sog_and_cog,
    get_maneuvers,
    group_by_maneuvers,
)
from scripts.visualize import map, plot_column_by_time
from scripts.parse import gpx_to_dataframe


def upload_event(file_input):
    df = gpx_to_dataframe(file_input)
    df = sog_and_cog(df)
    html_map = map(df)
    line_plot = plot_column_by_time(df, "Time", ["SOG"], [0, 40], 150)

    return df, html_map, line_plot


def calculate_event(
    df, port_start, port_end, starboard_start, starboard_end, plot_settings, twd=0
):
    if twd == 0:
        twd = twd(df, port_start, port_end, starboard_start, starboard_end)
    df = vmg(df, twd)
    df = twa(df, twd)
    html_map = map(df, twd=twd)

    height = 250
    # Upwind plots
    # plot_1_df = df[df['VMG'] > 5]
    plot_1_df = df[df["VMG"] > plot_settings["min_vmg"][0]]
    # plot_1_df = plot_1_df[plot_1_df['SOG'] > 5]
    plot_1_df = plot_1_df[plot_1_df["SOG"] > plot_settings["min_upwind_sog"][0]]
    # plot_1_df = plot_1_df[plot_1_df['TWA'] < 55]
    plot_1_df = plot_1_df[plot_1_df["TWA"] < plot_settings["max_upwind_twa"][0]]
    # plot_1_df = plot_1_df[plot_1_df['TWA'] > -55]
    plot_1_df = plot_1_df[plot_1_df["TWA"] > -plot_settings["max_upwind_twa"][0]]

    plot_1_up = plot_column_by_time(plot_1_df, "SOG", ["VMG"], height=height)

    # plot_2_df = df[df['VMG'] > 8]
    plot_2_df = df[df["VMG"] > plot_settings["min_vmg"][0]]
    # plot_2_df = plot_2_df[plot_2_df['SOG'] > 5]
    plot_2_df = plot_2_df[plot_2_df["SOG"] > plot_settings["min_upwind_sog"][0]]
    plot_2_up = plot_column_by_time(plot_2_df, "TWA", ["VMG"], height=height)

    # Downwind plots
    # plot_1_df = df[df['VMG'] < -5]
    plot_1_df = df[df["VMG"] < -plot_settings["min_vmg"][0]]
    # plot_1_df = plot_1_df[plot_1_df['SOG'] > 5]
    plot_1_df = plot_1_df[plot_1_df["SOG"] > plot_settings["min_downwind_sog"][0]]

    # plot_1_df = plot_1_df[plot_1_df['TWA'] < -120]
    # plot_1_df = plot_1_df[plot_1_df['TWA'] > 120]
    plot_1_down = plot_column_by_time(plot_1_df, "SOG", ["VMG"], height=height)

    # plot_2_df = df[df['VMG'] < -8]
    plot_2_df = df[df["VMG"] < -plot_settings["min_vmg"][0]]
    # plot_2_df = plot_2_df[plot_2_df['SOG'] > 5]
    plot_2_df = plot_2_df[plot_2_df["SOG"] > plot_settings["min_downwind_sog"][0]]
    plot_2_down = plot_column_by_time(plot_2_df, "TWA", ["VMG"], height=height)

    return twd, df, html_map, plot_1_up, plot_2_up, plot_1_down, plot_2_down


def maneuver_event(df, twd=0):
    new_df = get_maneuvers(df)
    # html_map = plot_map(new_df, twd=twd)
    df_manouver = group_by_maneuvers(new_df)
    checkbox_container = [gr.Checkbox(label=f"Maneuver {i}") for i in range(len(df))]

    return df_manouver, checkbox_container  # , html_map


def settings_event(
    min_upwind_sog,
    max_upwind_sog,
    min_downwind_sog,
    max_downwind_sog,
    min_upwind_twa,
    max_upwind_twa,
    min_downwind_twa,
    max_downwind_twa,
    min_vmg,
):
    df_settings = pd.DataFrame(
        {
            "min_upwind_sog": [min_upwind_sog],
            "max_upwind_sog": [max_upwind_sog],
            "min_downwind_sog": [min_downwind_sog],
            "max_downwind_sog": [max_downwind_sog],
            "min_upwind_twa": [min_upwind_twa],
            "max_upwind_twa": [max_upwind_twa],
            "min_downwind_twa": [min_downwind_twa],
            "max_downwind_twa": [max_downwind_twa],
            "min_vmg": [min_vmg],
        }
    )

    return df_settings
