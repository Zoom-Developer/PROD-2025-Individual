from pydantic import BaseModel


class Advertiser(BaseModel):
    advertiser_id: str
    name: str

class FindAdvertisers(BaseModel):
    total_pages: int
    current_page: int
    advertisers: list[Advertiser]