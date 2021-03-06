# The AMIGOS III operations system and command line interface

[![Build Status](https://travis-ci.com/wallinb/amigos3.svg?branch=master)](https://travis-ci.com/wallinb/amigos3)
[![codecov](https://codecov.io/gh/wallinb/amigos3/branch/master/graph/badge.svg)](https://codecov.io/gh/wallinb/amigos3)

## Development

### Getting started

Dependencies in the development environment are managed with [Conda](https://docs.conda.io/en/latest/index.html).

1. Initialize submodules (run in repository root directory)

    ```
    $ git submodule init && git submodule update
    ```

1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anoconda](https://www.anaconda.com/distribution/)

1. Create the environment (run in repository root directory)

    ```
    $ conda env create -f environment.yml
    ```

    This will create a 'amigos' environment with the correct version of python and dependencies for the project.

1. Activate the environment

    ```
    $ conda activate amigos-test-env
    ```

1. Install amigos CLI commands (local to source directory)

    ```
    $ python setup.py develop
    ```

### Running tests

Due to poor support for Python 2.6, tests are run in a separate Python 2.7 environment. Easy way:

```
make test
```
