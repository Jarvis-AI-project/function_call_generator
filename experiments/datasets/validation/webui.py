# """
# This WebUI is used to built so that humans and AI can collaborate to validate data.
# """
import pymongo
import json
import os
from jsonschema import validate, ValidationError, SchemaError
import gradio as gr

from dotenv import load_dotenv
load_dotenv()

# Connect to MongoDB and get the collection
_URI = f"mongodb://{os.environ['MONGODB_USERNAME']}:{os.environ['MONGODB_PASSWORD']}@{os.environ['MONGODB_HOST']}:{os.environ['MONGODB_PORT']}/{os.environ['MONGODB_DATABASE']}"
print(_URI)
client = pymongo.MongoClient(_URI)
db = client["function_calling"]

def echo(message, history):
    return message
with gr.Blocks() as demo:
    gr.HTML("""
    <h1 style="text-align: center; user-select:None; ">DATASET GENERATOR</h1>
    """)
    

    with gr.Row():
        with gr.Column():
            gr.ChatInterface(fn=echo,title="Function Calling",)
            
            
        with gr.Column():
            gr.ChatInterface(fn=echo,title="Response")
    
    
    gr.Button("Save to Database")
    


    demo.launch()

