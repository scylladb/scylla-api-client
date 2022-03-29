from scylla_api_client.api import ScyllaApi


def test_create_default_scyllaapi():
    scyllaapi = ScyllaApi()

    assert scyllaapi._host == "localhost"
    assert scyllaapi._port == 10000


def test_create_custom_scyllaapi():
    scyllaapi = ScyllaApi(host="1.1.1.1", port=20000)
    assert scyllaapi._host == "1.1.1.1"
    assert scyllaapi._port == 20000
