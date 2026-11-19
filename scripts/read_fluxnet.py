import zipfile
import re
from pathlib import Path
import pandas as pd

keep = [
	"TIMESTAMP_START", "TIMESTAMP_END",
	"TA_F", "SW_IN_F", "VPD_F", "P_F",
	"NETRAD", "G_F_MDS",
	"H_F_MDS", "H_F_MDS_QC",
	"LE_F_MDS", "LE_F_MDS_QC",
	"NEE_VUT_REF", "NEE_VUT_REF_QC",
	"GPP_NT_VUT_REF", "RECO_NT_VUT_REF"
]


def read_hh(zip_file):
	zip_file = Path(zip_file)

	match = re.search(r"_([A-Z]{2}-[^_]+)_FLUXNET_", zip_file.name)
	if match is None:
		raise ValueError(f"Could not identify site ID in {zip_file.name}")

	site = match.group(1)

	with zipfile.ZipFile(zip_file) as z:
		hh_name = [
			name for name in z.namelist()
			if "FLUXMET_HH" in name and name.endswith(".csv")
		][0]

		with z.open(hh_name) as f:
			hh = pd.read_csv(
				f,
				na_values=[-9999],
				usecols=lambda column: column in keep,
				dtype={
					"TIMESTAMP_START": str,
					"TIMESTAMP_END": str
				}
			)

	hh["time"] = pd.to_datetime(
		hh["TIMESTAMP_START"],
		format="%Y%m%d%H%M"
	)

	hh["site"] = site

	return hh


# Read all five FLUXNET towers
project_dir = Path(__file__).resolve().parent.parent
zip_files = sorted((project_dir / "data" / "raw").glob("*.zip"))

all_towers = pd.concat(
	[read_hh(zip_file) for zip_file in zip_files],
	ignore_index=True
)

# Check the combined dataset
print("Total rows:", len(all_towers))
print("\nRows per site:")
print(all_towers["site"].value_counts())
