import streamlit as st
import datetime

from other_pages.googleapi import download_data
from other_pages.googleapi import upload_data
from other_pages.googleapi import append_data
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
                "SC_CARD_INFO" : "!U:AN",
                "FIELD_ORDER": ['date','wakeup','SA','MC','MA','chant','Reading','book',
                                'Hearing_SP','Hearing_HHRNSM','Hearing_RSP','Hearing_Councellor',
                                'verse','college','self_study','seva','dayrest','shayan_kirtan','tobed'
                                ]
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
        current_week.append(weekday.strftime('%d/%m/%Y'))
    
    return current_week

def list2def(rawdata):
    df = {}
    for col in rawdata:
        df[col[0]] = col[1:]
    df = pd.DataFrame(df)
    return df
# ======================== some functions end


# ==================== Daily Filling page
def show_daily_filling():

    # get the database of user
    devotee = st.session_state['user']
    if 'sc_filled_info' not in st.session_state:
        try:
            st.session_state['sc_filled_info'] = download_data(db_id=2,
                    range_name=f"{devotee['name']}{scdict[devotee['group']]['SC_CARD_INFO']}",
                    major_dimention='COLUMNS')
        except :
            st.error("could not download sadhana card")
    
    try :
        my_sc_dates = st.session_state['sc_filled_info'][0]
    except IndexError:
        st.error("HK Prji, please contact to create your sadhana card")
        st.markdown("[Ask to create](http://wa.me/917260869161?text=Hare%20Krishna%20Pr%20Please%20create%20my%20sadhana%20card%20sheet)")
        st.button("Feed",on_click=change_page,args=['feed'])
        return -1
    last_week_SC = list2def(st.session_state['sc_filled_info'][1:])



    st.markdown("<div id='linkto_top'></div>", unsafe_allow_html=True)
    st.markdown('## Hare Krishna' )
    st.markdown(f"### :green[{devotee['name']} Pr]")  
    if devotee['name'] =='guest':
        st.button('Main Menu',on_click=change_page,args=['feed'])
    


    
      

    # ------------------Sadhana Card
    st.markdown("---")
    if 'filling_date' not in st.session_state:
        st.session_state['filling_date'] = datetime.datetime.today()
    
    aajkadin = st.session_state['filling_date']
    current_week = get_current_week(aajkadin)
    current_week_status = {}
    pending_days = []
    for day in current_week:
        if day in my_sc_dates:
            d = datetime.datetime.strptime(day,'%d/%m/%Y')
            current_week_status[d.strftime('%d %b %a')] = 'filled'
        else :
            d = datetime.datetime.strptime(day,'%d/%m/%Y')
            current_week_status[d.strftime('%d %b %a')] = 'pending'
            if d <= datetime.datetime.today():
                pending_days.append(d)
    

    left,middle,right = st.columns(3)
    left.write(':green[filled]')
    middle.write(':red[pending]')
    for day in current_week_status.keys():
        if current_week_status[day] =='filled':
            left.write(f':green[{day}]')
        else:
            assert current_week_status[day] =='pending'
            middle.write(f':red[{day}]')    

    filldate_string = right.radio("hari",options=pending_days,
    label_visibility='hidden',
    format_func=lambda x: x.strftime('%d %b %a'))
    
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
    fill = {}
    try:
        filldate = datetime.date(year=filldate_string.year,
                                month=filldate_string.month,
                                day=filldate_string.day).strftime("%d %b %a")

        fill['date'] = filldate
    except :
        fill['date'] = '-'
        st.success('all day filled')
    st.markdown(f"#### filling for :violet[{fill['date']}]")

    with st.expander("Morning Program",expanded=False):
        wakeup = st.number_input(":green[Wake Up] 🌞",value=340,
        help=""":blue[please write in 24 hour format without any delimiter]
                :violet[345 for 3:45am]""",step=1)
        st.caption(f':blue[wake up at {convert_time(wakeup)[1]}]')
        if convert_time(wakeup)[0] !=-1:
            fill['wakeup'] = convert_time(wakeup)[2]
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
            fill['chant'] = convert_time(chant)[2]
        else:
            fill['chant'] = '-'


    # ---------------Reading and Hearing
    with st.expander("Sadhana 🔥",expanded=False):
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
        fill['tobed'] = convert_time(tobed)[2]
    else:
        fill['tobed'] = '-'

    def submit(datasubmit):
       
        write_range = f"{devotee['name']}{scdict[devotee['group']]['APPEND_RANGE']}"
        write_value = []
        for field in scdict[devotee['group']]['FIELD_ORDER']:
            write_value.append(datasubmit[field])
        
        response = append_data(db_id=2,range_name=write_range,value=[write_value],
                                input_type='USER_ENTERED')        
        if response:
            st.session_state['message'] = f":green[filled Successfully!!] for :violet[{datasubmit['date']}]"
            st.session_state.pop('sc_filled_info')
        # except :
        #     st.error('could not upload scores')
    if fill['date'] !='-':
        submit = st.button('submit 👍',on_click=submit,
                        args=[fill])

    if 'message' in st.session_state:
        st.caption(st.session_state['message'])
        st.session_state.pop('message')
        

    st.markdown("---")
    st.markdown('### :blue[Sadhana Card current status]')

    st.dataframe(last_week_SC)
    st.markdown("<a href='#linkto_top'>Link to top</a>", unsafe_allow_html=True)
    st.markdown('---')
    st.markdown("### Other pages")
    left,right = st.columns(2)
    # left.button("Dashboard",on_click=change_subpage,args=['dashboard'])
    right.button("Feed",on_click=change_page,args=['feed'])

