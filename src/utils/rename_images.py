import os
from pathlib import Path

def rename_files_to_numbers(folder_path):
    image_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.JPG', '.JPEG', '.PNG', '.WEBP')
    
    # Get all image files and sort them naturally
    all_files_in_folder = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    image_files = [f for f in all_files_in_folder if f.lower().endswith(image_extensions)]
    
    # Sort files naturally to maintain a consistent order for renumbering
    # We need to import sort_files from utils
    from .utils import sort_files
    sorted_image_files = sort_files([os.path.join(folder_path, f) for f in image_files])
    
    # Calculate padding length based on total number of files
    padding = len(str(len(sorted_image_files)))

    # Prepare a list of (original_full_path, new_base_name, suffix)
    renaming_plan = []
    for idx, original_full_path in enumerate(sorted_image_files, 1):
        original_filename = os.path.basename(original_full_path)
        suffix = Path(original_filename).suffix
        new_number_str = str(idx).zfill(padding)
        renaming_plan.append((original_full_path, new_number_str, suffix))

    # First pass: Rename all files to temporary names to avoid conflicts
    temp_renames = {}
    for original_full_path, new_number_str, suffix in renaming_plan:
        original_filename = os.path.basename(original_full_path)
        temp_filename = f"temp_{new_number_str}{suffix}"
        temp_full_path = os.path.join(folder_path, temp_filename)
        
        os.rename(original_full_path, temp_full_path)
        temp_renames[temp_full_path] = (original_filename, new_number_str, suffix)

        # Rename corresponding text file to a temporary name
        original_text_path = os.path.splitext(original_full_path)[0] + '.txt'
        if os.path.exists(original_text_path):
            temp_text_filename = f"temp_{new_number_str}.txt"
            temp_text_full_path = os.path.join(folder_path, temp_text_filename)
            os.rename(original_text_path, temp_text_full_path)

    # Second pass: Rename from temporary names to final desired names
    for temp_full_path, (original_filename, new_number_str, suffix) in temp_renames.items():
        final_filename = f"{new_number_str}{suffix}"
        final_full_path = os.path.join(folder_path, final_filename)
        
        os.rename(temp_full_path, final_full_path)

        # Rename corresponding temporary text file to final name
        temp_text_full_path = os.path.splitext(temp_full_path)[0] + '.txt'
        if os.path.exists(temp_text_full_path):
            final_text_filename = f"{new_number_str}.txt"
            final_text_full_path = os.path.join(folder_path, final_text_filename)
            os.rename(temp_text_full_path, final_text_full_path)
