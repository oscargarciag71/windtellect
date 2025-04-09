# - IMPORTS
import gradio as gr
import pandas as pd
from scripts.visualize import map
from scripts.wrappers import (
    calculate_event,
    maneuver_event,
    settings_event,
    upload_event,
)
# --

# -- MAKE WINDTELLECT LOGO
with open("logo_windtellect.txt", "r") as file:
    image_base64 = file.read().strip()
windtellect_logo_html = f"""
<style>
  #logo-container {{
    position: fixed;
    top: 10px;
    left: 10px;
    z-index: 1000;
  }}
  #logo-container img {{
    width: 120px;
    height: auto;
  }}
</style>
<div id="logo-container">
    <img src="data:image/png;base64,{image_base64}">
</div>
"""
# --

css = """
.tooltip {
    position: relative;
    display: inline-block;
    cursor: pointer;
    font-size: 20px;
}

.tooltip .tooltip-text {
    visibility: hidden;
    width: 160px;
    background-color: black;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 5px;
    position: absolute;
    z-index: 1;
    bottom: 100%; /* Position above */
    left: 50%;
    transform: translateX(-50%);
    opacity: 0;
    transition: opacity 0.3s ease-in-out;
}

.tooltip:hover .tooltip-text {
    visibility: visible;
    opacity: 1;
}
"""

css_style_logo = """
#logo-container {
    position: absolute;
    top: 10px;
    left: 10px;
    z-index: 1000;
}

#logo-container img {
    height: 5px;  /* Adjust size as needed */
    width: auto;
    pointer-events: none; /* Prevent clicking */
}
"""

css_style_1 = """
body {
    overflow: hidden !important;  /* Prevents page scrolling */
}

#map-container { 
    height: 450px !important;  /* Set a fixed height */
}
"""

css_style_2 = """
#map-container { 
    width: 100% !important; /* Ensures full width */
    height: 420px !important; /* Fixed height */
    max-width: 100vw; /* Prevents overflow */
}
"""

df_settings = pd.DataFrame(
    {
        "min_upwind_sog": [5],
        "max_upwind_sog": [35],
        "min_downwind_sog": [5],
        "max_downwind_sog": [36],
        "min_upwind_twa": [25],
        "max_upwind_twa": [60],
        "min_downwind_twa": [120],
        "max_downwind_twa": [120],
        "min_vmg": [8],
    }
)

