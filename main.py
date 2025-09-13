from fastapi import FastAPI

app = FastAPI()

app.include_router(auth_router)
app.include_router(some_other router)
