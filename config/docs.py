import os
from pathlib import Path

ENABLE_DOCS = True if os.environ.get("ENABLE_DOCS", "False") == "True" else False


# #############################
# #   PROJECT ROOT DIR        #
# #############################
# BASE_DIR = Path(__file__).resolve().parent.parent


# TAGS = [
#     {"name": "Dropdowns", "description": "Endpoint for data to populate dropdown fields"},
# ]


# # Getting absolute path of the readme file and read the content
# README_ABSOLUTE_PATH = os.path.join(BASE_DIR, "common", "api_docs_readme.md")
# with open(README_ABSOLUTE_PATH) as file:
#     README_CONTENT = file.read()

# table_of_contents = """
# # Table of Contents
# - [Introduction](#introduction)
# - [API Endpoints](#api-endpoints)
# """


# for tag in TAGS:
#     table_of_contents += f"\n  - [{tag['name']}](#{tag['name'].lower().replace(' ', '-')})"


# # Concatenate all sections
# README_CONTENT_WITH_TOC = README_CONTENT.replace("# Table of Contents", table_of_contents)


# SPECTACULAR_SETTINGS = {
#     "PREPROCESSING_HOOKS": ["common.schema_generator.custom_preprocessing_hook"],
#     "DESCRIPTION": README_CONTENT_WITH_TOC,
#     "TITLE": "AltiusHub Backend",
#     "TAGS": TAGS,
#     "SERVE_INCLUDE_SCHEMA": False,
#     "SWAGGER_UI_SETTINGS": {
#         "defaultModelsExpandDepth": -1,
#     },
# }
