import requests
import pandas as pd
import streamlit as st

def fetch_thingspeak_data(channel_id, read_api_key, results=50):
    """
    Fetches the latest data from a ThingSpeak channel.
    """
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={read_api_key}&results={results}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        feeds = data.get('feeds', [])
        if not feeds:
            return pd.DataFrame()
        
        df = pd.DataFrame(feeds)
        
        # Rename fields for clarity (Map based on your ThingSpeak configuration)
        # Field 1: BPM, Field 2: Room_Temperature, Field 3: Humidity, Field 4: Gesture_Code
        # Field 5: Accel_X, Field 6: Accel_Y, Field 7: Accel_Z, Field 8: Gyro_Magnitude
        column_mapping = {
            'field1': 'BPM',
            'field2': 'Room_Temperature',
            'field3': 'Humidity',
            'field4': 'Gesture_Code',
            'field5': 'Accel_X',
            'field6': 'Accel_Y',
            'field7': 'Accel_Z',
            'field8': 'Gyro_Magnitude',
            'created_at': 'Timestamp'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Convert timestamp to datetime
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # Convert numeric columns
        numeric_cols = ['BPM', 'Room_Temperature', 'Humidity', 'Gesture_Code', 
                        'Accel_X', 'Accel_Y', 'Accel_Z', 'Gyro_Magnitude']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
        
    except Exception as e:
        st.error(f"Error fetching data from ThingSpeak: {e}")
        return pd.DataFrame()

def get_latest_reading(df):
    """
    Returns the most recent reading from the dataframe.
    """
    if df.empty:
        return None
    return df.iloc[-1]
