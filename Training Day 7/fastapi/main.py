from fastapi import FastAPI, Path, Query
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str
    description: str  = Field(None, title="The description of the item", max_length=300)
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    tax: float = None
        
app = FastAPI()

@app.get("/")
def hello():
    return {"Hello": "World"}

@app.post("/")
def post_body(item: Item):
    return item

@app.delete("/{item_id}")
def delete_method(item_id: int = Path(..., title="The ID of the item to remove"), price: int = Query):
    item = {"item_id": item_id, "price": price}
    return item

if __name__ == "__main__":
    # for local testing in case that fastapi cli not working
    import os
    os.system("uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
