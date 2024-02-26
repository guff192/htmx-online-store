from pydantic import BaseModel


class Banner(BaseModel):
    name: str
    description: str
    img_url: str

    def is_valid(self) -> bool:
        return self.name != '' and self.description != ''

    def build_context(self) -> dict:
        return {
            'name': self.name,
            'description': self.description,
            'img_url': self.img_url,
        }

