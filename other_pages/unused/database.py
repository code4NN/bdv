import streamlit as st


class database_gsheet:

    def __init__(self,spreadsheet_id,sheetname,range):
        """
        * spreadsheet_id is id for sheets as defined in googleapi.py
        * sheetname is name of the sheet in the spreadsheet
        * range Range in A1 Notation
        """
        