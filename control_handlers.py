import os
import glob
from tkinter import filedialog, messagebox
from utils import sort_files, save_caption_to_file
from florence2_inference import run_single, run_multiple

def run_florence2(self):
    if self.florence2_mode.get() == "single":
        caption = run_single(self.current_image_path, self.trigger_entry.get())
        self.text_entry.delete(1.0, "end")
        self.text_entry.insert(1.0, caption)    
    else:
        file_paths = list(self.file_map.values())
        run_multiple(file_paths, self.trigger_entry.get())

def open_folder(self):
    try:
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.current_folder = folder_path
            load_images_from_folder(self, folder_path)
            save_session(self)
    except Exception as e:
        print(f"Error opening folder: {e}")
        pass

def open_images(self):
    try:
        file_types = "*.bmp *.jpg *.jpeg *.png"
        file_paths = filedialog.askopenfilenames(
            filetypes=[("Common Image Files", file_types), ("All", "*.*")]
        )
        file_paths = sort_files(file_paths)
        if file_paths:
            self.current_folder = os.path.dirname(file_paths[0])
            self.image_list.delete("0", "end")
            self.file_map = {}
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                self.file_map[file_name] = file_path
                self.image_list.insert("end", file_name)
            save_session(self)
    except Exception as e:
        print(f"Error opening images: {e}")
        pass

def save_caption(self, event=None):
    try:
        description = self.text_entry.get(1.0, "end")
        description_file = str(self.current_image_path).rsplit(".", 1)[0] + ".txt"
        save_caption_to_file(description, description_file)
    except Exception as e:
        messagebox.showinfo(
            "Error", f"There was an error while saving the captions: {e}"
        )

def on_trigger_change(self, event):
    save_session(self)
