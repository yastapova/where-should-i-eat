import pandas as pd
import re
import operator

data_folder = "static/data/"
yelp_data = data_folder + "yelp_dataset_challenge_academic_dataset/"


def average(data_list):
    n = len(data_list)

    if n > 0:
        return sum(data_list) / n
    else:
        return -1


def prep_reviews():
    print("load all businesses")
    businesses = pd.read_json(yelp_data + "yelp_academic_dataset_business.json", lines=True)

    print("drop irrelevant columns")
    drop_bus = list(businesses.columns)
    drop_bus.remove("business_id")
    drop_bus.remove("categories")
    drop_bus.remove("name")
    businesses = businesses.drop(drop_bus, axis=1)

    print("only retain restaurants")
    businesses = businesses[businesses.categories.apply(lambda x: "Restaurants" in x and len(x) > 1)]

    print("load all reviews")
    reviews = pd.read_json(yelp_data + "yelp_academic_dataset_review.json", lines=True)

    print("drop irrelevant columns")
    drop_rev = list(reviews.columns)
    drop_rev.remove("business_id")
    drop_rev.remove("text")
    drop_rev.remove("stars")
    reviews = reviews.drop(drop_rev, axis=1)

    print("reviews: %d" % reviews.shape[0])

    print("filter by business id")
    reviews = reviews[reviews.business_id.isin(businesses.business_id)]

    print("reviews: %d" % reviews.shape[0])

    print("collapse spaces within reviews")
    reviews.text.replace(r"\s+", " ", regex=True, inplace=True)

    print("join reviews and businesses")
    joined = pd.merge(reviews, businesses, how="left", on="business_id")

    print("drop business_id and categories")
    joined = joined.drop("business_id", axis=1)

    print("write all data to file")
    joined.to_csv(data_folder + "data.csv", line_terminator='\n')


def parse_data(filename, result_file):
    # remove_dishes = {"rice", "chicken", "cheese", "meat", "sandwich",
    #                  "steak", "beef", "shrimp", "pork", "tuna", "onion",
    #                  "salt", "bacon", "potatoes", "salsa", "garlic", "pasta", "sage",
    #                  "beans", "mushroom", "salmon", "ice cream", "lobster", "lemon",
    #                  "mushrooms", "fast food", "spinach", "lamb", "filet", "nuts",
    #                  "olive", "sweet potato", "cookie", "mashed potatoes", "truffle", "honey"}
    remove_dishes = set()

    dish_ratings = {}
    # dish_place_ratings = {}

    print("read data", flush=True)
    with open(data_folder + "dishes.txt", "r") as f:
        dishes = f.readlines()
    dishes = set([d.strip().lower() for d in dishes]) - remove_dishes
    dishes = list(dishes)

    dish_re = {}
    for d in dishes:
        dish_re[d] = re.compile(r"\b" + d + r"\b")

    data = pd.read_csv(filename)
    n_reviews = data.shape[0]

    print("parse data", flush=True)
    # iterate over reviews, populate dictionaries
    for i in range(0, n_reviews):
        if i % 1000 == 0:
            print("\tOn review " + str(i) + " of " + str(n_reviews), flush=True)

        review = data.iloc[i]
        text = review.text.lower()
        # place = review.place_name
        rating = review.stars

        # check if any dishes are in the review
        contains_dishes = []
        for dish in dishes:
            if dish not in text:
                continue

            match = dish_re[dish].search(text)

            if match is not None:
                contains_dishes.append(dish)

        for dish in contains_dishes:
            # add to overall dish ratings
            if dish in dish_ratings:
                dish_ratings[dish].append(rating)
            else:
                dish_ratings[dish] = [rating]

            # add to dish ratings by places
            # if dish in dish_place_ratings:
            #     if place in dish_place_ratings[dish]:
            #         dish_place_ratings[dish][place].append(rating)
            #     else:
            #         dish_place_ratings[dish][place] = [rating]
            # else:
            #     dish_place_ratings[dish] = {place: [rating]}

    dish_ratings_list = []
    # dish_place_ratings_list = []

    print("calculate popularity and ratings", flush=True)
    # determine popularity by number of reviews talking about the dish
    # and rating by average of stars on those reviews
    for dish in dish_ratings.keys():
        rating = dish_ratings[dish]
        popularity = len(rating)
        rating = average(rating)

        dish_ratings_list.append((dish, popularity, rating))

    # determine popularity by number of places that refer to the dish
    # and rating by average of all averages of place reviews
    # for dish in dish_place_ratings.keys():
    #     places = dish_place_ratings[dish]
    #     popularity = len(places.keys())
    #     place_ratings = []
    #
    #     if popularity < 1:
    #         rating = -1
    #     else:
    #         for place in places:
    #             place_data = dish_place_ratings[dish][place]
    #             place_ratings.append(average(place_data))
    #         rating = average(place_ratings)
    #
    #     dish_place_ratings_list.append((dish, popularity, rating))

    print("sort by popularity", flush=True)
    dish_ratings_list.sort(key=lambda tup: tup[1], reverse=True)
    # dish_place_ratings_list.sort(key=lambda tup: tup[1], reverse=True)

    print("write to files", flush=True)
    with open(result_file + "_by_reviews.csv", "w", encoding="utf-8") as f:
        f.write("name,popularity,rating\n")
        for d in dish_ratings_list:
            f.write("{},{},{}\n".format(*d))

    # with open(result_file + "_by_places.csv", "w", encoding="utf-8") as f:
    #     f.write("name,popularity,rating\n")
    #     for d in dish_place_ratings_list:
    #         f.write("{},{},{}\n".format(*d))


