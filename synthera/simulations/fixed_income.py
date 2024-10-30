import io
import requests
import json
import pandas as pd


def simulation_past_date(api_key, request={}):
    headers = {'accept': 'application/vnd.apache.parquet', 'API_KEY': '123'}
    r = requests.post('http://127.0.0.1:8080/v1/simulation/past-date', headers=headers, json=request)
    print(f"API response code: {r.status_code}")
    response = json.loads(r.content)

    parquet_files = response.get('parquet_files')

    df_collection = {}
    for simulation_item in parquet_files:
        df = pd.read_parquet(io.BytesIO(eval(simulation_item.get('file'))))
        df_collection.update({simulation_item.get('label') : df})
    meta_data = response.get('simulation_meta_data', {})
    print(meta_data)
    return df_collection
