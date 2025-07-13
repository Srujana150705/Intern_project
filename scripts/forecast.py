# forecast.py

from prophet import Prophet
import pandas as pd

def forecast_price(df, district, commodity):
    data = df[(df['District'] == district) & (df['Commodity'] == commodity)]
    data = data.groupby('Arrival_Date')['Modal_Price'].mean().reset_index()
    data.columns = ['ds', 'y']

    if len(data) < 2:
        return None, f"Not enough data points to forecast {commodity} in {district}."
    
    model = Prophet()
    model.fit(data)

    future = model.make_future_dataframe(periods=8, freq='W')
    forecast = model.predict(future)

    return forecast[['ds', 'yhat']], None
