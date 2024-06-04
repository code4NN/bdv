import random
import streamlit as st
import pandas as pd
from other_pages.googleapi import download_data


class memorize_song_shloka:
    def __init__(self):
        self.page_config = {'page_title': "SSong",
                    'page_icon':'🤝',
                    'layout':'centered'}
        self.page_dict = {
            'shloka':self.shloka,
            'vsong':self.vsong,
        }
        self.current_page = 'vsong'
        
        # database related to Vaishnva Songs
        self._vsong_db = None
        self._have_vsong_db = False
                
        # database related to Shloka
        self._shlokadb = None
        self._have_shlokadb = False
        self.user_data_df = None # This we will keep updating
    
    @property
    def get_songdb(self):
        """
        * song_df
        * song_lis_df
        """
        if not self._have_vsong_db:
            vsong_array = download_data(8,"vsongdb!B:F")
            vsong_df = pd.DataFrame(vsong_array[1:],columns=vsong_array[0])
            vsong_df['stanza'] = vsong_df['stanza'].astype('int')
            
            vsong_selectordf = vsong_df[['vsong_name']].drop_duplicates(subset='vsong_name').copy()
            vsong_selectordf.insert(0, 'Select', False)
            vsong_selectordf.iloc[random.randint(0,len(vsong_selectordf)-1),0] = True
            
            # save the needful files
            self._vsong_db = {'song_df':vsong_df.copy(),
                              'song_list_df':vsong_selectordf.copy()}
            self._have_vsong_db = True
        
        return self._vsong_db
    
    @property
    def get_shlokadb(self):
        if not self._have_shlokadb:
            shloka_df_array = download_data(8,"shlokadb!A:M")
            shloka_df = pd.DataFrame(shloka_df_array[1:],columns=shloka_df_array[0])
            
            shloka_df[['canto','chapter']] = shloka_df[['canto','chapter']].fillna(-1).replace("",-1)
            shloka_df[['canto','chapter','text_start']] = shloka_df[['canto','chapter','text_start']].astype("int")
            self._shlokadb = {'fulldf':shloka_df}
        return self._shlokadb
            
    
    def extract_a_song(self,song_name):
        allsongdf = self.get_songdb['song_df'].query(f"vsong_name == '{song_name}'").copy()
        allsongdf.sort_values(by='stanza',ascending=True,inplace=True)
        
        return allsongdf.reset_index(drop=True)
        
        
    def vsong(self):
        vsong_db = self.get_songdb
        vsong_selectordf = vsong_db['song_list_df']
        vsongdf = vsong_db['song_df']
        
        st.header("VSongs")
        # with st.sidebar:
        #     search_query = st.text_input("Search a song")
        #     # do something and show the results and option to click and load the song
        with st.expander("Song List",expanded=True):
            def _df_single_selector(editor_key,check_box_column):
                """
                * editor_key = key for the st.data_editor
                * original_key = the df should be stored in st.session_state[original_key]
                * checkbox_column = name of the checkbox column
                * It must be the first column"""
                edited_rows = st.session_state[editor_key]['edited_rows']
                if len(edited_rows)==1:
                    row_num = list(edited_rows.keys())[0]
                    # df = st.session_state[original_key].copy(deep=True)
                    df = self.get_songdb['song_list_df'].copy()
                    
                    set_2_True = list(edited_rows.values())[0][check_box_column]        
                    if set_2_True:
                        df[check_box_column] = False
                        df.iloc[row_num,0] = True
                        self._vsong_db['song_list_df']= df.copy()
                    else:
                        df[check_box_column] = False
                        self._vsong_db['song_list_df']= df.copy()
                        st.session_state[editor_key]['edited_rows'] = {}

                
            edited_df = st.data_editor(vsong_selectordf,hide_index=True,
                                       column_config={'Select':st.column_config.CheckboxColumn("Select"),
                                                      'vsong_name':st.column_config.TextColumn("Song Name")},
                                       disabled=['vsong_name'],
                                       on_change=_df_single_selector,
                                       key='song_selector_df',
                                       args=['song_selector_df','Select'])
        active_song_list = edited_df.query("Select==True")['vsong_name'].tolist()
        if not active_song_list:
            st.warning("you have not selected any song")
        else:
            active_song = active_song_list[0]
            display_setting = {}
            with st.popover("Display Options"):
                display_setting["show translation"] = st.checkbox("Show Translation",value=True)
                display_setting['title size'] = '#'*st.slider("Stanza title size",min_value=1,max_value=5,value=3)
                st.markdown(f"{display_setting['title size']} Size Preview")
            
            active_song_df = self.extract_a_song(active_song)
            st.markdown(f"## :rainbow[{active_song.title()}]")
            for stanza_no,content in active_song_df.iterrows():
                st.divider()
                _title,_help = st.columns([2,1])
                _title.markdown(f"{display_setting['title size']} :gray[{stanza_no+1}.] :violet[{content['title']}]")
                with _help.popover("help"):
                    st.markdown(f"#### :blue[{content['title']}]")
                    # display the stanza
                    for a_line in content['content'].splitlines():
                        st.markdown(a_line)
                    # display the translation based on setting
                    st.markdown(f":gray[{content['translation']}]")
                    
    def shloka(self):
        shlokadb = self.get_shlokadb
        df = shlokadb['fulldf'].copy(deep=True)
        st.dataframe(df)
        left,right = st.columns(2)
        source_name = left.radio("Source",options=['SB','BG','CC','BS','MM'],index=1,horizontal=True)
        df = df.query(f"source=='{source_name}'")
        
        # if use have logged in then add a filter of status will do in phase-2
        # status_list = ['mark for learning','currently learning','freshly learnt','revision']
        # status_chosen = st.select_slider("Choose an option",['show all',*status_list],index=0)
        # if status_chosen != 'show all':
        #     df = df.query(f"status=='{status_chosen}'")
            
        with right.popover("➕ more filter"):
            if source_name == 'SB':
                # Select a canto
                chosen_canto = st.slider("Canto",min_value=1,max_value=12,value=1)
                df = df.query(f"canto=={chosen_canto}")
                
                # Select a chapter
                chapter_range = [df.chapter.min(),df.chapter.max()]
                chapter = st.number_input(f"Choose a chapter [{chapter_range[0]},{chapter_range[1]}]",
                                          min_value=chapter_range[0], max_value=chapter_range[1],
                                          value=chapter_range[0])
                df = df.query(f"chapter=={chapter}")
                
                # Select a section
                section_option = df['SB_Playlist'].unique().tolist()
                chosen_playlist = st.radio("Choose a section", options=['all',*section_option], index=0)
                if chosen_playlist != 'all':
                    df = df.query(f"SB_Playlist=='{chosen_playlist}'")
                
            elif source_name == 'BG':
                # select a chapter
                bgchapter = st.select_slider("BG Chapter",options=[i for i in range(1,19)])
                df = df.query(f"chapter=={bgchapter}")
                
                # Select a section
                section_option = df['BG_Playlist'].unique().tolist()
                chosen_playlist = st.radio("Choose a section", options=['all', *section_option], index=0)
                if chosen_playlist != 'all':
                    df = df.query(f"BG_Playlist=='{chosen_playlist}'")
            
            elif source_name == 'CC':
                st.info("in progress")
            elif source_name == 'BS':
                pass
            elif source_name == 'MM':
                pass
        
        # now display the shlokas with title
        hide_index = st.toggle("Hide verse Number",value=False)
        
        for _index,row in df.reset_index(drop=True).iterrows():
            st.divider()
            if hide_index:
                st.markdown(f"### :purple[{row['title']}]")
            else:
                st.markdown(f"### :gray[{row['vindex']}] :purple[{row['title']}]")
            with st.popover("Show the verse"):
                st.markdown(f" Display the verse")
                st.info('Also here we can give option to update the status of the shloka')
            
            if _index+1%10==0:
                # add a anchor
                # also add a link to go to the top
                # if _index >10 then also link to previous anchor
                if not st.checkbox(f"Show {len(df)-_index} more shlokas",key=f"{_index}_cnf_show"):
                    break                                            
    
    def run(self):
        self.page_dict[self.current_page]()