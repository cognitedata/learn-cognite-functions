from cognite.client.data_classes import TimeSeries
from math import log
import datetime
from datetime import timedelta

def thermal_resistance(x):
    '''Function to calculate Thermal Resistance'''
    # Some constants like Correction factor, Area and Cp values
    F = 0.8
    A = 1.0
    Cp_hot = 2.4
    Cp_cold	= 4.18
    # Calculate the cross temperature differences
    x['dT1'] = x['T_hot_IN'] - x['T_cold_OUT']
    x['dT2'] = x['T_hot_OUT'] - x['T_cold_IN']
    # Calculate the numerator and denominator for the thermal resistance calculation
    temp1 = A*F*(x['dT1']-x['dT2'])/log(x['dT1']/x['dT2'])
    temp2 = x['Flow_hot']*Cp_hot*(x['T_hot_IN']-x['T_hot_OUT'])
    tr = temp1/temp2
    return tr

def create_and_save_time_series_data(client,data, your_name):
    '''Function to create the time series and save the data'''
    asset_id = 7640884189698369 # 23-HA-9114 Asset
    
    ts_external_id = f"hx_thermal_resistance_{your_name}"
    cdf_ts = client.time_series.retrieve(external_id=ts_external_id)
    
    if cdf_ts is None:
        ts = TimeSeries(external_id=ts_external_id,name="Thermal Resistance", asset_id = asset_id, unit = 'm2K/W')
        client.time_series.create(ts)
        print("Created time series")
    else:
        print("Existing Time Series")
    
    dps = []
    for index, r in data.iterrows():
        dps= dps+[{"timestamp": r.name, "value": r['TR']}]
    
    print(dps)
    client.datapoints.insert(datapoints = dps,external_id = ts_external_id)
    


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
    ts_exids = ['pi:163657','pi:163658','pi:160887','pi:191092','pi:163374','pi:160184']
    column_names = ["T_cold_IN","T_cold_OUT","T_hot_IN","T_hot_OUT","Flow_cold","Flow_hot"]
    your_name = data['your_name'] # to be used for creating a unique time series external id
    # Retrieve the data
    start_date = datetime.datetime(2018, 8, 1)
    end_date = start_date + timedelta(days=30)
    df = client.datapoints.retrieve_dataframe(external_id=ts_exids,
                                                        aggregates=['average'],
                                                        granularity='6h',
                                                        start=start_date,
                                                        end=end_date,
                                                        include_aggregate_name=False
                                                        )
    df.fillna(method="ffill", inplace=True)
    df.columns = column_names
    # Calculate the Thermal resistance
    df['TR'] = df.apply(lambda x:thermal_resistance(x),axis=1)
    # Save the Result as time series
    create_and_save_time_series_data(client,df[['TR']], your_name)
    # Return the result as json
    result = df[['TR']].to_json()
    return result
