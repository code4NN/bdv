from __future__ import print_function

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import streamlit as st
import pandas as pd
creds = Credentials.from_authorized_user_info(st.secrets['refresh_token'])

@st.cache()
def fetch_data(spreadsheet_id,ranges):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """    
    if creds.expired and creds.refresh_token:
            creds.refresh(Request())
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        result = service.spreadsheets().values() \
        .get(spreadsheetId=spreadsheet_id, range=ranges,).execute()

        values = result.get('values', [])
        return values
        # return pd.DataFrame(values[1:],columns=values[0])
    except HttpError as err:
        st.write(err)