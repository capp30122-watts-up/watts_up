'''
Run the app or the getdata script, depending on the input provided
- To run the dashboard, type "python -m lie_brary dashboard"
- To run update data, type "python -m lie_brary getdata"

# Author: Jacob Trout
'''


from watts_up.data_processing import get_data
from watts_up import app

def run_getdata():
    '''Run the getdata script'''
    get_data.run_etl()

def run_dash():
    '''Run the dash app
    for local testing: debug=True'''
    app.app.run_server()


def main():
    '''Run the app or the getdata script, depending on the input provided'''
    run_getdata()
    run_dash()