# -*- coding: utf-8 -*-
"""图表设置对话框"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from PyQt5 import QtWidgets

if TYPE_CHECKING:
    from .base_plot_widget import BasePlotWidget


class PlotSettingsDialog(QtWidgets.QDialog):
    """图表设置对话框"""
    
    def __init__(self, parent: 'BasePlotWidget') -> None:
        """
        初始化设置对话框
        
        Args:
            parent: 父图表组件
        """
        super().__init__(parent)
        
        self._parent = parent
        self._plot_config = parent.get_plot_config()
        self._plot_selection = parent.get_plot_selection()
        self._data = parent.get_data()
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """设置UI"""
        self.setWindowTitle(self.tr("Plot settings"))
        vbox = QtWidgets.QVBoxLayout()
        
        # 数据集选择控件
        self.dataset_cb: list = []
        
        if self._plot_selection.single_dataset:
            for i in range(len(self._data)):
                cb = QtWidgets.QRadioButton(self._data[i].index.name)
                if i in self._plot_selection.selected_indices:
                    cb.setChecked(True)
                self.dataset_cb.append(cb)
        else:
            for i in range(len(self._data)):
                cb = QtWidgets.QCheckBox(self._data[i].index.name)
                if i in self._plot_selection.selected_indices:
                    cb.setChecked(True)
                self.dataset_cb.append(cb)
        
        # 设置区域
        group_area = QtWidgets.QGroupBox()
        group_area.setFlat(True)
        group_vbox = QtWidgets.QVBoxLayout()
        
        # 线宽设置
        if self._plot_config.linewidth_enabled:
            self.linewidth_sb = QtWidgets.QSpinBox()
            self.linewidth_sb.setAccelerated(True)
            self.linewidth_sb.setMaximum(999)
            self.linewidth_sb.setMinimum(1)
            self.linewidth_sb.setValue(self._plot_config.linewidth_selection)
            
            hbox = QtWidgets.QHBoxLayout()
            description = QtWidgets.QLabel(self.tr("Line width"))
            hbox.addWidget(self.linewidth_sb)
            hbox.addWidget(description)
            hbox.addStretch(1)
            group_vbox.addLayout(hbox)
        
        # 点大小设置
        if self._plot_config.dotsize_enabled:
            self.dotsize_sb = QtWidgets.QSpinBox()
            self.dotsize_sb.setAccelerated(True)
            self.dotsize_sb.setMaximum(999)
            self.dotsize_sb.setMinimum(1)
            self.dotsize_sb.setValue(self._plot_config.dotsize_selection)
            
            hbox = QtWidgets.QHBoxLayout()
            description = QtWidgets.QLabel(self.tr("Dot size"))
            hbox.addWidget(self.dotsize_sb)
            hbox.addWidget(description)
            hbox.addStretch(1)
            group_vbox.addLayout(hbox)
        
        # 散点量设置
        if self._plot_config.scatter_enabled:
            self.scatter_sb = QtWidgets.QDoubleSpinBox()
            self.scatter_sb.setAccelerated(True)
            self.scatter_sb.setMaximum(0.5)
            self.scatter_sb.setMinimum(0)
            self.scatter_sb.setSingleStep(0.01)
            self.scatter_sb.setDecimals(2)
            self.scatter_sb.setValue(self._plot_config.scatter_selection)
            
            hbox = QtWidgets.QHBoxLayout()
            description = QtWidgets.QLabel(self.tr("Scatter amount"))
            hbox.addWidget(self.scatter_sb)
            hbox.addWidget(description)
            hbox.addStretch(1)
            group_vbox.addLayout(hbox)
        
        # 标题设置
        if self._plot_config.title_enabled:
            self.title_cb = QtWidgets.QCheckBox(self.tr("Title"))
            self.title_cb.setChecked(self._plot_config.title_selection)
            group_vbox.addWidget(self.title_cb)
        
        # 图例设置
        if self._plot_config.legend_enabled:
            self.legend_cb = QtWidgets.QCheckBox(self.tr("Legend"))
            self.legend_cb.setChecked(self._plot_config.legend_selection)
            group_vbox.addWidget(self.legend_cb)
        
        # 网格设置
        if self._plot_config.grid_enabled:
            self.grid_cb = QtWidgets.QCheckBox(self.tr("Grid"))
            self.grid_cb.setChecked(self._plot_config.grid_selection)
            group_vbox.addWidget(self.grid_cb)
        
        group_area.setLayout(group_vbox)
        
        # 如果有任何设置选项，添加到布局
        has_settings = (
            self._plot_config.grid_enabled or
            self._plot_config.legend_enabled or
            self._plot_config.title_enabled or
            self._plot_config.dotsize_enabled or
            self._plot_config.linewidth_enabled or
            self._plot_config.scatter_enabled
        )
        
        if has_settings:
            vbox.addWidget(group_area)
        
        # 数据集选择滚动区域
        scroll_area = QtWidgets.QScrollArea()
        checkbox_widget = QtWidgets.QWidget()
        checkbox_vbox = QtWidgets.QVBoxLayout()
        
        for cb in self.dataset_cb:
            cb.setMinimumWidth(400)
            checkbox_vbox.addWidget(cb)
        
        checkbox_widget.setLayout(checkbox_vbox)
        scroll_area.setWidget(checkbox_widget)
        vbox.addWidget(scroll_area)
        
        # 按钮框
        hbox = QtWidgets.QHBoxLayout()
        buttonbox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttonbox.accepted.connect(self._read_settings)
        buttonbox.rejected.connect(self.reject)
        hbox.addStretch(1)
        hbox.addWidget(buttonbox)
        hbox.addStretch(1)
        hbox.setContentsMargins(0, 0, 0, 4)
        vbox.addLayout(hbox)
        
        self.setLayout(vbox)
        self.setMinimumWidth(800)
    
    def _read_settings(self) -> None:
        """读取设置并应用"""
        # 读取标题设置
        if self._plot_config.title_enabled:
            self._plot_config.title_selection = self.title_cb.isChecked()
        
        # 读取图例设置
        if self._plot_config.legend_enabled:
            self._plot_config.legend_selection = self.legend_cb.isChecked()
        
        # 读取网格设置
        if self._plot_config.grid_enabled:
            self._plot_config.grid_selection = self.grid_cb.isChecked()
        
        # 读取点大小设置
        if self._plot_config.dotsize_enabled:
            self._plot_config.dotsize_selection = self.dotsize_sb.value()
        
        # 读取线宽设置
        if self._plot_config.linewidth_enabled:
            self._plot_config.linewidth_selection = self.linewidth_sb.value()
        
        # 读取散点量设置
        if self._plot_config.scatter_enabled:
            self._plot_config.scatter_selection = self.scatter_sb.value()
        
        # 读取数据集选择
        self._plot_selection.selected_indices = []
        for i, cb in enumerate(self.dataset_cb):
            if cb.isChecked():
                self._plot_selection.selected_indices.append(i)
        
        # 应用设置到父组件
        self._parent.set_plot_config(self._plot_config)
        self._parent.set_plot_selection(self._plot_selection)
        
        self.close()
