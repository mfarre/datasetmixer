import os
import json
from datasets import Dataset, DatasetDict

# Path to the summary.json file
summary_path = "summary_output.json"

# Output Hugging Face repository
hf_repo = "HuggingFaceFV/longvumixexpanded"

# Load the summary.json
with open(summary_path, "r") as f:
    summary = json.load(f)

# Prepare the dataset
entries = []
for item in summary:
    text_file = item["text_file"]
    if item["images"] is not None:
        images = 'expansion/'+item['images'].split("expansion/")[1]
    else:
        images = None
    source = item["source"]
    case_type = item["type"]

    # Read the JSON content in the text file
    with open(text_file, "r") as tf:
        text_content = json.load(tf)

    user_query = text_content.get("user", "")
    assistant_response = text_content.get("assistant", "")

    # Format the conversations field
    conversations = [
        {
            "from": "human",
            "value": f"<image>\n{user_query}"
        },
        {
            "from": "gpt",
            "value": assistant_response
        }
    ]

    # Append the entry
    entries.append({
        "video": images,
        "conversations": conversations,
        "type": case_type
    })

# Convert to a Hugging Face dataset
dataset = Dataset.from_list(entries)

dataset_dict = DatasetDict({"train": dataset})

# Push to Hugging Face Hub
dataset_dict.push_to_hub(hf_repo)

print(f"Dataset successfully pushed to {hf_repo}.")
