from rest import RestClient


class ScyllaRestClient(RestClient):
    def __init__(self, host: str = "localhost", port: str = "10000"):
        super().__init__(host=host, port=port)

    def get_raw_api_json(self):
        return self.get("/api-doc").json()


if __name__ == "__main__":
    client = ScyllaRestClient()
    print(client.get_raw_api_json())
