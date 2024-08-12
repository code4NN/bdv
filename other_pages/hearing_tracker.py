import os
import random
import numpy as np
import streamlit as st
import pandas as pd
import json
import datetime

from custom_module.mega.mega.mega import Mega

from other_pages.googleapi import download_data,download_sheet,upload_data
from openpyxl.utils import get_column_letter
from streamlit.components.v1 import html as display_html

class SP_hearing_Class:
    def __init__(self):
        
        self.page_config = {'page_title': "Shravanam",
                            'page_icon':'💊',
                            'layout':'centered'}
        self.page_map = {
            'SP':self.sp_lectures,
            'SP_lec_player':self.hear_sp_now,
            "user_registration":self.registration
            }
        self.current_page = 'SP'
        self.mega = Mega()
        
        # ===================================databases=================================
        # for Prabhupada lectures------------------------------------------------------
        self.sp_sindhu_df = pd.read_csv("./local_data/SP_sindhu_config.csv")
        self.sp_sindhu_df.insert(0,"select",False)
        self.sp_sindhu_df['name'] = np.where(self.sp_sindhu_df['category'].isin(['Bg','SB']),
                                             self.sp_sindhu_df['prefix'] + " "+self.sp_sindhu_df['name'],
                                             self.sp_sindhu_df['name'])
        # user data (this is used if logged in)
        self._sp_userdb = None
        self._sp_userdb_refresh = True
        
        # prabhupada hearing page db
        self._sp_single_choice_dfdict = {
                                    # global
                                     'update_post_date':True,
                                    
                                    # for SB related
                                     'SB_canto':None,
                                     'SB_chapter':None,
                                     'SB_location':None,
                                     
                                     'update_post_canto':True,
                                     'update_post_chapter':True,
                                     
                                     # for BG related
                                     'update_post_bg_chapter':True,
                                     'BG_chapter':None,
                                     'BG_location':None,
                                     
                                     # for all other
                                     'update_post_radio':True,
                                     'update_post_year':True,
                                     'update_post_month':True,
                                     'yeardf':None,
                                     'monthdf':None,
                                     'locationdf':None
                                     }
        self.update_sp_sindhu_finder("category == 'SB'",['canto','chapter','location'])
        self.update_sp_sindhu_finder("category == 'Bg' ",['BG_chapter','BG_location'])
        
        # for hear now
        self.play_now_info_dict = None
        
        # for user info etc-------------------------------
        self._userdb = None
        self.refresh_userdb = True
        
        # userdata from sp-sindhu table
        self.userinfo = {"mode":"guest",
                         "user":{}
                         }
        self.registrationinfo = {"source":'external',# bdv,external
                                 'reg_status':None, # success after submission
                                }
    @property
    def user_exists(self):
        return self.userinfo['mode'] == 'user'
        
    @property
    def userdb(self):
        """
        dfself, dfall, dict
        """
        if self.refresh_userdb:
            dbarray = download_sheet(1,'sp_sindhu_creds')
            dbdf = pd.DataFrame(dbarray[1:],columns=dbarray[0])
            
            dbdict = {k:v for k,v in dict(zip(dbdf.mdata_key,
                              dbdf.mdata_value)).items() if k not in ['3','']}
            dbdict['existing_userid_list'] = dbdict['existing_userid_list'].split(",")
            
            self._userdb = {
                'dfself':None,
                'dfall':dbdf.drop(columns=['mdata_key','mdata_value']),
                'dict':dbdict
                }
        return self._userdb
    
    @property
    def bdvapp(self):
        return st.session_state['bdv_app']
    
