import openai
import json5
import sys
import os
import random
from dotenv import load_dotenv
from datetime import date
import base64



#script to generate images for existing articles that don't have them

load_dotenv()

SITE_CONTENT_PATH = os.getenv('SITE_CONTENT_PATH', '../site/content/posts')
SITE_IMAGES_PATH = os.getenv('SITE_IMAGES_PATH', '../site/content/images')

def get_image(dalle_prompt):
    # makes an api call to DALL-E to generate an image
    OPENAI_KEY = os.getenv("OPENAI_KEY")
    openai.api_key = OPENAI_KEY
    response = openai.Image.create(
        prompt=dalle_prompt,
        n=1,
        size="1024x1024",
        response_format="b64_json",
    )
    image_b64 = response['data'][0]['b64_json']
    return image_b64

if __name__ == "__main__":

    OPENAI_KEY = os.getenv("OPENAI_KEY")
    openai.api_key = OPENAI_KEY
    # for each article in the site content path, read the text of the article into an array
    for filename in os.listdir(SITE_CONTENT_PATH):
        with open(os.path.join(SITE_CONTENT_PATH, filename), 'r') as f:
            article = f.read()
            # slug is the filename. get the slug
            slug = filename.split('.')[0]
            # request openai to generate a dalle prompt for the article
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt= "Write a DALL-E prompt to generate a header image for the following article.\n\n" + article,
                max_tokens=256,
                temperature=0.2,
                n=1
            )
            # get the generated dalle prompt
            dalle_prompt = response['choices'][0]['text']
            # request openai to generate an image for the article
            img_b64 = get_image(dalle_prompt)
            # save the image to the images folder
            img_path = f'{SITE_IMAGES_PATH}/{slug}.png'
            with open(img_path, 'wb') as header_image:
                header_image.write(base64.b64decode(img_b64))