import sys
import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QScrollArea, QFrame, QSizePolicy,
    QComboBox, QCheckBox, QGroupBox, QDoubleSpinBox, QSpinBox, QGridLayout,
    QRadioButton, QButtonGroup
)
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt, pyqtSignal

from numpy import *

class LogiaUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logia Scientific Software - Advanced Plotting Interface")
        self.setWindowIcon(QIcon(":/icons/logia_icon.png"))
        self.initUI()
        self.apply_stylesheet()

        self.setGeometry(100, 100, 1400, 900)
        self.show()
        
        self.plot_functions()

    def initUI(self):
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main Layout (Horizontal: Side Panel | Plot Area)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # --- Side Panel (Left) ---
        self.side_panel_frame = QFrame()
        self.side_panel_frame.setFixedWidth(350)
        self.side_panel_frame.setContentsMargins(10, 10, 10, 10)
        self.side_panel_overall_layout = QVBoxLayout(self.side_panel_frame)
        self.side_panel_overall_layout.setSpacing(8)

        # --- Section: Function Input Management ---
        self.func_input_group = QGroupBox("Function Definitions")
        self.func_input_group.setFont(QFont("Arial", 12, QFont.Bold))
        self.func_input_layout = QVBoxLayout(self.func_input_group)
        self.func_input_layout.setSpacing(5)

        # Scroll Area for Dynamic Function Entries
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.scroll_area_content = QWidget()
        self.scroll_area.setWidget(self.scroll_area_content)
        self.function_entries_layout = QVBoxLayout(self.scroll_area_content)
        self.function_entries_layout.setContentsMargins(0, 0, 0, 0)
        self.function_entries_layout.setSpacing(5)

        self.function_entries = []
        self.add_function_entry() # Add an initial entry field

        self.func_input_layout.addWidget(self.scroll_area)
        self.side_panel_overall_layout.addWidget(self.func_input_group)

        # --- Buttons Section ---
        self.buttons_group = QGroupBox("Actions & Control")
        self.buttons_group.setFont(QFont("Arial", 12, QFont.Bold))
        self.buttons_layout = QVBoxLayout(self.buttons_group)
        self.buttons_layout.setSpacing(8)

        self.add_function_button = QPushButton("Add New Function Input")
        self.add_function_button.clicked.connect(self.add_function_entry)
        self.buttons_layout.addWidget(self.add_function_button)

        self.plot_button = QPushButton("Generate Plot from Functions")
        self.plot_button.clicked.connect(self.plot_functions)
        self.buttons_layout.addWidget(self.plot_button)
        
        self.side_panel_overall_layout.addWidget(self.buttons_group)

        # Add a major separator
        major_separator = QFrame()
        major_separator.setFrameShape(QFrame.HLine)
        major_separator.setFrameShadow(QFrame.Sunken)
        major_separator.setStyleSheet("QFrame { background-color: #007acc; height: 2px; }")
        self.side_panel_overall_layout.addWidget(major_separator)

        # --- Plot Settings Group Box ---
        self.settings_group_box = QGroupBox("Global Plot Settings")
        self.settings_group_box.setFont(QFont("Arial", 12, QFont.Bold))
        self.settings_group_layout = QVBoxLayout(self.settings_group_box)
        self.settings_group_layout.setSpacing(5)

        # --- Axes Ranges ---
        axes_ranges_group = QGroupBox("Axis Ranges")
        axes_ranges_group.setFont(QFont("Arial", 10, QFont.Bold))
        axes_ranges_layout = QGridLayout(axes_ranges_group)
        axes_ranges_layout.addWidget(QLabel("X-min:"), 0, 0)
        self.x_min_spinbox = QDoubleSpinBox()
        self.x_min_spinbox.setRange(-10000.0, 10000.0)
        self.x_min_spinbox.setValue(-10.0)
        self.x_min_spinbox.setDecimals(2)
        axes_ranges_layout.addWidget(self.x_min_spinbox, 0, 1)
        axes_ranges_layout.addWidget(QLabel("X-max:"), 0, 2)
        self.x_max_spinbox = QDoubleSpinBox()
        self.x_max_spinbox.setRange(-10000.0, 10000.0)
        self.x_max_spinbox.setValue(10.0)
        self.x_max_spinbox.setDecimals(2)
        axes_ranges_layout.addWidget(self.x_max_spinbox, 0, 3)
        
        axes_ranges_layout.addWidget(QLabel("Y-min:"), 1, 0)
        self.y_min_spinbox = QDoubleSpinBox()
        self.y_min_spinbox.setRange(-10000.0, 10000.0)
        self.y_min_spinbox.setValue(-10.0)
        self.y_min_spinbox.setDecimals(2)
        axes_ranges_layout.addWidget(self.y_min_spinbox, 1, 1)
        axes_ranges_layout.addWidget(QLabel("Y-max:"), 1, 2)
        self.y_max_spinbox = QDoubleSpinBox()
        self.y_max_spinbox.setRange(-10000.0, 10000.0)
        self.y_max_spinbox.setValue(10.0)
        self.y_max_spinbox.setDecimals(2)
        axes_ranges_layout.addWidget(self.y_max_spinbox, 1, 3)
        self.settings_group_layout.addWidget(axes_ranges_group)

        self.x_min_spinbox.valueChanged.connect(self.plot_functions)
        self.x_max_spinbox.valueChanged.connect(self.plot_functions)
        self.y_min_spinbox.valueChanged.connect(self.plot_functions)
        self.y_max_spinbox.valueChanged.connect(self.plot_functions)

        # --- Display Options ---
        display_options_group = QGroupBox("Display Options")
        display_options_group.setFont(QFont("Arial", 10, QFont.Bold))
        display_options_layout = QVBoxLayout(display_options_group)

        self.grid_checkbox = QCheckBox("Show Grid Lines (Major)")
        self.grid_checkbox.setChecked(True)
        self.grid_checkbox.stateChanged.connect(self.plot_functions)
        display_options_layout.addWidget(self.grid_checkbox)

        self.minor_grid_checkbox = QCheckBox("Show Minor Grid Lines")
        self.minor_grid_checkbox.setChecked(False)
        self.minor_grid_checkbox.stateChanged.connect(self.plot_functions)
        display_options_layout.addWidget(self.minor_grid_checkbox)

        self.legend_checkbox = QCheckBox("Display Function Legend")
        self.legend_checkbox.setChecked(True)
        self.legend_checkbox.stateChanged.connect(self.plot_functions)
        display_options_layout.addWidget(self.legend_checkbox)

        self.tight_layout_checkbox = QCheckBox("Auto-adjust Plot Layout")
        self.tight_layout_checkbox.setChecked(True)
        self.tight_layout_checkbox.stateChanged.connect(self.plot_functions)
        display_options_layout.addWidget(self.tight_layout_checkbox)

        self.settings_group_layout.addWidget(display_options_group)

        # --- Plot Customization ---
        plot_custom_group = QGroupBox("Curve Customization")
        plot_custom_group.setFont(QFont("Arial", 10, QFont.Bold))
        plot_custom_layout = QGridLayout(plot_custom_group)

        plot_custom_layout.addWidget(QLabel("Global Line Style:"), 0, 0)
        self.line_style_combo = QComboBox()
        self.line_style_combo.addItems(['Solid (-)', 'Dashed (--)', 'Dash-Dot (-.)', 'Dotted (:)'])
        self.line_style_combo.currentIndexChanged.connect(self.plot_functions)
        plot_custom_layout.addWidget(self.line_style_combo, 0, 1)

        plot_custom_layout.addWidget(QLabel("Global Line Width:"), 1, 0)
        self.line_width_spinbox = QSpinBox()
        self.line_width_spinbox.setRange(1, 10)
        self.line_width_spinbox.setValue(2)
        self.line_width_spinbox.valueChanged.connect(self.plot_functions)
        plot_custom_layout.addWidget(self.line_width_spinbox, 1, 1)

        plot_custom_layout.addWidget(QLabel("Global Marker Style:"), 2, 0)
        self.marker_style_combo = QComboBox()
        self.marker_style_combo.addItems(['None', 'Point (.)', 'Pixel (P)', 'Circle (o)', 'Square (s)', 'Star (*)', 'X (x)', 'Plus (+)'])
        self.marker_style_combo.setCurrentIndex(0)
        self.marker_style_combo.currentIndexChanged.connect(self.plot_functions)
        plot_custom_layout.addWidget(self.marker_style_combo, 2, 1)

        plot_custom_layout.addWidget(QLabel("Global Marker Size:"), 3, 0)
        self.marker_size_spinbox = QSpinBox()
        self.marker_size_spinbox.setRange(1, 20)
        self.marker_size_spinbox.setValue(6)
        self.marker_size_spinbox.valueChanged.connect(self.plot_functions)
        plot_custom_layout.addWidget(self.marker_size_spinbox, 3, 1)

        self.settings_group_layout.addWidget(plot_custom_group)

        # --- Axis Scaling ---
        axis_scale_group = QGroupBox("Axis Scaling")
        axis_scale_group.setFont(QFont("Arial", 10, QFont.Bold))
        axis_scale_layout = QVBoxLayout(axis_scale_group)

        axis_scale_layout.addWidget(QLabel("X-axis Scale Type:"))
        self.x_scale_group = QButtonGroup(self)
        self.x_linear_radio = QRadioButton("Linear")
        self.x_linear_radio.setChecked(True)
        self.x_log_radio = QRadioButton("Logarithmic")
        self.x_scale_group.addButton(self.x_linear_radio)
        self.x_scale_group.addButton(self.x_log_radio)
        axis_scale_layout.addWidget(self.x_linear_radio)
        axis_scale_layout.addWidget(self.x_log_radio)
        self.x_scale_group.buttonClicked.connect(lambda: self.plot_functions())

        axis_scale_layout.addWidget(QLabel("Y-axis Scale Type:"))
        self.y_scale_group = QButtonGroup(self)
        self.y_linear_radio = QRadioButton("Linear")
        self.y_linear_radio.setChecked(True)
        self.y_log_radio = QRadioButton("Logarithmic")
        self.y_scale_group.addButton(self.y_linear_radio)
        self.y_scale_group.addButton(self.y_log_radio)
        axis_scale_layout.addWidget(self.y_linear_radio)
        axis_scale_layout.addWidget(self.y_log_radio)
        self.y_scale_group.buttonClicked.connect(lambda: self.plot_functions())

        self.settings_group_layout.addWidget(axis_scale_group)
        self.side_panel_overall_layout.addWidget(self.settings_group_box)
        self.side_panel_overall_layout.addStretch(1)

        self.main_layout.addWidget(self.side_panel_frame)

        # --- Plotting Area (Right) ---
        self.plot_area_frame = QFrame()
        self.plot_area_frame.setFrameShape(QFrame.StyledPanel)
        self.plot_area_frame.setFrameShadow(QFrame.Sunken)
        self.plot_area_layout = QVBoxLayout(self.plot_area_frame)
        self.plot_area_layout.setContentsMargins(0, 0, 0, 0)

        self.fig, self.ax = plt.subplots(figsize=(8, 6), facecolor="#1e1e1e")
        self.ax.set_facecolor("#1e1e1e")
        self.ax.spines['bottom'].set_color('#cccccc')
        self.ax.spines['top'].set_color('#cccccc')
        self.ax.spines['right'].set_color('#cccccc')
        self.ax.spines['left'].set_color('#cccccc')
        self.ax.tick_params(axis='x', colors='#cccccc')
        self.ax.tick_params(axis='y', colors='#cccccc')
        self.ax.xaxis.label.set_color('#cccccc')
        self.ax.yaxis.label.set_color('#cccccc')
        self.ax.grid(True, linestyle=':', alpha=0.6, color='#555555')
        self.ax.set_xlabel("X-axis: Independent Variable")
        self.ax.set_ylabel("Y-axis: Function Output")
        self.ax.set_title("Scientific Data Visualization: Logia Plot", color="#ffffff") # Default title

        self.canvas = FigureCanvasQTAgg(self.fig)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        self.plot_area_layout.addWidget(self.toolbar)
        self.plot_area_layout.addWidget(self.canvas)

        self.main_layout.addWidget(self.plot_area_frame)

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #e0e0e0;
                font-family: Arial;
                font-size: 12px;
            }
            QFrame {
                background-color: #2b2b2b;
                border: none;
            }
            QFrame[frameShape="1"] {
                background-color: #1e1e1e;
                border: 2px solid #00aaff;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                font-family: Arial;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px 15px;
                border: 1px solid #005f99;
                text-align: center;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #008cdc;
            }
            QPushButton#clear_button:hover {
                background-color: #e03a3a;
            }
            QPushButton#add_function_button {
                background-color: #4a4a4a;
                border: 1px solid #333333;
                padding: 5px 10px;
                font-size: 10px;
            }
            QPushButton#add_function_button:hover {
                background-color: #5a5a5a;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: #00ff00;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 8px;
                selection-background-color: #007acc;
                font-family: Consolas, "Courier New", monospace;
                font-size: 14px;
            }
            QScrollArea {
                background-color: #2b2b2b;
                border: none;
            }
            QScrollArea > QWidget {
                background-color: #2b2b2b;
            }
            QScrollBar:vertical {
                border: 1px solid #444444;
                background: #333333;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #666666;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QPushButton.remove_btn {
                background-color: #555555;
                color: #ffffff;
                font-size: 10px;
                font-weight: bold;
                border-radius: 4px;
                padding: 2px 5px;
                border: none;
                width: 25px;
                height: 25px;
            }
            QPushButton.remove_btn:hover {
                background-color: #777777;
            }
            /* Group Box Styles */
            QGroupBox {
                border: 1px solid #007acc;
                border-radius: 5px;
                margin-top: 1ex;
                font-family: Arial;
                font-size: 12px;
                font-weight: bold;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                background-color: #2b2b2b;
            }
            /* ComboBox Styles */
            QComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
                min-height: 24px;
            }
            QComboBox::drop-down {
                border: 0px;
                background-color: #007acc;
                width: 24px;
            }
            QComboBox::down-arrow {
                /* Place your custom white arrow down PNG here, e.g., image: url(:/icons/arrow_down_white.png); */
                width: 16px;
                height: 16px;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: #ffffff;
                selection-background-color: #007acc;
                selection-color: #ffffff;
            }
            /* CheckBox Styles */
            QCheckBox {
                color: #e0e0e0;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                /* Place your custom unchecked checkbox PNG here, e.g., image: url(:/icons/unchecked_checkbox.png); */
            }
            QCheckBox::indicator:checked {
                /* Place your custom checked checkbox PNG here, e.g., image: url(:/icons/checked_checkbox.png); */
            }
            /* SpinBox Styles */
            QDoubleSpinBox, QSpinBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QDoubleSpinBox::up-button, QSpinBox::up-button {
                background-color: #555555;
                width: 20px;
                height: 12px;
                border-top-right-radius: 3px;
            }
            QDoubleSpinBox::down-button, QSpinBox::down-button {
                background-color: #555555;
                width: 20px;
                height: 12px;
                border-bottom-right-radius: 3px;
            }
            QDoubleSpinBox::up-arrow, QSpinBox::up-arrow {
                /* Place your custom white arrow up PNG here, e.g., image: url(:/icons/arrow_up_white.png); */
            }
            QDoubleSpinBox::down-arrow, QSpinBox::down-arrow {
                /* Place your custom white arrow down PNG here, e.g., image: url(:/icons/arrow_down_white.png); */
            }
            /* Radio Button Styles */
            QRadioButton {
                color: #e0e0e0;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            QRadioButton::indicator::unchecked {
                /* Place your custom unchecked radio button PNG here, e.g., image: url(:/icons/radio_unchecked.png); */
            }
            QRadioButton::indicator::checked {
                /* Place your custom checked radio button PNG here, e.g., image: url(:/icons/radio_checked.png); */
            }
        """)

        self.add_function_button.setObjectName("add_function_button")

    def add_function_entry(self):
        """Adds a new function input entry field with a remove button."""
        entry_row_widget = QWidget()
        entry_row_layout = QHBoxLayout(entry_row_widget)
        entry_row_layout.setContentsMargins(0, 0, 0, 0)
        entry_row_layout.setSpacing(5)

        entry = QLineEdit()
        entry.setPlaceholderText("Enter function (e.g., sin(x), x**2 + 5*x, pi * cos(x))")
        entry.textChanged.connect(self.plot_functions)
        self.function_entries.append(entry)
        self.function_entries_layout.addWidget(entry_row_widget)
        
        entry_row_layout.addWidget(entry)

        remove_button = QPushButton("X")
        remove_button.setObjectName("remove_btn")
        remove_button.setFixedSize(25, 25)
        remove_button.setToolTip("Remove this function input")
        remove_button.clicked.connect(lambda: self.remove_function_entry(entry_row_widget, entry))
        entry_row_layout.addWidget(remove_button)


    def remove_function_entry(self, entry_row_widget, entry_widget):
        """Removes a specific function input entry field."""
        entry_row_widget.deleteLater()
        if entry_widget in self.function_entries:
            self.function_entries.remove(entry_widget)
        self.plot_functions()

    def plot_functions(self):
        self.ax.clear()
        
        # Reset plot styling to initial default state (or current settings state)
        self.ax.set_facecolor("#1e1e1e")
        self.ax.spines['bottom'].set_color('#cccccc')
        self.ax.spines['top'].set_color('#cccccc')
        self.ax.spines['right'].set_color('#cccccc')
        self.ax.spines['left'].set_color('#cccccc')
        self.ax.tick_params(axis='x', colors='#cccccc')
        self.ax.tick_params(axis='y', colors='#cccccc')
        self.ax.xaxis.label.set_color('#cccccc')
        self.ax.yaxis.label.set_color('#cccccc')
        self.ax.set_xlabel("X-axis: Independent Variable")
        self.ax.set_ylabel("Y-axis: Function Output")
        self.ax.set_title("Scientific Data Visualization: Logia Plot", color="#ffffff") # Default title

        # Apply settings from UI
        if self.grid_checkbox.isChecked():
            self.ax.grid(True, which='major', linestyle=':', alpha=0.6, color='#555555')
        else:
            self.ax.grid(False, which='major')
        
        if self.minor_grid_checkbox.isChecked():
            self.ax.minorticks_on()
            self.ax.grid(True, which='minor', linestyle=':', alpha=0.3, color='#444444')
        else:
            self.ax.grid(False, which='minor')
            self.ax.minorticks_off()

        # Get axis ranges and scales
        x_start = self.x_min_spinbox.value()
        x_end = self.x_max_spinbox.value()
        y_start = self.y_min_spinbox.value()
        y_end = self.y_max_spinbox.value()

        x_scale_type = "linear" if self.x_linear_radio.isChecked() else "log"
        y_scale_type = "linear" if self.y_linear_radio.isChecked() else "log"
        
        # Validate ranges and log scales without showing pop-up error
        range_error = False
        log_scale_error = False

        if x_start >= x_end:
             range_error = True
        if y_start >= y_end:
             range_error = True
        if x_scale_type == 'log' and (x_start <= 0 or x_end <= 0):
             log_scale_error = True
        if y_scale_type == 'log' and (y_start <= 0 or y_end <= 0):
             log_scale_error = True

        if range_error:
            self.ax.set_title("Logia Plot: Range Error! (X-min >= X-max or Y-min >= Y-max)", color="red")
            self.canvas.draw()
            return # Stop plotting if ranges are invalid

        if log_scale_error:
            self.ax.set_title("Logia Plot: Log Scale Error! (Range must be > 0)", color="red")
            self.canvas.draw()
            return # Stop plotting if log scale range is invalid

        # Apply valid ranges and scales
        self.ax.set_xlim(x_start, x_end)
        self.ax.set_ylim(y_start, y_end)
        self.ax.set_xscale(x_scale_type)
        self.ax.set_yscale(y_scale_type)


        x = np.linspace(x_start, x_end, 500)

        colors = ['#ff6600', '#00ff00', '#00ccff', '#ff00ff', '#ffff00', '#ff0066', '#66ff00', '#0066ff', '#800080', '#008080']

        line_style_map = {
            'Solid (-)': '-', 'Dashed (--)': '--', 'Dash-Dot (-.)': '-.', 'Dotted (:)': ':'
        }
        marker_style_map = {
            'None': None, 'Point (.)': '.', 'Pixel (P)': 'P', 'Circle (o)': 'o',
            'Square (s)': 's', 'Star (*)': '*', 'X (x)': 'x', 'Plus (+)': '+'
        }
        line_style = line_style_map[self.line_style_combo.currentText()]
        line_width = self.line_width_spinbox.value()
        marker_style = marker_style_map[self.marker_style_combo.currentText()]
        marker_size = self.marker_size_spinbox.value()

        plotted_at_least_one = False
        function_error_detected = False

        for i, entry in enumerate(self.function_entries):
            function_str = entry.text().strip()
            if function_str:
                try:
                    eval_globals = globals().copy()
                    eval_globals['x'] = x

                    y = eval(function_str, eval_globals)

                    y = np.array(y)

                    y[np.isinf(y)] = np.nan 
                    
                    self.ax.plot(x, y, label=f"f{i+1}(x) = {function_str}",
                                 color=colors[i % len(colors)],
                                 linestyle=line_style,
                                 linewidth=line_width,
                                 marker=marker_style,
                                 markersize=marker_size)
                    plotted_at_least_one = True
                except Exception as e:
                    print(f"Error evaluating function '{function_str}': {e}")
                    function_error_detected = True
        
        if plotted_at_least_one and self.legend_checkbox.isChecked():
            self.ax.legend(facecolor="#3c3c3c", edgecolor="#555555", labelcolor="#ffffff", fontsize=10, loc='best')
        
        if function_error_detected:
            self.ax.set_title("Logia Plot: Function Syntax Error Detected! (See Console)", color="red")
        elif range_error or log_scale_error:
            pass
        else:
            self.ax.set_title("Scientific Data Visualization: Logia Plot", color="#ffffff")
            
        if self.tight_layout_checkbox.isChecked():
            self.fig.tight_layout()
        
        self.canvas.draw()

    def clear_plots(self):
        self.ax.clear()
        self.ax.set_facecolor("#1e1e1e")
        self.ax.spines['bottom'].set_color('#cccccc')
        self.ax.spines['top'].set_color('#cccccc')
        self.ax.spines['right'].set_color('#cccccc')
        self.ax.spines['left'].set_color('#cccccc')
        self.ax.tick_params(axis='x', colors='#cccccc')
        self.ax.tick_params(axis='y', colors='#cccccc')
        self.ax.xaxis.label.set_color('#cccccc')
        self.ax.yaxis.label.set_color('#cccccc')
        self.ax.grid(self.grid_checkbox.isChecked(), which='major', linestyle=':', alpha=0.6, color='#555555')
        if self.minor_grid_checkbox.isChecked():
            self.ax.minorticks_on()
            self.ax.grid(True, which='minor', linestyle=':', alpha=0.3, color='#444444')
        else:
            self.ax.grid(False, which='minor')
            self.ax.minorticks_off()

        self.ax.set_xlabel("X-axis: Independent Variable")
        self.ax.set_ylabel("Y-axis: Function Output")
        self.ax.set_title("Scientific Data Visualization: Logia Plot", color="#ffffff") # Reset title to default
        
        self.ax.set_xlim(self.x_min_spinbox.value(), self.x_max_spinbox.value())
        self.ax.set_ylim(self.y_min_spinbox.value(), self.y_max_spinbox.value())
        x_scale_type = "linear" if self.x_linear_radio.isChecked() else "log"
        y_scale_type = "linear" if self.y_linear_radio.isChecked() else "log"
        self.ax.set_xscale(x_scale_type)
        self.ax.set_yscale(y_scale_type)

        self.canvas.draw()
        
        for entry in self.function_entries:
            entry.clear()
        while len(self.function_entries) > 1:
            self.remove_function_entry(self.function_entries[-1].parentWidget(), self.function_entries[-1])


    def closeEvent(self, event):
        """Handle the close event to ensure application exit."""
        plt.close(self.fig)
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    logia_ui = LogiaUI()
    sys.exit(app.exec_())
