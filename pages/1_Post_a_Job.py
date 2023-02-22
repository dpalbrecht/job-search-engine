import streamlit as st
import sys
sys.path.append('..')
import search_index
import css; css.set_page_style()
from datetime import datetime



# Title and post form
st.markdown('<h1>Post a Job</h1><br>', unsafe_allow_html=True)
_, col2, _ = st.columns([1,8,1])
with col2:
    with st.form("job_form"):
        payload = {
            'company': st.text_input(label='Company', placeholder='Company *', label_visibility='collapsed'),
            'title': st.text_input(label='Job Title', placeholder='Job Title *', label_visibility='collapsed'),
            'description': st.text_area(label='Description', placeholder='Description *', label_visibility='collapsed'),
            'url': st.text_input(label='URL', placeholder='URL *', label_visibility='collapsed'),
            'poster': st.text_input(label='Your Name', placeholder='Your Name', label_visibility='collapsed'),
            'eu': st.checkbox(label='EU')
        }
        submitted = st.form_submit_button("Post")


# Display success/failure
if submitted:
    print(payload)
    post_payload = True
    for name, value in payload.items():
        if (name not in ['poster','EU']) and (value == ''):
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
