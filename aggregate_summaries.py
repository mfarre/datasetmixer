import os
import json
from collections import Counter, defaultdict

# Path to the folder containing the individual summary files
summaries_folder = "summaries/"
output_summary_path = "aggregated_summary.json"

# Initialize the aggregated summary
aggregated_summary = {
    "file_data": {},
    "data_types": Counter(),
    "source_types": defaultdict(lambda: defaultdict(int))
}

# List all summary files
summary_files = [
    os.path.join(summaries_folder, f)
    for f in os.listdir(summaries_folder)
    if f.startswith("summary_") and f.endswith(".json")
]

print(f"Aggregating {len(summary_files)} summary files.")

# Aggregate data
for summary_file in summary_files:
    with open(summary_file, "r") as f:
        summary = json.load(f)

        # Aggregate file_data
        aggregated_summary["file_data"].update(summary["file_data"])

        # Aggregate data_types
        for key, value in summary["data_types"].items():
            aggregated_summary["data_types"][key] += value

        # Aggregate source_types
        for case_type, sources in summary["source_types"].items():
            for source, count in sources.items():
                aggregated_summary["source_types"][case_type][source] += count

# Convert Counters to dicts for JSON serialization
aggregated_summary["data_types"] = dict(aggregated_summary["data_types"])
aggregated_summary["source_types"] = {
    key: dict(value) for key, value in aggregated_summary["source_types"].items()
}

# Save the aggregated summary
with open(output_summary_path, "w") as f:
    json.dump(aggregated_summary, f, indent=4)

print(f"Aggregated summary saved to {output_summary_path}")
