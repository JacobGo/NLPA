# run as script to generate an article
# parameters for the script: author, author_background

import openai
import json5
import sys
import os
import random
from dotenv import load_dotenv
from datetime import date
import base64

load_dotenv()

# lookup table for the author pulls their summary and script
authors = {
    "Robert the Builder": {
        "script": "You are Robert the Builder, an author on the site JakeJacob.com. You have interests in construction and homeowner DIY projects. You have experience in the construction field. You write advice on DIY projects and home improvement tips. Your tone is fatherly, competent, knowledgeable, and matter-of-fact. You occasionally use vernacular and trade language that isn't well known to the general public, but they find it endearing."
    },
    "Betty Books": {
        "script": "You are Betty Books, an author on the site JakeJacob.com. You write about the latest romance novels and popular wellness/self-help books. You occasionally write about the classics, though you suspect it alienates your readership. You are up to speed on all of the girlboss empowerment trends and sometimes churn out girlboss content even if a piece of your soul dies with every word. Remember, you write mostly about books!"
    },
    "Chef Sven": {
        "script": "You are Chef Sven, a Swedish chef. Your confidence in the quality of your recipes far outstrips their edibility, but you come up with easy, household ingredient recipes popular with the busy home chef. At one point, you were a TV chef. You incorporate funny anecdotes of your career as a chef and preface each recipe with a five-paragraph background story on the recipe. You are known to fabricate family members to include in these anecdotes. Your recipes must include all ingredients and quantities, as well as step-by-step instructions for the meal's preparation. Remember, you should be colorful and include an anecdote before the recipe!"
    }
}

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

def generate_article(title, content, keywords, slug, dalle_prompt):

    img_b64 = get_image(dalle_prompt)
    img_path = f'/images/{slug}.png'
    with open(f'{SITE_IMAGES_PATH}/{slug}.png', 'wb') as header_image:
        header_image.write(base64.b64decode(img_b64))

    article = f'''
+++
title = "{title}"
author = "{author}"
keywords = {keywords}
image = "{img_path}"
image_alt = "{dalle_prompt}"
date = {date.today()}
+++
{content}
'''



    with open(f'{SITE_CONTENT_PATH}/{slug}.md', 'w') as f:
        f.write(article)
    print(f'Wrote article to {slug}.md')
    

def run_conversation(author, past_work, script):
    # Step 1: send the conversation and available functions to GPT
    messages = [{"role": "system", "content": f'''You are an author named {author}
                    Your past work is about {past_work}.
                    Don't write about the same topic as your past work.
                    Your biography and writing style is detailed in the script below.
                    \n\n
                    {script}
                 '''
                 }]
    
    functions = [
        {
            "name": "generate_article",
            "description": "Format and publish an article with the given keywords and content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The title of the article"},
                    "content": {
                        "type": "string",
                        "description": "The article content written in markdown",
                    },
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Keywords to use for the article",
                    },
                    "slug": {
                        "type": "string",
                        "description": "Brief slug name about the article to use in the URL to the article."
                    },
                    "dalle_prompt": {
                        "type": "string",
                        "description": "The prompt to use for DALL-E to generate an image for the article."
                    }
                },
                "required": ["content", "title", "keywords", "slug", "dalle_prompt"],
            },
        }
    ]
    OPENAI_KEY = os.getenv("OPENAI_KEY")
    openai.api_key = OPENAI_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        function_call={"name": "generate_article"},  # auto is default, but we'll be explicit
    )
    response_message = response["choices"][0]["message"]
    print(response_message)
    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "generate_article": generate_article,
        }  # only one function in this example, but you can have multiple
        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json5.loads(response_message["function_call"]["arguments"])
        function_response = fuction_to_call(
            title=function_args.get("title"),
            content=function_args.get("content"),
            keywords=function_args.get("keywords"),
            slug=function_args.get("slug"),
            dalle_prompt=function_args.get("dalle_prompt")
        )
        # TODO generate fake comments
        # # Step 4: send the info on the function call and function response to GPT
        # messages.append(response_message)  # extend conversation with assistant's reply
        # messages.append(
        #     {
        #         "role": "function",
        #         "name": function_name,
        #         "content": function_response,
        #     }
        # )  # extend conversation with function response
        # second_response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo-0613",
        #     messages=messages,
        # )  # get a new response from GPT where it can see the function response
        return function_response
    print("No function call detected.")


# when run as script, generate an article
global author
if __name__ == "__main__":
    author = random.choice(list(authors.keys()))
    past_work = ', '.join([f.split('.')[0] for f in os.listdir(SITE_CONTENT_PATH)])
    author_script = authors[author]["script"]

    print(f"Generating article for {author} excluding {past_work}.")

    run_conversation(author, past_work, author_script)
