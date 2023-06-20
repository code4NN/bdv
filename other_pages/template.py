
from typing import Any


class template_page:
    def __init__(self) -> None:
        
        self.subpage = 'home'
        self.subpage_navigator = {
            'home':self.home
        }

    def home(self):
        pass

    def run(self):
        self.subpage_navigator[self.subpage]()