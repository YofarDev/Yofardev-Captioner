from email.mime import image
import os
from glob import glob
from unittest.mock import patch

import torch
from huggingface_hub import snapshot_download
from PIL import Image
from transformers import AutoModelForCausalLM, AutoProcessor
from transformers.dynamic_module_utils import get_imports
from utils import rewrite_caption_with_trigger_phrase, save_caption_to_file, load_file_as_string

def fixed_get_imports(filename: str | os.PathLike) -> list[str]:
    if not str(filename).endswith("modeling_florence2.py"):
        return get_imports(filename)
    imports = get_imports(filename)
    imports.remove("flash_attn")
    return imports


# Function to download and load the Florence-2 model
def download_and_load_model(model_name="microsoft/Florence-2-large"):
    print("Checking device...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # device = 'cpu'
    print(f"Device available : {device}")
    model_path = os.path.join("models", model_name.replace("/", "_"))
    if not os.path.exists(model_path):
        print(f"Downloading {model_name} model to: {model_path}")
        snapshot_download(
            repo_id=model_name, local_dir=model_path, local_dir_use_symlinks=False
        )
    print(f"Loading model {model_name}...")
    with patch(
        "transformers.dynamic_module_utils.get_imports", fixed_get_imports
    ):  # Workaround for unnecessary flash_attn requirement
        model = AutoModelForCausalLM.from_pretrained(
            model_path, trust_remote_code=True
        ).to(device)
        processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
    print("Model loaded.")
    return model, processor


def load_image_paths_from_folder(folder_path):
    valid_image_extensions = ["jpg", "jpeg", "png"]
    image_paths = []
    for ext in valid_image_extensions:
        for image_path in glob(os.path.join(folder_path, f"*.{ext}")):
            txt_path = os.path.splitext(image_path)[0] + ".txt"
            if not os.path.exists(txt_path):
                image_paths.append(image_path)
    return image_paths


def run_model_batch(
    image_paths,
    model,
    processor,
    task="caption",
    num_beams=3,
    max_new_tokens=1024,
    detail_mode=3,
):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    prompts = {1: "<CAPTION>", 2: "<DETAILED_CAPTION>", 3: "<MORE_DETAILED_CAPTION>"}
    prompt = prompts.get(detail_mode, "<MORE_DETAILED_CAPTION>")
    inputs = {"input_ids": [], "pixel_values": []}
    for image_path in image_paths:
        image_pil = Image.open(image_path).convert("RGB")
        input_data = processor(
            text=prompt, images=image_pil, return_tensors="pt", do_rescale=False
        )
        inputs["input_ids"].append(input_data["input_ids"])
        inputs["pixel_values"].append(input_data["pixel_values"])
        print(f"Processing image: {image_path}")
    inputs["input_ids"] = torch.cat(inputs["input_ids"]).to(device)
    inputs["pixel_values"] = torch.cat(inputs["pixel_values"]).to(device)
    generated_ids = model.generate(
        input_ids=inputs["input_ids"],
        pixel_values=inputs["pixel_values"],
        max_new_tokens=max_new_tokens,
        do_sample=False,
        num_beams=num_beams,
    )
    results = processor.batch_decode(generated_ids, skip_special_tokens=False)
    print(results)
    clean_results = [
        result.replace("</s>", "").replace("<s>", "").replace("<pad>", "")
        for result in results
    ]
    return clean_results


def process_single_image(image_path, model, processor):
    captions = run_model_batch(
        [image_path], model, processor, task="caption", detail_mode=3
    )
    if captions:
        return captions[0] 
    else:
        print(f"Failed to generate caption for {image_path}")


def run_single(image_path, trigger_phrase):
    model, processor = download_and_load_model()
    vanilla_caption = process_single_image(image_path, model, processor)
    if trigger_phrase != "":
            caption = rewrite_caption_with_trigger_phrase(
                vanilla_caption, trigger_phrase
            )
    return caption

def run_multiple(image_paths, trigger_phrase):
    model, processor = download_and_load_model()
    for image_path in image_paths:
        if load_file_as_string(image_path.rsplit(".", 1)[0] + ".txt") == "":
            vanilla_caption = ""
            vanilla_caption = process_single_image(image_path, model, processor)
            if trigger_phrase != "":
                caption = rewrite_caption_with_trigger_phrase(
                    vanilla_caption, trigger_phrase
                )
            else: 
                caption = vanilla_caption
            save_caption_to_file(caption, image_path.rsplit(".", 1)[0] + ".txt")
        
        
