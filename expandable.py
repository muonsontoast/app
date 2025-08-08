from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from . import style
from . import shared

class Expandable(QWidget):
    def __init__(self, listWidget, item, name, pv, componentKey):
        '''`list` the ListWidget containing the expandable widget.\n
        `item` is the ListWidgetItem this expandable is attached to.\n
        Accepts a list of kwarg widgets to display in the expandable content region.'''
        super().__init__()
        self.list = listWidget
        self.parent = item
        # self.setFixedWidth(self.list.viewport().width() - 5)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 10, 0)
        self.layout().setSpacing(0)
        self.pv = pv
        self.componentKey = componentKey
        # Bool to keep track of whether to display the content.
        self.showingContent = False
        self.width = self.width()
        self.headerHeight = 40
        self.widgetsDrawn = False
        # Header button
        self.name = name
        self.nameHousing = QWidget()
        self.nameHousing.setLayout(QHBoxLayout())
        self.nameHousing.setContentsMargins(0, 0, 0, 0)
        self.header = QPushButton(f'\u25BA    {self.name}')
        self.header.setFixedSize(215, self.headerHeight)
        self.header.setCheckable(True)
        self.header.clicked.connect(self.ToggleContent)
        self.nameHousing.setFixedHeight(self.headerHeight)
        self.nameHousing.layout().addWidget(self.header)
        self.nameHousing.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.layout().addWidget(self.nameHousing)
        # Expandable area
        self.content = QListWidget()
        self.content.setFocusPolicy(Qt.NoFocus)
        self.content.setSelectionMode(QListWidget.NoSelection)
        self.content.setStyleSheet(style.InspectorSectionStyle())
        self.content.setVisible(False)
        self.layout().addWidget(self.content)
        self.parent.setSizeHint(QSize(self.width, self.headerHeight + 10))
        self.widget = self.pv.settings['components'][self.componentKey]['type'](self.pv, self.componentKey) # Instantiate the widget
        self.UpdateColors()

    def UpdateColors(self):
        if shared.lightModeOn:
            self.nameHousing.setStyleSheet(style.InspectorHeaderHousingStyle(fontColor = '#1e1e1e'))
            self.header.setStyleSheet(style.InspectorHeaderStyle(color = '#D2C5A0', hoverColor = '#B5AB8D', borderColor = "#A1946D", fontColor = '#1e1e1e'))
            if self.widget is not None:
                self.widget.UpdateColors()
        else:
            self.nameHousing.setStyleSheet(style.InspectorHeaderHousingStyle(fontColor = '#c4c4c4'))
            self.header.setStyleSheet(style.InspectorHeaderStyle(color = '#2e2e2e', hoverColor = '#3e3e3e', borderColor = '#1e1e1e', fontColor = '#c4c4c4'))
            if self.widget is not None:
                self.widget.UpdateColors()

    def ToggleContent(self):
        shared.app.processEvents()
        expandedHeight = 0
        if not self.showingContent:
            self.header.setText(f'\u25BC    {self.name}')
            # Is this the first time drawing widgets for this expandable?
            if not self.widgetsDrawn:
                item = QListWidgetItem()
                print(f'Expandable ({self.name}) sees list width as: {self.list.viewport().width()}')
                self.widget.setFixedWidth(self.list.viewport().width() - 20)
                item.setSizeHint(self.widget.sizeHint())
                self.content.addItem(item)
                self.content.setItemWidget(item, self.widget)
            expandedHeight += self.widget.sizeHint().height()
            self.widgetsDrawn = True
            self.content.setVisible(True)
        else:
            self.header.setText(f'\u25BA    {self.name}')
            self.content.setVisible(False)
        
        self.content.setFixedHeight(expandedHeight)
        self.showingContent = not self.showingContent
        self.parent.setSizeHint(QSize(self.sizeHint().width(), self.headerHeight + expandedHeight))