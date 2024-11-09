import tkinter as tk

from ui import Captioner


def main():
    root = tk.Tk()
    Captioner(root)
    root.mainloop()


if __name__ == "__main__":
    main()
import tkinter as tk
from ui_components import Captioner

if __name__ == "__main__":
    root = tk.Tk()
    app = Captioner(root)
    root.mainloop()
