import streamlit as st



def set_page_style():
    st.set_page_config(layout="wide")
    margins_css = """
    <style>
        .main > div {
            padding-top: 2rem;
        }
        h1 {
          text-align: center;
        }
        h4 {
          text-align: center;
        }
        div.stButton>button {
            color: #4F8BF9;
            backgroud-color: #00ff00;
            text-decoration: underline;
            border-width: 3;
        }
    </style>
    """
    st.markdown(margins_css, unsafe_allow_html=True)
