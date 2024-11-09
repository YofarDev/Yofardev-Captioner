import json
from utils import check_file_exists

def save_session(self):
    session_data = {
        "trigger_phrase": self.trigger_entry.get(),
        "current_folder": self.current_folder,
        "current_image": self.current_image,
        "file_map": self.file_map,
    }
    with open("session.json", "w") as f:
        json.dump(session_data, f)

def load_session(self):
    try:
        with open("session.json", "r") as f:
            session_data = json.load(f)
        self.file_map = session_data.get("file_map", {})
        for file_name, file_path in self.file_map.items():
            if not check_file_exists(file_path):
                return     
        self.trigger_entry.insert(0, session_data.get("trigger_phrase", ""))
        self.current_folder = session_data.get("current_folder", "")
        self.current_image = session_data.get("current_image", "")

        if self.current_folder:
            load_images_from_folder(self, self.current_folder)

        if self.current_image:
            self.image_list.select_set(
                self.image_list.get(0, "end").index(self.current_image)
            )
            display_image(self, None)
    except FileNotFoundError:
        print("No previous session found.")
    except json.JSONDecodeError:
        print("Error decoding session file.")
