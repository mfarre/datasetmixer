import os
import tarfile
import json
from collections import Counter, defaultdict
import argparse

# Normalize source name for PDFA sources
def normalize_source(source):
    if source.startswith("PDFA key"):
        return "PDFA"
    return source

# Remove leading './' from tar member names
def clean_member_name(name):
    return name[2:] if name.startswith("./") else name

def process_tar(tar_file_path):
    # Dictionary to count occurrences
    data_types = Counter()
    source_types = defaultdict(lambda: defaultdict(int))  # Track sources per case type

    # Dictionary to store file data organized by source and tar origin
    file_data = {}

    with tarfile.open(tar_file_path, "r") as tar:
        members = tar.getmembers()
        for member in members:
            if member.isfile() and not clean_member_name(member.name).startswith("."):  # Ignore hidden files
                file_name = os.path.basename(clean_member_name(member.name))
                number_uuid = file_name.split(".")[0]
                if number_uuid not in file_data:
                    file_data[number_uuid] = {
                        "images": 0,
                        "texts": [],
                        "metadata": None,
                        "origin_tar": os.path.basename(tar_file_path),
                    }

                if file_name.endswith(".image.jpeg"):
                    file_data[number_uuid]["images"] += 1
                elif file_name.endswith(".text.txt"):
                    file_data[number_uuid]["texts"].append(member.name)
                elif file_name.endswith(".metadata.txt"):
                    file_data[number_uuid]["metadata"] = member.name

    with tarfile.open(tar_file_path, "r") as tar:  # Re-open tarfile for extraction
        for number_uuid, data in file_data.items():
            # Track sources
            sources = set()
            for text_member_name in data["texts"]:
                try:
                    with tar.extractfile(text_member_name) as f:
                        content = json.load(f)
                        if "source" in content:
                            sources.add(normalize_source(content["source"]))
                except (json.JSONDecodeError, KeyError, AttributeError):
                    pass

            if data["images"] == 1 and data["texts"]:
                data_types["single_image"] += 1
                data['coarse_data_type'] = 'single_image'
                for source in sources:
                    source_types["single_image"][source] += 1
                    data['fine_data_type'] = source

            elif data["images"] > 1 and data["texts"]:
                data_types["multi_image"] += 1
                data['coarse_data_type'] = 'multi_image'
                for source in sources:
                    source_types["multi_image"][source] += 1
                    data['fine_data_type'] = source

            elif data["images"] == 0 and data["texts"]:
                data_types["only_text"] += 1
                data['coarse_data_type'] = 'only_text'
                for source in sources:
                    source_types["only_text"][source] += 1
                    data['fine_data_type'] = source

    # Save the summary as JSON
    summary = {
        "file_data": {k: {"images": v["images"], "texts": v["texts"], "metadata": v["metadata"], "origin_tar": v["origin_tar"], "coarse_data_type":v['coarse_data_type'], "fine_data_type":v['fine_data_type']} for k, v in file_data.items()},
        "data_types": dict(data_types),
        "source_types": {k: dict(v) for k, v in source_types.items()},
    }

    summary_path = f"summaries/summary_{os.path.basename(tar_file_path)}.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=4)

    print(f"Summary saved to {summary_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a single tar file.")
    parser.add_argument("tar_file", type=str, help="Path to the tar file")
    args = parser.parse_args()

    process_tar(args.tar_file)
