"""
This file is used to generate mt data for JARVIS for `calculator`.
"""

import streamlit as st


st.header("USER Query")
st.text("What is 2 + 2?")

st.header("ASSISTANT Response")
st.text("2 + 2 = 4")

btns = st.radio("Is the response correct?", ("Yes", "No"))
st.button("Submit")