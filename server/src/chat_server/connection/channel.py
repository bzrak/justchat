from pydantic import BaseModel


# NOTE: Should this be a BaseModel instead of just a normal class ?
# What if I need to add some methods here ?
class Channel(BaseModel):
    id: int
    name: str

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(str(self))
