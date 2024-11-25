from fastapi import FastAPI


app = FastAPI(debug = True)


from .routes import api_router

app.include_router(api_router)