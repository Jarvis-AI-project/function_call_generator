"""
This file is used to generate mt data for JARVIS for `calculator`.
"""

from threading import Thread
from queue import Queue
import torch
import google.generativeai as genai
from time import sleep
import gradio as gr
import re
import os
from pymilvus import connections, Collection, db
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModel
import platform

if platform.system()=="Linux":
    _MODEL_PATH = "/mnt/nvme/MODELS/EMBEDINGS/UAE-Large-V1/"
    tokenizer = AutoTokenizer.from_pretrained(_MODEL_PATH, device="cuda:1")
    bert_model = AutoModel.from_pretrained(_MODEL_PATH, device_map="cuda:1", low_cpu_mem_usage=True)

else:
    tokenizer = AutoTokenizer.from_pretrained("WhereIsAI/UAE-Large-V1")
    bert_model = AutoModel.from_pretrained("WhereIsAI/UAE-Large-V1")


data_points = Queue(maxsize=4)

load_dotenv(".env")

genai.configure(api_key="AIzaSyDtqp125rVbUDH-I3ooH7lcFabsa3fu0vI")

connections.connect(
    alias="default",
    host=os.getenv("MILVUS_HOST"),
    port=19530,
    user=os.getenv("MILVUS_USER"),
    password=os.getenv("MILVUS_PASSWORD"),
)
db.using_database("JARVIS")

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

Example 1:
USER: can you split a bill for me
ASSISTANT: Of course! I'd be happy to help you split a bill. Please provide me with the total amount of the bill and the number of people you want to split it among. </s>
USER: the total amount is five hundred dollars and split it between five people
ASSISTANT: Each person should contribute <calculator> 500/5 </s> 100 </calculator> hundred dollars.</s>

Example 2:
USER: I need to find the total cost of coffee and cake.
ASSISTANT: Please provide me with the cost of coffee and cake separately. </s>
USER: the coffee costs three dollars and cake costs five dollars.
ASSISTANT: The total cost for coffee and cake together is <calculator> 3+5 </s> 8 </calculator> eight dollars. </s>


Generate more such conversations to train the assistant. 
- The main calculation should be surrounded by <calculator> and </calculator> which will not be shown to the user and is evaluated by a computer. After the assistant stops talking write this </s>
- Data should be multi-dialog. 
- The main calculation will not be visible to the user. 
- Keep your dialogs short and be frank. 
- Assume this system is being used to do day-to-day tasks.
- Do not explain your calculation.
- Avoid generating data points that require up-to-date knowledge.
- User query can't contain any kind symbols such as (%, $,₹, .,), etc. Instead, it should use the corresponding word representation of the symbols eg. dollar for $ and percentage for %
- If the user query contains currency or a number, convert it into words eg. ₹ 100 -> one Hundred rupees , 3500 rupees -> thirty-five hundred rupees, ₹ 500 -> five hundred rupees , 0.5 -> or 5 -> five  .
- Always use currency as rupees 
- the user query should not contain </s> eg. Calculate the cost of a dozen eggs for me.
- the assistant response should contain  </s> after numbers  in between the opening and closing tags of <calculator> and </calculator> and also after end of the response. eg. ASSISTANT: The cost of a dozen eggs would be <calculator> 1*12 </s> 12 </calculator> twelve rupees. </s>
- Output only one conversation at a time. 

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


def get_to_3_similar_conversations(current_conversation):
    # Get the top 3 conversations from the database symanitcally similar to the current conversation
    results = collection.search(
        data=[get_embedings(current_conversation)],
        anns_field="embeding",
        param={"metric_type": "COSINE"},
        limit=3,
        output_fields=["conversation"]
    )[0]

    prev_conversations = []
    for hit in results:
        prev_conversations.append(
            f"Similarity: {hit.distance}\n" + hit.entity.get('conversation').get('data'))

    if len(prev_conversations) < 3:
        prev_conversations.extend(
            ["Not Enough Data"] * (3 - len(prev_conversations)))

    return prev_conversations


def get_embedings(conv: str):
    tokens = tokenizer(conv, return_tensors="pt",
                       padding=True, truncation=True)
    tokens = {k: v.to(bert_model.device) for k, v in tokens.items()}
    with torch.no_grad():
        embedings = bert_model(**tokens).last_hidden_state[:, -1]
    return embedings.squeeze().cpu().numpy().tolist()


def accept_data(current_conversation, prev_conversation_1, prev_conversation_2, prev_conversation_3):
    if not current_conversation:
        gr.Error("No data to accept")
        return current_conversation, prev_conversation_1, prev_conversation_2, prev_conversation_3

    if not user_query_check(current_conversation) or not assistant_response_check(current_conversation):
        return current_conversation, prev_conversation_1, prev_conversation_2, prev_conversation_3

    # Insert current conversation into the database
    collection.insert(
        [{
            "embeding": get_embedings(current_conversation),
            "conversation": {
                "data": current_conversation,
            }
        }]
    )

    new_conversation = data_points.get()
    similar_conversations = get_to_3_similar_conversations(new_conversation)
    return new_conversation, similar_conversations[0], similar_conversations[1], similar_conversations[2]


