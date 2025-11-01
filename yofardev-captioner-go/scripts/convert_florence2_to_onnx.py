import os
import torch
from transformers import AutoModelForCausalLM, AutoProcessor
from PIL import Image
import onnxruntime
import onnx
from unittest.mock import patch
from transformers.dynamic_module_utils import get_imports
from typing import Union

def fixed_get_imports(filename: Union[str, os.PathLike]) -> list[str]:
    if not str(filename).endswith("modeling_florence2.py"):
        return get_imports(filename)
    imports = get_imports(filename)
    if "flash_attn" in imports:
        imports.remove("flash_attn")
    return imports

def download_and_load_model(model_name="microsoft/Florence-2-large"):
    # This function is adapted from florence2.py to ensure consistency
    # and to avoid re-downloading if already present.
    model_path = os.path.join("models", model_name.replace("/", "_"))
    if not os.path.exists(model_path):
        print(f"Downloading {model_name} model to: {model_path}")
        # Using snapshot_download directly here, as the patch for flash_attn is not needed for conversion
        # and might cause issues if not handled carefully in a standalone script.
        # For conversion, we just need the model weights.
        from huggingface_hub import snapshot_download
        snapshot_download(
            repo_id=model_name, local_dir=model_path, local_dir_use_symlinks=False
        )
    
    with patch(
        "transformers.dynamic_module_utils.get_imports", fixed_get_imports
    ):  # Workaround for unnecessary flash_attn requirement
        model = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True, attn_implementation="eager")
        processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
    return model, processor

def convert_florence2_to_onnx(model_name="microsoft/Florence-2-large", output_dir="migration-go/yofardev-captioner-go/assets/models"):
    model, processor = download_and_load_model(model_name)
    model.eval()

    # Create dummy inputs for ONNX export
    # Florence-2 expects input_ids and pixel_values
    # The input_ids are for the prompt, pixel_values for the image
    
    # Example prompt: "<MORE_DETAILED_CAPTION>"
    dummy_text = "<MORE_DETAILED_CAPTION>"
    
    # Create a dummy image (e.g., a black image)
    dummy_image = Image.new('RGB', (224, 224), color = 'black') # Florence-2 typically resizes to 224x224 or similar

    inputs = processor(text=dummy_text, images=dummy_image, return_tensors="pt", do_rescale=False)
    
    # Ensure inputs are on CPU for ONNX export
    dummy_input_ids = inputs["input_ids"].cpu()
    dummy_pixel_values = inputs["pixel_values"].cpu()

    # Create dummy decoder_input_ids for the generation task
    # A single token (e.g., the start token) is usually sufficient for tracing the decoder.
    # Assuming the model's config has a decoder_start_token_id
    decoder_start_token_id = processor.tokenizer.bos_token_id
    if decoder_start_token_id is None:
        # Fallback if bos_token_id is not set, use pad_token_id or a common start token like 0
        decoder_start_token_id = processor.tokenizer.pad_token_id if processor.tokenizer.pad_token_id is not None else 0
    
    dummy_decoder_input_ids = torch.tensor([[decoder_start_token_id]], dtype=torch.long, device="cpu")

    # Define input and output names for the ONNX model
    input_names = ["input_ids", "pixel_values", "decoder_input_ids"]
    output_names = ["output_ids"] # The model generates token IDs

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    onnx_model_path = os.path.join(output_dir, "florence2_large.onnx")

    print(f"Exporting model to ONNX at: {onnx_model_path}")
    torch.onnx.export(
        model,
        (dummy_input_ids, dummy_pixel_values, None, dummy_decoder_input_ids), # Pass None for attention_mask
        onnx_model_path,
        input_names=input_names,
        output_names=output_names,
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "pixel_values": {0: "batch_size"},
            "decoder_input_ids": {0: "batch_size", 1: "decoder_sequence_length"},
            "output_ids": {0: "batch_size", 1: "output_sequence_length"}
        },
        opset_version=17, # Use a recent opset version
        do_constant_folding=True,
    )
    print("ONNX model exported successfully.")

    # # Verify the ONNX model (commented out due to potential memory issues)
    # print("Verifying ONNX model...")
    # try:
    #     onnx_model = onnx.load(onnx_model_path)
    #     onnx.checker.check_model(onnx_model)
    #     print("ONNX model check passed!")
    # except Exception as e:
    #     print(f"ONNX model check failed: {e}")

    # # Test with ONNX Runtime (commented out due to potential memory issues)
    # print("Testing ONNX model with ONNX Runtime...")
    # try:
    #     ort_session = onnxruntime.InferenceSession(onnx_model_path)
        
    #     # Prepare inputs for ONNX Runtime
    #     ort_inputs = {
    #         ort_session.get_inputs()[0].name: dummy_input_ids.numpy(),
    #         ort_session.get_inputs()[1].name: dummy_pixel_values.numpy()
    #     }
    #     ort_outputs = ort_session.run(None, ort_inputs)
    #     print("ONNX Runtime inference successful.")
    #     # You can further decode ort_outputs[0] using the processor if needed
    #     # For now, just checking if it runs without error.
    # except Exception as e:
    #     print(f"ONNX Runtime inference failed: {e}")

if __name__ == "__main__":
    convert_florence2_to_onnx()
