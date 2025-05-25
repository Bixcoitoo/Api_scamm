from database.connection import get_db_connection
from typing import Dict, Optional, List
import asyncio
import logging
import apsw
from fastapi import HTTPException
from services.endereco_service import get_endereco
from pathlib import Path
import pandas as pd
from unidecode import unidecode

# Configuração do logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Cria um handler para console se não existir
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(handler)

async def get_parentes(cpf: str) -> Dict:
    try:
        with get_db_connection("SRS_MAPA_PARENTES_ANALYTICS") as conn:
            cursor = conn.cursor()
            result = cursor.execute("""
                SELECT VINCULO, CPF_VINCULO, NOME_VINCULO
                FROM SRS_MAPA_PARENTES_ANALYTICS 
                WHERE CPF_Completo = ?
            """, (cpf,))
            return [{"grau": row[0], "cpf": row[1], "nome": row[2]} for row in result]
    except Exception as e:
        print(f"Erro ao buscar parentes: {str(e)}")
        return []

async def get_irpf(cpf: str) -> Optional[Dict]:
    try:
        with get_db_connection("SRS_TB_IRPF") as conn:
            cursor = conn.cursor()
            result = cursor.execute("""
                SELECT 
                    DocNumber,
                    Instituicao_Bancaria,
                    Cod_Agencia,
                    Lote,
                    Ano_Referencia,
                    Dt_Lote,
                    Sit_Receita_Federal,
                    Dt_Consulta
                FROM SRS_TB_IRPF 
                WHERE DocNumber = ?
                ORDER BY Dt_Consulta DESC
                LIMIT 1
            """, (cpf,))
            
            row = result.fetchone()
            if row:
                return {
                    "doc_number": row[0],
                    "instituicao": row[1] or "",
                    "agencia": row[2] or "",
                    "lote": row[3] or "",
                    "ano_referencia": row[4],
                    "data_lote": row[5] or "",
                    "situacao_rf": row[6],
                    "data_consulta": row[7]
                }
            return None
            
    except Exception as e:
        logger.error(f"Erro ao buscar IRPF: {str(e)}")
        return None

async def get_score(cpf: str, contatos_conn = None) -> Optional[Dict]:
    try:
        contatos_id = None
        if contatos_conn:
            cursor = contatos_conn.cursor()
            result = cursor.execute("""
                SELECT CONTATOS_ID FROM SRS_CONTATOS WHERE CPF = ?
            """, (cpf,))
            row = result.fetchone()
            if row:
                contatos_id = row[0]
        else:
            with get_db_connection("SRS_CONTATOS") as conn:
                cursor = conn.cursor()
                result = cursor.execute("""
                    SELECT CONTATOS_ID FROM SRS_CONTATOS WHERE CPF = ?
                """, (cpf,))
                row = result.fetchone()
                if row:
                    contatos_id = row[0]

        if not contatos_id:
            return None

        with get_db_connection("SRS_TB_MODELOS_ANALYTICS_SCORE") as conn:
            cursor = conn.cursor()
            result = cursor.execute("""
                SELECT CSB8, CSB8_FAIXA, CSBA, CSBA_FAIXA
                FROM SRS_TB_MODELOS_ANALYTICS_SCORE 
                WHERE CONTATOS_ID = ?
            """, (contatos_id,))
            
            row = result.fetchone()
            if row:
                return {
                    "score_csb8": str(row[0]) if row[0] else None,
                    "faixa_csb8": row[1],
                    "score_csba": str(row[2]) if row[2] else None,
                    "faixa_csba": row[3]
                }
            return None
            
    except Exception as e:
        logger.error(f"Erro ao buscar score: {str(e)}")
        return None

