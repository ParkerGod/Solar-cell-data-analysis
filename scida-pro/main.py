# -*- coding: utf-8 -*-
"""
SCiDA Pro - 太阳能电池数据分析工具
主入口文件 (重构后)

使用MVC架构：
- models: 数据模型层
- views: 视图层 (PyQt5 UI组件)
- controllers: 控制器层 (业务逻辑)
- utils: 工具函数、配置管理、日志
"""

import sys
from PyQt5 import QtWidgets, QtGui, QtCore

# 导入MVC组件
from views import MainWindow
from controllers import DataController, PlotController, ReportController
from utils import ConfigManager

# 导入资源文件 (保持向后兼容)
try:
    import Required_resources
except ImportError:
    pass


def setup_application() -> QtWidgets.QApplication:
    """设置应用程序"""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    
    # 设置样式
    app.setStyle("Fusion")
    
    # 设置调色板
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(200, 201, 209))
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(200, 201, 209))
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(200, 201, 209))
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(255, 79, 0))
    app.setPalette(palette)
    
    return app


def create_controllers(config: ConfigManager) -> tuple:
    """
    创建控制器 (依赖注入)
    
    Args:
        config: 配置管理器
        
    Returns:
        (数据控制器, 图表控制器, 报告控制器)
    """
    # 创建模型
    from PyQt5 import QtGui
    series_list_model = QtGui.QStandardItemModel()
    
    # 创建控制器 (依赖注入配置管理器)
    data_controller = DataController(series_list_model, config)
    plot_controller = PlotController(config)
    report_controller = ReportController(config)
    
    return data_controller, plot_controller, report_controller


def main() -> int:
    """主函数"""
    # 创建应用程序
    app = setup_application()
    
    # 获取配置管理器 (单例)
    config = ConfigManager()
    
    # 创建控制器
    data_controller, plot_controller, report_controller = create_controllers(config)
    
    # 创建主窗口 (依赖注入控制器)
    window = MainWindow(
        data_controller=data_controller,
        plot_controller=plot_controller,
        report_controller=report_controller,
        config_manager=config
    )
    
    # 显示窗口
    window.show()
    
    # 运行应用程序
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
