from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='scylla-cli',
    version='0.0.1',    # Will be moved later to be set as part of the CI pipeline
    description='Command line tool for managing Scylla Clusters',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/scylladb/scylla-cli',
    author='ScyllaDB',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=['requests'],
    entry_points={
        'console_scripts': [
            'scylla-cli=scylla_cli.__main__:main',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/scylladb/scylla-cli/issues',
    },
)
