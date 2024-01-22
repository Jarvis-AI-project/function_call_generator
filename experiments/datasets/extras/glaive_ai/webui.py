"""Web UI for sorting and filtering Datasets for JARVIS"""

import random
import os
import streamlit as st
import pymongo
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(layout="wide", page_title="JARVIS Dataset Sorting and Filtering")
st.markdown("## JARVIS Dataset Sorting and Filtering")

_URI = f"mongodb://{os.environ['MONGODB_USERNAME']}:{os.environ['MONGODB_PASSWORD']}@{os.environ['MONGODB_HOST']}:{os.environ['MONGODB_PORT']}/{os.environ['MONGODB_DATABASE']}"

client = pymongo.MongoClient(_URI)
collection = client["function_calling"]["glaiveai_v2"]

def get_random_data_point() -> dict:
    """Get a random data point from the database"""
    record: dict = collection.find().skip(random.randint(0, collection.count_documents({}) - 1)).limit(1)[0]
    if record.get("data") and (record.get("data").get("categories") or record.get("data").get("categories") == []):
        return get_random_data_point()
    return record

def submit_handler(checkbox_values):
    """Function to execute when 'Submit' button is checked"""
    collection.update_one(
        {"_id": st.session_state.data["_id"]},
        {"$set": {"categories": [k for k, v in checkbox_values.items() if v]}},
    )

def write_data_point(data_point):
    """Write a data point to the web UI"""
    st.text("ID: " + str(data_point["_id"]))
    st.markdown("### SYSTEM PROMPT")
    st.text(data_point["data"]["system"])
    st.markdown("### CHAT")
    st.write(data_point["data"]["chat"])

def num_existing_data_points(category: str) -> int:
    """Count the number of existing data points"""
    return collection.count_documents({
        "categories": {
            "$elemMatch": {
                "$eq": category
            }
        }
    })

with st.sidebar:
    st.header("Categories")
    with st.form(key="categories_form", clear_on_submit=True):
        st.session_state.checkboxes = {
            "Calculator": st.checkbox(f"Calculator ({num_existing_data_points('Calculator')})", value=False),
            "Calendar": st.checkbox(f"Calendar ({num_existing_data_points('Calendar')})", value=False),
            "Clock": st.checkbox(f"Clock ({num_existing_data_points('Clock')})", value=False),
            "Todo List": st.checkbox(f"Todo List ({num_existing_data_points('Todo List')})", value=False),
            "General QnA": st.checkbox(f"General QnA ({num_existing_data_points('General QnA')})", value=False),
            "Code Generation": st.checkbox(f"Code Generation ({num_existing_data_points('Code Generation')})", value=False),
            "AI Denied Request": st.checkbox(f"AI Denied Request ({num_existing_data_points('AI Denied Request')})", value=False),
        }
        st.text("Choose all that apply and click 'Submit'")
        submit_button = st.form_submit_button(label="Submit", type="primary")

    st.text("'Skip' to skip this example")
    skip_button = st.button("Skip", key="skip_btn")

if submit_button:
    if list(st.session_state.checkboxes.values()).count(True) == 0:
        st.sidebar.error("You must select at least one category", icon="❌")
        write_data_point(st.session_state.data)
    else:
        submit_handler(st.session_state.checkboxes)
        st.session_state.data = get_random_data_point()
        write_data_point(st.session_state.data)
        st.sidebar.success("Submitted!", icon="✅")

if skip_button or not hasattr(st.session_state, "data"):
    st.session_state.data = get_random_data_point()
    write_data_point(st.session_state.data)
