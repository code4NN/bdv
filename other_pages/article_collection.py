import streamlit as st
import json
import pandas as pd
import openpyxl

from other_pages.googleapi import download_data
from other_pages.googleapi import upload_data

# ============= some variables
TAGGING_DATABASE = 'working_database!A:P'

UPLOAD_TAGS_RANGE = 'working_database!'
UPLOAD_TAG_BEGIN_COLUMN = 4
# ============= some variables end


## ----------- call back functions
def change_page(state,substate='default'):
    st.session_state['state'] = state
    st.session_state['substate'] = substate

def change_subpage(subpage):
    st.session_state['substate'] = subpage

## -------------

def home():

    if 'database' not in st.session_state.article_collection:
        array = download_data(db_id=3,range_name=TAGGING_DATABASE)
        df = pd.DataFrame(array[1:],columns=array[0])
        
        df.query("status == 'TRUE' ",inplace=True)
        
        # create our search data frame
        # columns = ['URL','Issue','Title','Author','Source']
        # make changes accordingly
        search_df_array = []
        # Iterate over one issue
        for _,row in df.iterrows():
            rowdf = row.to_frame(name='item').reset_index().query(" item != '' ")
            article_URL = rowdf.loc[rowdf['index']=='URL','item'].values[0]
            article_ISSUE = rowdf.loc[rowdf['index']=='ID','item'].values[0]
            
            # Iterate over available articles of one issue
            for _,one_article in rowdf.query(" `index`.str.contains('Article')").iterrows():
                thissample = [article_URL,article_ISSUE]
                article_dict = json.loads(one_article.loc['item'])
                thissample.append(article_dict['Title'])
                thissample.append(article_dict['Author'])
                thissample.append(article_dict['Source'])
                search_df_array.append(thissample)
        search_df = pd.DataFrame(search_df_array,columns=['URL','Issue','Title','Author','Source'])

        st.session_state['article_collection']['database'] = search_df

    database = st.session_state.article_collection['database']
    st.header(":green[Get the right article]")
    
    # st.write(st.session_state)
    if "search++" in st.session_state.user['roles']:
        st.button("Contribute",on_click=change_subpage,args=['tagging_activity'])

    ## some algorithm to filter the data based on query
    searchinput,searchbutton = st.columns([4,1])
    searchinput.text_input("Enter Text For searching")
    searchbutton.markdown("")
    searchbutton.markdown("")
    # searchbutton.button("🔍")

    ## some algorithm ends
    filtereddf = database.copy()
    
    col_title,col_author,col_goto = st.columns([3,2,1])
    col_title.markdown("### :green[Title]")
    col_author.markdown("### :green[Author]")
    col_goto.markdown("### :green[link]")
    
    for _,row in filtereddf.iterrows():
        col_title.markdown(row.loc['Title'])
        col_author.markdown(row.loc['Author'])
        col_goto.markdown(f"[ go to ]({row.loc['URL']})")

    st.markdown('---')
    st.button('home',key='home',on_click=change_page,args=['feed','default'])





