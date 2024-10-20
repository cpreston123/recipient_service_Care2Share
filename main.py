from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*']
)

@app.get("/")
async def root():
    return {"\n\nmessage": "Hello from recipient_service_Care2Share!\n\n"}


@app.get("/hello/{name}")
async def hello(name: str):
    msg = f"Hello {name} from recipient_service_Care2Share!"
    return {"\n\nmessage": msg}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)



