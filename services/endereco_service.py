import dask.dataframe as dd
import logging
from typing import List, Dict
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

async def get_endereco(contatos_id: int) -> List[Dict]:
    """Busca endereços usando Dask para processamento eficiente de grandes datasets"""
    logger.info(f"Buscando endereços para CONTATOS_ID: {contatos_id}")
    try:
        csv_path = Path(r"G:\SERASA DB\serasa_enderecos\srs_enderecos.csv")
        
        # Configura Dask para processar o arquivo em chunks
        ddf = dd.read_csv(csv_path,
                         blocksize="64MB",
                         header=0,  # Força primeira linha como cabeçalho
                         usecols=['CONTATOS_ID', 'LOGR_TIPO', 'LOGR_NOME', 'LOGR_NUMERO', 
                                 'LOGR_COMPLEMENTO', 'BAIRRO', 'CIDADE', 'UF', 'CEP'],
                         dtype={
                             'CONTATOS_ID': 'Int64',
                             'LOGR_TIPO': 'object',
                             'LOGR_NOME': 'object',
                             'LOGR_NUMERO': 'object',
                             'LOGR_COMPLEMENTO': 'object',
                             'BAIRRO': 'object',
                             'CIDADE': 'object',
                             'UF': 'object',
                             'CEP': 'object'
                         },
                         on_bad_lines='skip',
                         skip_blank_lines=True,  # Pula linhas em branco
                         comment='(',  # Ignora linhas que começam com (
                         assume_missing=True)
        
        # Filtra apenas os registros do CONTATOS_ID específico
        filtered_df = ddf[ddf.CONTATOS_ID == contatos_id].compute()
        
        enderecos = []
        for _, row in filtered_df.iterrows():
            if pd.notna(row['LOGR_TIPO']) and pd.notna(row['LOGR_NOME']):
                enderecos.append({
                    'logradouro': f"{row['LOGR_TIPO']} {row['LOGR_NOME']}".strip(),
                    'numero': str(row['LOGR_NUMERO']) if pd.notna(row['LOGR_NUMERO']) else '',
                    'complemento': str(row['LOGR_COMPLEMENTO']) if pd.notna(row['LOGR_COMPLEMENTO']) else '',
                    'bairro': str(row['BAIRRO']) if pd.notna(row['BAIRRO']) else '',
                    'cidade': str(row['CIDADE']) if pd.notna(row['CIDADE']) else '',
                    'uf': str(row['UF']) if pd.notna(row['UF']) else '',
                    'cep': str(row['CEP']) if pd.notna(row['CEP']) else ''
                })
            
        logger.info(f"Encontrados {len(enderecos)} endereços")
        return enderecos
            
    except Exception as e:
        logger.error(f"Erro ao buscar endereços: {str(e)}")
        return [] 