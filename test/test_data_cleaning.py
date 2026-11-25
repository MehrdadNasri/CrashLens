from pathlib import Path
import subprocess
import sys

import pandas as pd
import pytest

# AI assistance to design the test
@pytest.fixture
def cleaned_crashes(tmp_path):
    # Make a temporary folder so the test does not change the real CSV.
    repo = Path(__file__).resolve().parents[1]
    original_script = repo / "src" / "crashlens" / "data_cleaning.py"

    script = tmp_path / "src" / "crashlens" / "data_cleaning.py"
    script.parent.mkdir(parents=True)
    script.write_text(original_script.read_text(encoding="utf-8"), encoding="utf-8")

    data_folder = tmp_path / "Data" / "Seattle_City_Crash_Data"
    data_folder.mkdir(parents=True)

    # One crash has coordinates but no time. The other has a time but no coordinates.
    sample = pd.DataFrame({
        "INCKEY": [150000, 1177],
        "SEVERITYCODE": [1, 2],
        "COLLISIONTYPE": ["Rear Ended", "Angles"],
        "STATUS": ["Matched", "Unmatched"],
        "ADDRTYPE": ["Intersection", "Block"],
        "INCDTTM": ["4/29/2013", "3/30/2013 3:23:00 PM"],
        "x": ["1259532.68381456", ""],
        "y": ["209576.355722666", ""],
    })

    # The input needs these columns so the script can drop them.
    unused_columns = [
        "OBJECTID", "SE_ANNO_CAD_DATA", "COLDETKEY", "REPORTNO",
        "INTKEY", "EXCEPTRSNCODE", "EXCEPTRSNDESC", "INCDATE",
        "DIAGRAMLINK", "REPORTLINK", "PEDROWNOTGRNT", "SDOTCOLNUM",
        "SPEEDING", "SEGLANEKEY", "CROSSWALKKEY", "HITPARKEDCAR",
        "SPDCASENO", "Added date", "Modified date",
        "SHAREDMICROMOBILITYCD", "SHAREDMICROMOBILITYDESC",
        "ADDR_SEGINTKEY", "ALLEY",
    ]
    for column in unused_columns:
        sample[column] = ""
    sample["OBJECTID"] = [1, 2]

    # Pandas uses the .zip ending to save the sample as a ZIP file.
    sample.to_csv(data_folder / "SDOT_Collisions_All_Years_1_219605877446562784.zip",
                  index=False)

    # Run the copy with the same Python that is running pytest.
    subprocess.run([sys.executable, str(script)], check=True)
    output_file = script.parent / "Seattle_Crashes_Cleaned.csv"
    return pd.read_csv(output_file, keep_default_na=False)


def test_drops_unused_columns(cleaned_crashes):
    assert cleaned_crashes.columns.tolist() == [
        "INCKEY", "SEVERITYCODE", "COLLISIONTYPE", "STATUS", "ADDRTYPE",
        "INCDTTM", "x", "y", "crash_date", "crash_time", "crash_day",
    ]
    assert cleaned_crashes["INCKEY"].tolist() == [150000, 1177]
    assert cleaned_crashes["SEVERITYCODE"].tolist() == [1, 2]


def test_date_time_and_weekday(cleaned_crashes):
    assert cleaned_crashes["crash_date"].tolist() == ["2013-04-29", "2013-03-30"]
    assert cleaned_crashes["crash_time"].tolist() == ["N/A", "3:23:00 PM"]
    assert cleaned_crashes["crash_day"].tolist() == ["Monday", "Saturday"]


def test_longitude_and_latitude(cleaned_crashes):
    assert float(cleaned_crashes.loc[0, "x"]) == pytest.approx(-122.37620415, abs=0.00002)
    assert float(cleaned_crashes.loc[0, "y"]) == pytest.approx(47.56408227, abs=0.00002)
    assert cleaned_crashes.loc[1, "x"] == ""
    assert cleaned_crashes.loc[1, "y"] == ""
