import gradio as gr
import pandas as pd
from scripts.calculate import (
    get_twd,
    get_twa,
    get_vmg,
    get_sog_cog,
    get_maneuvers,
    group_by_maneuvers,
    do_smart_filtering,
)
from scripts.visualize import (
    get_map,
    get_polar_plot,
    get_timeline_plot,
    get_upwind_vmgsog_plot,
    get_upwind_vmgtwa_plot,
    get_downwind_vmgsog_plot,
    get_downwind_vmgtwa_plot,
)
from scripts.parse import gpx_to_dataframe


def upload_event(file_input):
    df_full = gpx_to_dataframe(file_input)
    df_full = get_sog_cog(df_full)
    html_map = get_map(df_full)
    line_plot = get_timeline_plot(df_full)
    df_select = df_full
    print("Upload event finished")

    return df_full, df_select, html_map, line_plot


def calculate_event(
    df,
    df_settings,
    twd=0,
    smart_filter_checkbox=False,
):
    df = get_sog_cog(df)

    print("twd")
    print(twd)

    try:
        # twd = float(twd)
        print("TWD has been converted to float")
    except (ValueError, TypeError):
        twd = 0.0  # fallback if the value is missing, invalid, or empty

    if smart_filter_checkbox:
        df = do_smart_filtering(df, df_settings)

    df = get_vmg(df, twd)
    df = get_twa(df, twd)
    html_map = get_map(df, twd=twd)

    timeline_plot = get_timeline_plot(df)
    upwind_vmgsog_plot = get_upwind_vmgsog_plot(df)
    upwind_vgmtwa_plot = get_upwind_vmgtwa_plot(df)
    downwind_vmgsog_plot = get_downwind_vmgsog_plot(df)
    downwind_vmgtwa_plot = get_downwind_vmgtwa_plot(df)
    polar_plot = get_polar_plot(df)

    return (
        twd,
        df,
        html_map,
        timeline_plot,
        upwind_vmgsog_plot,
        upwind_vgmtwa_plot,
        downwind_vmgsog_plot,
        downwind_vmgtwa_plot,
        polar_plot,
    )


def calculate_twd_event(
    port_start,
    port_end,
    starboard_start,
    starboard_end,
    df,
    df_settings,
    twd=0,
    smart_filter_checkbox=False,
):
    print("hello")
    twd = get_twd(df, port_start, port_end, starboard_start, starboard_end)
    calculate_event_outputs = calculate_event(
        df, df_settings, twd=twd, smart_filter_checkbox=True
    )

    return calculate_event_outputs


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


# Auxiliary function for callback, which returns de indices that the user selected in the timeline plot
def timeline_rescale_event(
    select: gr.SelectData,
):
    print("Timeline rescale indices selected")
    print(select.index[0])
    return [(select.index[0]), (select.index[1])]


# Crops the dataframe
def dataframe_rescale_event(df, track_start_unix, track_end_unix, twd=0):
    print("Befire")
    print(df["Time"])
    print(df.dtypes)
    # Make sure Time is parsed as datetime with timezone, needed because otherwise it's read as string
    print("After")
    print(df["Time"])
    print(df.dtypes)

    # 2. Convert Unix timestamps to timezone-aware datetime
    track_start = track_start_unix
    track_end = track_end_unix  # example end time

    # 3. Crop the dataframe
    df = df[
        (df["Elapsed_time"] >= track_start) & (df["Elapsed_time"] <= track_end)
    ].reset_index(drop=True)

    map_output = get_map(df, start_index=0, end_index=None, twd=0)
    timeline_plot = get_timeline_plot(df)

    return df, map_output, timeline_plot


def reset_data_event(df_full):
    df_select = df_full
    html_map = get_map(df_select, twd=0)
    timeline_plot = get_timeline_plot(df_select)
    return df_select, html_map, timeline_plot
