import streamlit as st
import sys
sys.path.append('..')
import json
import boto3
import css; css.set_page_style('Next Search Job • Analytics')
import plotly.graph_objs as go
import datetime
s3_resource = boto3.resource('s3')



YESTERDAY = datetime.datetime.utcnow().date() - datetime.timedelta(days=1)
MIN_DATE = datetime.date(2023,6,20)
st.markdown('<h1>Site Analytics</h1>', unsafe_allow_html=True)
st.markdown('<hr><br>', unsafe_allow_html=True)


# Plot a date range's activity
def plot_date_range_activity(dates):
    x, y = [], []
    dates = [dates[0] + datetime.timedelta(days=x) for x in range((dates[1]-dates[0]).days + 1)]
    for date in dates:
        date_str = date.strftime('%Y-%m-%d')
        temp_data = json.loads(s3_resource.Object('page-loads', f'processed/{date_str}.json').get()['Body'].read())
        x.append(date_str)
        y.append(sum(list(temp_data.values())))
    fig = go.Figure(data=go.Bar(x=x, y=y))
    fig.update_layout(title=f'Page Loads from {x[0]} to {x[-1]}', 
                      xaxis_title='Date', 
                      yaxis_title='Load Count')
    fig.update_xaxes(dtick="D1", tickformat="%Y-%m-%d")
    st.plotly_chart(fig)


container1 = st.container()
with container1:
    cols1 = st.columns(5)
    with cols1[0]:
        dates = st.date_input(label='Choose a Date Range Display (UTC):', 
                              value=(max(YESTERDAY-datetime.timedelta(days=7), MIN_DATE), YESTERDAY),
                              min_value=MIN_DATE, 
                              max_value=YESTERDAY)
    plot_date_range_activity(dates)


# Plot a single day's activity
def plot_date_activity(date):
    data = json.loads(s3_resource.Object('page-loads', f'processed/{date}.json').get()['Body'].read())
    x, y = [], []
    for hour, activity in sorted([(int(k),int(v)) for k,v in data.items()], key=lambda x: x[0]):
        x.append(hour)
        y.append(activity)
    fig = go.Figure(data=go.Scatter(x=x, y=y, mode='lines+markers', 
                                    line=dict(dash='dot'), marker=dict(size=10)))
    fig.update_layout(title=f'Page Loads on {date}', 
                      xaxis_title='Hour of the Day', 
                      yaxis_title='Load Count')
    st.plotly_chart(fig)


container2 = st.container()
with container2:
    cols2 = st.columns(5)
    with cols2[0]:
        date = st.date_input(label='Choose a Date to Display (UTC):', 
                             value=YESTERDAY,
                             min_value=MIN_DATE, 
                             max_value=YESTERDAY)
    plot_date_activity(date)