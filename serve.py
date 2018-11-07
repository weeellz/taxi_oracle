from keras.models import model_from_json
import scipy
import matplotlib
import pandas as pd
import numpy as np
from sklearn.externals import joblib
from keras.models import model_from_json
import tensorflow as tf

def get_model_api():
    jsonf = str()
    with open("model.json", "r") as f:
        jsonf = f.read()
    model = model_from_json(jsonf)
    model.load_weights("model.h5")
    model._make_predict_function()
    graph = tf.get_default_graph()
    datatypes = {
    'pickup_datetime': str, 
    'pickup_longitude': np.float32, 
    'pickup_latitude': np.float32, 
    'dropoff_longitude': np.float32, 
    'dropoff_latitude': np.float32, 
    'passenger_count': np.uint8
    }

    scaler = joblib.load("scaler.save")

    def late_night (row): 
        if (row['hour'] <= 6) or (row['hour'] >= 20): 
            return 1 
        else: 
            return 0 


    def night (row): 
        if ((row['hour'] <= 20) and (row['hour'] >= 16)) and (row['weekday'] < 5): 
            return 1 
        else: 
            return 0 
    
    
    def manhattan(pickup_lat, pickup_long, dropoff_lat, dropoff_long): 
        return np.abs(dropoff_lat - pickup_lat) + np.abs(dropoff_long - pickup_long)
    
    def add_time_features(df): 
        df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'], format='%Y-%m-%d %H:%M:%S %Z') 
        df['year'] = df['pickup_datetime'].apply(lambda x: x.year) 
        df['month'] = df['pickup_datetime'].apply(lambda x: x.month) 
        df['day'] = df['pickup_datetime'].apply(lambda x: x.day) 
        df['hour'] = df['pickup_datetime'].apply(lambda x: x.hour) 
        df['weekday'] = df['pickup_datetime'].apply(lambda x: x.weekday()) 
        df['pickup_datetime'] = df['pickup_datetime'].apply(lambda x: str(x)) 
        df['night'] = df.apply (lambda x: night(x), axis=1) 
        df['late_night'] = df.apply (lambda x: late_night(x), axis=1) 
        df = df.drop('pickup_datetime', axis=1) 
    
        return df 
    
    
    def add_coordinate_features(df): 
        lat1 = df['pickup_latitude'] 
        lat2 = df['dropoff_latitude'] 
        lon1 = df['pickup_longitude'] 
        lon2 = df['dropoff_longitude'] 
    
        df['latdiff'] = (lat1 - lat2) 
        df['londiff'] = (lon1 - lon2) 
    
        return df 
    
    
    def add_distances_features(df): 
        ny = (-74.0063889, 40.7141667) 
        jfk = (-73.7822222222, 40.6441666667) 
        ewr = (-74.175, 40.69) 
        lgr = (-73.87, 40.77) 
    
        lat1 = df['pickup_latitude'] 
        lat2 = df['dropoff_latitude'] 
        lon1 = df['pickup_longitude'] 
        lon2 = df['dropoff_longitude'] 
    
        df['euclidean'] = (df['latdiff'] ** 2 + df['londiff'] ** 2) ** 0.5 
        df['manhattan'] = manhattan(lat1, lon1, lat2, lon2) 
    
        df['downtown_pickup_distance'] = manhattan(ny[1], ny[0], lat1, lon1) 
        df['downtown_dropoff_distance'] = manhattan(ny[1], ny[0], lat2, lon2) 
        df['jfk_pickup_distance'] = manhattan(jfk[1], jfk[0], lat1, lon1) 
        df['jfk_dropoff_distance'] = manhattan(jfk[1], jfk[0], lat2, lon2) 
        df['ewr_pickup_distance'] = manhattan(ewr[1], ewr[0], lat1, lon1) 
        df['ewr_dropoff_distance'] = manhattan(ewr[1], ewr[0], lat2, lon2) 
        df['lgr_pickup_distance'] = manhattan(lgr[1], lgr[0], lat1, lon1) 
        df['lgr_dropoff_distance'] = manhattan(lgr[1], lgr[0], lat2, lon2) 
    
        return df
    
    def read(pickup_datetime, pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, passenger_count):
    
        df = pd.DataFrame(
            columns=[ "pickup_datetime",
                      "pickup_longitude",
                      "pickup_latitude",
                      "dropoff_longitude",
                      "dropoff_latitude", 
                      "passenger_count"], 
            data=[[
                      pickup_datetime, 
                      pickup_longitude, 
                      pickup_latitude, 
                      dropoff_longitude, 
                      dropoff_latitude, 
                      passenger_count]])
        
        for k,v in datatypes.items():
            if k in df.columns:
                df[k] = df[k].apply(lambda x: v(x))
        
        df = add_time_features(df)
        df = add_coordinate_features(df)
        df = add_distances_features(df)
        df = df.drop(["pickup_longitude","pickup_latitude","dropoff_longitude","dropoff_latitude","passenger_count"], axis=1)
        df = scaler.transform(df)
        return df

    def model_api(args):
        print(args)
        data = read(args["pickup_datetime"], args["pickup_longitude"], args["pickup_latitude"], args["dropoff_longitude"], args["dropoff_latitude"], args["passenger_count"])
        with graph.as_default():
        	return model.predict(data, batch_size = 128, verbose = 1)[0][0]

    return model_api

#kek = read("2015-01-27 13:08:24 UTC", -73.973320, 40.763805, -73.981430, 40.743835, 1)