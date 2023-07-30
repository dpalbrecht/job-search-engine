from dotenv import load_dotenv; load_dotenv()
import os
import pathlib
from bs4 import BeautifulSoup
import shutil
import streamlit as st
from collections import defaultdict
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    FilterExpression,
    Filter
)



def inject_google_analytics():
    GA_ID = os.environ['GOOGLE_ANALYTICS_ID']
    
    GA_JS = f"""
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>"""+"""
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
    """+f"""
        gtag('js', new Date());
        gtag('config', '{GA_ID}');
    </script>
    """

    # Insert the script in the head tag of the static template inside your virtual
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")
    if not soup.find(id=GA_ID):  # if cannot find tag
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)  # recover from backup
        else:
            shutil.copy(index_path, bck_index)  # keep a backup
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + GA_JS)
        index_path.write_text(new_html)


def get_data(query):
    credentials = service_account.Credentials.from_service_account_file(
        'google_analytics_credentials.json',
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )
    client = BetaAnalyticsDataClient(credentials=credentials)
    response = client.run_report(query)
    return response.rows


def parse_page_events(response):
    data = defaultdict(lambda: defaultdict(lambda: 0))
    for row in response:
        event_name, page_title = row.dimension_values
        event_count = row.metric_values[0]
        data[event_name.value][page_title.value] += int(event_count.value)
    return data


def parse_link_clicks(response):
    data = defaultdict(lambda: 0)
    for row in response:
        link_name = row.dimension_values[0]
        click_count = row.metric_values[0]
        data[link_name.value] += int(click_count.value)
    return data


def query_google_analytics(report_type, start_date, end_date):
    if report_type == 'page_events':
        query = RunReportRequest(
            property=f"properties/{os.environ['GA4_PROPERTY_ID']}",
            dimensions=[Dimension(name="eventName"), Dimension(name="pageTitle")],
            metrics=[Metric(name="eventCount")],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimension_filter=FilterExpression(
                filter=Filter(
                    field_name="eventName",
                    in_list_filter=Filter.InListFilter(values=["page_view","click"])
                )
            )
        )
        return parse_page_events(get_data(query))
    elif report_type == 'link_clicks':
        query = RunReportRequest(
            property=f"properties/{os.environ['GA4_PROPERTY_ID']}",
            dimensions=[Dimension(name="customEvent:link_url")],
            metrics=[Metric(name="eventCount")],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)]
        )
        return parse_link_clicks(get_data(query))