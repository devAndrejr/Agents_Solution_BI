import json
import logging
import os
from typing import Any, Dict, Optional

import pyodbc

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logs/mcp_sqlserver.log",
    filemode="a",
)
logger = logging.getLogger("mcp_sqlserver_adapter")


class SQLServerMCPAdapter:
    """
    Adaptador MCP para SQL Server que implementa processamento distribuído
    utilizando recursos nativos do SQL Server como stored procedures,
    particionamento de dados e jobs.
    """

    def __init__(self, config_file: str = None):
        """
        Inicializa o adaptador MCP para SQL Server

        Args:
            config_file (str, optional): Caminho para o arquivo de configuração.
                Se não fornecido, usa o padrão em data/sqlserver_mcp_config.json
                ou as credenciais diretamente do arquivo .env
        """
        # Carrega as variáveis do arquivo .env para garantir acesso às credenciais
        from dotenv import load_dotenv

        load_dotenv()

        self.config_file = config_file or os.path.join(
            os.getcwd(), "data", "sqlserver_mcp_config.json"
        )
        self.config = self._load_config()
        self.connection = None
        self.is_available = self._check_availability()

        # Registra informações sobre a conexão
        conn_info = self.config.get("connection", {})
        logger.info(
            f"SQLServerMCPAdapter inicializado para servidor: {conn_info.get('server')}/{conn_info.get('database')}"
        )
        logger.info(f"Status de disponibilidade: {self.is_available}")

    def _load_config(self) -> dict:
        """
        Carrega a configuração do adaptador do arquivo JSON
        ou das variáveis de ambiente se o arquivo não existir

        Returns:
            dict: Configuração carregada
        """
        try:
            # Tenta carregar do arquivo de configuração
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                logger.info(f"Configuração carregada do arquivo: {self.config_file}")
                return config
            else:
                # Se o arquivo não existir, usa as variáveis de ambiente
                from dotenv import load_dotenv

                load_dotenv()

                # Constrói a string de conexão diretamente das variáveis de ambiente
                # Usando r-string para evitar problemas com a barra invertida
                driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
                server = os.getenv("DB_SERVER", r"FAMILIA\SQLJR")
                database = os.getenv("DB_DATABASE", "Projeto_Opcom")
                user_env = os.getenv("DB_USER")
                user = user_env if user_env else "AgenteVirtual"
                password_env = os.getenv("DB_PASSWORD")
                password = password_env if password_env else "Cacula@2020"

                conn_string = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={user};PWD={password};"

                if os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes") == "yes":
                    conn_string += "TrustServerCertificate=yes;"

                # Cria configuração a partir das variáveis de ambiente
                config = {
                    "connection": {
                        "connection_string": conn_string,
                        "server": server,
                        "database": database,
                        "username": user,
                        "password": password,
                        "driver": driver,
                        "trust_server_certificate": os.getenv(
                            "DB_TRUST_SERVER_CERTIFICATE", "yes"
                        ),
                    },
                    "processing": {
                        "max_threads": int(os.getenv("MCP_MAX_THREADS", "4")),
                        "timeout": int(os.getenv("MCP_TIMEOUT", "30")),
                        "use_stored_procedures": os.getenv(
                            "MCP_USE_STORED_PROCEDURES", "yes"
                        )
                        == "yes",
                    },
                }
                logger.info("Configuração carregada das variáveis de ambiente")
                return config
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {str(e)}")
            # Retorna configuração padrão em caso de erro
            return {
                "connection": {
                    "server": "localhost",
                    "database": "master",
                    "username": "sa",
                    "password": "",
                    "driver": "ODBC Driver 18 for SQL Server",
                    "trust_server_certificate": "yes",
                },
                "processing": {
                    "max_threads": 4,
                    "timeout": 30,
                    "use_stored_procedures": True,
                },
            }

    def _check_availability(self) -> bool:
        """
        Verifica se o SQL Server está disponível e se as stored procedures necessárias estão instaladas
        Também verifica se o modo de dados mockados está ativado no arquivo .env

        Returns:
            bool: True se o SQL Server estiver disponível, False caso contrário
        """
        # Verifica se o modo de dados mockados está ativado
        use_mock_data = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
        if use_mock_data:
            logger.info(
                "Modo de dados mockados ativado no arquivo .env. Ignorando verificação de disponibilidade do SQL Server."
            )
            # Mesmo com dados mockados, marcamos como indisponível para que o sistema use o fallback
            return False

        try:
            # Tenta estabelecer uma conexão com o SQL Server
            conn = self._get_connection()
            if conn is None:
                logger.warning("Não foi possível estabelecer conexão com o SQL Server")
                return False

            # Verifica se as stored procedures necessárias existem
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*) FROM sys.objects
                WHERE type = 'P' AND name = 'sp_mcp_process_query'
            """
            )
            count = cursor.fetchone()[0]

            # Fecha a conexão
            conn.close()

            # Verifica se a stored procedure principal existe (deve haver 1)
            if count < 1:
                logger.warning(
                    f"A stored procedure 'sp_mcp_process_query' não foi encontrada. Encontradas: {count}/1"
                )
                return False

            logger.info(
                "SQL Server disponível e todas as stored procedures necessárias estão instaladas"
            )
            return True
        except Exception as e:
            logger.error(f"Erro ao verificar disponibilidade do SQL Server: {str(e)}")
            return False

    def _get_connection(self) -> Optional[pyodbc.Connection]:
        """
        Obtém uma conexão com o SQL Server com mecanismo de retry

        Returns:
            Optional[pyodbc.Connection]: Conexão com o SQL Server ou None em caso de erro
        """
        import time

        max_retries = 3
        retry_delay = 2

        # Verifica se o modo de dados mockados está ativado
        use_mock_data = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
        if use_mock_data:
            # Se estamos usando dados mockados, não precisamos tentar conectar ao banco
            # mas ainda retornamos None para que o sistema saiba que não há conexão real
            logger.info(
                "Modo de dados mockados ativado. Ignorando tentativa de conexão com o SQL Server."
            )
            return None

        for attempt in range(max_retries):
            try:
                # Verifica se já existe uma conexão ativa
                if self.connection is not None:
                    try:
                        # Testa a conexão existente
                        self.connection.cursor().execute("SELECT 1")
                        return self.connection
                    except Exception as e:
                        logger.warning(
                            f"Conexão existente falhou: {str(e)}. Criando nova conexão..."
                        )
                        # Se a conexão existente falhar, fecha-a e cria uma nova
                        try:
                            self.connection.close()
                        except:
                            pass
                        self.connection = None

                # Obtém os parâmetros de conexão da configuração
                conn_config = self.config.get("connection", {})

                # Verifica se há uma string de conexão completa na configuração
                if (
                    "connection_string" in conn_config
                    and conn_config["connection_string"]
                ):
                    conn_string = conn_config["connection_string"]
                    # Garante que os parâmetros de segurança estejam presentes
                    if "Encrypt=no" not in conn_string:
                        conn_string += "Encrypt=no;"
                else:
                    # Constrói a string de conexão a partir dos parâmetros individuais
                    driver = conn_config.get("driver", "ODBC Driver 18 for SQL Server")
                    server = conn_config.get("server", "localhost")
                    database = conn_config.get("database", "master")
                    username = conn_config.get("username", "sa")
                    password = conn_config.get("password", "")
                    trust_cert = conn_config.get("trust_server_certificate", "yes")

                    # Garantindo que a string de conexão seja formada corretamente
                    conn_string = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};"

                    # Adiciona parâmetros de segurança e timeout
                    if trust_cert == "yes":
                        conn_string += "TrustServerCertificate=yes;"
                    conn_string += "Encrypt=no;Connection Timeout=30;"

                logger.info(
                    f"Tentando conectar ao SQL Server (tentativa {attempt + 1}/{max_retries})"
                )
                # Estabelece a conexão
                self.connection = pyodbc.connect(conn_string)
                logger.info("Conexão com SQL Server estabelecida com sucesso")
                return self.connection
            except pyodbc.Error as e:
                erro_msg = str(e).lower()
                if "08001" in erro_msg or "named pipes provider" in erro_msg:
                    logger.error(
                        f"Erro de conexão: Servidor SQL não está acessível (tentativa {attempt + 1}/{max_retries})"
                    )
                elif "28000" in erro_msg or "login failed" in erro_msg:
                    logger.error(
                        f"Erro de autenticação: Credenciais inválidas (tentativa {attempt + 1}/{max_retries})"
                    )
                elif "42000" in erro_msg:
                    logger.error(
                        f"Erro de permissão: Usuário não tem acesso ao banco de dados (tentativa {attempt + 1}/{max_retries})"
                    )
                elif "timeout" in erro_msg:
                    logger.error(
                        f"Erro de timeout: Conexão expirou (tentativa {attempt + 1}/{max_retries})"
                    )
                else:
                    logger.error(
                        f"Erro ao estabelecer conexão com o SQL Server (tentativa {attempt + 1}/{max_retries}): {str(e)}"
                    )

                # Registra a string de conexão em caso de erro (ocultando a senha)
                safe_conn_string = (
                    conn_string.replace(password, "*****")
                    if "conn_string" in locals()
                    else "N/A"
                )
                logger.debug(f"String de conexão utilizada: {safe_conn_string}")

                if attempt < max_retries - 1:
                    logger.info(
                        f"Aguardando {retry_delay} segundos antes da próxima tentativa..."
                    )
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error(
                        "Todas as tentativas de conexão falharam. Verifique as configurações do servidor SQL."
                    )
                return None
        return None

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Processa uma consulta SQL usando o adaptador MCP

        Args:
            query (str): A consulta a ser processada

        Returns:
            Dict[str, Any]: Resultado do processamento da consulta
        """
        try:
            if not self.is_available:
                # Verifica se o modo de dados mockados está ativado
                use_mock_data = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
                if use_mock_data:
                    logger.info("Usando dados mockados para processar a consulta")
                    # Importa o provedor de dados mockados
                    try:
                        from core.mcp.mock_data import MockDataProvider

                        return MockDataProvider.process_query(query)
                    except ImportError as e:
                        logger.error(
                            f"Erro ao importar provedor de dados mockados: {str(e)}"
                        )
                        # Continua com a mensagem de erro padrão se não conseguir importar

                mensagem = "SQL Server MCP não está disponível. Verifique a conexão com o banco de dados."
                logger.error(mensagem)
                return {
                    "success": False,
                    "error": mensagem,
                    "type": "error",
                    "message": mensagem,
                }

            conn = self._get_connection()
            if conn is None:
                return {
                    "success": False,
                    "error": "Não foi possível estabelecer conexão com o SQL Server para processar a query MCP.",
                    "type": "error",
                    "message": "Falha na conexão com o banco de dados.",
                }

            cursor = conn.cursor()
            logger.info(f"Executando sp_mcp_process_query com a query: {query}")
            cursor.execute("EXEC dbo.sp_mcp_process_query @query = ?", query)

            rows = cursor.fetchall()
            columns = (
                [column[0] for column in cursor.description]
                if cursor.description
                else []
            )

            results_list = []
            for row in rows:
                results_list.append(dict(zip(columns, row)))

            # Inferir o tipo de resultado com base na query original
            query_lower = query.lower()
            inferred_type = "generic_data"  # Default type
            if any(term in query_lower for term in ["venda", "vendido", "faturamento"]):
                inferred_type = "sales_data"
            elif any(
                term in query_lower for term in ["produto", "código", "codigo", "item"]
            ):
                inferred_type = "product_data"
            elif any(
                term in query_lower for term in ["categoria", "grupo", "departamento"]
            ):
                inferred_type = "category_data"

            # Se a SP principal retornou a mensagem padrão, o tipo deve ser tratado como uma resposta genérica
            if (
                len(results_list) == 1
                and "message" in results_list[0]
                and results_list[0]["message"] == "Consulta processada com sucesso"
            ):
                inferred_type = "mcp_response"  # Alinhado com o que QueryProcessor espera para fallback da SP

            logger.info(
                f"Query MCP processada. Tipo inferido: {inferred_type}. Resultados: {len(results_list)} linhas."
            )

            return {
                "success": True,
                "result": results_list,
                "type": inferred_type,
                "message": "Consulta MCP processada com sucesso.",
            }
        except Exception as e:
            erro_msg = str(e).lower()
            mensagem = ""

            # Mensagens de erro mais específicas e amigáveis
            if "timeout" in erro_msg:
                mensagem = "O tempo de conexão com o banco de dados expirou. Por favor, tente novamente mais tarde."
            elif "login failed" in erro_msg:
                mensagem = "Falha na autenticação com o banco de dados. Verifique as credenciais."
            elif "network-related" in erro_msg or "named pipes provider" in erro_msg:
                mensagem = "Não foi possível conectar ao servidor de banco de dados. Verifique se o servidor está online."
            elif "driver" in erro_msg:
                mensagem = "Problema com o driver de conexão ao banco de dados. Contate o suporte técnico."
            else:
                mensagem = f"Erro ao processar consulta no SQL Server: {str(e)}"

            logger.error(f"Erro ao processar consulta: {str(e)}")
            return {
                "success": False,
                "error": mensagem,
                "type": "error",
                "message": mensagem,
            }

    # O método get_product_info foi removido pois sua funcionalidade agora é coberta
    # pelo process_query que chama a sp_mcp_process_query, que por sua vez
    # pode chamar sp_mcp_get_product_data.


# Função auxiliar para obter uma instância do adaptador MCP SQL Server
def get_sqlserver_mcp_adapter(config_file: str = None) -> SQLServerMCPAdapter:
    """
    Retorna uma instância do adaptador MCP SQL Server

    Args:
        config_file (str, optional): Caminho para o arquivo de configuração.
            Se não fornecido, usa o padrão em data/sqlserver_mcp_config.json
            ou as credenciais diretamente do arquivo .env

    Returns:
        SQLServerMCPAdapter: Instância do adaptador MCP SQL Server
    """
    return SQLServerMCPAdapter(config_file)
