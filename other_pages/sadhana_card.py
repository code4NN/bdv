import streamlit as st
import json
import datetime
import pandas as pd
from other_pages.googleapi import update_range
from other_pages.googleapi import fetch_data_forced

def change_subpage(subpage):
    st.session_state['substate'] = subpage

def convert_time(timestr):
    timestr = str(timestr)
    if timestr =="":
        return (-1,"please write 24h format like :blue[21:30]")
    elif '.' in timestr:                        

        hh,mm = timestr.split(".")
        try:
            standardtime = datetime.time(hour=int(hh),minute=int(mm)).strftime('%H:%M %p')
            return (1,f' :violet[{standardtime}]',standardtime)
        except:
            return (-1,"😔 :blue[Pr, could not convert]")
    else :
        return (-1,'wrong time input')
# ==================== Daily Filling page
def show_daily_filling():

    st.markdown('## Hare Krishna' )
    devotee_name = st.session_state['user']['name']
    st.markdown(f"### :green[{devotee_name} Pr]")    
    if devotee_name =='guest':
        def feed():
            st.session_state['state'] = 'feed'
        st.button('Main Menu',on_click=feed)
    


    
      
    if 'sc_db' not in st.session_state:
        st.session_state['sc_db'] = fetch_data_forced(st.secrets['db_sadhana']['sheetID'],
                                 f'{devotee_name}!S2:S',major_dimention='COLUMNS')[0]
    my_sc_dates = st.session_state['sc_db']

    # ------------------Sadhana Card
    st.markdown("---")
    aajkadin = datetime.datetime.today()
    last_monday = aajkadin - datetime.timedelta(days=aajkadin.weekday())
    last_week = []
    for i in range(7):
        weekday = last_monday + datetime.timedelta(days=i)
        last_week.append(weekday.strftime('%d/%m/%Y'))
    
    current_week_status = {}
    pending_days = []
    for day in last_week:
        if day in my_sc_dates:
            d = datetime.datetime.strptime(day,'%d/%m/%Y')
            current_week_status[d.strftime('%d %b %a')] = 'filled'
        else :
            d = datetime.datetime.strptime(day,'%d/%m/%Y')
            current_week_status[d.strftime('%d %b %a')] = 'pending'
            pending_days.append(d)
    
    def reload_scdb():
        st.session_state['sc_db'] = fetch_data_forced(st.secrets['db_sadhana']['sheetID'],
                                 f'{devotee_name}!S2:S',major_dimention='COLUMNS')[0]

    left,middle,right = st.columns(3)
    left.write(':green[filled]')
    middle.write(':red[pending]')
    for day in current_week_status.keys():
        if current_week_status[day] =='filled':
            left.write(f':green[{day}]')
            # display_status += f':green[{day}]' + '\n'
        else:
            assert current_week_status[day] =='pending'
            middle.write(f':red[{day}]')
            # display_status += f':red[{day}]' + '\n'

    fill = {}

    filldate_string = right.radio(" hari",options=pending_days,label_visibility='hidden',
    format_func=lambda x: x.strftime('%d %b %a'))
    middle.button('refresh status',on_click=reload_scdb)
    st.markdown('---')
    filldate = datetime.date(year=filldate_string.year,
                             month=filldate_string.month,
                             day=filldate_string.day).strftime("%d %b %a")
    fill['date'] = filldate
    st.markdown(f"#### filling for :violet[{fill['date']}]")

    with st.expander("Morning Program",expanded=True):
        # waking up
        wakeup = st.text_input("Wake Up 🌞",value=3.99,help=":blue[Please enter 3:30 am as 3.30]")
        st.caption(f':blue[wake up at {convert_time(wakeup)[1]}]')
        if convert_time(wakeup)[0] !=-1:
            fill['wakeup'] = convert_time(wakeup)[2]
        else:
            fill['wakeup'] = "error"

        
        # SA
        fill['SA'] = st.radio(label="SA Attendance",
                            options=['PP','L0','L1','L2','L3','L4','L5','LL'],
                            index=7,
                            horizontal=True)
        st.markdown("")

        # MC
        fill['MC'] = st.radio(label="Morning Class",
                            options=['Full Present','Partially Present','Absent'],
                            index=2,
                            horizontal=True)
        st.markdown("")

        # MA
        fill['MA'] = st.radio(label="Mangal Aarti",
                            options=['not filled','Present','Absent'],
                            index=2,
                            horizontal=True)
        st.markdown("")

        # Chanting
        chant = st.text_input("Chanting 📿",value=8.99,help=":blue[Please enter 6:30 pm as 18.30]")
        st.caption(f':blue[complete japa at {convert_time(chant)[1]}]')
        if convert_time(chant)[0] !=-1:
            fill['chant'] = convert_time(chant)[2]
        else:
            fill['chant'] = 'error' 


    # ---------------Reading and Hearing
    with st.expander("Sadhana 🔥",expanded=True):
        fill['Reading'] = st.number_input(label="Reading",
                                            min_value=0,
                                            value=0,
                                            step=30
                                            )
        if fill['Reading'] > 0:
            bookname = st.text_input("Which Book")
            fill['book'] = bookname
        else:
            fill['book'] = ""
        
        st.markdown("#### Hearings")
        fill['Hearing_SP'] = st.number_input(label="Srila Prabhupada",
                                            min_value=0,
                                            value=0,
                                            step=30
                                            )
                
        fill['Hearing_HHRNSM'] = st.number_input(label="HHRNSM",
                                            min_value=0,
                                            value=0,
                                            step=30
                                            )
                
        fill['Hearing_RSP'] = st.number_input(label="HG RSP",
                                            min_value=0,
                                            value=0,
                                            step=30
                                            )
        
        verse = st.radio(label="Shloka",options=['notdone','done-1','done-2','done-3'],horizontal=True)
        if verse!='notdone':
            verse_number = st.text_input(label="Which one 😎")
            if verse_number =="":
                fill['verse'] = verse.split('-')[-1]
            else:
                fill['verse'] = f"{verse.split('-')[-1]} : {verse_number}"
        else :
            assert verse == 'notdone'
            fill['verse'] = ''

    # --------------- College and Studies
    with st.expander('College and Studies',expanded=True):
        # st.markdown("### College")
        
        fill['college'] = st.radio(label='College Class',
                                options=['All Present','Missed 1','Missed 2', 'Missed 2+','no classes'],
                                index=3,
                                horizontal=True)
        st.markdown("")

        fill['self_study'] = st.number_input(label="Self Study",
                                            min_value=0,
                                            value=0,
                                            step=1
                                            )
    fill['dayrest'] = st.number_input("Day Rest ",
                                        min_value=0,
                                        value=0)

    tobed = st.number_input("To Bed 💤",value=21.45,help=":blue[Please enter 9:30 pm as 121.30]")
    st.caption(f':blue[took rest at] {convert_time(tobed)[1]}')
    # st.write(convert_time(tobed)[0]
    if convert_time(tobed)[0] !=-1:
        fill['tobed'] = convert_time(tobed)[2]
    else:
        fill['tobed'] = 'error'

    def submit(datasubmit):
        sheetID = st.secrets['db_sadhana']['sheetID']
        # st.write(datasubmit.keys())
        row = fetch_data_forced(sheetID,f"{st.session_state['user']['name']}!A3")[0][0]
        row = json.loads(row)
        row = row['first_blank_row']
        sheetrange = f"{st.session_state['user']['name']}!B{row}:Q{row}"

        response = update_range(sheetID,sheetrange,[list(datasubmit.values())],input_type='USER_ENTERED')
        if 'values' in response.keys():
            st.session_state['message'] = f":green[filled Successfully!!] for :violet[{datasubmit['date']}]"
        
    submit = st.button('submit 👍',on_click=submit,
                        args=[fill])

    if 'message' in st.session_state:
        st.caption(st.session_state['message'])
        st.session_state.pop('message')
        

    st.markdown("---")
    st.markdown("### Other pages")
    def changetab(subpage):
        st.session_state['substate'] = subpage
    def change_page(page):
        st.session_state['state'] = page
    st.button("Dashboard",on_click=changetab,args=['dashboard'])
    st.button("Feed",on_click=change_page,args=['feed'])

def show_sc_dashboard():
    if 'scfilling' not in st.session_state:
        query_raw = fetch_data_forced(st.secrets['db_sadhana']['sheetID'],
                                    'summary!B5:J19',major_dimention='COLUMNS')
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


#--------------------- 
sc_state_page = {'show_page':show_daily_filling,
                 'dashboard':show_sc_dashboard}

def sc_main():
    if 'substate' not in st.session_state:
        show_daily_filling()
    elif st.session_state['substate'] in sc_state_page.keys():
        # run the respective page
        sc_state_page[st.session_state.substate]()
    else :
        show_daily_filling()
           
    
