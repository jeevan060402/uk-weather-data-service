import os
from pathlib import Path

ENABLE_DOCS = True if os.environ.get("ENABLE_DOCS", "False") == "True" else False


#############################
#   PROJECT ROOT DIR        #
#############################
BASE_DIR = Path(__file__).resolve().parent.parent


TAGS = [
    {"name": "Dropdowns", "description": "Endpoint for data to populate dropdown fields"},
    {
        "name": "Dynamic Dropdowns",
        "description": "Endpoints for data to populate dropdown fields that is derived from created data",
    },
    {"name": "Organisations", "description": "Endpoints for Organisations"},
    {"name": "Partners", "description": "Endpoints for Partners"},
    {"name": "Products", "description": "Endpoints for Products"},
    {"name": "Serial Number Architect", "description": ""},
    {"name": "Warehouse Inbound Receipts", "description": ""},
    {"name": "Warehouse Country Clearance Declarations", "description": ""},
    {"name": "Warehouse Outbound Receipts", "description": ""},
    {"name": "Warehouse Container Reconciliation", "description": ""},
    {"name": "Working Reports", "description": ""},
    {"name": "Reports Vault", "description": ""},
    {"name": "HIVE", "description": ""},
    {"name": "Invitation Management", "description": ""},
    {"name": "Network Management", "description": ""},
    {"name": "Integration Management", "description": ""},
    {"name": "JWT User", "description": "Endpoints used for interacting with the Users' data"},
    {"name": "Token Auth", "description": ""},
    {"name": "Token User", "description": ""},
    {"name": "JWT Auth", "description": "Endpoints used for authentication"},
    {"name": "Login Policy", "description": ""},
    {"name": "Role", "description": ""},
    {"name": "NotificationSettings", "description": ""},
    {"name": "NotificationMessage", "description": ""},
]


# Getting absolute path of the readme file and read the content
README_ABSOLUTE_PATH = os.path.join(BASE_DIR, "common", "api_docs_readme.md")
with open(README_ABSOLUTE_PATH) as file:
    README_CONTENT = file.read()

table_of_contents = """
# Table of Contents
- [Introduction](#introduction)
- [API Endpoints](#api-endpoints)
"""


for tag in TAGS:
    table_of_contents += f"\n  - [{tag['name']}](#{tag['name'].lower().replace(' ', '-')})"


# Concatenate all sections
README_CONTENT_WITH_TOC = README_CONTENT.replace("# Table of Contents", table_of_contents)


SPECTACULAR_SETTINGS = {
    "PREPROCESSING_HOOKS": ["common.schema_generator.custom_preprocessing_hook"],
    "DESCRIPTION": README_CONTENT_WITH_TOC,
    "TITLE": "AltiusHub Backend",
    "TAGS": TAGS,
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS": {
        "defaultModelsExpandDepth": -1,
    },
}
