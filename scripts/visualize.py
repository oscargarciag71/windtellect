import folium
import gradio as gr
import plotly.express as px
from branca.colormap import linear
import plotly.graph_objects as go


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
    # df["Time"] = df.index.tolist()
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


def get_polar_plot_2(df):
    df = df.sort_values(by="TWA")
    fig = px.line_polar(df, r="SOG", theta="TWA", title="Sailing Polar Plot")
    return fig


def get_polar_plot_3(df):
    print("Making polar plot")
    closed_r = df["SOG"].tolist() + [df["SOG"].iloc[0]]
    closed_theta = df["TWA"].tolist() + [df["TWA"].iloc[0]]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=closed_r,
            theta=closed_theta,
            mode="markers",
            line=dict(color="orange"),
        )
    )

    fig.update_layout(
        title="Polar Plot",
        polar=dict(
            radialaxis=dict(visible=True),
            angularaxis=dict(rotation=90),  # Optional: rotate starting angle
        ),
        showlegend=False,
    )
    print("hell2")
    return fig


import plotly.graph_objects as go


def get_polar_plot(df):
    print("Making polar plot")
    closed_r = df["SOG"].tolist() + [df["SOG"].iloc[0]]
    closed_theta = df["TWA"].tolist() + [df["TWA"].iloc[0]]

    fig = go.Figure()

    # Scatterpolar plot with improved styling
    fig.add_trace(
        go.Scatterpolar(
            r=closed_r,
            theta=closed_theta,
            mode="markers",  # Only markers, no lines
            marker=dict(
                color="orange",  # Marker color
                size=10,  # Marker size
                line=dict(width=2, color="black"),  # Border around markers
            ),
        )
    )

    # Update layout for better appearance
    fig.update_layout(
        title="Sailing Polar Plot",
        title_x=0.5,  # Center title
        title_font=dict(size=24, color="darkblue", family="Arial"),  # Title styling
        polar=dict(
            radialaxis=dict(
                visible=True,
                showticklabels=True,
                ticks="outside",
                ticklen=10,
                tickwidth=2,
                tickcolor="grey",  # Customize radial axis ticks
            ),
            angularaxis=dict(
                rotation=90,  # Start angle at 90 degrees
                direction="clockwise",  # Rotate direction
                tickmode="array",  # Use array for specific ticks
                tickvals=[0, 90, 180, 270],  # Show only the cardinal directions
                ticktext=["0°", "90°", "180°", "270°"],  # Custom angular ticks
                showticklabels=True,
                ticks="outside",
                ticklen=10,
                tickwidth=2,
                tickcolor="grey",  # Customize angular axis ticks
            ),
        ),
        showlegend=False,  # Hide the legend
        plot_bgcolor="white",  # Set background to white for a clean look
        margin=dict(t=50, b=50, l=50, r=50),  # Adjust margins for better spacing
        height=600,  # Set a fixed height for the plot
        width=600,  # Set a fixed width for the plot
    )

    print("Finished polar plot")
    return fig
