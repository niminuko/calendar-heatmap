import requests
import datetime
import pandas as pd

TOKEN = '6532d6454b8aa370768e63d6ba5a832e' # Public Key

def time_to_date(col: pd.core.series.Series) -> pd.core.series.Series:
    '''
    Given a pandas Series (specifically pandas.core.series.Series) in 
    integer time format, transform into MM/DD/YYYY-HH:MM:SS format.
    '''
    temp = []
    for idx in range(len(col)):
        temp.append(datetime.datetime.fromtimestamp(col[idx]).strftime('%m/%d/%Y-%H:%M:%S'))
    return temp

def generate_month(icao: str, start_date: str, end_date: str) -> pd.DataFrame:
    '''
    Given an initial date and final date in %YYYY%mm%dd format,
    return a pandas DataFrame of observational weather data.
    
    Currently only returns information for Lubbock, Texas;
    however, location support may be added in the future.
    
    
    Parameters
    __________
    @ location, str: The associated ICAO code of the location of interest.
    @ start_date, str: A string object representing a datetime value (ex. \'20201201\').
    @ end_date, str: A String object representing a datetime value (ex. \'20201231\').
    '''
    
    # Placeholder
    icao_ = icao
    
    url = requests.get(f'https://api.weather.com/v1/location/{icao_}:9:US/observations/historical.json?apiKey={TOKEN}&units=e&startDate={start_date}&endDate={end_date}')
    response = url.json()
    
    # First DataFrame for formatting
    df = pd.DataFrame(response['observations'])
    df['valid_time_gmt'] = time_to_date(df['valid_time_gmt'])
    
    # Desired features
    cols_to_keep = ['obs_name', 
                'valid_time_gmt', 
                'pressure', 
                'temp', 
                'feels_like']
    
    slim_df = df[cols_to_keep]
    
    # Keep the column for indexing magic
    slim_df = slim_df.set_index(pd.DatetimeIndex(slim_df['valid_time_gmt'].values)) 

    return slim_df

def format_month(generated_month: pd.DataFrame) -> pd.DataFrame:
    
    '''
    Given some pandas DataFrame with column \'valid_time_gmt\',
    separate datetime features into separate columns to groupby
    indicator/feature extrema. 
    
    Parameters
    __________
    @ generated_month, pd.DataFrame: A pandas DataFrame created from 
                                     function_library function 
                                     ` generate_month() `.
    '''
    
    # Shorthand to reduce typing
    short = generated_month['valid_time_gmt']
    
    # Adjust datetime information
    month = []
    day = []
    year = []
    
    for idx in range(len(short)):
        month.append(short[idx].split('/')[0])
        day.append(short[idx].split('/')[1])
        year.append(short[idx].split('/')[-1].split('-')[0])
        
    copy = generated_month.copy()
    copy['month'] = month
    copy['day'] = day
    copy['year'] = year
    
    try:
        copy.drop(['valid_time_gmt'], axis = 1, inplace = True)
    except:
        pass
    
    return copy

def quick_group(df: pd.DataFrame) -> pd.core.groupby.generic.DataFrameGroupBy:
    '''
    Given a generated, formatted pandas DataFrame,
    return a groupby object which may have aggregate
    functions applied for insight and analysis.
    
    Parameters
    __________
    @ df, pd.DataFrame: A weather-data-containing pandas DataFrame.
    '''
    return df.groupby(['obs_name', 'year', 'month', 'day'])

def get_icao(state: str, city: str) -> str:
    
    '''
    Given a state and a city, return the associated
    ICAO code.
    
    Parameters
    __________
    @ state, str: Any one of the states forming the USA.
    @ city, str: A city within the given state.
    '''
    
    df = pd.read_csv('code_table.csv').drop('Unnamed: 0', axis = 1)
    df.head()
    
    state_df = df.loc[df['State'] == state.upper()]
    icao_ = state_df.loc[state_df['City'] == city.upper()]['ICAO']
    return icao_.values[0]