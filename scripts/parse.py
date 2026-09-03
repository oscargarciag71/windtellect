import io
import pandas as pd
import gpxpy


# Function to parse GPX file and convert it to a DataFrame
def gpx_to_dataframe(gpx_file):
    # If gpx_file is a string, it is the file path
    if isinstance(gpx_file, str):
        with open(gpx_file, "rb") as file:
            gpx_content = file.read()
    else:
        # Access the raw file content from the NamedString object
        gpx_content = gpx_file["data"]  # Correctly access the file's binary data

    # Convert the binary content into a file-like object
    gpx_io = io.BytesIO(gpx_content)  # Create a file-like object from the content

    # Parse the GPX content
    try:
        gpx = gpxpy.parse(gpx_io)
    except gpxpy.gpx.GPXXMLSyntaxException as e:
        return f"Error parsing GPX file: {e}"

    # Initialize empty lists to hold the data
    latitudes = []
    longitudes = []
    times = []

    prev_lat, prev_lon = None, None  # Track previous latitude and longitude
    flag = False

    # Extract data from the GPX track
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                # Only add the point if it's different from the previous one

                if flag:
                    flag = False
                    continue

                if (point.latitude, point.longitude) != (prev_lat, prev_lon):
                    latitudes.append(point.latitude)
                    longitudes.append(point.longitude)
                    times.append(point.time)
                    prev_lat = point.latitude
                    prev_lon = point.longitude
                    prev_time = point.time

                else:
                    flag = True
                    latitudes.pop()
                    longitudes.pop()
                    times.pop()

    # Create a DataFrame
    df = pd.DataFrame(
        {
            "latitude": latitudes,
            "longitude": longitudes,
            "Time": times,
        }
    )

    start_time = df["Time"].iloc[0]
    # Convert to minutes from start
    df["Elapsed_time"] = (df["Time"] - start_time).dt.total_seconds() / 60

    return df
