import json
import openai
import requests
import streamlit as st
import pandas as pd
import time
import random
from streamlit_gsheets import GSheetsConnection
from tenacity import retry, wait_random_exponential, stop_after_attempt
from streamlit_extras.let_it_rain import rain


GPT_MODEL = "gpt-3.5-turbo-0613"

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai.api_key,
    }
    json_data = {"model": model, "messages": messages}
    if tools is not None:
        json_data.update({"tools": tools})
    if tool_choice is not None:
        json_data.update({"tool_choice": tool_choice})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

tools = [
    {
        "type": "function",
        "function": {
            "name": "check_for_resume_inquiry",
            "description": "check if the user input is for the intent of seeing your resume.",
            "parameters": {
                "type": "object",
                "properties": {
                    "result": {
                        "type": "boolean",
                        "description": "the true or false result"
                    }
                },
                 "required": ["result"],
            },
        }
    }
]

def read_resume():
        with open("data/resume.txt") as f:
            resume = f.read()
        return resume 

def strip_resume(resume_doc):

    try:
        # Find the text after "RESUME:"
        start = resume_doc.index("RESUME:") + len("RESUME:")
        # Find the text before "PERSONAL INFO:"
        end = resume_doc.index("PERSONAL INFO:", start)
        # Extract the text between "RESUME:" and "PERSONAL INFO:"
        resume_info = resume_doc[start:end].strip()
        return resume_info
        
    except ValueError:
        resume_info = "The text does not contain 'RESUME:' or 'PERSONAL INFO:'"
        return resume_info
    
def standardize_resume_response(resume_info):
    
    return "Sure! here you go: \n\n {} \n\nLet me know if there anything specific you would like to know or discuss!".format(resume_info)


def check_for_resume(input):
    resume_doc = read_resume()
    resume_info = strip_resume(resume_doc)

    messages = []
    messages.append({"role": "system", "content": """You are engaging in dialog with a human.
you tasked with understanding if the intent of their turn in the conversation is to see your resume. use this definition of what an intent is for your bases: "An intent categorizes an end-user's intention for one conversation turn."

Below are 20 examples phrases of asking to see your resume:

* "Can I see your resume, please?"
* "Can I look at your resume?"
* "Can I get a copy of your resume?"
* "Can I take a peek at your resume?"
* "Could you provide me access to your resume?"
* "Can I check out your resume?"
* "Is it okay if I have a look at your resume?"
* "Would you be willing to share your resume with me?"
* "Can I view your resume?"
* "Might I have a glimpse of your resume?"
* "Would you mind letting me review your resume?"
* "Could I have a look at your resume?"
* "Is there a chance I could view your resume?"
* "Would you share your resume with me, please?"
* "Can I read your resume?"
* "Can I see that resume?"
* "Could you pass along your resume for me to review?"
* "Can I see your CV?"
* "May I request to see your resume?"
* "Would it be possible for me to take a look at your resume?"

Determine if the next input by the user is for the intent of seeing your resume
"""})
    
    messages.append({"role": "user", "content": input})
    chat_response = chat_completion_request(
        messages, tools=tools, tool_choice={"type": "function", "function": {"name": "check_for_resume_inquiry"}}
    )
    print(chat_response)
    chat_response = chat_response.json()["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"]

    resume_info = strip_resume(resume_doc)

    print("input: "+input+" result: "+ str((json.loads(chat_response))["result"]))
    return bool((json.loads(chat_response))["result"]), resume_info
    


def add_balloons():

    emoji_list = ["🎈","🔥","💯","🤖"]

    rain(
        emoji=random.choice(emoji_list),
        font_size=random.randint(54, 300),
        falling_speed=5,
        animation_length="infinite",
    )