async def get_pis(cpf: str, contatos_conn = None) -> Optional[str]:
    try:
        if contatos_conn:
            cursor = contatos_conn.cursor()
        else:
            with get_db_connection("SRS_CONTATOS") as conn:
                cursor = conn.cursor()
                
        result = cursor.execute("""
            SELECT CONTATOS_ID 
            FROM SRS_CONTATOS 
            WHERE CPF = ?
        """, (cpf,))
        row = result.fetchone()
        if not row:
            return None
        contatos_id = row[0]

        with get_db_connection("SRS_TB_PIS") as conn:
            cursor = conn.cursor()
            result = cursor.execute("""
                SELECT PIS
                FROM SRS_TB_PIS 
                WHERE CONTATOS_ID = ?
                ORDER BY DT_INCLUSAO DESC
                LIMIT 1
            """, (contatos_id,))
            row = result.fetchone()
            return str(row[0]) if row else None
    except Exception as e:
        print(f"Erro ao buscar PIS: {str(e)}")
        return None

async def get_poder_aquisitivo(cpf: str, contatos_conn = None) -> Optional[Dict]:
    try:
        if contatos_conn:
            cursor = contatos_conn.cursor()
        else:
            with get_db_connection("SRS_CONTATOS") as conn:
                cursor = conn.cursor()
                
        result = cursor.execute("""
            SELECT CONTATOS_ID 
            FROM SRS_CONTATOS 
            WHERE CPF = ?
        """, (cpf,))
        row = result.fetchone()
        if not row:
            return None
        contatos_id = row[0]

        try:
            with get_db_connection("SRS_TB_PODER_AQUISITIVO") as conn:
                cursor = conn.cursor()
                result = cursor.execute("""
                    SELECT 
                        PODER_AQUISITIVO,
                        RENDA_PODER_AQUISITIVO,
                        FX_PODER_AQUISITIVO,
                        COD_PODER_AQUISITIVO
                    FROM SRS_TB_PODER_AQUISITIVO 
                    WHERE CONTATOS_ID = ?
                """, (contatos_id,))
                row = result.fetchone()
                if row:
                    def decode_value(value):
                        if value is None:
                            return None
                        try:
                            return str(value)
                        except Exception as e:
                            logger.error(f"Erro ao decodificar valor: {str(e)}")
                            return None
                    
                    return {
                        "poder_aquisitivo": decode_value(row[0]),
                        "renda": decode_value(row[1]),
                        "faixa": decode_value(row[2]),
                        "codigo": decode_value(row[3])
                    }
                return None
                
        except Exception as db_error:
            logger.error(f"Erro ao acessar banco SRS_TB_PODER_AQUISITIVO: {str(db_error)}")
            return None
            
    except Exception as e:
        logger.error(f"Erro ao buscar poder aquisitivo: {str(e)}")
        return None

async def get_profissao(cpf: str, contatos_conn = None) -> Optional[Dict]:
    try:
        if contatos_conn:
            cursor = contatos_conn.cursor()
        else:
            with get_db_connection("SRS_CONTATOS") as conn:
                cursor = conn.cursor()
                
        result = cursor.execute("""
            SELECT CONTATOS_ID 
            FROM SRS_CONTATOS 
            WHERE CPF = ?
        """, (cpf,))
        row = result.fetchone()
        if not row:
            return None
        contatos_id = row[0]

        with get_db_connection("SRS_TB_PROFISSAO") as conn:
            cursor = conn.cursor()
            result = cursor.execute("""
                SELECT 
                    ID_PROFISSAO,
                    COD_PROFISSAO,
                    DESCRICAO_PROFISSAO,
                    CADASTRO_ID,
                    DT_INCLUSAO,
                    INCREMENTO,
                    ATUALIZACAO,
                    CBO_INEXISTENTE,
                    PROFISSAO_IGUAL
                FROM SRS_TB_PROFISSAO 
                WHERE CONTATOS_ID = ?
                ORDER BY DT_INCLUSAO DESC
                LIMIT 1
            """, (contatos_id,))
            row = result.fetchone()
            return {
                "id_profissao": row[0],
                "codigo": row[1],
                "descricao": row[2],
                "cadastro_id": row[3],
                "data_inclusao": row[4],
                "incremento": row[5],
                "atualizacao": row[6],
                "cbo_inexistente": row[7],
                "profissao_igual": row[8]
            } if row else None
    except Exception as e:
        print(f"Erro ao buscar profissão: {str(e)}")
        return None

