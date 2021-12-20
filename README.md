# Simple Web Crawler
This is a simple web crawler application, built in python.

## Installation
It is recommended that for all installation mechanisms to use a virtual environment. You can create and activate a virtual environment using the following:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Poetry
If you use poetry for package management, simply perform the following from the repositry root to install and setup the required packages:
```bash
poetry env use .venv/bin/python # Only if you don't have poetry handle environs
poetry install
```

#### Pip
If you are not using poetry for installation, you can use pip to install
the requirements with the following:
```bash
pip install -r requiments.txt
```

## Quick Start
The service is available as a script, that can be called from the command line.
```bash
python app.py \
    -url https://martinfowler.com/architecture \
    --depth 2 \
    --output sitemap.json
```

In the above example, we crawl `https://martinfowler.com/architecture` with a
maximum depth set to 2 (i.e. we won't follow more than two links in a single
path) and we will push the output to `output.json`.

#### Arguments:
 - `-url`: The url that is to be crawled.
 - `--depth` (*Optional*): The maximum allowed depth to traverse. Default functionality is to not limit the depth.
 - `--output` (*Optional*): The output location, relative to where the script is called from. The default output location is `./outputs/sitemap.json`.