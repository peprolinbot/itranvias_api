import requests
import random
from datetime import datetime
import logging


class QueryItrResponse:
    """
    A class representing a response from `/queryitr_v3.php`
    """

    def __init__(self, response: requests.Response, full_data: dict = None):
        self.response: requests.Response = response
        """
        The `requests.Response` object of the request
        """

        try:
            self.full_data: dict = full_data or response.json()
            """
            The full JSON response from the API as a dictionary
            """
        except (
            requests.exceptions.JSONDecodeError
        ):  # When we hit rate limit for example
            self.full_data = {}

        # The following attributes are set by self.parse()

        self.result: str = None
        """
        Usually `OK` or `ERROR`
        """
        self.request_date: datetime = None
        """
        The date (server-side) at which the petition was received
        """

        self.internal_endpoint: str = None
        """
        The (internal?) endpoint to which the request was sent
        """

        self.size: int = None
        """
        The size of the response (in bytes)
        """

        self.origin: str = None
        """
        Where the request originated from, this usually says some version of the official web of iTranvias, e.g `Web_Beta`
        """

        self.data: dict = {}
        """
        Remaining JSON data that has not been parsed into other attributes
        """

        self.parse()

    def parse(self):
        if self.full_data == {}:
            return

        # We copy the dict so we don't modify the original
        data = self.full_data

        self.result = data.pop("resultado")
        self.request_date = datetime.strptime(
            data.pop("fecha_peticion"), "%Y%m%d%H%M%S"
        )
        self.internal_endpoint = data.pop("peticion")
        self.size = data.pop("tama\u00f1o")
        self.origin = data.pop("Origen")

        self.data: dict = data

    def __repr__(self) -> dict:
        return self.data


class QueryItrError(Exception):
    """
    Exception used for succesful connections to the server but that for some reason didn't work
    """

    def __init__(self, response: requests.Response, full_data: dict = None):
        self.app_response: QueryItrResponse = QueryItrResponse(response, full_data)
        """
        The `QueryItrResponse` object for the failed request
        """

        self.id: int = self.app_response.data.pop("id_error", None)
        """
        The error id given by the app
        """

        self.message: str = self.app_response.data.pop("error", None)
        """
        The error message given by the app
        """

        super().__init__(
            f"HTTP --> {self.app_response.response.status_code}: {self.app_response.response.reason} || App --> {self.id or "?"}: {self.message or "?"}"
        )


class QueryItrAdapter:
    """
    A class used to simplify calls to `/queryitr_v3.php`
    """

    def __init__(
        self, url: str, logger: logging.Logger = None, bypass_rate_limit: bool = False
    ):
        self.url: str = url
        """
        Url where `/queryitr_v3.php` is, e.g. `https://itranvias.com/queryitr_v3.php`. The known ones are in known_servers.py
        """

        self._logger: logging.Logger = logger or logging.getLogger(__name__)
        """
        If your app has a logger, pass it in here. It will try to automatically get it when possible
        """

        self.bypass_rate_limit: bool = bypass_rate_limit
        """
        Wether this adapter should bypass the API's rate limit or not. This works because, as found & already reported by [@delthia](https://github.com/delthia/bus-coruna-api),
        the server accepts the `X-Forwarded-For` header from anyone, not just the porxy.
        This is disabled by default. Not that it can also be temporarily enabled when calling `QueryItrAdapter.get`
        """

    def get(
        self,
        func: int,
        dato=None,
        **extra_params,
    ) -> QueryItrResponse:
        """
        Actually calls `/queryitr_v3.php`

        :param func: The number of the function to call the endpoint with. `0` is for example the stop info
        :param dato: The main parameter of a function, any other **extra parameters can be passed as keyword arguments**
        :param bypass_rate_limit: Wether to temporarily enable the rate limit bypass
        """

        if self.bypass_rate_limit:
            # The server accepts this header from anyone, not just the proxy (found & already reported by @delthia)
            headers = {"X-Forwarded-For": self._random_private_ip()}
        else:
            headers = {}

        ep_params = {"func": func, "dato": dato} | extra_params

        def _escape_dict(data: dict) -> str:
            return str(data).replace("{", "{{").replace("}", "}}")

        # Log line to show before doing the request
        log_line_pre = f"method=GET, url={
            self.url}, params={_escape_dict(ep_params)}"
        # Log line to show how the request went
        log_line_post = ", ".join(
            (log_line_pre, "success={}, status_code={}, message={}")
        )

        # The actual request is made here
        self._logger.debug(msg=log_line_pre)
        response = requests.request(
            method="GET", url=self.url, headers=headers, params=ep_params
        )

        is_success = 299 >= response.status_code >= 200  # 200 to 299 is OK
        log_line = log_line_post.format(
            is_success, response.status_code, response.reason
        )

        if is_success:
            self._logger.debug(msg=log_line)
            # Filter the json data by the given key
            return QueryItrResponse(response)

        self._logger.error(msg=log_line)
        raise QueryItrError(response)

    def _random_private_ip(self) -> str:
        """
        Generates a random IPv4 address in one of these ranges: 10.0.0.0/8, 172.16.0.0/12 or 192.168.0.0/16
        """

        # First octet
        x1 = random.choice([10, 172, 192])

        if x1 == 172:
            # Second octet for 172.x.x.x
            x2 = random.randint(16, 31)
        else:
            # Second octet for 10.x.x.x and 192.x.x.x
            x2 = random.randint(0, 255)

        # Third octet
        x3 = random.randint(0, 255)
        # Fourth octet
        x4 = random.randint(0, 255)

        # Get all the octets into a string
        return ".".join(map(str, [x1, x2, x3, x4]))
