from florence2 import describe_image as describe_image_florence2
from pixtral import describe_image as describe_image_pixtral
from open_ai import describe_image as describe_image
import time
from session_file import save_session
from utils import (
    load_file_as_string,
    save_caption_to_file,
)


def get_caption(model, image_path, trigger_phrase):
    try:
        if model == "Florence2":
            caption = describe_image_florence2(image_path, trigger_phrase)
        elif model == "Pixtral":
            caption = describe_image_pixtral(image_path, trigger_phrase)
        elif model == "GPT4o":
            caption = describe_image(image_path, trigger_phrase, "https://models.inference.ai.azure.com", "gpt-4o", "GITHUB_API_KEY")
        elif model == "Qwen2 72B":
            caption = describe_image(image_path, trigger_phrase, "https://openrouter.ai/api/v1", "qwen/qwen-2-vl-72b-instruct", "OPENROUTER_API_KEY")
        elif model == "Gemini 2.0 Flash":
            caption = describe_image(image_path, trigger_phrase, "https://generativelanguage.googleapis.com/v1beta/", "gemini-2.0-flash-exp", "GEMINI_API_KEY")
        print(caption)
        return caption
    except Exception as e:
        print(f"Error getting caption: {e}")
        return ""



def save_caption(caption, image_path):
    save_caption_to_file(caption, image_path.rsplit(".", 1)[0] + ".txt")
    
def debounce(self):
    current_time = time.time()
    time_diff = 10
    if self.gpt_last_used:
        time_diff = current_time - self.gpt_last_used
    if time_diff < 6:
        time.sleep(6 - time_diff)
    self.gpt_last_used = current_time
    save_session(self)
    

def on_run_pressed(self, caption_mode, model, image_paths, index, trigger_phrase):
    caption = ''
    if caption_mode == "single":
        caption = get_caption(model, image_paths[index], trigger_phrase)
        save_caption(caption, image_paths[index])
    else:
        for i, img in enumerate(image_paths):
            if load_file_as_string(img.rsplit(".", 1)[0] + ".txt") == "":
                if model == "GPT4o":
                    debounce(self)
                c = get_caption(model, img, trigger_phrase)
                save_caption(c, img)
                if i == index:
                    caption = c
    return caption

                    