def tagging_activity():
    st.session_state['LAYOUT'] = 'wide'
    def refresh():
        st.session_state.article_collection.pop('edit_database')
    if 'edit_database' not in st.session_state.article_collection:
        dataarray = download_data(db_id=3,range_name=TAGGING_DATABASE)
        dataframe = pd.DataFrame(dataarray[1:],columns=dataarray[0])
        dataframe.query("status =='FALSE' ",inplace=True)
        
        st.session_state.article_collection['row2edit'] = 1
        st.session_state.article_collection['edit_database'] = dataframe
    
    if 'sales_man' not in st.session_state.article_collection:
        st.session_state.article_collection['sales_man'] = [
            {"Author":"Srila Prabhupada",
             "Title":'',
             "Source":'',
             "Raw_Text":""},
            {"Author":"BSST",
             "Title":'',
             "Source":'',
             "Raw_Text":""},
            {"Author":"Gour Govinda Swami Maharaja",
             "Title":'',
             "Source":'',
             "Raw_Text":""}
             ]
    
    st.header(":green[Welcome to the Article Tagging zone]")
    database = st.session_state.article_collection['edit_database']
    left,right = st.columns(2)
    left.button("🔁",on_click=refresh)
    right.button("Go to Dashboard",on_click=change_subpage,args=['default'])

    st.dataframe(database.head())

    # get the not-done list
    not_done_db = database.query("status =='FALSE' ").iloc[0,:]
    # st.dataframe(not_done_db)

    def verify_allowed_characters(text):
        allowed_characters = set(" abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789(){}[]-+_+=|?@!")
        for char in text:
            if char not in allowed_characters:
                return False
        return True
    # display and collect input
    st.markdown("---")
    columns = st.columns(3)
    columns[0].markdown(f":green[Issue - {not_done_db['ID']}]")
    columns[1].markdown(f"[Click to Open]({not_done_db['URL']})")    

    collection_dictionary = []
    valid_inputs = True
    for i,input_dict in enumerate(st.session_state.article_collection['sales_man']):
        aa,bb,cc,ee = st.columns([2,2,2,1])
        ee.markdown("")
        ee.markdown("")
        ee.markdown("")
        current_title = {}
        if input_dict['Author'] :
            aa.text_area(label='Author',value=input_dict['Author'],key=f'tag_info_prefill_{i}_a',
                         disabled=True,height=40
                         )
            current_title['Author'] =input_dict['Author']
        else :
            current_title['Author'] = aa.text_area(label='Author',key=f'tag_info_input_{i}_a',height=40)
        current_title['Title'] = bb.text_area(label='Title',key=f'tag_info_input_{i}_b',height=40)
        current_title['Source'] = cc.text_area(label='Source',key=f'tag_info_input_{i}_c',height=40)
        # current_title['Raw_Text'] = dd.text_input(label='Text',key=f'tag_info_input_{i}_d')
        current_title['consider'] = ee.checkbox("Done",key=f'tag_info_checkbox_{i}_e')
        # e.markdown("")
        # e.markdown("")
        # e.markdown("")
        if not current_title['Title'].strip() and current_title['consider']:
            valid_inputs = False
            bb.markdown(":red[it is blank]")
            aa.markdown("")
            cc.markdown("")
            # dd.markdown("")
            ee.markdown("")
        # Verification
        if not verify_allowed_characters(current_title['Title']):
            bb.markdown(":red[some invalid character]")
        if not verify_allowed_characters(current_title['Author']):
            bb.markdown(":red[some invalid character]")
        if not verify_allowed_characters(current_title['Source']):
            bb.markdown(":red[some invalid character]")
        collection_dictionary.append(current_title)
    
    def add_new_title(reverse):
        if not reverse:
            st.session_state.article_collection['sales_man'].append(
                {"Author":"",
                "Title":'',
                "Source":'',
                "Raw_Text":""}
            )
        else :
            st.session_state.article_collection['sales_man'].pop()
    
    a,b,c,e = st.columns([2,2,2,1])
    a.button("Add new",key='add_new',on_click=add_new_title,args=[False])
    b.button("Drop last",key='drop_last',on_click=add_new_title,args=[True])
    dict_to_submit = list(filter(lambda x: x['consider'], collection_dictionary))
    # Some processing of dict
    for one_sample in dict_to_submit:
        one_sample['Title'] = one_sample['Title'].strip().lower()
        one_sample['Author'] = one_sample['Author'].strip().title()
    if st.checkbox("Preview what is filled",key='preview_checkbox'):
        st.write(dict_to_submit)
    if valid_inputs:
        def upload_title_tags(tag_dict,upload_row):
            to_upload = ['TRUE']
            for articles in tag_dict:
                to_upload.append(json.dumps(articles))
            try :
                start_column = openpyxl.utils.get_column_letter(UPLOAD_TAG_BEGIN_COLUMN)
                end_column = openpyxl.utils.get_column_letter(UPLOAD_TAG_BEGIN_COLUMN + len(tag_dict))
                if upload_data(db_id=3,
                        range_name=f"{UPLOAD_TAGS_RANGE}{start_column}{upload_row}:{end_column}{upload_row}",
                        value=[to_upload]):
                        st.session_state.article_collection['upload_successful'] = True
                        st.session_state.article_collection.pop('edit_database')
                        for keys in st.session_state:
                            if keys.__contains__("tag_info_input_"):
                                st.session_state[keys] = ""
            
            
            except Exception as e:
                if st.session_state.DEBUG_ERROR:
                    st.write(e)
                else:
                    st.session_state.article_collection['upload_successful'] = False
            
            
        c.button("Upload this 👍",on_click=upload_title_tags,
                 args=[dict_to_submit,not_done_db.loc['row_number']],key='upload_button')
        
        if 'upload_successful' in st.session_state.article_collection:
            if st.session_state.article_collection['upload_successful']:
                d.success('Success!!!!')
                st.session_state.article_collection.pop('upload_successful')
            else :
                d.error('Some error!!!!')
                st.session_state.article_collection.pop('upload_successful')

    # st.write(st.session_state)
# ---------------------- Wrapper
pagestate_map = {
    'default':home,
    'tagging_activity':tagging_activity
}

def get_article_main():
    if 'article_collection' not in st.session_state:
        st.session_state['article_collection'] = {}

    if 'substate' not in st.session_state:
        # default behaviour
        home()

    elif st.session_state['substate'] in pagestate_map.keys():
        # directed behaviour
        pagestate_map[st.session_state['substate']]()
    else:
        # exceptional
        pass 