async def get_dados_eleitorais(cpf: str, contatos_conn = None) -> Optional[Dict]:
    try:
        if contatos_conn:
            cursor = contatos_conn.cursor()
        else:
            with get_db_connection("SRS_CONTATOS") as conn:
                cursor = conn.cursor()
                
        result = cursor.execute("""
            SELECT CONTATOS_ID 
            FROM SRS_CONTATOS 
            WHERE CPF = ?
        """, (cpf,))
        row = result.fetchone()
        if not row:
            return None
        contatos_id = row[0]

        with get_db_connection("SRS_TB_TSE") as conn:
            cursor = conn.cursor()
            result = cursor.execute("""
                SELECT TITULO_ELEITOR, ZONA, SECAO
                FROM SRS_TB_TSE 
                WHERE CONTATOS_ID = ?
            """, (contatos_id,))
            row = result.fetchone()
            return {
                "titulo": row[0] if row else None,
                "zona": row[1] if row else None,
                "secao": row[2] if row else None
            } if row else None
    except Exception as e:
        print(f"Erro ao buscar dados eleitorais: {str(e)}")
        return None

async def get_dados_universitarios(cpf: str, contatos_conn = None) -> Optional[Dict]:
    try:
        if contatos_conn:
            cursor = contatos_conn.cursor()
        else:
            with get_db_connection("SRS_CONTATOS") as conn:
                cursor = conn.cursor()
                
        result = cursor.execute("""
            SELECT CONTATOS_ID 
            FROM SRS_CONTATOS 
            WHERE CPF = ?
        """, (cpf,))
        row = result.fetchone()
        if not row:
            return None
        contatos_id = row[0]

        with get_db_connection("SRS_TB_UNIVERSITARIOS") as conn:
            cursor = conn.cursor()
            result = cursor.execute("""
                SELECT 
                    NOME,
                    ANO_VESTIBULAR,
                    FACULDADE,
                    UF,
                    CAMPUS,
                    CURSO,
                    PERIODO_CURSADO,
                    INSCRICAO_VESTIBULAR,
                    DATA_NASCIMENTO,
                    COTA,
                    ANO_CONCULSAO,
                    DT_INCLUSAO,
                    CADASTRO_ID
                FROM SRS_TB_UNIVERSITARIOS 
                WHERE CONTATOS_ID = ?
                ORDER BY ANO_VESTIBULAR DESC
                LIMIT 1
            """, (contatos_id,))
            row = result.fetchone()
            return {
                "nome": row[0],
                "ano_vestibular": row[1],
                "faculdade": row[2],
                "uf": row[3],
                "campus": row[4],
                "curso": row[5],
                "periodo": row[6],
                "inscricao": row[7],
                "data_nascimento": row[8],
                "cota": row[9],
                "ano_conclusao": row[10],
                "data_inclusao": row[11],
                "cadastro_id": row[12]
            } if row else None
    except Exception as e:
        print(f"Erro ao buscar dados universitários: {str(e)}")
        return None

async def get_emails(cpf: str, contatos_conn = None) -> List[str]:
    logger.info(f"Iniciando busca de emails para CPF: {cpf}")
    try:
        contatos_id = None
        if contatos_conn:
            cursor = contatos_conn.cursor()
            result = cursor.execute("""
                SELECT CONTATOS_ID FROM SRS_CONTATOS WHERE CPF = ?
            """, (cpf,))
            row = result.fetchone()
            if row:
                contatos_id = row[0]
        else:
            with get_db_connection("SRS_CONTATOS") as conn:
                cursor = conn.cursor()
                result = cursor.execute("""
                    SELECT CONTATOS_ID FROM SRS_CONTATOS WHERE CPF = ?
                """, (cpf,))
                row = result.fetchone()
                if row:
                    contatos_id = row[0]

        if not contatos_id:
            logger.warning(f"CONTATOS_ID não encontrado para CPF: {cpf}")
            return []

        logger.info(f"CONTATOS_ID encontrado: {contatos_id}")
        with get_db_connection("SRS_EMAIL") as conn:
            cursor = conn.cursor()
            result = cursor.execute("""
                SELECT DISTINCT EMAIL 
                FROM SRS_EMAIL 
                WHERE CONTATOS_ID = ?
                AND EMAIL IS NOT NULL 
                AND EMAIL != ''
            """, (contatos_id,))
            emails = [row[0] for row in result.fetchall()]
            logger.info(f"Emails encontrados: {emails}")
            return emails

    except Exception as e:
        logger.error(f"Erro ao buscar emails: {str(e)}")
        return []

