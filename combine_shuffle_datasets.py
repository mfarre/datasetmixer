import random
from datasets import load_dataset, Dataset, DatasetDict

# Set random seed for reproducibility
random.seed(42)

# Datasets to pull
original_repo = "HuggingFaceFV/longvumix"
expanded_repo = "HuggingFaceFV/longvumixexpanded"
output_repo = "HuggingFaceFV/longvucauldron"

# Load the original dataset
print(f"Loading dataset from {original_repo}...")
original_dataset = load_dataset(original_repo, split="train")

# Add 'type' column to the original dataset and set it to 'video'
def add_type_column(example):
    example["type"] = "video"
    return example

original_dataset = original_dataset.map(add_type_column)

# Load the expanded dataset
print(f"Loading dataset from {expanded_repo}...")
expanded_dataset = load_dataset(expanded_repo, split="train")

# Mix both datasets
print("Combining datasets...")
mixed_dataset = Dataset.from_dict({
    key: original_dataset[key] + expanded_dataset[key]
    for key in original_dataset.column_names
})
mixed_dataset = mixed_dataset.shuffle(seed=42)

# Push the combined dataset to Hugging Face Hub
dataset_dict = DatasetDict({"train": mixed_dataset})
print(f"Pushing the combined dataset to {output_repo}...")
dataset_dict.push_to_hub(output_repo)

# Count the rows per type
total_rows = len(mixed_dataset)
type_counts = mixed_dataset.unique("type")

print("Dataset Analysis:")
print(f"Total rows: {total_rows}")
for case_type in type_counts:
    count = mixed_dataset.filter(lambda x: x["type"] == case_type).num_rows
    print(f"  {case_type}: {count}")
