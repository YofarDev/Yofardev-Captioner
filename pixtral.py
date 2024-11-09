import os
from mistralai import Mistral
from utils import local_image_to_data_url

def describe_image(image_path, trigger_phrase):
    # ToDo: Add trigger phrase to prompt
    data_url = local_image_to_data_url(image_path)
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "pixtral-12b-2409"
    client = Mistral(api_key=api_key)
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Reply with a paragraph describing this image and nothing else."
                },
                {
                    "type": "image_url",
                    "image_url": data_url
                }
            ]
        }
    ]
    chat_response = client.chat.complete(
        model=model,
        messages=messages
    )
    caption = chat_response.choices[0].message.content
    return caption