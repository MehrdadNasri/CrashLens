from pathlib import Path
import pandas as pd
from pyproj import Transformer

# Read the original CSV. Asked AI assistant to resolve the file path.
data_folder = Path(__file__).resolve().parents[2] / "Data" / "Seattle_City_Crash_Data"
input_file = f"{data_folder}/SDOT_Collisions_All_Years_1_219605877446562784.zip"
df = pd.read_csv(input_file, dtype=str)


# Drop the columns we don't need.
df = df.drop(columns=[
    "OBJECTID", "SE_ANNO_CAD_DATA", "COLDETKEY", "REPORTNO",
    "INTKEY", "EXCEPTRSNCODE", "EXCEPTRSNDESC", "INCDATE",
    "DIAGRAMLINK", "REPORTLINK", "PEDROWNOTGRNT", "SDOTCOLNUM",
    "SPEEDING", "SEGLANEKEY", "CROSSWALKKEY", "HITPARKEDCAR",
    "SPDCASENO", "Added date", "Modified date",
    "SHAREDMICROMOBILITYCD", "SHAREDMICROMOBILITYDESC",
    "ADDR_SEGINTKEY", "ALLEY"
])

# Split INCDTTM into a date and a time. Asked AI assistant to help with converting the date into day of the week.
parts = df["INCDTTM"].str.split(n=1, expand=True)
dates = pd.to_datetime(parts[0], format="%m/%d/%Y")

df["crash_date"] = dates.dt.strftime("%Y-%m-%d")
df["crash_time"] = parts[1].fillna("N/A")
df["crash_day"] = dates.dt.day_name()

# Convert the original coordinates to longitude and latitude.
x = pd.to_numeric(df["x"])
y = pd.to_numeric(df["y"])

converter = Transformer.from_crs("EPSG:2926", "EPSG:4326", always_xy=True)
longitude, latitude = converter.transform(x.to_numpy(), y.to_numpy())

df["x"] = longitude.round(8)
df["y"] = latitude.round(8)

# Save the cleaned CSV. 
output_file = Path(__file__).resolve().parent / "Seattle_Crashes_Cleaned.csv"
df.to_csv(output_file, index=False)

