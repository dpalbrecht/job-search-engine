from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3
from datetime import datetime



# Get session client
credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, 'us-west-1')
client = OpenSearch(
    hosts = [{'host': 'search-opensearch-jobs-af5xd22qh6zatxk5wbfhnvdje4.us-west-1.es.amazonaws.com',
              'port': 443}],
    http_auth = auth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
)
index_name = 'jobs-index'



def query(user_query):
    query = {
      'size': 10,
      'query': {
        'multi_match': {
          'query': user_query,
          'fields': ['title^1','description^1'],
          "type": "most_fields", # if we expect search terms to appear in most fields
          "operator": "or",
          "minimum_should_match": 1,
          "tie_breaker": 1.0, # sum of all field scores
          "analyzer": "english",
          "boost": 1,
          "fuzziness": "AUTO",
          "fuzzy_transpositions": True, # reduces the number of fuzziness movements for adjacent characters
          "lenient": False, # allows data type mismatches
          "prefix_length": 0, # number of leading characters that are not considered in fuzziness
          "auto_generate_synonyms_phrase_query": True, # enables synonym searches if you have them
          "zero_terms_query": "none" # returns no results if query gets reduced to no terms (if all of them are stopwords)
        }
      }
    }
    response = client.search(
        body = query,
        index = index_name
    )
    return response


def count():
    return client.count(index=index_name)['count']


def post(payload):
    payload['url'] = payload['url'].strip('/')
    payload['created_at'] = datetime.utcnow().strftime('%Y-%m-%d')
    if len(payload['poster'])==0:
        payload['poster'] = 'Unknown'
    try:
        client.index(index=index_name, body=payload, id=payload['url'])
        return True
    except:
        return False
