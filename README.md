# job-search-engine
A job search engine and site created for the Relevance &amp; Matching Tech community on Slack (relevancy.slack.com).  
<br>
![alt text](https://github.com/dpalbrecht/job-search-engine/blob/main/images/homepage.png)  
<br><hr><br>

## How did this site come about?
Soon after I joined the group and started perusing open roles in the #jobs channel, I realized there was an opportunity to 1) build a quick search engine MVP and 2) contribute to the community. Below are the steps I took to deploy the site:
1. Create a new AWS account, so you can use Free Tier resources.
2. Create an [OpenSearch](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/gsgcreate-domain.html) instance.
	- When setting up fine-grained access control, create a user using IAM and use it as the master user.
3. Create the index and mapping using either the [OpenSearch Dashboard](https://opensearch.org/docs/latest/dashboards/quickstart-dashboards/), [command line](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/gsgupload-data.html), or [juptyer notebook](https://dylancastillo.co/opensearch-python/#create-an-index) (my personal recommendation). For the latter two, you'll need to either pass in your AWS credentials explicitly or install the CLI (`pip install awscli`) and run `aws configure` where you will store them (_highly_ recommended). 
4. Build your [Streamlit](https://streamlit.io/) app (or copy what I have above).
5. [Deploy on EC2](https://towardsdatascience.com/how-to-deploy-a-streamlit-app-using-an-amazon-free-ec2-instance-416a41f69dc3).
	- Just as in step 3, for local access, you'll need to `aws configure` so the app can query the index.

<br><hr><br>
## Notable Updates
* [4/23] Get a real domain name by using Amazon Route 53 and PairDomains.com
* [4/23] Enable user to search for "more jobs like this" with a single button click
* [5/23] Track user behavior <s>with Streamlit Analytics</s> <s>by writing page load and click events to S3, and a nightly cron for aggregating them</s> with Google Analytics (7/29). Add a page to visualize activity
* [5/23] Align dev and prod environments by using Docker
* [6/23] Add new page, Scrape Jobs, so developers can more easily pull in jobs to the site
* [7/19] Enable HTTPS