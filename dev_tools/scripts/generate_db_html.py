import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

# Adiciona o diretório raiz ao sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from core.tools.node_mcp_client import get_node_mcp_client  # noqa: E402

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)


class DbStructureGenerator:
    """
    Gera uma visualização HTML da estrutura do banco de dados.
    """

    def __init__(self):
        load_dotenv()
        self.node_client = get_node_mcp_client()

    def get_db_structure(self):
        """Obtém a estrutura das tabelas e colunas via MCP."""
        if not self.node_client:
            logging.error("Cliente MCP não inicializado.")
            return None

        tables = []
        try:
            sql_tables = (
                "SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
                "WHERE TABLE_TYPE = 'BASE TABLE'"
            )
            resp_tables = self.node_client.execute_sql(sql_query=sql_tables)

            if not resp_tables.get("success") or not resp_tables.get("result"):
                logging.error(
                    "Erro ao obter tabelas via MCP: %s", resp_tables.get("error")
                )
                return None

            for row in resp_tables["result"]:
                schema, table_name = row["TABLE_SCHEMA"], row["TABLE_NAME"]
                table_info = {"schema": schema, "name": table_name, "columns": []}

                sql_columns = (
                    "SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE "
                    "FROM INFORMATION_SCHEMA.COLUMNS "
                    "WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?"
                )
                resp_cols = self.node_client.execute_sql(
                    sql_query=sql_columns, parameters=[schema, table_name]
                )

                if resp_cols.get("success") and resp_cols.get("result"):
                    for col_row in resp_cols["result"]:
                        table_info["columns"].append(
                            {
                                "name": col_row["COLUMN_NAME"],
                                "type": col_row["DATA_TYPE"],
                                "nullable": col_row["IS_NULLABLE"] == "YES",
                            }
                        )
                tables.append(table_info)
            return tables
        except Exception as e:
            logging.error("Erro ao consultar o banco de dados via MCP: %s", e)
            return None

    def generate_html(self, db_structure):
        """Gera o conteúdo HTML com base na estrutura do banco de dados."""
        if not db_structure:
            return "<p>Não foi possível obter a estrutura do banco de dados.</p>"

        # Template HTML separado para clareza
        html_template = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Estrutura do Banco de Dados</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #3498db; margin-top: 30px; }}
        h3 {{ color: #2980b9; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .table-container {{ margin-bottom: 40px; border: 1px solid #eee; padding: 15px; border-radius: 5px; }}
        .nullable {{ color: #e74c3c; }}
        .not-nullable {{ color: #27ae60; }}
        .search-container {{ margin-bottom: 20px; }}
        #tableSearch {{ padding: 8px; width: 300px; }}
        .hidden {{ display: none; }}
    </style>
</head>
<body>
    <h1>Estrutura do Banco de Dados</h1>
    <div class="search-container">
        <input type="text" id="tableSearch" placeholder="Pesquisar tabelas...">
    </div>
    <p>Total de tabelas: <strong>{total_tables}</strong></p>
    {tables_html}
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const searchInput = document.getElementById('tableSearch');
            const tableContainers = document.querySelectorAll('.table-container');
            searchInput.addEventListener('input', () => {{
                const filter = searchInput.value.toLowerCase();
                tableContainers.forEach(container => {{
                    const tableName = container.querySelector('h3').textContent.toLowerCase();
                    container.classList.toggle('hidden', !tableName.includes(filter));
                }});
            }});
        }});
    </script>
</body>
</html>"""

        tables_html = ""
        for table in db_structure:
            columns_html = ""
            for column in table["columns"]:
                nullable_class = "nullable" if column["nullable"] else "not-nullable"
                nullable_text = "Sim" if column["nullable"] else "Não"
                columns_html += f"""
                <tr>
                    <td>{column['name']}</td>
                    <td>{column['type']}</td>
                    <td class="{nullable_class}">{nullable_text}</td>
                </tr>"""

            tables_html += f"""
            <div class="table-container" id="table_{table['schema']}_{table['name']}">
                <h3>{table['schema']}.{table['name']}</h3>
                <p>Colunas: <strong>{len(table['columns'])}</strong></p>
                <table>
                    <tr><th>Nome</th><th>Tipo</th><th>Nulo</th></tr>
                    {columns_html}
                </table>
            </div>"""

        return html_template.format(
            total_tables=len(db_structure), tables_html=tables_html
        )

    def run(self):
        """Executa o processo completo de geração do HTML."""
        logging.info("Iniciando geração de HTML da estrutura do banco...")
        db_structure = self.get_db_structure()
        if db_structure:
            html_output = self.generate_html(db_structure)
            output_path = ROOT_DIR / "data" / "database_structure.html"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_output)
            logging.info("Arquivo %s atualizado com sucesso.", output_path)
        else:
            logging.error("Falha ao gerar o arquivo HTML.")


if __name__ == "__main__":
    generator = DbStructureGenerator()
    generator.run()
