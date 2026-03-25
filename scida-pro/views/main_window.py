# -*- coding: utf-8 -*-
"""主窗口 - 应用程序主界面"""

from __future__ import annotations

from typing import Optional, Dict, Any, List
from PyQt5 import QtCore, QtGui, QtWidgets

from ..controllers import DataController, PlotController, ReportController
from ..utils import ConfigManager, get_logger


class MainWindow(QtWidgets.QMainWindow):
    """应用程序主窗口"""
    
    def __init__(
        self,
        data_controller: Optional[DataController] = None,
        plot_controller: Optional[PlotController] = None,
        report_controller: Optional[ReportController] = None,
        config_manager: Optional[ConfigManager] = None,
        parent: Optional[QtWidgets.QWidget] = None
    ) -> None:
        """
        初始化主窗口
        
        Args:
            data_controller: 数据控制器
            plot_controller: 图表控制器
            report_controller: 报告控制器
            config_manager: 配置管理器
            parent: 父窗口
        """
        super().__init__(parent)
        
        self._logger = get_logger(__name__)
        self._config = config_manager or ConfigManager()
        
        # 初始化模型
        self._series_list_model = QtGui.QStandardItemModel()
        self._series_list_model.itemChanged.connect(self._on_rename_dataset)
        
        # 初始化控制器 (依赖注入)
        self._data_controller = data_controller or DataController(self._series_list_model, self._config)
        self._plot_controller = plot_controller or PlotController(self._config)
        self._report_controller = report_controller or ReportController(self._config)
        
        # 连接信号
        self._data_controller.data_loaded.connect(self._on_data_loaded)
        self._data_controller.error_occurred.connect(self._on_error)
        self._report_controller.report_error.connect(self._on_error)
        
        # 状态变量
        self._prev_dir_path = ""
        self._report_path = ""
        self._label_format = 0
        
        # 初始化UI
        self._setup_window()
        self._create_menu()
        self._create_main_frame()
    
    def _setup_window(self) -> None:
        """设置窗口属性"""
        self.setWindowTitle(self.tr("SCiDA Pro"))
        self.setWindowIcon(QtGui.QIcon(":ScidaPro_icon.png"))
        
        # 设置窗口大小并居中
        self.resize(1024, 576)
        frameGm = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
        
        # 设置字体
        self.setStyleSheet('font-size: 12pt;')
    
    def _create_menu(self) -> None:
        """创建菜单栏"""
        # 文件菜单
        file_menu = self.menuBar().addMenu(self.tr("File"))
        
        load_action = QtWidgets.QAction(self.tr("Load files"), self)
        load_action.setIcon(QtGui.QIcon(":open.png"))
        load_action.triggered.connect(self._on_load_files)
        load_action.setShortcut('Ctrl+O')
        file_menu.addAction(load_action)
        
        save_action = QtWidgets.QAction(self.tr("Save files"), self)
        save_action.setIcon(QtGui.QIcon(":save.png"))
        save_action.triggered.connect(self._on_save_files)
        save_action.setShortcut('Ctrl+S')
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        quit_action = QtWidgets.QAction(self.tr("Quit"), self)
        quit_action.setIcon(QtGui.QIcon(":quit.png"))
        quit_action.triggered.connect(self.close)
        quit_action.setShortcut('Ctrl+Q')
        file_menu.addAction(quit_action)
        
        # 编辑菜单
        edit_menu = self.menuBar().addMenu(self.tr("Edit"))
        
        combine_action = QtWidgets.QAction(self.tr("Combine datasets"), self)
        combine_action.setIcon(QtGui.QIcon(":combine.png"))
        combine_action.triggered.connect(self._on_combine_datasets)
        edit_menu.addAction(combine_action)
        
        filter_action = QtWidgets.QAction(self.tr("Filter data"), self)
        filter_action.setIcon(QtGui.QIcon(":filter.png"))
        filter_action.triggered.connect(self._on_filter_data)
        edit_menu.addAction(filter_action)
        
        # 报告菜单
        report_menu = self.menuBar().addMenu(self.tr("Report"))
        
        make_report_action = QtWidgets.QAction(self.tr("Make report"), self)
        make_report_action.setIcon(QtGui.QIcon(":report.png"))
        make_report_action.triggered.connect(self._on_make_report)
        make_report_action.setShortcut('Ctrl+R')
        report_menu.addAction(make_report_action)
        
        open_report_action = QtWidgets.QAction(self.tr("Open report"), self)
        open_report_action.setIcon(QtGui.QIcon(":open_report.png"))
        open_report_action.triggered.connect(self._on_open_report)
        report_menu.addAction(open_report_action)
    
    def _create_main_frame(self) -> None:
        """创建主框架"""
        # 中央部件
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        hbox = QtWidgets.QHBoxLayout()
        central_widget.setLayout(hbox)
        
        # 左侧：数据集列表
        left_vbox = QtWidgets.QVBoxLayout()
        
        list_label = QtWidgets.QLabel(self.tr("Data series"))
        left_vbox.addWidget(list_label)
        
        self._series_list_view = QtWidgets.QListView()
        self._series_list_view.setModel(self._series_list_model)
        left_vbox.addWidget(self._series_list_view)
        
        hbox.addLayout(left_vbox, 1)
        
        # 右侧：图表选择和控制
        right_vbox = QtWidgets.QVBoxLayout()
        
        # 图表类型选择
        plot_type_label = QtWidgets.QLabel(self.tr("Plot type"))
        right_vbox.addWidget(plot_type_label)
        
        self._plot_type_combo = QtWidgets.QComboBox()
        self._plot_type_combo.addItems([
            'Boxplot', 'Violinplot', 'Category scatter',
            'Walk-through', 'Rolling mean', 'Low to high',
            'Histogram', 'Density', 'Histogram + density',
            'Voc-Isc', 'Eta-FF', 'Rsh-FF'
        ])
        self._plot_type_combo.currentIndexChanged.connect(self._on_plot_type_changed)
        right_vbox.addWidget(self._plot_type_combo)
        
        # 参数选择
        param_label = QtWidgets.QLabel(self.tr("Parameter"))
        right_vbox.addWidget(param_label)
        
        self._param_combo = QtWidgets.QComboBox()
        self._param_combo.addItems(['Uoc', 'Isc', 'Voc*Isc', 'FF', 'Eta', 'RserLfDfIEC', 'Rsh', 'IRev1'])
        right_vbox.addWidget(self._param_combo)
        
        # 绘图按钮
        plot_button = QtWidgets.QPushButton(self.tr("Plot"))
        plot_button.clicked.connect(self._on_plot)
        right_vbox.addWidget(plot_button)
        
        right_vbox.addStretch(1)
        
        hbox.addLayout(right_vbox, 2)
        
        # 状态栏
        self._status_label = QtWidgets.QLabel(self.tr("Ready"))
        self.statusBar().addWidget(self._status_label, 1)
    
    def _on_plot_type_changed(self, index: int) -> None:
        """图表类型改变回调"""
        # 某些图表类型需要禁用参数选择
        if index < 3:  # Boxplot, Violinplot, Category scatter
            self._param_combo.setEnabled(True)
        elif 2 < index < 7:  # Walk-through, Rolling mean, Low to high
            self._param_combo.setCurrentIndex(4)  # Eta
            self._param_combo.setDisabled(True)
        else:
            self._param_combo.setDisabled(True)
    
    def _on_load_files(self) -> None:
        """加载文件"""
        file_names, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            self.tr("Load files"),
            self._prev_dir_path,
            "Excel Files (*.csv *.xls *.xlsx)"
        )
        
        if not file_names:
            return
        
        # 更新目录路径
        if file_names:
            import ntpath
            self._prev_dir_path = ntpath.dirname(file_names[0])
        
        # 加载数据
        success, warnings = self._data_controller.load_files(file_names, self._label_format)
        
        # 处理警告
        if "read_error" in warnings:
            QtWidgets.QMessageBox.warning(
                self,
                self.tr("Warning"),
                self.tr("Error while reading data files.\n\nData labels were perhaps not recognized.")
            )
        
        if "empty_data" in warnings:
            QtWidgets.QMessageBox.warning(
                self,
                self.tr("Warning"),
                self.tr("Empty data sets were found.\n\nThe application only accepts data entries with a value for Voc, Isc, FF, Eta, Rser, Rsh and Irev. All values also need to be non-negative.")
            )
        
        if "non_ascii_filename" in warnings:
            QtWidgets.QMessageBox.warning(
                self,
                self.tr("Warning"),
                self.tr("Filenames with non-ASCII characters were found.\n\nThe application currently only supports ASCII filenames.")
            )
        
        if success:
            self._status_label.setText(self.tr("Ready"))
        else:
            self._status_label.setText(self.tr("Please load data files"))
    
    def _on_save_files(self) -> None:
        """保存文件"""
        dest_dir = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            self.tr('Open directory'),
            self._prev_dir_path,
            QtWidgets.QFileDialog.ShowDirsOnly
        )
        
        if not dest_dir:
            return
        
        if self._data_controller.data_count == 0:
            self._status_label.setText(self.tr("Please load data files"))
            return
        
        self._prev_dir_path = dest_dir
        saved_files = self._data_controller.save_data(dest_dir)
        
        if saved_files:
            self._status_label.setText(self.tr("Files saved"))
    
    def _on_combine_datasets(self) -> None:
        """合并数据集"""
        if self._data_controller.combine_datasets():
            self._status_label.setText(self.tr("Ready"))
        else:
            self._status_label.setText(self.tr("Please load data files"))
    
    def _on_filter_data(self) -> None:
        """过滤数据"""
        if self._data_controller.data_count == 0:
            self._status_label.setText(self.tr("Please load data files"))
            return
        
        self._data_controller.apply_filters()
        self._status_label.setText(self.tr("Ready"))
    
    def _on_make_report(self) -> None:
        """生成报告"""
        if self._data_controller.data_count == 0:
            self._status_label.setText(self.tr("Please load data files"))
            return
        
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            self.tr("Save file"),
            self._prev_dir_path,
            "Excel Files (*.xlsx)"
        )
        
        if not file_name:
            return
        
        self._report_path = file_name
        
        success = self._report_controller.generate_excel_report(
            self._data_controller.data,
            {},  # yield_loss_data
            self._report_path
        )
        
        if success:
            self._status_label.setText(self.tr("Ready"))
    
    def _on_open_report(self) -> None:
        """打开报告"""
        if not self._report_path:
            return
        
        import os
        import platform
        
        if platform.system() == 'Windows':
            os.startfile(self._report_path)
        elif platform.system() == 'Darwin':
            import subprocess
            subprocess.call(['open', self._report_path])
        else:
            import subprocess
            subprocess.call(['xdg-open', self._report_path])
    
    def _on_plot(self) -> None:
        """绘图"""
        if self._data_controller.data_count == 0:
            self._status_label.setText(self.tr("Please load data files"))
            return
        
        plot_type_str = self._plot_type_combo.currentText()
        param = self._param_combo.currentText() if self._param_combo.isEnabled() else None
        
        # 转换图表类型
        from ..models.plot_model import PlotType
        plot_type_map = {
            'Voc-Isc': PlotType.VOC_ISC,
            'Eta-FF': PlotType.ETA_FF,
            'Rsh-FF': PlotType.RSH_FF,
            'Low to high': PlotType.LOW_TO_HIGH,
            'Density': PlotType.DENSITY,
            'Walk-through': PlotType.WALKTHROUGH,
            'Rolling mean': PlotType.ROLLING_MEAN,
            'Boxplot': PlotType.BOXPLOT,
        }
        
        plot_type = plot_type_map.get(plot_type_str)
        if plot_type is None:
            return
        
        # 创建并显示图表
        widget = self._plot_controller.create_plot(
            plot_type=plot_type,
            parent=self,
            data=self._data_controller.get_dataframes(),
            param=param
        )
        
        if widget:
            self._plot_controller.show_plot(widget)
    
    def _on_rename_dataset(self, item: QtGui.QStandardItem) -> None:
        """重命名数据集"""
        index = self._series_list_model.indexFromItem(item).row()
        new_name = item.text()
        
        if not self._data_controller.rename_dataset(index, new_name):
            # 恢复原名
            data = self._data_controller.get_data(index)
            if data:
                item.setText(data.name)
    
    def _on_data_loaded(self, index: int, name: str) -> None:
        """数据加载回调"""
        self._status_label.setText(self.tr("Ready"))
    
    def _on_error(self, message: str) -> None:
        """错误回调"""
        if message == "non_ascii_filename":
            QtWidgets.QMessageBox.warning(
                self,
                self.tr("Warning"),
                self.tr("Filenames with non-ASCII characters were found.\n\nThe application currently only supports ASCII filenames.")
            )
        else:
            QtWidgets.QMessageBox.critical(self, self.tr("Error"), message)
    
    def closeEvent(self, event: QtCore.QEvent) -> None:
        """关闭事件处理"""
        self._plot_controller.close_all_plots()
        event.accept()
