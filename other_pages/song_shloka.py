
import random
import streamlit as st
import pandas as pd
from other_pages.googleapi import download_data, upload_data

# for vedabase shloka etc
import requests
from bs4 import BeautifulSoup

def url_fetch(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    alltext = {
        a_match.find_all("a")[0].text.lower().replace("text ",'').replace("texts ",''):
            a_match for a_match in soup.find_all(class_='bb r-verse')}
    return alltext

class memorize_song_shloka:
    def __init__(self):
        self.page_config = {'page_title': "SSong",
                    'page_icon':'🤝',
                    'layout':'centered'}
        self.page_dict = {
            'shloka':self.shloka,
            'vsong':self.vsong,
            'add_shloka':self.addshloka
        }
        self.current_page = 'add_shloka'
        
        # database related to Vaishnva Songs
        self._vsong_db = None
        self._have_vsong_db = False
                
        # database related to Shloka
        self._shlokadb = None
        self._have_shlokadb = False
        self.user_data_df = None # This we will keep updating
        
        # shloka page related
        self.SCQ_filter_dfs = {'SB_canto':None,
                               'SB_chapter':None,
                               'BG_chapter':None}
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
        """
        * fulldf
        also populates SB_canto_df and BG_chapter_df
        """
        if not self._have_shlokadb:
            self._have_shlokadb = True
            
            shloka_df_array = download_data(8,"shlokadb!A:M")
            shloka_df = pd.DataFrame(shloka_df_array[1:],columns=shloka_df_array[0])
            
            shloka_df[['canto','chapter']] = shloka_df[['canto','chapter']].fillna(-1).replace("",-1)
            shloka_df[['canto','chapter','text_start']] = shloka_df[['canto','chapter','text_start']].astype("int")
            
            self._shlokadb = {'fulldf':shloka_df}
            # initialize the SB_canto_df and BG_chapter_df
            # SB related
            SB_canto_df = shloka_df[['source','canto']].query("source=='SB' and canto != -1").drop(columns='source')\
                            .drop_duplicates(keep='first').copy(deep=True)
            SB_canto_df.sort_values(by='canto',ascending=True,inplace=True)
            SB_canto_df.insert(0, 'select', False)
            SB_canto_df.iloc[random.randint(0, len(SB_canto_df)-1),0] = True
            self.SCQ_filter_dfs['SB_canto'] = SB_canto_df.copy()
            # BG related
            BG_chapter_df = shloka_df[['source','chapter']].query("source=='BG' and chapter != -1").drop(columns='source')\
                            .drop_duplicates(keep='first').copy(deep=True)
            BG_chapter_df.sort_values(by='chapter', ascending=True, inplace=True)
            BG_chapter_df.insert(0, 'select', False)
            BG_chapter_df.iloc[random.randint(0, len(BG_chapter_df)-1),0] = True
            self.SCQ_filter_dfs['BG_chapter'] = BG_chapter_df.copy()
            
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
    
    def __SCQ_handler(self,editor_key,original_key,checkbox_column):
        """
        * editor_key = key for the st.data_editor
        * original_key = the df should be stored in st.session_state[original_key]
        * checkbox_column = name of the checkbox column
        * It must be the first column"""
        edited_rows = st.session_state[editor_key]['edited_rows']
        if len(edited_rows)==1:
            row_num = list(edited_rows.keys())[0]
            # df = st.session_state[original_key].copy(deep=True)
            df = self.SCQ_filter_dfs[original_key].copy()
            
            set_2_True = list(edited_rows.values())[0][checkbox_column]        
            if set_2_True:
                df[checkbox_column] = False
                df.iloc[row_num,0] = True
                self.SCQ_filter_dfs[original_key]= df.copy()
            else:
                df[checkbox_column] = False
                self.SCQ_filter_dfs[original_key]= df.copy()
                st.session_state[editor_key]['edited_rows'] = {}
        
        if editor_key == 'SB_canto_df':
            # update the SB_chapter_df accordingly
            # row_num : row which got edited
            # set_2_True whether it was checked or unchecked
            if set_2_True:
                # get the chapter of the selected canto
                selected_canto = df.iloc[row_num,1]
                available_chapter_df = self.get_shlokadb['fulldf'].query(f"canto=={selected_canto}")\
                [['chapter']].drop_duplicates(keep='first').copy()
                available_chapter_df.sort_values(by='chapter', ascending=True, inplace=True)
                available_chapter_df.insert(0, 'select', False)
                available_chapter_df.iloc[random.randint(0, len(available_chapter_df)-1),0] = True
                
                self.SCQ_filter_dfs['SB_chapter'] = available_chapter_df.copy()
    
    def shloka(self):
        shlokadb = self.get_shlokadb
        df = shlokadb['fulldf'].copy(deep=True)
        st.dataframe(df)
        
        source_name = st.radio("Source",options=['SB','BG','CC','BS','MM'],
                               index=1,
                               horizontal=True)
        df = df.query(f"source=='{source_name}'")
        
        # if use have logged in then add a filter of status will do in phase-2
        # status_list = ['mark for learning','currently learning','freshly learnt','revision']
        # status_chosen = st.select_slider("Choose an option",['show all',*status_list],index=0)
        # if status_chosen != 'show all':
        #     df = df.query(f"status=='{status_chosen}'")
            
        if source_name == 'SB':
            # Select a canto
            chosen_canto_list = st.data_editor(self.SCQ_filter_dfs['SB_canto'],hide_index=True,
                                            column_config={'select':st.column_config.CheckboxColumn("Select"),
                                                           'canto':st.column_config.TextColumn("Canto")},
                                            disabled=['canto'],
                                            key='SB_canto_df',
                                            on_change=self.__SCQ_handler,
                                            args=['SB_canto_df','SB_canto','select']).query("select==True")['canto'].tolist()
            if not chosen_canto_list:
                st.caption("You have not selected any canto")
                st.stop()
            else:
                df = df.query(f"canto=={chosen_canto_list[0]}")
            
            # Select a chapter            
            chosen_chapter_list = st.data_editor(self.SCQ_filter_dfs['SB_chapter'],hide_index=True,
                                            column_config={'select':st.column_config.CheckboxColumn("Select"),
                                                           'chapter':st.column_config.TextColumn("Chapter")},
                                            disabled=['chapter'],
                                            key='SB_chapter_df',
                                            on_change=self.__SCQ_handler,
                                            args=['SB_chapter_df','SB_chapter','select']).query("select==True")['chapter'].tolist()
            if not chosen_chapter_list:
                st.caption("You have not selected any chapter")
                st.stop()
            else:
                df = df.query(f"chapter=={chosen_chapter_list[0]}")
            
            # Select a section ( this is optional perhaps after a month we will start this)
            # section_option = df['SB_Playlist'].unique().tolist()
            # chosen_playlist = st.radio("Choose a section", options=['all',*section_option], index=0)
            # if chosen_playlist != 'all':
            #     df = df.query(f"SB_Playlist=='{chosen_playlist}'")
            
        elif source_name == 'BG':
            # select a chapter
            chosen_chapter_list = st.data_editor(self.SCQ_filter_dfs['BG_chapter'],hide_index=True,
                                            column_config={'select':st.column_config.CheckboxColumn("Select"),
                                                           'chapter':st.column_config.TextColumn("Chapter")},
                                            disabled=['chapter'],
                                            key='BG_chapter_df',
                                            on_change=self.__SCQ_handler,
                                            args=['BG_chapter_df','BG_chapter','select']).query("select==True")['chapter'].tolist()
            if not chosen_chapter_list:
                st.caption("You have not selected any chapter")
                st.stop()
            else:
                df = df.query(f"chapter=={chosen_chapter_list[0]}")
            
            # Select a section ( this is optional perhaps after a month we will start this)
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
    
    def addshloka(self):
        url = st.text_input("Enter URL").strip()
        if url:
            resultdict = {}
            for key,a_match in url_fetch(url).items():
                # get the text number
                verse_index = key
                
                # get the devnagri
                devnagri = a_match.find_next_sibling(class_='wrapper-devanagari')\
                .find("div",class_='r r-devanagari').getText(separator='\n')
                
                # get english
            #     eng = a_match.find_next_sibling(class_='wrapper-verse-text')\
            #     .find('div',class_='r r-lang-en r-verse-text').getText(separator='\n')
                eng = '\n\n'.join([i.getText(separator='\n') for i in a_match.find_next_sibling(class_='wrapper-verse-text')\
                .findAll('div',class_='r r-lang-en r-verse-text')])
                
                # get purport
                translation = a_match.find_next_sibling(class_='wrapper-translation')\
                .find("div",class_='r r-lang-en r-translation').getText()
                
                # now store
                resultdict[verse_index] = {'verse_index':verse_index,"verse_dev":devnagri,'verse_eng':eng,'verse_translation':translation}
            # create a dataframe
            resultdf = pd.DataFrame.from_dict(resultdict,orient='index')
            st.dataframe(resultdf)
            
        
    def run(self):
        self.page_dict[self.current_page]()

class shlokaloka:
    def __init__(self) -> None:
        self.page_config = {
            "page_title":"shloka-loka",
            "page_icon":"💉",
            "layout":'centered'
        }
        
        self.page_map = {
            "active":"dash",
            "dash":self.dash
        }
        
        # 
        self.url_fetcher = {
            # "URL": response json
        }
    
    def fetch_url(self,url,ftype):
        if url in self.url_fetcher.keys():
            return self.url_fetcher[url]
        elif ftype=='multi':
            
            response = requests.get(url)
            self.url_fetcher[url] = response
            soup = BeautifulSoup(response.content, 'html.parser')
            book = url.replace("https://vedabase.io/en/library","").split("/")[1].upper()
            if book == "BG":
                chapter = url.replace("https://vedabase.io/en/library","").split("/")[2]
                book = f"{book} {chapter}."
            elif book =='SB':
                canto = url.replace("https://vedabase.io/en/library","").split("/")[2]
                chapter = url.replace("https://vedabase.io/en/library","").split("/")[3]
                book = f"{book} {canto}.{chapter}."
            else:
                book = ''
                
            alltext = {(book+a_match.find_all("a")[0]
                        .text.lower().replace("text ",'')
                        .replace("texts ",'')): a_match 
                       for a_match in soup.find_all(class_='bb r-verse')}
            
            resultdict = {}
            for key,a_match in alltext.items():
                # get the text number
                verse_index = key
                
                # get the devnagri
                devnagri = (a_match
                            .find_next_sibling(class_='wrapper-devanagari')
                            .find("div",class_='r r-devanagari')
                            .getText(separator='\n'))
                
                # get english
                eng = ('\n'
                       .join([i.getText(separator='\n') for i in a_match
                              .find_next_sibling(class_='wrapper-verse-text')
                              .findAll('div',class_='r r-lang-en r-verse-text')
                              ]
                             )
                       )
                
                # get translation
                translation = (a_match
                               .find_next_sibling(class_='wrapper-translation')
                               .find("div",class_='r r-lang-en r-translation')
                               .getText())
                
                # now store
                resultdict[verse_index] = {'verse_index':verse_index,
                                           "verse_dev":devnagri,
                                           'verse_eng':eng,
                                           'verse_translation':translation}
            return resultdict
        
        elif ftype =='single':
            response = requests.get(url)
            self.url_fetcher[url] = response
            soup = BeautifulSoup(response.content, 'html.parser')
            
            verse_index = soup.find(class_ = "r r-title r-verse").getText().strip()
            verse_dev = soup.find("div",class_ = "r r-devanagari").getText(separator='\n')
            verse_eng = ('\n'
                       .join([i.getText(separator='\n') for i in soup
                              .find("div",class_='wrapper-verse-text')
                              .findAll('div',class_='r r-lang-en r-verse-text')
                              ]
                             )
                       )
            verse_trnslation = (soup
                               .find("div",class_='wrapper-translation')
                               .find("div",class_='r r-lang-en r-translation')
                               .getText())
            
            return {'verse_index':verse_index,
                    "verse_dev":verse_dev,
                    "verse_eng":verse_eng,
                    "verse_translation":verse_trnslation}
            
    def dash(self):
        
        st.header(":rainbow[Welcome to Shloka Loka]")
        entry_option = st.radio("Choose type of entry",
                 options=['one verse','multiple verses'],
                 horizontal=True)
        
        url = st.text_input("Enter vedabase URL")
        if url:
            response = self.fetch_url(url=url,
                                      ftype='multi' if entry_option =="multiple verses" else 'single')
            st.write(response)
        # if entry_option =="one verse":
            
        
        
    def run(self):
        self.page_map[self.page_map['active']]()