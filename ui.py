import glob
import os
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

from rename_images import rename_files_to_numbers
from session_file import load_session, save_session
from thumbnail import ThumbnailListbox
from utils import save_caption_to_file, sort_by_name, sort_files
from vision_service import on_run_pressed
import settings


class Captioner:
    def __init__(self, root):
        self.root = root
        self.file_map = {}
        self.current_folder = ""
        self.current_image = ""
        self.current_image_path = ""
        self.caption_mode = tk.StringVar(value="single")
        self.selected_model = tk.StringVar(value="Florence2")
        self.gpt_last_used = None
        self.index = 0
        self.prompt_text = "Describe this image as one paragraph, without mentionning the style nor the atmosphere."
        self.setup_ui()
        load_session(self)

    def setup_ui(self):
        self.setup_window()
        self.setup_frames()
        self.setup_image_list()
        self.setup_image_display()
        self.setup_text_entry()
        self.setup_control_frame()
        self.setup_settings_icon()
        self.bind_events()

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = int(screen_width / 1.5)
        height = int(screen_height / 1.2)
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry("%dx%d+%d+%d" % (width, height, x, y))

    def setup_window(self):
        self.root.title("Yofardev Captioner")
        self.center_window()
        self.root.resizable(False, False)

    def setup_frames(self):
        self.frame_list = tk.Frame(self.root)
        self.frame_list.pack(side="left", fill="y")
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side="bottom", fill="x", pady=10)

    def setup_image_list(self):
        self.image_list = ThumbnailListbox(self.frame_list, self)
        self.image_list.pack(side="left", fill="both", expand=True)

    def setup_scrollbars(self):
        h_scrollbar = tk.Scrollbar(self.frame_list, orient="horizontal")
        h_scrollbar.pack(side="bottom", fill="x")
        h_scrollbar.config(command=self.image_list.xview)
        self.image_list.config(xscrollcommand=h_scrollbar.set)

        v_scrollbar = tk.Scrollbar(self.frame_list, orient="vertical")
        v_scrollbar.pack(side="right", fill="y")
        v_scrollbar.config(command=self.image_list.yview)
        self.image_list.config(yscrollcommand=v_scrollbar.set)

    def setup_image_display(self):
        self.image_label = tk.Label(self.root)
        self.image_label.pack(side="top", anchor="center")
        self.image_label.pack_propagate(False)

        # Add a label to display resolution and aspect ratio
        self.resolution_label = tk.Label(self.root, text="", font=("Arial", 10))
        self.resolution_label.pack(side="top", anchor="center", pady=5)

    def setup_text_entry(self):
        self.text_entry = tk.Text(self.root, height=16, width=85, wrap="word")
        self.text_entry.config(borderwidth=2, relief="groove")
        # Set the font and font size
        self.text_entry.config(font=("Verdana", 18))  # Change "Helvetica" and 12 to your desired font and size
        self.text_entry.config(padx=10, pady=10)  # Adjust the padding values as needed

        
        self.text_entry.pack(side="bottom", fill="both")
        # Enable the undo mechanism
        self.text_entry.config(undo=True, autoseparators=True, maxundo=-1)

    def setup_settings_icon(self):
        # Create a text button for settings
        self.settings_button = tk.Button(
            self.root,
            text="API Keys",
            command=self.open_settings,
            bd=0,
            highlightthickness=0,
            bg="gray25",
            fg="black",
            font=("Arial", 10, "bold")
        )
        self.settings_button.place(relx=1.0, rely=0.0, x=-10, y=10, anchor=tk.NE)

    def open_settings(self):
        settings.open_settings(self)


    def undo_text(self, event):
        try:
            self.text_entry.edit_undo()
        except tk.TclError:
            # Ignore the error if there's nothing to undo
            pass

    def redo_text(self, event):
        try:
            self.text_entry.edit_redo()
        except tk.TclError:
            # Ignore the error if there's nothing to redo
            pass

    def setup_control_frame(self):
        # Create two separate frames for the rows
        self.top_row_frame = tk.Frame(self.control_frame)
        self.top_row_frame.pack(fill="x", pady=(0, 5))

        self.bottom_row_frame = tk.Frame(self.control_frame)
        self.bottom_row_frame.pack(fill="x")

        self.setup_first_row()
        self.setup_second_row()

    def setup_first_row(self):
        buttons = [
            ("Load Folder", self.open_folder),
            ("Load Image(s)", self.open_images),
            ("Rename all images", self.rename_images),
        ]
        for text, command in buttons:
            tk.Button(self.top_row_frame, text=text, command=command).pack(
                side="left", padx=5
            )

        self.setup_prompt_entry()

    def setup_prompt_entry(self):
        tk.Button(self.top_row_frame, text="Edit Captioner Prompt", command=self.open_prompt_window).pack(side="left", padx=5)

    def open_prompt_window(self):
        prompt_window = tk.Toplevel(self.root)
        prompt_window.title("Edit Captioner Prompt")
        prompt_window.geometry("600x400")

        prompt_text = tk.Text(prompt_window, wrap="word", font=("Verdana", 14))
        prompt_text.pack(expand=True, fill="both", padx=10, pady=10)
        prompt_text.insert(1.0, self.prompt_text)

        def save_prompt():
            self.prompt_text = prompt_text.get(1.0, "end-1c")
            prompt_window.destroy()

        save_button = tk.Button(prompt_window, text="Save", command=save_prompt)
        save_button.pack(pady=10)

    def setup_trigger_entry(self):
        tk.Label(self.bottom_row_frame, text="Trigger Phrase:").pack(
            side="left", padx=5
        )
        self.trigger_entry = tk.Entry(self.bottom_row_frame, width=20)
        self.trigger_entry.pack(side="left", padx=5)

    def setup_model_dropdown(self):
        tk.Label(self.bottom_row_frame, text="Model:").pack(side="left", padx=5)
        models = [
            "Florence2",
            "GPT-4.1",
            "Pixtral",
            "Gemini 2.5 Flash",
            "Gemini 2.5 Pro",
            "Qwen2.5 72B",
            "Grok",
            
        ]
        self.model_dropdown = tk.OptionMenu(
            self.bottom_row_frame, self.selected_model, *models
        )
        self.model_dropdown.pack(side="left", padx=5)

    def setup_second_row(self):
        self.setup_trigger_entry()
        self.setup_model_dropdown()
        tk.Button(self.bottom_row_frame, text="Run", command=self.run_model).pack(
            side="left", padx=5
        )
        tk.Radiobutton(
            self.bottom_row_frame,
            text="For this image",
            variable=self.caption_mode,
            value="single",
        ).pack(side="left", padx=5)
        tk.Radiobutton(
            self.bottom_row_frame,
            text="For all empty captions",
            variable=self.caption_mode,
            value="all",
        ).pack(side="left", padx=5)

    def bind_events(self):
        self.image_list.bind("<<ListboxSelect>>", self.display_image)
        self.root.bind("<Control-s>", self.save_caption)
        self.trigger_entry.bind("<KeyRelease>", self.on_trigger_change)
        self.text_entry.bind("<Control-z>", self.undo_text)
        self.text_entry.bind("<Control-y>", self.redo_text)

    def run_model(self):
        model = self.selected_model.get()
        caption_mode = self.caption_mode.get()
        
        if caption_mode == "single":
            file_paths = [self.current_image_path]
            index = 0
        else:
            file_paths = list(self.file_map.values())
            index = self.index

        caption = on_run_pressed(
            self,
            caption_mode,
            model,
            file_paths,
            index,
            self.trigger_entry.get(),
            self.prompt_text,
        )
        self.text_entry.delete(1.0, "end")
        self.text_entry.insert(1.0, caption)

    def open_folder(self):
        try:
            folder_path = filedialog.askdirectory()
            if folder_path:
                self.current_folder = folder_path
                self.load_images_from_folder(folder_path)
                save_session(self)
        except Exception as e:
            print(f"Error opening folder: {e}")

    def load_images_from_folder(self, folder_path):
        for item in self.image_list.items:
            item.destroy()
        self.image_list.items = []
        self.file_map = {}
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
            self.file_map[file_name] = file_path
            item = self.image_list.insert(file_path, file_name)
            self.check_and_color_item(item, file_path)

    def open_images(self):
        try:
            file_types = "*.bmp *.jpg *.jpeg *.png"
            file_paths = filedialog.askopenfilenames(
                filetypes=[("Common Image Files", file_types), ("All", "*.*")]
            )
            file_paths = sort_files(file_paths)
            if file_paths:
                self.current_folder = os.path.dirname(file_paths[0])
                for item in self.image_list.items:
                    item.destroy()
                self.image_list.items = []
                self.file_map = {}
                for file_path in file_paths:
                    file_name = os.path.basename(file_path)
                    self.file_map[file_name] = file_path
                    item = self.image_list.insert(file_path, file_name)
                    self.check_and_color_item(item, file_path)
                save_session(self)
        except Exception as e:
            print(f"Error opening images: {e}")

    def rename_images(self):
        rename_files_to_numbers(self.current_folder)
        self.load_images_from_folder(self.current_folder)
        save_session(self)

    def display_image(self, event):
        try:
            self.save_caption()
            selection = self.image_list.curselection()
            if not selection:
                return
            self.text_entry.delete(1.0, "end")
            self.index = selection[0]
            file_name = self.image_list.get(self.index)
            file_path = self.file_map[file_name]
            self.current_image = file_name
            self.current_image_path = file_path
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            max_size = (int(screen_width / 2.5), int(screen_height / 1.5))

            with Image.open(file_path) as image:
                original_width, original_height = image.size
                aspect_ratio = original_width / original_height
                aspect_ratio_str = f"{aspect_ratio:.2f}"
                new_width, new_height = original_width, original_height
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

                # Update the resolution and aspect ratio label
                resolution_text = f"{original_width}x{original_height} ({aspect_ratio_str})"
                self.resolution_label.config(text=resolution_text)

                description_file = str(self.current_image_path).rsplit(".", 1)[0] + ".txt"
                if os.path.isfile(description_file):
                    with open(description_file, "r") as file:
                        description = file.read()
                        self.text_entry.insert(1.0, description)
                else:
                    self.text_entry.delete(1.0, "end")
                self.root.title(f"Yofardev Captioner - {self.current_image_path}")
        except Exception as e:
            print(f"Error loading image: {e}")
            messagebox.showinfo("Error", f"There was an error loading the image: {e}")

    def save_caption(self, event=None):
        try:
            description = self.text_entry.get(1.0, "end").strip()
            if description == "":
                return
            description_file = str(self.current_image_path).rsplit(".", 1)[0] + ".txt"
            save_caption_to_file(description, description_file)
            # After saving, check and color the item again
            item = self.image_list.items[self.index]
            self.check_and_color_item(item, self.current_image_path)
        except Exception as e:
            messagebox.showinfo(
                "Error", f"There was an error while saving the captions: {e}"
            )

    def on_trigger_change(self, event):
        save_session(self)

    def check_and_color_item(self, item, file_path):
        caption_file = os.path.splitext(file_path)[0] + ".txt"
        if not os.path.exists(caption_file) or os.path.getsize(caption_file) == 0:
            item.set_bg_color("gray15", fg="white")
        else:
            item.set_bg_color("gray25", fg="white")


if __name__ == "__main__":
    root = tk.Tk()
    app = Captioner(root)
    root.mainloop()
