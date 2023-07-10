import streamlit as st



def set_page_style(page_title):
    st.set_page_config(page_title=page_title, page_icon='images/relevant_search.jpg', layout='wide')
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
        div.job-link {
          font-size: 28px;
        }
    </style>
    """
    st.markdown(margins_css, unsafe_allow_html=True)
