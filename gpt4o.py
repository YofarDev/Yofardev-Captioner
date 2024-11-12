
from openai import OpenAI
import os
from dotenv import load_dotenv
from utils import local_image_to_data_url


def describe_image(image_path, trigger_phrase):
    load_dotenv()
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.getenv('GITHUB_API_KEY'),
    )
    prompt = "Describe this image."
    if trigger_phrase != "":
        prompt =f"{prompt} Start the description with the following phrase: '{trigger_phrase}'"
    data_url = local_image_to_data_url(image_path)
    response = client.chat.completions.create(
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
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_url
                        }
                    } 
            ] 
            }
        ],
        model="gpt-4o",
        temperature=1,
        max_tokens=4096,
        top_p=1
    )

    return response.choices[0].message.content
