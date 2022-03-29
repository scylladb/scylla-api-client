# Scylla-API-Client
Scylla API Client is a command line utility implementing a thin client directly utilizing the Scylla REST API


## Requirements
* python > 3.8
* requests
* pytest (developers)

## Installation
```
pip install scylla-api-client
```

## Usage

See `scylla-api-client --help` for all options, below are some sample uses:

* Show all API modules
    ```
    $ scylla-api-client --list-modules
    system
    compaction_manager
    gossiper
    endpoint_snitch_info
    storage_proxy
    column_family
    stream_manager
    messaging_service
    storage_service
    cache_service
    failure_detector
    hinted_handoff
    lsa
    commitlog
    collectd
    error_injection
    ```

* Show all API commands for specific module _system_
    ```
    $ scylla-api-client --list-module-commands system
    system/logger:
    GET: Get all logger names
    POST: Set all logger level
    system/drop_sstable_caches:
    POST: Drop in-memory caches for data which is in sstables
    system/uptime_ms:
    GET: Get system uptime, in milliseconds
    system/logger/{name}:
    GET: Get logger level
    POST: Set logger level
    ```

* Get loglevel for specific logger _httpd_
    ```
    $ scylla-api-client system/logger/{name} GET --name httpd
    "info"
    ```

* Set loglevel _level=debug_ for specific logger _httpd_
    ```
    $ scylla-api-client system/logger/{name} POST --name httpd --level debug
    ```


## Tests
pytest is used for writing and executing tests
to run tests you can execute:
```
pip install -r dev-requirements.txt 
pytest -s -v tests/
```


## Design
![](https://raw.githubusercontent.com/scylladb/scylla-api-client/master/scylla-cli-design.png)


## Release
Releases are published automatically by GitHub Actions when a tag (v**) is pushed to GitHub.
- Make sure you tag the correct commit
- Pushing a tag to GitHub requires maintainers/admin privileges

```commandline
git tag v1.0 <some-commit-hash>
git push upstream v1.0
```