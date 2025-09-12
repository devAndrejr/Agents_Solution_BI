#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rotas de API para o chat

Este módulo implementa as rotas de API para o processamento de
mensagens do chat.
"""

import logging
import os
from datetime import datetime

import pandas as pd
from flask import Blueprint, jsonify, request, session

from core.query_processor import QueryProcessor

logger = logging.getLogger(__name__)

# Cria o Blueprint para as rotas de chat
chat_routes = Blueprint("chat_routes", __name__, url_prefix="/api")


class ChatService:
    """
    Encapsula a lógica de negócio para o processamento de chat.
    """

    def process_message(self, user_message: str):
        """
        Processa a mensagem do usuário, lida com a lógica de fallback e
        formata a resposta.
        """
        logger.info("Processando mensagem: %s", user_message)
        try:
            processor = QueryProcessor()
            logger.info("Processador de consulta inicializado.")
            response = processor.process_query(user_message)
            logger.info("Consulta processada. Tipo da resposta: %s", type(response))
            if not isinstance(response, dict):
                response = {"type": "text", "content": str(response)}
            return self._format_response(response)
        except Exception as e:
            logger.error("Erro ao processar consulta: %s", e, exc_info=True)
            return self._format_response(
                {
                    "type": "error",
                    "error": "Erro interno do servidor",
                    "details": (
                        str(e)
                        if os.getenv("FLASK_ENV") == "development"
                        else "Contate o administrador"
                    ),
                }
            )

    def _format_response(self, response: dict) -> dict:
        """Formata a resposta final, adicionando metadados e limpando os dados."""
        response["timestamp"] = datetime.now().isoformat()
        response["session_id"] = session.get("id", "anonymous")

        # Converte recursivamente valores NaT (Not a Time) do pandas para None
        def convert_nat_to_none(obj):
            if isinstance(obj, dict):
                return {k: convert_nat_to_none(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert_nat_to_none(i) for i in obj]
            if pd.isna(obj) and isinstance(obj, type(pd.NaT)):
                return None
            return obj

        return convert_nat_to_none(response)


@chat_routes.route("/chat", methods=["POST"])
def process_chat():
    """Processa as mensagens do chat e retorna a resposta do assistente"""
    try:
        logger.info("Requisição recebida em /api/chat: %s", request.remote_addr)
        logger.debug("Headers: %s", dict(request.headers))

        data = request.get_json()
        if not data:
            raise ValueError("Dados da requisição inválidos ou ausentes")

        user_message = data.get("query", data.get("message", "")).strip()
        if not user_message:
            raise ValueError(
                "Mensagem vazia. Por favor, digite uma consulta."
            )

        chat_service = ChatService()
        response = chat_service.process_message(user_message)
        return jsonify(response), 200

    except ValueError as ve:
        logger.warning(f"Erro de validação: {str(ve)}")
        return (
            jsonify(
                {
                    "type": "error",
                    "error": str(ve),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            400,
        )

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}", exc_info=True)
        error_message = (
            "O assistente está temporariamente indisponível. "
            "Por favor, tente novamente em alguns minutos."
        )
        user_error = error_message
        return (
            jsonify(
                {
                    "type": "error",
                    "error": user_error,
                    "details": (
                        str(e)
                        if os.getenv("FLASK_ENV") == "development"
                        else None
                    ),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@chat_routes.route("/chat/upload", methods=["POST"])
def upload_chat_file():
    """
    Endpoint para upload de arquivo (CSV ou Excel) para análise rápida.
    Processa o arquivo em memória e retorna colunas e shape.
    """
    try:
        if "file" not in request.files:
            return jsonify({
                "success": False,
                "error": "Arquivo não enviado (campo 'file' ausente)."
            }), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({
                "success": False,
                "error": "Nome do arquivo vazio."
            }), 400
        filename = file.filename.lower()
        if filename.endswith(".csv"):
            df = pd.read_csv(file)
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            df = pd.read_excel(file)
        else:
            return jsonify({
                "success": False,
                "error": "Formato não suportado. Envie CSV ou Excel."
            }), 400
        return jsonify({
            "success": True,
            "filename": file.filename,
            "columns": list(df.columns),
            "shape": list(df.shape),
        }), 200
    except Exception as e:
        logger.error(
            f"Erro no upload: {str(e)}",
            exc_info=True
        )
        return jsonify({
            "success": False,
            "error": f"Erro ao processar arquivo: {str(e)}"
        }), 500
