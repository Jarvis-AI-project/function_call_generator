# """
# This WebUI is used to built so that humans and AI can collaborate to validate data.
# """
import pymongo
import json
import os
from jsonschema import validate, ValidationError, SchemaError
import gradio as gr

from dotenv import load_dotenv
load_dotenv(".env")


def save_to_database(data):

    _URI = f"mongodb://{os.environ['MONGODB_USERNAME']}:{os.environ['MONGODB_PASSWORD']}@{os.environ['MONGODB_HOST']}:{os.environ['MONGODB_PORT']}/{os.environ['MONGODB_DATABASE']}"
    print(_URI)
    client = pymongo.MongoClient(_URI)
    db = client["function_calling"]


def echo(message, history):
    return message


bot1 = gr.Chatbot(height=600)
bot2 = gr.Chatbot(height=600)


with gr.Blocks(css="footer {visibility: hidden}") as demo:
    gr.HTML("""
    <h1 style="text-align: center; user-select:None; ">DATASET GENERATOR</h1>
    """)

    with gr.Row():
        with gr.Column():
            gr.ChatInterface(chatbot=bot1, fn=echo, title="Function Calling")
            # create a Test Case with symbol and input

        with gr.Column():
            gr.ChatInterface(chatbot=bot2, fn=echo, title="Response")

    gr.Button("Save to Database")


if __name__ == "__main__":
    demo.launch()
