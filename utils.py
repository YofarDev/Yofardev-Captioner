import glob
import os
import re


def extract_first_sentence(text):
    match = re.match(r"([^.!?]*[.!?])", text)
    if match:
        return match.group(1).strip()
    else:
        return None


def get_substring_starting_from_word(text, word):
    index = text.find(word)
    if index != -1:
        return text[index:]
    else:
        return None


def rewrite_caption_with_trigger_phrase(txt, trigger_phrase):
    pre_prompt = f"A {trigger_phrase} style image"
    if txt.startswith("The image shows"):
        new_prompt = txt.replace("The image shows", f"{pre_prompt} that shows")
    elif txt.startswith("The image is an aerial view"):
        new_prompt = txt.replace("The image is", f"{pre_prompt} of")
    elif txt.startswith("The image is a close-up"):
        new_prompt = txt.replace("The image is", f"{pre_prompt} of")
    elif txt.startswith("The image is a macro"):
        new_prompt = txt.replace("The image is", f"{pre_prompt} of")
    elif txt.startswith("The image is a panorama"):
        new_prompt = txt.replace("The image is", f"{pre_prompt} of")
    elif txt.startswith("The image is a wide-angle"):
        new_prompt = txt.replace("The image is", f"{pre_prompt} of")
    elif txt.startswith("The image is a landscape"):
        new_prompt = txt.replace("The image is", f"{pre_prompt} of").replace(
            "landscape painting", "landscape"
        )
    else:
        fs = extract_first_sentence(txt)
        of_sentence = get_substring_starting_from_word(fs, " of ")
        if of_sentence is None:
            new_prompt = txt.replace(fs, f"{pre_prompt}.")
            return new_prompt
        else:
            end_of_sentence = get_substring_starting_from_word(txt, of_sentence)
            new_prompt = f"{pre_prompt}{end_of_sentence}"
    return new_prompt.replace('illustration', 'image')

def sort_files(files_path):
    def convert(text):
        return int(text) if text.isdigit() else text.lower()
    def alphanum_key(key):
        return [convert(c) for c in re.split("([0-9]+)", key)]
    return sorted(files_path, key=alphanum_key)

def load_images_from_folder(folder_path):
    file_map = {}
    file_types = ("*.bmp", "*.jpg", "*.jpeg", "*.png")
    for file_type in file_types:
        for file_path in sort_files(glob.glob(os.path.join(folder_path, file_type))):
            file_name = os.path.basename(file_path)
            file_map[file_name] = file_path
    return file_map

def save_caption_to_file(caption, file_path):
    with open(file_path, "w") as file:
                file.write(caption)
    print(f"Captions saved successfully at {file_path}")
    
    
def load_file_as_string(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return ""
    


