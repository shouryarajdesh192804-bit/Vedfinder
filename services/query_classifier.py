LOCATION_WORDS = {

    "india",
    "usa",
    "america",
    "canada",
    "japan",
    "china",
    "france",
    "germany",
    "italy",
    "uk",
    "england",
    "london",
    "paris",
    "tokyo",
    "mumbai",
    "delhi",
    "airport",
    "station",
    "hotel",
    "museum",
    "restaurant",
    "hospital",
    "college",
    "school",
    "temple",
    "mosque",
    "church",
    "mall",
    "park",
    "beach",
    "lake",
    "river",
    "mountain"
}


def is_location_query(query):

    q = query.lower()

    for word in LOCATION_WORDS:

        if word in q:

            return True

    return False