async def get_telefones(cpf: str, contatos_conn = None) -> List[str]:
    logger.info(f"Iniciando busca de telefones para CPF: {cpf}")
    try:
        contatos_id = None
        if contatos_conn:
            cursor = contatos_conn.cursor()
            result = cursor.execute("""
                SELECT CONTATOS_ID FROM SRS_CONTATOS WHERE CPF = ?
            """, (cpf,))
            row = result.fetchone()
            if row:
                contatos_id = row[0]
        else:
            with get_db_connection("SRS_CONTATOS") as conn:
                cursor = conn.cursor()
                result = cursor.execute("""
                    SELECT CONTATOS_ID FROM SRS_CONTATOS WHERE CPF = ?
                """, (cpf,))
                row = result.fetchone()
                if row:
                    contatos_id = row[0]

        if not contatos_id:
            logger.warning(f"CONTATOS_ID não encontrado para CPF: {cpf}")
            return []

        logger.info(f"CONTATOS_ID encontrado: {contatos_id}")
        with get_db_connection("SRS_HISTORICO_TELEFONES") as conn:
            cursor = conn.cursor()
            result = cursor.execute("""
                SELECT DISTINCT DDD || TELEFONE as telefone
                FROM SRS_HISTORICO_TELEFONES 
                WHERE CONTATOS_ID = ?
            """, (contatos_id,))
            telefones = [row[0] for row in result.fetchall()]
            logger.info(f"Telefones encontrados: {telefones}")
            return telefones
    except Exception as e:
        logger.error(f"Erro ao buscar telefones: {str(e)}")
        return []

async def get_endereco(contatos_id: str) -> List[Dict]:
    """Busca endereços usando o serviço dedicado"""
    try:
        # Removendo a tentativa de conexão SQL e usando apenas o CSV
        from services.endereco_service import get_endereco as get_endereco_service
        enderecos = await get_endereco_service(int(contatos_id))
        
        if not enderecos:
            logger.warning(f"Nenhum endereço encontrado para CONTATOS_ID: {contatos_id}")
            return []
            
        return enderecos
        
    except Exception as e:
        logger.error(f"Erro ao buscar endereços: {str(e)}")
        return []

