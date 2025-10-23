import os
import subprocess
import tkinter as tk

from vision_service import on_run_pressed


class ModelControls:
    """Handles AI model selection and execution controls."""

    def __init__(self, captioner):
        self.captioner = captioner
        self.caption_mode = tk.StringVar(value="single")
        self.selected_model = tk.StringVar(value="Gemini 2.5 Flash")
        self.gpt_last_used = None
        self.control_frame = None
        self.top_row_frame = None
        self.bottom_row_frame = None
        self.model_dropdown = None

    def setup_control_frame(self):
        """Setup the main control frame with two rows."""
        self.control_frame = tk.Frame(self.captioner.root)
        self.control_frame.pack(side="bottom", fill="x", pady=10)

        # Create two separate frames for the rows
        self.top_row_frame = tk.Frame(self.control_frame)
        self.top_row_frame.pack(fill="x", pady=(0, 5))

        self.bottom_row_frame = tk.Frame(self.control_frame)
        self.bottom_row_frame.pack(fill="x")

        self.setup_first_row()
        self.setup_second_row()

    def setup_first_row(self):
        """Setup the first row of controls (file operations and search)."""
        buttons = [
            ("📂", self.captioner.image_manager.open_folder),
            ("📷", self.captioner.image_manager.open_images),
            ("🔄", self.captioner.image_manager.refresh_images),
            ("Rename all files", self.captioner.image_manager.rename_images),
            (
                "🔍 Search/Replace",
                self.captioner.search_replace_dialog.open_search_replace_window,
            ),
            ("Open current", self.open_current_folder),
        ]
        for text, command in buttons:
            tk.Button(self.top_row_frame, text=text, command=command).pack(
                side="left", padx=5
            )

        self.setup_prompt_entry()

    def setup_prompt_entry(self):
        """Setup the prompt editing button."""
        tk.Button(
            self.top_row_frame,
            text="Edit Prompt",
            command=self.captioner.prompt_dialog.open_prompt_window,
        ).pack(side="left", padx=5)

    def setup_model_dropdown(self):
        """Setup the model selection dropdown."""
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
        """Setup the second row of controls (model selection and run)."""
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

    def open_current_folder(self):
        """Open the current folder in the system file explorer."""
        if self.captioner.current_folder and os.path.exists(
            self.captioner.current_folder
        ):
            try:
                subprocess.run(["open", self.captioner.current_folder])
            except Exception as e:
                print(f"Error opening folder: {e}")
        else:
            print("No folder is currently open")

    def run_model(self):
        """Execute the selected AI model for captioning."""
        model = self.selected_model.get()
        caption_mode = self.caption_mode.get()

        if caption_mode == "single":
            file_paths = [self.captioner.current_image_path]
            index = 0
        else:
            file_paths = list(self.captioner.file_map.values())
            index = self.captioner.index

        caption = on_run_pressed(
            self.captioner,
            caption_mode,
            model,
            file_paths,
            index,
            self.captioner.prompt_dialog.prompt_text,
        )
        self.captioner.caption_editor.set_caption_text(caption)
