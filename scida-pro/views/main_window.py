# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Optional
import ntpath
from PyQt5 import QtCore, QtGui, QtWidgets

from models import DataModel, FilterModel
from controllers import DataController, FilterController, PlotController, ReportController
from utils import get_config, get_logger
from .dialogs import HelpDialog


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        
        self._config = get_config()
        self._logger = get_logger()
        
        self._init_models()
        self._init_controllers()
        self._init_ui_state()
        
        self._setup_window()
        self._create_menu()
        self._create_main_frame()
        self._set_default_filters()
    
    def _init_models(self) -> None:
        self._data_model = DataModel()
        self._filter_model = FilterModel()
    
    def _init_controllers(self) -> None:
        self._data_controller = DataController(self._data_model)
        self._filter_controller = FilterController(self._filter_model)
        self._plot_controller = PlotController()
        self._report_controller = ReportController(self._data_model)
    
    def _init_ui_state(self) -> None:
        self._translator: Optional[QtCore.QTranslator] = None
        self._first_run: bool = True
        self._wid: Optional[QtWidgets.QMainWindow] = None
        
        self._series_list_model = QtGui.QStandardItemModel()
        self._series_list_model.itemChanged.connect(self._rename_dataset)
        
        self._filter_table_widget = QtWidgets.QTableWidget()
        self._clip = QtWidgets.QApplication.clipboard()
        
        self._status_text = QtWidgets.QLabel("")
        self._label_text = QtWidgets.QLabel("Data label set A")
    
    def _setup_window(self) -> None:
        self.setWindowTitle(self.tr("SCiDA Pro"))
        self.setWindowIcon(QtGui.QIcon(":ScidaPro_icon.png"))
        
        self.resize(
            self._config.get('app.window_width', 1024),
            self._config.get('app.window_height', 576)
        )
        
        frameGm = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
        
        self.setStyleSheet(f"font-size: {self._config.get('app.font_size', 12)}pt;")
    
    def _create_menu(self) -> None:
        self._create_file_menu()
        self._create_edit_menu()
        self._create_language_menu()
        self._create_help_menu()
    
    def _create_file_menu(self) -> None:
        self.file_menu = self.menuBar().addMenu(self.tr("File"))
        
        tip = self.tr("Open file")
        load_action = QtWidgets.QAction(self.tr("Open..."), self)
        load_action.setIcon(QtGui.QIcon(":open.png"))
        load_action.triggered.connect(self._load_file)
        load_action.setToolTip(tip)
        load_action.setStatusTip(tip)
        self.file_menu.addAction(load_action)
        
        tip = self.tr("Save files")
        save_action = QtWidgets.QAction(self.tr("Save..."), self)
        save_action.setIcon(QtGui.QIcon(":save.png"))
        save_action.triggered.connect(self._save_files)
        save_action.setToolTip(tip)
        save_action.setStatusTip(tip)
        self.file_menu.addAction(save_action)
        
        self.file_menu.addSeparator()
        
        tip = self.tr("Quit")
        quit_action = QtWidgets.QAction(tip, self)
        quit_action.setIcon(QtGui.QIcon(":quit.png"))
        quit_action.triggered.connect(self.close)
        quit_action.setToolTip(tip)
        quit_action.setStatusTip(tip)
        quit_action.setShortcut('Ctrl+Q')
        self.file_menu.addAction(quit_action)
    
    def _create_edit_menu(self) -> None:
        self.edit_menu = self.menuBar().addMenu(self.tr("Data labels"))
        
        format_actions = [
            (self._set_data_format0, "Data label set A"),
            (self._set_data_format1, "Data label set B"),
            (self._set_data_format2, "Data label set C"),
            (self._set_data_format3, "Data label set D"),
            (self._set_data_format4, "Custom labels"),
        ]
        
        for i, (handler, label) in enumerate(format_actions):
            tip = self.tr(label)
            action = QtWidgets.QAction(self.tr(label), self)
            action.setIcon(QtGui.QIcon(":label.png"))
            action.triggered.connect(handler)
            action.setToolTip(tip)
            action.setStatusTip(tip)
            self.edit_menu.addAction(action)
    
    def _create_language_menu(self) -> None:
        self.lang_menu = self.menuBar().addMenu(self.tr("Language"))
        
        languages = [
            (self._lang_chinese, "Chinese", "Switch to Chinese language"),
            (self._lang_korean, "Korean", "Switch to Korean language"),
            (self._lang_english, "English", "Switch to English language"),
        ]
        
        for handler, label, tip in languages:
            action = QtWidgets.QAction(self.tr(label), self)
            action.setIcon(QtGui.QIcon(":lang.png"))
            action.triggered.connect(handler)
            action.setToolTip(self.tr(tip))
            action.setStatusTip(self.tr(tip))
            self.lang_menu.addAction(action)
    
    def _create_help_menu(self) -> None:
        self.help_menu = self.menuBar().addMenu(self.tr("Help"))
        
        tip = self.tr("Help information")
        help_action = QtWidgets.QAction(self.tr("Help..."), self)
        help_action.setIcon(QtGui.QIcon(":help.png"))
        help_action.triggered.connect(self._open_help_dialog)
        help_action.setToolTip(tip)
        help_action.setStatusTip(tip)
        help_action.setShortcut('H')
        self.help_menu.addAction(help_action)
        
        tip = self.tr("About the application")
        about_action = QtWidgets.QAction(self.tr("About..."), self)
        about_action.setIcon(QtGui.QIcon(":info.png"))
        about_action.triggered.connect(self._on_about)
        about_action.setToolTip(tip)
        about_action.setStatusTip(tip)
        about_action.setShortcut('F1')
        self.help_menu.addAction(about_action)
    
    def _create_main_frame(self) -> None:
        self.setWindowTitle(self.tr("Solar cell data analysis"))
        self.main_frame = QtWidgets.QWidget()
        
        left_vbox = self._create_left_panel()
        mid_vbox = self._create_middle_panel()
        toolbar_hbox = self._create_toolbar()
        
        top_hbox = QtWidgets.QHBoxLayout()
        top_hbox.addLayout(left_vbox)
        top_hbox.addLayout(mid_vbox)
        
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(toolbar_hbox)
        vbox.addLayout(top_hbox)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
        
        self.statusBar().addWidget(self._status_text, 1)
        
        if self._first_run:
            self.statusBar().removeWidget(self._label_text)
            self._first_run = False
        
        self.statusBar().addPermanentWidget(self._label_text)
    
    def _create_left_panel(self) -> QtWidgets.QVBoxLayout:
        self._series_list_view = QtWidgets.QTreeView()
        self._series_list_view.setModel(self._series_list_model)
        self._series_list_model.setHorizontalHeaderLabels([self.tr('Data series')])
        self._series_list_view.setRootIsDecorated(False)
        self._series_list_view.setDragDropMode(QtWidgets.QAbstractItemView.NoDragDrop)
        self._series_list_view.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        
        open_files_button = QtWidgets.QPushButton()
        open_files_button.clicked.connect(self._load_file)
        open_files_button.setIcon(QtGui.QIcon(":open.png"))
        open_files_button.setToolTip(self.tr("Load files"))
        open_files_button.setStatusTip(self.tr("Load files"))
        
        save_files_button = QtWidgets.QPushButton()
        save_files_button.clicked.connect(self._save_files)
        save_files_button.setIcon(QtGui.QIcon(":save.png"))
        save_files_button.setToolTip(self.tr("Save files"))
        save_files_button.setStatusTip(self.tr("Save files"))
        
        combine_data_button = QtWidgets.QPushButton()
        combine_data_button.clicked.connect(self._combine_datasets)
        combine_data_button.setIcon(QtGui.QIcon(":combine.png"))
        combine_data_button.setToolTip(self.tr("Combine data sets"))
        combine_data_button.setStatusTip(self.tr("Combine data sets"))
        
        clear_data_button = QtWidgets.QPushButton()
        clear_data_button.clicked.connect(self._clear_data)
        clear_data_button.setIcon(QtGui.QIcon(":erase.png"))
        clear_data_button.setToolTip(self.tr("Remove all data sets"))
        clear_data_button.setStatusTip(self.tr("Remove all data sets"))
        
        buttonbox0 = QtWidgets.QDialogButtonBox()
        buttonbox0.addButton(open_files_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(save_files_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(combine_data_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(clear_data_button, QtWidgets.QDialogButtonBox.ActionRole)
        
        left_vbox = QtWidgets.QVBoxLayout()
        left_vbox.addWidget(self._series_list_view)
        left_vbox.addWidget(buttonbox0)
        
        return left_vbox
    
    def _create_middle_panel(self) -> QtWidgets.QVBoxLayout:
        self._filter_table_widget.setRowCount(self._filter_controller.max_filter_rows)
        self._filter_table_widget.setColumnCount(3)
        self._filter_table_widget.setHorizontalHeaderLabels(
            (self.tr('Parameter'), self.tr('< or >'), self.tr('Number'))
        )
        self._filter_table_widget.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self._filter_table_widget.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        
        open_filters_button = QtWidgets.QPushButton()
        open_filters_button.clicked.connect(self._load_filter_settings)
        open_filters_button.setIcon(QtGui.QIcon(":open.png"))
        open_filters_button.setToolTip(self.tr("Load filter settings"))
        open_filters_button.setStatusTip(self.tr("Load filter settings"))
        
        save_filters_button = QtWidgets.QPushButton()
        save_filters_button.clicked.connect(self._save_filter_settings)
        save_filters_button.setIcon(QtGui.QIcon(":save.png"))
        save_filters_button.setToolTip(self.tr("Save filter settings"))
        save_filters_button.setStatusTip(self.tr("Save filter settings"))
        
        check_filters_button = QtWidgets.QPushButton()
        check_filters_button.clicked.connect(self._read_filter_table)
        check_filters_button.setIcon(QtGui.QIcon(":check.png"))
        check_filters_button.setToolTip(self.tr("Check filters"))
        check_filters_button.setStatusTip(self.tr("Check filters"))
        
        execute_filters_button = QtWidgets.QPushButton()
        execute_filters_button.clicked.connect(self._filter_data)
        execute_filters_button.setIcon(QtGui.QIcon(":filter.png"))
        execute_filters_button.setToolTip(self.tr("Execute filters"))
        execute_filters_button.setStatusTip(self.tr("Execute filters"))
        
        default_filters_button = QtWidgets.QPushButton()
        default_filters_button.clicked.connect(self._set_default_filters)
        default_filters_button.setIcon(QtGui.QIcon(":revert.png"))
        default_filters_button.setToolTip(self.tr("Reload default filters"))
        default_filters_button.setStatusTip(self.tr("Reload default filters"))
        
        buttonbox1 = QtWidgets.QDialogButtonBox()
        buttonbox1.addButton(open_filters_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox1.addButton(save_filters_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox1.addButton(check_filters_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox1.addButton(execute_filters_button, QtWidgets.QDialogButtonBox.ActionRole)
        buttonbox1.addButton(default_filters_button, QtWidgets.QDialogButtonBox.ActionRole)
        
        mid_vbox = QtWidgets.QVBoxLayout()
        mid_vbox.addWidget(self._filter_table_widget)
        mid_vbox.addWidget(buttonbox1)
        
        return mid_vbox
    
    def _create_toolbar(self) -> QtWidgets.QHBoxLayout:
        report_button = QtWidgets.QPushButton()
        report_button.clicked.connect(self._make_report)
        report_button.setIcon(QtGui.QIcon(":report.png"))
        report_button.setToolTip(self.tr("Make report"))
        report_button.setStatusTip(self.tr("Make report"))
        
        openreport_button = QtWidgets.QPushButton()
        openreport_button.clicked.connect(self._open_report)
        openreport_button.setIcon(QtGui.QIcon(":link.png"))
        openreport_button.setToolTip(self.tr("Open report"))
        openreport_button.setStatusTip(self.tr("Open report"))
        
        plotselection_button = QtWidgets.QPushButton()
        plotselection_button.clicked.connect(self._open_plot_selection)
        plotselection_button.setIcon(QtGui.QIcon(":chart.png"))
        plotselection_button.setToolTip(self.tr("Plot selection"))
        plotselection_button.setStatusTip(self.tr("Plot selection"))
        
        top_buttonbox = QtWidgets.QDialogButtonBox()
        top_buttonbox.addButton(report_button, QtWidgets.QDialogButtonBox.ActionRole)
        top_buttonbox.addButton(openreport_button, QtWidgets.QDialogButtonBox.ActionRole)
        top_buttonbox.addButton(plotselection_button, QtWidgets.QDialogButtonBox.ActionRole)
        
        self._param_one_combo = QtWidgets.QComboBox(self)
        for item in self._plot_controller.plot_selection_list:
            self._param_one_combo.addItem(item)
        self._param_one_combo.setCurrentIndex(4)
        
        self._plot_selection_combo = QtWidgets.QComboBox(self)
        for item in self._plot_controller.plot_type_list:
            self._plot_selection_combo.addItem(item)
        self._plot_selection_combo.currentIndexChanged.connect(self._plot_selection_changed)
        
        toolbar_hbox = QtWidgets.QHBoxLayout()
        toolbar_hbox.addWidget(top_buttonbox)
        toolbar_hbox.addWidget(self._param_one_combo)
        toolbar_hbox.addWidget(self._plot_selection_combo)
        
        return toolbar_hbox
    
    @QtCore.pyqtSlot(int)
    def _plot_selection_changed(self, index: int) -> None:
        enabled, default_index = self._plot_controller.should_enable_param_combo(index)
        self._param_one_combo.setEnabled(enabled)
        if default_index >= 0:
            self._param_one_combo.setCurrentIndex(default_index)
    
    @QtCore.pyqtSlot(QtGui.QStandardItem)
    def _rename_dataset(self, item: QtGui.QStandardItem) -> None:
        entered_name = str(item.text())
        index = self._series_list_model.indexFromItem(item).row()
        
        success, new_name = self._data_controller.rename_dataset(index, entered_name)
        if success:
            if index in self._data_model.data:
                df = self._data_model.data[index]
                display_name = f"{new_name} ({len(df)} cells)"
                item.setText(display_name)
                item.setData(new_name, QtCore.Qt.UserRole)
        else:
            if index in self._data_model.data:
                df = self._data_model.data[index]
                display_name = f"{df.index.name} ({len(df)} cells)"
                item.setText(display_name)
    
    def _load_file(self) -> None:
        loaded_data, empty_warnings, non_ascii_warnings, read_error_warnings = \
            self._data_controller.load_files(self)
        
        for idx, df in loaded_data.items():
            display_name = f"{df.index.name} ({len(df)} cells)"
            item = QtGui.QStandardItem(display_name)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            item.setData(df.index.name, QtCore.Qt.UserRole)
            self._series_list_model.appendRow(item)
            self._logger.info(f"Added item to list: {display_name}")
        
        self._logger.info(f"Loaded data count: {len(loaded_data)}, Total data count: {len(self._data_model.data)}")
        
        if read_error_warnings:
            msg = self.tr("Error while reading data files.\n\nData labels were perhaps not recognized.")
            QtWidgets.QMessageBox.about(self, self.tr("Warning"), msg)
        
        if empty_warnings:
            msg = self.tr("Empty data sets were found.\n\nThe application only accepts data entries with a value for Voc, Isc, FF, Eta, Rser, Rsh and Irev. All values also need to be non-negative.")
            QtWidgets.QMessageBox.about(self, self.tr("Warning"), msg)
        
        if non_ascii_warnings:
            msg = self.tr("Filenames with non-ASCII characters were found.\n\nThe application currently only supports ASCII filenames.")
            QtWidgets.QMessageBox.about(self, self.tr("Warning"), msg)
        
        if self._data_model.data:
            self.statusBar().showMessage(self.tr("Ready"), 3000)
        else:
            self.statusBar().showMessage(self.tr("Please load data files"), 3000)
    
    def _save_files(self) -> None:
        success, message = self._data_controller.save_files(self)
        self.statusBar().showMessage(self.tr(message), 3000)
    
    def _combine_datasets(self) -> None:
        if len(self._data_model.data) <= 1:
            self.statusBar().showMessage(self.tr("Please load data files"), 3000)
            return
        
        self.statusBar().showMessage(self.tr("Combining data sets..."), 3000)
        
        success, message = self._data_controller.combine_datasets()
        
        self._series_list_model.clear()
        self._series_list_model.setHorizontalHeaderLabels([self.tr('Data series')])
        
        if success and self._data_model.data:
            df = list(self._data_model.data.values())[0]
            display_name = f"{df.index.name} ({len(df)} cells)"
            item = QtGui.QStandardItem(display_name)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            item.setData(df.index.name, QtCore.Qt.UserRole)
            self._series_list_model.appendRow(item)
        
        self.statusBar().showMessage(self.tr("Ready"), 3000)
    
    def _clear_data(self) -> None:
        self._data_controller.clear_data()
        self._series_list_model.clear()
        self._series_list_model.setHorizontalHeaderLabels([self.tr('Data series')])
        self.statusBar().showMessage(self.tr("All data has been cleared"), 3000)
    
    def _filter_data(self) -> None:
        if not self._data_model.data:
            self.statusBar().showMessage(self.tr("Please load data files"), 3000)
            return
        
        self.statusBar().showMessage(self.tr("Filtering data..."), 3000)
        
        self._read_filter_table()
        
        filtered_data, yield_loss = self._filter_controller.apply_filters(
            self._data_model.data
        )
        
        self._data_model._data = filtered_data
        
        self._series_list_model.clear()
        self._series_list_model.setHorizontalHeaderLabels([self.tr('Data series')])
        
        for idx, df in self._data_model.data.items():
            display_name = f"{df.index.name} ({len(df)} cells)"
            item = QtGui.QStandardItem(display_name)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            item.setData(df.index.name, QtCore.Qt.UserRole)
            self._series_list_model.appendRow(item)
        
        self.statusBar().showMessage(self.tr("Ready"), 3000)
    
    def _make_report(self) -> None:
        if not self._data_model.data:
            self.statusBar().showMessage(self.tr("Please load data files"), 3000)
            return
        
        self.statusBar().showMessage(self.tr("Making an Excel report..."), 3000)
        
        yield_loss = self._filter_controller.get_yield_loss()
        
        success, message = self._report_controller.generate_report(self, yield_loss)
        
        self.statusBar().showMessage(self.tr("Ready"), 3000)
    
    def _open_report(self) -> None:
        if not self._report_controller.report_path:
            self.statusBar().showMessage(self.tr("No report file found"), 3000)
            return
        
        self.statusBar().showMessage(self.tr("Opening report..."), 3000)
        
        success, message = self._report_controller.open_report()
        
        self.statusBar().showMessage(self.tr("Ready"), 3000)
    
    def _open_plot_selection(self) -> None:
        if not self._data_model.data:
            self.statusBar().showMessage(self.tr("Please load data files"), 3000)
            return
        
        plot_type_index = self._plot_selection_combo.currentIndex()
        param = self._param_one_combo.currentText()
        
        self._wid = self._plot_controller.create_plot(
            self,
            self._data_model.data,
            plot_type_index,
            param
        )
        
        if self._wid:
            self._wid.show()
            self.statusBar().showMessage(self.tr("Ready"), 3000)
    
    def _set_default_filters(self) -> None:
        self._filter_table_widget.clearContents()
        
        filters = self._filter_controller.default_filters
        for i, row in enumerate(filters):
            for j, column in enumerate(row):
                item = QtWidgets.QTableWidgetItem(str(column))
                self._filter_table_widget.setItem(i, j, item)
    
    def _read_filter_table(self) -> None:
        self.statusBar().showMessage(self.tr("Checking filters..."), 3000)
        
        table_data = []
        for i in range(self._filter_controller.max_filter_rows):
            row = []
            for j in range(3):
                item = self._filter_table_widget.item(i, j)
                row.append(item.text() if item else "")
            table_data.append(row)
        
        valid_filters = self._filter_controller.parse_filter_table(table_data)
        
        self._filter_table_widget.clearContents()
        for i, filter_item in enumerate(valid_filters):
            for j, value in enumerate(filter_item):
                item = QtWidgets.QTableWidgetItem(str(value))
                self._filter_table_widget.setItem(i, j, item)
        
        self.statusBar().showMessage(self.tr("Ready"), 3000)
    
    def _load_filter_settings(self) -> None:
        success, filepath, error = self._filter_controller.load_filters(
            self,
            self._data_controller.prev_dir_path
        )
        
        if success:
            self._set_user_filters()
            self.statusBar().showMessage(self.tr("New filter settings loaded"), 3000)
        elif error:
            QtWidgets.QMessageBox.about(self, self.tr("Warning"), error)
    
    def _save_filter_settings(self) -> None:
        self._read_filter_table()
        
        success, filepath, error = self._filter_controller.save_filters(
            self,
            self._data_controller.prev_dir_path
        )
        
        if success:
            self.statusBar().showMessage(self.tr("File saved"), 3000)
        elif error:
            QtWidgets.QMessageBox.about(self, self.tr("Warning"), error)
    
    def _set_user_filters(self) -> None:
        self._filter_table_widget.clearContents()
        
        filters = self._filter_controller.get_filter_table_data(use_user_filters=True)
        for i, row in enumerate(filters):
            for j, column in enumerate(row):
                item = QtWidgets.QTableWidgetItem(str(column))
                self._filter_table_widget.setItem(i, j, item)
    
    def _set_data_format0(self) -> None:
        self._data_model.label_format = 0
        self._update_label_text("Data label set A")
    
    def _set_data_format1(self) -> None:
        self._data_model.label_format = 1
        self._update_label_text("Data label set B")
    
    def _set_data_format2(self) -> None:
        self._data_model.label_format = 2
        self._update_label_text("Data label set C")
    
    def _set_data_format3(self) -> None:
        self._data_model.label_format = 3
        self._update_label_text("Data label set D")
    
    def _set_data_format4(self) -> None:
        success, message = self._data_controller.load_custom_labels(self)
        if success:
            msg = self.tr('Data series') + ": " + message
            QtWidgets.QMessageBox.about(self, self.tr("Warning"), msg)
            self._update_label_text("Custom label set")
        else:
            QtWidgets.QMessageBox.about(self, self.tr("Warning"), message)
    
    def _update_label_text(self, text: str) -> None:
        self.statusBar().removeWidget(self._label_text)
        self._label_text = QtWidgets.QLabel(text)
        self.statusBar().addPermanentWidget(self._label_text)
    
    def _lang_korean(self) -> None:
        if self._translator:
            QtWidgets.QApplication.removeTranslator(self._translator)
        
        self._translator = QtCore.QTranslator()
        self._translator.load(":IVMain_kr.qm")
        QtWidgets.QApplication.installTranslator(self._translator)
        
        self._retranslate_ui()
    
    def _lang_chinese(self) -> None:
        if self._translator:
            QtWidgets.QApplication.removeTranslator(self._translator)
        
        self._translator = QtCore.QTranslator()
        self._translator.load(":IVMain_cn.qm")
        QtWidgets.QApplication.installTranslator(self._translator)
        
        self._retranslate_ui()
    
    def _lang_english(self) -> None:
        if self._translator:
            QtWidgets.QApplication.removeTranslator(self._translator)
        
        self._retranslate_ui()
    
    def _retranslate_ui(self) -> None:
        self.menuBar().clear()
        self.create_menu()
        self._param_one_combo.clear()
        self._plot_selection_combo.clear()
        
        for item in self._plot_controller.plot_selection_list:
            self._param_one_combo.addItem(item)
        
        for item in self._plot_controller.plot_type_list:
            self._plot_selection_combo.addItem(item)
        
        self.main_frame.deleteLater()
        self._create_main_frame()
    
    def _open_help_dialog(self) -> None:
        help_dialog = HelpDialog(self)
        help_dialog.setModal(True)
        help_dialog.show()
    
    def _on_about(self) -> None:
        msg = self.tr("Solar cell data analysis\nAuthor: Ronald Naber\nLicense: Public domain")
        QtWidgets.QMessageBox.about(self, self.tr("About the application"), msg)
    
    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if e.modifiers() & QtCore.Qt.ControlModifier:
            selected = self._filter_table_widget.selectedRanges()
            
            if e.key() == QtCore.Qt.Key_V:
                if selected:
                    first_row = selected[0].topRow()
                    first_col = selected[0].leftColumn()
                    
                    for r, row in enumerate(self._clip.text().split('\n')):
                        for c, text in enumerate(row.split('\t')):
                            if len(text):
                                self._filter_table_widget.setItem(
                                    first_row + r,
                                    first_col + c,
                                    QtWidgets.QTableWidgetItem(text)
                                )
            
            elif e.key() == QtCore.Qt.Key_C:
                if selected:
                    s = ""
                    for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
                        for c in range(selected[0].leftColumn(), selected[0].rightColumn() + 1):
                            try:
                                s += str(self._filter_table_widget.item(r, c).text()) + "\t"
                            except AttributeError:
                                s += "\t"
                        s = s[:-1] + "\n"
                    self._clip.setText(s)
