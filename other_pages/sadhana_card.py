import streamlit as st
import pandas as pd
import json
from datetime import datetime
from datetime import timedelta
from other_pages.googleapi import download_data,upload_data
from other_pages.sadhana_card_helper import daily_filling

class sadhana_card_class:
    def __init__(self):
        self.page_config = {'page_title': "Sadhana Card",
                    'page_icon':'📈',
                    'layout':'centered'}
        self.page_dict = {
            'filling':self.filling
        }
        self.current_page = 'filling'
        
        # sadhana card meta data
        self.dbi = 2
        self._mdbrange = "database!A:B"
        self._db_sheet_name = "database"
        # scdb
        self._scdb_refresh = True
        self._scdb = None

        # get sadhana card standards etc
        self._scstandard_refresh = True
        self._scstandard = None
        self._filling_format_range = "meta!E:J"
    @property
    def bdv(self):
        return st.session_state['bdv_app']
    
    @property
    def scdb(self):
        if self._scdb_refresh:
            
            # get the metadata
            mscraw = download_data(self.dbi,self._mdbrange)
            mscdf = pd.DataFrame(mscraw[1:],columns=mscraw[0])
            mscdf.dropna(subset='key',inplace=True)
            mscdf.query("key != ''",inplace=True)
            mscdict = dict(zip(mscdf['key'],mscdf['value']))

            # get name -> column mapping
            name2colraw = download_data(self.dbi,"meta!A:B")
            name2coldf = pd.DataFrame(name2colraw[1:],columns=name2colraw[0])
            name2coldict = dict(zip(name2coldf['name'],name2coldf['column']))
            mscdict['name2col'] = name2coldict
            # st.write(mscdict)

            # get the sadhana card data
            scdbraw = download_data(self.dbi,f"{self._db_sheet_name}!{mscdict['data_col_range']}")
            scdbdf = pd.DataFrame(scdbraw[1:],columns=scdbraw[0])
            # st.dataframe(scdbdf)
            devotee_name = self.bdv.userinfo['name']
            if devotee_name not in mscdict['name2col'].keys():
                self.add_name_in_sc()
            
            # get my sadhana card
            myscdf = scdbdf[['row_number','week_id',self.bdv.userinfo['name']]].copy()

            # final db
            scdb = {'meta':mscdict,
                    "allsc":scdbdf,
                    "mysc":myscdf}
            self._scdb = scdb
            self._scdb_refresh = False
            return self._scdb
        else:
            return self._scdb

    @property
    def scstandard(self):
        if self._scstandard_refresh:

            # get questions for daily filling
            qnaraw = download_data(self.dbi,self._filling_format_range)
            qnadf = pd.DataFrame(qnaraw[1:],columns=qnaraw[0])
            qnadict = {}
            for index,row in qnadf.iterrows():
                qnadict[row['key']] = {"title":row['title'],
                                       'type':row['type'],
                                       'helptext':row['help_message'],
                                       'min':row['min'],
                                       'max':row['max']}

            self._scstandard = {'qnadict':qnadict}
            self._scstandard_refresh = False
            return self._scstandard
        else:
            return self._scstandard
    def filling(self):
        
        scdata = self.scdb
        metadata = scdata['meta']
        current_week_scdata = scdata['mysc'].query(f"`week_id` == '{metadata['current_week']}' ").to_dict(orient='list')
        
        scstandards = self.scstandard
        qna = scstandards['qnadict']

        active_row = current_week_scdata['row_number'][0]
        active_column = metadata['name2col'][self.bdv.userinfo['name']]
        active_range = f"{self._db_sheet_name}!{active_column}{active_row}"
        st.write(metadata)
        st.write(current_week_scdata)
        st.write(qna)
        st.write()
        st.divider()
        st.header(f"For :green[{metadata['current_week']}]")

        if current_week_scdata[self.bdv.userinfo['name']][0]=="":
            weekdata = {}
        else:
            weekdata = json.loads(current_week_scdata[self.bdv.userinfo['name']][0])
        
        weekstart = datetime(int(metadata['current_year']),
                             int(metadata['current_month']),
                             int(metadata['current_monday']))
        weekdays = [weekstart + timedelta(days=i) for i in range(7)]
        # drop future days
        aajkadin = datetime(2024,2,29)
        availabledays = [day for day in weekdays if day <= aajkadin]
        # get date which have been filled
        def fillformatfunc(x):
            if x.strftime("%b %d %a") in weekdata.keys():
                return f":green[{x.strftime('%b %d %a')}--already filled]"
            else:
                return f':red[{x.strftime("%b %d %a")}]'
        fillingdate = st.radio("Filling For",availabledays,format_func=fillformatfunc,index=len(availabledays)-1)
        fillingdate = fillingdate.strftime("%b %d %a")
        st.markdown(f"#### Filling for :violet[{fillingdate}]")
        if fillingdate in weekdata.keys():
            st.warning("You have already filled for this date")
            st.markdown(":red[filling again will overwrite the previous data]")
        incomplete,dailydata = daily_filling(qna,show_help_text=False)
        if incomplete:
            st.button("Submit",disabled=True)
        else:
            def dailyscreport(weekdata,data_2_upload,filldate,range_name):
                weekdata[filldate] = data_2_upload
                jsonifieddf = json.dumps(weekdata)
                upload_data(self.dbi,range_name,[[jsonifieddf]])

            st.button("Submit",on_click=dailyscreport, args=[weekdata,dailydata,fillingdate,active_range])







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
        self.page_dict[self.current_page]()