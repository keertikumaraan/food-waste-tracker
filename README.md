# Food Waste Tracker

Small food businesses (bakeries, tiffin services, sweet shops) guess how much to make each day, so they over-produce and throw food away. This app lets an owner log what was made, sold and wasted in under 30 seconds, then shows waste percentage, waste cost and profit per item.

## Tech stack
Python, FastAPI, SQLAlchemy, SQLite, plain HTML/JavaScript

## Run locally
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

Then open http://127.0.0.1:8000

## Roadmap
- Demand forecasting per item
- Multi-shop login
- Discount suggestions for leftoverss