import streamlit as st
import pandas as pd
import json
import datetime
# from st_aggrid import AgGrid, GridOptionsBuilder

from other_pages.googleapi import download_data
from other_pages.googleapi import upload_data

import requests
from streamlit.components.v1 import html as HTML

class hearing_Class:
    def __init__(self) -> None:
        
        self.page_config = {'page_title': "BDV",
                            'page_icon':'☔',
                            'layout':'centered'}
        self.page_map = {
            'SP':self.srila_prabhupada_page,
            }
        self.current_page = 'SP'
        # databases
        # for Prabhupada
        self._morning_walk_db = None
        self._morning_walk_db_refresh = True
        self._morning_walk_db_range = "SP-morning-walk!A2:J341"

    @property
    def morning_walk_db(self):
        if self._morning_walk_db_refresh:

            temp = download_data(5,self._morning_walk_db_range)
            temp = pd.DataFrame(temp[1:],columns=temp[0])
            for column in ['year','month','day',]:
                temp[column] = pd.to_numeric(temp[column],errors='coerce')
            
            self._morning_walk_db = temp.copy()
            self._morning_walk_db_refresh=False
            return self._morning_walk_db
        
        else :
            return self._morning_walk_db

    
    @property
    def bdvapp(self):
        return st.session_state.get('bdv_app',None)


    def srila_prabhupada_page(self):
        st.title("Srila Prabhupada Vaani")
        section = st.radio("Choose",
                           options=['Morning Walks'],
                            horizontal=True,
                            label_visibility='hidden',
                            format_func=lambda x: f":green[{x}]")
        
        if section == 'Morning Walks':
            st.header(":blue[Morning Walks]")
            
            data = self.morning_walk_db
            query_list = []

            filteryear = st.select_slider("Year",
                                         options=['all',*sorted(data.year.unique())]
                                         )
            if filteryear!='all':
                data=data.query(f"year == {filteryear}")

            filters = st.columns([1,1])

            filtermonth = filters[0].selectbox("Month",
                                               options=data['month-english'].unique())
            
            if filtermonth:
                data = data.query(f" `month-english` == '{filtermonth}' ")
            
            filterplace = filters[1].selectbox("Place",
                                                options=sorted(data.place.unique()),
                                                )
            if filterplace:
                data = data.query(f" place == '{filterplace}' ")
            
            st.caption(f"Total {len(data)} records found")
            data.insert(0,"Choose",False)

            idf = st.data_editor(data,hide_index=True,
                                 column_order=['Choose','place','date','title'])

            idf=idf.query("Choose == True").reset_index(drop=True)
            
            if len(idf)>0:
                
                def freeze_status(status,timestamp,sheetrow):
                    targetrange = f"SP-morning-walk!J{sheetrow}"
                    data = download_data(5,targetrange)
                    if data:
                        data = json.loads(data[0][0])
                    else:
                        data={}
                    data[self.bdvapp.userinfo['name']] = {'status':status,
                                                            'timestamp':timestamp,
                                                            'last_modified':datetime.datetime.now().strftime("%y-%b-%d-%a-%H:%M")}
                    upload_data(5,
                                targetrange,
                                [[json.dumps(data)]])

                    self._morning_walk_db_refresh=True

                for row in range(len(idf)):
                    if st.checkbox(idf.loc[row,'title']):
                        st.audio(data = idf.loc[row,'URL'])
                        left,middle,right = st.columns(3)
                        status = left.radio("Status",
                                          options=[':red[in progress]',
                                                   ':green[completed]'],
                                          key='statusradio'+str(row))
                        with right:
                            st.markdown("")
                            st.markdown("")

                        if status ==':red[in progress]':
                            timestamp = middle.text_input("Timestamp",
                                              key=f"timeinput{row}")
                            if not timestamp:
                                right.button("Freeze",disabled=True,
                                             help='Must fill timestamp',
                                             key=f"submit button {row}")
                            else:
                                right.button("Freeze",
                                         on_click=freeze_status,
                                         args=['iprogress',timestamp,idf.loc[row,'sheetrow']],
                                         key=f"submit button {row}")
                        else:
                            middle.success("Jai Ho!!")
                            value = download_data(5,f"SP-morning-walk!J9")
                            right.button("Freeze Status",
                                      on_click=freeze_status,
                                      args=['done','full',idf.loc[row,'sheetrow']],
                                      key=f"submit button {row}")
                        
                    st.divider()
                                



        else:
            st.snow()
            st.title("In progress...")
        

    def run(self):
        st.markdown(
        """
        <style>
        .step-up,
        .step-down {
            display: none;
        }
        </style>
        </style>
        """,
        unsafe_allow_html=True
        )
        self.page_map[self.current_page]()

# --------------- 