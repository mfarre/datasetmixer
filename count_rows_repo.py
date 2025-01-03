import os
from datasets import load_dataset
from tqdm import tqdm

# Hugging Face repository to analyze
hf_repo = "HuggingFaceFV/longvucauldron"

# Base path to check for files and folders
base_path = "/fsx/miquel/longvu-dataset/composition/"

# Load the dataset
print(f"Loading dataset from {hf_repo}...")
dataset = load_dataset(hf_repo, split="train")

# Initialize counters
total_rows = len(dataset)  # Get total count for tqdm
type_counts = {}
issues = []

# Iterate through the dataset with tqdm
for row in tqdm(dataset, total=total_rows, desc="Analyzing dataset"):
    case_type = row.get("type", "unknown")
    video_path = row.get("video")

    if case_type not in type_counts:
        type_counts[case_type] = 0
    type_counts[case_type] += 1

    if case_type == "single_image" and video_path:
        # Check for single image existence
        file_path = os.path.join(base_path, video_path)
        if not os.path.isfile(file_path):
            issues.append(f"Missing file for single_image: {file_path}")
            print(f"Missing file for single_image: {file_path}")

    elif case_type == "multi_image" and video_path:
        # Check for multi-image folder existence and contents
        folder_path = os.path.join(base_path, video_path)
        if not os.path.isdir(folder_path):
            issues.append(f"Missing folder for multi_image: {folder_path}")
            print(f"Missing folder for multi_image: {folder_path}")
        elif not os.listdir(folder_path):
            issues.append(f"Empty folder for multi_image: {folder_path}")
            print(f"Empty folder for multi_image: {folder_path}")

# Print the results
print("\nDataset Analysis:")
print(f"Total rows: {total_rows}")
for case_type, count in type_counts.items():
    print(f"  {case_type}: {count}")

# Report issues
print("\nIssues Found:")
if issues:
    for issue in issues:
        print(issue)
    print(f"\nTotal issues: {len(issues)}")
else:
    print("No issues found.")