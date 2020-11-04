import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()


def get_request_token(consumer_key, redirect_uri):
    response = requests.get(
        "https://getpocket.com/v3/oauth/request", params={"consumer_key": consumer_key, "redirect_uri": redirect_uri}
    )

    return response.text.lstrip("code=")


def get_access_token_and_username(consumer_key, request_token):
    response = requests.get(
        "https://getpocket.com/v3/oauth/authorize", params={"consumer_key": consumer_key, "code": request_token}
    )

    parsed_response = response.text.lstrip("access_token=").split("&username=")

    return {"access_token": parsed_response[0], "username": parsed_response[1]}


def get_user_pocket_articles(consumer_key, access_token):
    response = requests.get(
        "https://getpocket.com/v3/get",
        params={"consumer_key": consumer_key, "access_token": access_token}
    )

    response_as_json = json.loads(response.text)

    return response_as_json["list"]


def sort_articles_by_time_to_read(articles):
    a_with_ttr = {}

    for article_id, article in articles.items():
        try:
            time_to_read = article["time_to_read"]
            item_id = article["item_id"]

            a_with_ttr[item_id] = time_to_read
        except KeyError:
            pass

    a_with_ttr = {k: v for k, v in sorted(a_with_ttr.items(), key=lambda item: item[1])}
    return a_with_ttr


def export_to_csv(articles, file_name):
    try:
        os.remove(f"{file_name}.csv")
    except FileNotFoundError:
        pass

    with open(f"{file_name}.csv", "w") as file:
        file.write("Item ID, Time to read, Link")
        file.write("\n")

        for item_id, ttr in articles.items():
            open_article_url = f"https://app.getpocket.com/read/{item_id}"

            file.write(f"{item_id},{ttr},{open_article_url}")
            file.write("\n")


def main():
    # Authorization

    consumer_key = os.getenv("CONSUMER_KEY")

    request_token = get_request_token(consumer_key, "https://www.google.com/")
    auth_redirect_url = "https://www.google.com/"

    authorization_url = f"https://getpocket.com/auth/authorize?request_token={request_token}&redirect_uri={auth_redirect_url}"

    print("Please visit the following URL to give authorization to this app:", authorization_url)

    input("Press Enter to continue...")

    access_token_and_username = get_access_token_and_username(consumer_key, request_token)
    access_token = access_token_and_username["access_token"]
    username = access_token_and_username["username"]

    print(f"Authorization successful for user {username}")

    # Get the user"s articles

    articles = get_user_pocket_articles(consumer_key, access_token)
    # print(articles)

    # Sort articles by "time to read" (and discard articles that don"t include this)

    articles = sort_articles_by_time_to_read(articles)

    # Export results to .csv file

    file_name = "pocket-obttr"

    export_to_csv(articles, file_name)

    print(f"Results exported to '{file_name}.csv' file")

    return 0


if __name__ == "__main__":
    main()
