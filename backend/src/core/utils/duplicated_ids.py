from pydantic import BaseModel


def remove_duplicated_ids[T: list[BaseModel]](objects: T, id_key: str) -> T:
    return list({getattr(i, id_key): i for i in objects}.values())