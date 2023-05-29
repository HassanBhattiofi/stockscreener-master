import yfinance as yf

from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Stock
from pydantic import BaseModel

app = FastAPI()

templates = Jinja2Templates(directory="templates")


class StockRequest(BaseModel):
    symbol: str


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/")
def home(request: Request, forward_pe=None, dividend_yield=None, ma50=None, ma200=None, db: Session = Depends(get_db)):
    stocks = db.query(Stock)

    if forward_pe:
        stocks = stocks.filter(Stock.forward_pe < forward_pe)

    if dividend_yield:
        stocks = stocks.filter(Stock.dividend_yield > dividend_yield)

    if ma50:
        stocks = stocks.filter(Stock.price > Stock.ma50)

    if ma200:
        stocks = stocks.filter(Stock.price > Stock.ma200)

    stocks = stocks.all()

    return templates.TemplateResponse("home.html", {
        "request": request,
        "stocks": stocks,
        "dividend_yield": dividend_yield,
        "forward_pe": forward_pe,
        "ma200": ma200,
        "ma50": ma50
    })


def fetch_stock_data(id: int):
    db = SessionLocal()
    stock = db.query(Stock).filter(Stock.id == id).first()
    yahoo_data = yf.Ticker(stock.symbol).info

    stock.ma200 = yahoo_data.get('twoHundredDayAverage', None)
    stock.ma50 = yahoo_data.get('fiftyDayAverage', None)
    stock.price = yahoo_data.get('regularMarketPrice', None)
    stock.forward_pe = yahoo_data.get('forwardPE', None)
    stock.forward_eps = yahoo_data.get('forwardEps', None)
    stock.dividend_yield = yahoo_data.get('dividendYield', None) * 100 if yahoo_data.get('dividendYield', None) else None

    db.add(stock)
    db.commit()


@app.post("/stock")
async def create_stock(stock_request: StockRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    stock = Stock(symbol=stock_request.symbol)
    db.add(stock)
    db.commit()

    background_tasks.add_task(fetch_stock_data, stock.id)

    return {
        "code": "success",
        "message": "Stock was added to the database."
    }
