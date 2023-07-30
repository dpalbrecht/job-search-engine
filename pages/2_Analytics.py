import streamlit as st
import sys
sys.path.append('..')
import css; css.set_page_style('Next Search Job • Analytics')
import plotly.graph_objs as go
import datetime
from google_analytics import query_google_analytics
from dotenv import load_dotenv; load_dotenv()



st.markdown('<h1>Site Analytics</h1>', unsafe_allow_html=True)
st.markdown('<hr><br>', unsafe_allow_html=True)



def plot_histogram(data, event_type):
    x, y = [], []
    for key, value in data[event_type].items():
        x.append(key)
        y.append(value)
    fig = go.Figure(data=go.Bar(x=x, y=y))
    fig.update_layout(title=f"{event_type.replace('_',' ').title()} Events", 
                      xaxis_title='Page', 
                      yaxis_title='Count')
    st.plotly_chart(fig)



# Plot a date range's activity
container1 = st.container()
with container1:
    cols1 = st.columns(5)
    with cols1[0]:
        dates = st.date_input(label='Choose a Date Range Display:', 
                              value=(datetime.datetime.utcnow().date()-datetime.timedelta(days=7), 
                                     datetime.datetime.utcnow().date()))
    start_date = dates[0].strftime('%Y-%m-%d')
    end_date = dates[1].strftime('%Y-%m-%d')
    page_event_dict = query_google_analytics('page_events', start_date, end_date)
    plot_histogram(page_event_dict, event_type='click')
    plot_histogram(page_event_dict, event_type='page_view')