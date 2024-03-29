from django.http import JsonResponse
from django.http import HttpResponse
from datetime import datetime, timedelta
import pandas as pd 
import requests
import json
import os
# from dotenv import load_dotenv
# load_dotenv()
# API_KEY = os.getenv('API_KEY')

def health_check(request):
    return JsonResponse({"status": "healthy"})

def get_data(ticker):
    actual_date = datetime.now().date() 
    month_ago = actual_date - timedelta(days=30)
    formatted_actual_date = actual_date.strftime('%Y-%m-%d')
    formatted_month_ago = month_ago.strftime('%Y-%m-%d')
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{formatted_month_ago}/{formatted_actual_date}?adjusted=true&sort=asc&limit=120&apiKey=ivZzORZgwRUh111oi0qOsGj4pKbiSoYG"
    response = requests.get(url)
    data = response.json()
    return pd.DataFrame(data["results"])

def get_ticker_data(request, ticker):
    try:
        data = get_data(ticker)
        if data.empty:
            return HttpResponse(json.dumps({'error': 'No data available'}), content_type='application/json', status=400)
        
        # Calculate volatility per day
        data['volatility'] = data['h'] - data['l']
        
        # Find the highest, lowest, and average volatility
        highest_volatility = round(data['volatility'].max(), 2)
        lowest_volatility = round(data['volatility'].min(), 2)
        average_volatility = round(data['volatility'].mean(), 2)
        
        # Find the highest, lowest, and average closing prices
        highest_close = round(data['c'].max(), 2)
        lowest_close = round(data['c'].min(), 2)
        average_close = round(data['c'].mean(), 2)
        
        # Convert DataFrame to dictionary
        df_dict = data.to_dict(orient='records')
        
        # Create a dictionary containing all the data
        response_data = {
            'data': df_dict,
            'highest_volatility': highest_volatility,
            'lowest_volatility': lowest_volatility,
            'average_volatility': average_volatility,
            'highest_close': highest_close,
            'lowest_close': lowest_close,
            'average_close': average_close
        }
        
        # Serialize dictionary to JSON
        json_data = json.dumps(response_data)
        
        # Return JSON data as response
        return HttpResponse(json_data, content_type='application/json')
    except Exception as e:
        return HttpResponse(json.dumps({'error': str(e)}), content_type='application/json', status=500)