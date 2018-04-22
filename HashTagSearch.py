import sys
import bs4
import requests
import json
import hashlib
import re
import logging as log

from abc import ABCMeta, abstractmethod
from json import JSONDecodeError
from InstagramUser import InstagramUser
from InstagramPost import InstagramPost


def get_md5(s):
    m = hashlib.md5()
    m.update(s.encode())
    return m.hexdigest()


class HashTagSearch(metaclass=ABCMeta):
    instagram_root = "https://www.instagram.com"

    def __init__(self, ):
        """
        This class performs a search on Instagrams hashtag search engine, and extracts posts for that given hashtag.
        There are some limitations, as this does not extract all occurrences of the hash tag.
        Instead, it extracts the most recent uses of the tag.
        """
        super().__init__()
        self.session = requests.session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0'
        self.session.cookies.set('ig_pr', '1', domain='www.instagram.com')
        self.session.cookies.set('ig_vh', '959', domain='www.instagram.com')
        self.session.cookies.set('ig_vw', '1034', domain='www.instagram.com')
        self.session.cookies.set('ig_or', 'landscape-primary', domain='www.instagram.com')

    def extract_recent_tag(self, tag):
        """
        Extracts Instagram posts for a given hashtag
        :param tag: Hashtag to extract
        """

        url_string = "https://www.instagram.com/explore/tags/%s/" % tag
        response = bs4.BeautifulSoup(self.session.get(url_string).text, "html.parser")
        potential_query_ids = self.get_query_id(response)
        shared_data = self.extract_shared_data(response)

        media = shared_data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']

        posts = []
        for node in media:
            post = self.extract_recent_instagram_post(node['node'])
            posts.append(post)
        self.save_results(posts)

        hashtag = shared_data['entry_data']['TagPage'][0]['graphql']['hashtag']
        end_cursor = hashtag['edge_hashtag_to_media']['page_info']['end_cursor']

        # figure out valid queryId
        success = False
        for potential_id in potential_query_ids:
            variables = {
                'tag_name': tag,
                'first': 4,
                'after': end_cursor
            }
            url = "https://www.instagram.com/graphql/query/?query_hash=%s&variables=%s" % (
                potential_id, json.dumps(variables).replace(" ", ""))
            try:
                response = self.session.get(url, headers={
                    'X-Instagram-GIS': get_md5(shared_data['rhx_gis'] + ':' + json.dumps(variables).replace(" ", ""))})
                data = response.json()
                if data['status'] == 'fail':
                    # empty response, skip
                    continue
                query_id = potential_id
                success = True
                break
            except JSONDecodeError as de:
                # no valid JSON retured, most likely wrong query_id resulting in 'Oops, an error occurred.'
                pass
        if not success:
            log.error("Error extracting Query Id, exiting")
            sys.exit(1)

        while end_cursor is not None:
            variables = {
                'tag_name': tag,
                'first': 12,
                'after': end_cursor
            }
            url = "https://www.instagram.com/graphql/query/?query_hash=%s&variables=%s" % (
                query_id, json.dumps(variables).replace(" ", ""))
            try:
                response = self.session.get(url, headers={
                    'X-Instagram-GIS': get_md5(shared_data['rhx_gis'] + ':' + json.dumps(variables).replace(" ", ""))})
                data = response.json()
                if data['status'] == 'fail':
                    print("END")
                    break
            except:
                print("ERROR")
                break

            end_cursor = data['data']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
            posts = []
            for node in data['data']['hashtag']['edge_hashtag_to_media']['edges']:
                posts.append(self.extract_recent_query_instagram_post(node['node']))
            self.save_results(posts)

    @staticmethod
    def extract_shared_data(doc):
        for script_tag in doc.find_all("script"):
            if script_tag.text.startswith("window._sharedData ="):
                shared_data = re.sub("^window\._sharedData = ", "", script_tag.text)
                shared_data = re.sub(";$", "", shared_data)
                shared_data = json.loads(shared_data)
                return shared_data

    @staticmethod
    def extract_recent_instagram_post(node):
        return InstagramPost(
            post_id=node['id'],
            code=node['shortcode'],
            user=InstagramUser(user_id=node['owner']['id']),
            caption=HashTagSearch.extract_caption(node),
            display_src=node['display_url'],
            is_video=node['is_video'],
            created_at=node['taken_at_timestamp']
        )

    @staticmethod
    def extract_recent_query_instagram_post(node):
        return InstagramPost(
            post_id=node['id'],
            code=node['shortcode'],
            user=InstagramUser(user_id=node['owner']['id']),
            caption=HashTagSearch.extract_caption(node),
            display_src=node['display_url'],
            is_video=node['is_video'],
            created_at=node['taken_at_timestamp']
        )

    @staticmethod
    def extract_caption(node):
        if len(node['edge_media_to_caption']['edges']) > 0:
            return node['edge_media_to_caption']['edges'][0]['node']['text']
        else:
            return None

    @staticmethod
    def extract_owner_details(owner):
        """
        Extracts the details of a user object.
        :param owner: Instagrams JSON user object
        :return: An Instagram User object
        """
        username = None
        if "username" in owner:
            username = owner["username"]
        is_private = False
        if "is_private" in owner:
            is_private = is_private
        user = InstagramUser(owner['id'], username=username, is_private=is_private)
        return user

    def get_query_id(self, doc):
        query_ids = []
        for script in doc.find_all("script"):
            if script.has_attr("src"):
                text = requests.get("%s%s" % (self.instagram_root, script['src'])).text
                if "queryId" in text:
                    for query_id in re.findall("(?<=queryId:\")[0-9A-Za-z]+", text):
                        query_ids.append(query_id)
        return query_ids

    @abstractmethod
    def save_results(self, instagram_results):
        """
        Implement yourself to work out what to do with each extract batch of posts
        :param instagram_results: A list of Instagram Posts
        """
