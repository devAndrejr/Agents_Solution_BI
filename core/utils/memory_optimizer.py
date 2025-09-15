"""
Utilitários para otimização de memória no Agent_BI.
"""
import logging
import psutil
import pandas as pd
from typing import Dict, Any, List
import gc

logger = logging.getLogger(__name__)

class MemoryOptimizer:
    """Classe para monitoramento e otimização de uso de memória."""

    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Retorna o uso atual de memória em MB."""
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            "rss_mb": memory_info.rss / (1024 * 1024),  # Resident Set Size
            "vms_mb": memory_info.vms / (1024 * 1024),  # Virtual Memory Size
            "percent": process.memory_percent()
        }

    @staticmethod
    def log_memory_usage(operation: str):
        """Log do uso de memória para uma operação específica."""
        memory_info = MemoryOptimizer.get_memory_usage()
        logger.info(f"🔬 MEMORY USAGE - {operation}: "
                   f"RSS={memory_info['rss_mb']:.1f}MB, "
                   f"VMS={memory_info['vms_mb']:.1f}MB, "
                   f"Percent={memory_info['percent']:.1f}%")

    @staticmethod
    def check_memory_threshold(threshold_mb: float = 1000.0) -> bool:
        """Verifica se o uso de memória excede o limite."""
        memory_info = MemoryOptimizer.get_memory_usage()
        if memory_info['rss_mb'] > threshold_mb:
            logger.warning(f"⚠️ MEMORY WARNING: Usage {memory_info['rss_mb']:.1f}MB exceeds threshold {threshold_mb}MB")
            return True
        return False

    @staticmethod
    def optimize_dataframe_memory(df: pd.DataFrame) -> pd.DataFrame:
        """Otimiza o uso de memória de um DataFrame."""
        logger.info(f"📊 DATAFRAME OPTIMIZATION - Original shape: {df.shape}")
        original_memory = df.memory_usage(deep=True).sum() / (1024 * 1024)
        logger.info(f"📊 DATAFRAME OPTIMIZATION - Original memory: {original_memory:.2f}MB")

        # Otimizar tipos de dados
        for col in df.columns:
            col_type = df[col].dtype

            if col_type == 'object':
                # Tentar converter strings para categories se houver repetições
                unique_ratio = df[col].nunique() / len(df)
                if unique_ratio < 0.5:  # Se menos de 50% dos valores são únicos
                    df[col] = df[col].astype('category')

            elif 'int' in str(col_type):
                # Otimizar tipos inteiros
                if df[col].min() >= 0:
                    if df[col].max() < 255:
                        df[col] = df[col].astype('uint8')
                    elif df[col].max() < 65535:
                        df[col] = df[col].astype('uint16')
                    elif df[col].max() < 4294967295:
                        df[col] = df[col].astype('uint32')
                else:
                    if df[col].min() > -128 and df[col].max() < 127:
                        df[col] = df[col].astype('int8')
                    elif df[col].min() > -32768 and df[col].max() < 32767:
                        df[col] = df[col].astype('int16')
                    elif df[col].min() > -2147483648 and df[col].max() < 2147483647:
                        df[col] = df[col].astype('int32')

            elif 'float' in str(col_type):
                # Tentar converter float64 para float32 se possível
                if df[col].min() >= -3.4e38 and df[col].max() <= 3.4e38:
                    df[col] = df[col].astype('float32')

        optimized_memory = df.memory_usage(deep=True).sum() / (1024 * 1024)
        reduction = ((original_memory - optimized_memory) / original_memory) * 100

        logger.info(f"📊 DATAFRAME OPTIMIZATION - Optimized memory: {optimized_memory:.2f}MB")
        logger.info(f"📊 DATAFRAME OPTIMIZATION - Memory reduction: {reduction:.1f}%")

        return df

    @staticmethod
    def force_garbage_collection():
        """Força a coleta de lixo para liberar memória."""
        before = MemoryOptimizer.get_memory_usage()
        gc.collect()
        after = MemoryOptimizer.get_memory_usage()

        freed_mb = before['rss_mb'] - after['rss_mb']
        logger.info(f"🗑️ GARBAGE COLLECTION - Freed {freed_mb:.1f}MB of memory")

        return freed_mb

    @staticmethod
    def sample_large_dataset(data: List[Dict[str, Any]], max_size: int = 1000) -> List[Dict[str, Any]]:
        """Amostra um dataset grande para reduzir uso de memória."""
        if len(data) <= max_size:
            return data

        logger.warning(f"🔽 DATASET SAMPLING - Reducing from {len(data)} to {max_size} rows")

        # Amostragem estratificada simples - pega elementos uniformemente distribuídos
        step = len(data) // max_size
        sampled_data = data[::step][:max_size]

        logger.info(f"🔽 DATASET SAMPLING - Final sample size: {len(sampled_data)}")
        return sampled_data