async def _consulta_cpf(cpf: str, api_key: str):
    logger.info("\n" + "="*50)
    logger.info(f"INICIANDO CONSULTA PARA CPF: {cpf}")
    logger.info("="*50)
    
    try:
        logger.info("\n[1/8] Buscando dados básicos...")
        with get_db_connection("SRS_CONTATOS") as conn:
            cursor = conn.cursor()
            result = cursor.execute("""
                SELECT NOME, CPF, NASC, NOME_MAE, NOME_PAI, SEXO, CONTATOS_ID
                FROM SRS_CONTATOS 
                WHERE CPF = ?
            """, (cpf,))
            
            pessoa = result.fetchone()
            if not pessoa:
                logger.error("❌ Pessoa não encontrada")
                raise HTTPException(status_code=404, detail="Pessoa não encontrada")
            
            logger.info("✓ Dados básicos encontrados:")
            logger.info(f"  Nome: {pessoa[0]}")
            logger.info(f"  CPF: {pessoa[1]}")
            logger.info(f"  Nascimento: {pessoa[2]}")
            logger.info(f"  Nome Mãe: {pessoa[3]}")
            logger.info(f"  Nome Pai: {pessoa[4]}")
            logger.info(f"  Sexo: {pessoa[5]}")
            logger.info(f"  CONTATOS_ID: {pessoa[6]}")
            
            logger.info("\n[2/8] Buscando emails...")
            emails = await get_emails(cpf, conn)
            logger.info(f"✓ Emails: {emails if emails else 'Não encontrado'}")
            
            logger.info("\n[3/8] Buscando telefones...")
            telefones = await get_telefones(cpf, conn)
            logger.info(f"✓ Telefones: {telefones if telefones else 'Não encontrado'}")
            
            logger.info("\n[4/8] Buscando endereços...")
            enderecos = await get_endereco(pessoa[6])
            logger.info(f"✓ Endereços: {enderecos if enderecos else 'Não encontrado'}")

            logger.info("\n[5/8] Buscando dados financeiros...")
            score = await get_score(cpf, conn)
            irpf = await get_irpf(cpf)
            logger.info(f"✓ Score: {score if score else 'Não encontrado'}")
            logger.info(f"✓ IRPF: {irpf if irpf else 'Não encontrado'}")

            logger.info("\n[6/8] Buscando dados profissionais...")
            pis = await get_pis(cpf, conn)
            profissao = await get_profissao(cpf, conn)
            logger.info(f"✓ PIS: {pis if pis else 'Não encontrado'}")
            logger.info(f"✓ Profissão: {profissao if profissao else 'Não encontrado'}")

            logger.info("\n[7/8] Buscando dados educacionais...")
            educacao = await get_dados_universitarios(cpf, conn)
            logger.info(f"✓ Educação: {educacao if educacao else 'Não encontrado'}")

            logger.info("\n[8/8] Buscando dados eleitorais...")
            eleitoral = await get_dados_eleitorais(cpf, conn)
            logger.info(f"✓ Dados Eleitorais: {eleitoral if eleitoral else 'Não encontrado'}")

            logger.info("\n" + "="*50)
            logger.info("CONSULTA FINALIZADA COM SUCESSO")
            logger.info("="*50 + "\n")

            return {
                "dados_basicos": {
                    "nome": pessoa[0],
                    "cpf": pessoa[1],
                    "nascimento": pessoa[2],
                    "nome_mae": pessoa[3],
                    "nome_pai": pessoa[4],
                    "sexo": pessoa[5]
                },
                "contatos": {
                    "emails": emails,
                    "telefones": telefones
                },
                "enderecos": enderecos,
                "financeiro": {
                    "score": score,
                    "irpf": irpf
                },
                "profissional": {
                    "pis": pis,
                    "profissao": profissao
                },
                "educacao": educacao,
                "eleitoral": eleitoral
            }
    except Exception as e:
        logger.error(f"Erro na consulta: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao consultar dados: {str(e)}"
        )

async def consulta_nome(nome: str, limit: int = 10) -> List[Dict]:
    try:
        async with get_db_connection() as conn:
            # Normaliza o nome para busca
            nome_busca = unidecode(nome.upper())
            nomes = nome_busca.split()
            
            if len(nomes) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="Forneça nome e sobrenome"
                )

            # Query otimizada usando índice GIN e ts_vector
            query = """
                SELECT 
                    nome, cpf, nasc as nascimento,
                    nome_mae, nome_pai, sexo,
                    similarity(unaccent(upper(nome)), unaccent($1)) as score
                FROM srs_contatos
                WHERE 
                    to_tsvector('portuguese', unaccent(nome)) @@ 
                    to_tsquery('portuguese', $2)
                ORDER BY score DESC
                LIMIT $3
            """
            
            # Prepara termos de busca
            search_terms = ' & '.join(nomes)
            
            # Executa query
            rows = await conn.fetch(query, nome_busca, search_terms, limit)
            
            return [dict(row) for row in rows]
            
    except Exception as e:
        logger.error(f"Erro na consulta: {str(e)}")
        raise