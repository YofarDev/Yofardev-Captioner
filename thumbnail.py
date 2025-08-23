import tkinter as tk

from PIL import Image,  ImageTk


class ThumbnailItem(tk.Frame):
    def __init__(
            self, parent, image_path, text, thumbnail_size=(50, 50),listbox=None
    ):
        super().__init__(parent, bd=1, relief="solid")
        
        
        # Store the listbox reference
        self.listbox = listbox

        # Create and resize thumbnail to square aspect ratio
        image = Image.open(image_path)
        image = self._resize_to_square(image, thumbnail_size[0])

        photo = ImageTk.PhotoImage(image)

        # Create and pack widgets
        self.image_label = tk.Label(self, image=photo)
        self.image_label.image = photo  # Keep reference
        self.image_label.pack(side="left", padx=2, pady=2)
        self.image_label.bind("<Button-1>", self._on_click)

        self.text_label = tk.Label(self, text=text, anchor="w", bg='gray25', fg='white')
        self.text_label.pack(side="left", fill="x", expand=True, padx=2)
        self.text_label.bind("<Button-1>", self._on_click)

        self.configure(bg="gray25")
        
    def _on_click(self, event):
        if self.listbox:
            self.listbox._on_select(self.listbox.items.index(self))


    

    def set_bg_color(self, color, fg="white"):
        self.configure(bg=color)
        self.text_label.configure(bg=color, fg=fg)

    def _resize_to_square(self, image, size):
        """Resize image to a square aspect ratio using BoxFit.cover effect"""
        width, height = image.size
        ratio = max(size / width, size / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)

        # Crop the image to fit the square
        left = (new_width - size) / 2
        top = (new_height - size) / 2
        right = (new_width + size) / 2
        bottom = (new_height + size) / 2
        cropped_image = resized_image.crop((left, top, right, bottom))

        return cropped_image
    

class ThumbnailListbox(tk.Frame):
    def __init__(self, parent, captioner, width=300):
        super().__init__(parent)
        self.captioner = captioner

        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self, width=width)
        self.scrollbar = tk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas)

        # Configure canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas_frame = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )

        # Pack widgets
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind events
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Initialize variables
        self.items = []
        self.selected_index = None
        self.selected_item = None

    def insert(self, image_path, text):
        item = ThumbnailItem(self.scrollable_frame, image_path, text, listbox=self)
        item.pack(fill="x", padx=2, pady=1)
        item.bind("<Button-1>", lambda e, idx=len(self.items): self._on_select(idx))
        self.items.append(item)
        return item

    def delete(self, first, last=None):
        # Convert string indices to integers
        if first == "0":
            first = 0
        if first == "end":
            first = len(self.items) - 1

        if last == "end":
            last = len(self.items) - 1
        elif last is None:
            last = first

        for idx in range(first, last + 1):
            if idx < len(self.items):
                self.items[idx].destroy()

        self.items = self.items[:first] + self.items[last + 1 :]
        self.selected_index = None
        self.selected_item = None

    def _on_select(self, index):
        if self.selected_item:
            try:
                # Get the file path of the deselected item
                file_name = self.get(self.selected_index)
                file_path = self.captioner.file_map[file_name]
                # Check and restore the correct background color
                self.captioner.check_and_color_item(self.selected_item, file_path)
            except (tk.TclError, KeyError):
                # Ignore the error if the item has been destroyed or not in file_map
                pass

        if 0 <= index < len(self.items):
            self.selected_index = index
            self.selected_item = self.items[index]
            self.selected_item.configure(bg="lavender blush")
            self.selected_item.text_label.configure(bg='lavender blush', fg='black')

            # Generate virtual event
            self.event_generate("<<ListboxSelect>>")

    def curselection(self):
        return (self.selected_index,) if self.selected_index is not None else ()

    def get(self, first, last=None):
        # Handle string indices
        if isinstance(first, str):
            if first == "0":
                first = 0
            elif first == "end":
                first = len(self.items) - 1

        if isinstance(last, str) and last == "end":
            last = len(self.items) - 1

        # If only first parameter is provided and it's an integer
        if last is None and isinstance(first, int):
            return self.items[first].text_label["text"]

        # If both parameters are provided, return a list of items
        if last is not None:
            return [item.text_label["text"] for item in self.items[first : last + 1]]

        # If only first parameter is provided and we want all items
        return [item.text_label["text"] for item in self.items]

    def select_set(self, first, last=None):
        # Convert string indices to integers
        if isinstance(first, str):
            if first == "0":
                first = 0
            elif first == "end":
                first = len(self.items) - 1

        if isinstance(last, str) and last == "end":
            last = len(self.items) - 1
        elif last is None:
            last = first

        for idx in range(first, last + 1):
            if 0 <= idx < len(self.items):
                self._on_select(idx)

    def select_clear(self, first, last=None):
        if self.selected_item:
            self.selected_item.configure(bg="white")
            self.selected_index = None
            self.selected_item = None

    def size(self):
        return len(self.items)

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def see(self, index):
        """Scroll to make the item at index visible"""
        if 0 <= index < len(self.items):
            item = self.items[index]
            bbox = self.canvas.bbox(self.canvas_frame)
            if bbox:
                item_y = item.winfo_y()
                #canvas_height = self.canvas.winfo_height()
                self.canvas.yview_moveto(item_y / bbox[3])
