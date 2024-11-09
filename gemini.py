import os

from openai import OpenAI

from utils import local_image_to_data_url


def describe_image(image_path, trigger_phrase):
    client = OpenAI(
        api_key=os.environ["GEMINI_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/",
    )
    data_url = local_image_to_data_url(image_path)
    response = client.chat.completions.create(
        model="gemini-1.5-flash",
        n=1,
        messages=[
            {
                "role": "system",
                "content": "",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Reply with a paragraph describing this image and nothing else.",
                    },
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            },
        ],
    )
    return response.choices[0].message.content
