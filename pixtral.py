import os

from dotenv import load_dotenv
from mistralai import Mistral

from utils import local_image_to_data_url

def describe_image(image_path,prompt):
    load_dotenv()
    data_url = local_image_to_data_url(image_path)
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "pixtral-large-latest"
    client = Mistral(api_key=api_key)
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": data_url},
            ],
        }
    ]
    chat_response = client.chat.complete(model=model, messages=messages)
    caption = chat_response.choices[0].message.content
    return caption
