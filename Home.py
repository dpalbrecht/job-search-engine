import streamlit as st
import search_index
import css; css.set_page_style()
from datetime import datetime
import requests



st.markdown('<h1>Search Relevance & Matching Tech</h1><br>', unsafe_allow_html=True)

col1, col2, _ = st.columns([1,2,1])
with col1:
    st.markdown('<h3 style="text-align:end; padding:0px;">&#x1F50D;&#xFE0D;</h3>', unsafe_allow_html=True)
with col2:
    query = st.text_input(label="Find jobs...",
                          placeholder=f"Search through {search_index.count():,} jobs...",
                          label_visibility='collapsed')

query_results = search_index.query(query)
for result in query_results['hits']['hits']:
    days_ago_posted = (datetime.utcnow() - datetime.strptime(result['_source']['created_at'], '%Y-%m-%d')).days
    st.markdown(f"""
    <hr>
    <h3>{result['_source']['company']}</h3>
    <h5><a href={result['_source']['url']}>{result['_source']['title']}</a></h5>
    <div style="padding:0px 0px 16px;"><b>{result['_source']['poster']} posted {days_ago_posted} days ago</b></div>
    <div>{result['_source']['description'][:1000]+'...'}</div>
    """, unsafe_allow_html=True)
st.markdown('<hr>', unsafe_allow_html=True)
