import json
import streamlit as st
import requests
import pandas as pd
from other_pages.googleapi import upload_data, download_data
from other_pages.notionapi import get_block_content

class class_notes_Class:
    def __init__(self):
        
        self.page_config = {'page_title': "Revision",
                            'page_icon':'☔',
                            'layout':'wide'}
        self.page_dict = {
            'all':self.all_classes
        }
        self.current_page = 'all'

        self._link_input_sheetname = "hearing-summary"
        self._link_inputdb = None
        self._link_inputdb_refresh = True
        self._link_inputdb_range = f"{self._link_input_sheetname}!A3:F"
        
        self._notesdb = None
        self._notesdb_refresh = True
        self._notesdb_range = 'hearing_notes!A:C'
        
    @property
    def bdvapp(self):
        return st.session_state.get('bdv_app',None)
    
    @property
    def link_input_db(self):
        if self._link_inputdb_refresh:
            data = download_data(6,self._link_inputdb_range)
            data = pd.DataFrame(data[1:],columns=data[0])
            data = data.to_dict(orient='list')
            final_list = [['speaker','URL','row']]
            # iterate over data
            for key,value in data.items():
                column_name = {'SP':"A",
                               'HH RNSM':'B',
                               'HG RSP':'C',
                               'HG Priyagopesh Pr':'D',
                               'Others':'E'}[key]
                list_toadd = [[key,i,f"{self._link_input_sheetname}!{column_name}{_i}"] for _i,i in enumerate(value,start=4) if i!='']
                final_list.extend(list_toadd)
            
            df = pd.DataFrame(final_list[1:],columns=final_list[0])
            self._link_inputdb = df
            return self._link_inputdb
        else:
            return self._link_inputdb
    
    @property
    def notes_db(self):
        if self._notesdb_refresh:
            data = download_data(7,self._notesdb_range)
            data = pd.DataFrame(data[1:],columns=data[0])
            metadata = dict(zip(data['key'],data['value']))
            if len(data.query("data !=''"))==0:
                data = []
            else:
                data = [json.loads(d) for d in data['data']]
                final_content_list = [['speaker','class','heading','content','views','URL']]
                for asample in reversed(data):
                    block = asample['block_data']
                    collected = [asample['speaker'],
                                 block['class_title'],
                                 block['heading'],
                                 block['content'],
                                 asample['view_count'],
                                 block['URL']]
                    final_content_list.append(collected)
                data = pd.DataFrame(final_content_list[1:],columns=final_content_list[0])
            self._notesdb = {'data':data,'append_range':metadata['add_here']}
            return self._notesdb
        else:
            return self._notesdb
    
    def write_summary(self,notion_dict,index=None):
        """
        """
        class_name = notion_dict['class_title']
        heading = notion_dict['heading']
        contents = notion_dict['content']
        url = notion_dict['URL']
        if index:
            st.markdown(f"##### :orange[{heading}-[{index}]]")
        else:
            st.markdown(f"##### :orange[{heading}]")

        all_lines = contents.split('\n')
        for oneline in all_lines:
            st.markdown(f" {oneline}")
        st.caption(f"from class [{class_name}]({url})")

    def all_classes(self):
        st.header("Lecture notes revision")       
        def mark_noted_1st_time(block_content_dict,erase_range,speaker):
            # upload
            upload_range = self.notes_db['append_range']
            data2upload = {'block_data':block_content_dict,
                           'view_count':1,
                           'speaker':speaker}
            upload_data_json = json.dumps(data2upload)
            upload_data(7,upload_range,[[upload_data_json]])
            self._notesdb_refresh=True
            # erase link
            upload_data(6,erase_range,[['']])
        st.image("https://i.pinimg.com/736x/76/ae/bd/76aebd8959a94f39dcb2a8dac8658ec2.jpg",
                 width=500)
        with st.expander("Unseen Points",expanded=True):
            unseendb = self.link_input_db
            for index,item in unseendb.iterrows():
                left,right = st.columns([4,1])
                with left:
                    _contents = get_block_content(item['URL'])
                    self.write_summary(_contents)
                with right:
                    st.button("Mark seen",key=f'seenbutton{index}',
                              on_click=mark_noted_1st_time,args=[_contents,item['row'],item['speaker']])
                st.divider()

        st.divider()
        notesdf = self.notes_db['data']
        for index,item in notesdf.iterrows():
            self.write_summary({'class_title':item['class'],
                                **item})
            st.divider()


    def run(self):
        self.page_dict[self.current_page]()