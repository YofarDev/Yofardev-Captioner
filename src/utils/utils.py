import glob
import os
import re
import base64
import io
import tempfile
from mimetypes import guess_type
from PIL import Image

# Define the maximum image size in bytes (10MB)
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024

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


def sort_files(files_path):
    def convert(text):
        return int(text) if text.isdigit() else text.lower()
    def alphanum_key(key):
        return [convert(c) for c in re.split("([0-9]+)", key)]
    return sorted(files_path, key=alphanum_key)

def sort_by_name(file_list):
    try:
        sorted_files = sorted(file_list, key=lambda x: os.path.basename(x).lower())
        return sorted_files
    except Exception as e:
        print(f"Error sorting files: {e}")
        return file_list

def load_images_from_folder(folder_path):
    file_map = {}
    file_types = ("*.bmp", "*.jpg", "*.jpeg", "*.png")
    for file_type in file_types:
        for file_path in sort_files(glob.glob(os.path.join(folder_path, file_type))):
            file_name = os.path.basename(file_path)
            file_map[file_name] = file_path
    return file_map

def save_caption_to_file(caption, file_path):
    if caption is None:
        caption = "" # Ensure caption is a string, even if None is passed
    with open(file_path, "w") as file:
        file.write(caption)
    print(f"Captions saved successfully at {file_path}")
    
    
def load_file_as_string(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return ""
    
def check_file_exists(file_path):
    return os.path.isfile(file_path)

# Function to encode a local image into data URL 
def local_image_to_data_url(image_path):
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Default MIME type if none is found
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:{mime_type};base64,{base64_encoded_data}"

def resize_image_if_needed(image_path, max_size_bytes=MAX_IMAGE_SIZE_BYTES):
    """
    Resizes an image if its file size exceeds max_size_bytes.
    Returns the path to the (potentially temporary) resized image.
    """
    file_size = os.path.getsize(image_path)

    if file_size <= max_size_bytes:
        return image_path, False # No resize needed, return original path and a flag

    print(f"Image {image_path} is too large ({file_size / (1024 * 1024):.2f} MB). Resizing...")

    try:
        with Image.open(image_path) as img:
            # Determine initial quality/scale
            quality = 90
            scale_factor = 0.9

            # Create a temporary file to save the resized image
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image_path)[1])
            temp_path = temp_file.name
            temp_file.close()

            # Iteratively reduce quality/scale until size is acceptable
            while True:
                # Save to a buffer to check size without writing to disk repeatedly
                img_byte_arr = io.BytesIO()
                
                # Handle different image formats
                if img.mode in ("RGBA", "P"): # PNGs and images with alpha channel
                    img.save(img_byte_arr, format='PNG', optimize=True)
                else: # JPEGs and other formats
                    img.save(img_byte_arr, format='JPEG', quality=quality, optimize=True)
                
                current_size = img_byte_arr.tell()

                if current_size <= max_size_bytes:
                    # Write the content from buffer to the temporary file
                    with open(temp_path, 'wb') as f:
                        f.write(img_byte_arr.getvalue())
                    print(f"Resized image saved to {temp_path} with size {current_size / (1024 * 1024):.2f} MB")
                    return temp_path, True # Return temporary path and a flag indicating resize happened

                # Reduce quality or scale down if still too large
                if quality > 10:
                    quality -= 10
                else:
                    # If quality is already low, start scaling down dimensions
                    new_width = int(img.width * scale_factor)
                    new_height = int(img.height * scale_factor)
                    if new_width < 100 or new_height < 100: # Prevent image from becoming too small
                        print("Warning: Image could not be resized to fit within limits without becoming too small.")
                        # As a last resort, save with lowest quality and current dimensions
                        with open(temp_path, 'wb') as f:
                            f.write(img_byte_arr.getvalue())
                        return temp_path, True
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                    scale_factor -= 0.1 # Further reduce scale for next iteration
                    quality = 90 # Reset quality for new dimensions

    except Exception as e:
        print(f"Error resizing image {image_path}: {e}")
        return image_path, False # Fallback to original if resize fails

def local_image_to_data_url(image_path):
    """
    Encodes a local image into a data URL, resizing it if necessary.
    """
    resized_path, was_resized = resize_image_if_needed(image_path)
    
    mime_type, _ = guess_type(resized_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Default MIME type if none is found
    
    with open(resized_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Clean up the temporary file if it was created
    if was_resized:
        os.remove(resized_path)
        print(f"Cleaned up temporary resized image: {resized_path}")

    return f"data:{mime_type};base64,{base64_encoded_data}"
