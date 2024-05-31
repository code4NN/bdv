import streamlit as st
import pandas as pd


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
        
        # data related to Vaishnva songs
        self.vsong_df = pd.read_excel('data/vsong.xlsx',sheet_name='allsongs')
        self.vsong_selectordf = self.vsong_df[['vsong_name']].drop_duplicates(subset='vsong_name').copy()
        self.vsong_selectordf.insert(0, 'Select', False)
        
        self.active_song_data_list = []
        
        # Data related to Shloka
        self.shloka_df = None # it will be single fetch
        self.user_data_df = None # This we will keep updating
        
    def vsong(self):
        st.header("VSongs")
        with st.sidebar:
            search_query = st.text_input("Search a song")
            # do something and show the results and option to click and load the song
        with st.popover("Song List"):
            def update_playlist(df):
                pass
            edited_df = st.data_editor(self.vsong_selectordf,hide_index=True,
                                       column_config={'Select':st.column_config.CheckboxColumn("Select"),
                                                      'vsong_name':st.column_config.TextColumn("Song Name")},
                                       disabled=['vsong_name'],
                                       on_change=update_playlist)
            
        
        if self.active_song_data_list:
            st.divider()
            display_setting = {}
            with st.popover("Display Options"):
                # display_setting['mode'] = st.radio("Choose a mode",options=['revise','memorize'],horizontal=True,index=0)                
                display_setting["show translation"] = st.checkbox("Show Translation",value=True)
                display_setting['title size'] = '#'*st.slider("Stanza title size",min_value=1,max_value=5,value=3)
                st.markdown(f"{display_setting['title size']} Size Preview")
            
            song2, song1 = self.active_song_data_list[-2:]
            _t1,_t2 = st.tabs(['Title of song 1', 'title of song 2'])
            with _t1:
                for stanza,content in song1.items():
                    st.divider()
                    _title,_help = st.columns([3,1])
                    _title.markdown(f"{display_setting['title size']} :gray[{stanza}]. :purple[{content['title']}]")
                    with _help.popover("help"):
                        st.markdown(f"**{content['title']}**")
                        # display the stanza
                        # display the translation based on setting
                        st.markdown(f"jai ")
            with _t2:
                for stanza,content in song2.items():
                    st.divider()
                    _title,_help = st.columns([3,1])
                    _title.markdown(f"{display_setting['title size']} :gray[{stanza}]. :purple[{content['title']}]")
                    with _help.popover("help"):
                        st.markdown(f"**{content['title']}**")
                        # display the stanza
                        # display the translation based on setting
                        st.markdown(f"jai ")
    
    def shloka(self):
        df = self.shloka_df.copy()
        source_name = st.radio("Source",options=['SB','BG','CC','BS','MM'],index=1)
        df = df.query(f"source=='{source_name}'")
        
        status_list = ['mark for learning','currently learning','freshly learnt','revision']
        status_chosen = st.select_slider("Choose an option",['show all',*status_list],index=0)
        if status_chosen != 'show all':
            df = df.query(f"status=='{status_chosen}'")
            
        with st.popover("➕ more filter"):
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
                bgchapter = st.slider("BG Chapter", min_value=1, max_value=19, value=1)
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