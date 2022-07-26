import datetime
from datetime import timedelta
from math import log


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
    TR = temp1 / temp2
    return TR


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
    end_date = start_date + timedelta(days=10)
    df = client.datapoints.retrieve_dataframe(
        external_id=ts_exids,
        aggregates=["average"],
        granularity="6h",
        start=start_date,
        end=end_date,
        include_aggregate_name=False,
    )
    df.fillna(method="ffill", inplace=True)
    df.columns = column_names
    # Calculate the Thermal resistance
    df["TR"] = df.apply(lambda x: thermal_resistance(x), axis=1)
    # Return the result as json
    result = df[["TR"]].to_json()
    return result
