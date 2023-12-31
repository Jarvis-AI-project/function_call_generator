"""
This WebUI let you compare the semantic similarity of two text chunks input by the user.
"""

import os
import gradio as gr
from openai import OpenAI
from scipy.spatial.distance import cosine
from dotenv import load_dotenv

load_dotenv("synthetic/.env")
client = OpenAI(api_key=os.getenv("OPENAI_KEY_EMBEDINGS"))

def get_embedding(text, model="text-embedding-ada-002"):
    """Get the embedding of a text chunk using the given model."""
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding

def compare(text_1, text_2) -> float:
    """Compare the semantic similarity of two text chunks."""
    text_1_embedding = get_embedding(text_1)
    text_2_embedding = get_embedding(text_2)
    similarity = 1 - cosine(text_1_embedding, text_2_embedding)
    return round(similarity, 3)

with gr.Blocks() as iface:
    gr.HTML("""
    <h1 style="text-align: center; user-select:None; ">DATASET GENERATOR</h1>
    """)
    
    with gr.Row():
        text_1 = gr.TextArea(lines=30, label="Text 1")
        text_2 = gr.TextArea(lines=30, label="Text 2")
    
    output = gr.Textbox(label="Semantic Similarity Score", interactive=False)
    compare_btn = gr.Button(value="Compare")
    compare_btn.click(compare, inputs=[text_1, text_2], outputs=output)
    

if __name__ == "__main__":
    iface.launch()
