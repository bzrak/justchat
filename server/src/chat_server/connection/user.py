from pydantic import BaseModel


# NOTE: Should this be a BaseModel instead of just a normal class ?
# What if I need to add some methods here ?
class User(BaseModel):
    id: int | None = None
    username: str

    @property
    def is_guest(self) -> bool:
        return self.id is None

    def __eq__(self, other):
        return self.username == other.username

    def __hash__(self):
        return hash(str(self))
