# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from utils import get_config, get_logger


class ReportModel:
    def __init__(self) -> None:
        self._config = get_config()
        self._logger = get_logger()
        
        self._summary_index = self._config.get('report.summary_index', 
            ['Best cell', 'Median', 'Average', 'Std.dev.'])
        self._summary_columns = self._config.get('report.summary_columns',
            ['Voc [V]', 'Isc [A]', 'Rser [mOhm*cm2]', 'Rshunt [kOhm]', 'FF [%]', 'Eta [%]', 'Irev [A]'])
        self._rounding = self._config.get('report.rounding', [3, 2, 2, 2, 1, 2, 2])
        
        self._summaries: List[pd.DataFrame] = []
        self._correlations: List[pd.DataFrame] = []
        self._yield_loss_output: List[pd.DataFrame] = []
    
    @property
    def summaries(self) -> List[pd.DataFrame]:
        return self._summaries
    
    @property
    def correlations(self) -> List[pd.DataFrame]:
        return self._correlations
    
    @property
    def yield_loss_output(self) -> List[pd.DataFrame]:
        return self._yield_loss_output
    
    def generate_summaries(
        self,
        data: Dict[int, pd.DataFrame]
    ) -> List[pd.DataFrame]:
        self._summaries = []
        
        for idx, df in data.items():
            smr = pd.DataFrame(index=self._summary_index, columns=self._summary_columns)
            smr.index.name = 'Data property'
            smr['Data set'] = f"{df.index.name} ({len(df)} cells)"
            smr = smr.set_index('Data set', append=True).swaplevel(0, 1)
            
            for col_idx, col_name in enumerate(df.columns):
                if col_idx < len(self._summary_columns):
                    smr.iloc[0, col_idx] = df.iloc[df[col_name].idxmax()][col_name] if col_name in df.columns else np.nan
                    smr.iloc[1, col_idx] = df[col_name].median() if col_name in df.columns else np.nan
                    smr.iloc[2, col_idx] = df[col_name].mean() if col_name in df.columns else np.nan
                    
                    if col_idx in [0, 1, 4, 5]:
                        smr.iloc[3, col_idx] = df[col_name].std() if len(df) > 1 else np.nan
                    else:
                        smr.iloc[3, col_idx] = np.nan
            
            smr = smr.apply(pd.to_numeric, errors='coerce')
            
            if 'RserLfDfIEC' in df.columns:
                smr.iloc[:, 2] = smr.iloc[:, 2] * 1000
            if 'Rsh' in df.columns:
                smr.iloc[:, 3] = smr.iloc[:, 3] / 1000
            
            for col_idx, decimals in enumerate(self._rounding):
                if col_idx < len(smr.columns):
                    smr.iloc[:, col_idx] = np.round(smr.iloc[:, col_idx].astype(np.double), decimals=decimals)
            
            self._summaries.append(smr)
        
        return self._summaries
    
    def generate_correlations(
        self,
        data: Dict[int, pd.DataFrame]
    ) -> List[pd.DataFrame]:
        self._correlations = []
        
        for idx, df in data.items():
            if len(df) <= 1:
                continue
            
            corr = np.round(df.corr(), decimals=2)
            corr.iloc[:, 2:4] = np.nan
            corr.iloc[2:4, :] = np.nan
            corr.iloc[6, :] = np.nan
            corr.iloc[:, 6] = np.nan
            corr = corr.dropna(0, 'all').T.dropna(0, 'all')
            corr.index.name = 'Data property'
            corr['Data set'] = f"{df.index.name} ({len(df)} cells)"
            corr = corr.set_index('Data set', append=True).swaplevel(0, 1)
            
            self._correlations.append(corr)
        
        return self._correlations
    
    def generate_yield_loss_output(
        self,
        yield_loss: List[pd.DataFrame],
        data: Dict[int, pd.DataFrame]
    ) -> List[pd.DataFrame]:
        self._yield_loss_output = yield_loss[:]
        
        for idx, yl_df in enumerate(self._yield_loss_output):
            yl_df['Total'] = np.nan
            yl_df.iloc[1, 12] = yl_df.iloc[1, :].sum()
            
            yl_df.loc['Loss %'] = np.nan
            for col_idx in range(len(yl_df.columns)):
                try:
                    total_count = int(yl_df.index.name)
                    loss_count = yl_df.iloc[1, col_idx]
                    if not pd.isna(loss_count) and total_count > 0:
                        yl_df.iloc[2, col_idx] = np.round(100 * loss_count / total_count, decimals=2)
                except Exception:
                    pass
            
            yl_df = yl_df.dropna(1, 'all')
            yl_df.index.name = 'Data property'
            
            if idx in data:
                yl_df['Data set'] = f"{data[idx].index.name} ({yl_df.index.name} cells)"
            yl_df = yl_df.set_index('Data set', append=True).swaplevel(0, 1)
            
            self._yield_loss_output[idx] = yl_df
        
        return self._yield_loss_output
    
    def export_to_excel(
        self,
        filepath: str,
        summaries: Optional[List[pd.DataFrame]] = None,
        yield_loss: Optional[List[pd.DataFrame]] = None,
        correlations: Optional[List[pd.DataFrame]] = None
    ) -> Tuple[bool, str]:
        try:
            writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
            
            if summaries:
                output = pd.concat(summaries)
                output.to_excel(writer, 'Summary')
            
            if yield_loss:
                output = pd.concat(yield_loss)
                output.to_excel(writer, 'Yield loss')
            
            if correlations:
                output = pd.concat(correlations)
                output.to_excel(writer, 'Correlation')
            
            writer.close()
            return True, ""
        except Exception as e:
            self._logger.error(f"Failed to export report: {e}")
            return False, str(e)
