import streamlit as st
import pandas as pd

from other_pages.googleapi import download_data
from other_pages.googleapi import upload_data

# ============= some variables
JAPA_TALK_RANGE = 'audio_bdv!B:C'
# ============= some variables end


## ----------- call back functions
def change_page(state,substate='default'):
    st.session_state['state'] = state
    st.session_state['substate'] = substate

def change_subpage(subpage):
    st.session_state['substate'] = subpage

## -------------

def japa_talk_home():
    st.session_state.pop('jt_db')
    if "jt_db" not in st.session_state:
        array = download_data(db_id=1,range_name=JAPA_TALK_RANGE)
        df = pd.DataFrame(array[1:],columns=array[0])

        # extract date
        df['date'] = df.Name.str.split("_Japa Talk_").str[0].str.split('_').str[0]
        df['Date'] = pd.to_datetime(df['date'],format='%Y-%m-%d',errors='coerce')
        df.dropna(inplace=True)
        df.reset_index(drop=True,inplace=True)
        df.reset_index(inplace=True)
        df['user_friendly_date'] = df['Date'].dt.strftime('%y %b %d')
        
        # extract title
        df['Title'] = df.Name.str.split("_Japa Talk_").str[1].str.rsplit("_",1).str[0]
        
        st.session_state['jt_db'] = df

    jt_db = st.session_state['jt_db']
    # st.dataframe(jt_db)
    st.header(":green[Japa Talks by HG Radheshyam Prabhuji]")
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

    # col_title,col_link = st.columns([3,1])
    for i in viewdf.index:
        st.markdown(f"""{i}. :violet[{viewdf.loc[i]['Title']}] on :orange[{viewdf.loc[i]['user_friendly_date']}] {'-'*5}
        [:green[Hear]]({viewdf.loc[i,"URL"]})""")
        # :green[yes]""")
        # col_link.markdown(f'[Hear]({viewdf.loc[i,"URL"]})')
        # col_link.markdown("")
        # col_link.markdown("")
        # right.button("Play",key=i,on_click=play,args=[viewdf.loc[i]['URL'],
                                                    #   viewdf.loc[i]['Title'],
                                                    #   viewdf.loc[i]['Date'],
                                                    #   i])

    st.markdown("---")
    st.button('home',key='home',on_click=change_page,args=['feed','default'])
    # st.dataframe(jt_db[
    # jt_db.index.isin(range((pageindex-1)*show_at_a_time,((pageindex-1)*show_at_a_time)+show_at_a_time+1))])



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
login_state_map = {'home':japa_talk_home,
                   'play':playing}

def jt_main():
    if 'substate' not in st.session_state:
        # default behaviour
        japa_talk_home()

    elif st.session_state['substate'] in login_state_map.keys():
        # directed behaviour
        login_state_map[st.session_state['substate']]()
    else:
        # exceptional
        japa_talk_home()