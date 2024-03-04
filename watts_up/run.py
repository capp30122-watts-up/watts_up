'''
Run the app or the getdata script, depending on the input provided
- To run the dashboard, type "python -m lie_brary dashboard"
- To run update data, type "python -m lie_brary getdata"

# Author: Jacob Trout
'''
import sys
from watts_up.data_processing import get_data
from watts_up import app

def run_getdata():
    '''Run the getdata script'''
    get_data.run_etl()

def run_dash():
    '''Run the dash app
    for local testing: debug=True'''
    app.app.run_server(debug=True,port = 1230)


message = ('To run the dashboard, type "python -m watts_up dashboard" | '
            'To run update data, type "python -m watts_up getdata"')


def main():
    '''Run the app or the getdata script, depending on the input provided'''
    if len(sys.argv) > 1:
        if sys.argv[1] == 'dashboard':
            run_dash()
        elif sys.argv[1] == 'getdata':
            run_getdata()
        else:
            print("[Invalid Input Provided] " + message )
    else:
        print("[No Input Provided] " + message)