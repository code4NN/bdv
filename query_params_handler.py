import streamlit as st
# from other_pages.hearing_tracker import VANI_hearing_class as class_under_development
from other_pages.hearing_tracker import SP_hearing_Class as class_under_development

def process_query_parameters(app,qdict):
    target = qdict.get("target",'login')
    clear_queries = qdict.get('clear','no')
    
    app.handled_query_params = True if target !='dev' else False
    
    # for development this would be the target 
    # ?target=dev&page=vani_hearing&subpage=dash&refresh=no
    if target == 'dev':
        page = qdict['page']
        subpage = qdict.get('subpage','blank')
        refresh = qdict.get('refresh','yes')
        
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
    
    # for productions we will have one of the following
    elif target =='login':
        # login page
        username = qdict.get('user',"nouser")
        password = qdict.get('pass','blank')
        login_page = app.page_map['login']
        userdb = login_page.userdb
        
        if username in userdb.keys():
            if password == userdb[username]['password']:
                # success
                app.userinfo = login_page.parse_userinfo(username)
    
    elif target =='hear-now':
        source = qdict.get("source")
        lecture_id = qdict.get("id")
        redirect_mode = qdict.get("mode",'guest')
        
        if redirect_mode=='user':
            username = qdict.get('user')
            password = qdict.get('pass')
            
        if source == 'sp_sindhu':
            app.current_page = 'sp_hearing'
            player = app.page_map['sp_hearing']
            player.page_config = {'page_title': fullname,
                                'page_icon':'🎧',
                                'layout':'wide'}
            
            player.current_page = 'SP_lec_player'
            player.play_now_info_dict = {'megaid':megaid,
                                        'spid':spid,
                                        'name':fullname}
            st.rerun()
    
    
    
    
    
    # for clearing query
    if clear_queries == 'yes':
        st.query_params.clear()