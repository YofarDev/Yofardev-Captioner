import os
import re
import tkinter as tk
from tkinter import messagebox


class SearchReplaceDialog:
    """Handles search and replace functionality in caption files."""
    
    def __init__(self, captioner):
        self.captioner = captioner
        self.search_replace_window = None
    
    def get_caption_files(self):
        """Get all caption txt files associated with loaded images."""
        caption_files = []
        for file_path in self.captioner.file_map.values():
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
            if self.captioner.current_image_path:
                current_caption_file = (
                    os.path.splitext(self.captioner.current_image_path)[0] + ".txt"
                )
                if current_caption_file in [
                    os.path.join(self.captioner.current_folder, os.path.basename(cf))
                    for cf in caption_files
                ]:
                    # Reload the caption for current image
                    if os.path.exists(current_caption_file):
                        with open(current_caption_file, "r", encoding="utf-8") as f:
                            self.captioner.caption_editor.text_entry.delete(1.0, "end")
                            self.captioner.caption_editor.text_entry.insert(1.0, f.read())

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
        if not self.captioner.current_folder:
            messagebox.showwarning("Warning", "Please open a folder first.")
            return

        if (
            self.search_replace_window is not None
            and self.search_replace_window.winfo_exists()
        ):
            self.search_replace_window.focus()
            return

        self.search_replace_window = tk.Toplevel(self.captioner.root)
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