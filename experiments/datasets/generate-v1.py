"""This is python file for `generate-v1.ipynb` notebook. Used to generate data for `calculator_v1` collection."""
from dotenv import load_dotenv
import openai
import google.generativeai as genai
import os
from threading import Thread
import re
import time
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility, db
load_dotenv('../.env')

MAX_QUERIES_PER_MINUTE = 60
DATABASE_NAME = 'CUSTOM_DATASETS'
COLLECTION_NAME = 'calculator_v1'

SYSTEM_PROMPT = """
Generate a sample Multi-Turn conversation between a user and a voice assistant named JARVIS in which the voice assistant has the capability of using a calculator. The assistant has a frank personality and is very helpful.
The calculator can perform these arithmetic operations.
1. Addition (+): adds two operands
2. Subtraction (-): subtracts two operands
3. Multiplication (*): multiplies two operands
4. Division (/): divides two operands
5. Modulus (%): returns the remainder when the first operand is divided by the second
6. Floor division (//): returns the quotient when the first operand is divided by the second
7. Exponent (**): returns the first operand raised to the power of the second operand

Note: This calculator works on the BODMAS rule which means multiplication and division are performed before addition and subtraction.
Example Usage:
<calculator>2+3</calculator>

Note: If you need to use two or more operators in a single expression, you need to apply brackets to specify the order of operations.
Precedence of operators:
1. Exponentiation (**)
2. Multiplication (*), Division (/), Floor division (//), and Modulus (%)
3. Addition (+) and Subtraction (-)
Example Usage:
<calculator>2+(3*4)</calculator> Here, 3 and 4 will be multiplied first and then the result will be added to 2.

<|user|>
Hey, buddy, I'm planning a road trip, and I want to calculate the total distance I'll be driving. The trip involves multiple stops, and I have the distances between each pair of stops. Can you help me find the total distance?
<|assistant|>
Absolutely! I'd be happy to assist. Could you provide me with the distances between each pair of stops and the list of stops on your road trip?</s>
<|user|>
Sure, Home to Gas Station is 10 miles Gas Station to Mountain View is 30 miles Mountain View to Lakeside Park is 15 miles Lakeside Park to Beach Resort is 25 miles Beach Resort to Home is 40 miles.
<|assistant|>
Great, Let me calculate the total distance for you. <calculator>10+30+15+25+40<stop>120</calculator>The total distance is 120 miles. Is there anything else I can help you with?</s>
<|user|>
That's perfect. One more thing, what's the average speed I should maintain if I want to reach the Beach Resort in 2 hours?
<|assistant|>
Let me calculate that for you. <calculator>120/2<stop>60</calculator>You should maintain an average speed of 60 miles per hour. Is there anything else I can help you with?</s>
<|user|>
That's all I need. Thanks for your help.
<|assistant|>
You're welcome. Have a great trip! Drive Safe, and feel free to ask for any help.</s>

Generate more such conversations to train the assistant. 
- The main calculation should be surrounded by "<calculator>" and "</calculator>" which will not be shown to the user and is evaluated by a computer. 
- Assume this system is being used to do day-to-day tasks.
- Do not explain your calculation to the user.
- Avoid generating data points that require up-to-date knowledge.
- User query can't contain any kind of symbols such as (%, $,₹, .,), etc. Instead, it should use the corresponding word representation of the symbols eg. dollar for $ and percentage for %
- If the user query contains currency or a number, convert it into words eg. ₹100 -> one Hundred rupees, 3500 rupees -> thirty-five hundred rupees, ₹500 -> five hundred rupees, ₹.25 -> twenty-five paisa.
- Try to use currency as rupees
- the user query should not contain or end with "</s>" or "<stop>"
- Assistant response should end with "</s>"
- the assistant response should contain "<stop>" after the expression in between the opening and closing tags of "<calculator>" and "</calculator>". eg. ASSISTANT: The cost of a dozen eggs would be <calculator>1*12<stop>12</calculator>twelve rupees.</s>
- If calculator gives a float value, round it accordingly.
"""

## Setting API Keys and Connecting to the Database
openai.api_key = os.getenv('OPENAI_API_KEY')

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

