import streamlit as st
import datetime

from other_pages.googleapi import download_data
from other_pages.googleapi import download_data_in_batch
from other_pages.googleapi import upload_data
from other_pages.googleapi import append_data

import other_pages.sc_helper as scutils
import pandas as pd
import json

# ------------------------ some Constants
scdict = {'yud':
                {"APPEND_RANGE": "!A:R",
                "SC_CARD_INFO" : "!U:AM",
                "FIELD_ORDER": ['date','wakeup','SA','MC','MA','chant','Reading','book',
                                'Hearing_SP','Hearing_HHRNSM','Hearing_RSP','Hearing_Councellor',
                                'verse','company','seva','dayrest','shayan_kirtan','tobed'
                                ]
                },
          'bhim':
                {"APPEND_RANGE": "!A:S",
                "SC_CARD_INFO" : "!U:AN",
                "FIELD_ORDER": ['date','wakeup','SA','MC','MA','chant','Reading','book',
                                'Hearing_SP','Hearing_HHRNSM','Hearing_RSP','Hearing_Councellor',
                                'verse','college','self_study','seva','dayrest','shayan_kirtan','tobed'
                                ]
                },
          'nak':
                {"APPEND_RANGE": "!A:S",
                "SC_CARD_INFO" : "!V:AO",
                "FIELD_ORDER": {'date':object,'wakeup':int,'SA':str,'MC':str,'MA':str,'chant':int,'Reading':int,'book':str,
                                'Hearing_SP':int,'Hearing_HHRNSM':int,'Hearing_RSP':int,'Hearing_Councellor':int,
                                'verse':str,'college':str,'self_study':int,'seva':int,'dayrest':int,'shayan_kirtan':str,'tobed':int
                                },
                }
        }

# ------------------------ some Constants end

# ======================== some functions
def change_page(state,substate='default'):
    st.session_state['state'] = state
    st.session_state['substate'] = substate

def change_subpage(subpage):
    st.session_state['substate'] = subpage
    
def convert_time(timestr):
    hourdigit = -1

    # try to convert to number
    try :
        timestr = int(timestr)
    except:
        return (-1,"please write 24h format like :blue[21.30]")

    if 0<=timestr<=59:
        hourdigit=0
    elif 100<=timestr<=959:
        hourdigit =1
    else:
        hourdigit =2
    timestr = str(timestr)
    if hourdigit!=0:
        timestr = f'{timestr[:hourdigit]}.{timestr[hourdigit:]}'
    else:
        timestr = f'0.{timestr}'


    if timestr =="":
        return (-1,"please write 24h format like :blue[21.30]")
    elif '.' in timestr:                        

        hh,mm = timestr.split(".")
        try:
            standardtime = datetime.time(hour=int(hh),minute=int(mm)).strftime('%H:%M %p')
            timeforsheet = datetime.time(hour=int(hh),minute=int(mm)).strftime('%H:%M')
                
            return (1,f' :violet[{standardtime}]',timeforsheet)
        except:
            return (-1,"😔 :blue[Pr, could not convert]")
    else :
        return (-1,'wrong time input')

def get_current_week(aajkadin):
    last_monday = aajkadin - datetime.timedelta(days=aajkadin.weekday())
    current_week = []
    for i in range(7):
        weekday = last_monday + datetime.timedelta(days=i)
        current_week.append(weekday.strftime("%d/%m/%Y"))
    
    return current_week

def process_filled_sadhana_card(rawdata,datatypedict):
    """
    rawdata: the two d array 
    datatypedict: for converting columns to teheir type
    
    returns pandas dataframe
    """
    df_my_sadhana_card = None
    if len(rawdata) ==1 :
                df_my_sadhana_card = pd.DataFrame(columns=rawdata[0])
    else :
        df_my_sadhana_card = pd.DataFrame(rawdata[1:],columns=rawdata[0])

    dtype_dict = {**datatypedict,'dbindex':int}

    df_my_sadhana_card = df_my_sadhana_card.astype(dtype_dict)

    df_my_sadhana_card['date'] = pd.to_datetime(df_my_sadhana_card['date'], format="%d/%m/%Y")
    df_my_sadhana_card['strdate'] = df_my_sadhana_card['date'].apply(lambda x: x.strftime("%d/%m/%Y"))

    return df_my_sadhana_card
# ======================== some functions end


