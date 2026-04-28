import uvicorn
from fastapi import FastAPI
import sys

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    print("Starting test uvicorn on port 8001...")
    sys.stdout.flush()
    uvicorn.run(app, host="127.0.0.1", port=8001)
