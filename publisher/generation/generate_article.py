# run as script to generate an article
# parameters for the script: author, author_background

import openai
import json    
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# lookup table for the author pulls their summary and script
authors = {
    "Robert the Builder": {
        "script": "You are Robert the Builder, an author on the site JakeJacob.com. You have interests in construction and homeowner DIY projects. You have experience in the construction field. You write advice on DIY projects and home improvement tips. Your tone is fatherly, competent, knowledgeable, and matter-of-fact. You occasionally use vernacular and trade language that isn't well known to the general public, but they find it endearing."
    },
    "author2": {
        "script": "author2_script"
    },
    "author3": {
        "script": "author3_script"
    }
}

def generate_article(title, content, keywords):
    print(f"Title: {title}\n\nContent: {content}\n\nKeywords: {keywords}")
    return f"Title: {title}\n\nContent: {content}\n\nKeywords: {keywords}"


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
                    }
                },
                "required": ["content", "title", "keywords"],
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
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = fuction_to_call(
            title=function_args.get("title"),
            content=function_args.get("content"),
            keywords=function_args.get("keywords"),
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
    return "No function call detected."


# when run as script, generate an article
if __name__ == "__main__":
    # get the author and their background from the command line

    author = sys.argv[1]
    past_work = sys.argv[2]
    #script = sys.argv[3]

    # get the author's summary and script
    author_script = authors[author]["script"]
    run_conversation(author, past_work, author_script)
