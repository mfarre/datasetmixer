import os
import json
import random
import tarfile
from collections import defaultdict

# Set random seed for reproducibility
random.seed(42)

# Path to the summary.json file
summary_path = "aggregated_summary.json"

# Output folders
output_folders = {
    "text": "/fsx/miquel/longvu-dataset/expansion/text",
    "images": "/fsx/miquel/longvu-dataset/expansion/images",
}

# Create output directories if they don't exist
for folder in output_folders.values():
    os.makedirs(folder, exist_ok=True)

# Target counts
target_counts = {
    "only_text": 256000,
    "multi_image": 295112,
    "single_image": 586667,
}

# Load the summary
with open(summary_path, "r") as f:
    summary = json.load(f)

file_data = summary["file_data"]

# Normalize paths in file_data
for uuid, data in file_data.items():
    data["texts"] = [os.path.normpath(text.lstrip("./")) for text in data["texts"]]
    data["metadata"] = os.path.normpath(data["metadata"].lstrip("./"))
    data["origin_tar"] = os.path.normpath(data["origin_tar"])

# Shuffle and select cases
selected_cases = {
    "only_text": [],
    "multi_image": [],
    "single_image": [],
}

for case_type in selected_cases.keys():
    if case_type == "only_text":
        cases = [k for k, v in file_data.items() if v["images"] == 0 and v["texts"]]
    elif case_type == "multi_image":
        cases = [k for k, v in file_data.items() if v["images"] > 1 and v["texts"]]
    elif case_type == "single_image":
        cases = [k for k, v in file_data.items() if v["images"] == 1 and v["texts"]]
    else:
        continue

    random.shuffle(cases)
    selected_cases[case_type] = cases[:target_counts[case_type]]
    print(f"Case: {case_type} items: {len(selected_cases[case_type])}")

# Organize selected cases by tar file to minimize tar openings
cases_by_tar = defaultdict(lambda: defaultdict(list))
for case_type, cases in selected_cases.items():
    for case in cases:
        tar_name = file_data[case]["origin_tar"]
        cases_by_tar[tar_name][case_type].append(case)
        # print(f"{tar_name}:{case_type}:{case}")

# Function to extract specific files from tar
def extract_files_from_tar(tar, file_names, output_folder):
    tar_files = {member.name: member for member in tar.getmembers()}
    for file_name in file_names:
        # Ensure file matches exactly
        if file_name in tar_files:
            tar.extract(tar_files[file_name], path=output_folder)
        else:
            print(f"\tERROR: {file_name} not found in tar.")

output_summary = []
# Process cases by tar file
for tar_name, cases in cases_by_tar.items():
    print(f"Parsing {tar_name}")
    tar_path = os.path.join(".", tar_name)
    with tarfile.open(tar_path, "r") as tar:
        tar_files = [member.name for member in tar.getmembers()]  # List all files in tar
        for case_type, case_ids in cases.items():
            for case in case_ids:
                data = file_data[case]
                metadata_file = data["metadata"]

                # Match exact path in tar
                if metadata_file not in tar_files:
                    if f"./{metadata_file}" in tar_files:
                        metadata_file = f"./{metadata_file}"
                    else:
                        print(f"ERROR: Metadata file {metadata_file} not found in tar {tar_name}")
                        continue

                metadata_path = os.path.join("/tmp/metadata", os.path.basename(metadata_file))

                # Extract metadata file
                tar.extract(metadata_file, path="/tmp/metadata")

                # Read metadata to identify files
                with open(metadata_path, "r") as f:
                    file_list = f.read().strip().splitlines()

                # Normalize paths in file_list
                file_list = [os.path.normpath(file.lstrip("./")) for file in file_list]

                # Extract all text files to the text folder
                text_files = ['./' + f for f in file_list if f.endswith(".text.txt")]
                extract_files_from_tar(tar, text_files, output_folders["text"])

                # For "only_text" cases
                if case_type == "only_text":
                    for text_file in text_files:
                        output_summary.append({
                            "text_file": os.path.join(output_folders["text"], os.path.basename(text_file)),
                            "images": None,
                            "source": data.get("source", "unknown"),
                            "type": "only_text",
                        })

                # For "multi_image" cases
                elif case_type == "multi_image":
                    image_files = ['./' + f for f in file_list if f.endswith(".image.jpeg")]
                    if image_files:
                        uuid_folder = os.path.join(output_folders["images"], case)
                        os.makedirs(uuid_folder, exist_ok=True)
                        extract_files_from_tar(tar, image_files, uuid_folder)
                        selected_text = random.choice(text_files)
                        output_summary.append({
                            "text_file": os.path.join(output_folders["text"], os.path.basename(selected_text)),
                            "images": os.path.join(output_folders["images"], case),
                            "source": data.get("source", "unknown"),
                            "type": "multi_image",
                        })

                # For "single_image" cases
                elif case_type == "single_image":
                    image_files = ['./' + f for f in file_list if f.endswith(".image.jpeg")]
                    if len(image_files) == 1:
                        extract_files_from_tar(tar, image_files, output_folders["images"])
                        selected_text = random.choice(text_files)
                        output_summary.append({
                            "text_file": os.path.join(output_folders["text"], os.path.basename(selected_text)),
                            "images": os.path.join(output_folders["images"], os.path.basename(image_files[0])),
                            "source": data.get("source", "unknown"),
                            "type": "single_image",
                        })
                    else:
                        print("\t Error: more than one image ")

# Save the output summary as JSON
output_summary_path = "summary_output.json"
with open(output_summary_path, "w") as f:
    json.dump(output_summary, f, indent=4)

print(f"Files have been organized into the respective folders and summary saved to {output_summary_path}.")
