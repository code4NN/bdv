import streamlit as st
import datetime

def change_page(pagename):
    st.session_state.state = pagename

def show_feed():
    st.header(':green[Barasana Dhaam]')
    # st.subheader(':blue[Sri Sri Nimai Nitai Ki Jai]')
    st.image('https://i.pinimg.com/550x/75/0d/ee/750dee9058de489b184e32b07d2a52d1.jpg')

    st.markdown('---') #------------------------ Forms
    st.subheader(":blue[Quick Forms]")    
    st.button('Sadhana Card',on_click=change_page,args=['Sadhana_Card'])
    st.button('Settlement Form',on_click=change_page,args=['settlement'])
    # st.button('Suggession')

    st.markdown('---') #------------------------ Birthday

    st.subheader(":blue[Birthday's]")
    f"Today {datetime.datetime.now().date()}"
    ':green[Parth Pr]'
    "Upcoming"
    ':red[Vivek Pr] Tuesday'
    
    st.markdown('---') #------------------------Quote and verse

    st.subheader(":blue[Quote of the day]")
    st.image("data:image/jpeg;base64,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")
    st.markdown('_:green[Free time is not an oppulence]_')

    st.markdown('---') #------------------------ Sadhana

    # st.subheader(':blue[Sadhana]')
    # "some kind of overall progress summary "
    # ":green[here]"
    # st.button('Nakula Devotees')
    # st.button('Arjun Devotees')
    # st.button('Bhim Devotees')
    # st.button('Yudhisthir Devotees')

    # st.markdown('---') #------------------------ Departments

    st.subheader(":blue[Departments]")

    st.button("Structure",on_click=change_page,args=['dept_structure'])
    # st.button('Preaching 🔊')
    # st.button('Cleanliness 🧹')
    # st.button('Study 👨‍🎓')
    # st.button('Internal Management')
    # st.button("Kitchen 🔥")
    # st.button("Accounts 💸")

    # st.button('Deity Darshans')

    "A summary of all department and respective IC, VM etc"
    ":green[here]"

    st.markdown('---')
    def logout():
        st.session_state.pop('state')
    st.button("logout",on_click=logout)