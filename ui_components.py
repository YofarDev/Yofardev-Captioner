import tkinter as tk
from tkinter import Entry, Listbox, filedialog, messagebox
from PIL import Image, ImageTk
from image_handling import load_images_from_folder, display_image, update_list_colors
from session_management import save_session, load_session
from control_handlers import run_florence2, open_folder, open_images, save_caption, on_trigger_change
from florence2_inference import run_single, run_multiple
from utils import sort_files, save_caption_to_file, check_file_exists

class Captioner:
    def __init__(self, root):
        self.root = root
        self.file_map = {}
        self.current_folder = ""
        self.current_image = ""
        self.current_image_path = ""
        self.florence2_mode = tk.StringVar(value="single")
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
        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))

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
        self.setup_trigger_entry()
        self.setup_buttons()

    def setup_trigger_entry(self):
        tk.Label(self.control_frame, text="Trigger Phrase:").pack(side="left", padx=5)
        self.trigger_entry = Entry(self.control_frame, width=20)
        self.trigger_entry.pack(side="left", padx=5)
        
    def setup_buttons(self):
        buttons = [
            ("Load Folder", self.open_folder),
            ("Load Image(s)", self.open_images),
            ("Run Florence2", self.run_florence2),
        ]
        for text, command in buttons:
            tk.Button(self.control_frame, text=text, command=command).pack(
                side="left", padx=5
            )
        tk.Radiobutton(self.control_frame, text="For this image", variable=self.florence2_mode, value="single").pack(side="left", padx=5)
        tk.Radiobutton(self.control_frame, text="For all empty captions", variable=self.florence2_mode, value="all").pack(side="left", padx=5)

    def run_florence2(self):
        if self.florence2_mode.get() == "single":
            caption = run_single(self.current_image_path, self.trigger_entry.get())
            self.text_entry.delete(1.0, "end")
            self.text_entry.insert(1.0, caption)    
        else:
            file_paths = list(self.file_map.values())
            run_multiple(file_paths, self.trigger_entry.get())

    def open_folder(self):
        try:
            folder_path = filedialog.askdirectory()
            if folder_path:
                self.current_folder = folder_path
                self.load_images_from_folder(folder_path)
                self.save_session()
        except Exception as e:
            print(f"Error opening folder: {e}")
            pass

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
                self.save_session()
        except Exception as e:
            print(f"Error opening images: {e}")
            pass

    def bind_events(self):
        self.image_list.bind("<<ListboxSelect>>", display_image)
        self.root.bind("<Control-s>", save_caption)
        self.trigger_entry.bind("<KeyRelease>", on_trigger_change)
