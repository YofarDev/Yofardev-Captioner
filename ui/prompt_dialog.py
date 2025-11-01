import tkinter as tk

from src.services.session_file import save_session


class PromptDialog:
    """Handles the prompt editing dialog window."""
    
    def __init__(self, captioner):
        self.captioner = captioner
        self.prompt_window = None
        self.prompt_text = "Describe this image as one paragraph, without mentionning the style nor the atmosphere."
    
    def open_prompt_window(self):
        """Open the prompt editing window."""
        if self.prompt_window is not None and self.prompt_window.winfo_exists():
            self.prompt_window.focus()
            return

        self.prompt_window = tk.Toplevel(self.captioner.root)
        self.prompt_window.title("Edit Captioner Prompt")
        self.prompt_window.geometry("600x400")

        def save_prompt():
            self.prompt_text = prompt_text.get(1.0, "end-1c")
            save_session(self.captioner)
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
