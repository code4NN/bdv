import streamlit as st
from other_pages.hearing_tracker import hearing_Class as class_under_development

def process_query_parameters(app,qdict):
    target = qdict.get("target",'login')
    clear_queries = qdict.get('clear','no')
    
    app.handled_query_params = True if target !='dev' else False
    
    if target =='login':
        # login page
        username = qdict.get('user',"nouser")
        password = qdict.get('pass','blank')
        login_page = app.page_map['login']
        userdb = login_page.userdb
        
        if username in userdb.keys():
            if password == userdb[username]['password']:
                # success
                app.userinfo = login_page.parse_userinfo(username)
    
    elif target == 'dev':
        page = qdict['page']
        subpage = qdict.get('subpage','blank')
        refresh = qdict.get('refresh','no')
        
        # if refresh, create a fresh instance of the class
        if refresh == 'yes':
            newpage = class_under_development()
            # update subpage if available
            if subpage != 'blank':
                newpage.current_page = subpage
            app.page_map[page] = newpage        
        
        # update the bdv app
        app.current_page = page
        app.in_development = True
        
    elif target =='hear-now':
        megaid = qdict['mega-id']
        spid = qdict['sp-id']
        fullname = qdict['name']
        
        app.current_page = 'heart_medicine'
        
        player = app.page_map['heart_medicine']
        
        player.page_config = {'page_title': fullname,
                            'page_icon':'🎧',
                            'layout':'wide'}
        
        player.current_page = 'SP_lec_player'
        player.play_now_info_dict = {'megaid':megaid,
                                     'spid':spid,
                                     'name':fullname}
        st.rerun()
        
    if clear_queries == 'yes':
        st.query_params.clear()