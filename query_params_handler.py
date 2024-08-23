import streamlit as st
# from other_pages.hearing_tracker import VANI_hearing_class as class_under_development
from other_pages.hearing_tracker import SP_hearing_Class as class_under_development

def process_query_parameters(app,qdict):
    target = qdict.get("target",'login')
    clear_queries = qdict.get('clear','no')
    
    app.handled_query_params = True if target !='dev' else False
    
    # for development this would be the target 
    # Vani syllabus: ?target=dev&page=vani_hearing&subpage=dash&refresh=no
    # sp vani : ?target=dev&mode=user&page=sp_hearing&subpage=SP&refresh=no
    
    if target == 'dev':
        page = qdict['page']
        loginmode = qdict['mode'] # guest or user
        subpage = qdict.get('subpage','blank')
        refresh = qdict.get('refresh','yes')
        
        # login if login_mode is user
        if loginmode == 'user':
            username = qdict.get('username','Shiven')
            password = qdict.get('pass','mindit')
            
            app.scriptcial_login(username,password)
            
        
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
        
        app.scriptcial_login(username,password)
    
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
            
            # get lecture name
            lec_info = player.sp_sindhu_df.query(f"encrypt_id == '{lecture_id}'")
            lec_name = lec_info.name.tolist()[0]
            full_name = lec_info.full_name.tolist()[0]
            mega_id = lec_info.mega_id.tolist()[0]
            sp_id = lec_info['id'].tolist()[0]
            
            player.page_config = {'page_title': lec_name,
                                'page_icon':'🎧',
                                'layout':'wide'}
            
            player.current_page = 'SP_lec_player'
            player.play_now_info_dict = {'encrypt_id':lecture_id,
                                         'mega_id':mega_id,
                                         'sp_id':sp_id,
                                         'lecture_name':lec_name}
            st.rerun()
    
    
    
    
    
    # for clearing query
    if clear_queries == 'yes':
        st.query_params.clear()