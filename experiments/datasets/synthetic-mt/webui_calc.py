"""
This file is used to generate mt data for JARVIS for `calculator`.
"""

import streamlit as st
from threading import Thread
from queue import Queue
import google.generativeai as genai
import jsonlines
import ast
queue = Queue(maxsize=10)

genai.configure(api_key="AIzaSyD2FkGlX8WQUt8JUXqW8Wp2OoENfgLynRQ")

# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

prompt_parts = [
  "{\"role\": \"system\", \"content\": \"Your task is to generate data to train a virtual assistant that has access to calculator. It can only perform the following operations: addition '+', subtraction '-', multiplication '*', division '/ ', power '**'). It can also use these operations to perform complicated computations. Don't include any other symbol not defined.\"},\n    {\"user\": \"Jarvis, can you help me split the restaurant bill among three people? The total is $120.\", \"assistant\": \"the answer is <calculator> 2+2 </s> 4 </calculator>four. </s>\"},\n\t{\"user\": \"what is the square root of 4\", \"assistant\": \"the square root of 4 is <calculator> 4** 0.5 </s> 2. </s>\"},\n\t{\"user\": \"Jarvis, can you help me split the restaurant bill among three people? The total is 120 dollars.\", \"assistant\": \"Certainly, sir. Let me divide that for you. <calculator> 120 / 3 </s> 40 </calculator>Each person should contribute 40.</s> Anything else you'd like assistance with?\"},\n\t{\"user\": \"Hey Jarvis, I'm planning to buy a new phone. It costs 800 dolars, and the sales tax is 8 percent. Can you calculate the total amount I'll be paying?\", \"assistant\": \"Certainly, sir. Let me calculate that for you. <calculator> 800 + (800 * 0.08) </s> 864 </calculator>The total amount, including tax, is 864 dollars.</s> Is there anything else you'd like to know?\"},\n\t{\"user\": \"Jarvis, can you help me figure out my monthly expenses? I earn 3000 dollars, and I want to save 20 percent of my income.\", \"assistant\": \"Absolutely, sir. Let me calculate that for you. <calculator> 3000 * 0.20 </s> 600 </calculator>You should save 600 dollars each month.</s>\"},\nwrite more such user assistant data to train the assistant. queries shouldn't include any symbols beside + - * / .only generate one example at a time.\n",
]

def generate_data():
    response = model.generate_content(prompt_parts)


    data = response.text.split(",\n")
    # data


    dict_data = [ast.literal_eval(item) for item in data]


    # for i in range(len(dict_data)):
    #     st.header("USER Query")
    #     st.text(dict_data[i]["user"])
    #     st.header("ASSISTANT Response")
    #     st.text(dict_data[i]["assistant"])

    #     btns = st.radio("Is the response correct?", ("Yes", "No"))
    #     st.button("Submit")

    #     if btns == "Yes":
    #         with jsonlines.open('output.jsonl', mode='a') as writer:
    #             writer.write(dict_data[i])