def show_sc_dashboard():
    if 'scfilling' not in st.session_state:
        # query_raw = fetch_data_forced(st.secrets['db_sadhana']['sheetID'],
        #                             'summary!B5:J19',major_dimention='COLUMNS')
        query_raw = download_data(db_id=2,range_name=FILLING_SUMMARY,
                        major_dimention='COLUMNS')
        filling_info = {}
        for devotee in query_raw:
            filling_info[devotee[0]] = devotee[1:]
        st.session_state['scfilling'] = filling_info
            
    scfillinginfo = st.session_state['scfilling']
    # ------This week
    st.header(":blue[Sadhana Card Dashboard]")        
    st.markdown("### :violet[Daily Filling Status]")
    st.markdown(':violet[current Week]')

    aajkadin = datetime.datetime.today()
    last_monday = aajkadin - datetime.timedelta(days=aajkadin.weekday())
    last_week = get_current_week(aajkadin)

    current_week_table = pd.DataFrame(last_week,columns=['dates_raw'])
    current_week_table['date'] = pd.to_datetime(current_week_table['dates_raw'],format='%d/%m/%Y')
    current_week_table['date'] = current_week_table['date'].apply(lambda x:x.strftime('%b %d %a'))
    

    def daily_status(name,day):
        if day in scfillinginfo[name]:
            return 'filled'
        else :
            return '-'
    
    for devotee in scfillinginfo:
        current_week_table[f'{devotee} Pr'] = [daily_status(devotee,d) for d in current_week_table['dates_raw']]
        
    st.dataframe(current_week_table.drop(columns=['dates_raw']).copy())

    def refresh_week():
        st.session_state.pop('scfilling')

    st.button("Refresh Week",on_click=refresh_week)
    st.markdown('---')
    # ------------------ last week
    st.markdown(':violet[Previous Week]')
    aajkadin = datetime.datetime.today() - datetime.timedelta(days=7)
    last_monday = aajkadin - datetime.timedelta(days=aajkadin.weekday())
    last_week = []
    for i in range(7):
        weekday = last_monday + datetime.timedelta(days=i)
        last_week.append(weekday.strftime('%d/%m/%Y'))

    current_week_table = pd.DataFrame(last_week,columns=['dates_raw'])
    current_week_table['date'] = pd.to_datetime(current_week_table['dates_raw'],format='%d/%m/%Y')
    current_week_table['date'] = current_week_table['date'].apply(lambda x:x.strftime('%b %d %a'))
    def daily_status(name,day):
        if day in scfillinginfo[name]:
            return 'filled'
        else :
            return '-'
    for devotee in scfillinginfo:
        current_week_table[f'{devotee} Pr'] = [daily_status(devotee,d) for d in current_week_table['dates_raw']]
        
    st.dataframe(current_week_table.drop(columns=['dates_raw']))


    st.markdown('---')

    st.button('Fill today',on_click=change_subpage,args=['show_page'])


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