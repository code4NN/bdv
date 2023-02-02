import pandas as pd
import streamlit as st

from other_pages.googleapi import download_data

standard_range = {'nak': "standards!B3:E90"}


def get_standard(groupname):
    # if True:
    if f'standard_{groupname}' not in st.session_state:
        raw_array = download_data(db_id=2,
        range_name=standard_range[groupname])

        alldf  = pd.DataFrame(raw_array[1:],columns=raw_array[0])
        alldf.dropna(inplace=True)

        standard = {}
        max_score = {}

        # wakeup
        temp = alldf[alldf['filter']=='wakeup']
        temp = temp.astype({'index':int,'value':int,'Marks':int})
        temp.sort_values(by='index',inplace=True)
        temp.reset_index(inplace=True,drop=True)

        standard['wakeup'] = temp.copy()
        max_score['wakeup'] = temp['Marks'].max()

        # SA
        temp = alldf[alldf['filter']=='sa']
        temp = temp.astype({'index':int,'value':str,'Marks':int})
        temp.sort_values(by='index',inplace=True)        
        standard['sa'] = dict(zip(temp['value'],temp['Marks']))        
        max_score['sa'] = temp['Marks'].max()
        
        # MC
        temp = alldf[alldf['filter']=='mc']
        temp = temp.astype({'index':int,'value':str,'Marks':int})
        temp.sort_values(by='index',inplace=True)
        standard['mc'] = dict(zip(temp['value'],temp['Marks']))
        max_score['mc'] = temp['Marks'].max()

        # Ma
        temp = alldf[alldf['filter']=='ma']
        temp = temp.astype({'index':int,'value':str,'Marks':int})
        temp.sort_values(by='index',inplace=True)
        standard['ma'] = dict(zip(temp['value'],temp['Marks']))
        max_score['ma'] = temp['Marks'].max()


        # chanting
        temp = alldf[alldf['filter']=='chant']
        temp = temp.astype({'index':int,'value':int,'Marks':int})
        temp.sort_values(by='index',inplace=True)
        temp.reset_index(inplace=True,drop=True)

        standard['chant'] = temp.copy()
        max_score['chant'] = temp['Marks'].max()
        
        if 'college' in alldf['filter'].tolist():
            temp = alldf[alldf['filter']=='college']
            temp = temp.astype({'index':int,'value':str,'Marks':int})
            temp.sort_values(by='index',inplace=True)

            standard['college'] = dict(zip(temp['value'],temp['Marks']))
            max_score['college'] = temp['Marks'].max()
        
        # dayrest
        temp = alldf[alldf['filter']=='dayrest']
        temp = temp.astype({'index':int,'value':int,'Marks':int})
        temp.sort_values(by='index',inplace=True)
        temp.reset_index(inplace=True,drop=True)
        
        standard['dayrest'] = temp.copy()
        max_score['dayrest'] = temp['Marks'].max()

        # shayan kirtan
        temp = alldf[alldf['filter']=='sk']
        temp = temp.astype({'index':int,'value':str,'Marks':int})
        temp.sort_values(by='index',inplace=True)

        standard['sk'] = dict(zip(temp['value'],temp['Marks']))
        max_score['sk'] = temp['Marks'].max()

        # targets
        temp = alldf[alldf['filter']=='targets']
        temp = temp.astype({'index':str,'value':int,'Marks':int})        
        temp.reset_index(inplace=True,drop=True)

        standard['targets'] = temp.copy()          
        
        for i in range(len(temp)):
            max_score[temp.loc[i,'index']] = temp.loc[i,'Marks']

        # tobed
        temp = alldf[alldf['filter']=='tobed']
        temp = temp.astype({'index':int,'value':int,'Marks':int})
        temp.sort_values(by='index',inplace=True)
        temp.reset_index(inplace=True,drop=True)

        standard['tobed'] = temp.copy()
        max_score['tobed'] = temp['Marks'].max()

        standard['max'] = max_score
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
    score['Other'] = card['Hearing_Other'].apply(lambda x: int(x))

    councellor_hearing = 0
    if 'Hearing_Councellor' in card.columns.tolist():
        score['Councellor'] = card['Hearing_Councellor'].apply(lambda x: int(x))
        councellor_hearing = score['Councellor'].sum()
    
    
    score['verse'] = card['verse'].apply(lambda x: int(x) if x !='-' else 0)

    if 'college' in card.columns.tolist():
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
    
    # calculating body soul study
    
    # SOUL
    # sa, mc, ma Chanting
    maxscore = standard['max']

    mpscore = score['SA'].sum() + score['MC'].sum() + score['MA'].sum()    
    chantscore = score['chant'].sum()


    # hearing
    # Reading 
    target_zip = {}
    for i in range(len(standard['targets'])):
        target_zip[standard['targets'].iloc[i,1]] = standard['targets'].iloc[i,2:].tolist()
        # value with index 1 is total marks
        # value with index 0 is total target in minute of #count
    readingscore = score['Reading'].sum() * (target_zip['Reading'][1]/target_zip['Reading'][0])

    hearingscore = (score['SP'].sum() * (target_zip['hear_SP'][1]/target_zip['hear_SP'][0])) + \
    (score['HHRNSM'].sum() * (target_zip['hear_HHRNSM'][1]/target_zip['hear_HHRNSM'][0])) + \
    (score['HGRSP'].sum() * (target_zip['hear_HGRSP'][1]/target_zip['hear_HGRSP'][0]))

    if 'Councellor' in score.columns.tolist():
        councellorscore = score['Councellor'].sum()* (target_zip['hear_Councellor'][1]/target_zip['hear_Councellor'][0])
        hearingscore += councellorscore
    
    shlokascore = (target_zip['shloka'][1]/target_zip['shloka'][0])* score['verse'].sum()

    hearingscore = min(hearingscore, target_zip['hear_SP'][1] + target_zip['hear_HHRNSM'][1] + target_zip['hear_HGRSP'][1] + target_zip['hear_Councellor'][1])
    readingscore = min(readingscore,target_zip['Reading'][1])
    shlokascore = min(shlokascore,target_zip['shloka'][1])
    
    shayanscore = score['SK'].sum()

    soul_percent = (mpscore + chantscore + shayanscore + readingscore + hearingscore + shlokascore)\
                    / (((maxscore['sa'] + maxscore['mc'] + maxscore['ma'])*7) + target_zip['Reading'][1] + target_zip['Hearing'][1]  + target_zip['shloka'][1])
    
    
    # body
    # wakeup, dayrest, tobed
    wakeupscore = score['wakeup'].sum()
    dayrestscore = score['dayrest'].sum()
    tobedscore = score['tobed'].sum()

    body_percent = (wakeupscore + dayrestscore + tobedscore) / (7*(maxscore['wakeup'] + maxscore['dayrest'] + maxscore['tobed']))
    # study, college
    if 'college' in score.columns.tolist():
        studyscore = score['study'].sum()
        collegescore = score['college'].sum()
        study_percent = (studyscore + collegescore) / (target_zip['Study'][1] + (maxscore['college']*7))
    
    # one report
    report = {'body':round(body_percent,2)*100,
               'soul':round(soul_percent,2)*100}
    if 'college' in card.columns.tolist():
        report['study'] = round(study_percent,2)*100
        report['total'] = round((soul_percent + body_percent + study_percent)/3,2)*100
    else:
        report['study'] = 0.0
        report['total'] = (soul_percent + body_percent)/2  

    # another report
    report_score = {"reading":score['Reading'].sum(),
              'hearing': score['HGRSP'].sum() + score['HHRNSM'].sum() + score['SP'].sum() + councellor_hearing + score['Other'].sum(),
              'study': score['study'].sum() if 'college' in card.columns.tolist() else 0
            }

    # and last one
    report3 = {  'wakeup':round(100*wakeupscore/(7*maxscore['wakeup']),0),
                'dayrest':round(100*dayrestscore/(7*maxscore['dayrest']),0),
                  'tobed':round(100*tobedscore/(7*maxscore['tobed']),0),
                  'chant':round(100*chantscore/(7*maxscore['chant']),0)
               }
    # st.write(report)
    # st.write(report_score)
    # st.write(report3)
    # st.write(hearingscore,target_zip['Hearing'])
    report4 = {'reading':[score['Reading'].sum(),min(1,readingscore/target_zip['Reading'][1]),target_zip['Reading'][0]],
                'hearing':[councellor_hearing + score['HGRSP'].sum() + score['HHRNSM'].sum() + score['Other'].sum() + score['SP'].sum()
                ,min(1,hearingscore/target_zip['Hearing'][1]),target_zip['Hearing'][0]]}

    return {"table":score,                                               
            'report1': report,
            'report2': report_score,
            'report3': report3,
            'report4':report4,
            'ndays': len(score)
            }



# -------------
def gradient(t):
    r = int(255 * (1 - t))
    g = int(255 * t)
    b = 0
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def get_progressbar(status):
    html = f"""
<div style="width: 100%; height: 20px; background-color: #ddd;">
  <div id="progress-bar" style="width: {status*100}%; height: 100%; background-color: {gradient(status)};">
  </div>
</div>
"""
    return html