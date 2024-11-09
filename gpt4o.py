
from openai import OpenAI
import os
from utils import local_image_to_data_url


def describe_image(image_path, trigger_phrase):
    # ToDo: Add trigger phrase to prompt
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.getenv('GITHUB_API_KEY'),
    )
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
                        "text": "Describe this picture:"
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
