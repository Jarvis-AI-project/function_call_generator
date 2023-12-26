"""
This WebUI is used to built so that humans and AI can collaborate to generate synthetic dataset.
"""
import os
import pymongo
import gradio as gr
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(".env")
genai.configure(api_key=os.environ["GOOGLE_MAKERSUITE_API_KEY"])

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
    
    model = genai.GenerativeModel(
        model_name="gemini-pro",
        generation_config=generation_config
    )
    history.append(prompt)

    response = model.generate_content(history)
    return response.text

bot1 = gr.Chatbot(height=600)
bot2 = gr.Chatbot(height=600)

with gr.Blocks(css="footer {visibility: hidden}") as iface:
    gr.HTML("""
    <h1 style="text-align: center; user-select:None; ">DATASET GENERATOR</h1>
    """)

    with gr.Row():
        with gr.Column():
            gr.ChatInterface(
                fn=gemini_api,
                chatbot=bot1,
                title="Function Calling",
            )

        with gr.Column():
            gr.ChatInterface(
                fn=gemini_api,
                chatbot=bot2,
                title="Response"
            )

    # gr.Button("Save to Database")


if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0")
