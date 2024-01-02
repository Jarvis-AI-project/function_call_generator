"""
This file is used to generate mt data for JARVIS for `calculator`.
"""

from threading import Thread
from queue import Queue
import google.generativeai as genai
import json
from time import sleep
import gradio as gr
from ngram import NGram
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained(
    "WhereIsAI/UAE-Large-V1", device="mps")
bert_model = AutoModel.from_pretrained("WhereIsAI/UAE-Large-V1",
                                       device_map="mps")


data_points = Queue(maxsize=4)


genai.configure(api_key="AIzaSyDtqp125rVbUDH-I3ooH7lcFabsa3fu0vI")


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
                response = response.text
                print(response)
                print(data_points.qsize())
                data_points.put(response)
            except Exception as e:
                gr.Error(e)
                pass
        else:
            sleep(1)


def get_ngram(user, assistant):
    """Ngram Similarity of two text chunks."""
    return round(NGram.compare(user, assistant, N=2), 2)


def get_bert_embedding(user, assistant):
    """BERT Similarity of two text chunks."""
    user = tokenizer(user, return_tensors="pt", padding=True, truncation=True)
    user = {k: v.to(bert_model.device) for k, v in user.items()}
    assistant = tokenizer(assistant, return_tensors="pt",
                          padding=True, truncation=True)
    assistant = {k: v.to(bert_model.device) for k, v in assistant.items()}

    user_embeddings = bert_model(**user).last_hidden_state[:, -1]
    assistant_embeddings = bert_model(**assistant).last_hidden_state[:, -1]
    return round(cosine_similarity(user_embeddings.detach().cpu().numpy(), assistant_embeddings.detach().cpu().numpy())[0][0], 5)


def extract_and_compare():
    data = data_points.get()
    user = data
    assistant = data
    similarity = get_bert_embedding(user, assistant)
    output_ngram = get_ngram(user, assistant)
    return user, assistant, similarity, output_ngram


with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.HTML("""
    <h1 style="text-align: center; user-select:None; ">DATASET GENERATOR</h1>
    """)

    with gr.Row():

       data= gr.Textbox(label="Data", lines=20, placeholder="Data will appear here", interactive=True)
    with gr.Row():

        output_ngram = gr.Textbox(
            label="Ngram Similarity Score", interactive=False)
        output_bert = gr.Textbox(
            label="BERT Similarity Score", interactive=False)
    with gr.Row():

        accept_btn = gr.Button(value="Accept")
        reject_btn = gr.Button(value="Reject")
        accept_btn.click(
            extract_and_compare, outputs=[data,output_ngram, output_bert])


if __name__ == "__main__":

    Thread(target=push_data_to_queue, args=(data_points,)).start()

    demo.launch()
