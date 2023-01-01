import streamlit as st
import json
import datetime
from streamlit import components
from other_pages.googleapi import update_range
from other_pages.googleapi import fetch_data_forced
# ==================== Daily Filling page
def show_daily_filling():   
    st.markdown('## Hare Krishna' )
    devotee_name = st.session_state['user']['name']
    st.markdown(f"### :green[{devotee_name} Pr]")

    filldate = st.date_input("Filling for ",label_visibility='hidden')    
    st.markdown(f"#### filling for {filldate.strftime('%d %b %a')}")
    
    # current_week_status
    this_week = fetch_data_forced(st.secrets['db_sadhana']['sheetID'],
                                 f'{devotee_name}!R2:R',major_dimention='COLUMNS')[0]
    this_week = [datetime.datetime.strptime(d,)]
    st.write(this_week)
    # st.write(filldate.strftime())
    fill = {}
    fill['date'] = filldate.strftime("%d/%m/%y")
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


    submit = st.button("done 👍")
    if submit:        
        sheetID = st.secrets['db_sadhana']['sheetID']
        row = fetch_data_forced(sheetID,f"{st.session_state['user']['name']}!A3")[0][0]
        row = json.loads(row)
        row = row['first_blank_row']
        range = f"{st.session_state['user']['name']}!B{row}:P{row}"
        
        response = update_range(sheetID,range,[list(fill.values())],input_type='USER_ENTERED')
        if 'values' in response.keys():
            st.write(":green[filled Successfully!!]")
        
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

#--------------------- 
sc_state_page = {'show_page':show_daily_filling,
                 'dashboard':show_sc_dashboard}

def sc_main():
    if 'substate' not in st.session_state:
        show_daily_filling()
    else:
        # run the respective page
        sc_state_page[st.session_state.substate]()
