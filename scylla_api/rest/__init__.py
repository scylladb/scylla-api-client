from typing import Optional

import requests
from logging import getLogger

from requests import Response
from requests.exceptions import ConnectionError

logger = getLogger(__name__)


class RestClient(object):
    def __init__(self,
                 host: str,
                 port: str,
                 ssl: bool = False,
                 endpoint: str = ""):
        """
        Create a Rest client instance for making http/s requests.
        :param ssl: should the client work in SSL mode or not
        """
        self.__url_prefix = "https://" if ssl else "http://"
        self.__host = host
        self.__port = port
        self.__endpoint = endpoint

    @property
    def url_prefix(self):
        return self.__url_prefix

    @property
    def host(self):
        return self.__host

    @property
    def port(self):
        return self.__port

    @property
    def endpoint(self):
        return self.__endpoint

    @endpoint.setter
    def endpoint(self, value):
        self.__endpoint = value

    def get(self, resource_path: str, query_params: dict = None) -> Optional[Response]:
        """
        Sends a GET method request to the host resource specified
        by the resource path. Returns a Response type response and throws
        a ConnectionError in case of problems.
        :param resource_path: string with the path to the resource
        :param query_params: dict with params to add to the GET request
        :return: request response
        :rtype: Response
        """
        # construct request headers
        headers = {"Host": self.host,
                   "Content-Type": "application/json"}

        # add additional headers if needed
        logger.debug(f"Using headers: {headers}")

        # construct url string
        url = self.__construct_url(resource_path)

        logger.debug(f"Attempting a GET request for: {url}")
        try:
            return requests.get(url=url, params=query_params, headers=headers)
        except ConnectionError as details:
            logger.error(f"Connection error: {details}")
            return None

    def post(self, resource_path: str, query_params: dict = None, json: dict = None) -> Response:
        """
        Sends a POST method request to the host resource specified
        by the resource path. Returns a Response type response and throws
        a ConnectionError in case of problems.
        :param resource_path: string with the path to the resource
        :param query_params: dict with params to add to the GET request
        :param json: dict object to add as the POST methods json
        :return: request response
        :rtype: Response
        """
        # construct request headers
        headers = {"Host": self.host,
                   "Content-Type": "application/json"}

        # add additional headers if needed
        logger.debug(f"Using headers: {headers}")

        # construct url string
        url = self.__construct_url(resource_path)

        logger.debug(f"Attempting a POST request for: {url}")
        return requests.post(url=url, params=query_params, headers=headers, json=json)

    def delete(self, resource_path: str, query_params: dict = None) -> Response:
        """
        Sends a DELETE method request to the host resource specified
        by the resource path. Returns a Response type response and throws
        a ConnectionError in case of problems.
        :param resource_path: string with the path to the resource
        :param query_params: dict with params to add to the GET request
        :return: request response
        :rtype: Response
        """
        # construct request headers
        headers = {"Host": self.host,
                   "Content-Type": "application/json"}

        # add additional headers if needed
        logger.debug(f"Using headers: {headers}")

        # construct url string
        url = self.__construct_url(resource_path)

        logger.debug(f"Attempting a DELETE request for: {url}")
        return requests.delete(url=url, params=query_params, headers=headers)

    def __construct_url(self, resource_path: str) -> str:
        return f"{self.__url_prefix}{self.__host}:{self.port}{self.__endpoint}{resource_path}"
