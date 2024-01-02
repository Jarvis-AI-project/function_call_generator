"""
This file is used to generate mt data for JARVIS for `calculator`.
"""

from threading import Thread
from queue import Queue
import torch
import google.generativeai as genai
# import json
from time import sleep
import gradio as gr
import os
from pymilvus import connections, Collection, db
# from ngram import NGram
# from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModel

_MODEL_PATH = "/mnt/nvme/MODELS/EMBEDINGS/UAE-Large-V1/"

tokenizer = AutoTokenizer.from_pretrained(_MODEL_PATH, device="cuda:1")
bert_model = AutoModel.from_pretrained(_MODEL_PATH, device_map="cuda:1", low_cpu_mem_usage=True)

data_points = Queue(maxsize=4)

load_dotenv(".env")

genai.configure(api_key="AIzaSyDtqp125rVbUDH-I3ooH7lcFabsa3fu0vI")

db.using_database("JARVIS")
connections.connect(
    alias="default",
    host = os.getenv("MILVUS_HOST"),
    port = 19530,
    user=os.getenv("MILVUS_USER"),
    password=os.getenv("MILVUS_PASSWORD"),
)

collection = Collection("calculator", using="default")

generation_config = {
    "temperature": 0.9,
    "max_output_tokens": 1024,
}

model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config

)

prompt = """
I want some data to train my language model. The model can only perform simple calculations including plus, minus, multiply, divide and power. the operations are represented by the signs + - * / **. don't include any other signs in the data.

Example:
USER: can you split a bill for me
ASSISTANT: Of course! I'd be happy to help you split a bill. Please provide me with the total amount of the bill and the number of people you want to split it among. </s>
USER: the total amount is 500 dollars and split it between 5 people
ASSISTANT: Each person should contribute <calculator> 500/5 </s> 100 </calculator> 100 dollars.</s>

Generate more such conversations to train the assistant. 
- The main calculation should be surrounded by <calculator> and </calculator> which will not be shown to the user and is evaluated by a computer. After the assistant stops talking write this </s>
- Data should be multi-dialog. 
- The main calculation will not be visible to the user. 
- Keep your dialogs short and be frank. 
- Assume this system is being used to do day-to-day tasks.
- Do not explain your calculation.
- Avoid generating data points that require up-to-date knowledge.
- Only output one conversation at a time. 
"""


def push_data_to_queue(data_points: Queue):
    while True:
        if not data_points.full():
            response = model.generate_content(prompt)
            try:
                data_points.put(response.text)
            except Exception as e:
                gr.Error(e)
                pass
        else:
            sleep(1)


# def get_ngram(user, assistant):
#     """Ngram Similarity of two text chunks."""
#     return round(NGram.compare(user, assistant, N=2), 2)


# def get_bert_embedding(user, assistant):
#     """BERT Similarity of two text chunks."""
#     user = tokenizer(user, return_tensors="pt", padding=True, truncation=True)
#     user = {k: v.to(bert_model.device) for k, v in user.items()}
#     assistant = tokenizer(assistant, return_tensors="pt",
#                           padding=True, truncation=True)
#     assistant = {k: v.to(bert_model.device) for k, v in assistant.items()}

#     user_embeddings = bert_model(**user).last_hidden_state[:, -1]
#     assistant_embeddings = bert_model(**assistant).last_hidden_state[:, -1]
#     return round(cosine_similarity(user_embeddings.detach().cpu().numpy(), assistant_embeddings.detach().cpu().numpy())[0][0], 5)


# def extract_and_compare():
#     data = data_points.get()
#     user = data
#     assistant = data
#     similarity = get_bert_embedding(user, assistant)
#     output_ngram = get_ngram(user, assistant)
#     return user, assistant, similarity, output_ngram

def get_new_conversation():
    new_conversation = data_points.get()
    return new_conversation

def get_to_3_similar_conversations(current_conversation):
    # Get the top 3 conversations from the database symanitcally similar to the current conversation
    results = collection.search(
        data = [get_embedings(current_conversation)],
        anns_field="Embedings",
        param={"metric_type": "L2"},
        limit=3,
        output_fields=["Conversation"]
    )[0]

    prev_conversations = []
    for hit in results:
        # prev_conversations.update({"Conversation": hit.entity.get('Conversation'), "Similarity": hit.distance})
        prev_conversations.append(f"Similarity: {hit.distance}\n" + hit.entity.get('Conversation').get('data'))

    if len(prev_conversations) < 3:
        prev_conversations.extend(["Not Enough Data"] * (3 - len(prev_conversations)))

    return prev_conversations
    

def get_embedings(conv: str):
    return torch.randn(1024).numpy().tolist()

def accept_data(current_conversation):
    if not current_conversation:
        gr.Error("No data to accept")
        return
    
    # Insert current conversation into the database
    collection.insert(
        {
            "Embedings": get_embedings(current_conversation),
            "Conversation": {
                "data": current_conversation,
            }
        }
    )

    new_conversation = get_new_conversation()
    similar_conversations = get_to_3_similar_conversations(new_conversation)
    return new_conversation, similar_conversations[0], similar_conversations[1], similar_conversations[2]

def reject_data():
    new_conversation = get_new_conversation()
    similar_conversations = get_to_3_similar_conversations(new_conversation)
    return new_conversation, similar_conversations[0], similar_conversations[1], similar_conversations[2]

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.HTML("""
    <h1 style="text-align: center; user-select:None; ">DATASET GENERATOR</h1>
    """)

    with gr.Row():
        mt_conversation = gr.TextArea(label="Generated MT Conversation", placeholder="Click Reject to get 1st data point", interactive=True)

    with gr.Row():
        accept_btn = gr.Button(value="Accept")
        reject_btn = gr.Button(value="Reject")

    with gr.Column():
        gr.Markdown("## Top Conversation taht already exists in the database")
        prev_conversation_1 = gr.Textbox(label="Conversation 1", placeholder="", interactive=False)
        prev_conversation_2 = gr.Textbox(label="Conversation 2", placeholder="", interactive=False)
        prev_conversation_3 = gr.Textbox(label="Conversation 3", placeholder="", interactive=False)

    accept_btn.click(accept_data, inputs=[mt_conversation], outputs=[mt_conversation, prev_conversation_1, prev_conversation_2, prev_conversation_3])
    reject_btn.click(reject_data, outputs=[mt_conversation, prev_conversation_1, prev_conversation_2, prev_conversation_3])
    
if __name__ == "__main__":
    Thread(target=push_data_to_queue, args=(data_points,)).start()
    demo.launch()
