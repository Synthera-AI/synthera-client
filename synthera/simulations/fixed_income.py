import io
import json

import numpy as np
import pandas as pd
import requests


def simulation_past_date(api_key, request: dict, api_address=None) -> (dict, dict):
    """Requests simulation data using a date for defining the conditional.

    :param api_key: defines the client secret, not implemented yet
    :param request: request body, should contain no_of_days, no_of_samples, reference_date, yield_curve_names
    :param api_address: defines the address where the api is hosted, defaults to localhost
    :return: simulation_data as dict as well as meta_data from the simulation
    """
    api_address = "http://127.0.0.1:8080/v1/" if api_address is None else api_address
    headers = {"accept": "application/vnd.apache.parquet", "API_KEY": "123"}

    no_samples = request.get("request", {}).get("no_of_samples", 1)
    r = requests.post(
        f"{api_address}simulation/past-date", headers=headers, json=request
    )
    print(f"API response code: {r.status_code}")
    response = json.loads(r.content)

    api_response = None
    if r.status_code != 200:
        print(response)
        api_response = (response, r.status_code)
    else:
        parquet_files = response.get("parquet_files", {})

        simulation_data = {}
        for simulation_item in parquet_files:
            df = pd.read_parquet(io.BytesIO(eval(simulation_item.get("file"))))
            df['IDX'] = pd.to_datetime(df['IDX'], unit='s')
            df['SAMPLE'] = df['SAMPLE'].astype(int)
            simulation_data.update({simulation_item.get("label"): df})

        if len(simulation_data) > 0:
            array = np.concatenate(
                [
                    df.values.reshape(no_samples, 1, -1, df.values.shape[1])
                    for key, df in simulation_data.items()
                ],
                axis=1,
            )
            simulation_data.update({"numpy_array": array, "column_names": list(df.columns)})

        meta_data = response.get("simulation_meta_data")
        api_response = (simulation_data, meta_data), 200
    return api_response
