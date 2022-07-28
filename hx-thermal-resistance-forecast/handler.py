import datetime
from datetime import timedelta
from math import log

from cognite.client.data_classes import TimeSeries
from prophet import Prophet


def thermal_resistance(x):
    """Function to calculate Thermal Resistance"""
    # Some constants like Correction factor, Area and Cp values
    F = 0.8
    A = 1.0
    Cp_hot = 2.4
    # Calculate the cross temperature differences
    x["dT1"] = x["T_hot_IN"] - x["T_cold_OUT"]
    x["dT2"] = x["T_hot_OUT"] - x["T_cold_IN"]
    # Calculate the numerator and denominator for the thermal resistance calculation
    temp1 = A * F * (x["dT1"] - x["dT2"]) / log(x["dT1"] / x["dT2"])
    temp2 = x["Flow_hot"] * Cp_hot * (x["T_hot_IN"] - x["T_hot_OUT"])
    tr = temp1 / temp2
    return tr


def thermal_resistance_forecast(df):
    """Function to forecast the Thermal Resistance"""
    df2 = df.copy()[["TR"]].reset_index()
    df2 = df2.rename(columns={"index": "ds", "TR": "y"})
    m = Prophet()
    m.fit(df2)
    future = m.make_future_dataframe(periods=24 * 15, freq="H")
    future["cap"] = 1.1 * df["TR"].mean()  #
    fcst = m.predict(future)
    fcst_df = fcst[["ds", "yhat"]].set_index("ds")
    fcst_df.columns = ["TR"]
    return fcst_df


def create_and_save_time_series_data(client, data, ts_external_id):
    """Function to create the time series and save the data"""
    asset_id = 7640884189698369  # 23-HA-9114 Asset
    cdf_ts = client.time_series.retrieve(external_id=ts_external_id)
    if cdf_ts is None:
        ts = TimeSeries(
            external_id=ts_external_id,
            name=ts_external_id,
            asset_id=asset_id,
            unit="m2K/W",
        )
        client.time_series.create(ts)
        print("Created time series")
    else:
        print("Existing Time Series")
    dps = []
    for index, r in data.iterrows():
        dps = dps + [{"timestamp": r.name, "value": r["TR"]}]
    try:
        client.datapoints.insert(datapoints=dps, external_id=ts_external_id)
    except BaseException as e:
        print(str(e))


def handle(client, data=None, secrets=None, function_call_info=None):
    """Handler Function to be Run/Deployed
    Args:
        client : Cognite Client (not needed, it's availble to it, when deployed)
        data : data needed by function
        secrets : Any secrets it needs
        function_call_info : any other information about function

    Returns:
        response : response or result from the function
    """
    ts_exids = [
        "pi:163657",
        "pi:163658",
        "pi:160887",
        "pi:191092",
        "pi:163374",
        "pi:160184",
    ]
    column_names = [
        "T_cold_IN",
        "T_cold_OUT",
        "T_hot_IN",
        "T_hot_OUT",
        "Flow_cold",
        "Flow_hot",
    ]
    # Retrieve the data
    start_date = datetime.datetime(2018, 8, 1)
    end_date = start_date + timedelta(days=30)
    df = client.datapoints.retrieve_dataframe(
        external_id=ts_exids,
        aggregates=["average"],
        granularity="1h",
        start=start_date,
        end=end_date,
        include_aggregate_name=False,
    )
    df.fillna(method="ffill", inplace=True)
    df.columns = column_names
    # Calculate the Thermal resistance
    df["TR"] = df.apply(lambda x: thermal_resistance(x), axis=1)
    # Forecast the Thermal resistance
    fcst_df = thermal_resistance_forecast(df)
    # Save the Results as time series
    create_and_save_time_series_data(client, df[["TR"]], "hx_thermal_resistance")
    create_and_save_time_series_data(
        client, fcst_df[["TR"]], "hx_thermal_resistance_forecast"
    )
    # Return the result as json
    result = df[["TR"]].to_json()
    return result
