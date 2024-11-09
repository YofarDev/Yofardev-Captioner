from florence2 import describe_image as describe_image_florence2
from gpt4o import describe_image as describe_image_gpt4o
from pixtral import describe_image as describe_image_pixtral
from gemini import describe_image as describe_image_gemini
import time
from session_file import save_session
from utils import (
    load_file_as_string,
    rewrite_caption_with_trigger_phrase,
    save_caption_to_file,
)


def get_caption(model, image_path, trigger_phrase):
    try:
        if model == "Florence2":
            caption = describe_image_florence2(image_path, trigger_phrase)
        elif model == "Pixtral":
            caption = describe_image_pixtral(image_path, trigger_phrase)
        elif model == "GPT4o":
            caption = describe_image_gpt4o(image_path, trigger_phrase)
        elif model == "Gemini":
            caption = describe_image_gemini(image_path, trigger_phrase)
        print(caption)
        return caption
    except Exception as e:
        print(f"Error getting caption: {e}")
        return ""



def save_caption(caption, trigger_phrase, image_path):
    vanilla_caption = caption
    if trigger_phrase != "":
        caption = rewrite_caption_with_trigger_phrase(vanilla_caption, trigger_phrase)
    else:
        caption = vanilla_caption
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
        save_caption(caption, trigger_phrase, image_paths[index])
    else:
        for i, img in enumerate(image_paths):
            if load_file_as_string(img.rsplit(".", 1)[0] + ".txt") == "":
                if model == "GPT4o":
                    debounce(self)
                c = get_caption(model, img, trigger_phrase)
                save_caption(c, trigger_phrase, img)
                if i == index:
                    caption = c
    return caption

                    
