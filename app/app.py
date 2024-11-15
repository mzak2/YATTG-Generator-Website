import random
import warnings
warnings.simplefilter(action='ignore', category=DeprecationWarning)
import pandas as pd
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from database.menu import MainMenu
from database.table import getEnumDF
from database.string_templates import townEventString, magicItemString, potionsString, civilizationString, \
    wildernessString, characterString, blessingOrCurseString, setbackString, criticalString, bookString, \
    divinationString, dungeonRmTypeString, shopString

# Initialize FastAPI
app = FastAPI()

# create directories for index.html and css stylesheet
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static",)

# ------------Start Program
db_url = os.environ.get('DB_URL')  # connects to the docker version for deployment
#db_url = os.environ.get('db_url') # used for local testing, use other for docker
engine = create_engine(f"{db_url}")
Session = sessionmaker(bind=engine)


def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()


@app.get("/")
async def index(request: Request):
    session = Session()
    menu = MainMenu(session)
    session.close()
    return templates.TemplateResponse("index.html", {"request": request, "menu": menu})


@app.post("/roll")
async def roll(request: Request):
    data = await request.json()
    category_id = data.get("category_id")
    session = Session()

    try:
        result_df = getEnumDF(session, category_id)

        if category_id == 4:
            result_str = townEventString(result_df)
        elif category_id == 13:
            result_str = setbackString(result_df)
        elif category_id == 19:
            result_str = dungeonRmTypeString(result_df)
        elif category_id == 22:
            result_str = shopString(result_df)
        elif category_id == 25:
            result_str = divinationString(result_df)
        elif category_id == 26:
            result_str = criticalString(result_df)
        elif category_id == 28:
            result_str = bookString(result_df)
        elif category_id == 29:
            result_str = magicItemString(result_df)
        elif category_id == 30:
            result_str = potionsString(result_df)
        elif category_id == 23 or category_id == 24:
            result_str = blessingOrCurseString(result_df)
        elif category_id > 0 and category_id < 6 or category_id == 9:
            result_str = civilizationString(result_df)
        elif category_id >= 6 and category_id < 15 and category_id != 9 and category_id != 13:
            result_str = wildernessString(result_df)
        elif 15 <= category_id <= 22 and category_id != 18 and category_id != 19:
            result_str = characterString(result_df)
        else:
            result_str = result_df.iloc[0, 1] if not result_df.empty else "No result available."

        result_html = result_df.to_html(classes="table table-bordered")

        return JSONResponse({"result_string": result_str, "result_df": result_html})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
