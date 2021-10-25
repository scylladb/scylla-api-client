import requests
import json
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

    def get(self, resource_path: str, additional_headers: dict = None) -> Response:
        """
        Sends a GET method request to the host resource specified
        by the resource path. Returns a JSON type response and throws
        a ConnectionError in case of problems.
        :param resource_path: string with the path to the resource
        :param additional_headers: a dict of headers to add to the
        default ones
        :return: request response
        :rtype: json
        """
        # construct request headers
        headers = {"Host": self.host,
                   "Content-Type": "application/json"}

        # add additional headers if needed
        if additional_headers:
            headers.update(additional_headers)

        logger.debug(f"Using headers: {headers}")

        # construct url string
        url = f"{self.__url_prefix}{self.__host}:{self.port}{self.__endpoint}{resource_path}"

        logger.debug(f"Attempting a GET request for: {url}")
        try:
            return requests.get(url=url, params=None, headers=headers)
        except ConnectionError as details:
            logger.error(f"Connection error: {details}")
            return None
