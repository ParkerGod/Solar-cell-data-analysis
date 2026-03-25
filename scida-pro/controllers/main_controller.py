# -*- coding: utf-8 -*-
"""
Main Controller for SCiDA Pro
Handles business logic and coordinates between models and views
"""

from __future__ import division
import os
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from PyQt5 import QtWidgets

from models import DataCollection, IVDataModel
from views import (
    MainWindow,
    CorrVocIsc,
    CorrEtaFF,
    CorrRshFF,
    DistLtoH,
    DensEta,
    DistWT,
    DistRM,
    IVBoxPlot,
    ViolinPlot,
    IVHistPlot,
    IVHistDenPlot,
    CategoryScatter
)
from utils import ConfigManager, get_logger, is_number


class MainController:
    """
    Main application controller
    Coordinates between models (data) and views (UI)
    """
    
    def __init__(self, 
                 data_collection: Optional[DataCollection] = None,
                 config: Optional[ConfigManager] = None,
                 view: Optional[MainWindow] = None):
        """
        Initialize main controller with dependency injection
        Args:
            data_collection: DataCollection instance
            config: ConfigManager instance
            view: MainWindow instance
        """
        self._data_collection = data_collection or DataCollection()
        self._config = config or ConfigManager()
        self._view = view
        self._logger = get_logger()
        self._plot_windows: List[QtWidgets.QMainWindow] = []
        
        # Label formats
        self._label_formats = self._config.get_label_formats()
    
    def set_view(self, view: MainWindow) -> None:
        """Set the view and connect signals"""
        self._view = view
        self._connect_view_signals()
    
    def _connect_view_signals(self) -> None:
        """Connect view signals to controller slots via callbacks"""
        if not self._view:
            return
        
        # Set callbacks on the view
        self._view._load_data_callback = self.load_data
        self._view._save_table_callback = self.save_table
        self._view._show_statistics_callback = self.show_statistics
        self._view._reset_filters_callback = self.reset_filters
        self._view._apply_filters_callback = self.apply_filters
        self._view._create_report_callback = self.create_report
        self._view._add_plot_callback = self.add_plot
        self._view._show_plot_callback = self.show_plot
    
    def load_data(self) -> None:
        """Load data from files"""
        if not self._view:
            return
        
        files = self._view.get_open_files_dialog()
        if not files:
            return
        
        self._view.show_status_message("Loading data...")
        errors: List[str] = []
        
        for filename in files:
            dataset, status = IVDataModel.from_file(
                filename,
                self._label_formats,
                self._data_collection.label_format
            )
            
            if status == "success" and dataset is not None:
                if dataset.is_empty():
                    errors.append(f"{os.path.basename(filename)}: No valid data")
                    continue
                    
                self._data_collection.add_dataset(dataset)
                self._logger.info(f"Loaded data from {filename}")
                
            elif status == "non_ascii":
                errors.append(f"{os.path.basename(filename)}: Non-ASCII filename")
                
            elif status == "read_error":
                errors.append(f"{os.path.basename(filename)}: Read error")
        
        # Update UI
        if not self._data_collection.is_empty():
            self._update_table_view()
            self._view.show_status_message(
                f"Loaded {len(self._data_collection)} dataset(s)"
            )
        else:
            self._view.show_status_message("No data loaded")
        
        # Show errors if any
        if errors:
            error_msg = "Errors occurred:\n" + "\n".join(errors)
            self._view.show_warning("Load Errors", error_msg)
    
    def _update_table_view(self) -> None:
        """Update the table view with current data"""
        if not self._view or self._data_collection.is_empty():
            return
        
        # Combine all data for table view (show first dataset for now)
        # In a real implementation, might want to show combined or selected dataset
        combined = self._data_collection.combine_all()
        if combined is not None and not combined.is_empty():
            self._view.update_table(combined.data.head(100))  # Show first 100 rows
    
    def apply_filters(self) -> None:
        """Apply filters to all datasets"""
        if not self._view or self._data_collection.is_empty():
            return
        
        # Get filter settings from UI
        filter_settings = self._get_filter_settings()
        
        if not filter_settings:
            self._view.show_information("Filters", "No active filters")
            return
        
        # Apply filters to all datasets
        self._data_collection.apply_filters(filter_settings)
        
        # Update view
        self._update_table_view()
        
        total_removed = sum(
            ds.original_count - len(ds.data)
            for ds in self._data_collection
        )
        
        self._view.show_status_message(
            f"Filtered out {total_removed} cells"
        )
    
    def _get_filter_settings(self) -> List[Tuple[str, str, float]]:
        """Get filter settings from UI"""
        if not self._view:
            return []
        
        filters = []
        
        # Get filter UI components - need access to filter checkboxes
        # For now, use default filters from config
        default_filters = self._config.get_default_filters()
        
        # Convert to proper format
        for f in default_filters:
            if len(f) >= 3 and is_number(f[2]):
                filters.append((f[0], f[1], float(f[2])))
        
        return filters
    
    def reset_filters(self) -> None:
        """Reset all filters"""
        # Re-import data to reset filters
        # In real implementation, would need to keep original data
        self._view.show_status_message("Filters reset (reload data to apply)")
    
    def show_statistics(self) -> None:
        """Show statistics dialog"""
        if self._data_collection.is_empty():
            self._view.show_warning("Statistics", "No data available")
            return
        
        # Get statistics and correlation
        stats = self._data_collection.get_all_statistics()
        corr = self._data_collection.get_all_correlations()
        yl = self._data_collection.get_yield_loss_summary()
        
        # Create a simple dialog to show statistics
        dialog = QtWidgets.QDialog(self._view)
        dialog.setWindowTitle("Statistics and Correlation")
        dialog.setModal(True)
        dialog.resize(800, 600)
        
        layout = QtWidgets.QVBoxLayout()
        
        # Create tab widget
        tabs = QtWidgets.QTabWidget()
        
        # Statistics tab
        stats_text = QtWidgets.QTextEdit()
        stats_text.setReadOnly(True)
        stats_text.setText(self._df_to_html(stats))
        tabs.addTab(stats_text, "Statistics")
        
        # Correlation tab
        corr_text = QtWidgets.QTextEdit()
        corr_text.setReadOnly(True)
        corr_text.setText(self._df_to_html(corr))
        tabs.addTab(corr_text, "Correlation")
        
        # Yield loss tab
        yl_text = QtWidgets.QTextEdit()
        yl_text.setReadOnly(True)
        yl_text.setText(self._df_to_html(yl))
        tabs.addTab(yl_text, "Yield Loss")
        
        layout.addWidget(tabs)
        
        # Button box
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def _df_to_html(self, df: pd.DataFrame) -> str:
        """Convert DataFrame to HTML table"""
        if df.empty:
            return "<p>No data available</p>"
        
        # Format numbers
        styled = df.copy()
        for col in styled.columns:
            styled[col] = styled[col].apply(
                lambda x: f"{x:.4f}" if pd.notna(x) and is_number(x) else str(x)
            )
        
        return styled.to_html(na_rep="")
    
    def save_table(self) -> None:
        """Save table data to file"""
        if self._data_collection.is_empty():
            self._view.show_warning("Save Table", "No data available")
            return
        
        filename = self._view.get_save_file_dialog("table.csv")
        if not filename:
            return
        
        combined = self._data_collection.combine_all()
        if combined is not None:
            if combined.to_csv(filename):
                self._view.show_status_message(f"Saved to {filename}")
            else:
                self._view.show_warning("Save Table", "Failed to save file")
    
    def create_report(self) -> None:
        """Create Excel report"""
        if self._data_collection.is_empty():
            self._view.show_warning("Report", "No data available")
            return
        
        filename = self._view.get_save_file_dialog("report.xlsx")
        if not filename:
            return
        
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Write statistics
                stats = self._data_collection.get_all_statistics()
                if not stats.empty:
                    stats.to_excel(writer, sheet_name="Statistics")
                
                # Write correlation
                corr = self._data_collection.get_all_correlations()
                if not corr.empty:
                    corr.to_excel(writer, sheet_name="Correlation")
                
                # Write yield loss
                yl = self._data_collection.get_yield_loss_summary()
                if not yl.empty:
                    yl.to_excel(writer, sheet_name="Yield Loss")
                
                # Write raw data
                for ds_id, ds in self._data_collection.items():
                    sheet_name = f"Data_{ds.name[:25]}"
                    ds.data.to_excel(writer, sheet_name=sheet_name, index=False)
            
            self._view.show_status_message(f"Report saved to {filename}")
            
        except Exception as e:
            self._logger.error(f"Failed to create report: {e}")
            self._view.show_warning("Report", f"Failed to create report: {str(e)}")
    
    def add_plot(self) -> None:
        """Add plot based on UI selection"""
        if not self._view or self._data_collection.is_empty():
            return
        
        plot_type_idx = self._view._plot_type_combo.currentIndex()
        data_prop_idx = self._view._data_property_combo.currentIndex()
        
        plot_classes = [
            IVBoxPlot,
            ViolinPlot,
            CategoryScatter,
            DistWT,
            DistRM,
            DistLtoH,
            IVHistPlot,
            DensEta,
            IVHistDenPlot,
            CorrVocIsc,
            CorrEtaFF,
            CorrRshFF
        ]
        
        if 0 <= plot_type_idx < len(plot_classes):
            plot_class = plot_classes[plot_type_idx]
            
            # Some plots require data property selection
            if plot_type_idx <= 8:  # First 9 plot types use data property
                plot_window = plot_class(self._view, data_prop_idx)
            else:
                plot_window = plot_class(self._view)
            
            plot_window.show()
            self._plot_windows.append(plot_window)
    
    def show_plot(self, plot_type: str) -> None:
        """
        Show specific plot type
        Args:
            plot_type: 'voc_isc', 'eta_ff', or 'rsh_ff'
        """
        if not self._view or self._data_collection.is_empty():
            return
        
        plot_classes = {
            'voc_isc': CorrVocIsc,
            'eta_ff': CorrEtaFF,
            'rsh_ff': CorrRshFF
        }
        
        if plot_type in plot_classes:
            plot_window = plot_classes[plot_type](self._view)
            plot_window.show()
            self._plot_windows.append(plot_window)
    
    def run(self) -> None:
        """Run the application"""
        if self._view:
            self._view.show()
