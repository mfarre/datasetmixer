import json

# File paths
aggregated_summary_path = "aggregated_summary.json"
summary_output_path = "summary_output.json"
summary_output_augmented_path = "summary_output_augmented.json"

# Load aggregated summary data
with open(aggregated_summary_path, 'r') as f:
    aggregated_summary = json.load(f)

# Load summary output data
with open(summary_output_path, 'r') as f:
    summary_output = json.load(f)

# Prepare augmented summary output
augmented_summary_output = []

# Iterate through each entry in summary output
for item in summary_output:
    text_file = item.get("text_file")
    text_file_search = text_file.split("/")[-1]
    text_file_search = './' + text_file_search
    coarse_data_type = None
    fine_data_type = None

    # Attempt to find matching coarse and fine data types from aggregated summary
    for key, data in aggregated_summary.get("file_data", {}).items():
        if text_file_search in data.get("texts", []):
            coarse_data_type = data.get("coarse_data_type")
            fine_data_type = data.get("fine_data_type")
            break

    # Print a warning if no match is found
    if coarse_data_type is None or fine_data_type is None:
        print(f"Warning: No coarse or fine data type found for text file: {text_file} using for search {text_file_search}")

    # Append augmented data to the output list
    augmented_summary_output.append({
        "text_file": text_file,
        "images": item.get("images"),
        "source": item.get("source"),
        "type": item.get("type"),
        "coarse_data_type": coarse_data_type,
        "fine_data_type": fine_data_type
    })

# Write augmented summary output to a new file
with open(summary_output_augmented_path, 'w') as f:
    json.dump(augmented_summary_output, f, indent=4)

print(f"Augmented summary output saved to {summary_output_augmented_path}")