# ==================== Daily Filling page
def show_daily_filling():

    # get the database of user
    devotee = st.session_state['user']
    if 'sc_filled_info' not in st.session_state:
        try:
            rawdata = download_data(db_id=2,
                    range_name=f"{devotee['name']}{scdict[devotee['group']]['SC_CARD_INFO']}")
            st.session_state['sc_filled_info'] = process_filled_sadhana_card(rawdata,
            datatypedict=scdict[devotee['group']]['FIELD_ORDER'])
        except Exception as e:
            st.error("could not download sadhana card")
            show = st.checkbox('Show errors')
            if show:
                st.write(e)
    
    
    df_my_sadhana_card = st.session_state['sc_filled_info']    



    st.markdown("<div id='linkto_top'></div>", unsafe_allow_html=True)
    st.markdown('## Hare Krishna' )
    st.markdown(f"### :green[{devotee['name']} Pr]")

    if devotee['name'] =='guest':
        st.button('Main Menu',on_click=change_page,args=['feed'])
    


    
      

    # ------------------Sadhana Card
    
    # set the reference day to decide which week to fill
    st.markdown("---")
    if 'filling_date' not in st.session_state:
        st.session_state['filling_date'] = datetime.datetime.today()
    
    aajkadin = st.session_state['filling_date']

    # get the current week
    # also next
    # get the current week status for each day. Filled or pending    
    current_week = get_current_week(aajkadin)
    current_week_status = {}
    pending_days = []
    completed_days = []

    for day in current_week:
        if day in df_my_sadhana_card['strdate'].tolist():
            d = datetime.datetime.strptime(day,'%d/%m/%Y')
            current_week_status[d.strftime('%d %b %a')] = 'filled'
            completed_days.append(d)
        else :
            d = datetime.datetime.strptime(day,'%d/%m/%Y')
            current_week_status[d.strftime('%d %b %a')] = 'pending'
            # if day <= datetime.datetime.today():
            pending_days.append(d)
    
    
    # Two take aways
    # current_week_status = {string: either 'filled' or 'pending'} fixed length 7
    # pending_days [date object] variable length 0 - 7
    # completed_days [date object] variable length 0 - 7

    # draw the canvass
    filltype  = st.radio("choice",options=['fill','refill'],index=0,key='filloption',horizontal=True)
    
    left,middle,right = st.columns(3)
    left.write(':green[FILLED]')
    middle.write(':red[PENDING]')

    # display the status of filled and pending 
    # uses current_week_status (dict)
    for day in current_week_status.keys():
        if current_week_status[day] =='filled':
            left.write(f':green[{day}]')
        else:
            assert current_week_status[day] =='pending'
            middle.write(f':red[{day}]')    

    # choose a date to fill / edit

    #
    sc_fill_date_option = None
    if filltype =='fill':
        sc_fill_date_option = [pending_days,':blue[date to :orange[FILL]]']
    else :
        assert filltype =='refill'
        sc_fill_date_option  = [completed_days,':blue[date to :orange[REFILL]]']
    
    date_choose_option = False
    if len(sc_fill_date_option[0]) >0:
        selected_filldate = right.radio(
            label=sc_fill_date_option[1],
        options=sc_fill_date_option[0],
        format_func=lambda x: x.strftime('%d %b %a'))

        date_choose_option = True
    else:
        st.success("No days to select from")

    if filltype =='refill':
        try:
            editrow = df_my_sadhana_card[df_my_sadhana_card.strdate ==selected_filldate.strftime("%d/%m/%Y")].dbindex.tolist()[0]
            refill_begin, refill_end = scdict[devotee['group']]['APPEND_RANGE'].split(":")
            refill_range = f"{devotee['name']}{refill_begin}{editrow}:{refill_end}{editrow}"
        except Exception as e:
            st.error("Some error happened")
            def show_error(e):
                st.write(e)
            st.button("show error",on_click=show_error,args=[e])

    # some UX
    def refresh_filled_dates():
        st.session_state.pop('sc_filled_info')
    def change_week(direction):
        if direction ==-1:
            st.session_state['filling_date'] = st.session_state['filling_date'] - datetime.timedelta(days=7)
        elif direction ==0:
            st.session_state['filling_date'] = datetime.datetime.today()

    middle.button('refresh status',on_click=refresh_filled_dates)
    right.button('previous week',on_click=change_week,args=[-1])
    right.button('Go to today',on_click=change_week,args=[0])
    


    # ----------------------filling begins
    st.markdown('---')
    fill = {'valid':1}

    if date_choose_option:
        fill['date'] = selected_filldate.strftime("%d/%m/%Y")
        fill['show_date'] = selected_filldate.strftime("%d %b %a")
    else :
        fill['valid'] = fill['valid'] * 0    


    if fill['valid'] !=0:
        st.markdown(f"#### filling for :violet[{fill['show_date']}]")

    with st.expander("Morning Program",expanded=False):
        wakeup = st.number_input(":green[Wake Up] 🌞",value=340,
        help=""":blue[please write in 24 hour format without any delimiter]
                :violet[345 for 3:45am]""",step=1)
        st.caption(f':blue[wake up at {convert_time(wakeup)[1]}]')
        if convert_time(wakeup)[0] !=-1:
            fill['wakeup'] = wakeup
        else:
            fill['wakeup'] = "-"

        
        # SA
        fill['SA'] = st.radio(label=":green[SA Attendance]",
                            options=['PP','L0','L1','L2','L3','L4','L5','LL'],
                            index=7,
                            horizontal=True)
        st.markdown("")

        # MC
        fill['MC'] = st.radio(label=":green[Morning Class]",
                            options=['Full Present','Partially Present','Absent'],
                            index=2,
                            horizontal=True)
        st.markdown("")

        # MA
        fill['MA'] = st.radio(label=":green[Mangal Aarti]",
                            options=['Present','Absent'],
                            index=1,
                            horizontal=True)
        st.markdown("")

        # Chanting
        chant = st.number_input(":green[Chanting] 📿",value=830,
                help=""":blue[please write in 24 hour format]
                        830 for 8:30 am""",step=1)

        st.caption(f':blue[complete japa at {convert_time(chant)[1]}]')
        if convert_time(chant)[0] !=-1:
            fill['chant'] = chant
        else:
            fill['chant'] = '-'


    # ---------------Reading and Hearing
    with st.expander("Sadhana 🔥",expanded=True):
        fill['Reading'] = st.number_input(label=":green[Reading]",
                                            min_value=0,
                                            value=0,
                                            step=30
                                            )
        if fill['Reading'] > 0:
            bookname = st.text_input("Which Book")
            if bookname.strip():
                fill['book'] = bookname
            else:
                fill['book']  = f"-{bookname}"
        else:
            fill['book'] = "-"
        
        st.markdown("#### Hearings")
        fill['Hearing_SP'] = st.number_input(label=":green[Srila Prabhupada]",
                                            min_value=0,
                                            value=0,
                                            step=30
                                            )
                
        fill['Hearing_HHRNSM'] = st.number_input(label=":green[HHRNSM]",
                                            min_value=0,
                                            value=0,
                                            step=30
                                            )
                
        fill['Hearing_RSP'] = st.number_input(label=":green[HG RSP]",
                                            min_value=0,
                                            value=0,
                                            step=30
                                            )
        if st.session_state['user']['group'] not in ['sah']:
            fill['Hearing_Councellor']=st.number_input(label=":green[Councellor Hearing]",
                                                min_value=0,
                                                value=0,
                                                step=30
                                                )
        
        verse = st.radio(label=":green[Shloka]",options=['notdone','done-1','done-2','done-3'],horizontal=True,
        help=""":blue[since marks do not change after 3, so for verse above 3 please fill done-3]""")
        if verse!='notdone':
            verse_number = st.text_input(label=":green[Which one] 😎")
            if verse_number =="":
                fill['verse'] = verse.split('-')[-1]
            else:
                fill['verse'] = f"{verse.split('-')[-1]} : {verse_number}"
        else :
            assert verse == 'notdone'
            fill['verse'] = '-'

    # --------------- College and Studies
    if st.session_state['user']['group'] not in ['yud']:
        fill['college'] = st.radio(label=':green[College Class]',
                                    options=['All Present','Missed 1','Missed 2', 'Missed 2+','no classes'],
                                    index=3,
                                    horizontal=True)
        st.markdown("")

        fill['self_study'] = st.number_input(label=":green[Self Study]",
                                            min_value=0,
                                            value=0,
                                            step=30
                                            )
    else:
        st.markdown("")
        fill['company'] = st.number_input(":orange[Company work (mins)]",
                                           min_value=0,value=540,step=60)
        st.caption(f":blue[:orange[{round((fill['company']/60),1)}] hours of company work]")
        st.markdown("")
    
    fill['seva'] = st.number_input(':green[seva (duration in min)]',min_value=0,step=30,
                    help=":blue[includes IM, Preaching, department seva, adhoc seva]")
    st.markdown("")
    st.markdown("")
    st.markdown("")

    fill['dayrest'] = st.number_input(":green[Day Rest]",
                                        min_value=0,
                                        value=0,
                                        step=30)
    fill['shayan_kirtan'] = st.radio(":green[Shayan Kirtan]",options=['done','notdone'],
                                    index=1,key='sk',horizontal=True)

    tobed = st.number_input(":green[To Bed] 💤",value=2130,
            help=""":blue[please write in 24 hour format]
                    2130 for 9:30 pm""",step=1)
    st.caption(f':blue[took rest at] {convert_time(tobed)[1]}')

    if convert_time(tobed)[0] !=-1:
        fill['tobed'] = tobed
    else:
        fill['tobed'] = '-'







    # submission codes
    def submit(datasubmit,upload_append,refill_range):
       
        if upload_append =='fill':
            write_range = f"{devotee['name']}{scdict[devotee['group']]['APPEND_RANGE']}"
            write_value = []
            for field in scdict[devotee['group']]['FIELD_ORDER'].keys():
                write_value.append(datasubmit[field])
            
            response = append_data(db_id=2,range_name=write_range,value=[write_value])        
            if response:
                st.session_state['message'] = f":green[filled Successfully!!] for :violet[{datasubmit['show_date']}]"
                st.session_state.pop('sc_filled_info')
                
        
        elif upload_append =='refill':
            write_value = []
            for field in scdict[devotee['group']]['FIELD_ORDER'].keys():
                write_value.append(datasubmit[field])
            
            response = upload_data(db_id=2,range_name=refill_range,
            value=[write_value])
            # append_data(db_id=2,range_name=write_range,value=[write_value],
            #                         input_type='USER_ENTERED')        
            if response:
                st.session_state['message'] = f":green[filled Successfully!!] for :violet[{datasubmit['show_date']}]"
                st.session_state.pop('sc_filled_info')
                
        

    
    # if valid then show the submit button
    if fill['valid']!=0:
        if filltype =='fill':
            st.button('submit 👍',on_click=submit,
                        args=[fill,'fill',None])
        elif filltype =='refill':
            st.button('submit 👍',on_click=submit,
                        args=[fill,'refill',refill_range])


    if 'message' in st.session_state:
        st.caption(st.session_state['message'])
        st.session_state.pop('message')        

        



    # score card

    st.markdown("---")
    st.markdown('### :blue[Sadhana Card Various metrices]')

    

    
    current_week_values = df_my_sadhana_card[df_my_sadhana_card.date.isin([*pending_days,*completed_days])].copy()    
    current_week_evaluation = scutils.get_scores(devotee['group'],current_week_values)
    current_week_table = current_week_evaluation['table']
    mytarget = scutils.get_standard(devotee['group'])['targets']
    mytarget = dict(zip(mytarget['index'],mytarget['value']))

    st.markdown(
    """
    <style>
        .stProgress > div > div > div > div {
            background-image: linear-gradient(to right, #FA350B , #8DFA0B);
        }
    </style>""",
    unsafe_allow_html=True,
    )
    
    # Reading status
    reading_completed = current_week_evaluation['reading']
    st.markdown(f':blue[SP Readinga Completed: :orange[{reading_completed} min] Target: :orange[{mytarget["Reading"]} min]]')
    st.progress(float(1) if reading_completed>=mytarget['Reading'] else float(reading_completed/mytarget['Reading']))
    
    # # Hearing status
    hearing_completed = current_week_evaluation['hearing']
    st.markdown(f':blue[Hearing Completed: :orange[{hearing_completed} min] Target: :orange[{mytarget["Hearing"]} min]]')
    st.progress(float(1) if hearing_completed>=mytarget['Hearing'] else float(hearing_completed/mytarget['Hearing']))

    # verse
    verses_completed = current_week_evaluation['verse']
    st.markdown(f':blue[Verse: :orange[{verses_completed}] completed Target: :orange[{mytarget["shloka"]}]]')
    st.progress(float(1) if verses_completed>=mytarget['shloka'] else float(verses_completed/mytarget['shloka']))

    # study
    if current_week_evaluation['study']!= None:
        study_completed = current_week_evaluation['study']
        st.markdown(f':blue[Studies: :orange[{study_completed} min] completed Target: :orange[{mytarget["Study"]} min]]')
        st.progress(float(1) if study_completed>=mytarget['Study'] else float(study_completed/mytarget['Study']))
    

    mysc,mygroup,fillingpage = st.tabs(["my Sadhana card",'All Devotees',"Sadhana Card Report"])

    with mysc:
        current_week_values.drop(columns=['strdate','dbindex'],inplace=True)  
        current_week_values['date'] = [d.strftime('%d %b %a') for d in current_week_values['date']]

        st.dataframe(current_week_values)
        st.dataframe(current_week_table)

    

def show_sc_dashboard():
    return -1

#------------------------------ Wrapper
view_dict= {'default':show_daily_filling,
            'dashboard':show_sc_dashboard}

def sc_main():    
    if 'substate' not in st.session_state:
        # default behaviour
        view_dict['default']()
    else:
        view = st.session_state['substate']
        if view in view_dict.keys():
            # directed behaviour
            view_dict[view]()
        else:
            # exceptional     
            view_dict['default']()