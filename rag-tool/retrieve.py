import requests

# Accepts any url link which points to a raw data (*.md/text files etc.)
# example: https://raw.githubusercontent.com/knative/func/main/docs/function-templates/python.md
def get_raw_content(url: str) -> str:
    """ retrieve contents of github raw url as a text """
    response = requests.get(url)
    response.raise_for_status() # errors if bad response
    return response.text
