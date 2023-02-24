import streamlit as st
import sys
import json
sys.path.append('..')
import search_index
import css; css.set_page_style()
from datetime import datetime
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import requests


def raise_on_unsupported_job_site(url):
    parsed = urlparse(url)
    if parsed.hostname not in ['linkedin.com', 'www.linkedin.com']:
        raise ValueError(f"Unsupported host - {parsed.hostname}")


def crawl(url):
    # From https://colab.research.google.com/drive/1L_s0ey6T-aK65J2wHSZEhoBVW8vmJlkH?usp=sharing#scrollTo=a8yeMg5Tv9Nx
    raise_on_unsupported_job_site(url)

    html = requests.get(url).content
    soup = BeautifulSoup(html)
    description = soup.find(
        name='div',
        attrs={'class':"show-more-less-html__markup show-more-less-html__markup--clamp-after-5"}
    )
    description = description.get_text('\n')
    # company_info = json.loads(soup.find(name='script', attrs={'type':'application/ld+json'}).text)
    title = soup.find('h1').text
    company = soup.find('a', {'href': re.compile('linkedin.com/company/*')}).text

    return {
        "url": url,
        "company": company,
        "title": title,
        "poster": "Unknown",
        "description": description,
    }


def crawl_and_populate():
    url = st.session_state.crawl_url
    try:
        crawled = crawl(url)
        st.session_state.url = crawled['url']
        st.session_state.title = crawled['title']
        st.session_state.company = crawled['company']
        st.session_state.description = crawled['description']
    except ValueError:
        st.warning(f"Only LinkedIn URLs currently supported... However you can still manually add your job below", icon='🚨')



# Title and post form
st.markdown('<h1>Post a Job</h1><br>', unsafe_allow_html=True)
_, col2, _ = st.columns([1,8,1])
with col2:
    with st.form("crawl_form"):
        st.markdown("Attempt to populate by crawling job URL (beta)")
        st.text_input(label='URL', placeholder='URL *',
                      label_visibility='collapsed',
                      key='crawl_url')
        submitted = st.form_submit_button("Crawl (Beta)", on_click=crawl_and_populate)
    with st.form("job_form"):
        st.markdown("Edit / confirm your submission")
        payload = {
            'company': st.text_input(label='Company', key='company',
                                     placeholder='Company *', label_visibility='collapsed'),
            'title': st.text_input(label='Job Title', key='title',
                                   placeholder='Job Title *', label_visibility='collapsed'),
            'description': st.text_area(label='Description', placeholder='Description *',
                                        label_visibility='collapsed', key='description'),
            'url': st.text_input(label='URL', placeholder='URL *', label_visibility='collapsed',
                                 key='url'),
            'poster': st.text_input(label='Your Name', placeholder='Your Name', label_visibility='collapsed'),
            'eu': st.checkbox(label='EU')
        }
        submitted = st.form_submit_button("Post")


# Display success/failure
if submitted:
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
