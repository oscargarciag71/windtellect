import numpy as np
import pandas as pd
from geopy.distance import geodesic


def get_sog_cog(df):
    sogs = [0.0]  # First point has no speed
    cogs = [0.0]  # First point has no heading

    for row in df.itertuples(index=True):
        i = row.Index
        curr_point = (row.latitude, row.longitude)
        curr_time = row.Time

        # Skip the first index to start with the second datapoint
        if i == 0:
            prev_point, prev_time = curr_point, curr_time
            continue

        # Calculate time difference
        time_diff = (curr_time - prev_time).total_seconds() / 3600.0  # In hours

        # Calculate distance difference
        distance_diff = geodesic(prev_point, curr_point).nm  # In nautical miles

        # Calculate SOG
        sog = distance_diff / time_diff if time_diff > 0 else 0  # In knots

        # Calculate COG using arctan2 formula
        lat1, lon1 = np.radians(prev_point)
        lat2, lon2 = np.radians(curr_point)
        delta_lon = lon2 - lon1
        x = np.sin(delta_lon) * np.cos(lat2)
        y = np.cos(lat1) * np.sin(lat2) - (
            np.sin(lat1) * np.cos(lat2) * np.cos(delta_lon)
        )
        cog = (np.degrees(np.arctan2(x, y)) + 360) % 360  # Normalize heading

        # Update values and append
        prev_point, prev_time = curr_point, curr_time
        sogs.append(sog)
        cogs.append(cog)

    df["SOG"] = sogs
    df["COG"] = cogs

    print("SOG and COG calculated")

    return df


def do_smart_filtering(df, df_settings):
    # Remove first 5 datapoints
    df = df.iloc[5:].reset_index(drop=True)
    print(df_settings)
    # Remove points where SOG is larger than maximum boat SOG
    maxSOG = float(df_settings["max_downwind_sog"].iloc[0])
    print(maxSOG)
    bad_idxs = df[df["SOG"] > maxSOG].index  # Find indices
    to_remove = set()  # Create set if indices to remove
    for idx in bad_idxs:
        to_remove.update([idx - 1, idx, idx + 1])
    to_remove = [
        i for i in to_remove if 0 <= i < len(df)
    ]  # Make sure we don't go out of DataFrame bounds
    df = df.drop(to_remove).reset_index(drop=True)  # Drop the rows and reset index

    print("Smart filtering done")

    return df


def get_twd(df, port_start, port_end, starboard_start, starboard_end):
    """Calculate True Wind Direction."""
    headings = df["COG"]

    # Extract headings for port and starboard tacks
    port_headings = headings[port_start : port_end + 1]
    starboard_headings = headings[starboard_start : starboard_end + 1]

    # Calculate the mean heading for each tack
    mean_port_heading = np.mean(port_headings)
    mean_starboard_heading = np.mean(starboard_headings)

    # Calculate True Wind Direction (TWD)
    twd = (mean_port_heading + mean_starboard_heading) / 2
    # Correct for heading crossing the 0°/360° threshold
    if abs(mean_port_heading - mean_starboard_heading) > 180:
        twd = (twd + 180) % 360

    print("TWD calculated")

    return twd


def get_vmg(df, twd):
    """Calculate Velocity Made Good (VMG) based on a target direction (e.g., upwind/downwind)."""
    df["VMG"] = df["SOG"] * np.cos(np.radians(df["COG"] - twd))

    print("VMG calculated")

    return df


def get_twa(df, twd=0):
    """Calculate True Wind Angle (TWA) (angle with respect to wind direction, negative = left, positive = right)."""
    df["TWA"] = ((df["COG"] - twd + 180) % 360) - 180

    print("TWA calculated")

    return df


def group_by_maneuvers(new_df):
    maneuver_ids = []
    types = []
    start_indexs = []
    end_indexs = []
    performances = []

    for i, sub_df in new_df.groupby("maneuver_id"):
        first = sub_df.first_valid_index()
        last = sub_df.last_valid_index()

        maneuver_ids.append(i)
        types.append(sub_df["maneuver_type"][first])

        start = sub_df["iii"][first]
        end = sub_df["iii"][last]
        start_indexs.append(start)
        end_indexs.append(end)

        # calculate performance
        vmg_in = sub_df["VMG"][
            first
        ]  # ideally we'd like to do the mean of the first 3 points

        time_in = sub_df["Time"][first]
        time_out = sub_df["Time"][last]

        # Vectorized calculation of point performances (subtract VMG_in from all VMG values)
        point_performances = np.abs(sub_df["VMG"]) - np.abs(vmg_in)

        # Sum the point performances and append
        performances.append(np.sum(point_performances))

    df_maneuvers = pd.DataFrame(
        {
            "maneuver_id": maneuver_ids,
            "type": types,
            "start_index": start_indexs,
            "end_index": end_indexs,
            "performance": performances,
        }
    )

    return df_maneuvers


def maneuver_dataframe(df):
    # Pre-allocated lists to create dataframe
    latitudes, longitudes, times = [], [], []
    sogs, cogs, twas, vmgs = [], [], [], []
    maneuver_ids, maneuver_types = [], []

    # Check if VMG column exists, else exit the function
    if "VMG" not in df.columns:
        return "'ERROR!! You need to set the wind direction first!!!'"

    first_valid_index = df.first_valid_index()


def get_maneuvers(df):
    TWA_LIMIT = 35
    SOG_LIMIT = 4
    WINDOW_SIZE = 8

    maneuver_id = 1

    indexes = []

    # Pre-allocated lists to create dataframe
    latitudes, longitudes, times = [], [], []
    sogs, cogs, twas, vmgs = [], [], [], []
    maneuver_ids, maneuver_types = [], []

    if "VMG" in df.keys():
        first = df.first_valid_index()

        for row in df.itertuples(index=True):
            i = row.Index
            twa = row.TWA
            sog = row.SOG

            if i < first + WINDOW_SIZE:
                previous_twa = twa

            elif sog > SOG_LIMIT:
                is_tack_PS = twa > 0 and previous_twa < 0
                is_tack_SP = twa < 0 and previous_twa > 0

                if is_tack_PS or is_tack_SP:
                    if is_tack_PS:
                        maneuver_type = "Tack Port -> Starboard"
                    else:
                        maneuver_type = "Tack Starboard -> Port"

                    # take previous and later 5 points
                    for j in range(-WINDOW_SIZE, WINDOW_SIZE + 1):
                        if i + j not in indexes:
                            latitudes.append(df["latitude"][i + j])
                            longitudes.append(df["longitude"][i + j])
                            times.append(df["Time"][i + j])
                            sogs.append(df["SOG"][i + j])
                            cogs.append(df["COG"][i + j])
                            twas.append(df["TWA"][i + j])
                            vmgs.append(df["VMG"][i + j])
                            maneuver_ids.append(maneuver_id)
                            maneuver_types.append(maneuver_type)
                            indexes.append(i + j)

                    maneuver_id += 1

            previous_twa = twa

        new_df = pd.DataFrame(
            {
                "latitude": latitudes,
                "longitude": longitudes,
                "Time": times,
                "SOG": sogs,
                "COG": cogs,
                "TWA": twas,
                "VMG": vmgs,
                "maneuver_id": maneuver_ids,
                "maneuver_type": maneuver_types,
                "iii": indexes,
            }
        )

        return new_df

    else:
        return f"'ERROR!! You need to set the wind direction first!!!'"
