from PySide6.QtWidgets import (
    QWidget, QLineEdit, QSlider, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from .. import shared
from .. import style

class SliderComponent(QWidget):
    def __init__(self, pv, component, sliderSteps = 1000000, floatdp = 3, **kwargs):
        '''Leave `sliderSteps` at 1e6 for smooth sliding, or restrict to a low number for discrete applications.\n
        `floatdp` is the decimal precision of the line edit elements.\n
        `hideRange` allows you to supress the min and max widgets.\n
        `sliderOffset` (int) adds a horizontal offset to the slider row.\n
        `sliderRowSpacing` (int) controls width of SpacerItem between the slider and slider value.\n
        `paddingLeft` and `paddingBottom` (int) are padding for text inside line edit elements.'''
        super().__init__()
        self.hideRange = kwargs.get('hideRange', False)
        self.sliderOffset = kwargs.get('sliderOffset', 0)
        self.paddingLeft = kwargs.get('paddingLeft', 5)
        self.paddingBottom = kwargs.get('paddingBottom', 5)
        self.sliderOffset = kwargs.get('sliderOffset', 5)
        self.sliderRowSpacing = kwargs.get('sliderRowSpacing', 20)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(self.sliderOffset, 0, 0, 15)
        self.layout().setSpacing(10)
        self.pv = pv
        self.component = component
        self.floatdp = int(floatdp)
        self.range = pv.settings['components'][component]['max'] - pv.settings['components'][component]['min']
        self.steps = sliderSteps
        # Slider row
        self.sliderRow = QWidget()
        self.sliderRow.setLayout(QHBoxLayout())
        self.sliderRow.layout().setContentsMargins(self.sliderOffset, 0, 0, 0)
        self.sliderRow.layout().setSpacing(0)
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.slider.setRange(0, sliderSteps)
        self.slider.setValue(self.ToSliderValue(pv.settings['components'][component]['value']))
        self.slider.valueChanged.connect(self.UpdateSliderValue)
        self.sliderRow.layout().addWidget(self.slider)
        self.sliderRow.layout().addItem(QSpacerItem(self.sliderRowSpacing, 0, QSizePolicy.Fixed, QSizePolicy.Preferred))
        # Value
        self.value = QLineEdit(f'{pv.settings['components'][component]['value']:.{self.floatdp}f}')
        self.value.setAlignment(Qt.AlignCenter)
        self.value.setFixedSize(75, 25)
        self.value.returnPressed.connect(self.SetSliderValue)
        self.sliderRow.layout().addWidget(self.value, alignment = Qt.AlignRight)
        self.sliderRow.layout().addItem(QSpacerItem(self.sliderRowSpacing, 0, QSizePolicy.Fixed, QSizePolicy.Preferred))
        # Reset
        self.resetButton = QPushButton('Reset')
        self.resetButton.setFixedWidth(65)
        self.resetButton.clicked.connect(self.Reset)
        self.sliderRow.layout().addWidget(self.resetButton)
        if not self.hideRange:
            # Minimum
            self.minimumRow = QWidget()
            self.minimumRow.setLayout(QHBoxLayout())
            self.minimumRow.layout().setContentsMargins(0, 0, 0, 0)
            self.minimumLabel = QLabel('Minimum')
            self.minimumLabel.setAlignment(Qt.AlignCenter)
            self.minimum = QLineEdit(f'{pv.settings['components'][component]['min']:.{self.floatdp}f}')
            self.minimum.setAlignment(Qt.AlignCenter)
            self.minimum.setFixedSize(75, 25)
            self.minimum.returnPressed.connect(self.SetMinimum)
            self.minimumRow.layout().addWidget(self.minimumLabel, alignment = Qt.AlignLeft)
            self.minimumRow.layout().addWidget(self.minimum, alignment = Qt.AlignRight)
            self.minimumRow.layout().addItem(QSpacerItem(200, 0, QSizePolicy.Preferred, QSizePolicy.Preferred))
            # Maximum
            self.maximumRow = QWidget()
            self.maximumRow.setLayout(QHBoxLayout())
            self.maximumRow.layout().setContentsMargins(0, 0, 0, 0)
            self.maximumLabel = QLabel('Maximum')
            self.maximumLabel.setAlignment(Qt.AlignCenter)
            self.maximum = QLineEdit(f'{pv.settings['components'][component]['max']:.{self.floatdp}f}')
            self.maximum.setAlignment(Qt.AlignCenter)
            self.maximum.setFixedSize(75, 25)
            self.maximum.returnPressed.connect(self.SetMaximum)
            self.maximumRow.layout().addWidget(self.maximumLabel, alignment = Qt.AlignLeft)
            self.maximumRow.layout().addWidget(self.maximum, alignment = Qt.AlignRight)
            self.maximumRow.layout().addItem(QSpacerItem(200, 0, QSizePolicy.Preferred, QSizePolicy.Preferred))
            # Default
            self.defaultRow = QWidget()
            self.defaultRow.setLayout(QHBoxLayout())
            self.defaultRow.layout().setContentsMargins(0, 0, 0, 0)
            self.defaultLabel = QLabel('Default')
            self.defaultLabel.setAlignment(Qt.AlignCenter)
            self.defaultRow.layout().addWidget(self.defaultLabel, alignment = Qt.AlignLeft)
            self.default = QLineEdit(f'{pv.settings['components'][component]['default']:.{self.floatdp}f}')
            self.default.setAlignment(Qt.AlignCenter)
            self.default.setFixedSize(75, 25)
            self.default.returnPressed.connect(self.SetDefault)
            self.defaultRow.layout().addWidget(self.default, alignment = Qt.AlignRight)
            self.defaultRow.layout().addItem(QSpacerItem(200, 0, QSizePolicy.Preferred, QSizePolicy.Preferred))
        # Add rows
        self.layout().addWidget(self.sliderRow)
        if not self.hideRange:
            self.layout().addWidget(self.minimumRow)
            self.layout().addWidget(self.maximumRow)
            self.layout().addWidget(self.defaultRow)
        # Apply colors
        self.UpdateColors()

    def ToAbsolute(self, v):
        return self.pv.settings['components'][self.component]['min'] + v / self.steps * self.range
    
    def ToSliderValue(self, v):
        return (v - self.pv.settings['components'][self.component]['min']) / self.range * self.steps

    def UpdateSliderValue(self):
        v = self.ToAbsolute(self.slider.value())
        self.value.setText(f'{v:.{self.floatdp}f}')
        if 'valueType' not in self.pv.settings['components'][self.component].keys():
            self.pv.settings['components'][self.component]['valueType'] = float
        self.pv.settings['components'][self.component]['value'] = self.pv.settings['components'][self.component]['valueType'](v)

    def SetSliderValue(self):
        self.value.clearFocus()
        self.value.setText(f'{float(self.value.text()):.{self.floatdp}f}')
        if 'valueType' not in self.pv.settings['components'][self.component].keys():
            self.pv.settings['components'][self.component]['valueType'] = float
        self.pv.settings['components'][self.component]['value'] = self.pv.settings['components'][self.component]['valueType'](self.value.text())
        if self.hideRange: # blinking cursor error in proxy widgets, so redraw the line edit.
            value = QLineEdit(f'{self.pv.settings['components'][self.component]['value']:.{self.floatdp}f}')
            value.setAlignment(Qt.AlignCenter)
            value.setFixedSize(75, 25)
            value.returnPressed.connect(self.SetSliderValue)
            self.sliderRow.layout().replaceWidget(self.value, value)
            self.value.setParent(None)
            self.value.deleteLater()
            shared.app.processEvents()
            self.value = value
            self.UpdateColors()
        self.UpdateSlider()

    def UpdateSlider(self):
        self.slider.setValue(self.ToSliderValue(float(self.value.text())))

    def Reset(self):
        self.slider.setValue(self.ToSliderValue(self.pv.settings['components'][self.component]['default']))

    def SetDefault(self):
        self.default.clearFocus()
        default = max(self.pv.settings['components'][self.component]['min'], min(self.pv.settings['components'][self.component]['max'], float(self.default.text())))
        self.default.setText(f'{default:.{self.floatdp}f}')
        self.pv.settings['components'][self.component]['default'] = default
        if self.hideRange: # blinking cursor error in proxy widgets, so redraw the line edit.
            default = QLineEdit(f'{self.pv.settings['components'][self.component]['default']:.{self.floatdp}f}')
            default.setAlignment(Qt.AlignCenter)
            default.setFixedSize(75, 25)
            default.returnPressed.connect(self.SetDefault)
            self.defaultRow.layout().replaceWidget(self.default, default)
            self.default.setParent(None)
            self.default.deleteLater()
            shared.app.processEvents()
            self.default = default
            self.UpdateColors()

    def SetMinimum(self):
        self.minimum.clearFocus()
        v = float(self.minimum.text())
        self.pv.settings['components'][self.component]['min'] = v
        self.pv.settings['components'][self.component]['default'] = max(v, self.pv.settings['components'][self.component]['default'])
        self.default.setText(f'{self.pv.settings['components'][self.component]['default']:.{self.floatdp}f}')
        self.range = self.pv.settings['components'][self.component]['max'] - v
        self.default.setText(f'{self.pv.settings['components'][self.component]['default']:.{self.floatdp}f}')
        self.minimum.setText(f'{v:.{self.floatdp}f}')
        newSliderValue = max(float(self.value.text()), v)
        self.slider.setValue(self.ToSliderValue(newSliderValue))
        self.value.setText(f'{newSliderValue:.{self.floatdp}f}')
        self.pv.settings['components'][self.component]['value'] = newSliderValue
        if self.hideRange: # blinking cursor error in proxy widgets, so redraw the line edit.
            minimum = QLineEdit(f'{self.pv.settings['components'][self.component]['min']:.{self.floatdp}f}')
            minimum.setAlignment(Qt.AlignCenter)
            minimum.setFixedSize(75, 25)
            minimum.returnPressed.connect(self.SetMinimum)
            self.minimumRow.layout().replaceWidget(self.minimum, minimum)
            self.minimum.setParent(None)
            self.minimum.deleteLater()
            shared.app.processEvents()
            self.minimum = minimum
            self.UpdateColors()
    
    def SetMaximum(self):
        self.maximum.clearFocus()
        v = float(self.maximum.text())
        self.pv.settings['components'][self.component]['max'] = v
        self.pv.settings['components'][self.component]['default'] = min(v, self.pv.settings['components'][self.component]['default'])
        self.default.setText(f'{self.pv.settings['components'][self.component]['default']:.{self.floatdp}f}')
        self.range = v - self.pv.settings['components'][self.component]['min']
        self.maximum.setText(f'{v:.{self.floatdp}f}')
        newSliderValue = min(float(self.value.text()), v)
        self.slider.setValue(self.ToSliderValue(newSliderValue))
        self.value.setText(f'{newSliderValue:.{self.floatdp}f}')
        self.pv.settings['components'][self.component]['value'] = newSliderValue
        if self.hideRange: # blinking cursor error in proxy widgets, so redraw the line edit.
            maximum = QLineEdit(f'{self.pv.settings['components'][self.component]['max']:.{self.floatdp}f}')
            maximum.setAlignment(Qt.AlignCenter)
            maximum.setFixedSize(75, 25)
            maximum.returnPressed.connect(self.SetMaximum)
            self.maximumRow.layout().replaceWidget(self.maximum, maximum)
            self.maximum.setParent(None)
            self.maximum.deleteLater()
            shared.app.processEvents()
            self.maximum = maximum
            self.UpdateColors()

    def UpdateColors(self, **kwargs):
        '''Override `fillColorLight` and `fillColorDark` with a #ABCDEF color string.'''
        fillColorDark = kwargs.get('fillColorLight', "#C74343")
        fillColorLight = kwargs.get('fillColorDark', "#B43C3C")
        if shared.lightModeOn:
            self.slider.setStyleSheet(style.SliderStyle(backgroundColor = "#D2C5A0", fillColor = fillColorLight, handleColor = "#2E2E2E"))
            self.value.setStyleSheet(style.LineEditStyle(color = '#D2C5A0', fontColor = '#1e1e1e', paddingLeft = self.paddingLeft, paddingBottom = self.paddingBottom))
            if not self.hideRange:
                self.minimum.setStyleSheet(style.LineEditStyle(color = '#D2C5A0', fontColor = '#1e1e1e', paddingLeft = self.paddingLeft, paddingBottom = self.paddingBottom))
                self.maximum.setStyleSheet(style.LineEditStyle(color = '#D2C5A0', fontColor = '#1e1e1e', paddingLeft = self.paddingLeft, paddingBottom = self.paddingBottom))
                self.minimumLabel.setStyleSheet(style.LabelStyle(fontColor = '#1e1e1e'))
                self.maximumLabel.setStyleSheet(style.LabelStyle(fontColor = '#1e1e1e'))
                self.default.setStyleSheet(style.LineEditStyle(color = '#D2C5A0', fontColor = '#1e1e1e', paddingLeft = self.paddingLeft, paddingBottom = self.paddingBottom))
                self.defaultLabel.setStyleSheet(style.LabelStyle(fontColor = '#1e1e1e'))
            self.resetButton.setStyleSheet(style.PushButtonStyle(color = '#D2C5A0', borderColor = '#A1946D', hoverColor = '#B5AB8D', fontColor = '#1e1e1e', padding = 4))
            return
        self.slider.setStyleSheet(style.SliderStyle(backgroundColor = "#202020", fillColor = fillColorDark, handleColor = "#858585"))
        self.value.setStyleSheet(style.LineEditStyle(color = '#202020', bold = True, fontColor = '#c4c4c4', paddingLeft = self.paddingLeft, paddingBottom = self.paddingBottom))
        if not self.hideRange:
            self.minimum.setStyleSheet(style.LineEditStyle(color = '#2d2d2d', fontColor = '#c4c4c4', paddingLeft = self.paddingLeft, paddingBottom = self.paddingBottom))
            self.maximum.setStyleSheet(style.LineEditStyle(color = '#2d2d2d', fontColor = '#c4c4c4', paddingLeft = self.paddingLeft, paddingBottom = self.paddingBottom))
            self.minimumLabel.setStyleSheet(style.LabelStyle(fontColor = '#c4c4c4'))
            self.maximumLabel.setStyleSheet(style.LabelStyle(fontColor = '#c4c4c4'))
            self.default.setStyleSheet(style.LineEditStyle(color = '#2d2d2d', fontColor = '#c4c4c4', paddingLeft = self.paddingLeft, paddingBottom = self.paddingBottom))
            self.defaultLabel.setStyleSheet(style.LabelStyle(fontColor = '#c4c4c4'))
        self.resetButton.setStyleSheet(style.PushButtonStyle(color = '#1e1e1e', fontColor = '#c4c4c4', padding = 5))