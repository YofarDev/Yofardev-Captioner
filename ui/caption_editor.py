import os
import tkinter as tk
from tkinter import messagebox

from src.utils.utils import save_caption_to_file


class CaptionEditor:
    """Handles text editing and caption management."""
    
    def __init__(self, captioner):
        self.captioner = captioner
        self.text_entry = None
    
    def setup_text_entry(self):
        """Setup the text entry widget."""
        self.text_entry = tk.Text(self.captioner.root, height=16, width=85, wrap="word")
        self.text_entry.config(borderwidth=2, relief="groove")
        # Set the font and font size
        self.text_entry.config(
            font=("Verdana", 18)
        )  # Change "Helvetica" and 12 to your desired font and size
        self.text_entry.config(padx=10, pady=10)  # Adjust the padding values as needed

        self.text_entry.pack(side="bottom", fill="both")
        # Enable the undo mechanism
        self.text_entry.config(undo=True, autoseparators=True, maxundo=-1)
    
    def undo_text(self, event):
        """Undo text changes."""
        try:
            self.text_entry.edit_undo()
        except tk.TclError:
            # Ignore the error if there's nothing to undo
            pass

    def redo_text(self, event):
        """Redo text changes."""
        try:
            self.text_entry.edit_redo()
        except tk.TclError:
            # Ignore the error if there's nothing to redo
            pass

    def save_caption(self, event=None):
        """Save the current caption to file."""
        try:
            description = self.text_entry.get(1.0, "end").strip()
            if description == "":
                return
            description_file = str(self.captioner.current_image_path).rsplit(".", 1)[0] + ".txt"
            save_caption_to_file(description, description_file)
            # After saving, check and color the item again
            item = self.captioner.image_manager.image_list.items[self.captioner.index]
            self.captioner.image_manager.check_and_color_item(item, self.captioner.current_image_path)
        except Exception as e:
            messagebox.showinfo(
                "Error", f"There was an error while saving the captions: {e}"
            )
    
    def load_caption(self, file_path):
        """Load caption from file into text entry."""
        self.text_entry.delete(1.0, "end")
        description_file = str(file_path).rsplit(".", 1)[0] + ".txt"
        if os.path.isfile(description_file):
            with open(description_file, "r") as file:
                description = file.read()
                self.text_entry.insert(1.0, description)
    
    def clear_caption(self):
        """Clear the text entry."""
        self.text_entry.delete(1.0, "end")
    
    def get_caption_text(self):
        """Get the current caption text."""
        return self.text_entry.get(1.0, "end").strip()
    
    def set_caption_text(self, text):
        """Set the caption text."""
        self.text_entry.delete(1.0, "end")
        self.text_entry.insert(1.0, text)