# - GRADIO LAYOUT
with gr.Blocks(css=css_style_2) as demo:
    # Load Windtellect logo
    gr.HTML(windtellect_logo_html)

    # Create dataframe
    dataframe = gr.Dataframe(visible=False, datatype="pandas")

    # Sidebar for setting wind direction
    with gr.Sidebar(position="right"):
        track_start = gr.Number(label="Start Point", visible=False)
        track_end = gr.Number(label="End Point", visible=False)
        twd = gr.Number(label="Wind direction")
        set_twd_button = gr.Button("Set TWD")

        with gr.Accordion("🧭 Wind Direction Calculator", open=False):
            # Starboard Section
            gr.Markdown("**Starboard**")  # Title in a separate row
            starboard_start = gr.Number(label="Start Point")
            starboard_end = gr.Number(label="End Point")

            # Port Section
            gr.Markdown("**Port**")  # Title in a separate row
            port_start = gr.Number(label="Start Point")
            port_end = gr.Number(label="End Point")

            calculate_twd_button = gr.Button("Calculate TWD")

    # Tab for track visualization
    with gr.Tab("🌍 Track Visualization"):
        with gr.Column():
            with gr.Row(scale=1):
                file_input = gr.File(label="Upload your GPX file here!")
            with gr.Row(scale=10):
                map_output = gr.HTML(
                    elem_id="map-container"
                )  # Assign a custom ID for styling
            with gr.Row(scale=1):
                speed_by_time = gr.LinePlot()

    # Tab for data analysis
    with gr.Tab("📈 Data Analysis"):
        with gr.Row():
            with gr.Column(scale=5):
                gr.Markdown("### Find your optimal🤙")
                # speed_by_time = gr.LinePlot()
                gr.Markdown(
                    "Manualy set or calculate the wind direction in the right side bar ➡️ to see stats about VMG and TWA"
                )
            with gr.Column(scale=1):
                refresh_button = gr.Button("🔄 Refresh data")

        gr.Markdown("#### Upwind data")
        with gr.Row():
            with gr.Column():
                plot_1_up = gr.LinePlot()
            with gr.Column():
                plot_2_up = gr.LinePlot()

        gr.Markdown("#### Downwind data")
        with gr.Row():
            with gr.Column():
                plot_1_down = gr.LinePlot()
            with gr.Column():
                plot_2_down = gr.LinePlot()

        gr.Markdown("## Sailing Polar Plot")
        with gr.Row():
            polar_plot = gr.Plot()

    # Tab for maneuver analysis
    with gr.Tab("⛵ Maneuver Analysis"):
        gr.Markdown("## tick tack")
        calculate_maneuver_button = gr.Button("Calculate maneuvers")
        with gr.Row():
            with gr.Column(scale=1):
                df_maneuver = gr.Dataframe(visible=False)
                # Checkboxes in a column
                checkboxes = []
                with gr.Row():  # Align table with checkboxes
                    with gr.Column():
                        gr.Markdown("### Select Rows:")
                        for i in range(df_maneuver.row_count[0]):
                            checkboxes.append(gr.Checkbox(label=f"Maneuver {i}"))
            with gr.Column(scale=3):
                text = gr.Text()
                maneuver_map_output = gr.HTML(elem_id="map-container")

    # Tab for settings
    with gr.Tab("⚙️ Advanced settings"):
        gr.Markdown("## set set set")
        set_dataframe = gr.Dataframe(df_settings, visible=False)
        with gr.Row():
            with gr.Column():
                min_upwind_sog = gr.Number(
                    label="Minimum upwind boat SOG",
                    value=df_settings["min_upwind_sog"][0],
                )
                max_upwind_sog = gr.Number(
                    label="Maximum upwind boat SOG",
                    value=df_settings["max_upwind_sog"][0],
                )
                min_downwind_sog = gr.Number(
                    label="Minimum downwind boat SOG",
                    value=df_settings["min_downwind_sog"][0],
                )
                max_downwind_sog = gr.Number(
                    label="Maximum downwind boat SOG",
                    value=df_settings["max_downwind_sog"][0],
                )
            with gr.Column():
                min_upwind_twa = gr.Number(
                    label="Minimum upwind TWA", value=df_settings["min_upwind_twa"][0]
                )
                max_upwind_twa = gr.Number(
                    label="Maximum upwind TWA", value=df_settings["max_upwind_twa"][0]
                )
                min_downwind_twa = gr.Number(
                    label="Minimum downwind TWA",
                    value=df_settings["min_downwind_twa"][0],
                )
                max_downwind_twa = gr.Number(
                    label="Maximum downwind TWA",
                    value=df_settings["max_downwind_twa"][0],
                )
            with gr.Column():
                min_vmg = gr.Number(
                    label="Minimum VMG", value=df_settings["min_vmg"][0]
                )
        set_settings_button = gr.Button("Set settings")

        smart_filter_checkbox = gr.Checkbox(label="Enable smart filtering")

    # Select time frame from speed by time plot
    time_graphs = [speed_by_time]  # , plot_1, plot_2]

    def rescale(select: gr.SelectData):
        print(round(select.index[0]), type(select.index[0]))
        return [round(select.index[0]), round(select.index[1])]

    rescale_evt = gr.on(
        [plot.select for plot in time_graphs], rescale, None, [track_start, track_end]
    )

    # EVENT-TRIGGERED CALLBACKS:
    # To improve code readibility, we define "calculate_event_inputs" and "calculate_event_outputs"
    calculate_event_inputs = [
        dataframe,
        set_dataframe,
        port_start,
        port_end,
        starboard_start,
        starboard_end,
        set_dataframe,
        twd,
        smart_filter_checkbox,
    ]
    calculate_event_outputs = [
        twd,
        dataframe,
        map_output,
        plot_1_up,
        plot_2_up,
        plot_1_down,
        plot_2_down,
        polar_plot,
    ]

    # Triggering when uploading new file -> parses gpx, calculates SOG and COG and plots
    file_input.change(
        upload_event,
        inputs=file_input,
        outputs=[dataframe, map_output, speed_by_time],
    )
    # Triggering when clicking the TWD calculator -> calculates TWD, VMG and TWA and plots
    calculate_twd_button.click(
        calculate_event,
        inputs=calculate_event_inputs,
        outputs=calculate_event_outputs,
    )

    # Triggering when user manually updates wind direction -> calculates TWD, VMG and TWA and plots
    set_twd_button.click(
        calculate_event,
        inputs=calculate_event_inputs,
        outputs=calculate_event_outputs,
    )

    # Triggering when "Refresh data" in Data Analysis tab is clicked -> calculates TWD, VMG and TWA and plots
    refresh_button.click(
        calculate_event,
        inputs=calculate_event_inputs,
        outputs=calculate_event_outputs,
    )

    # Sets custom user settings in the "Advanced settings" tab
    set_settings_button.click(
        settings_event,
        inputs=[
            min_upwind_sog,
            max_upwind_sog,
            min_downwind_sog,
            max_downwind_sog,
            min_upwind_twa,
            max_upwind_twa,
            min_downwind_twa,
            max_downwind_twa,
            min_vmg,
        ],
        outputs=[set_dataframe],
    )

    # When settings change also recalculate data -> calculates TWD, VMG and TWA and plots
    set_dataframe.change(
        calculate_event,
        inputs=calculate_event_inputs,
        outputs=calculate_event_outputs,
    )

    # When enabling smart filtering recalculate data -> calculates TWD, VMG and TWA and plots
    smart_filter_checkbox.change(
        calculate_event,
        inputs=calculate_event_inputs,
        outputs=calculate_event_outputs,
    )

    # Calculate maneuvers
    calculate_maneuver_button.click(
        maneuver_event,
        inputs=[dataframe, twd],
        outputs=[df_maneuver],  # , checkbox_container],  # , maneuver_map_output]
    )

    # Triggering when changing the track start or end -> plot
    track_start.change(
        map, inputs=[dataframe, track_start, track_end, twd], outputs=map_output
    )
    track_end.change(
        map, inputs=[dataframe, track_start, track_end, twd], outputs=map_output
    )
    # --

if __name__ == "__main__":
    demo.launch()

    def update_checkboxes(df):
        # Get the row count of the dataframe
        row_count = len(df)

        # Create a list to store the checkboxes dynamically
        checkboxes = []

        for i in range(row_count):
            checkboxes.append(gr.Checkbox(label=f"Maneuver {i}"))

        # Return the list of checkboxes to be displayed
        return checkboxes

    # Trigger the update_checkboxes function whenever the dataframe is updated
    df_maneuver.change(fn=update_checkboxes, inputs=df_maneuver, outputs=checkboxes)

    def show_one_maneuver(board, dataframe, twd, evt: gr.SelectData):
        if evt.value:
            # print(evt.value)
            maneuver_id = board["maneuver_id"][evt.value - 1]
            maneuver_start = board["start_index"][maneuver_id - 1]
            maneuver_end = board["end_index"][maneuver_id - 1]

            # print(maneuver_id, maneuver_start, maneuver_end)

            html_map = map(
                dataframe, start_index=maneuver_start, end_index=maneuver_end, twd=twd
            )

        return f"{maneuver_id}", html_map

    df_maneuver.select(
        show_one_maneuver,
        [df_maneuver, dataframe, twd],
        [text, maneuver_map_output],
        show_progress="hidden",
    )