connections.connect(
    alias="default",
    host=os.getenv("MILVUS_HOST"),
    port=os.getenv("MILVUS_PORT"),
    user=os.getenv("MILVUS_USER"),
    password=os.getenv("MILVUS_PASSWORD"),
)

## Creating Milvus Database to store embeddings and text data
if not DATABASE_NAME in db.list_database():
    db.create_database(DATABASE_NAME)
db.using_database(DATABASE_NAME)

if not COLLECTION_NAME in utility.list_collections():
    # Create collection
    conversation_id = FieldSchema(
        name="conversation_id", 
        dtype=DataType.INT64, 
        is_primary=True, 
        auto_id=True, 
        description="Unique id for each conversation"
    )
    embeding = FieldSchema(
        name="embeding", 
        dtype=DataType.FLOAT_VECTOR, 
        dim=1536,
        description="Embedings generated using text-embedding-ada-002-v2"
    )
    conversation = FieldSchema(
        name="conversation",
        dtype=DataType.VARCHAR,
        max_length=4096,
        description="Conversation between user and assistant"
    )

    schema = CollectionSchema(fields=[conversation_id, embeding, conversation], description=SYSTEM_PROMPT)

    collection = Collection(name=COLLECTION_NAME, schema=schema)

    collection.create_index(
        field_name="embeding", 
        index_params={
            "index_type": "IVF_FLAT",
            "metric_type": "COSINE",
            "params": {"nlist": 128}
        }
    )

    print(f'Collection {COLLECTION_NAME} created successfully.')

else:
    collection = Collection(name=COLLECTION_NAME)

collection.load()
print(f'Collection {COLLECTION_NAME} loaded successfully.')

## Function to get embeddings from OpenAI API
def get_embeding(text):
    text = text.replace("\n", " ")
    return openai.embeddings.create(
        model="text-embedding-ada-002",
        input=[text]
    ).data[0].embedding

## Gemini Configuration
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 1024,
}
model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
    safety_settings=None
)

## Test Cases
def assistant_response_endswith_eos_token(text: str):
    # Matches all the assistant responses in the text except the last one
    expr = r'<\|assistant\|>\n(.*?)<\|user\|>'
    assistant_responses = [x.strip() for x in re.findall(expr, text, re.DOTALL)]
    # Last assistant response
    assistant_responses.append(text.split('<|assistant|>')[-1].strip())
    return not all([x.endswith('</s>') for x in assistant_responses])

def stop_token_between_calculator_tags(text):
    expr = r'<calculator>(.*?)</calculator>'
    calculator_expressions = [x.strip() for x in re.findall(expr, text)]
    return not all([x.count('<stop>') == 1 for x in calculator_expressions])

def number_of_open_calc_tags_equal_number_of_close_calc_tags(text):
    return not text.count('<calculator>') == text.count('</calculator>')

def user_input_should_not_contain_special_token(text):
    spl_tokens = ['<s>', '</s>', '<unk>', '<calculator>', '</calculator>', '<stop>']
    expr = r'<\|user\|>\n(.*?)<\|assistant\|>'
    user_inputs = [x.strip() for x in re.findall(expr, text)]
    return not all([not any([x.count(y) > 0 for y in spl_tokens]) for x in user_inputs])

def number_of_user_inputs_equal_number_of_assistant_responses(text):
    return not text.count('<|user|>') == text.count('<|assistant|>')

def test_response(text):
    return assistant_response_endswith_eos_token(text) or stop_token_between_calculator_tags(text) or number_of_open_calc_tags_equal_number_of_close_calc_tags(text) or user_input_should_not_contain_special_token(text) or number_of_user_inputs_equal_number_of_assistant_responses(text)

## Generate Data
global num
num=0
def insert_data_point():
    global num
    try:
        response = model.generate_content(SYSTEM_PROMPT)
        embeding = get_embeding(response.text)

        if not test_response(response.text):
            collection.insert({
                "embeding": embeding,
                "conversation": response.text
            })
        num += 1
        print(f'Inserted data point {num}')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    while True:
        threads = [Thread(target=insert_data_point) for _ in range(MAX_QUERIES_PER_MINUTE)]
        for thread in threads:
            thread.start()
        time.sleep(60)
        for thread in threads:
            thread.join()
