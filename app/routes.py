from flask import render_template, request
from app import app
from .backend import search_cuisine_yelp
import json


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    """Creates the home page view."""

    return render_template('index.html')


@app.route('/search_cuisine', methods=['POST'])
def search_cuisine():
    """Search Yelp for restaurants by category."""
    categories = json.loads(request.form["categories"])
    location = request.form["location"]
    coords = json.loads(request.form["coords"])

    results = search_cuisine_yelp(categories, coords, location)

    return render_template("results.html", businesses=results)
