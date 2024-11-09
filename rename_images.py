import os
from pathlib import Path

def rename_files_to_numbers(folder_path):
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
    image_files = [f for f in os.listdir(folder_path) 
                  if f.lower().endswith(image_extensions)]
    # Calculate padding length based on total number of files
    padding = len(str(len(image_files)))
    # Create a mapping of old names to new names
    new_names = {}
    for idx, old_name in enumerate(sorted(image_files), 1):
        new_number = str(idx).zfill(padding)
        new_name = f"{new_number}{Path(old_name).suffix}"
        # Check if the new name already exists
        if os.path.exists(os.path.join(folder_path, new_name)):
            return
        new_names[old_name] = new_name
    # Second pass: perform the renaming
    for old_name, new_name in new_names.items():
        old_path = os.path.join(folder_path, old_name)
        new_path = os.path.join(folder_path, new_name)
        # Rename image file
        os.rename(old_path, new_path)
        # Check for corresponding text file
        old_text = os.path.splitext(old_name)[0] + '.txt'
        new_text = os.path.splitext(new_name)[0] + '.txt'
        old_text_path = os.path.join(folder_path, old_text)
        new_text_path = os.path.join(folder_path, new_text)
        # Rename text file if it exists
        if os.path.exists(old_text_path):
            os.rename(old_text_path, new_text_path)
        

