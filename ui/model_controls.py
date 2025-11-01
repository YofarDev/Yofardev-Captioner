import os
import subprocess
import tkinter as tk
import threading
import queue

from src.services.vision_service import on_run_pressed


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
        self.llm_queue = queue.Queue()
        self.llm_thread = None
        self.stop_llm_generation = threading.Event()
        self.run_button = None # Added to disable during LLM generation
        self.progress_label = None # Added for LLM progress

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
        self.run_button = tk.Button(self.bottom_row_frame, text="Run", command=self.run_model)
        self.run_button.pack(side="left", padx=5)
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
        self.progress_label = tk.Label(self.bottom_row_frame, text="", font=("Arial", 10), fg="green")
        self.progress_label.pack(side="left", padx=5)
        self.captioner.root.after(100, self._process_llm_queue)

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
        """Execute the selected AI model for captioning in a background thread."""
        self.run_button.config(state=tk.DISABLED) # Disable button during processing
        self.progress_label.config(text="Generating caption...")
        self.stop_llm_generation.set() # Signal any existing thread to stop
        if self.llm_thread and self.llm_thread.is_alive():
            self.llm_thread.join() # Wait for the thread to finish

        self.llm_queue = queue.Queue()
        self.stop_llm_generation.clear() # Reset the stop event

        model = self.selected_model.get()
        caption_mode = self.caption_mode.get()

        if caption_mode == "single":
            file_paths = [self.captioner.current_image_path]
            index = 0
        else:
            file_paths = list(self.captioner.file_map.values())
            index = self.captioner.index

        self.llm_thread = threading.Thread(
            target=self._generate_captions_in_background,
            args=(caption_mode, model, file_paths, index, self.captioner.prompt_dialog.prompt_text)
        )
        self.llm_thread.daemon = True
        self.llm_thread.start()
        
        # Schedule queue processing to start
        self.captioner.root.after(100, self._process_llm_queue)

    def _generate_captions_in_background(self, caption_mode, model, file_paths, index, prompt):
        """Generate captions in a background thread."""
        caption = on_run_pressed(
            self.captioner,
            caption_mode,
            model,
            file_paths,
            index,
            prompt,
            self.llm_queue, # Pass the queue to the service
            self.stop_llm_generation # Pass the stop event
        )
        self.llm_queue.put(("COMPLETED", caption)) # Sentinel value for completion

    def _process_llm_queue(self):
        """Process LLM results from the queue and update the UI."""
        generation_complete = False
        try:
            while not self.llm_queue.empty():
                message_type, data = self.llm_queue.get_nowait()
                if message_type == "COMPLETED":
                    final_caption = data
                    self.captioner.caption_editor.set_caption_text(final_caption)
                    self.run_button.config(state=tk.NORMAL) # Re-enable button
                    self.progress_label.config(text="Caption generation complete.")
                    print("LLM caption generation complete.")
                    generation_complete = True
                elif message_type == "PROGRESS":
                    current, total = data
                    self.progress_label.config(text=f"Generating caption... {current}/{total}")
                elif message_type == "UPDATE_CAPTION":
                    file_path, caption_text = data
                    # Update the UI for a specific image if it's currently displayed
                    if self.captioner.current_image_path == file_path:
                        self.captioner.caption_editor.set_caption_text(caption_text)
                elif message_type == "ERROR":
                    error_message = data
                    self.progress_label.config(text=f"Error: {error_message}", fg="red")
                    self.run_button.config(state=tk.NORMAL)
                    print(f"LLM generation error: {error_message}")
                    generation_complete = True

        except queue.Empty:
            pass # No items in queue yet

        # Check if generation is complete
        if generation_complete:
            print("Caption generation finished - stopping queue processing.")
            # Don't reschedule
        elif self.llm_thread and not self.llm_thread.is_alive() and self.llm_queue.empty():
            print("Thread finished and queue empty - cleaning up.")
            self.run_button.config(state=tk.NORMAL)
            self.progress_label.config(text="")
        else:
            # Continue processing if thread is alive or queue has items
            self.captioner.root.after(100, self._process_llm_queue) # Schedule next check
