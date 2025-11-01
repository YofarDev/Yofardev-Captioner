import os
from pathlib import Path
from tkinter import Button, Entry, Label, Toplevel, messagebox

from dotenv import load_dotenv, set_key


def load_env_file():
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Create an empty .env file if it doesn't exist
        env_path.touch()


def open_settings(self):
    load_env_file()

    keys = ["GITHUB_API_KEY", "MISTRAL_API_KEY", "GEMINI_API_KEY"]
    values = {key: os.getenv(key, "") for key in keys}

    def save_settings():
        for key, entry in entries.items():
            value = entry.get()
            set_key(".env", key, value)
        messagebox.showinfo("Success", "API keys saved successfully.")

    # Create a popup window
    popup = Toplevel()
    popup.title("Edit API Keys")

    entries = {}
    for idx, (key, value) in enumerate(values.items()):
        Label(popup, text=key).grid(row=idx, column=0)
        entry = Entry(popup, width=50)
        entry.grid(row=idx, column=1)
        entry.insert(0, value)
        entries[key] = entry

    save_button = Button(popup, text="Save", command=save_settings)
    save_button.grid(row=len(keys), column=0, columnspan=2)
