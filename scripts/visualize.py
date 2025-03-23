import folium
import gradio as gr
from branca.colormap import linear


def map(df, start_index=0, end_index=None, twd=0):
    # Default to full DataFrame if end_index is not provided
    end_index = end_index or len(df)
    df_subset = df[start_index : end_index + 1]

    # Create base map centered at the first point of the subset
    m = folium.Map(
        location=[df_subset["latitude"].mean(), df_subset["longitude"].mean()],
        zoom_start=15,
        width="100%",  # Width of the map
        height="400px",
    )  # Height of the map)

    # Define color scale based on speed (corrected)
    colormap = linear.YlGnBu_09.scale(df["SOG"].min(), df["SOG"].max())
    colormap.caption = "SOG (knots)"
    m.add_child(colormap)

    for row in df_subset.itertuples(index=True):
        if row.Index == start_index:  # Get first coordinates
            prev_lat, prev_lon = row.latitude, row.longitude
            continue

        # Add track when there is or there isn't a defined wind direction
        if twd == 0:
            map_tooltip = f"""
                    <div style="font-size: 16px; color: black;">
                        Index: {start_index + row.Index}<br>
                        SOG: {row.SOG:.2f} knots<br>
                        COG: {row.COG:.1f}°<br>
                    </div>
                """
        else:
            map_tooltip = f"""
                    <div style="font-size: 16px; color: black;">
                        Index: {start_index + row.Index}<br>
                        SOG: {row.SOG:.2f} knots<br>
                        COG: {row.COG:.1f}°<br>
                        VMG: {row.VMG:.2f} knots<br>
                        TWA: {row.TWA:.2f}°<br>
                    </div>
                """

        folium.PolyLine(
            locations=[[prev_lat, prev_lon], [row.latitude, row.longitude]],
            color=colormap(row.SOG),
            weight=5,
            tooltip=map_tooltip,
        ).add_to(m)

        prev_lat, prev_lon = row.latitude, row.longitude  # Update previous coordinates

    if twd != 0:
        # Add Wind Direction Arrow
        arrow_icon = folium.DivIcon(
            html=f'<div style="font-size: 100px; color: #FF8D33; transform: rotate({twd}deg);">&#8595;</div>'
        )

        # Place the arrow at a specific point, e.g., at the starting point of the track (first position)
        folium.Marker(
            location=[max(df_subset["latitude"]), max(df_subset["longitude"])],
            icon=arrow_icon,
            popup=f"Wind Direction: {twd}°",
        ).add_to(m)

    # Return the map as HTML
    return m._repr_html_()


def plot_column_by_time(df, x_col, y_columns, y_lim=None, height=None):
    # Prepare data for Gradio LinePlot (stacked format)
    # plot_data = df.melt(id_vars=[col_x], value_vars=col_y_list, var_name="Metric", value_name="Value")
    df["Time"] = df.index.tolist()
    plot_data = df.melt(
        id_vars=[x_col], value_vars=y_columns, var_name="Metric", value_name="Value"
    )

    line_plot = gr.LinePlot(
        plot_data,
        x=x_col,
        y="Value",
        y_title=f"{', '.join(y_columns)}",
        x_label=False,
        y_lim=y_lim,
        height=height,
        container=False,
    )

    return line_plot
