import streamlit as st
import pandas as pd

from other_pages.googleapi import download_data
from other_pages.googleapi import upload_data

# ============= some variables
# ============= some variables end


## ----------- call back functions
def change_page(state,substate='default'):
    st.session_state['state'] = state
    st.session_state['substate'] = substate

def change_subpage(subpage):
    st.session_state['substate'] = subpage

## -------------

def home():
    if "jt_db" not in st.session_state:
        array = download_data(db_id=1,range_name="Japa Talks!E:G")
        df = pd.DataFrame(array[1:],columns=array[0])
        df['dateraw'] = df['Date']
        df['Date1'] = pd.to_datetime(df['Date'], format="%d/%m/%y")
        df['Date'] = [d.strftime('%y-%b %d') for d in df['Date1']]
        df.sort_values(by='Date1',ascending=True,inplace=True)
        df.reset_index(inplace=True,drop=True)
        st.session_state['jt_db'] = df
    jt_db = st.session_state['jt_db']
    # st.dataframe(jt_db)
    
    left,right = st.columns(2)

    show_at_a_time = left.selectbox("Show rows at a time",options=[5,10,50,100],index=1)

    slice = len(jt_db)//show_at_a_time
    pageindex = right.selectbox("page",options=[i for i in range(1,slice+2)])
    right.caption(f'total {slice+1} pages')

    st.markdown('---')
    viewdf = jt_db[jt_db.index.isin(range((pageindex-1)*show_at_a_time,((pageindex-1)*show_at_a_time)+show_at_a_time+1))]
    def play(url,title,date,i):
        st.session_state['jt_url'] = url
        st.session_state['jt_title'] = title
        st.session_state['jt_date'] = date
        st.session_state['jt_index'] = i
        # change_subpage('play')

    for i in viewdf.index:
        left,right = st.columns([5,1])
        left.markdown(f"[:blue[{viewdf.loc[i]['Title']}] on {viewdf.loc[i]['Date']}]({viewdf.loc[i]['URL']})")
        right.button("Play",key=i,on_click=play,args=[viewdf.loc[i]['URL'],
                                                      viewdf.loc[i]['Title'],
                                                      viewdf.loc[i]['Date'],
                                                      i])

    # st.dataframe(jt_db[jt_db.index.isin(range((pageindex-1)*show_at_a_time,((pageindex-1)*show_at_a_time)+show_at_a_time+1))])


def playing():
    url = st.session_state['jt_url']
    title = st.session_state['jt_title']
    date = st.session_state['jt_date']
    index = st.session_state['jt_index']
    st.write(url)
    st.header(f':blue[{title}]')
    st.caption(date)
    # st.audio()
    st.markdown(f"""<audio controls>
  <source src={url} />
</audio>""",unsafe_allow_html=True)







# ---------------------- Wrapper
login_state_map = {'home':home,
                   'play':playing}

def jt_home():
    if 'substate' not in st.session_state:
        # default behaviour
        home()

    elif st.session_state['substate'] in login_state_map.keys():
        # directed behaviour
        login_state_map[st.session_state['substate']]()
    else:
        # exceptional
        home()