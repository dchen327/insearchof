from fastapi import FastAPI

app = FastAPI()


@app.get("/api/helloworld")
def healthchecker():
    return {"message": "Hello World"}
