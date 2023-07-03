import streamlit as st
import css; css.set_page_style('Next Search Job • Sponsors')



# Title
st.markdown('<h1>Thank You to Our Sponsors</h1><br>', unsafe_allow_html=True)
st.markdown('<hr>', unsafe_allow_html=True)


# Sponsors
cols = st.columns(5)
with cols[0]:
    st.image('images/serpapi.png', use_column_width=True)
    st.markdown("""<a href="https://serpapi.com/" target="_blank">SerpApi</a> kindly donated a year's worth of Developer access.""", unsafe_allow_html=True)