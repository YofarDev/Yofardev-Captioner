import os

from dotenv import load_dotenv
from openai import OpenAI

from utils import local_image_to_data_url


def describe_image(image_path, trigger_phrase):
    load_dotenv()
    client = OpenAI(
        api_key=os.environ["GEMINI_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/",
    )
    prompt = "Describe this image."
    if trigger_phrase != "":
        prompt = f"{prompt} Start the description with the following phrase: '{trigger_phrase}'"
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
                        "text": prompt,
                    },
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            },
        ],
    )
    return response.choices[0].message.content
