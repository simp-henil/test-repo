import uvicorn
from fastapi import FastAPI

from models.database_engine import init_db
from routes.routes import router

app = FastAPI()

app.include_router(router=router)



if __name__ == "__main__":
    init_db()
    uvicorn.run("main:app", reload=True)
