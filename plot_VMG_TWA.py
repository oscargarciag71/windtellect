import os
import glob
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

data_folder = "tests/3_Junio_2025"  # <-- change this to your folder name or path


def load_and_combine_files(patterns):
    all_data = []
    for pattern in patterns:
        full_pattern = os.path.join(data_folder, pattern)  # Include folder path
        for file in glob.glob(full_pattern):
            try:
                df = pd.read_csv(file, sep="\t")
                df["source_file"] = os.path.basename(file)
                if "CH" in os.path.basename(file):
                    df["source_type"] = "Chubanga"
                elif "FS" in os.path.basename(file):
                    df["source_type"] = "Flying Sardine"
                else:
                    df["source_type"] = "Unknown"
                all_data.append(df)
            except Exception as e:
                print(f"Error reading {file}: {e}")
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return None


def filter_outliers(df):
    # Remove rows with |TWA| > 50 or VMG < 13.5
    return df[(abs(df["TWA"]) < 50.5)]


def plot_data_with_stats(df, title):
    # Filter outliers before stats
    df_filtered = filter_outliers(df)

    # Calculate mean and std
    stats = (
        df_filtered.groupby("source_type")
        .agg(
            mean_TWA=("TWA", "mean"),
            std_TWA=("TWA", "std"),
            mean_VMG=("VMG", "mean"),
            std_VMG=("VMG", "std"),
        )
        .reset_index()
    )

    # Base scatter plot with all points (including outliers)
    fig = px.scatter(
        df_filtered,
        x="TWA",
        y="VMG",
        color="source_type",
        title=title,
        labels={
            "TWA": "True Wind Angle (TWA) (º)",
            "VMG": "Velocity Made Good (VMG) (kt)",
        },
        category_orders={"source_type": ["Flying Sardine", "Chubanga"]},
    )

    # Compose the stats text to show on plot
    annotation_texts = []
    y_pos = df_filtered["VMG"].max() * 0.95  # Start near top
    x_pos = df_filtered["TWA"].max()  # Right side of plot (accounting for negative TWA)
    y_gap = (
        df_filtered["VMG"].max() - df_filtered["VMG"].min()
    ) * 0.06  # Gap between text blocks

    for i, row in stats.iterrows():
        text = (
            f"{row['source_type']} stats:<br>"
            f"Mean TWA: {row['mean_TWA']:.2f}º ± {row['std_TWA']:.2f}º <br>"
            f"Mean VMG: {row['mean_VMG']:.2f} kt ± {row['std_VMG']:.2f} kt"
        )
        annotation_texts.append(
            (x_pos, y_pos - i * y_gap * 3, text)
        )  # leave vertical space

    # Add annotations
    for x, y, text in annotation_texts:
        fig.add_annotation(
            x=x,
            y=y,
            text=text,
            showarrow=False,
            align="left",
            bgcolor="white",
            bordercolor="black",
            borderwidth=1,
            font=dict(size=12),
            xanchor="left",
            yanchor="top",
        )

    fig.show()


# Patterns
# Updated patterns to match CH/FS with any digit and up/down in filename
port_patterns = [
    "FS*_up_port*.txt",
    "FS*_down_port*.txt",
    "CH*_up_port*.txt",
    "CH*_down_port*.txt",
]
starboard_patterns = [
    "FS*_up_starboard*.txt",
    "FS*_down_starboard*.txt",
    "CH*_up_starboard*.txt",
    "CH*_down_starboard*.txt",
]


# Load
port_df = load_and_combine_files(port_patterns)
starboard_df = load_and_combine_files(starboard_patterns)

# Plot port
if port_df is not None:
    plot_data_with_stats(port_df, "Upwind - Port")
else:
    print("No matching port files found.")

# Plot starboard
if starboard_df is not None:
    plot_data_with_stats(starboard_df, "Upwind - Starboard")
else:
    print("No matching starboard files found.")
