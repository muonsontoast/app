from PySide6.QtWidgets import (
    QWidget, QListView, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QSpacerItem,
    QSizePolicy, QGraphicsProxyWidget
)
from PySide6.QtCore import Qt, QPoint, QStringListModel, QSortFilterProxyModel, QModelIndex, QItemSelectionModel
from ..blocks.draggable import Draggable
from ..utils.transforms import MapDraggableRectToScene
from ..utils import commands
from .. import shared
from .. import style

placeBlockOffset = QPoint(175, 0)

class EditorMenu(Draggable):
    '''Pop-up editor menu upon right-clicking the editor.'''
    def __init__(self, parent, **kwargs):
        self.proxy = QGraphicsProxyWidget()
        self.proxy.setZValue(100)
        self.proxy.setFocusPolicy(Qt.StrongFocus)
        super().__init__(self.proxy, size = kwargs.pop('size', [350, 250]), name = 'EditorMenu', type = 'EditorMenu')
        self.parent = parent
        self.hidden = True
        self.offset = QPoint(0, 0)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.model = QStringListModel([k + f" ({', '.join(v['shortcut'])})" for k, v in zip(commands.commands.keys(), commands.commands.values())])
        self.matchingModel = QSortFilterProxyModel()
        self.matchingModel.setSourceModel(self.model)
        self.matchingModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.shortcuts = QListView()
        self.shortcuts.pressed.connect(self.RunCommandFromClick)
        self.shortcuts.setFixedHeight(175)
        self.shortcuts.setFocusPolicy(Qt.NoFocus)
        self.shortcuts.setFrameShape(QListView.NoFrame)
        self.shortcuts.setVerticalScrollMode(QListView.ScrollPerPixel)
        self.shortcuts.setModel(self.matchingModel)
        self.currentShortcutIndex = QModelIndex()

        self.Push()

    def Push(self):
        self.main = QWidget()
        self.main.setLayout(QVBoxLayout())
        self.main.layout().setContentsMargins(0, 0, 0, 0)
        self.main.setObjectName('main')
        self.header = QWidget()
        self.header.setFixedHeight(30)
        self.header.setLayout(QHBoxLayout())
        self.header.layout().setContentsMargins(10, 0, 0, 0)
        self.title = QLabel('Quick Menu')
        self.header.layout().addWidget(self.title, alignment = Qt.AlignLeft)
        self.main.layout().addWidget(self.header)
        self.body = QWidget()
        self.body.setLayout(QVBoxLayout())
        self.body.layout().setContentsMargins(5, 0, 5, 0)
        self.body.layout().setSpacing(5)
        # Search bar
        self.search = QLineEdit()
        self.search.textChanged.connect(self.UpdateShortcuts)
        self.search.returnPressed.connect(self.RunCommandFromSearch)
        self.search.setPlaceholderText(' Type an action ...')
        self.search.setStyleSheet(style.LineEditStyle(color = '#2a2a2a', fontColor = '#c4c4c4'))
        self.search.setFixedHeight(30)
        self.body.layout().addWidget(self.search)
        # Matching shortcut commands
        self.body.layout().addWidget(self.shortcuts)
        self.body.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.main.layout().addWidget(self.body)
        self.layout().addWidget(self.main)
        self.proxy.setWidget(self)
        self.UpdateColors()

    def wheelEvent(self, event):
        angle = event.angleDelta().y()
        if angle < 0:
            self.IncrementShortcutIndex()
        else:
            self.DecrementShortcutIndex()
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.DecrementShortcutIndex()
        elif event.key() == Qt.Key_Down:
            self.IncrementShortcutIndex()
        elif event.key() == Qt.Key_Return:
            self.RunCommandFromSearch()
        event.accept()

    def UpdateShortcuts(self, pattern: str):
        self.matchingModel.setFilterFixedString(pattern)
        self.currentShortcutIndex = 0
        index = self.shortcuts.model().index(self.currentShortcutIndex, 0)
        self.shortcuts.setCurrentIndex(index)
        self.shortcuts.selectionModel().select(index, QItemSelectionModel.ClearAndSelect)

    def IncrementShortcutIndex(self):
        if self.currentShortcutIndex == QModelIndex():
            self.currentShortcutIndex = 0
        else:
            self.currentShortcutIndex = (self.currentShortcutIndex + 1) % self.shortcuts.model().rowCount()
        index = self.shortcuts.model().index(self.currentShortcutIndex, 0)
        self.shortcuts.setCurrentIndex(index)
        self.shortcuts.selectionModel().select(index, QItemSelectionModel.ClearAndSelect)

    def DecrementShortcutIndex(self):
        if self.currentShortcutIndex == QModelIndex():
            self.currentShortcutIndex = self.shortcuts.model().rowCount() - 1
        else:
            self.currentShortcutIndex = (self.currentShortcutIndex - 1) % self.shortcuts.model().rowCount()
        self.shortcuts.setCurrentIndex(self.shortcuts.model().index(self.currentShortcutIndex, 0))

    def RunCommandFromSearch(self):
        text = self.shortcuts.model().index(self.currentShortcutIndex, 0).data()
        commandName = text.split(' (')[0]
        args = []
        for arg in commands.commands[commandName]['args']:
            if arg == commands.GetMousePos:
                args.append(shared.PVs[self.ID]['rect'].center() + placeBlockOffset)
                continue
            args.append(arg())
        commands.commands[commandName]['func'](*args)

    def RunCommandFromClick(self, index):
        text = index.data()
        commandName = text.split(' (')[0]
        args = []
        for arg in commands.commands[commandName]['args']:
            if arg == commands.GetMousePos:
                args.append(shared.PVs[self.ID]['rect'].center() + placeBlockOffset)
                continue
            args.append(arg())
        commands.commands[commandName]['func'](*args)

    def Show(self, point: QPoint):
        self.proxy.setPos(point - self.offset)
        if not self.hidden:
            return
        shared.activeEditor.scene.addItem(self.proxy)
        shared.PVs[self.ID] = dict(pv = self, rect = MapDraggableRectToScene(self))
        self.proxy.setFocus()
        self.hidden = False
    
    def Hide(self):
        if self.hidden:
            return
        shared.PVs.pop(self.ID)
        shared.activeEditor.scene.removeItem(self.proxy)
        self.search.setText('')
        self.hidden = True

    def UpdateColors(self):
        if shared.lightModeOn:
            pass
        else:
            self.setStyleSheet(style.WidgetStyle(color = '#2e2e2e', borderRadius = 4))
            self.header.setStyleSheet(style.WidgetStyle(color = '#3d3d3d', borderRadiusTopLeft = 4, borderRadiusTopRight = 4))
            self.shortcuts.setStyleSheet(style.ListView(color = '#2e2e2e', hoverColor = '#363636', fontColor = '#c4c4c4', spacing = 5))
            self.shortcuts.horizontalScrollBar().setStyleSheet(style.ScrollBarStyle(handleColor = '#3d3d3d', backgroundColor = '#2e2e2e'))
            self.shortcuts.verticalScrollBar().setStyleSheet(style.ScrollBarStyle(handleColor = '#3d3d3d', backgroundColor = '#2e2e2e'))
            self.title.setStyleSheet(style.LabelStyle(padding = 0, fontColor = '#c4c4c4'))

    def ToggleStyling(self, **kwargs):
        pass