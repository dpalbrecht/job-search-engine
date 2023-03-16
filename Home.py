import streamlit as st
import search_index
import css; css.set_page_style()
from datetime import datetime
from wordcloud import WordCloud, STOPWORDS



# Title and search bar, and format options
st.markdown('<h1>Search Relevance & Matching Tech</h1>', unsafe_allow_html=True)
st.markdown("""<h4><a href="https://www.opensourceconnections.com/slack/">Join the Slack Channel</a></h4><br><br>""", unsafe_allow_html=True)
col1, col2, _ = st.columns([1,2,1])
with col1:
    st.markdown('<h3 style="text-align:end; padding:0px;">&#x1F50D;&#xFE0D;</h3>', unsafe_allow_html=True)
with col2:
    query = st.text_input(label="Find jobs...",
                          placeholder=f"Search through {search_index.count():,} jobs...",
                          label_visibility='collapsed')
    most_recent_flag = st.checkbox(label='Last 30 Days', value=True)
    eu_flag = st.checkbox(label='EU')
    json_flag = st.checkbox(label='JSON Format')
    if not query:
        random_text = ''
        for doc in search_index.random_query()['hits']['hits']:
            random_text += doc['_source']['title'] + ' '
        wordcloud = WordCloud(width=800, height=400,
                              background_color="white",
                              stopwords=STOPWORDS,
                              mode='RGBA',
                              colormap='plasma',
                              collocations=False,
                              min_word_length=2).generate(random_text)
        st.image(wordcloud.to_image())
st.markdown('<hr>', unsafe_allow_html=True)



# Show query results
query_results = search_index.query(query, eu_flag, most_recent_flag)
if json_flag:
    st.json(query_results['hits']['hits'])
else:
    for n, result in enumerate(query_results['hits']['hits'], 1):
        days_ago_posted = (datetime.utcnow() - datetime.strptime(result['_source']['created_at'], '%Y-%m-%d')).days
        st.markdown(f"""
        <h3>{n}. {result['_source']['company']}</h3>
        <h5><a href={result['_source']['url']}>{result['_source']['title']}</a></h5>
        <div style="padding:0px 0px 16px;"><b>{result['_source']['poster']} posted {days_ago_posted} days ago</b></div>
        <div>{result['_source']['description'][:1000]+'...'}</div>
        <hr>
        """, unsafe_allow_html=True)
