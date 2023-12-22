"""
This WebUI is used to built so that humans and AI can colaborate to validate data.
"""

import pymongo
import json
import os
from jsonschema import validate, ValidationError, SchemaError
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB and get the collection
_URI = f"mongodb://{os.environ['MONGODB_USERNAME']}:{os.environ['MONGODB_PASSWORD']}@{os.environ['MONGODB_HOST']}:{os.environ['MONGODB_PORT']}"
client = pymongo.MongoClient(_URI)
db = client["function_calling"]

# Page Header
st.title("Data Validation")

# Dropdown to select the collection
st.sidebar.title("Select the collection")
collection = st.sidebar.selectbox(
    label='Collection',
    options=db.list_collection_names(),
    # key="collection",
)
collection = db[collection]

# Select the split of the data to validate
st.sidebar.title("Select the split")
data_split = st.sidebar.selectbox(
    label="Split",
    options=[
        f"{str(split_name).capitalize()} Split ({collection.count_documents({'split': split_name})} documents)" 
        for split_name in collection.distinct("split")
    ],
    # key="split",
)


if data_split:
    data_split = data_split.split(" ")[0].lower()
    total_documents = collection.count_documents({"split": data_split})
    document = collection.find_one(
        {
            "split": data_split.split(" ")[0].lower(),
        }
    )
    st.json(document)