# ================functions related to Srila Prabhupada Sindhu hearing
    def get_sp_sindhu_value_count(self,query,column_name,new_name):
        df = self.sp_sindhu_df.copy(deep=True)
        dfsummary = df.query(query)[column_name]\
        .value_counts().reset_index().sort_values(column_name,ascending=True)
        dfsummary.columns = [new_name,'count']
        dfsummary.insert(0,'select',False)
        return dfsummary.copy()
    
    def update_sp_sindhu_finder(self,query,update_list):
        """
        #### for SB
        * canto
        * chapter
        * location
        #### for BG
        * BG_chapter
        * BG_location
        
        #### for other
        * yeardf
        * monthdf
        * locationdf
        """
        # for SB
        if 'canto' in update_list:
            self._sp_single_choice_dfdict['SB_canto'] = self.get_sp_sindhu_value_count(query,'sb_canto','canto')
        
        if 'chapter' in update_list:
            self._sp_single_choice_dfdict['SB_chapter'] = self.get_sp_sindhu_value_count(query,'sb_ch','chapter')
        
        if 'location' in update_list:
            self._sp_single_choice_dfdict['SB_location'] = self.get_sp_sindhu_value_count(query,'location','location')
        
        # for BG
        if 'BG_chapter' in update_list:
            self._sp_single_choice_dfdict['BG_chapter'] = self.get_sp_sindhu_value_count(query,'bg_ch','chapter')
        
        if 'BG_location' in update_list:
            self._sp_single_choice_dfdict['BG_location'] = self.get_sp_sindhu_value_count(query,'location','location')
        
        # for all other
        if 'yeardf' in update_list:
            self._sp_single_choice_dfdict['yeardf'] = self.get_sp_sindhu_value_count(query,'year','year')
        
        if 'monthdf' in update_list:
            df = self.get_sp_sindhu_value_count(query,'month_Eng','month')
            monthmap = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
            df['newcol'] = df['month'].apply(lambda x:monthmap[x])
            df = df.sort_values(by='newcol',ascending=True)
            df = df.drop(columns='newcol')
            self._sp_single_choice_dfdict['monthdf'] = df.copy()
        
        if 'locationdf' in update_list:
            self._sp_single_choice_dfdict['locationdf'] = self.get_sp_sindhu_value_count(query,'location','location')
            
    def __single_select_chb_sp(self,editor_key,original_key,checkbox_column):
        """
        * editor_key = key for the st.data_editor
        * original_key = the df should be stored in st.session_state[original_key]
        * checkbox_column = name of the checkbox column
        * It must be the first column"""
        edited_rows = st.session_state[editor_key]['edited_rows']
        if len(edited_rows)==1:
            row_num = list(edited_rows.keys())[0]
            # df = st.session_state[original_key].copy(deep=True)
            df = self._sp_single_choice_dfdict[original_key].copy()
            
            set_2_True = list(edited_rows.values())[0][checkbox_column]        
            if set_2_True:
                df[checkbox_column] = False
                df.iloc[row_num,0] = True
                self._sp_single_choice_dfdict[original_key]= df.copy()
            else:
                df[checkbox_column] = False
                self._sp_single_choice_dfdict[original_key]= df.copy()
                st.session_state[editor_key]['edited_rows'] = {}
        
        # for SB
        if editor_key == 'sb_canto_selector':
            self._sp_single_choice_dfdict['update_post_canto'] = True
        
        elif editor_key == 'sb_chapter_selector':
            self._sp_single_choice_dfdict['update_post_chapter'] = True        
        # for bG
        elif editor_key == 'bg_chapter_picker':
            self._sp_single_choice_dfdict['update_post_bg_chapter'] = True
        # for others
        elif editor_key == 'yeardf_picker':
            self._sp_single_choice_dfdict['update_post_year'] = True
        
        elif editor_key == 'monthdf_picker':
            self._sp_single_choice_dfdict['update_post_month'] = True
            
    def sp_lectures(self):
        
        if self.bdvapp.userinfo:
            if 'sp_vani_admin' in self.bdvapp.userinfo['roles']:
                st.button("Pending Registrations",on_click=self.switch_page,
                        args=['user_registration'])
        
        st.header(":rainbow[Srila Prabhupada Ki Jai!!]")
        if self.user_exists:
            st.markdown(f"### :gray[Hare Krishna] :rainbow[{self.userinfo['user']['creds']['name']}]")
        
        spdf = self.sp_sindhu_df.copy(deep=True) # load the lecture config file
        displayconfig = {
            'select':st.column_config.CheckboxColumn('pick'),
            'category':st.column_config.TextColumn("type",width='small'),
            # 'prefix':st.column_config.TextColumn("id"),
            'name':st.column_config.TextColumn("title"),
            'name_1':st.column_config.TextColumn("title"),
            'url':st.column_config.LinkColumn("url",display_text="download"),
            'duration':st.column_config.NumberColumn("⏳min"),
            'month_Eng':st.column_config.TextColumn("month"),
            'mmm_dd':st.column_config.TextColumn("day"),
            'yy_mmm_dd':st.column_config.TextColumn("date")
        }
        
        # st.dataframe(spdf,column_config=displayconfig)
        
        subsubpage_dict = {1:'SB',
                           2:'BG',
                           3:'MW, RC etc'
                           }
        def sectionradiohandler():
            self._sp_single_choice_dfdict['update_post_date'] = True
        section_index = st.radio("Choose a Section",
                              options=range(1,len(subsubpage_dict.keys())+1),
                              index=0,
                              format_func=lambda x: subsubpage_dict[x],
                              horizontal=True,
                              on_change=sectionradiohandler
                              )
            # SB corner
            # 1. first display as many tabs as bookmarks in the file (if logged in)
            # 3. selector
            #     -> Date (year, month and day)
            #     -> Canto
            #     -> Chapter
            #     -> Location
            # 2. Show a search-box for searching lectures plus a display of results
            #    -> results in data frame
        
        if section_index==1:
            querysofar = ["category == 'SB'"]
        
        elif section_index ==2:
            querysofar = ["category == 'Bg' "]
            
        elif section_index == 3:
            def update_on_change_radio():
                self._sp_single_choice_dfdict['update_post_radio'] = True
                self._sp_single_choice_dfdict['update_post_date'] = True
                
            further_type = st.radio("Choose further",
                     options=['MW','RC',"Interv",'Lect','Fest','Cc',"Addr",'Story'],
                     on_change=update_on_change_radio,
                     format_func=lambda x:{"MW":'Morning Walks',
                                           'RC':'Room Conversation',
                                           'Lect':"Public Lectures",
                                           'Cc':"CC Lectures",
                                           'Fest':"Festivals",
                                           "Interv":"Interviews",
                                           "Addr":"Addresses",
                                           'Story':"Stories"
                                           }[x])
            querysofar = [f"category =='{further_type}'"]
            if further_type == 'Addr':
                querysofar = [f"((category == 'Arr') or  (category == 'Addr')) "]
            
            if self._sp_single_choice_dfdict['update_post_radio']:
                self.update_sp_sindhu_finder(" and ".join(querysofar),
                                             ['yeardf','monthdf','locationdf'])
                self._sp_single_choice_dfdict['update_post_radio'] = False
        
        # this filters based on section selection
        spdf = spdf.query(" and ".join(querysofar))
        
        # -------------provision for date filter
        def checkbox_handler():
            if not st.session_state['date_filter_checkbox']:
                if section_index==1:
                    self.update_sp_sindhu_finder("category == 'SB'",
                                                ['canto','chapter','location'])
                elif section_index == 2:
                    self.update_sp_sindhu_finder("category == 'Bg' ",
                                                 ['BG_chapter','BG_location'])
                elif section_index ==3:
                    self.update_sp_sindhu_finder(querysofar[0],
                                                 ['yeardf','monthdf','locationdf'])
        if section_index==3 and further_type=="Story":
            pass
        
        elif st.checkbox("Add date filter",
                        key='date_filter_checkbox',
                        on_change=checkbox_handler):
            def sp_date_handler():
                self._sp_single_choice_dfdict['update_post_date'] = True
            
            chosen_date = st.date_input("Enter date", 
                                        format="YYYY-MM-DD",
                                        min_value=datetime.date(1966,2,19), # hardcoded from excel
                                        max_value=datetime.date(1977,7,1), # hardcoded from excel
                                        value=datetime.date(1972,
                                                            datetime.datetime.today().month,
                                                            datetime.datetime.today().day),
                                        on_change=sp_date_handler)
            chosen_year = chosen_date.year
            chosen_month = chosen_date.month
            chosen_day = chosen_date.day
            
            querysofar.extend([f"year == {chosen_year}", f"month == {chosen_month}"])
            if not st.toggle("Ignore day", value=True,on_change=sp_date_handler):
                querysofar.append(f"day == {chosen_day}")
            
            spdf = spdf.query(" and ".join(querysofar))
            if self._sp_single_choice_dfdict['update_post_date']:
                if section_index==1:
                    self.update_sp_sindhu_finder(' and '.join(querysofar),
                                                ['canto','chapter','location'])
                elif section_index ==2:
                    self.update_sp_sindhu_finder(' and '.join(querysofar),
                                                 ['BG_chapter','BG_location'])
                elif section_index==3:
                    self.update_sp_sindhu_finder(" and ".join(querysofar),
                                                 ['yeardf','monthdf','locationdf'])
                self._sp_single_choice_dfdict['update_post_date'] = False
            st.caption(f"found {len(spdf)} records from 1849")
        
        # date filter ends here
        
        if section_index == 1:
            # further filters of canto- chapter location
            st.divider()
            left,middle,right = st.columns(3)
            with left:
                st.markdown("Choose Canto")
                list_chosen_canto = st.data_editor(self._sp_single_choice_dfdict['SB_canto'],
                                                    hide_index=True,
                                                    column_config={'select':st.column_config.CheckboxColumn("Select"),
                                                                    'canto':st.column_config.NumberColumn('Canto')},
                                                    key='sb_canto_selector',
                                                    on_change=self.__single_select_chb_sp,
                                                    args=['sb_canto_selector','SB_canto','select']
                                                    ).query("select == True")['canto'].tolist()
                # st.write(st.session_state['sb_canto_selector'])
                # st.dataframe(self._sp_single_choice_dfdict['SB_canto'])
                
                if list_chosen_canto :
                    querysofar.append(f"sb_canto == {list_chosen_canto[0]}")
                    spdf = spdf.query(" and ".join(querysofar) )
                    
                # update only when canto is changed
                if self._sp_single_choice_dfdict['update_post_canto']:
                    # querylist = ["category == 'SB'",*date_filter]
                    # if list_chosen_canto:
                    #     querylist.append(cantoquery)
                    self.update_sp_sindhu_finder(' and '.join(querysofar),
                                                ['chapter','location'])
                    self._sp_single_choice_dfdict['update_post_canto'] = False        
            
            with middle:
                st.markdown("Choose Chapter")
                list_chosen_chapter = st.data_editor(self._sp_single_choice_dfdict['SB_chapter'],
                                                    hide_index=True,
                                                    column_config={'select':st.column_config.CheckboxColumn("Select"),
                                                                    'chapter':st.column_config.NumberColumn('Chapter')},
                                                    key='sb_chapter_selector',
                                                    on_change=self.__single_select_chb_sp,
                                                    args=['sb_chapter_selector','SB_chapter','select']
                                                    ).query("select == True")['chapter'].tolist()
                
                if list_chosen_chapter:
                    querysofar.append(f" sb_ch == {list_chosen_chapter[0]}")
                    spdf = spdf.query(" and ".join(querysofar))
                
                # update only if chapter edited
                if self._sp_single_choice_dfdict['update_post_chapter']:
                    # querylist = ["category == 'SB' ",*date_filter]
                    # if list_chosen_canto:
                    #     querylist.append(cantoquery)
                    # if list_chosen_chapter:
                    #     querylist.append(chapterquery)
                    # chapterquery = "" if not list_chosen_canto else f"{chapterquery}"
                    self.update_sp_sindhu_finder(' and '.join(querysofar),
                                                    update_list=['location'])
                    self._sp_single_choice_dfdict['update_post_chapter'] = False
                            
            with right:
                st.markdown("Choose Location")
                list_chosen_location = st.data_editor(self._sp_single_choice_dfdict['SB_location'],
                                                    hide_index=True,
                                                    column_config={'select':st.column_config.CheckboxColumn("Select"),
                                                                    'location':st.column_config.TextColumn('Location')},
                                                    key='sb_location_selector',
                                                    on_change=self.__single_select_chb_sp,
                                                    args=['sb_location_selector','SB_location','select']
                                                    ).query("select == True")['location'].tolist()
                if list_chosen_location:
                    spdf = spdf.query(f"location == '{list_chosen_location[0]}' ")            
        
        elif section_index==2:
            # BG
            st.divider()
            left,right = st.columns(2)
            with left:
                st.markdown("choose chapter")
                list_chosen_chapter = st.data_editor(
                    data=self._sp_single_choice_dfdict['BG_chapter'],
                    hide_index=True,
                    column_config={'select':st.column_config.CheckboxColumn("Select"),
                                   'chapter':st.column_config.NumberColumn("Chapter")},
                    key='bg_chapter_picker',
                    on_change=self.__single_select_chb_sp,
                    args=['bg_chapter_picker','BG_chapter','select']
                ).query("select == True")['chapter'].tolist()
                
                if list_chosen_chapter:
                    querysofar.append(f"bg_ch == {list_chosen_chapter[0]} ")
                    spdf = spdf.query(" and ".join(querysofar))
                
                if self._sp_single_choice_dfdict['update_post_bg_chapter']:
                    self.update_sp_sindhu_finder(" and ".join(querysofar),
                                                 ['BG_location'])
                    self._sp_single_choice_dfdict['update_post_bg_chapter'] = False
            
            with right:
                st.markdown("Choose location")
                list_chosen_location = st.data_editor(
                    data=self._sp_single_choice_dfdict['BG_location'],
                    hide_index=True,
                    column_config={'select':st.column_config.CheckboxColumn("Select"),
                                   'location':st.column_config.TextColumn("location")},
                    disabled=['location'],
                    on_change=self.__single_select_chb_sp,
                    key='bg_location_picker',
                    args=['bg_location_picker','BG_location','select']
                )
                
        elif section_index == 3:
            # morning Waslk and Room Conversations
            if further_type!='Story':
                st.divider()
                left,middle,right = st.columns(3)
                with left:
                    st.markdown('Choose Year')
                    list_chosen_year = st.data_editor(
                        data=self._sp_single_choice_dfdict['yeardf'],
                        hide_index=True,
                        column_config={'year':st.column_config.NumberColumn("year"),
                                    'select':st.column_config.CheckboxColumn("Select")},
                        disabled=['year'],
                        on_change=self.__single_select_chb_sp,
                        key='yeardf_picker',
                        args=['yeardf_picker','yeardf','select']
                    ).query("select == True")['year'].tolist()

                    if list_chosen_year:
                        querysofar.append(f"year == {list_chosen_year[0]}")
                        spdf.query(" and ".join(querysofar))
                    
                    if self._sp_single_choice_dfdict['update_post_year']:
                        self.update_sp_sindhu_finder(" and ".join(querysofar),
                                                    ['monthdf','locationdf'])
                        self._sp_single_choice_dfdict['update_post_year'] = False
                
                with middle:
                    st.markdown("Choose month")
                    list_chosen_month = st.data_editor(
                        data=self._sp_single_choice_dfdict['monthdf'],
                        hide_index=True,
                        column_config={'month':st.column_config.TextColumn("Month"),
                                    'select':st.column_config.CheckboxColumn("Select")},
                        disabled=['month'],
                        on_change=self.__single_select_chb_sp,
                        key='monthdf_picker',
                        args=['monthdf_picker','monthdf','select']
                    ).query("select == True")['month'].tolist()
                    
                    if list_chosen_month:
                        querysofar.append(f"month_Eng == '{list_chosen_month[0]}'")
                        spdf.query(" and ".join(querysofar))
                    
                    if self._sp_single_choice_dfdict['update_post_month']:
                        self.update_sp_sindhu_finder(" and ".join(querysofar),
                                                    ['locationdf'])
                        self._sp_single_choice_dfdict['update_post_month'] = False
                
                with right:
                    st.markdown("Choose Location")
                    list_chosen_location = st.data_editor(
                        data = self._sp_single_choice_dfdict['locationdf'],
                        hide_index=True,
                        column_config={'select':st.column_config.CheckboxColumn("Select"),
                                    'location':st.column_config.TextColumn("Location")},
                        disabled=['location'],
                        key='locationdf_picker',
                        on_change=self.__single_select_chb_sp,
                        args=['locationdf_picker','locationdf','select']
                    )
            #now display the list of filtered lectures
            # spdf
        
        # now we have all the filters applied. Just display the filtered
        st.divider()
        st.caption(f"found {len(spdf)} records")
        sb_column_config = {k:v for k,v in displayconfig.items() if k in 
                            ['select','prefix','name','yy_mmm_dd','duration']}
        choice = st.checkbox("Pick ",value=True)
        spdf['select'] = choice
        response = st.data_editor(spdf,column_config=sb_column_config,
                        column_order=list(sb_column_config.keys()),
                        hide_index=True,
                        disabled=list(set(sb_column_config.keys())-{'select'})).query("select==True")
        
        for _row,row in response.reset_index(drop=True).iterrows():
            with st.expander(
            f"{_row+1}\. {row['full_name'][:-4]}  :violet[{row['duration']}min]",
            expanded=False):
                cols = st.columns(2)
                cols[0].link_button("Hear in new tab",
                    url="https://bdv-voice-dev.streamlit.app/?target=hear-now"\
                        +f"&source=sp_sindhu"
                        +f"&mode=guest"
                        +f"&id={row['encrypt_id']}"
                        )
                cols[1].markdown(f"[download from mega]({row['url']})")
            
            if (_row+1)%15 ==0:
                placeholder = st.empty()
                if not placeholder.checkbox(f"Show {len(spdf)-1-_row} more",
                                    key=f'showmore_{_row}',
                                    value=False):
                    break
                else:
                    placeholder.empty()

    def hear_sp_now(self):
        url = f"https://mega.co.nz/#!{self.play_now_info_dict['megaid']}"
        destination = './local_data/sp_storage'
        filename = f"{self.play_now_info_dict['spid']}.mp3"
        displayname = self.play_now_info_dict['name']
        available_files = os.listdir(destination)
        
        msgbox = st.empty()
        if filename not in available_files:
            # keep the latest 10 files and delete the older ones
            # reverse = True sorted in decending order
            available_files = sorted(available_files,
                                     key=lambda x: os.path.getmtime(f"{destination}/{x}"),reverse=True)
            for one_file in available_files[5:]:
                os.remove(f"{destination}/{one_file}")
                
            with msgbox.container():
                st.markdown(f"downloading from mega ")
                st.caption(displayname)
                st.caption("This may take a while please wait ...")
                self.mega.download_url(url,destination,dest_filename=filename)
                st.success("completed")
                
        msgbox.markdown(f"## :rainbow[{displayname}]")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        foward_min = st.number_input("forward (in min)",step=1,min_value=0)
        
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.audio(f"{destination}/{filename}",format="audio/wav",
                 start_time=foward_min*60)
    
    def switch_page(self,newpage):
        self.current_page=newpage
    
    def registration(self):
        if self.registrationinfo['reg_status'] == 'success':
            st.success("You have successfully submitted your form")
            st.info("Upon verification your account will be created")
            
        elif self.registrationinfo=='bdv':
            st.success("Congratulations!!")
            st.subheader(":rainbow[You are already part of BDV family]")
            st.markdown("### :gray[Just enter your phone number to register]")
            with st.popover("Why are we asking phone number"):
                st.markdown("1\. To protect against robotic attacks")
                st.markdown("2\. To have a unique id of user")
                st.markdown("2\. To connect with you if any problems 🤝")
            number = st.number_input("Please enter 10 digit phone number")
            if number:
                if len(str(number)) !=10:
                    st.error("Please enter 10 digit number")
                elif not all([i in '0123456789' for i in str(number)]):
                    st.error("Only Numbers are allowed")
                
                elif str(number) in self.userdb['dict']['existing_userid_list']:
                    st.error("A user already exists with this number")
                else:
                    # success
                    def register_user(number):
                        password = self.bdvapp.userinfo['password']
                        name = f"{self.bdvapp.userinfo['name']} Pr"
                        userinfo = {
                                    "account_is_active":'no',
                                    "creds":{'name':name,
                                             'password':password,
                                             'phone':number}
                                    }
                        id_insert_col = int(self.userdb['dict']['insert_id_col_index'])
                        upload_range = f"sp_sindhu_creds!{get_column_letter(id_insert_col)}1:{get_column_letter(id_insert_col)}2"
                        upload_data(1,upload_range,
                                    [[number],[json.dumps(userinfo)]])
                        self.registrationinfo['reg_status'] = 'success'
                        
                    st.divider()
                    st.button("Click to Register",
                              on_click=register_user,
                              args=[str(number)])
        
        else:
            # external user
            st.subheader(":rainbow[Welcome to the SP sindhu registration]")
            st.markdown("### :gray[Just enter few details]")
            with st.popover("Why are we asking phone number"):
                st.markdown("1\. To protect against robotic attacks")
                st.markdown("2\. To have a unique id of user")
                st.markdown("2\. To connect with you if any problems 🤝")
            
            number = st.number_input("Please enter 10 digit phone number",step=1)
            number_verified = False
            if number:
                if len(str(number)) !=10:
                    st.error("Please enter 10 digit number")
                elif not all([i in '0123456789' for i in str(number)]):
                    st.error("Only Numbers are allowed")
                
                elif str(number) in self.userdb['dict']['existing_userid_list']:
                    st.error("A user already exists with this number")
                else:
                    # success
                    st.caption("Jai Haribol!!")
                    number_verified = True
            if  number_verified:
                # move ahead only if number is verified
                
                name = st.text_input("Enter name (without any prefix like ys or your servant )",
                                    max_chars=20)
                password = st.text_input("Enter password",type='password',
                                        max_chars=15)
                if not name:
                    st.caption("Must write name")
                elif not password:
                    st.caption("Must have a password")
                else:
                    # verified
                    def register_user_ext(number,userinfo):
                            password = userinfo['password']
                            name = f"{userinfo['name']} Pr"
                            userinfo = {
                                        "account_is_active":'no',
                                        "creds":{'name':name,
                                                'password':password,
                                                'phone':number}
                                        }
                            id_insert_col = int(self.userdb['dict']['insert_id_col_index'])
                            upload_range = f"sp_sindhu_creds!{get_column_letter(id_insert_col)}1:{get_column_letter(id_insert_col)}2"
                            upload_data(1,upload_range,
                                        [[number],[json.dumps(userinfo)]])
                            self.registrationinfo['reg_status'] = 'success'
                            
                    st.divider()
                    st.button("Click to Register",
                            on_click=register_user_ext,
                            args=[number,{"name":name,
                                   "password":password,
                                   'phone':number}])
        
        st.button("Continue as guest for now",
                      on_click=self.switch_page,
                      args=['SP'])
        if self.bdvapp.userinfo and 'sp_vani_admin' in self.bdvapp.userinfo['roles']:
            # show the pending registrations
            def activate_account(update_range,update_dict):
                update_dict['account_is_active'] = 'yes'
                update_json = json.dumps(update_dict)
                upload_data(1,update_range,[[update_json]])
                
                self._sp_userdb_refresh = True
            
            alldf = self.userdb['dfall']
            for one_user in self.userdb['dict']['existing_userid_list']:
                userdict = json.loads(alldf.query("spid=='userinfo'")[one_user].tolist()[0])
                spdb_col = json.loads(alldf.query("spid=='dbcol'")[one_user].tolist()[0])
                spdb_row = 2
                spdb_update_range = f"sp_sindhu_creds!{get_column_letter(spdb_col)}{spdb_row}"
                if userdict['account_is_active'] == 'no':
                    st.write(userdict)
                    st.button(f"Activate `{userdict['creds']['name']}`",
                              on_click=activate_account,
                              args=[spdb_update_range,userdict],
                              key="activation_"+one_user)
                    st.divider()
            
    
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
        
        if self.userinfo['mode'] == 'guest' and self.current_page !='user_registration':
            # option to login
            with st.sidebar:
                st.info("You are not logged in")
                st.markdown(":gray[Login to have a personalized experience]")
                
                def login_karo(userinfo):
                    self.userinfo = {'mode':'user',
                                    'user':userinfo}
                    st.snow()
                    
                username = str(st.number_input("Enter username (10digit phone)",min_value=0,step=1))
                password = st.text_input("Enter password",type='password')
                if username:
                    if username in self.userdb['dict']['existing_userid_list']:
                        # verify password
                        userinfo = json.loads(
                            self.userdb['dfall'].query("spid=='userinfo'")[username].tolist()[0])
                        if password == userinfo['creds']['password']:
                            st.button("login",key='login',on_click=login_karo,
                                    args=[userinfo],
                                    type='primary')
                        else:
                            st.caption("incorrect password")
                            
                    else:
                        st.caption("no user found")
                
                st.divider()
                st.button("Click Here to register",type='primary',on_click=self.switch_page,
                        args=['user_registration'])
                
        
        self.page_map[self.current_page]()

