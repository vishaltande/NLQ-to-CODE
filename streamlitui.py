import streamlit as st
import langchain_helper as lch

st.title("Ship Query System")

question = st.sidebar.text_area(label=f"Ask a question")

if st.sidebar.button("Get Answer"):
    response = lch.get_insights(question)
    # final = response['result'].split("````")[1]

    # st.write("Answer:", final)
    print(type(response))
    for key in response:
        print(key)
    print(response["result"])
    st.write("Answer:", response['result'])
