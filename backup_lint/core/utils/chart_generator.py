import logging
import os

import plotly.express as px

logging.basicConfig(level=logging.INFO)

"""Módulo para geração de gráficos e visualizações de dados"""


class ChartGenerator:
    def __init__(self, charts_dir):
        """Inicializa o gerador de gráficos

        Args:
            charts_dir (str): Diretório onde os gráficos serão salvos
        """
        self.charts_dir = charts_dir
        os.makedirs(self.charts_dir, exist_ok=True)

    # O método _generate_chart_filename e a escrita de arquivos HTML não são mais necessários
    # se os gráficos são passados diretamente como objetos Plotly para o Streamlit.
    # Pode ser removido ou comentado se não houver outro uso.
    # def _generate_chart_filename(self, prefix="chart"):
    #     """Gera um nome único para o arquivo do gráfico
    #
    #     Args:
    #         prefix (str): Prefixo para o nome do arquivo
    #
    #     Returns:
    #         str: Caminho completo para o arquivo do gráfico
    #     """
    #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    #     filename = f"{prefix}_{timestamp}.html"
    #     return os.path.join(self.charts_dir, filename)

    def create_sales_chart(self, data, title="Vendas por Período"):
        """Cria um gráfico de vendas

        Args:
            data (pd.DataFrame): DataFrame com os dados de vendas
            title (str): Título do gráfico

        Returns:
            dict: Dicionário com informações do gráfico gerado
        """
        try:
            if data is None or data.empty:
                return {
                    "type": "sales_chart",
                    "success": False,
                    "message": "Não há dados disponíveis para gerar o gráfico.",
                }

            # Ordena os dados pela coluna de data para garantir a ordem cronológica
            if 'data' in data.columns:
                data = data.sort_values(by="data")

            # Cria o gráfico de linha
            fig = px.line(data, x="data", y="vendas", title=title)
            fig.update_layout(
                xaxis_title="Data", yaxis_title="Vendas", template="plotly_white"
            )

            return {
                "type": "sales_chart",
                "success": True,
                "plotly_fig": fig,  # Retorna o objeto da figura Plotly
                "message": "Gráfico de vendas gerado com sucesso!",
            }

        except Exception as e:
            return {
                "type": "sales_chart",
                "success": False,
                "message": f"Erro ao gerar gráfico de vendas: {str(e)}",
            }

    def create_top_products_chart(self, data, title="Top Produtos"):
        """Cria um gráfico de barras para os produtos mais vendidos

        Args:
            data (pd.DataFrame): DataFrame com os dados dos produtos
            title (str): Título do gráfico

        Returns:
            dict: Dicionário com informações do gráfico gerado
        """
        try:
            if data is None or data.empty:
                return {
                    "type": "top_products_chart",
                    "success": False,
                    "message": "Não há dados disponíveis para gerar o gráfico.",
                }

            # Cria o gráfico de barras
            fig = px.bar(data, x="nome", y="vendas", title=title)
            fig.update_layout(
                xaxis_title="Produto",
                yaxis_title="Vendas",
                template="plotly_white",
                xaxis_tickangle=-45,
            )

            return {
                "type": "top_products_chart",
                "success": True,
                "plotly_fig": fig,  # Retorna o objeto da figura Plotly
                "message": "Gráfico de top produtos gerado com sucesso!",
            }

        except Exception as e:
            return {
                "type": "top_products_chart",
                "success": False,
                "message": f"Erro ao gerar gráfico de top produtos: {str(e)}",
            }

    def create_category_sales_chart(self, data, title="Vendas por Categoria"):
        """Cria um gráfico de pizza para vendas por categoria

        Args:
            data (pd.DataFrame): DataFrame com os dados de vendas por categoria
            title (str): Título do gráfico

        Returns:
            dict: Dicionário com informações do gráfico gerado
        """
        try:
            if data is None or data.empty:
                return {
                    "type": "category_sales_chart",
                    "success": False,
                    "message": "Não há dados disponíveis para gerar o gráfico.",
                }

            # Cria o gráfico de pizza
            fig = px.pie(data, values="vendas", names="categoria", title=title)
            fig.update_layout(template="plotly_white")

            return {
                "type": "category_sales_chart",
                "success": True,
                "plotly_fig": fig,  # Retorna o objeto da figura Plotly
                "message": "Gráfico de vendas por categoria gerado com sucesso!",
            }

        except Exception as e:
            return {
                "type": "category_sales_chart",
                "success": False,
                "message": f"Erro ao gerar gráfico de vendas por categoria: {str(e)}",
            }


    def create_generic_chart(self, data, chart_type, x_col, y_col, title="Gráfico Personalizado"):
        """Cria um gráfico genérico com base nas especificações.

        Args:
            data (pd.DataFrame): DataFrame com os dados.
            chart_type (str): Tipo de gráfico ('bar', 'line', 'pie').
            x_col (str): Nome da coluna para o eixo X.
            y_col (str): Nome da coluna para o eixo Y.
            title (str): Título do gráfico.

        Returns:
            dict: Dicionário com o objeto da figura Plotly ou uma mensagem de erro.
        """
        try:
            if data is None or data.empty:
                return {"success": False, "message": "Dados insuficientes para gerar o gráfico."}

            # Para gráficos de linha, ordena os dados pelo eixo X para garantir a plotagem correta
            if chart_type == 'line' and x_col in data.columns:
                data = data.sort_values(by=x_col)

            fig = None
            if chart_type == 'bar':
                fig = px.bar(data, x=x_col, y=y_col, title=title)
            elif chart_type == 'line':
                fig = px.line(data, x=x_col, y=y_col, title=title)
            elif chart_type == 'pie':
                # Para gráfico de pizza, y_col é 'values' e x_col é 'names'
                fig = px.pie(data, values=y_col, names=x_col, title=title)
            else:
                return {"success": False, "message": f"Tipo de gráfico '{chart_type}' não suportado."}

            fig.update_layout(template="plotly_white")
            return {"success": True, "plotly_fig": fig, "message": "Gráfico gerado com sucesso!"}

        except Exception as e:
            logging.error(f"Erro ao gerar gráfico genérico: {e}")
            return {"success": False, "message": f"Erro ao criar o gráfico: {e}"}


if __name__ == "__main__":
    print("Rodando como script...")
    # TODO: Adicionar chamada a uma função principal se necessário