# def recommend_places(filename, result_file):
#     dishes = ["burrito"]
#     filename_plus = "_".join(dishes)
#
#     place_ratings = {}
#
#     dish_re = {}
#     for d in dishes:
#         dish_re[d] = re.compile(r"\b" + d + r"\b")
#
#     print("read data", flush=True)
#     data = pd.read_csv(filename)
#     n_reviews = data.shape[0]
#
#     print("parse data", flush=True)
#     # iterate over reviews, populate dictionaries
#     for i in range(0, n_reviews):
#         if i % 1000 == 0:
#             print("\tOn review " + str(i) + " of " + str(n_reviews), flush=True)
#
#         review = data.iloc[i]
#         text = review.text.lower()
#         place = review.place_name
#         rating = review.stars
#
#         # check if any dishes are in the review
#         contains_dishes = []
#         for dish in dishes:
#             if dish not in text:
#                 continue
#
#             match = dish_re[dish].search(text)
#
#             if match is not None:
#                 contains_dishes.append(dish)
#
#         dishes_mentioned = len(contains_dishes)
#
#         if dishes_mentioned > 0:
#             # add to overall dish ratings
#             if place in place_ratings:
#                 place_ratings[place] += [rating] * dishes_mentioned
#             else:
#                 place_ratings[place] = [rating] * dishes_mentioned
#
#     place_ratings_list = []
#
#     print("calculate popularity and ratings", flush=True)
#     # determine popularity by number of reviews talking about the dishes
#     # and rating by average of stars on those reviews
#     for place in place_ratings.keys():
#         rating = place_ratings[place]
#         popularity = len(rating)
#         rating = average(rating)
#
#         place_ratings_list.append((place, popularity, rating))
#
#     print("sort by popularity", flush=True)
#     place_ratings_list.sort(key=lambda tup: tup[1], reverse=True)
#
#     print("write to files", flush=True)
#     with open(result_file + filename_plus + ".csv", "w", encoding="utf-8") as f:
#         f.write("name,popularity,rating\n")
#         for d in place_ratings_list:
#             f.write("{},{},{}\n".format(*d))


def mine_links_for_vis(cuisine_file, dish_file, review_data_file, result_file):
    results = {}

    print("read data", flush=True)
    # only collect data for these cuisines
    cuisines = pd.read_csv(cuisine_file)
    cuisines = list(cuisines.name)

    for c in cuisines:
        results[c] = {}

    # only collect data for top n dishes
    n_dishes = 100
    top_n_per_cuisine = 15

    dishes = pd.read_csv(dish_file)
    dishes = list(dishes.name)
    dishes = dishes[0:n_dishes]

    dish_re = {}
    for d in dishes:
        dish_re[d] = re.compile(r"\b" + d + r"\b")

    data = pd.read_csv(review_data_file)
    n_reviews = data.shape[0]

    print("parse data", flush=True)
    # iterate over reviews, populate dictionary
    for i in range(0, n_reviews):
        if i % 1000 == 0:
            print("\tOn review " + str(i) + " of " + str(n_reviews), flush=True)

        review = data.iloc[i]
        text = review.text.lower()
        categories = eval(review.categories, {'__builtins__': None}, {})

        categories = [c for c in categories if c in cuisines]
        if len(categories) == 0:
            continue

        # check if any dishes are in the review
        for dish in dishes:
            if dish not in text:
                continue

            match = dish_re[dish].search(text)

            if match is not None:
                for c in categories:
                    if dish in results[c]:
                        results[c][dish] += 1
                    else:
                        results[c][dish] = 1

    for c in results.keys():
        dishes = results[c]

        sorted_dishes = sorted(dishes.items(), key=operator.itemgetter(1), reverse=True)
        sorted_dishes = sorted_dishes[0:top_n_per_cuisine]
        sorted_dishes = [p[0] for p in sorted_dishes]

        results[c] = sorted_dishes

    with open(result_file, "w") as f:
        f.write("cuisine,dishes\n")
        for k in results.keys():
            v = list(results[k])

            if len(v) < 1:
                continue

            f.write('{},"{}"\n'.format(k, str(v)))


if __name__ == "__main__":
    cuisine_file = data_folder + "cuisines.csv"
    dish_file = data_folder + "dish_popularity_by_reviews.csv"
    review_data_file = data_folder + "data.csv"
    result_file = data_folder + "links.csv"

    # prep_reviews()
    # parse_data(data_folder + "data.csv", data_folder + "dish_popularity")
    mine_links_for_vis(cuisine_file, dish_file, review_data_file, result_file)
