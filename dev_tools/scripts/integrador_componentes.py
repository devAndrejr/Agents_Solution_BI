import logging
import os
import re
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/integrador_componentes.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("integrador_componentes")

# Garantir que o diretório de logs existe
os.makedirs("logs", exist_ok=True)


class IntegradorComponentes:
    """Classe responsável por integrar componentes desconectados ao projeto principal"""

    def __init__(self, diretorio_base):
        self.diretorio_base = diretorio_base
        self.componentes_desconectados = []
        self.componentes_principais = []
        self.mapa_importacoes = {}
        self.arquivos_python = []

    def carregar_componentes_desconectados(self, arquivo_relatorio=None):
        """Carrega os componentes desconectados do relatório de integração ou executa análise"""
        if arquivo_relatorio and os.path.exists(arquivo_relatorio):
            logger.info(
                f"Carregando componentes desconectados do relatório: {arquivo_relatorio}"
            )
            try:
                with open(arquivo_relatorio, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                    # Extrair componentes desconectados do relatório markdown
                    secao_desconectados = re.search(
                        r"## Componentes Desconectados\s*\n\n([\s\S]*?)(?:\n##|$)",
                        conteudo,
                    )
                    if secao_desconectados:
                        texto_secao = secao_desconectados.group(1)
                        # Extrair caminhos dos componentes listados com formato `- `caminho``
                        componentes = re.findall(r"- `([^`]+)`", texto_secao)
                        self.componentes_desconectados = componentes
                        logger.info(
                            f"Encontrados {len(self.componentes_desconectados)} componentes desconectados no relatório"
                        )
            except Exception as e:
                logger.error(f"Erro ao carregar relatório: {str(e)}")
        else:
            # Se não tiver relatório, executar análise para identificar componentes desconectados
            logger.info("Executando análise para identificar componentes desconectados")
            try:
                from analise.analisador_integracao import AnalisadorIntegracao

                analisador = AnalisadorIntegracao(self.diretorio_base)
                analisador.encontrar_arquivos_python()
                analisador.analisar_importacoes()
                self.componentes_desconectados = (
                    analisador.identificar_componentes_desconectados()
                )
                logger.info(
                    f"Análise concluída. Encontrados {len(self.componentes_desconectados)} componentes desconectados"
                )
            except ImportError:
                logger.error(
                    "Não foi possível importar o AnalisadorIntegracao. Verifique se o módulo está disponível."
                )

        return self.componentes_desconectados

    def identificar_componentes_principais(self):
        """Identifica os componentes principais do projeto (mais utilizados)"""
        logger.info("Identificando componentes principais do projeto...")

        # Encontrar todos os arquivos Python
        for raiz, _, arquivos in os.walk(self.diretorio_base):
            # Ignorar diretórios de ambiente virtual e cache
            if ".venv" in raiz or "venv" in raiz or "__pycache__" in raiz:
                continue

            for arquivo in arquivos:
                if arquivo.endswith(".py"):
                    caminho_completo = os.path.join(raiz, arquivo)
                    caminho_relativo = os.path.relpath(
                        caminho_completo, self.diretorio_base
                    )
                    self.arquivos_python.append(caminho_relativo)

        # Analisar importações para identificar componentes mais utilizados
        contagem_importacoes = {}
        padrao_import = re.compile(
            r"^\s*(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))"
        )

        for arquivo in self.arquivos_python:
            caminho_completo = os.path.join(self.diretorio_base, arquivo)
            try:
                with open(caminho_completo, "r", encoding="utf-8") as f:
                    conteudo = f.readlines()

                for linha in conteudo:
                    match = padrao_import.match(linha)
                    if match:
                        modulo_importado = match.group(1) or match.group(2)
                        # Contar importações de cada módulo
                        if modulo_importado:
                            modulo_principal = modulo_importado.split(".")[0]
                            contagem_importacoes[modulo_principal] = (
                                contagem_importacoes.get(modulo_principal, 0) + 1
                            )
            except Exception as e:
                logger.error(f"Erro ao analisar {arquivo}: {str(e)}")

        # Ordenar por número de importações
        modulos_ordenados = sorted(
            contagem_importacoes.items(), key=lambda x: x[1], reverse=True
        )

        # Selecionar os 10 módulos mais importados como principais
        self.componentes_principais = [modulo for modulo, _ in modulos_ordenados[:10]]
        logger.info(
            f"Componentes principais identificados: {self.componentes_principais}"
        )

        return self.componentes_principais

    def analisar_dependencias_faltantes(self):
        """Analisa as dependências faltantes nos componentes desconectados"""
        logger.info(
            "Analisando dependências faltantes nos componentes desconectados..."
        )

        dependencias_faltantes = {}

        for componente in self.componentes_desconectados:
            caminho_completo = os.path.join(self.diretorio_base, componente)
            if not os.path.exists(caminho_completo):
                logger.warning(f"Componente não encontrado: {caminho_completo}")
                continue

            # Analisar o componente para identificar possíveis importações dos componentes principais
            try:
                with open(caminho_completo, "r", encoding="utf-8") as f:
                    conteudo = f.read()

                # Verificar se o componente poderia importar algum dos componentes principais
                importacoes_sugeridas = []
                for modulo_principal in self.componentes_principais:
                    # Verificar se o componente já importa este módulo
                    padrao_importacao = re.compile(
                        f"^\s*(?:from\s+{modulo_principal}(?:\.|\s)|import\s+{modulo_principal}(?:\.|\s))",
                        re.MULTILINE,
                    )
                    if not padrao_importacao.search(conteudo):
                        # Verificar se o componente usa funcionalidades que poderiam vir deste módulo
                        # Esta é uma heurística simples - na prática, seria necessário uma análise mais profunda
                        if self._verificar_possivel_dependencia(
                            conteudo, modulo_principal
                        ):
                            importacoes_sugeridas.append(modulo_principal)

                if importacoes_sugeridas:
                    dependencias_faltantes[componente] = importacoes_sugeridas

            except Exception as e:
                logger.error(f"Erro ao analisar dependências em {componente}: {str(e)}")

        logger.info(
            f"Análise concluída. {len(dependencias_faltantes)} componentes com dependências faltantes."
        )
        return dependencias_faltantes

    def _verificar_possivel_dependencia(self, conteudo, modulo):
        """Verifica se um componente poderia depender de um módulo específico"""
        # Esta é uma implementação simplificada - na prática, seria necessário uma análise mais sofisticada

        # Mapeamento de módulos para padrões de uso comuns
        padroes_uso = {
            "core": ["agent", "processor", "config", "database", "query", "state"],
            "utils": ["util", "helper", "format", "convert", "validate"],
            "database": ["db", "sql", "query", "connection", "table"],
            "api": ["route", "endpoint", "request", "response", "http"],
            "mcp": ["mcp", "adapter", "context", "server"],
            "analise": ["analis", "report", "estatistic", "metric"],
        }

        # Verificar se o conteúdo contém padrões associados ao módulo
        if modulo in padroes_uso:
            for padrao in padroes_uso[modulo]:
                if re.search(f"\b{padrao}\w*\b", conteudo, re.IGNORECASE):
                    return True

        return False

    def sugerir_integracoes(self):
        """Sugere integrações para os componentes desconectados"""
        logger.info("Gerando sugestões de integração...")

        # Carregar componentes desconectados se ainda não foram carregados
        if not self.componentes_desconectados:
            self.carregar_componentes_desconectados()

        # Identificar componentes principais se ainda não foram identificados
        if not self.componentes_principais:
            self.identificar_componentes_principais()

        # Analisar dependências faltantes
        dependencias_faltantes = self.analisar_dependencias_faltantes()

        # Gerar sugestões de integração
        sugestoes = {}
        for componente, modulos in dependencias_faltantes.items():
            sugestoes[componente] = {
                "importacoes_sugeridas": modulos,
                "modificacoes": self._gerar_modificacoes_sugeridas(componente, modulos),
            }

        # Salvar sugestões em um arquivo
        caminho_sugestoes = os.path.join(
            self.diretorio_base, "relatorios", "sugestoes_integracao.json"
        )
        os.makedirs(os.path.dirname(caminho_sugestoes), exist_ok=True)
        with open(caminho_sugestoes, "w", encoding="utf-8") as f:
            import json

            json.dump(sugestoes, f, indent=4, ensure_ascii=False)

        logger.info(f"Sugestões de integração geradas e salvas em {caminho_sugestoes}")
        return sugestoes

    def _gerar_modificacoes_sugeridas(self, componente, modulos):
        """Gera sugestões específicas de modificações para integrar o componente"""
        modificacoes = []

        # Para cada módulo sugerido, gerar uma sugestão de importação
        for modulo in modulos:
            # Determinar o tipo de importação mais adequado
            if modulo == "core":
                modificacoes.append(
                    f"from {modulo} import query_processor, agent_state"
                )
            elif modulo == "utils":
                modificacoes.append(f"from core.{modulo} import db_utils, text_utils")
            elif modulo == "database":
                modificacoes.append(f"from core.{modulo} import connection_manager")
            elif modulo == "api":
                modificacoes.append(f"from core.{modulo} import routes")
            elif modulo == "mcp":
                modificacoes.append(f"from core.{modulo} import mcp_manager")
            elif modulo == "analise":
                modificacoes.append(f"from {modulo} import analisador_projeto")
            else:
                modificacoes.append(f"import {modulo}")

        return modificacoes

    def aplicar_integracoes(self, sugestoes=None, interativo=True):
        """Aplica as integrações sugeridas aos componentes desconectados"""
        logger.info("Aplicando integrações aos componentes desconectados...")

        # Se não foram fornecidas sugestões, gerar novas
        if not sugestoes:
            sugestoes = self.sugerir_integracoes()

        # Para cada componente com sugestões
        for componente, dados in sugestoes.items():
            caminho_completo = os.path.join(self.diretorio_base, componente)
            if not os.path.exists(caminho_completo):
                logger.warning(f"Componente não encontrado: {caminho_completo}")
                continue

            # Se modo interativo, perguntar ao usuário se deseja aplicar as modificações
            aplicar = True
            if interativo:
                print(f"\nComponente: {componente}")
                print("Modificações sugeridas:")
                for mod in dados["modificacoes"]:
                    print(f"  - {mod}")
                resposta = input("Aplicar estas modificações? (s/n): ").lower()
                aplicar = resposta == "s" or resposta == "sim"

            if aplicar:
                try:
                    # Ler o conteúdo atual do arquivo
                    with open(caminho_completo, "r", encoding="utf-8") as f:
                        conteudo = f.readlines()

                    # Encontrar a posição adequada para inserir as importações
                    # (após as importações existentes)
                    pos_insercao = 0
                    for i, linha in enumerate(conteudo):
                        if (
                            linha.strip()
                            and not linha.startswith("import ")
                            and not linha.startswith("from ")
                        ):
                            pos_insercao = i
                            break
                        pos_insercao = i + 1

                    # Inserir as novas importações
                    for modificacao in reversed(dados["modificacoes"]):
                        conteudo.insert(pos_insercao, modificacao + "\n")

                    # Adicionar um comentário explicativo
                    conteudo.insert(
                        pos_insercao,
                        "# Importações adicionadas pelo integrador de componentes\n",
                    )

                    # Escrever o conteúdo modificado de volta ao arquivo
                    with open(caminho_completo, "w", encoding="utf-8") as f:
                        f.writelines(conteudo)

                    logger.info(
                        f"Integrações aplicadas com sucesso ao componente {componente}"
                    )
                except Exception as e:
                    logger.error(
                        f"Erro ao aplicar integrações ao componente {componente}: {str(e)}"
                    )

        logger.info("Processo de integração concluído")
        return True


def main():
    # Obter o diretório base do projeto
    diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"Iniciando integração de componentes no projeto em: {diretorio_base}")
    integrador = IntegradorComponentes(diretorio_base)

    # Carregar componentes desconectados do relatório de integração
    relatorio_path = os.path.join(diretorio_base, "relatorio_integracao.md")
    if os.path.exists(relatorio_path):
        integrador.carregar_componentes_desconectados(relatorio_path)
    else:
        print("Relatório de integração não encontrado. Executando análise direta...")
        integrador.carregar_componentes_desconectados()

    # Identificar componentes principais
    integrador.identificar_componentes_principais()

    # Gerar e aplicar sugestões de integração
    sugestoes = integrador.sugerir_integracoes()
    integrador.aplicar_integracoes(sugestoes)

    print("\nIntegração de componentes concluída!")
    print(
        f"Relatório de sugestões salvo em: {os.path.join(diretorio_base, 'relatorios', 'sugestoes_integracao.json')}"
    )


if __name__ == "__main__":
    main()
