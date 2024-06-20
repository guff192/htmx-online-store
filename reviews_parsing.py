# coding: utf-8
from typing import NamedTuple
import requests
from bs4 import BeautifulSoup


BUSINESS_ID = 119376854596


class CommentData(NamedTuple):
    name: str
    date: str
    stars_count: int
    text: str


def get_yandex_reviews(business_id):
    url = f"https://yandex.ru/maps-reviews-widget/{business_id}?comments"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    comments = soup.find_all("div", {"class": "comment"})

    comment_dicts = []
    for comment in comments:
        # parsing
        comment_text = comment.find("p", {"class": "comment__text"}).text
        comment_name = comment.find("p", {"class": "comment__name"}).text
        comment_date = comment.find("p", {"class": "comment__date"}).text
        comment_stars_count = len(comment.find_all(
            "li", {"class": "stars-list__star"}))

        # creating comment dicts
        comment_dicts.append(
            CommentData(
                name=comment_name,
                date=comment_date,
                stars_count=comment_stars_count,
                text=comment_text,
            )
        )

    return comment_dicts


if __name__ == "__main__":
    print(get_yandex_reviews(BUSINESS_ID))

