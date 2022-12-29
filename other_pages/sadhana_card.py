import streamlit as st
import datetime

# ==================== Daily Filling page
def show_daily_filling():

    filldate = st.date_input("Filling for ",label_visibility='hidden')    
    st.markdown(f"#### filling for {filldate.strftime('%d %b %a')}")
    
    # current_week_status 

    fill = {}
    with st.expander("Morning Program",expanded=True):
        # waking up
        fill['wakeup'] = st.time_input('wake up')
        st.markdown("")
        
        # SA
        fill['SA'] = st.radio(label="SA Attendance",
                            options=['not filled','PP','L0','L1','L2','L3','L4','L5','LL'],
                            index=0,
                            horizontal=True)
        st.markdown("")

        # MC
        fill['MC'] = st.radio(label="Morning Class",
                            options=['not filled','Full Present','Partially Present','Absent'],
                            index=0,
                            horizontal=True)
        st.markdown("")

        # MA
        fill['MA'] = st.radio(label="Mangal Aarti",
                            options=['not filled','Present','Absent'],
                            index=0,
                            horizontal=True)
        st.markdown("")

        # Chanting
        fill['chant'] = st.time_input("Chanting 📿")

    # ---------------Reading and Hearing
    with st.expander("Sadhana 🔥",expanded=True):
        fill['Reading'] = st.number_input(label="Reading",
                                            min_value=-1,
                                            value=-1,
                                            step=1
                                            )
        
        st.markdown("#### Hearings")
        fill['Hearing_SP'] = st.number_input(label="Srila Prabhupada",
                                            min_value=-1,
                                            value=-1,
                                            step=1
                                            )
                
        fill['Hearing_HHRNSM'] = st.number_input(label="HHRNSM",
                                            min_value=-1,
                                            value=-1,
                                            step=1
                                            )
                
        fill['Hearing_SP'] = st.number_input(label="HG RSP",
                                            min_value=-1,
                                            value=-1,
                                            step=1
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
                                index=0,
                                horizontal=True)
        st.markdown("")

        fill['self_study'] = st.number_input(label="Self Study",
                                            min_value=-1,
                                            value=-1,
                                            step=1
                                            )


    submit = st.button("done 👍")
    if submit:
        fill
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
