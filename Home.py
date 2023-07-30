import streamlit as st
import search_index
import css; css.set_page_style('Next Search Job • Find')
from datetime import datetime, timedelta
from streamlit.components.v1 import html
import google_analytics; google_analytics.inject_google_analytics()



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


# Update session query from Find Similar Jobs
def update_session_query(new_query):
    st.session_state.query = new_query


# Get link clicks from the last 14 days
end_date = datetime.utcnow().date()
start_date = end_date - timedelta(days=14)
link_click_dict = google_analytics.query_google_analytics(
    'link_clicks', start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))


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
        col1, col2 = st.columns([0.95,0.05])
        with col1:
            st.write(f"""<div class="job-link">{n}. """+
                    f"""<a href="{result['_source']['url']}" target="_blank" onclick="gtag('event', 'click', """
                    +"""{'event_category' : 'outbound', 'event_label' : """
                    +f"""'{result['_source']['url']}'"""+"""});">"""
                    +f"""{result['_source']['title']} @ {result['_source']['company']}</a>"""
                    +"</div><br>", unsafe_allow_html=True)
        with col2:
            st.button(f"{link_click_dict.get(result['_source']['url'], 0)}",
                    key=result['_source']['url']+'_LINK_CLICKS',
                    help='Number of times this link has been clicked in the last 14 days.',
                    disabled=True)
        st.button('Find Similar Jobs',
                key=result['_source']['url']+'_FIND_SIMILAR_JOBS',
                on_click=update_session_query,
                kwargs={'new_query':result['_source']['title']})
        st.markdown(f"""
        <div style="padding:0px 0px 16px;"><b>{poster_msg}</b></div>
        <div>{result['_source']['description'][:1000]+'...'}</div>
        <hr>
        """, unsafe_allow_html=True)