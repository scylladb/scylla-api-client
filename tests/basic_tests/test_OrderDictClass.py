from scylla_api_client.api import OrderedDict



def test_OrderdDict_empty():
    d = OrderedDict()
    assert not d


def test_OrderDict_insert():
    d = OrderedDict()
    d.insert("k", "v")

    assert d["k"] == "v"
    assert d[0] == "v"


def test_OrderDict_serveral_elements():
    d = OrderedDict()
    for i in range(10):
        d.insert(f"k{i}", f"v{i}")

    assert len(d) == 10
    for i in range(10):
        assert d[f"k{i}"] == f"v{i}"


def test_OrderedDict_random_element():
    d = OrderedDict()
    for i in range(10):
        d.insert(f"k{i}", f"v{i}")

    assert d[f"k6"] == f"v6"
    assert d[6] == f"v6"


def test_OrderedDict_keys():
    d = OrderedDict()
    d.insert("key1", "value1")
    d.insert("key2", "value2")
    d.insert("key3", "value3")

    all_keys = ["key1", "key2", "key3"]

    assert list(d.keys()) == all_keys


def test_interator():
    d = OrderedDict()
    for i in range(5):
        d.insert(f"k{i}", f"v{i}")
    it = iter(d)
    for i, key in enumerate(it):
        assert key == f"k{i}"
        assert d[key] == f"v{i}"