def reject_data():
    new_conversation = data_points.get()
    similar_conversations = get_to_3_similar_conversations(new_conversation)
    return new_conversation, similar_conversations[0], similar_conversations[1], similar_conversations[2]

# `USER` query check
def user_query_check(conversation: str):
    user_queries = [conversation for conversation in conversation.split("\n") if conversation.startswith("USER:")]
    regex = re.compile("[^a-zA-Z0-9-,.: ]")
    for query in user_queries:
        if regex.search(query):
            gr.Error("`USER:` query regex check failed.")

# `ASSISTANT` response check
# def assistant_response_check(conversation: str):
#     assistant_responses = [conversation for conversation in conversation.split("\n") if conversation.startswith("ASSISTANT:")]
#     for response in assistant_responses:
#         # Check that it ends with </s>.
#         if response.endswith("</s>") == False:
#             gr.Error("`ASSISTANT:` does not end with </s>.")
#             return False

#         # If response contains <calculator> then it should also contain </calculator>
#         if "<calculator>" in response and "</calculator>" not in response:
#             gr.Error("`ASSISTANT:` contains <calculator> but not </calculator>.")
#             return False
#         if "</calculator>" in response and "<calculator>" not in response:
#             gr.Error("`ASSISTANT:` contains </calculator> but not <calculator>.")
#             return False

#         if "<calculator>" in response and "</calculator>" in response:
            
#             # Between <calculator> and </calculator> there should be a </s> token.
#             if "</s>" not in response[response.index("<calculator>")+12:response.index("</calculator>")+13]:
#                 gr.Error("Between <calculator> and </calculator> there should be a </s> token.")
#                 return False
            
#             # Between <calculator> and </s> token there should be a calculation.
#             regex = re.compile("[^0-9+-/* ]")
#             calculator_input = response[response.index("<calculator>")+12:response.index("</s>")]
#             calculator_output = response[response.index("</s>")+4:response.index("</calculator>")]
#             if regex.search(calculator_input):
#                 gr.Error("Between <calculator> and </s> token there should be a calculation.")
#                 return False

#             if regex.search(calculator_output):
#                 gr.Error("Between </s> and </calculator> there should be a calculation.")
#                 return False

#             evaluated_input = eval(calculator_input)
#             if str(float(evaluated_input)).split(".")[1] == "0":
#                 evaluated_input = int(evaluated_input)
#             if evaluated_input != eval(calculator_output):
#                 gr.Error("The calculation is not correct.")
#                 return False

def assistant_response_check(conversation: str):
    assistant_responses = [conversation for conversation in conversation.split("\n") if conversation.startswith("ASSISTANT:")]

    for response in assistant_responses:
        calculator_matches = re.findall(r"<calculator>(.*?)<\/calculator>", response)
        if calculator_matches:
            for calculator_block in calculator_matches:
                
                calc_input = calculator_block.split("</s>")[0].strip()
                calc_output = calculator_block.split("</s>")[1].strip()
                if calc_input is None or calc_output is None:
                    gr.Error("ERROR in calculator block")

                calc_input_regex = re.compile("[^0-9+-/* ]")
                calc_output_regex = re.compile("[^0-9 ]")
                if calc_input_regex.search(calc_input) or calc_output_regex.search(calc_output):
                    gr.Error("ERROR in calculator block")

                evaluated_input = eval(calc_input)
                if str(float(evaluated_input)).split(".")[1] == "0":
                    evaluated_input = int(evaluated_input)
                if evaluated_input != eval(calc_output):
                    gr.Error("The calculation is not correct.")

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.HTML("""
    <h1 style="text-align: center; user-select:None; ">DATASET GENERATOR</h1>
    """)

    with gr.Row():
        mt_conversation = gr.Textbox(label="Generated MT Conversation",
                                     placeholder="Click Reject to get 1st data point", interactive=True)

    with gr.Row():
        accept_btn = gr.Button(value="Accept")
        reject_btn = gr.Button(value="Reject")

    with gr.Column():
        gr.Markdown("## Top Conversation taht already exists in the database")
        prev_conversation_1 = gr.Textbox(
            label="Conversation 1", placeholder="", interactive=False)
        prev_conversation_2 = gr.Textbox(
            label="Conversation 2", placeholder="", interactive=False)
        prev_conversation_3 = gr.Textbox(
            label="Conversation 3", placeholder="", interactive=False)

    accept_btn.click(accept_data,
                     inputs=[mt_conversation, prev_conversation_1, prev_conversation_2, prev_conversation_3], 
                     outputs=[mt_conversation, prev_conversation_1, prev_conversation_2, prev_conversation_3])
    reject_btn.click(reject_data, outputs=[mt_conversation, prev_conversation_1, prev_conversation_2, prev_conversation_3])

if __name__ == "__main__":
    Thread(target=push_data_to_queue, args=(data_points,)).start()
    demo.launch()
