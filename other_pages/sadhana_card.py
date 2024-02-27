import streamlit as st
import pandas as pd
import json
from datetime import datetime
from datetime import timedelta
from other_pages.googleapi import download_data,upload_data
from other_pages.sadhana_card_helper import daily_filling, evaluate_weekly_summary

class sadhana_card_class:
    def __init__(self):
        self.page_config = {'page_title': "Sadhana Card",
                    'page_icon':'📈',
                    'layout':'centered'}
        self.page_dict = {
            'filling':self.filling,
            'dashboard':self.dashboard,
        }
        self.current_page = 'filling'
        self.userinfo = st.session_state['bdv_app'].userinfo
        self.username = self.userinfo['name']
        
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
            devotee_name = self.username
            if devotee_name not in mscdict['name2col'].keys():
                # add name to sadhana card
                def add_new_name():
                    insertrange = f"{self._db_sheet_name}!{mscdict['new_name_append_range']}"
                    upload_data(self.dbi,insertrange,devotee_name)
                    upload_data(self.dbi,f"{self._db_sheet_name}!{mscdict['new_name_col_update']}",
                                int(mscdict['data_col_last_column'])+1)
                    st.snow()
                st.header("You do not have a sadhana card yet!!")
                st.button("create one for me",on_click=add_new_name)
                return None
                
            
            # get my sadhana card
            myscdf = scdbdf[['row_number','week_id',self.username]].copy()

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
            
            # get the two standards
            lt3hraw = download_data(self.dbi,"standards!C2:E")
            lt3hdf = pd.DataFrame(lt3hraw[1:],columns=lt3hraw[0])
            lt3hdf.query("name !='' ",inplace=True)
            lt3hdf.fillna(-1,inplace=True)
            lt3hdict = {}
            for _,item in lt3hdf.query("name not in ['japa_time','to_bed','wake_up','day_rest']").iterrows():
                lt3hdict[item['name']] = {'value':int(item['value']),
                                          'mark':int(item['mark'])}
            
            self._scstandard = {'qnadict':qnadict,
                                'sc_fast':{'df':lt3hdf,
                                           'dict':lt3hdict}
                                }
            self._scstandard_refresh = False
            return self._scstandard
        else:
            return self._scstandard
    
    def filling(self):
        def switch():
            self.current_page='dashboard'
        st.button("Go To Dashboard",on_click=switch)
        
        scdatabase = self.scdb
        if not scdatabase:
            # this will happend when devotee do not have name added in the sadhana card
            # name addition page will be handled by self.scdb
            # therefore don't show anything further
            return
        
        # retrieve all the data from scdatabase
        scmetadata = scdatabase['meta']
        
        # get the current week's details
        current_week_scdata = scdatabase['mysc'].query(f"`week_id` == '{scmetadata['current_week']}' ").to_dict(orient='list')
        active_row = current_week_scdata['row_number'][0]
        active_column = scmetadata['name2col'][self.username]
        active_range = f"{self._db_sheet_name}!{active_column}{active_row}"
        
        # Get the sadhana card standards
        scstandards = self.scstandard
        qna = scstandards['qnadict']
        # st.write(metadata)
        # st.write(current_week_scdata)
        # st.write(qna)
        # st.write()
        # st.divider()
        st.header(f"For :green[{scmetadata['current_week']}]")

        if current_week_scdata[self.username][0]=="":
            # create the schema for data
            weekdatabase = {'data':{},'summary':{}}
            weekdata = weekdatabase['data']
        else:
            weekdatabase = json.loads(current_week_scdata[self.username][0])
            weekdata = weekdatabase['data']
        
        weekstart = datetime(int(scmetadata['current_year']),
                             int(scmetadata['current_month']),
                             int(scmetadata['current_monday']))
        weekdays = [weekstart + timedelta(days=i) for i in range(7)]
        
        # drop future days
        aajkadin = datetime.today()
        availabledays = [day for day in weekdays if day <= aajkadin]
        
        # get date which have been filled
        def fillformatfunc(x):
            if x.strftime("%b %d %a") in weekdata.keys():
                return f":green[{x.strftime('%b %d %a')}--already filled]"
            else:
                return f':red[{x.strftime("%b %d %a")}]'
            
        fillingdate = st.radio("Filling For",
                               availabledays,
                               format_func=fillformatfunc,
                               index=len(availabledays)-1).strftime("%b %d %a")

        st.markdown(f"### Filling for :violet[{fillingdate}]")
        if fillingdate in weekdata.keys():
            st.warning("You have already filled for this date")
            st.markdown("## :red[filling again will overwrite the previous data]")
        incomplete,dailydata = daily_filling(qna,show_help_text=False)
        if incomplete:
            st.button("Submit",type='primary',disabled=True,help="some required filleds are blank")
        else:
            def dailyscreport(weekdata,data_2_upload,filldate,range_name):
                # in the base case weekdata will be {}
                # final structure would be {"data":{weekdata},"scores":reportdata}
                weekdata[filldate] = data_2_upload
                weekdatabase['data'] = weekdata
                weekdatabase['summary'] = evaluate_weekly_summary(weekdata)
                
                jsonifieddf = json.dumps(weekdatabase)
                upload_data(self.dbi,range_name,[[jsonifieddf]])
                st.balloons()

            st.button("Submit",on_click=dailyscreport, args=[weekdata,dailydata,fillingdate,active_range])
    
    def dashboard(self):        
        scdb = self.scdb
        scmetadata = scdb['meta']
        scdata = scdb['allsc']
        mysc = scdb['mysc']
        
        viwing_week = scmetadata['current_week']
        mysc_this_week = scdb['mysc'].query(f"`week_id` == '{viwing_week}' ").to_dict(orient='list')
        if mysc_this_week[self.username][0]=="":
            # create the schema for data
            st.error("You have not filled for any day")
            return
        else:
            weekdatabase = json.loads(mysc_this_week[self.username][0])
            weekdata = weekdatabase['data']
            weeksummary = weekdatabase['summary']
        
        st.header(f"For :green[{viwing_week}]")
        _mysc,_mygroup,_allsc=st.tabs(["My Sadhana Scores",'Group',"All"])
        
        with _mysc:
            weekdf = pd.DataFrame.from_dict(weekdata, orient="index").reset_index()
            st.dataframe(weekdf)
            st.divider()
            left,middle,right = st.columns(3)
            with left:
                st.metric("Body", f"{weeksummary['summary']['body']['achieved']:.2%}")
            with right:
                st.metric("Soul", f"{weeksummary['summary']['soul']['achieved']:.2%}")
            with middle:
                st.metric("Total", f"{weeksummary['summary']['total']['achieved']:.2%}")
            st.divider()
            for i in ['reading','hearing']:
                st.markdown(f"### {i.title()}: {weeksummary['summary'][i]['achieved']} minutes ---total: {weeksummary['summary'][i]['target']} minutes")

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