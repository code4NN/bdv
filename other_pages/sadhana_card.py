import streamlit as st
import pandas as pd
import json
from datetime import datetime
from datetime import timedelta
from other_pages.googleapi import download_data,upload_data
from other_pages.sadhana_card_helper import daily_filling, evaluate_weekly_summary
from other_pages.sadhana_card_helper import display_weekly_filling
from other_pages.sadhana_card_helper import extract_week_summary
from other_pages.sadhana_card_helper import verify_time
from urllib.parse import quote_plus

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
        
        # userdata about sadhana card
        self._userinfo_db = None
        self._userinfo_db_refresh = True


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
    def bdvuserinfo(self):
        return st.session_state['bdv_app'].userinfo
    
    @property
    def user_name(self):
        return self.bdvuserinfo['name']
    
    @property
    def scuserinfo(self):
        # get usermetadata
        mscdict = self.scdb['meta']
        if self._userinfo_db_refresh:
            rangename = f"{self._db_sheet_name}!{mscdict['name2col'][self.user_name]}1"
            userdict = download_data(self.dbi,rangename)[0][0]
            _userinfo_db = json.loads(userdict)

            # information about other devotees
            ousersraw = download_data(self.dbi,"meta!A:C")
            ousersdf = pd.DataFrame(ousersraw[1:],columns=ousersraw[0])
            # st.dataframe(ousersdf)
            ousersdf.query("name != 'summary' ",inplace=True)
            ouserdict = dict(zip(ousersdf['name'],ousersdf['userdata']))
            finaluserdict = {}
            for item,value in ouserdict.items():
                if item =='summary':
                    continue
                else:
                    data = json.loads(value)['info']['scgroup']
                    finaluserdict[item] = data
            _userinfo_db['other_users'] = finaluserdict

            self._userinfo_db = _userinfo_db
            self._userinfo_db_refresh = False
            return self._userinfo_db
        else:
            return self._userinfo_db
    
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
            
            # user creation page
            devotee_name = self.user_name
            if devotee_name not in mscdict['name2col'].keys():
                # add name to sadhana card
                def add_new_name(sc_type,sc_group):
                    nameinsertrange = f"{self._db_sheet_name}!{mscdict['new_name_append_range']}"
                    metadatainsertrange = f"{self._db_sheet_name}!{mscdict['new_name_append_metadata_range']}"
                    
                    upload_data(self.dbi,nameinsertrange,[[devotee_name]])
                    upload_data(self.dbi,f"{self._db_sheet_name}!{mscdict['new_name_col_update']}",
                                [[int(mscdict['data_col_last_column'])+1]])
                    # add the sadhana card type
                    userdatadict = {'info':{"sctype":sc_type,
                                            'scgroup':sc_group},
                                    'formatted_msg':'empty'
                                    }
                    userdatadump = json.dumps(userdatadict)
                    upload_data(self.dbi,metadatainsertrange,[[userdatadump]])
                    st.snow()
                    st.success("Successful!")
                    self._scdb_refresh = True

                st.markdown(f"## Hare Krishna :green[{devotee_name} Pr!!]")
                st.markdown(f"### You do not have a sadhana card yet!!")
                st.markdown("#### Let's create one 🏃‍♂️")
                
                sctype = st.radio("Please Choose your Sadhana Card Type",
                                  ['gt3h','le3h'],
                                  format_func=lambda x: 'Working Hour > 3hours' if x=='gt3h' else "Working Hour <= 3 hours"
                                  )
                scgroup = st.radio("Please Choose you sadhana Slot Group",
                                   ['Govind','Gopinath','Damodar'])
                st.button("create one for me",on_click=add_new_name,args=[sctype,scgroup])
                return None
                
            
            # get my sadhana card
            myscdf = scdbdf[['row_number','week_id',self.user_name]].copy()                        
                
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
                qnadict[row['key']] = {'key':row['key'],
                                        "title":row['title'],
                                       'type':row['type'],
                                       'helptext':row['help_message'],
                                       'min':row['min'],
                                       'max':row['max']}
            
            # get the standard for working less than or equal to 3 hours
            lt3hraw = download_data(self.dbi,"standards!C2:E")
            lt3hdf = pd.DataFrame(lt3hraw[1:],columns=lt3hraw[0])
            lt3hdf.query("name !='' ",inplace=True)
            lt3hdf.fillna(-1,inplace=True)
            lt3hdict = {}
            for _,item in lt3hdf\
            .query("name not in ['japa_time','to_bed','wake_up','day_rest']").iterrows():
                lt3hdict[item['name']] = {'value':int(item['value']),
                                          'mark':int(item['mark'])}
            
            # get the standard for working more than 3 hours
            gt3hraw = download_data(self.dbi,"standards!G2:I")
            gt3hdf = pd.DataFrame(gt3hraw[1:],columns=gt3hraw[0])
            gt3hdf.query("name !='' ",inplace=True)
            gt3hdf.fillna(-1,inplace=True)
            gt3hdict = {}
            for _,item in gt3hdf\
            .query("name not in ['japa_time','to_bed','wake_up','day_rest']").iterrows():
                gt3hdict[item['name']] = {'value':int(item['value']),
                                          'mark':int(item['mark'])}
            
            self._scstandard = {'qnadict':qnadict,
                                'sc_fast':{'df':lt3hdf,
                                           'dict':lt3hdict},

                                'sc_std':{'df':gt3hdf,
                                          'dict':gt3hdict}
                                }
            self._scstandard_refresh = False
            return self._scstandard
        else:
            return self._scstandard
    
    def filling(self):
        st.title(":rainbow[Sadhana Card]")
        st.header(f":rainbow[for {self.user_name} Pr]")
        scdatabase = self.scdb
        if not scdatabase:
            # this will happend when devotee do not have name added in the sadhana card
            # name addition page will be handled by self.scdb
            # therefore don't show anything further
            return
        
        def switch():
            self.current_page='dashboard'                
        st.button("Go To Dashboard",on_click=switch)
        
        # for 
        with st.expander("Information Centre",expanded=False):
            scuserinfo = self.scuserinfo
            _group,_standard = st.columns(2)
            with _group:
                st.markdown(f"### Your group is :green[{scuserinfo['info']['scgroup']}]")
            with _standard:
                sctype = scuserinfo['info']['sctype']
                sctypetext = \
                {'gt3h':'Working hours more than 3 hours',
                 'le3h':"Working hours less than or equal to 3 hours"}[sctype]
                st.markdown(f"### SC standard :green[{sctypetext}]")
                
                def change_usersctype(current_scuserinfo,current_sc):
                    newsctype = 'gt3h' if current_sc =='le3h' else 'le3h'
                    current_scuserinfo['info']['sctype'] = newsctype
                    current_scuserinfo = {'info':current_scuserinfo['info'],
                                          'formatted_msg':current_scuserinfo['formatted_msg']}
                    
                    toupload = json.dumps(current_scuserinfo)
                    mscdict = self.scdb['meta']
                    rangename = f"{self._db_sheet_name}!{mscdict['name2col'][self.user_name]}1"
                    upload_data(self.dbi,rangename,[[toupload]])
                    self._userinfo_db_refresh=True
                    st.snow()
                    

                st.button("Click To Change",on_click=change_usersctype,args=[scuserinfo,sctype])
            st.divider()
            update_formatted_msg = st.checkbox("Update Format Message",key='_chb_update_format_msg')
            if update_formatted_msg:
                _default_ = '' if scuserinfo['formatted_msg'] == 'empty' else scuserinfo['formatted_msg']
                messageinput = st.text_area("Enter your formatted message",height=800,
                                            value=_default_)
                mandatory_field = ['<japa>',"<wake>",'<tobed>','<dr>']
                mandatory_exists = [f':green[{i}]' if messageinput.__contains__(i) else f':red[{i}]' for i in mandatory_field]
                
                optional_field = ['<hear_hgrsp>','<hear_sp>','<hear_hhrnsm>']
                optional_exists = [f':green[{i}]' if messageinput.__contains__(i) else f':red[{i}]' for i in optional_field]
                
                # verify all the mandatory fields are present
                incomplete = 1
                for i in mandatory_field:
                    if not messageinput.__contains__(i):
                        incomplete = incomplete * 0
                st.markdown(f"mandatory fields {', '.join(mandatory_exists)}")
                st.markdown(f"optional fields {', '.join(optional_exists)}")

                if incomplete != 0:
                    def _update_format_message(current_scuserinfo,formatmsg):
                        new_userinfo = {'info':current_scuserinfo['info'],
                                          'formatted_msg':formatmsg}
                        
                        toupload = json.dumps(new_userinfo)
                        mscdict = self.scdb['meta']
                        rangename = f"{self._db_sheet_name}!{mscdict['name2col'][self.user_name]}1"
                        upload_data(self.dbi,rangename,[[toupload]])
                        self._userinfo_db_refresh=True
                        st.session_state['_chb_update_format_msg'] = False
                        st.snow()
                    st.button("Update",on_click=_update_format_message,args=[scuserinfo,messageinput])
                return


        scmetadata = scdatabase['meta']
        
        # for creating next week's container
        if 'y_sc_ic' in self.bdvuserinfo['roles']:
            # generate next week
            def create_next_week(metadata):
                update_date = [[metadata['next_year']],
                               [metadata['next_month']],
                               [metadata['next_monday']]]
                update_date_range = f"{self._db_sheet_name}!B2:B4"
                upcoming_week = metadata['upcoming_week']
                week_id_range = f"{self._db_sheet_name}!E{metadata['next_week_row']}"
                upload_data(self.dbi,update_date_range,update_date)
                upload_data(self.dbi,week_id_range,[[upcoming_week]])
                self._scdb_refresh = True
                st.snow()

            
            st.button(f"Create {scmetadata['upcoming_week']}",on_click=create_next_week,args=[scmetadata])
        
        # get the current week's details
        list_of_week = scdatabase['allsc']['week_id'].tolist()[-5:]
        active_weekname = st.radio("Choose the week",
                                   options=list_of_week,
                                   index=len(list_of_week)-1)
        
        active_week_scdata = scdatabase['mysc'].query(f"`week_id` == '{active_weekname}' ").to_dict(orient='list')
        active_row = active_week_scdata['row_number'][0]
        active_column = scmetadata['name2col'][self.user_name]
        active_range = f"{self._db_sheet_name}!{active_column}{active_row}"
        
        # Get the sadhana card standards
        scstandards = self.scstandard
        qna = scstandards['qnadict']
        # st.write(metadata)
        # st.write(current_week_scdata)
        # st.write(qna)
        # st.write()
        # st.divider()
        st.header(f"Week :green[{active_weekname}]")

        if active_week_scdata[self.user_name][0]=="":
            # create the schema for data
            weekdatabase = {'data':{},'summary':{}}
            weekdata = weekdatabase['data']
            weekreport = weekdatabase['summary']
        else:
            weekdatabase = json.loads(active_week_scdata[self.user_name][0])
            weekdata = weekdatabase['data']            
            weekreport = weekdatabase['summary']
            weekdf = pd.DataFrame.from_dict(weekdata, orient="index")
            display_weekly_filling(weekdf)
        
        if len(weekreport.keys())!=0:
            st.markdown(f"#### Reading: :violet[{weekreport['summary']['reading']['achieved']} min] Target: :orange[{weekreport['summary']['reading']['target']} min]")
            st.markdown(f"#### Hearing: :violet[{weekreport['summary']['hearing']['achieved']} min] Target: :orange[{weekreport['summary']['hearing']['target']} min]")
        st.divider()

        active_monday = active_weekname.split(" to ")[0]

        # weekstart = datetime(int(scmetadata['current_year']),
        #                      int(scmetadata['current_month']),
        #                      int(scmetadata['current_monday']))
        weekstart = datetime.strptime(f"{active_monday}-2024",'%b-%d-%Y')
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

        st.markdown(f"### Date :orange[{fillingdate}]")
        st.divider()
        # show reading and hearing targets
        # with st.container():

        if fillingdate in weekdata.keys():
            _format_message = scuserinfo['formatted_msg']
            if _format_message == 'empty':
                st.error("Format message is not set")
                st.caption("Please update in Information centre")
            else:
                _format_message = scuserinfo['formatted_msg']
                todays_dict = weekdata[fillingdate]
                # time waale fields
                for find,replace in {'<japa>':'japa_time',
                                     "<wake>":'wake_up',
                                     '<tobed>':'to_bed'}.items():
                    inputmsg = verify_time(todays_dict[replace])[1]
                    _format_message =  _format_message.replace(find,inputmsg)
                
                # duration waale fields
                for find,replace in {'<dr>':'day_rest',
                                     '<hear_hgrsp>':'hearing_hgrsp',
                                     '<hear_sp>':'hearing_sp',
                                     '<hear_hhrnsm>':'hearing_hhrnsm'}.items():
                    duration = todays_dict[replace]
                    _format_message = _format_message.replace(find,f'{duration} min')
                # st.markdown(_format_message)
                    prji_ka_phone = st.secrets['numbers']['hgprgp']
                st.markdown(f"[Send message](https://wa.me/91{prji_ka_phone}?text={quote_plus(_format_message)})")

            st.success("You have already filled for this date")
            st.markdown("## :red[filling again will overwrite the previous data]")
            if not st.checkbox("I know and I wish to refill"):
                return
        
        
        
        # get the sadhana card filled for the selected week and date
        left,right = st.columns(2)
        _show_help_text = left.checkbox("Show help text",value=True)
        _show_marks = right.checkbox("Show Marks",value=True)
        st.divider()
        
        _devotee_standard_database =  scstandards['sc_fast'] if scuserinfo['info']['sctype'] == 'le3h' else scstandards['sc_std']
        incomplete,dailydata = daily_filling(qna,_show_help_text,_show_marks,_devotee_standard_database)

        if incomplete:
            st.button("Submit",type='primary',disabled=True,help="some required fieleds are blank")
            st.caption("Some required fields are blank")
        else:
            def dailyscreport(weekdata,data_2_upload,filldate,range_name):
                # in the base case weekdata will be {}
                # final structure would be {"data":{weekdata},"summary":reportdata}
                weekdata[filldate] = data_2_upload
                weekdatabase['data'] = weekdata
                devotee_standard_database =  scstandards['sc_fast'] if scuserinfo['info']['sctype'] == 'le3h' else scstandards['sc_std']
                weekdatabase['summary'] = evaluate_weekly_summary(weekdata,devotee_standard_database)
                # st.write(weekdatabase)
                jsonifieddf = json.dumps(weekdatabase)
                upload_data(self.dbi,range_name,[[jsonifieddf]])
                st.balloons()
                self._scdb_refresh= True

            st.button("Submit",on_click=dailyscreport,
                      args=[weekdata,dailydata,fillingdate,active_range])
    
    def dashboard(self):
        def switch():
            self.current_page = 'filling'
        st.button("Go to Sadhana Card",on_click=switch)

        scdb = self.scdb
        # scmetadata = scdb['meta']
        scdata = scdb['allsc']
        # mysc = scdb['mysc']
        
        list_of_week = scdata['week_id'].tolist()[-5:]
        active_weekname = st.radio("Choose the week",
                                   options=list_of_week,
                                   index=len(list_of_week)-1)
        
        mysc_this_week = scdb['mysc'].query(f"`week_id` == '{active_weekname}' ").to_dict(orient='list')
        all_sc_this_week = scdata.query(f"`week_id` == '{active_weekname}' ").to_dict(orient='list')
        if mysc_this_week[self.user_name][0]=="":
            # create the schema for data
            st.error("You have not filled for any day")
            _not_filled = True
        else:
            _not_filled = False
            weekdatabase = json.loads(mysc_this_week[self.user_name][0])
            weekdata = weekdatabase['data']
            weeksummary = weekdatabase['summary']
        
        st.header(f"For :green[{active_weekname}]")
        _mysc,_mygroup,_allsc,_standards =st.tabs(["My Sadhana Scores",'Group',"All", "Standards"])
        
        with _mysc:
            if _not_filled :
                st.markdown("No Data Available")
            else:
                weekdf = pd.DataFrame.from_dict(weekdata, orient="index")
                display_weekly_filling(weekdf)

                st.divider()
                left,middle,right = st.columns(3)
                with left:
                    st.metric("Body", f"{weeksummary['summary']['body']['achieved']:.2%}")
                with right:
                    st.metric("Soul", f"{weeksummary['summary']['soul']['achieved']:.2%}")
                with middle:
                    st.metric("Total", f"{weeksummary['summary']['total']['achieved']:.2%}")
                st.divider()
                
                bodytab, soultab = st.tabs(['Body related','Soul related'])
                with bodytab:
                    for item in ['wake_up','day_rest','to_bed']:
                        st.metric(item.replace("_"," ").title(),
                                f"{weeksummary['all'][item]['%']:.0%}")
                with soultab:
                    st.metric('japa_time'.replace("_"," ").title(),
                        f"{weeksummary['all']['japa_time']['%']:.0%}")
                st.divider()
                st.markdown(
        f"""#### Hearing :green[{weeksummary['summary']['hearing']['achieved']} min] out of :red[{weeksummary['summary']['hearing']['target']}] min""")
                st.markdown(
        f"""#### Reading :green[{weeksummary['summary']['reading']['achieved']} min] out of :red[{weeksummary['summary']['reading']['target']}] min""")

        with _mygroup:
            userinfo = self.scuserinfo
            my_group_name = userinfo['info']['scgroup']
            ignore_list  = ['row_number','week_id','summary']

            for key,value in userinfo['other_users'].items():
                if value != my_group_name:
                    ignore_list.append(key)
            not_filled = []
            all_devotee_together_dict = {}
            # st.write(all_sc_this_week)
            _have_no_data = True
            for name, data in all_sc_this_week.items():
                if name in ignore_list:
                    continue
                elif data[0] == '':
                    not_filled.append(name)
                else:
                    _have_no_data = False
                    converted2dict = json.loads(data[0])['summary']
                    all_devotee_together_dict[name] = extract_week_summary(name,converted2dict)
            st.markdown(f"### Group: :green[{my_group_name}]")
            st.markdown("Not Filled by")
            st.write(not_filled)
            if _have_no_data == True:
                st.warning("No one have filled")
            else:
            # st.write(all_devotee_together_dict)
                alddf = pd.DataFrame.from_dict(all_devotee_together_dict,orient='index')
                scorecard = st.empty()
                st.markdown("### Toppers")
                for i in ['Japa','Reading','Hearing','Total']:
                    _topper = alddf.at[alddf[i].idxmax(),'Name']
                    _value = alddf.loc[alddf['Name']==_topper,i].tolist()[0]
                    if _value < 1:
                        _value = f'{int(_value * 100)} %'
                    st.markdown(f"#### {i}: :green[{_topper}] ({_value})")
                
                percentcols = ['Japa','Body','Soul','Total','To Bed','Wake Up','Day Rest']
                alddf[percentcols] = alddf[percentcols]*100
                mycolumn_config = {col:st.column_config.NumberColumn(col,format="%.0f %%") for col in percentcols}
                mycolumn_config = {**mycolumn_config,
                                   'Reading':st.column_config.NumberColumn("Reading",format="%.0f min"),
                                   'Hearing':st.column_config.NumberColumn("Hearing",format="%.0f min"),
                                   'Days filled':st.column_config.NumberColumn("days filled",format="%.0f days"),
                                   }
                scorecard.data_editor(alddf,
                           disabled=True,hide_index=True,
                            column_config=mycolumn_config,key='_editor_df_group')
                alldays_filled = alddf.loc[alddf['Days filled']==7,'Name'].tolist()
                st.caption("Filled all 7 days")
                st.write(alldays_filled)

        with _allsc:
            # st.write(all_sc_this_week)
            ignore_list = ['row_number','week_id','summary']
            not_filled = []
            all_devotee_together_dict = {}
            _have_not_data = True
            for name, data in all_sc_this_week.items():
                if name in ignore_list:
                    continue
                elif data[0] == '':
                    not_filled.append(name)
                else:
                    _have_not_data = False
                    converted2dict = json.loads(data[0])['summary']
                    all_devotee_together_dict[name] = extract_week_summary(name,converted2dict)
            # st.write(all_devotee_together_dict)
            st.markdown("Not Filled by")
            st.write(not_filled)
            if _have_not_data == True:
                st.warning("No one have filled")
            else:
                alddf = pd.DataFrame.from_dict(all_devotee_together_dict,orient='index')
                scorecard = st.empty()
                st.markdown("### Toppers")
                for i in ['Japa','Reading','Hearing','Total']:
                    _topper = alddf.at[alddf[i].idxmax(),'Name']
                    _value = alddf.loc[alddf['Name']==_topper,i].tolist()[0]
                    if _value < 1:
                        _value = f'{int(_value * 100)} %'
                    else:
                        _value = f"{round(_value)} minutes"
                    st.markdown(f"#### {i}: :green[{_topper}] ({_value})")
                
                # now for displaying the summary
                percentcols = ['Japa','Body','Soul','Total','To Bed','Wake Up','Day Rest']
                alddf[percentcols] = alddf[percentcols]*100
                mycolumn_config = {col:st.column_config.NumberColumn(col,format="%.0f %%") for col in percentcols}
                mycolumn_config = {**mycolumn_config,
                                   'Reading':st.column_config.NumberColumn("Reading",format="%.0f min"),
                                   'Hearing':st.column_config.NumberColumn("Hearing",format="%.0f min"),
                                   'Days filled':st.column_config.NumberColumn("days filled",format="%.0f days"),
                                   }
                scorecard.data_editor(alddf,
                           disabled=True,hide_index=True,
                            column_config=mycolumn_config,key='_editor_df_all_devotees')  
                alldays_filled = alddf.loc[alddf['Days filled']==7,'Name'].tolist()
                st.caption("Filled all 7 days")
                st.write(alldays_filled)                     

        with _standards:
            st.markdown("This section describes various targets for the two Sadhana Card")
            stdb = self.scstandard
            choice = st.radio("View For ",
                     options=['fast','slow'],
                     format_func=lambda x: "Less than 3 hours " if x=='fast' else 'More than 3 hours')
            if choice == 'fast':
                scdf = stdb['sc_fast']['df']
                scdict = stdb['sc_fast']['dict']
            else:
                scdf = stdb['sc_std']['df']
                scdict = stdb['sc_std']['dict']
            st.divider()
            st.header("Soul")
            st.markdown(f"### Reading {scdict['total_reading']['mark']} marks for {scdict['total_reading']['value']} mins")            
            st.markdown(f"#### Srila Prabhupada Books: :violet[{scdict['sp_books']['value']} mins]")
            st.markdown(f"#### About Srila Prabhupada: :violet[{scdict['about_sp']['value']} mins]")
            
            st.divider()

            st.markdown(f"### Hearing {scdict['total_hearing']['mark']} marks for {scdict['total_hearing']['value']} mins")            
            for i in ["hearing_sp","hearing_hhrnsm","hearing_hgrsp","hearing_councellor"]:
                st.markdown(f"#### {i.replace('hearing_','').upper()}: :violet[{scdict[i]['value']} mins]")
            
            st.markdown(f"#### Shloka {scdict['shloka']['mark']} for {scdict['shloka']['value']} Shlokas")
            st.caption("Marks are proportional to the hearing")

            st.divider()

            st.markdown(f"### Full Morning Program marks {scdict['full_mp']['mark']}")
            st.caption("Individual marks are as follows")
            for i in [
                    'on_time',
                    'sa',
                    'mangal_aarti',
                    'morning_class',
                    # 'full_mp',
                    ]:
                st.markdown(f"""* {i.replace("_"," ").upper()}: {scdict[i]['mark']}""")
            st.divider()
            st.markdown(f"### Japa full marks for a day {scdict['_japa_time']['mark']}")
            st.caption("Various division is as follows")
            df = scdf.query("name == 'japa_time' ")[['value','mark']].astype('int').reset_index(drop=True)
            df.sort_values(by='value',ascending=True,inplace=True)
            # st.data_editor(df,disabled=True)
            for _i, _row in df.iterrows():
                st.markdown(f"* {_i+1}. Before :orange[{_row['value']}]: :violet[{_row['mark']}]")

            st.markdown("# Body")

            st.markdown(f"### Wake Up full marks for a day {scdict['_wake_up']['mark']}")
            df = scdf.query("name == 'wake_up' ")[['value','mark']].astype('int').reset_index(drop=True)
            df.sort_values(by='value',ascending=True,inplace=True)
            # st.data_editor(df,disabled=True)
            for _i, _row in df.iterrows():
                st.markdown(f"* {_i+1}. Before :orange[{_row['value']}]: :violet[{_row['mark']}]")
            
            st.markdown(f"### Day Rest full marks for a day {scdict['_day_rest']['mark']}")
            df = scdf.query("name == 'day_rest' ")[['value','mark']].astype('int').reset_index(drop=True)
            df.sort_values(by='value',ascending=True,inplace=True)
            # st.data_editor(df,disabled=True)
            for _i, _row in df.iterrows():
                st.markdown(f"* {_i+1}. Less than :orange[{_row['value']}] min :- :violet[{_row['mark']}]")

            st.markdown(f"### To Bed full marks for a day {scdict['_to_bed']['mark']}")
            df = scdf.query("name == 'to_bed' ")[['value','mark']].astype('int').reset_index(drop=True)
            df.sort_values(by='value',ascending=True,inplace=True)
            # st.data_editor(df,disabled=True)
            for _i, _row in df.iterrows():
                if _row['value'] < 0:
                    continue
                st.markdown(f"* {_i}. Before :orange[{_row['value']}]: :violet[{_row['mark']}] min")
            
            st.markdown(f"### Personal Cleanliness full marks for a day: {scdict['pc']['mark']}")
            st.markdown(f"### Filling Sadhana Card full marks for a day: {scdict['fsc']['mark']}")

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