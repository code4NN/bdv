import streamlit as st


class finder_Class:
    def __init__(self):
        
        self.page_dict = {'home':self.home,
                          'sp_transcript':self.vedabase_SP,
                          'idt_hhrnsm':self.idt_lectures_by_HHRNSM}
        self.current_page = 'home'
    
    @property
    def bdvapp(self):
        return st.session_state.get('bdv_app',None)
    
    def home(self):
        pass

    def vedabase_SP(self):
        pass

    def idt_lectures_by_HHRNSM(self):
        pass
    

    def run(self):
        self.page_dict[self.current_page]()