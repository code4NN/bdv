import streamlit as st
import json
import datetime
from streamlit import components
from other_pages.googleapi import update_range
from other_pages.googleapi import fetch_data_forced
from other_pages.googleapi import fetch_data
fetch_data
def change_subpage(subpage):
    st.session_state['substate'] = subpage
# ==================== Daily Filling page
def show_daily_filling():
    padding = 0
    st.markdown(f""" <style>
    .reportview-container.main.block-container{{
        padding-top: {padding}rem;
        padding-right: {padding}rem;
        padding-left: {padding}rem;
        padding-bottom: {padding}rem;
    }} </style> """, unsafe_allow_html=True)
    st.markdown('## Hare Krishna' )
    devotee_name = st.session_state['user']['name']
    st.markdown(f"### :green[{devotee_name} Pr]")    
    if devotee_name =='guest':
        def feed():
            st.session_state['state'] = 'feed'
        st.button('Main Menu',on_click=feed)
        return -1
    aajkadin = datetime.datetime.today()


    st.caption("Current week status")
    def reload_scdb():
        st.session_state['sc_db'] = fetch_data_forced(st.secrets['db_sadhana']['sheetID'],
                                 f'{devotee_name}!R2:R',major_dimention='COLUMNS')[0]

    reload_week = st.button('reload status',on_click=reload_scdb)
    
    filled_dates = None    
    if 'sc_db' not in st.session_state:
        st.session_state['sc_db'] = fetch_data_forced(st.secrets['db_sadhana']['sheetID'],
                                 f'{devotee_name}!R2:R',major_dimention='COLUMNS')[0]
    

    if reload_week :
        filled_dates = fetch_data_forced(st.secrets['db_sadhana']['sheetID'],
                                 f'{devotee_name}!R2:R',major_dimention='COLUMNS')[0]
    else:
        filled_dates = st.session_state['sc_db']
    st.markdown("---")
    last_monday = aajkadin - datetime.timedelta(days=aajkadin.weekday())
    last_week = []
    for i in range(7):
        weekday = last_monday + datetime.timedelta(days=i)
        last_week.append(weekday.strftime('%d/%m/%Y'))
    
    current_week_status = {}
    pending_days = []
    for day in last_week:
        if day in filled_dates:
            d = datetime.datetime.strptime(day,'%d/%m/%Y')
            current_week_status[d.strftime('%d %b %a')] = 'filled'
        else :
            d = datetime.datetime.strptime(day,'%d/%m/%Y')
            current_week_status[d.strftime('%d %b %a')] = 'pending'
            pending_days.append(d)

    # display_status = ""
    left,right = st.columns(2)
    left.write(':green[filled]')
    right.write(':red[pending]')
    for day in current_week_status.keys():
        if current_week_status[day] =='filled':
            left.write(f':green[{day}]')
            # display_status += f':green[{day}]' + '\n'
        else:
            assert current_week_status[day] =='pending'
            right.write(f':red[{day}]')
            # display_status += f':red[{day}]' + '\n'
    st.markdown('---')

    fill = {}
    filldate = st.radio(" hari",options=pending_days,label_visibility='hidden',
    format_func=lambda x: x.strftime('%d %b %a'))
    fill['date'] = filldate.strftime('%d %b %a')
    st.markdown(f"#### filling for :violet[{fill['date'].strftime('%d %b %a')}]")

    with st.expander("Morning Program",expanded=True):
        # waking up
        wakeup = st.time_input('wake up')
        fill['wakeup']  = f'{wakeup.hour}:{wakeup.minute}'
        st.markdown("")
        
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
        chant = st.time_input("Chanting 📿")
        fill['chant']  = f'{chant.hour}:{chant.minute}'

    # ---------------Reading and Hearing
    with st.expander("Sadhana 🔥",expanded=True):
        fill['Reading'] = st.number_input(label="Reading",
                                            min_value=0,
                                            value=0,
                                            step=30
                                            )
        if fill['Reading'] > 0:
            st.text_input("Which Book")
        
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
        
        verse = st.radio(label="Shloka",options=['notdone','done'],horizontal=True)
        if verse=='done':
            verse_number = st.text_input(label="Which one 😎")
            if verse_number =="":
                fill['verse'] = 'done'
            else:
                fill['verse'] = verse_number
        else :
            fill['verse'] = 'notdone'

    # --------------- College and Studies
    with st.expander('College and Studies',expanded=True):
        # st.markdown("### College")
        
        fill['college'] = st.radio(label='College Class',
                                options=['notfilled','All Present','Missed 1','Missed 2', 'Missed 2+','no classes'],
                                index=5,
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
    tobed = st.time_input("To Bed")
    fill['tobed']  = f'{tobed.hour}:{tobed.minute}'


    def submit(datasubmit):
        sheetID = st.secrets['db_sadhana']['sheetID']
        row = fetch_data_forced(sheetID,f"{st.session_state['user']['name']}!A3")[0][0]
        row = json.loads(row)
        row = row['first_blank_row']
        sheetrange = f"{st.session_state['user']['name']}!B{row}:P{row}"

        response = update_range(sheetID,sheetrange,[list(datasubmit.values())],input_type='USER_ENTERED')
        if 'values' in response.keys():
            st.write(":green[filled Successfully!!]")
        
    submit = st.button('submit 👍',on_click=submit,
                        args=[fill])

        
    st.markdown("---")

    st.markdown("### Other pages")




    def run2feed():
        st.session_state['substate'] = 'dashboard'
    st.button("go 2 feed",on_click=run2feed)
# ==================== Dashboard for all
    st.markdown('---')
    st.markdown('## Sadhana Card Dashboard')
    st.markdown('[wa me](http://wa.me/917260869161?text=Hare%20Krishna%20Prabhuji)')
    st.markdown('[wa me](tel:917260869161)')

def show_sc_dashboard():
    st.header("Dashboard")
    st.button('Fill today',on_click=change_subpage,args=['show_page'])

#--------------------- 
sc_state_page = {'show_page':show_daily_filling,
                 'dashboard':show_sc_dashboard}

def sc_main():
    if 'substate' not in st.session_state:
        try:
            show_daily_filling()
        except:
            pass
    elif st.session_state['state'] in sc_state_page.keys():
        # run the respective page
        try:
            sc_state_page[st.session_state.substate]()
        except:
            pass
    else :
        try:
            show_daily_filling()
        except:
            pass    
    
