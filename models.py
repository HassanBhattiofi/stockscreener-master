from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Stock(Base):
    __tablename__ = 'stocks'

    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    price = Column(Float)
    forward_pe = Column(Float)
    forward_eps = Column(Float)
    dividend_yield = Column(Float)
    ma50 = Column(Float)
    ma200 = Column(Float)
