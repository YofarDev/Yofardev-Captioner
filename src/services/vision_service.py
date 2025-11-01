import time

from src.models.florence2 import describe_image as describe_image_florence2
from src.models.open_ai import describe_image as describe_image
from src.models.pixtral import describe_image as describe_image_pixtral
from src.services.session_file import save_session
from src.utils.utils import load_file_as_string, save_caption_to_file


def get_caption(model, image_path, prompt):
    try:
        if model == "Florence2":
            caption = describe_image_florence2(image_path, prompt)
        elif model == "Pixtral":
            caption = describe_image_pixtral(image_path, prompt)
        elif model == "GPT-4.1":
            caption = describe_image(
                image_path,
                "https://models.github.ai/inference",
                "openai/gpt-4.1",
                "GITHUB_TOKEN",
                prompt,
            )
        elif model == "Qwen2.5 72B":
            caption = describe_image(
                image_path,
                "https://openrouter.ai/api/v1",
                "qwen/qwen2.5-vl-72b-instruct:free",
                "OPENROUTER_API_KEY",
                prompt,
            )
        elif model == "Gemini 2.5 Flash":
            caption = describe_image(
                image_path,
                "https://generativelanguage.googleapis.com/v1beta/",
                "gemini-2.5-flash",
                "GEMINI_API_KEY",
                prompt,
            )
        elif model == "Gemini 2.5 Pro":
            caption = describe_image(
                image_path,
                "https://generativelanguage.googleapis.com/v1beta/",
                "gemini-2.5-pro",
                "GEMINI_API_KEY",
                prompt,
            )
        elif model == "Grok":
            caption = describe_image(
                image_path,
                "https://openrouter.ai/api/v1",
                "x-ai/grok-4-fast:free",
                "OPENROUTER_API_KEY",
                prompt,
            )
        print(caption)
        return caption
    except Exception as e:
        print(f"Error getting caption: {e}")
        return None  # Return None on error to be handled by calling function


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


def on_run_pressed(self, caption_mode, model, image_paths, index, prompt, llm_queue, stop_event):
    caption = None
    if caption_mode == "single":
        try:
            caption = get_caption(model, image_paths[0], prompt)
            if caption:
                save_caption(caption, image_paths[0])
        except Exception as e:
            llm_queue.put(("ERROR", str(e)))
            return None
    else:
        total_images = len(image_paths)
        for i, img in enumerate(image_paths):
            if stop_event.is_set():
                llm_queue.put(("ERROR", "Caption generation cancelled."))
                break

            llm_queue.put(("PROGRESS", (i + 1, total_images)))
            
            # Check if the caption file is empty
            if load_file_as_string(img.rsplit(".", 1)[0] + ".txt") == "":
                if model not in ["Florence2"]:
                    debounce(self)
                try:
                    c = get_caption(model, img, prompt)
                    if c:
                        save_caption(c, img)
                        llm_queue.put(("UPDATE_CAPTION", (img, c))) # Update UI for this image
                    # If the current image is the one selected in the UI, update the caption
                    if i == index:
                        caption = c
                except Exception as e:
                    llm_queue.put(("ERROR", f"Error generating caption for {os.path.basename(img)}: {e}"))
                    # Continue to next image even if one fails
    return caption if caption is not None else ""
