import streamlit as st
import search_index
import css; css.set_page_style('Next Search Job • Find')
from datetime import datetime
from streamlit.components.v1 import html
import json
import boto3
s3_resource = boto3.resource('s3')



# Record page loads to S3
if 'page_loaded' not in st.session_state:
    st.session_state['page_loaded'] = True
    s3_object = s3_resource.Object('page-loads', f'temp/{datetime.utcnow()}')
    s3_object.put(Body=(b''))


# Title and search bar, and format options
if 'query' not in st.session_state:
    st.session_state.query = ''
st.markdown('<h1>Search Relevance & Matching Tech</h1>', unsafe_allow_html=True)
st.markdown("""<h4><a href="https://www.opensourceconnections.com/slack/">Join the Slack Channel</a></h4><br><br>""", unsafe_allow_html=True)
col1, col2, _ = st.columns([1,2,1])
with col1:
    st.markdown('<h3 style="text-align:end; padding:0px;">&#x1F50D;&#xFE0D;</h3>', unsafe_allow_html=True)
with col2:
    query = st.text_input(label="Find jobs...",
                          value=st.session_state.query,
                          placeholder='Search through jobs...',
                          label_visibility='collapsed')
    most_recent_flag = st.checkbox(label='Last 30 Days', value=True)
    eu_flag = st.checkbox(label='EU')
    json_flag = st.checkbox(label='JSON Format')
    st.write(f"{search_index.count(most_recent_flag, eu_flag):,} jobs to be exact!")
st.markdown('<hr>', unsafe_allow_html=True)


# Open new tab and write log to S3
def click_job_url(url, query, rank):
    html(f"""<script type="text/javascript">window.open('{url}', '_blank');</script>""", height=0)
    s3_object = s3_resource.Object('job-clicks', f'{datetime.utcnow()}.json')
    s3_object.put(
        Body=(bytes(json.dumps({'query':query, 'url':url, 'rank':rank}).encode('UTF-8')))
    )


# Update session query from Find Similar Jobs
def update_session_query(new_query):
    st.session_state.query = new_query


# Show query results
if len(query) == 0:
    query_results = search_index.blank_query(query, eu_flag, most_recent_flag)
else:
    query_results = search_index.query(query, eu_flag, most_recent_flag)
if json_flag:
    st.json(query_results['hits']['hits'])
else:
    for n, result in enumerate(query_results['hits']['hits'], 1):
        days_ago_posted = (datetime.utcnow() - datetime.strptime(result['_source']['created_at'], '%Y-%m-%d')).days
        if result['_source']['poster'] != 'Unknown':
            poster_msg = f"{result['_source']['poster']} posted {days_ago_posted} days ago"
        else:
            poster_msg = f"Posted {days_ago_posted} days ago"
        st.markdown(f"<h3>{n}. {result['_source']['company']}</h3>", unsafe_allow_html=True)
        st.button(result['_source']['title'],
                    key=result['_source']['url'],
                    on_click=click_job_url,
                    kwargs={'url':result['_source']['url'], 'query':query, 'rank':n})
        st.button('Find Similar Jobs',
                    key=result['_source']['url']+'_FIND_SIMILAR_JOBS',
                    on_click=update_session_query,
                    kwargs={'new_query':result['_source']['title']})
        st.markdown(f"""
        <div style="padding:0px 0px 16px;"><b>{poster_msg}</b></div>
        <div>{result['_source']['description'][:1000]+'...'}</div>
        <hr>
        """, unsafe_allow_html=True)
