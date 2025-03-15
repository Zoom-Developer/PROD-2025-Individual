from config import config


def image_id2url(image_id: str) -> str:
    return config.api_url + "/files/" + image_id