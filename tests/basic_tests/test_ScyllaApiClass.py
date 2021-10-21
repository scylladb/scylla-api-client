from scylla_cli import ScyllaApi


def test_create_default_scyllaapi():
    scyllaapi = ScyllaApi()

    assert scyllaapi.node_address == "localhost"
    assert scyllaapi.port == 10000


def test_create_custom_scyllaapi():
    scyllaapi = ScyllaApi(node_address="1.1.1.1", port=20000)
    assert scyllaapi.node_address == "1.1.1.1"
    assert scyllaapi.port == 20000
