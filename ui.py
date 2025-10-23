import glob
import os
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

import settings
from rename_images import rename_files_to_numbers
from session_file import load_session, save_session
from thumbnail import ThumbnailListbox
from utils import save_caption_to_file, sort_by_name, sort_files
from vision_service import on_run_pressed


class Captioner:
    def __init__(self, root):
        self.root = root
        self.file_map = {}
        self.current_folder = ""
        self.current_image = ""
        self.current_image_path = ""
        self.caption_mode = tk.StringVar(value="single")
        self.selected_model = tk.StringVar(value="Gemini 2.5 Flash")
        self.gpt_last_used = None
        self.index = 0
        self.prompt_text = "Describe this image as one paragraph, without mentionning the style nor the atmosphere."
        self.prompt_window = None
        self.search_replace_window = None
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

        # Add a label to display resolution and aspect ratio
        self.resolution_label = tk.Label(self.root, text="", font=("Arial", 10))
        self.resolution_label.pack(side="top", anchor="center", pady=5)

    def setup_text_entry(self):
        self.text_entry = tk.Text(self.root, height=16, width=85, wrap="word")
        self.text_entry.config(borderwidth=2, relief="groove")
        # Set the font and font size
        self.text_entry.config(
            font=("Verdana", 18)
        )  # Change "Helvetica" and 12 to your desired font and size
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
            font=("Arial", 10, "bold"),
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
            ("📂", self.open_folder),
            ("📷", self.open_images),
            ("🔄", self.refresh_images),
            ("Rename all images", self.rename_images),
            ("🔍 Search/Replace", self.open_search_replace_window),
        ]
        for text, command in buttons:
            tk.Button(self.top_row_frame, text=text, command=command).pack(
                side="left", padx=5
            )

        self.setup_prompt_entry()

    def refresh_images(self):
        if self.current_folder:
            self.load_images_from_folder(self.current_folder)

    def setup_prompt_entry(self):
        tk.Button(
            self.top_row_frame,
            text="Edit Captioner Prompt",
            command=self.open_prompt_window,
        ).pack(side="left", padx=5)

    def open_prompt_window(self):
        if self.prompt_window is not None and self.prompt_window.winfo_exists():
            self.prompt_window.focus()
            return

        self.prompt_window = tk.Toplevel(self.root)
        self.prompt_window.title("Edit Captioner Prompt")
        self.prompt_window.geometry("600x400")

        def save_prompt():
            self.prompt_text = prompt_text.get(1.0, "end-1c")
            save_session(self)
            self.prompt_window.destroy()

        def set_default_prompt():
            prompt_text.delete(1.0, "end")
            prompt_text.insert(
                1.0,
                "Describe this image as one paragraph, without mentionning the style nor the atmosphere.",
            )

        button_frame = tk.Frame(self.prompt_window)
        button_frame.pack(pady=10, side="top", fill="x")

        save_button = tk.Button(button_frame, text="Save", command=save_prompt)
        save_button.pack(side="left", padx=5)

        default_button = tk.Button(
            button_frame, text="Default", command=set_default_prompt
        )
        default_button.pack(side="left", padx=5)

        close_button = tk.Button(
            button_frame, text="Close", command=self.prompt_window.destroy
        )
        close_button.pack(side="right", padx=5)

        prompt_text = tk.Text(self.prompt_window, wrap="word", font=("Verdana", 14))
        prompt_text.pack(expand=True, fill="both", padx=10, pady=10)
        prompt_text.insert(1.0, self.prompt_text)

    def get_caption_files(self):
        """Get all caption txt files associated with loaded images."""
        caption_files = []
        for file_path in self.file_map.values():
            caption_file = os.path.splitext(file_path)[0] + ".txt"
            if os.path.exists(caption_file):
                caption_files.append(caption_file)
        return caption_files

    def search_in_files(self, search_text, case_sensitive):
        """Search for text in caption files and return matches."""
        if not search_text:
            return {}

        caption_files = self.get_caption_files()
        results = {}

        for caption_file in caption_files:
            try:
                with open(caption_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                matches = []
                for line_num, line in enumerate(lines, 1):
                    if case_sensitive:
                        count = line.count(search_text)
                    else:
                        count = line.lower().count(search_text.lower())

                    if count > 0:
                        matches.append((line_num, line.rstrip(), count))

                if matches:
                    results[os.path.basename(caption_file)] = matches
            except Exception as e:
                print(f"Error reading {caption_file}: {e}")

        return results

    def preview_replacements(
        self, search_text, replace_text, case_sensitive, preview_widget
    ):
        """Preview what will be changed before applying."""
        preview_widget.delete(1.0, "end")

        if not search_text:
            preview_widget.insert("end", "Please enter text to search for.\n")
            return 0

        results = self.search_in_files(search_text, case_sensitive)

        if not results:
            preview_widget.insert("end", "No matches found.\n")
            return 0

        total_matches = 0
        for filename, matches in results.items():
            file_match_count = sum(count for _, _, count in matches)
            total_matches += file_match_count
            preview_widget.insert(
                "end", f"\n{filename}: {file_match_count} match(es)\n", "filename"
            )

            for line_num, line, count in matches:
                if case_sensitive:
                    preview_line = line.replace(search_text, replace_text)
                else:
                    # Case-insensitive replacement
                    import re

                    pattern = re.compile(re.escape(search_text), re.IGNORECASE)
                    preview_line = pattern.sub(replace_text, line)

                preview_widget.insert("end", f"  Line {line_num}: ", "line_num")
                preview_widget.insert(
                    "end", f'"{line}" → "{preview_line}"\n', "preview"
                )

        preview_widget.insert(
            "end",
            f"\nTotal: {total_matches} match(es) in {len(results)} file(s)\n",
            "summary",
        )

        # Configure tags for better readability
        preview_widget.tag_config(
            "filename", foreground="blue", font=("Verdana", 12, "bold")
        )
        preview_widget.tag_config("line_num", foreground="green")
        preview_widget.tag_config("preview", foreground="black")
        preview_widget.tag_config(
            "summary", foreground="red", font=("Verdana", 11, "bold")
        )

        return total_matches

    def apply_replacements(self, search_text, replace_text, case_sensitive):
        """Apply search and replace to all caption files."""
        if not search_text:
            messagebox.showwarning("Warning", "Please enter text to search for.")
            return False

        caption_files = self.get_caption_files()
        modified_count = 0
        error_files = []

        for caption_file in caption_files:
            try:
                with open(caption_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Perform replacement
                if case_sensitive:
                    new_content = content.replace(search_text, replace_text)
                else:
                    import re

                    pattern = re.compile(re.escape(search_text), re.IGNORECASE)
                    new_content = pattern.sub(replace_text, content)

                # Only write if content changed
                if new_content != content:
                    with open(caption_file, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    modified_count += 1
            except Exception as e:
                error_files.append((os.path.basename(caption_file), str(e)))
                print(f"Error processing {caption_file}: {e}")

        # Show results
        if modified_count > 0:
            message = f"Successfully modified {modified_count} file(s)."
            if error_files:
                message += f"\n\nErrors in {len(error_files)} file(s):\n"
                for filename, error in error_files[:5]:  # Show first 5 errors
                    message += f"- {filename}: {error}\n"
            messagebox.showinfo("Success", message)

            # Refresh current image display if it was modified
            if self.current_image_path:
                current_caption_file = (
                    os.path.splitext(self.current_image_path)[0] + ".txt"
                )
                if current_caption_file in [
                    os.path.join(self.current_folder, os.path.basename(cf))
                    for cf in caption_files
                ]:
                    # Reload the caption for current image
                    if os.path.exists(current_caption_file):
                        with open(current_caption_file, "r", encoding="utf-8") as f:
                            self.text_entry.delete(1.0, "end")
                            self.text_entry.insert(1.0, f.read())

            return True
        else:
            if error_files:
                messagebox.showerror(
                    "Error", "Failed to modify files. Check console for details."
                )
            else:
                messagebox.showinfo("Info", "No changes were made (no matches found).")
            return False

    def open_search_replace_window(self):
        """Open the search and replace dialog window."""
        if not self.current_folder:
            messagebox.showwarning("Warning", "Please open a folder first.")
            return

        if (
            self.search_replace_window is not None
            and self.search_replace_window.winfo_exists()
        ):
            self.search_replace_window.focus()
            return

        self.search_replace_window = tk.Toplevel(self.root)
        self.search_replace_window.title("Search and Replace in Caption Files")
        self.search_replace_window.geometry("700x500")

        # Input frame
        input_frame = tk.Frame(self.search_replace_window)
        input_frame.pack(pady=10, padx=10, fill="x")

        # Search field
        tk.Label(input_frame, text="Search for:", font=("Verdana", 10)).grid(
            row=0, column=0, sticky="w", pady=5
        )
        search_entry = tk.Entry(input_frame, width=50, font=("Verdana", 10))
        search_entry.grid(row=0, column=1, pady=5, padx=5)

        # Replace field
        tk.Label(input_frame, text="Replace with:", font=("Verdana", 10)).grid(
            row=1, column=0, sticky="w", pady=5
        )
        replace_entry = tk.Entry(input_frame, width=50, font=("Verdana", 10))
        replace_entry.grid(row=1, column=1, pady=5, padx=5)

        # Case sensitive checkbox
        case_sensitive_var = tk.BooleanVar(value=False)
        case_checkbox = tk.Checkbutton(
            input_frame,
            text="Case sensitive",
            variable=case_sensitive_var,
            font=("Verdana", 10),
        )
        case_checkbox.grid(row=2, column=1, sticky="w", pady=5)

        # Preview frame
        preview_frame = tk.Frame(self.search_replace_window)
        preview_frame.pack(pady=10, padx=10, fill="both", expand=True)

        tk.Label(preview_frame, text="Preview:", font=("Verdana", 10, "bold")).pack(
            anchor="w"
        )

        # Preview text widget with scrollbar
        preview_text = tk.Text(
            preview_frame, wrap="word", font=("Verdana", 9), height=15
        )
        preview_scrollbar = tk.Scrollbar(preview_frame, command=preview_text.yview)
        preview_text.config(yscrollcommand=preview_scrollbar.set)
        preview_scrollbar.pack(side="right", fill="y")
        preview_text.pack(side="left", fill="both", expand=True)

        # Button frame
        button_frame = tk.Frame(self.search_replace_window)
        button_frame.pack(pady=10, fill="x")

        def on_preview():
            search_text = search_entry.get()
            replace_text = replace_entry.get()
            case_sensitive = case_sensitive_var.get()
            self.preview_replacements(
                search_text, replace_text, case_sensitive, preview_text
            )

        def on_replace_all():
            search_text = search_entry.get()
            replace_text = replace_entry.get()
            case_sensitive = case_sensitive_var.get()

            # Confirm before replacing
            if messagebox.askyesno(
                "Confirm", "Are you sure you want to replace all occurrences?"
            ):
                if self.apply_replacements(search_text, replace_text, case_sensitive):
                    # Refresh preview after replacement
                    on_preview()

        preview_button = tk.Button(
            button_frame, text="Preview", command=on_preview, font=("Verdana", 10)
        )
        preview_button.pack(side="left", padx=5)

        replace_button = tk.Button(
            button_frame,
            text="Replace All",
            command=on_replace_all,
            font=("Verdana", 10),
        )
        replace_button.pack(side="left", padx=5)

        close_button = tk.Button(
            button_frame,
            text="Close",
            command=self.search_replace_window.destroy,
            font=("Verdana", 10),
        )
        close_button.pack(side="right", padx=5)

        # Initial message
        preview_text.insert(
            "end",
            "Enter search text and click 'Preview' to see what will be changed.\n",
        )

    def setup_model_dropdown(self):
        tk.Label(self.bottom_row_frame, text="Model:").pack(side="left", padx=5)
        models = [
            "Gemini 2.5 Flash",
            "Qwen2.5 72B",
            "GPT-4.1",
            "Pixtral",
            "Gemini 2.5 Pro",
            "Grok",
            "Florence2",
        ]
        self.model_dropdown = tk.OptionMenu(
            self.bottom_row_frame, self.selected_model, *models
        )
        self.model_dropdown.pack(side="left", padx=5)

    def setup_second_row(self):
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
            "",  # Removed self.trigger_entry.get()
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

                description_file = (
                    str(self.current_image_path).rsplit(".", 1)[0] + ".txt"
                )
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
