import glob
import os
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

from rename_images import rename_files_to_numbers
from session_file import save_session
from thumbnail import ThumbnailListbox
from utils import sort_by_name, sort_files


class ImageManager:
    """Handles all image-related operations."""
    
    def __init__(self, captioner):
        self.captioner = captioner
        self.image_list = None
        self.image_label = None
        self.resolution_label = None
        self.frame_list = None
    
    def setup_image_list(self):
        """Setup the thumbnail image list."""
        self.image_list = ThumbnailListbox(self.frame_list, self.captioner)
        self.image_list.pack(side="left", fill="both", expand=True)

    def setup_scrollbars(self):
        """Setup scrollbars for the image list."""
        h_scrollbar = tk.Scrollbar(self.frame_list, orient="horizontal")
        h_scrollbar.pack(side="bottom", fill="x")
        h_scrollbar.config(command=self.image_list.xview)
        self.image_list.config(xscrollcommand=h_scrollbar.set)

        v_scrollbar = tk.Scrollbar(self.frame_list, orient="vertical")
        v_scrollbar.pack(side="right", fill="y")
        v_scrollbar.config(command=self.image_list.yview)
        self.image_list.config(yscrollcommand=v_scrollbar.set)

    def setup_image_display(self):
        """Setup the image display area."""
        self.image_label = tk.Label(self.captioner.root)
        self.image_label.pack(side="top", anchor="center")

        # Add a label to display resolution and aspect ratio
        self.resolution_label = tk.Label(self.captioner.root, text="", font=("Arial", 10))
        self.resolution_label.pack(side="top", anchor="center", pady=5)

    def open_folder(self):
        """Open a folder and load all images from it."""
        try:
            folder_path = filedialog.askdirectory()
            if folder_path:
                self.captioner.current_folder = folder_path
                self.load_images_from_folder(folder_path)
                save_session(self.captioner)
        except Exception as e:
            print(f"Error opening folder: {e}")

    def load_images_from_folder(self, folder_path):
        """Load all images from the specified folder."""
        for item in self.image_list.items:
            item.destroy()
        self.image_list.items = []
        self.captioner.file_map = {}
        file_types = ("*.bmp", "*.jpg", "*.jpeg", "*.png")
        all_files = []

        # Collect all files first
        for file_type in file_types:
            all_files.extend(glob.glob(os.path.join(folder_path, file_type)))

        # Sort all files by name
        sorted_files = sort_by_name(all_files)

        # Insert sorted files into the image list
        for file_path in sorted_files:
            file_name = os.path.basename(file_path)
            self.captioner.file_map[file_name] = file_path
            item = self.image_list.insert(file_path, file_name)
            self.check_and_color_item(item, file_path)

    def open_images(self):
        """Open individual image files."""
        try:
            file_types = "*.bmp *.jpg *.jpeg *.png"
            file_paths = filedialog.askopenfilenames(
                filetypes=[("Common Image Files", file_types), ("All", "*.*")]
            )
            file_paths = sort_files(file_paths)
            if file_paths:
                self.captioner.current_folder = os.path.dirname(file_paths[0])
                for item in self.image_list.items:
                    item.destroy()
                self.image_list.items = []
                self.captioner.file_map = {}
                for file_path in file_paths:
                    file_name = os.path.basename(file_path)
                    self.captioner.file_map[file_name] = file_path
                    item = self.image_list.insert(file_path, file_name)
                    self.check_and_color_item(item, file_path)
                save_session(self.captioner)
        except Exception as e:
            print(f"Error opening images: {e}")

    def refresh_images(self):
        """Refresh the image list from the current folder."""
        if self.captioner.current_folder:
            self.load_images_from_folder(self.captioner.current_folder)

    def rename_images(self):
        """Rename all images in the current folder to numbers."""
        rename_files_to_numbers(self.captioner.current_folder)
        self.load_images_from_folder(self.captioner.current_folder)
        save_session(self.captioner)

    def display_image(self, event):
        """Display the selected image."""
        try:
            self.captioner.caption_editor.save_caption()
            selection = self.image_list.curselection()
            if not selection:
                return
            self.captioner.caption_editor.clear_caption()
            self.captioner.index = selection[0]
            file_name = self.image_list.get(self.captioner.index)
            file_path = self.captioner.file_map[file_name]
            self.captioner.current_image = file_name
            self.captioner.current_image_path = file_path
            screen_width = self.captioner.root.winfo_screenwidth()
            max_height = 500  # Fixed height limit

            with Image.open(file_path) as image:
                original_width, original_height = image.size
                aspect_ratio = original_width / original_height
                aspect_ratio_str = f"{aspect_ratio:.2f}"

                new_width, new_height = original_width, original_height

                # Scale down if image height is greater than max_height
                if original_height > max_height:
                    new_height = max_height
                    new_width = int(new_height * aspect_ratio)

                # If the new width exceeds the screen width, scale down proportionally
                if new_width > screen_width:
                    new_width = screen_width
                    new_height = int(new_width / aspect_ratio)

                image = image.resize((new_width, new_height), Image.LANCZOS)
                image = ImageTk.PhotoImage(image)
                self.image_label.config(image=image)
                self.image_label.image = image
                self.image_label.config(borderwidth=5, relief="groove")

                # Get file size
                file_size_bytes = os.path.getsize(file_path)
                file_size_kb = file_size_bytes / 1024
                file_size_mb = file_size_kb / 1024

                if file_size_mb >= 1:
                    file_size_str = f"{file_size_mb:.2f} MB"
                else:
                    file_size_str = f"{file_size_kb:.2f} KB"

                # Update the resolution, aspect ratio, and file size label
                resolution_text = f"{original_width}x{original_height} ({aspect_ratio_str}) - {file_size_str}"
                self.resolution_label.config(text=resolution_text)

                # Load caption if exists
                self.captioner.caption_editor.load_caption(file_path)
                self.captioner.root.title(f"Yofardev Captioner - {self.captioner.current_image_path}")
        except Exception as e:
            print(f"Error loading image: {e}")
            messagebox.showinfo("Error", f"There was an error loading the image: {e}")

    def check_and_color_item(self, item, file_path):
        """Check if caption exists and color the item accordingly."""
        caption_file = os.path.splitext(file_path)[0] + ".txt"
        if not os.path.exists(caption_file) or os.path.getsize(caption_file) == 0:
            item.set_bg_color("gray15", fg="white")
        else:
            item.set_bg_color("gray25", fg="white")