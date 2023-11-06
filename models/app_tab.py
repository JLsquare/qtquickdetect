from PyQt6.QtWidgets import QTabWidget, QWidget, QTabBar
from views.start_view import StartView


class AppTab(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._next_tab_index = 0
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.tabBarClicked.connect(self.check_tab)
        self.add_new_tab()

    def check_tab(self, index):
        if index == self.count() - 1:
            self.add_new_tab()

    def add_new_tab(self):
        self._next_tab_index += 1
        new_tab = StartView()
        self.insertTab(self.count() - 1, new_tab, f"Tab {self._next_tab_index}")
        self.setCurrentIndex(self.count() - 2)
        if self._next_tab_index == 1:
            self.addTab(QWidget(), "+")
            self.tabBar().setTabButton(self.count() - 1, QTabBar.ButtonPosition.RightSide, None)

    def close_tab(self, index):
        if self.count() > 1:
            self.removeTab(index)
            self.setCurrentIndex(self.count() - 2)
