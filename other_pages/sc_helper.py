import pandas as pd
import streamlit as st

from other_pages.googleapi import download_data



def get_standard(groupname):
    # if f'standard_{groupname}'  in st.session_state:
    # st.session_state.pop(f'standard_{groupname}')
    if f'standard_{groupname}' not in st.session_state:
        raw_array = download_data(db_id=2,
        range_name=f'standard_{groupname}')

        alldf  = pd.DataFrame(raw_array[1:],columns=raw_array[0])
        alldf.dropna(inplace=True)

        standard = {}

        # wakeup
        temp = alldf[alldf['filter']=='wakeup']
        temp = temp.astype({'index':int,'value':int,'Marks':int})
        temp.sort_values(by='index',inplace=True)
        temp.reset_index(inplace=True,drop=True)
        temp.reset_index(inplace=True,drop=True)
        standard['wakeup'] = temp.copy()
        del temp

        # SA
        temp = alldf[alldf['filter']=='sa']
        temp = temp.astype({'index':int,'value':str,'Marks':int})
        temp.sort_values(by='index',inplace=True)        
        standard['sa'] = dict(zip(temp['value'],temp['Marks']))        
        del temp
        
        # MC
        temp = alldf[alldf['filter']=='mc']
        temp = temp.astype({'index':int,'value':str,'Marks':int})
        temp.sort_values(by='index',inplace=True)
        standard['mc'] = dict(zip(temp['value'],temp['Marks']))
        del temp
       
        # Ma
        temp = alldf[alldf['filter']=='ma']
        temp = temp.astype({'index':int,'value':str,'Marks':int})
        temp.sort_values(by='index',inplace=True)
        standard['ma'] = dict(zip(temp['value'],temp['Marks']))
        del temp

        # chanting
        temp = alldf[alldf['filter']=='chant']
        temp = temp.astype({'index':int,'value':int,'Marks':int})
        temp.sort_values(by='index',inplace=True)
        temp.reset_index(inplace=True,drop=True)
        temp.reset_index(inplace=True,drop=True)
        standard['chant'] = temp.copy()
        del temp
        
        if groupname =='nak':
            temp = alldf[alldf['filter']=='college']
            temp = temp.astype({'index':int,'value':str,'Marks':int})
            temp.sort_values(by='index',inplace=True)
            standard['college'] = dict(zip(temp['value'],temp['Marks']))
            del temp
        
        # dayrest
        temp = alldf[alldf['filter']=='dayrest']
        temp = temp.astype({'index':int,'value':int,'Marks':int})
        temp.sort_values(by='index',inplace=True)
        temp.reset_index(inplace=True,drop=True)
        temp.reset_index(inplace=True,drop=True)
        standard['dayrest'] = temp.copy()
        del temp

        # shayan kirtan
        temp = alldf[alldf['filter']=='sk']
        temp = temp.astype({'index':int,'value':str,'Marks':int})
        temp.sort_values(by='index',inplace=True)
        standard['sk'] = dict(zip(temp['value'],temp['Marks']))
        del temp

        # targets
        temp = alldf[alldf['filter']=='targets']
        temp = temp.astype({'index':str,'value':int,'Marks':int})
        temp.reset_index(inplace=True,drop=True)
        standard['targets'] = temp.copy()
        del temp                      

        # dayrest
        temp = alldf[alldf['filter']=='tobed']
        temp = temp.astype({'index':int,'value':int,'Marks':int})
        temp.sort_values(by='index',inplace=True)
        temp.reset_index(inplace=True,drop=True)
        temp.reset_index(inplace=True,drop=True)
        standard['tobed'] = temp.copy()
        del temp
        st.session_state[f'standard_{groupname}'] = standard
            
    return st.session_state[f"standard_{groupname}"]




def get_scores(group,card):
    standard = get_standard(group)

    score = pd.DataFrame()
    score['date'] = [d.strftime('%d %b %a') for d in card['date']]

    # wakeup
    def _wakeup(value):
        value = int(value)
        for i in range(len(standard['wakeup'])):
            if value< standard['wakeup'].loc[i,'value']:
                return standard['wakeup'].loc[i,'Marks']
        return -1

    score['wakeup'] = card['wakeup'].apply(lambda x: _wakeup(x))
    
    score['SA'] = card['SA'].apply(lambda x: standard['sa'][x])
    score['MC'] = card['MC'].apply(lambda x: standard['mc'][x])
    score['MA'] = card['MA'].apply(lambda x: standard['ma'][x])

    def _chant(value):
        value = int(value)
        for i in range(len(standard['chant'])):
            if value< standard['chant'].loc[i,'value']:
                return standard['chant'].loc[i,'Marks']
        return -1
    score['chant'] = card['chant'].apply(lambda x: _chant(x))
    score['Reading'] = card['Reading'].apply(lambda x: int(x))
    score['SP'] = card['Hearing_SP'].apply(lambda x: int(x))
    score['HHRNSM'] = card['Hearing_HHRNSM'].apply(lambda x: int(x))    
    score['HGRSP'] = card['Hearing_RSP'].apply(lambda x: int(x))    
    score['Councellor'] = card['Hearing_Councellor'].apply(lambda x: int(x))
    
    
    score['verse'] = card['verse'].apply(lambda x: int(x) if x !='-' else 0)

    if group =='nak':
        score['college'] = card['college'].apply(lambda x: standard['college'][x])
        score['study'] = card['self_study'].apply(lambda x: int(x))
    
    def _dayrest(query):
        value = int(query)
        for i in range(len(standard['dayrest'])):
            if value < standard['dayrest'].loc[i,'value']:
                return standard['dayrest'].loc[i,'Marks']
        return -1
    score['dayrest'] = card['dayrest'].apply(lambda x: _dayrest(x))
    score['SK'] = card['shayan_kirtan'].apply(lambda x: standard['sk'][x])
    def _tobed(query):
        value = int(query)
        for i in range(len(standard['tobed'])):
            if value < standard['tobed'].loc[i,'value']:
                return standard['tobed'].loc[i,'Marks']
        return -1
    
    score['tobed'] = card['tobed'].apply(lambda x: _tobed(x))
    # st.dataframe(score)
    # st.write(standard['ma'])
    return score