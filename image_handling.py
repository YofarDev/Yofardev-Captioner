import os
import glob
from PIL import Image, ImageTk
from utils import sort_files

def load_images_from_folder(self, folder_path):
    self.image_list.delete("0", "end")
    self.file_map = {}
    file_types = ("*.bmp", "*.jpg", "*.jpeg", "*.png")
    for file_type in file_types:
        for file_path in sort_files(
            glob.glob(os.path.join(folder_path, file_type))
        ):
            file_name = os.path.basename(file_path)
            self.file_map[file_name] = file_path
            self.image_list.insert("end", file_name)

def display_image(self, event):
    try:
        self.save_caption()
        selection = self.image_list.curselection()
        if not selection:
            return

        self.text_entry.delete(1.0, "end")
        index = selection[0]
        file_name = self.image_list.get(index)
        file_path = self.file_map[file_name]
        self.current_image = file_name
        self.current_image_path = file_path

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        max_size = int(screen_width / 2), int(screen_height / 2.1)

        image = Image.open(file_path)

        original_width, original_height = image.size
        aspect_ratio = original_width / original_height
        new_width, new_height = max_size

        if original_width > original_height:
            new_height = int(new_width / aspect_ratio)
        else:
            new_width = int(new_height * aspect_ratio)

        if new_width > max_size[0]:
            new_width = max_size[0]
            new_height = int(new_width / aspect_ratio)
        if new_height > max_size[1]:
            new_height = max_size[1]
            new_width = int(new_height * aspect_ratio)

        image = image.resize((new_width, new_height), Image.LANCZOS)
        image = ImageTk.PhotoImage(image)
        self.image_label.config(image=image)
        self.image_label.image = image
        self.image_label.config(borderwidth=5, relief="groove")

        description_file = str(self.current_image_path).rsplit(".", 1)[0] + ".txt"

        if os.path.isfile(description_file):
            with open(description_file, "r") as file:
                description = file.read()
                self.text_entry.insert(1.0, description)
        else:
            self.text_entry.delete(1.0, "end")
        self.root.title(f"Yofardev Captioner - {self.current_image}")
        update_list_colors(self)
    except Exception as e:
        print(f"Error loading image: {e}")
        pass

def update_list_colors(self):
    self.image_list.itemconfig(0, {'bg':'white'})
    for i in range(self.image_list.size()):
        if self.image_list.get(i) == self.current_image:
            self.image_list.itemconfig(i, {'bg':'light blue'})
        else:
            self.image_list.itemconfig(i, {'bg':'black'})
