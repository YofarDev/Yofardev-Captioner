import os
import shutil

# Define the paths for the folders
folder1 = '/Users/yofardev/Downloads/all'
folder2 = '/Users/yofardev/development/Projects/Python/kiki/100'
folder3 = '/Users/yofardev/development/Projects/Python/kiki/todo'

# Create folder3 if it doesn't exist
os.makedirs(folder3, exist_ok=True)

# Get the list of files in both folders
files_in_folder1 = set(os.listdir(folder1))
files_in_folder2 = set(os.listdir(folder2))

# Subtract the two sets to get the files in folder1 that are not in folder2
files_to_copy = files_in_folder1 - files_in_folder2

# Copy the files to folder3
for file_name in files_to_copy:
    src_file = os.path.join(folder1, file_name)
    dst_file = os.path.join(folder3, file_name)
    shutil.copy2(src_file, dst_file)

print(f"Files copied to {folder3}: {files_to_copy}")
