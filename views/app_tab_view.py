from PyQt6.QtWidgets import QTabWidget, QWidget, QTabBar
from views.start_view import StartView


class AppTabView(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.tabBarClicked.connect(self.check_tab)
        self.add_new_tab()

    def check_tab(self, index):
        if index == self.count() - 1:
            self.add_new_tab()

    def add_new_tab(self, new_tab=None, title="Start", redirect=True):
        if new_tab is None:
            new_tab = StartView(self.add_new_tab)
        self.insertTab(self.count() - 1, new_tab, title)
        if redirect:
            self.setCurrentIndex(self.count() - 2)
        if self.count() == 1:
            self.addTab(QWidget(), "+")
            self.tabBar().setTabButton(self.count() - 1, QTabBar.ButtonPosition.RightSide, None)

    def close_tab(self, index):
        if self.count() > 1:
            self.removeTab(index)
            self.setCurrentIndex(self.count() - 2)
