from pydantic import BaseModel


class Advert(BaseModel):
    ad_id: str
    ad_title: str
    ad_text: str
    ad_image_id: str | None
    advertiser_id: str
    ad_image_url: str | None