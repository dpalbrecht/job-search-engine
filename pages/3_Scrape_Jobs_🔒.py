import streamlit as st
import json
from serpapi import GoogleSearch
import sys; sys.path.append('..')
import search_index
from datetime import datetime
import css; css.set_page_style('Next Search Job • 🔒')
import boto3
from dotenv import load_dotenv; load_dotenv()
import os
s3_resource = boto3.resource('s3')
s3_client = boto3.client('s3')



def remove_job_from_session_state(job_data):
    st.session_state['current_query']['jobs_to_display'] = [job for job in st.session_state['current_query']['jobs_to_display'] 
                                                            if job['job_id'] != job_data['job_id']]
    st.session_state['current_query']['job_ids_to_display'].remove(job['job_id'])


def filter_job_data(job):
    keys_to_keep = ['company_name','title','description',
                    'merged_description','job_url','job_id']
    return {key:job[key] for key in keys_to_keep}


def add_job_to_site(query, job_data):
    payload = {
        'company': job_data['company_name'],
        'title': job_data['title'],
        'description': job_data['merged_description'],
        'url': job_data['job_url'],
        'poster': '',
        'email': '',
        'slack_blurb': '',
        'eu': False
    }
    success = search_index.post(payload)
    remove_job_from_session_state(job_data)


def remove_job_listing(query, job_data):
    job_url = job_data['job_url'].replace('/',';')
    s3_object = s3_resource.Object('scraped-job-urls', f"blocked/{job_url}")
    s3_object.put(Body=json.dumps(job_data))
    remove_job_from_session_state(job_data)


def get_blocked_job_urls():
    response = s3_client.list_objects_v2(Bucket='scraped-job-urls', Prefix='blocked')
    keys = [r['Key'].replace('blocked/','') for r in response.get('Contents', [])]
    return set(keys)


def get_job_link(job_id):
    params = {
        "engine": "google_jobs_listing",
        "q": job_id,
        "api_key": os.environ['SERPAPI_KEY']
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    apply_options = sorted(results['apply_options'], key=lambda x: x['title'])
    for apply_option in apply_options:
        if apply_option['title'] == "Apply on LinkedIn":
            return apply_option['link']
    return results['apply_options'][0]['link']


def get_job_listings(query, search_param_start):
    search_params = {
        "q": query,
        "engine": "google_jobs",
        "location_requested": "United States",
        "location_used": "United States",
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us",
        "ltype": "1",
        "start": search_param_start,
        "api_key": os.environ['SERPAPI_KEY']
    }
    search = GoogleSearch(search_params)
    results = search.get_dict()
    return results.get('jobs_results', [])


def merge_job_description(job):
    description = job['description'] + "\n"
    for highlight in job['job_highlights']:
        if highlight.get('title'):
            description += highlight['title']  + "\n"
        for item in highlight['items']:
            description += item  + "\n"
    job['merged_description'] = description
    return job


def display_similar_jobs(job):
    query = f"{job['title']} @ {job['company_name']}"
    query_results = search_index.query(query, eu_flag=False, most_recent_flag=True, num_results=3)
    spaces = ''.join(['&nbsp;']*10)
    st.write('Similar jobs we added in the last 30 days:')
    for n, result in enumerate(query_results['hits']['hits'], 1):
        st.markdown(f"""{spaces}{n}) <a href="{result['_source']['url']}" target="_blank">{result['_source']['title']} @ {result['_source']['company']}</a>""", 
                    unsafe_allow_html=True)


def display_this_job(n, job, query):
    st.markdown(f"""
        <h3>{n}. 
            <a href="{job['job_url']}" target="_blank">{job['title']} @ {job['company_name']}</a>
        </h3>""", unsafe_allow_html=True)
    display_similar_jobs(job)
    st.button("Add to Site", 
              key=job['job_id'],
              on_click=add_job_to_site,
              kwargs={'job_data':job, 'query':query})
    st.markdown(f"""
    <div style="padding:0px 0px 16px;"><b>Posted {job.get('detected_extensions',{}).get('posted_at','Unknown')}</b></div>
    <div>{job['merged_description'][:1000]+'...'}</div>
    """, unsafe_allow_html=True)
    st.button("Don't Show This Job Again", 
              key=job['job_id']+"-2",
              on_click=remove_job_listing,
              kwargs={'job_data':job, 'query':query})


def add_new_session_state(query):
    st.session_state['queries'][query] = {
        'query': query,
        'job_ids_to_display': set(),
        'jobs_to_display': [],
        'search_param_start': 0
    }



# Password check
placeholder = st.empty()
input_password = placeholder.text_input(label="This page is locked. What's the password?",
                                        value='', type='password').lower()

if st.session_state.get('password') or (input_password == os.environ['STREAMLIT_PW']):
    st.session_state['password'] = True
    placeholder.empty()

    # Title and search bar
    st.markdown('<h1>Add More Jobs!</h1>', unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;''>(be careful pulling in jobs as some sites have old postings)</div><br>", unsafe_allow_html=True)
    col1, col2, _ = st.columns([1,2,1])
    with col1:
        st.markdown('<h3 style="text-align:end; padding:0px;">&#x1F50D;&#xFE0D;</h3>', unsafe_allow_html=True)
    with col2:
        query = st.text_input(label="Find jobs...",
                            value="search engineer",
                            placeholder='Search through jobs...',
                            label_visibility='collapsed')
    st.markdown('<hr>', unsafe_allow_html=True)


    # Display query results
    if query:
        if 'queries' not in st.session_state:
            st.session_state['queries'] = {}
        if query not in st.session_state['queries']:
            add_new_session_state(query)
        st.session_state['current_query'] = st.session_state['queries'][query]

        if len(st.session_state['current_query']['jobs_to_display']) < 10:
            blocked_job_urls = get_blocked_job_urls()

        percent_complete = int(len(st.session_state['current_query']['jobs_to_display'])/10)
        progress_bar = st.progress(percent_complete, text='Fetching Jobs...')

        while len(st.session_state['current_query']['jobs_to_display']) < 10:

            job_listings = get_job_listings(query, st.session_state['current_query']['search_param_start'])
            if len(job_listings) == 0:
                break

            for n, job in enumerate(job_listings, 1):

                if job['job_id'] not in st.session_state['current_query']['job_ids_to_display']:
                    job['job_url'] = get_job_link(job['job_id'])

                    # If the job link is already in OpenSearch, don't show it
                    if (not search_index.already_posted_job(job['job_url'])) \
                        and (job['job_url'].replace('/',';') not in blocked_job_urls):

                        # Merge description text
                        job = merge_job_description(job)

                        # Keep only necessary data to save cache space
                        job = filter_job_data(job)

                        # Add job to those we want to display
                        st.session_state['current_query']['jobs_to_display'].append(job)
                        st.session_state['current_query']['job_ids_to_display'].add(job['job_id'])

                        # Update progress bar
                        percent_complete += 10
                        progress_bar.progress(percent_complete, text='Fetching Jobs...')
                        if len(st.session_state['current_query']['jobs_to_display']) == 10:
                            break

            st.session_state['current_query']['search_param_start'] += 10

        # Display jobs
        for n, job in enumerate(st.session_state['current_query']['jobs_to_display'], 1):
            display_this_job(n, job, query)
            st.markdown("<hr>", unsafe_allow_html=True)            
        progress_bar.empty()
else:
    if input_password != '':
        st.warning(f"Incorrect password! {datetime.utcnow().strftime('%H-%M-%S')}", icon='🚨')