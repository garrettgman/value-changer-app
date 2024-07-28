# app.py
import pandas as pd

from shiny import reactive
from shiny.express import input, render, ui
from shiny.types import FileInfo

# Upload a dataset
ui.input_file("file", "Choose CSV File", accept=[".csv"], multiple=False)

ui.input_text("value", "Missing value symbol", value="NaN")

@reactive.calc
def parsed_data():
    file: list[FileInfo] | None = input.file()
    if file is None:
        return pd.DataFrame()
    return pd.read_csv(file[0]["datapath"])

# Filter to rows of interest
@reactive.calc
def filtered_data():
    df = parsed_data()
    filtered_df = df[df.map(lambda x: x == input.value()).any(axis=1)]
    return filtered_df

# Display data in editable table
@render.data_frame
def data():
    return render.DataGrid(filtered_data(), editable=True)

# Add logic
@data.set_patch_fn
def upgrade_patch(*, patch,):
    orig_data = data.data()
    orig_value = orig_data.iloc[
        patch["row_index"], 
        patch["column_index"]
    ]
    if orig_value == input.value():
        return patch["value"]
    else:
        ui.notification_show(
            f"You can only edit cells that contain the missing value {input.value()}.",
            type="error",
        )
        return orig_value


# Download the finished data
@render.download(label="Download", filename="updated-data.csv")
def download():
    yield data.data_view().to_csv(index=False)