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


def add_ttr_tags_to_articles(articles):
    count = 0

    for article_id, article in articles.items():
        try:
            # time_to_read = article["time_to_read"]

            # add_tag_to_article(article_id, time_to_read)
            count += 1
        except KeyError:
            pass

    print(count)


def main():
    # Authorization

    consumer_key = os.getenv("CONSUMER_KEY")

    request_token = get_request_token(consumer_key, "https://www.google.com/")
    auth_redirect_url = "https://www.google.com/"

    authorization_url = f'https://getpocket.com/auth/authorize?request_token={request_token}&redirect_uri={auth_redirect_url}'

    print("Please visit the following URL to give authorization to this app", authorization_url, sep="\n")

    input("Press Enter to continue...")

    access_token_and_username = get_access_token_and_username(consumer_key, request_token)
    access_token = access_token_and_username["access_token"]
    username = access_token_and_username["username"]

    print(f"Authorization successful for user {username}")

    # Get the user's articles

    articles = get_user_pocket_articles(consumer_key, access_token)
    # print(articles)

    # Add a tag to them with their time to read

    add_ttr_tags_to_articles(articles)

    return 0


if __name__ == "__main__":
    main()
