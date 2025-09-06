import json
import logging
import os
from datetime import datetime

"""
Histórico de consultas
"""


class QueryHistory:
    def __init__(self, history_dir):
        """
        Inicializa o histórico de consultas

        Args:
            history_dir (str): Diretório para armazenar o histórico
        """
        self.history_dir = history_dir

        # Cria o diretório se não existir
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)

        # Define o arquivo de histórico para o dia atual
        filename = f"history_{datetime.now().strftime('%Y%m%d')}.json"
        self.history_file = os.path.join(self.history_dir, filename)

        # Inicializa o arquivo se não existir
        if not os.path.exists(self.history_file):
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump([], f)

        logging.info(
            f"Histórico de consultas inicializado. Arquivo: {self.history_file}"
        )

    def add_query(
        self, query, session_id=None, success=True, results_count=0, error=None
    ):
        """
        Adiciona uma consulta ao histórico

        Args:
            query (str): Consulta SQL
            session_id (str): ID da sessão
            success (bool): Indica se a consulta foi bem-sucedida
            results_count (int): Número de resultados
            error (str): Mensagem de erro (se houver)

        Returns:
            bool: True se a consulta foi adicionada com sucesso, False caso contrário
        """
        try:
            # Carrega o histórico
            with open(self.history_file, "r", encoding="utf-8") as f:
                history = json.load(f)

            # Adiciona a consulta
            history.append(
                {
                    "query": query,
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "success": success,
                    "results_count": results_count,
                    "error": error,
                }
            )

            # Salva o histórico
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)

            logging.info(f"Consulta adicionada ao histórico")

            return True

        except Exception as e:
            logging.error(f"Erro ao adicionar consulta ao histórico: {e}")
            return False

    def get_history(self, limit=100):
        """
        Obtém o histórico de consultas

        Args:
            limit (int): Número máximo de consultas a retornar

        Returns:
            list: Lista de consultas
        """
        try:
            # Carrega o histórico
            with open(self.history_file, "r", encoding="utf-8") as f:
                history = json.load(f)

            # Retorna as consultas mais recentes
            return history[-limit:]

        except Exception as e:
            logging.error(f"Erro ao obter histórico de consultas: {e}")
            return []
