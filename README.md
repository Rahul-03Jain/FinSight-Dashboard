# FinSight - Portfolio & Investment Risk Analytics Dashboard

FinSight is a production-style Flask dashboard for tracking stock portfolios, evaluating risk exposure, and monitoring investment goals. It combines practical financial analytics with modern UI design for a clean, portfolio-ready project.

## Features

- Portfolio KPI dashboard (total value, invested amount, profit/loss, daily gain/loss)
- Stock analytics cards with current pricing, return metrics, and trend charts
- Smart risk score system (1-10) based on diversification, concentration, and volatility
- Investment goal tracker with progress percentage and remaining amount
- Buy/Sell transaction workflow with validation and filterable history
- Allocation analytics (sector, stock, and P/L contribution visualizations)
- Dark mode toggle and responsive sidebar layout
- Auto database creation and seeded sample portfolio data

## Tech Stack

- Frontend: HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js
- Backend: Python, Flask
- Database: SQLite with SQLAlchemy ORM
- Analytics/Data: pandas, numpy, yfinance, matplotlib, plotly

## Project Structure

```text
project/
├── app.py
├── requirements.txt
├── README.md
├── database.db
├── templates/
├── static/
├── models/
├── routes/
├── services/
└── utils/
```

## Installation

1. Clone or download the project.
2. Open terminal and move into the project directory:
   - `cd project`
3. Create virtual environment:
   - Windows: `python -m venv venv`
   - Activate: `venv\Scripts\activate`
4. Install dependencies:
   - `pip install -r requirements.txt`

## Run Locally

1. Ensure your virtual environment is active.
2. Start the Flask app:
   - `python app.py`
3. Open browser:
   - `http://127.0.0.1:5000`

The app automatically creates and seeds `database.db` if it does not exist.

## Screenshots

Add screenshots here after running locally:

- Dashboard overview
- Portfolio holdings page
- Analytics page
- Goals tracker
- Transactions page

## Future Improvements

- User authentication and multi-user portfolio support
- CSV import/export for transactions
- Real-time websocket market updates
- Enhanced benchmark comparison and drawdown analytics
- Notification system for risk spikes and goal milestones
