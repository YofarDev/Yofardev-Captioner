import os
from unittest.mock import patch

import torch
from huggingface_hub import snapshot_download
from PIL import Image
from transformers import AutoModelForCausalLM, AutoProcessor
from transformers.dynamic_module_utils import get_imports

from utils import rewrite_caption_with_trigger_phrase


def fixed_get_imports(filename: str | os.PathLike) -> list[str]:
    if not str(filename).endswith("modeling_florence2.py"):
        return get_imports(filename)
    imports = get_imports(filename)
    if "flash_attn" in imports:
        imports.remove("flash_attn")
    return imports


# Function to download and load the Florence-2 model
def download_and_load_model(model_name="microsoft/Florence-2-large"):
    device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps" if torch.backends.mps.is_available() else "cpu"
    )
    model_path = os.path.join("models", model_name.replace("/", "_"))
    if not os.path.exists(model_path):
        print(f"Downloading {model_name} model to: {model_path}")
        snapshot_download(
            repo_id=model_name, local_dir=model_path, local_dir_use_symlinks=False
        )
    with patch(
        "transformers.dynamic_module_utils.get_imports", fixed_get_imports
    ):  # Workaround for unnecessary flash_attn requirement
        model = AutoModelForCausalLM.from_pretrained(
            model_path, trust_remote_code=True
        ).to(device)
        processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
    return model, processor


def run_model(
    image_path,
    model,
    processor,
    task="caption",
    num_beams=3,
    max_new_tokens=1024,
    detail_mode=3,
):
    device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps" if torch.backends.mps.is_available() else "cpu"
    )
    prompts = {1: "<CAPTION>", 2: "<DETAILED_CAPTION>", 3: "<MORE_DETAILED_CAPTION>"}
    prompt = prompts.get(detail_mode, "<MORE_DETAILED_CAPTION>")
    inputs = {"input_ids": [], "pixel_values": []}
    image_pil = Image.open(image_path).convert("RGB")
    input_data = processor(
        text=prompt, images=image_pil, return_tensors="pt", do_rescale=False
    )
    inputs["input_ids"].append(input_data["input_ids"])
    inputs["pixel_values"].append(input_data["pixel_values"])
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
    clean_results = [
        result.replace("</s>", "").replace("<s>", "").replace("<pad>", "")
        for result in results
    ]
    return clean_results[0]


def describe_image(image_path, trigger_phrase, prompt):
    model, processor = download_and_load_model()
    vanilla_caption = run_model(
        image_path, model, processor, task="caption", detail_mode=3
    )
    # The florence2 model doesn't accept a prompt, but we have to make sure an empty prompt is not passed to the `rewrite_caption_with_trigger_phrase` function
    print("Florence2 doesn't use a prompt. The prompt will be ignored.")
    if trigger_phrase != "":
        caption = rewrite_caption_with_trigger_phrase(vanilla_caption, trigger_phrase)
    else:
        caption = vanilla_caption
    return caption
