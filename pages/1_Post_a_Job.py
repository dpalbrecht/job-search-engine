import streamlit as st
import sys
import json
sys.path.append('..')
import search_index
import css; css.set_page_style('Next Search Job • Post')
from datetime import datetime
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import requests



def crawl(url):
    # From https://colab.research.google.com/drive/1L_s0ey6T-aK65J2wHSZEhoBVW8vmJlkH?usp=sharing#scrollTo=a8yeMg5Tv9Nx

    # Determine whether the host is supported (LinkedIn only at the moment)
    parsed = urlparse(url)
    if parsed.hostname not in ['linkedin.com', 'www.linkedin.com']:
        return {}

    # Scrape the data
    html = requests.get(url).content
    soup = BeautifulSoup(html)
    description = soup.find(
        name='div',
        attrs={'class':"show-more-less-html__markup show-more-less-html__markup--clamp-after-5 relative overflow-hidden"}
    )
    description = description.get_text('\n').strip()
    title = soup.find('h1').text
    company = soup.find('a', {'href': re.compile('linkedin.com/company/*')}).text

    return {
        "url": url,
        "company": company,
        "title": title,
        "poster": '',
        "description": description,
    }


def crawl_and_populate():
    try:
        crawled_data = crawl(st.session_state.url)
        if crawled_data:
            st.session_state.url = crawled_data['url']
            st.session_state.title = crawled_data['title']
            st.session_state.company = crawled_data['company']
            st.session_state.description = crawled_data['description']
        else:
            st.warning(f"Only LinkedIn URLs currently supported... But you can still manually add your job below!", icon='🚨')
    except:
        st.warning(f"Something went wrong... But you can still manually add your job below!", icon='🚨')



# Title and post form
st.markdown('<h1>Post a Job</h1><br>', unsafe_allow_html=True)
_, col2, _ = st.columns([1,8,1])
with col2:
    with st.form("job_form"):
        url = st.text_input(label='URL', placeholder='* URL', label_visibility='collapsed', key='url')
        _ = st.form_submit_button('Auto-Populate (LinkedIn URL)', on_click=crawl_and_populate)
        payload = {
            'company': st.text_input(label='Company', key='company',
                                     placeholder='* Company', label_visibility='collapsed'),
            'title': st.text_input(label='Job Title', key='title',
                                   placeholder='* Job Title', label_visibility='collapsed'),
            'description': st.text_area(label='Description', placeholder='* Description',
                                        label_visibility='collapsed', key='description'),
            'url': url,
            'poster': st.text_input(label='Your Name', placeholder='Your Name', label_visibility='collapsed'),
            'eu': st.checkbox(label='EU')
        }
        password = st.text_input(label=' ', placeholder='* Password: What book is on the cover of the Search Relevance Slack channel?', label_visibility='collapsed')
        submitted = st.form_submit_button("Post")


# Display success/failure
if submitted:
    if password.lower() == 'relevant search':
        post_payload = True
        for name, value in payload.items():
            if (name not in ['poster', 'EU']) and (value == ''):
                post_payload = False
                st.warning(f"The '{name}' parameter is required. Can't post job.", icon='🚨')
        if post_payload:
            if search_index.already_posted_job(payload['url']):
                st.warning(f"This job has already been posted. {datetime.utcnow().strftime('%H-%M-%S')}", icon='⚠️')
            else:
                success = search_index.post(payload)
                if success:
                    st.success(f"Success! {datetime.utcnow().strftime('%H-%M-%S')}", icon='✅')
                else:
                    st.warning(f"Something went wrong! The job was not posted. {datetime.utcnow().strftime('%H-%M-%S')}", icon='🚨')
    else:
        st.warning(f"Incorrect password! {datetime.utcnow().strftime('%H-%M-%S')}", icon='🚨')
