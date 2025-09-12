import json
import logging
import os
import time
from datetime import datetime

"""
Gerenciador de sessões de usuário
"""


class SessionManager:
    def __init__(self, sessions_dir=None):
        """
        Inicializa o gerenciador de sessões

        Args:
            sessions_dir (str): Diretório para armazenar as sessões
        """
        if sessions_dir is None:
            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            sessions_dir = os.path.join(base_dir, "data", "sessions")

        self.sessions_dir = sessions_dir

        # Cria o diretório de sessões se não existir
        if not os.path.exists(sessions_dir):
            os.makedirs(sessions_dir)

        logging.info(f"SessionManager inicializado. Diretório: {sessions_dir}")

    def create_session(self, session_id=None):
        """
        Cria uma nova sessão

        Args:
            session_id (str): ID da sessão (opcional)

        Returns:
            str: ID da sessão criada
        """
        # Gera um ID de sessão se não fornecido
        if session_id is None:
            session_id = f"session_{int(time.time())}_{os.urandom(4).hex()}"

        # Cria o arquivo de sessão
        session_data = {
            "id": session_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": [],
        }

        # Salva a sessão
        self._save_session(session_id, session_data)

        logging.info(f"Sessão criada: {session_id}")
        return session_id

    def get_session(self, session_id):
        """
        Obtém os dados de uma sessão

        Args:
            session_id (str): ID da sessão

        Returns:
            dict: Dados da sessão ou None se não encontrada
        """
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")

        if not os.path.exists(session_path):
            logging.warning(f"Sessão não encontrada: {session_id}")
            return None

        try:
            with open(session_path, "r", encoding="utf-8") as f:
                session_data = json.load(f)

            return session_data

        except Exception as e:
            logging.error(f"Erro ao ler sessão {session_id}: {e}")
            return None

    def add_message(self, session_id, role, content):
        """
        Adiciona uma mensagem a uma sessão

        Args:
            session_id (str): ID da sessão
            role (str): Papel do remetente ("user" ou "assistant")
            content (str): Conteúdo da mensagem

        Returns:
            bool: True se a mensagem foi adicionada com sucesso, False caso contrário
        """
        # Obtém a sessão
        session_data = self.get_session(session_id)

        # Se a sessão não existir, cria uma nova
        if session_data is None:
            session_id = self.create_session(session_id)
            session_data = self.get_session(session_id)

        # Adiciona a mensagem
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }

        session_data["messages"].append(message)
        session_data["updated_at"] = datetime.now().isoformat()

        # Salva a sessão
        self._save_session(session_id, session_data)

        logging.info(f"Mensagem adicionada à sessão {session_id}")
        return True

    def get_messages(self, session_id, max_messages=None):
        """
        Obtém as mensagens de uma sessão

        Args:
            session_id (str): ID da sessão
            max_messages (int): Número máximo de mensagens a retornar

        Returns:
            list: Lista de mensagens
        """
        # Obtém a sessão
        session_data = self.get_session(session_id)

        if session_data is None:
            return []

        messages = session_data.get("messages", [])

        # Limita o número de mensagens se necessário
        if max_messages is not None and max_messages > 0:
            messages = messages[-max_messages:]

        return messages

    def delete_session(self, session_id):
        """
        Exclui uma sessão

        Args:
            session_id (str): ID da sessão

        Returns:
            bool: True se a sessão foi excluída com sucesso, False caso contrário
        """
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")

        if not os.path.exists(session_path):
            logging.warning(f"Sessão não encontrada para exclusão: {session_id}")
            return False

        try:
            os.remove(session_path)
            logging.info(f"Sessão excluída: {session_id}")
            return True

        except Exception as e:
            logging.error(f"Erro ao excluir sessão {session_id}: {e}")
            return False

    def _save_session(self, session_id, session_data):
        """
        Salva os dados de uma sessão

        Args:
            session_id (str): ID da sessão
            session_data (dict): Dados da sessão
        """
        session_path = os.path.join(self.sessions_dir, f"{session_id}.json")

        try:
            with open(session_path, "w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logging.error(f"Erro ao salvar sessão {session_id}: {e}")


if __name__ == "__main__":
    print("Rodando como script...")
    # TODO: Adicionar chamada a uma função principal se necessário
