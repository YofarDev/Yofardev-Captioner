import glob
import os
import tkinter as tk
from tkinter import Entry, Listbox, filedialog, messagebox

from PIL import Image, ImageTk

from rename_images import rename_files_to_numbers
from session_file import load_session, save_session
from utils import save_caption_to_file, sort_files, sort_by_name
from vision_service import on_run_pressed


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
        self.setup_ui()
        load_session(self)

    def setup_ui(self):
        self.setup_window()
        self.setup_frames()
        self.setup_image_list()
        self.setup_image_display()
        self.setup_text_entry()
        self.setup_control_frame()
        self.bind_events()

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = int(screen_width / 1.5)
        height = int(screen_height / 1.5)
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

        # ... (Existing code remains unchanged)

    # ... (Existing methods up to setup_image_list remain unchanged)
    def setup_image_list(self):
        self.image_list = Listbox(self.frame_list, width=30)
        self.setup_scrollbars()
        self.image_list.pack(side="left", fill="both")

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

    def setup_text_entry(self):
        self.text_entry = tk.Text(self.root, height=6, width=85, wrap="word")
        self.text_entry.config(borderwidth=5, relief="groove")
        self.text_entry.pack(side="bottom", fill="both")

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
            ("Rename Images", self.rename_images),
        ]
        for text, command in buttons:
            tk.Button(self.top_row_frame, text=text, command=command).pack(
                side="left", padx=5
            )

    def setup_trigger_entry(self):
        tk.Label(self.bottom_row_frame, text="Trigger Phrase:").pack(
            side="left", padx=5
        )
        self.trigger_entry = Entry(self.bottom_row_frame, width=20)
        self.trigger_entry.pack(side="left", padx=5)

    def setup_model_dropdown(self):
        tk.Label(self.bottom_row_frame, text="Model:").pack(side="left", padx=5)
        models = [
            "Florence2",
            "GPT4o",
            "Pixtral",
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

    def run_model(self):
        model = self.selected_model.get()
        file_paths = list(self.file_map.values())
        caption = on_run_pressed(
            self,
            self.caption_mode.get(),
            model,
            file_paths,
            self.image_list.curselection()[0],
            self.trigger_entry.get(),
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
        self.image_list.delete("0", "end")
        self.file_map = {}
        file_types = ("*.bmp", "*.jpg", "*.jpeg", "*.png")
        for file_type in file_types:
            # Get all files of the current type and sort them
            files = glob.glob(os.path.join(folder_path, file_type))
            sorted_files = sort_by_name(files)
            for file_path in sorted_files:
                file_name = os.path.basename(file_path)
                self.file_map[file_name] = file_path
                self.image_list.insert("end", file_name)

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

    def rename_images(self):
        rename_files_to_numbers(self.current_folder)
        self.load_images_from_folder(self.current_folder)
        save_session(self)

    def update_list_colors(self):
        self.image_list.itemconfig(0, {"bg": "white"})
        for i in range(self.image_list.size()):
            if self.image_list.get(i) == self.current_image:
                self.image_list.itemconfig(i, {"bg": "light blue"})
            else:
                self.image_list.itemconfig(i, {"bg": "black"})

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
            self.update_list_colors()
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
        except Exception as e:
            messagebox.showinfo(
                "Error", f"There was an error while saving the captions: {e}"
            )

    def on_trigger_change(self, event):
        save_session(self)


if __name__ == "__main__":
    root = tk.Tk()
    app = Captioner(root)
    root.mainloop()

