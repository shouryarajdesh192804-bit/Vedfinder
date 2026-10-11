from urllib.parse import quote


def get_map(query):

    q = quote(query)

    return {

        "url":

        "https://www.google.com/maps/search/"

        + q,

        "embed":

        "https://www.google.com/maps?q="

        + q

        + "&output=embed"

    }