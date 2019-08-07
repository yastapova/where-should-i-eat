import http.client
import json
import urllib
import os

YELP_API_KEY = os.environ["YELP_API_KEY"]

# from .keys import YELP_API_KEY

api_url = "api.yelp.com"
search_cuisine = "/v3/businesses/search?"
headers = {
    "authorization": "Bearer " + YELP_API_KEY
}


def search_cuisine_yelp(categories, location):
    if location is None or location == "":
        location = "New York, NY"

    data = query_yelp(categories, location)
    data = data["businesses"]
    data = process_results(data)

    return data


def query_yelp(categories, location):
    # categories.append("restaurants")
    categories = ",".join(categories)
    params = {"categories": categories, "location": location}

    param_string = urllib.parse.urlencode(params)
    full_url = search_cuisine + param_string

    # establish connection to api
    conn = http.client.HTTPSConnection(api_url)
    conn.request("GET", full_url, headers=headers)

    response = conn.getresponse()
    data = response.read()
    data = json.loads(data.decode("utf-8"))

    return data


def process_results(results, top_n=10):
    results = results[0:top_n]
    new_results = []

    for r in results:
        business = {"name": r["name"]}

        categories = [c["title"] for c in r["categories"]]
        categories = ", ".join(categories)
        business["categories"] = categories
        business["url"] = r["url"]
        business["rating"] = r["rating"]
        business["review_count"] = r["review_count"]

        new_results.append(business)

    return new_results
