# -*- coding: utf-8 -*-
"""
Main Window for SCiDA Pro
Main application window with UI components
"""

from __future__ import division
import os
import sys
import platform
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets

from utils import ConfigManager
from models import DataCollection


class MainWindow(QtWidgets.QMainWindow):
    """Main application window"""
    
    # Signal for data loaded
    data_loaded = QtCore.pyqtSignal()
    
    def __init__(self, 
                 data_collection: Optional[DataCollection] = None,
                 config: Optional[ConfigManager] = None):
        """
        Initialize main window with dependency injection
        Args:
            data_collection: DataCollection instance (dependency injection)
            config: ConfigManager instance (dependency injection)
        """
        super().__init__()
        
        # Dependencies (injected)
        self._data_collection = data_collection or DataCollection()
        self._config = config or ConfigManager()
        
        # UI components
        self._table: Optional[QtWidgets.QTableWidget] = None
        self._filter_combos: List[QtWidgets.QComboBox] = []
        self._filter_values: List[QtWidgets.QLineEdit] = []
        self._plot_type_combo: Optional[QtWidgets.QComboBox] = None
        self._data_property_combo: Optional[QtWidgets.QComboBox] = None
        self._add_plot_button: Optional[QtWidgets.QPushButton] = None
        self._file_open_button: Optional[QtWidgets.QPushButton] = None
        self._statistics_button: Optional[QtWidgets.QPushButton] = None
        self._report_button: Optional[QtWidgets.QPushButton] = None
        
        # Filter checkboxes
        self._filter_cbs: List[QtWidgets.QCheckBox] = []
        
        # Callback functions (set by controller)
        self._load_data_callback = None
        self._save_table_callback = None
        self._show_statistics_callback = None
        self._reset_filters_callback = None
        self._apply_filters_callback = None
        self._create_report_callback = None
        self._add_plot_callback = None
        self._show_plot_callback = None
        
        # Initialize UI
        self._init_ui()
        self._connect_signals()
        
        # Apply label format (set to first format by default)
        self._data_collection.label_format = 0
    
    @property
    def data_collection(self) -> DataCollection:
        """Get data collection"""
        return self._data_collection
    
    def _init_ui(self) -> None:
        """Initialize UI components"""
        # Window setup
        window_title = self._config.get_app_setting(
            'window_title', 
            'Solar cell data analysis'
        )
        self.setWindowTitle(self.tr(window_title))
        self.setWindowIcon(QtGui.QIcon(":app-icon.png"))
        
        window_size = self._config.get_app_setting('initial_size', [1024, 576])
        self.resize(window_size[0], window_size[1])
        
        # Center window
        frame_geom = self.frameGeometry()
        center_point = QtWidgets.QDesktopWidget().availableGeometry().center()
        frame_geom.moveCenter(center_point)
        self.move(frame_geom.topLeft())
        
        # Menu bar
        self._create_menus()
        
        # Main widget and layout
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(6, 6, 6, 6)
        
        # Create toolbar section
        toolbar_layout = self._create_toolbar()
        main_layout.addLayout(toolbar_layout)
        
        # Create main content (filters + table)
        content_layout = self._create_content()
        main_layout.addLayout(content_layout, stretch=1)
        
        # Create plot section
        plot_layout = self._create_plot_section()
        main_layout.addLayout(plot_layout)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Status bar
        self.statusBar().showMessage(self.tr("Ready"))
    
    def _create_menus(self) -> None:
        """Create menu bar"""
        # File menu
        file_menu = self.menuBar().addMenu(self.tr("File"))
        
        # Open action
        open_action = QtWidgets.QAction(QtGui.QIcon(":folder-open.png"), self.tr("Open..."), self)
        open_action.triggered.connect(self._on_load_data)
        open_action.setToolTip(self.tr("Open data file(s)"))
        open_action.setStatusTip(self.tr("Open data file(s)"))
        open_action.setShortcut('Ctrl+O')
        file_menu.addAction(open_action)
        
        # Save table action
        save_table_action = QtWidgets.QAction(QtGui.QIcon(":table_save.png"), self.tr("Save table..."), self)
        save_table_action.triggered.connect(self._on_save_table)
        save_table_action.setToolTip(self.tr("Save table to file"))
        save_table_action.setStatusTip(self.tr("Save table to file"))
        file_menu.addAction(save_table_action)
        
        file_menu.addSeparator()
        
        # Quit action
        quit_action = QtWidgets.QAction(QtGui.QIcon(":quit.png"), self.tr("Quit"), self)
        quit_action.triggered.connect(self.close)
        quit_action.setToolTip(self.tr("Quit application"))
        quit_action.setStatusTip(self.tr("Quit application"))
        quit_action.setShortcut('Ctrl+Q')
        file_menu.addAction(quit_action)
        
        # Tools menu
        tools_menu = self.menuBar().addMenu(self.tr("Tools"))
        
        # Show statistics action
        stats_action = QtWidgets.QAction(self.tr("Show statistics"), self)
        stats_action.triggered.connect(self._on_show_statistics)
        stats_action.setToolTip(self.tr("Show statistics table"))
        stats_action.setStatusTip(self.tr("Show statistics table"))
        tools_menu.addAction(stats_action)
        
        # Reset filters action
        reset_filters_action = QtWidgets.QAction(self.tr("Reset filters"), self)
        reset_filters_action.triggered.connect(self._on_reset_filters)
        reset_filters_action.setToolTip(self.tr("Reset all filters to default"))
        reset_filters_action.setStatusTip(self.tr("Reset all filters to default"))
        tools_menu.addAction(reset_filters_action)
        
        # Plot menu
        plot_menu = self.menuBar().addMenu(self.tr("Plot"))
        
        # Voc-Isc plot
        voc_isc_action = QtWidgets.QAction(self.tr("Voc-Isc correlation"), self)
        voc_isc_action.triggered.connect(lambda: self._on_show_plot('voc_isc'))
        plot_menu.addAction(voc_isc_action)
        
        # Eta-FF plot
        eta_ff_action = QtWidgets.QAction(self.tr("Eta-FF correlation"), self)
        eta_ff_action.triggered.connect(lambda: self._on_show_plot('eta_ff'))
        plot_menu.addAction(eta_ff_action)
        
        # Rsh-FF plot
        rsh_ff_action = QtWidgets.QAction(self.tr("Rsh-FF correlation"), self)
        rsh_ff_action.triggered.connect(lambda: self._on_show_plot('rsh_ff'))
        plot_menu.addAction(rsh_ff_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu(self.tr("Help"))
        
        # About action
        about_action = QtWidgets.QAction(self.tr("About SCiDA"), self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
        # Help action
        help_action = QtWidgets.QAction(self.tr("Help content"), self)
        help_action.triggered.connect(self._show_help)
        help_menu.addAction(help_action)
    
    def _create_toolbar(self) -> QtWidgets.QHBoxLayout:
        """Create toolbar layout"""
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 4)
        
        # Open file button
        self._file_open_button = QtWidgets.QPushButton()
        self._file_open_button.setIcon(QtGui.QIcon(":folder-open.png"))
        self._file_open_button.setToolTip(self.tr("Open data file(s)"))
        self._file_open_button.setStatusTip(self.tr("Open data file(s)"))
        layout.addWidget(self._file_open_button)
        
        # Statistics button
        self._statistics_button = QtWidgets.QPushButton()
        self._statistics_button.setIcon(QtGui.QIcon(":graph.png"))
        self._statistics_button.setToolTip(self.tr("Show statistics and correlation"))
        self._statistics_button.setStatusTip(self.tr("Show statistics and correlation"))
        layout.addWidget(self._statistics_button)
        
        # Save table button
        self._save_table_button = QtWidgets.QPushButton()
        self._save_table_button.setIcon(QtGui.QIcon(":table_save.png"))
        self._save_table_button.setToolTip(self.tr("Save table to file"))
        self._save_table_button.setStatusTip(self.tr("Save table to file"))
        layout.addWidget(self._save_table_button)
        
        # Reset filters button
        self._reset_filters_button = QtWidgets.QPushButton()
        self._reset_filters_button.setIcon(QtGui.QIcon(":undo.png"))
        self._reset_filters_button.setToolTip(self.tr("Reset all filters to default"))
        self._reset_filters_button.setStatusTip(self.tr("Reset all filters to default"))
        layout.addWidget(self._reset_filters_button)
        
        layout.addStretch(1)
        
        # Report button
        self._report_button = QtWidgets.QPushButton()
        self._report_button.setIcon(QtGui.QIcon(":save-as.png"))
        self._report_button.setText(self.tr("Create report"))
        self._report_button.setToolTip(self.tr("Create Excel report"))
        self._report_button.setStatusTip(self.tr("Create Excel report"))
        layout.addWidget(self._report_button)
        
        return layout
    
    def _create_content(self) -> QtWidgets.QHBoxLayout:
        """Create main content layout (filters + table)"""
        layout = QtWidgets.QHBoxLayout()
        
        # Filter panel
        filter_group = QtWidgets.QGroupBox(self.tr("Data filter options"))
        filter_layout = QtWidgets.QVBoxLayout()
        
        # Create filter rows
        data_columns = self._config.get_data_columns()
        default_filters = self._config.get_default_filters()
        
        for i in range(12):
            row_layout = QtWidgets.QHBoxLayout()
            
            # Filter checkbox
            filter_cb = QtWidgets.QCheckBox(f"Filter {i+1}")
            if i < len(default_filters):
                filter_cb.setChecked(True)
            self._filter_cbs.append(filter_cb)
            
            # Column selector
            column_combo = QtWidgets.QComboBox()
            column_combo.addItems(data_columns)
            if i < len(default_filters):
                idx = column_combo.findText(default_filters[i][0])
                if idx >= 0:
                    column_combo.setCurrentIndex(idx)
            self._filter_combos.append(column_combo)
            
            # Operator selector
            op_combo = QtWidgets.QComboBox()
            op_combo.addItems(['<', '>'])
            if i < len(default_filters):
                idx = op_combo.findText(default_filters[i][1])
                if idx >= 0:
                    op_combo.setCurrentIndex(idx)
            
            # Value input
            value_edit = QtWidgets.QLineEdit()
            value_edit.setFixedWidth(60)
            if i < len(default_filters):
                value_edit.setText(str(default_filters[i][2]))
            self._filter_values.append(value_edit)
            
            # Assemble row
            row_layout.addWidget(filter_cb)
            row_layout.addWidget(column_combo)
            row_layout.addWidget(op_combo)
            row_layout.addWidget(value_edit)
            row_layout.addStretch(1)
            
            filter_layout.addLayout(row_layout)
        
        # Apply filter button
        apply_btn = QtWidgets.QPushButton(self.tr("Apply filter to all data sets"))
        apply_btn.clicked.connect(self._on_apply_filters)
        filter_layout.addWidget(apply_btn)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group, stretch=1)
        
        # Table panel
        table_group = QtWidgets.QGroupBox(self.tr("Data overview"))
        table_layout = QtWidgets.QVBoxLayout()
        
        self._table = QtWidgets.QTableWidget()
        self._table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._table.setSortingEnabled(True)
        table_layout.addWidget(self._table)
        
        table_group.setLayout(table_layout)
        layout.addWidget(table_group, stretch=2)
        
        return layout
    
    def _create_plot_section(self) -> QtWidgets.QHBoxLayout:
        """Create plot selection section"""
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 4, 0, 0)
        
        # Plot type selection
        layout.addWidget(QtWidgets.QLabel(self.tr("Plot type")))
        
        self._plot_type_combo = QtWidgets.QComboBox()
        plot_types = self._config.get_plot_types()
        self._plot_type_combo.addItems(plot_types)
        layout.addWidget(self._plot_type_combo)
        
        # Data property selection
        layout.addWidget(QtWidgets.QLabel(self.tr("Data property")))
        
        self._data_property_combo = QtWidgets.QComboBox()
        plot_selection_list = self._config.get_plot_selection_list()
        self._data_property_combo.addItems(plot_selection_list)
        layout.addWidget(self._data_property_combo)
        
        # Add plot button
        self._add_plot_button = QtWidgets.QPushButton()
        self._add_plot_button.setIcon(QtGui.QIcon(":plus.png"))
        self._add_plot_button.setText(self.tr("Add plot"))
        layout.addWidget(self._add_plot_button)
        
        return layout
    
    def _connect_signals(self) -> None:
        """Connect UI signals to slots"""
        # Toolbar buttons
        if self._file_open_button:
            self._file_open_button.clicked.connect(self._on_load_data)
        if self._statistics_button:
            self._statistics_button.clicked.connect(self._on_show_statistics)
        if self._save_table_button:
            self._save_table_button.clicked.connect(self._on_save_table)
        if self._reset_filters_button:
            self._reset_filters_button.clicked.connect(self._on_reset_filters)
        if self._report_button:
            self._report_button.clicked.connect(self._on_create_report)
        
        # Plot button
        if self._add_plot_button:
            self._add_plot_button.clicked.connect(self._on_add_plot)
    
    # Callback methods (called by UI events)
    def _on_load_data(self) -> None:
        """Handle load data button click"""
        if self._load_data_callback:
            self._load_data_callback()
    
    def _on_save_table(self) -> None:
        """Handle save table button click"""
        if self._save_table_callback:
            self._save_table_callback()
    
    def _on_show_statistics(self) -> None:
        """Handle show statistics button click"""
        if self._show_statistics_callback:
            self._show_statistics_callback()
    
    def _on_reset_filters(self) -> None:
        """Handle reset filters button click"""
        if self._reset_filters_callback:
            self._reset_filters_callback()
    
    def _on_apply_filters(self) -> None:
        """Handle apply filters button click"""
        if self._apply_filters_callback:
            self._apply_filters_callback()
    
    def _on_create_report(self) -> None:
        """Handle create report button click"""
        if self._create_report_callback:
            self._create_report_callback()
    
    def _on_add_plot(self) -> None:
        """Handle add plot button click"""
        if self._add_plot_callback:
            self._add_plot_callback()
    
    def _on_show_plot(self, plot_type: str) -> None:
        """Handle show plot menu action"""
        if self._show_plot_callback:
            self._show_plot_callback(plot_type)
    
    def _show_about(self) -> None:
        """Show about dialog"""
        from .help_dialog import HelpDialog
        HelpDialog.show_about(self)
    
    def _show_help(self) -> None:
        """Show help dialog"""
        from .help_dialog import HelpDialog
        HelpDialog.show_help(self)
    
    # UI helper methods
    def get_filter_settings(self) -> List[Tuple[str, str, float]]:
        """Get current filter settings"""
        filters = []
        
        for i in range(12):
            if not self._filter_cbs[i].isChecked():
                continue
            
            column = self._filter_combos[i].currentText()
            operator = '<' if i % 2 == 0 else '>'  # Default based on position
            # Get actual operator from combo (if we had the reference stored)
            # For now, use the combo at position 2*i + 2 from the layout
            
            # Get value
            value_text = self._filter_values[i].text()
            try:
                value = float(value_text)
            except ValueError:
                value = 0.0
            
            filters.append((column, '>', value))
        
        return filters
    
    def update_table(self, data: pd.DataFrame) -> None:
        """Update table with data"""
        if self._table is None:
            return
        
        self._table.setSortingEnabled(False)
        self._table.clear()
        
        if data.empty:
            self._table.setRowCount(0)
            self._table.setColumnCount(0)
            return
        
        # Set headers
        self._table.setColumnCount(len(data.columns))
        self._table.setRowCount(len(data.index))
        
        self._table.setHorizontalHeaderLabels(data.columns)
        if data.index.name:
            self._table.setVerticalHeaderLabels([str(i) for i in data.index])
        
        # Populate data
        for row in range(len(data.index)):
            for col in range(len(data.columns)):
                value = data.iloc[row, col]
                if pd.isna(value):
                    item = QtWidgets.QTableWidgetItem("")
                else:
                    item = QtWidgets.QTableWidgetItem(f"{value:.4f}")
                self._table.setItem(row, col, item)
        
        self._table.resizeColumnsToContents()
        self._table.setSortingEnabled(True)
    
    def show_status_message(self, message: str, timeout: int = 0) -> None:
        """Show message in status bar"""
        self.statusBar().showMessage(message, timeout)
    
    def show_warning(self, title: str, message: str) -> None:
        """Show warning dialog"""
        QtWidgets.QMessageBox.warning(self, title, message)
    
    def show_information(self, title: str, message: str) -> None:
        """Show information dialog"""
        QtWidgets.QMessageBox.information(self, title, message)
    
    def get_open_files_dialog(self) -> List[str]:
        """Show open files dialog"""
        file_filters = (
            "CSV/Excel files (*.csv *.xls *.xlsx);;"
            "CSV files (*.csv);;"
            "Excel files (*.xls *.xlsx);;"
            "All files (*.*)"
        )
        
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            self.tr("Open data file(s)"),
            "",
            file_filters
        )
        
        return files if files else []
    
    def get_save_file_dialog(self, default_name: str = "report.xlsx") -> str:
        """Show save file dialog"""
        file_filters = (
            "Excel files (*.xlsx);;"
            "CSV files (*.csv);;"
            "All files (*.*)"
        )
        
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            self.tr("Save file"),
            default_name,
            file_filters
        )
        
        return filename
