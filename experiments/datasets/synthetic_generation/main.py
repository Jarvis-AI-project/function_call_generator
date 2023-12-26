"""
This WebUI is used to built so that humans and AI can collaborate to generate synthetic dataset.
"""
import os
import pymongo
import gradio as gr

import google.generativeai as genai
genai.configure(api_key=os.environ["GOOGLE_MAKERSUITE_API_KEY"])

from dotenv import load_dotenv
load_dotenv(".env")


_URI = f"mongodb://{os.environ['MONGODB_USERNAME']}:{os.environ['MONGODB_PASSWORD']}@{os.environ['MONGODB_HOST']}:{os.environ['MONGODB_PORT']}/{os.environ['MONGODB_DATABASE']}"

client = pymongo.MongoClient(_URI)
db = client[os.environ["MONGODB_DATABASE"]]


def gemini_api(prompt: str, history):
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
        f"{prompt}"
    ]

    response = model.generate_content(prompt_parts)
    return response.text


bot1 = gr.Chatbot(height=600)
bot2 = gr.Chatbot(height=600)


with gr.Blocks(css="footer {visibility: hidden}") as demo:
    gr.HTML("""
    <h1 style="text-align: center; user-select:None; ">DATASET GENERATOR</h1>
    """)

    with gr.Row():
        with gr.Column():
            gr.ChatInterface(chatbot=bot1, fn=gemini_api, title="Function Calling")
            # create a Test Case with symbol and input

        with gr.Column():
            gr.ChatInterface(chatbot=bot2, fn=gemini_api, title="Response")

    gr.Button("Save to Database")


if __name__ == "__main__":
    demo.launch()
