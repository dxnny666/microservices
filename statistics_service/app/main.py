import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status

from database import database as database

app = FastAPI()
database.Base.metadata.create_all(bind=database.engine)

@app.get("")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))