class VANI_hearing_class():
    def __init__(self):
        
        self.page_config = {'page_title': "Hearing",
                            'page_icon':'💌',
                            'layout':'centered'}
        self.page_map = {
            'dash':self.dash,
            }
        self.current_page = 'dash'
        
        # page data
        self.user_selections = {'speaker':None,
                                'semyear':None}
    
    def dash(self):
        st.header(":rainbow[Vaani Syllabus @BDV]")
        st.markdown("")
        st.markdown("")
        speaker_dict = {0:['dd','DD Series'],
                        1:['hgrsp','HG RSP'],
                        2:['hhrnsm','HH RNSM'],
                        3:['sp','Srila Prabhupada']}
        
        cols = st.columns(4,gap='small')        
        for i in range(4):
            skey,sname = speaker_dict[i]
            is_selected = self.user_selections['speaker'] == skey
            cols[i].button(label=sname,
                           key=f"chosen_speaker_{skey}",
                           on_click=lambda x: self.user_selections.__setitem__('speaker',x),
                           args=[skey],
                           type="primary" if is_selected else "secondary")                        
        st.divider()
        speaker = self.user_selections['speaker']
        # based on speaker one should get the list of semester of year and button just like above
        # for now let's define
        
        available_semester = [f"Sem {i}" for i in range(3,9)]
        available_semester = [f"Year {i}" for i in range(2,5)]
        cols = st.columns(len(available_semester),gap='small')
        for i in range(len(cols)):
            semester = available_semester[i]
            is_selected = self.user_selections['semyear'] == semester
            cols[i].button(label=semester,
                           key=f"chosen_semester_{semester}",
                           on_click=lambda x: self.user_selections.__setitem__('semyear',x),
                           args=[semester],
                           type="primary" if is_selected else "secondary")                                           
        
        
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