import tkinter as tk

import settings
from session_file import load_session

from .caption_editor import CaptionEditor
from .image_manager import ImageManager
from .model_controls import ModelControls
from .prompt_dialog import PromptDialog
from .search_replace_dialog import SearchReplaceDialog


class Captioner:
    """Main application window and orchestration."""
    
    def __init__(self, root):
        self.root = root
        
        # Shared state
        self.file_map = {}
        self.current_folder = ""
        self.current_image = ""
        self.current_image_path = ""
        self.index = 0
        
        # Initialize components
        self.caption_editor = CaptionEditor(self)
        self.image_manager = ImageManager(self)
        self.model_controls = ModelControls(self)
        self.prompt_dialog = PromptDialog(self)
        self.search_replace_dialog = SearchReplaceDialog(self)
        
        # Setup UI
        self.setup_ui()
        
        # Load session
        load_session(self)

    def setup_ui(self):
        """Setup the user interface."""
        self.setup_window()
        self.setup_frames()
        self.setup_image_list()
        self.setup_image_display()
        self.setup_control_frame()
        self.setup_text_entry()
        self.setup_settings_icon()
        self.bind_events()

    def center_window(self):
        """Center the window on the screen."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = int(screen_width / 1.5)
        height = int(screen_height / 1.2)
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry("%dx%d+%d+%d" % (width, height, x, y))

    def setup_window(self):
        """Setup the main window properties."""
        self.root.title("Yofardev Captioner")
        self.center_window()
        self.root.resizable(False, False)

    def setup_frames(self):
        """Setup the main frames."""
        self.image_manager.frame_list = tk.Frame(self.root)
        self.image_manager.frame_list.pack(side="left", fill="y")

    def setup_image_list(self):
        """Setup the image list component."""
        self.image_manager.setup_image_list()

    def setup_image_display(self):
        """Setup the image display component."""
        self.image_manager.setup_image_display()

    def setup_text_entry(self):
        """Setup the text entry component."""
        self.caption_editor.setup_text_entry()

    def setup_control_frame(self):
        """Setup the control frame component."""
        self.model_controls.setup_control_frame()

    def setup_settings_icon(self):
        """Create a text button for settings."""
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
        """Open the settings dialog."""
        settings.open_settings(self)

    def bind_events(self):
        """Bind keyboard shortcuts and events."""
        self.image_manager.image_list.bind("<<ListboxSelect>>", self.image_manager.display_image)
        self.root.bind("<Control-s>", self.caption_editor.save_caption)
        self.caption_editor.text_entry.bind("<Control-z>", self.caption_editor.undo_text)
        self.caption_editor.text_entry.bind("<Control-y>", self.caption_editor.redo_text)
    
    def check_and_color_item(self, item, file_path):
        """Delegate to image_manager for backward compatibility."""
        self.image_manager.check_and_color_item(item, file_path)
    
    def load_images_from_folder(self, folder_path):
        """Delegate to image_manager for backward compatibility."""
        self.image_manager.load_images_from_folder(folder_path)
    
    def display_image(self, event):
        """Delegate to image_manager for backward compatibility."""
        self.image_manager.display_image(event)
    
    @property
    def gpt_last_used(self):
        """Delegate to model_controls for backward compatibility."""
        return self.model_controls.gpt_last_used
    
    @gpt_last_used.setter
    def gpt_last_used(self, value):
        """Delegate to model_controls for backward compatibility."""
        self.model_controls.gpt_last_used = value
    
    @property
    def selected_model(self):
        """Delegate to model_controls for backward compatibility."""
        return self.model_controls.selected_model
    
    @property
    def prompt_text(self):
        """Delegate to prompt_dialog for backward compatibility."""
        return self.prompt_dialog.prompt_text
    
    @prompt_text.setter
    def prompt_text(self, value):
        """Delegate to prompt_dialog for backward compatibility."""
        self.prompt_dialog.prompt_text = value