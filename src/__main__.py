# from fastapi import FastAPI


# app = FastAPI()


# @app.get("/")
# async def root():
#     return {"message": "Hello World!"}

from .forecast import make_forecast


def main():
    json = make_forecast("mroc")
    print(json)


if __name__ == "__main__":
    main()
