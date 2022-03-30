# Scylla-API-Client
Scylla API Client is a command line utility implementing a thin client directly utilizing the Scylla REST API

* [Installation](#Installation)
* [Usage](#Usage)
* [Tests](#Tests)
* [Design](#Design)
* [Contributing](#Contributing)
* [Release](#Release)

## Installation
```shell
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
pytest is used for writing and executing tests, to run tests you can execute:
```
pip install -r dev-requirements.txt 
pytest -s -v tests/
```


## Design
![](https://raw.githubusercontent.com/scylladb/scylla-api-client/master/scylla-cli-design.png)


## Release
Releases are automatically released via GitHub Actions when a new tag `v**` is pushed to GitHub. 

```shell
git tag v1.0 <some-commit-hash>
git push origin v1.0
```

**Note:** pushing a tag to GitHub requires maintainers/admin privileges.

## Contributing
Contributions are welcomed! please create a fork and open a pull request to submit your changes,

Contributing requires installation from source:
1. Clone scylla-api-client repository
2. Install development tools by `pip install -r dev-requirements.txt`
3. Install scylla-api-client from source by `python3 setup.py install --user`

Once installed, scylla-api-client can be used by `python3 -m scylla_api_client`

**Note:** by installing from source, the package will be installed under `$HOME/.local/bin` and depending on your OS  
may require adding this folder to you $PATH ex. `export PATH=$PATH:$HOME/.local/bin`.