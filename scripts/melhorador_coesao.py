import json
import logging
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

import networkx as nx

# Adiciona o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/melhorador_coesao.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("melhorador_coesao")

# Garantir que o diretório de logs existe
os.makedirs("logs", exist_ok=True)


class MelhoradorCoesao:
    """Classe responsável por melhorar a coesão do código, reorganizando os módulos"""

    def __init__(self, diretorio_base):
        self.diretorio_base = diretorio_base
        self.grafo = nx.DiGraph()
        self.modulos = set()
        self.dependencias = defaultdict(set)
        self.arquivos_python = []
        self.modulos_centrais = []
        self.modulos_isolados = []
        self.sugestoes_coesao = []

    def carregar_dados_integracao(self, arquivo_relatorio=None):
        """Carrega os dados de integração do relatório ou executa análise"""
        if arquivo_relatorio and os.path.exists(arquivo_relatorio):
            logger.info(
                f"Carregando dados de integração do relatório: {arquivo_relatorio}"
            )
            try:
                with open(arquivo_relatorio, "r", encoding="utf-8") as f:
                    conteudo = f.read()

                    # Extrair densidade do grafo
                    densidade_match = re.search(
                        r"Densidade do grafo de integração:\s*([0-9.]+)", conteudo
                    )
                    densidade = (
                        float(densidade_match.group(1)) if densidade_match else 0
                    )

                    # Extrair módulos centrais
                    secao_modulos = re.search(
                        r"## Módulos Centrais\s*\n\n([\s\S]*?)(?:\n##|$)", conteudo
                    )
                    if secao_modulos:
                        texto_secao = secao_modulos.group(1)
                        self.modulos_centrais = re.findall(r"- `([^`]+)`", texto_secao)

                    logger.info(
                        f"Dados carregados: densidade={densidade}, {len(self.modulos_centrais)} módulos centrais"
                    )
                    return densidade
            except Exception as e:
                logger.error(f"Erro ao carregar relatório: {str(e)}")

        # Se não tiver relatório ou falhar, executar análise
        logger.info("Executando análise de integração")
        try:
            from analise.analisador_integracao import AnalisadorIntegracao

            analisador = AnalisadorIntegracao(self.diretorio_base)
            analisador.encontrar_arquivos_python()
            analisador.analisar_importacoes()
            self.arquivos_python = analisador.arquivos_python
            self.grafo = analisador.grafo
            self.modulos = analisador.modulos
            self.dependencias = analisador.dependencias

            # Calcular densidade do grafo
            densidade = nx.density(self.grafo)

            # Identificar módulos centrais (maior centralidade)
            centralidade = nx.degree_centrality(self.grafo)
            modulos_centrais = sorted(
                centralidade.items(), key=lambda x: x[1], reverse=True
            )[:10]
            self.modulos_centrais = [modulo for modulo, _ in modulos_centrais]

            logger.info(
                f"Análise concluída: densidade={densidade}, {len(self.modulos_centrais)} módulos centrais"
            )
            return densidade
        except ImportError:
            logger.error(
                "Não foi possível importar o AnalisadorIntegracao. Verifique se o módulo está disponível."
            )
            return 0

    def encontrar_arquivos_python(self):
        """Encontra todos os arquivos Python no projeto"""
        logger.info(f"Buscando arquivos Python em: {self.diretorio_base}")
        for raiz, _, arquivos in os.walk(self.diretorio_base):
            # Ignorar diretórios de ambiente virtual
            if ".venv" in raiz or "venv" in raiz or "__pycache__" in raiz:
                continue

            for arquivo in arquivos:
                if arquivo.endswith(".py"):
                    caminho_completo = os.path.join(raiz, arquivo)
                    caminho_relativo = os.path.relpath(
                        caminho_completo, self.diretorio_base
                    )
                    self.arquivos_python.append(caminho_relativo)
                    self.grafo.add_node(caminho_relativo)

        logger.info(f"Encontrados {len(self.arquivos_python)} arquivos Python")
        return self.arquivos_python

    def analisar_importacoes(self):
        """Analisa as importações em cada arquivo Python"""
        logger.info("Analisando importações entre arquivos...")
        padrao_import = re.compile(
            r"^\s*(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))"
        )

        for arquivo in self.arquivos_python:
            caminho_completo = os.path.join(self.diretorio_base, arquivo)
            modulo_atual = os.path.splitext(arquivo)[0].replace(os.path.sep, ".")
            self.modulos.add(modulo_atual)

            try:
                with open(caminho_completo, "r", encoding="utf-8") as f:
                    conteudo = f.readlines()

                for linha in conteudo:
                    match = padrao_import.match(linha)
                    if match:
                        modulo_importado = match.group(1) or match.group(2)

                        # Verificar se é um módulo do projeto
                        for mod in self.modulos:
                            if modulo_importado == mod or modulo_importado.startswith(
                                mod + "."
                            ):
                                self.dependencias[modulo_atual].add(mod)
                                self.grafo.add_edge(
                                    arquivo, self._converter_modulo_para_arquivo(mod)
                                )
                                break
            except Exception as e:
                logger.error(f"Erro ao analisar {arquivo}: {str(e)}")

        logger.info(
            f"Análise de importações concluída. {len(self.dependencias)} módulos com dependências."
        )
        return self.dependencias

    def _converter_modulo_para_arquivo(self, modulo):
        """Converte um nome de módulo para o caminho relativo do arquivo"""
        for arquivo in self.arquivos_python:
            arquivo_sem_ext = os.path.splitext(arquivo)[0]
            if arquivo_sem_ext.replace(os.path.sep, ".") == modulo:
                return arquivo
        return modulo.replace(".", os.path.sep) + ".py"

    def identificar_modulos_isolados(self):
        """Identifica módulos com poucas conexões no grafo"""
        logger.info("Identificando módulos isolados...")

        # Calcular grau de cada nó (número de conexões)
        graus = dict(self.grafo.degree())

        # Ordenar por grau (do menor para o maior)
        nos_ordenados = sorted(graus.items(), key=lambda x: x[1])

        # Selecionar os 20% dos nós com menor grau
        num_isolados = max(1, int(len(nos_ordenados) * 0.2))
        self.modulos_isolados = [no for no, _ in nos_ordenados[:num_isolados]]

        logger.info(f"Identificados {len(self.modulos_isolados)} módulos isolados")
        return self.modulos_isolados

    def analisar_similaridade_funcional(self):
        """Analisa a similaridade funcional entre módulos isolados e centrais"""
        logger.info("Analisando similaridade funcional entre módulos...")

        # Se não temos módulos isolados, identificar agora
        if not self.modulos_isolados:
            self.identificar_modulos_isolados()

        # Extrair palavras-chave de cada módulo
        palavras_chave_por_modulo = {}

        # Padrões para extrair palavras-chave
        padrao_funcao = re.compile(r"def\s+(\w+)")
        padrao_classe = re.compile(r"class\s+(\w+)")
        padrao_variavel = re.compile(r"^\s*(\w+)\s*=")

        # Analisar cada arquivo
        for arquivo in self.arquivos_python:
            caminho_completo = os.path.join(self.diretorio_base, arquivo)
            try:
                with open(caminho_completo, "r", encoding="utf-8") as f:
                    conteudo = f.read()

                # Extrair palavras-chave
                funcoes = set(padrao_funcao.findall(conteudo))
                classes = set(padrao_classe.findall(conteudo))
                variaveis = set(padrao_variavel.findall(conteudo))

                # Adicionar ao dicionário
                palavras_chave_por_modulo[arquivo] = {
                    "funcoes": funcoes,
                    "classes": classes,
                    "variaveis": variaveis,
                }
            except Exception as e:
                logger.error(f"Erro ao analisar {arquivo}: {str(e)}")

        # Calcular similaridade entre módulos isolados e centrais
        similaridades = []

        for modulo_isolado in self.modulos_isolados:
            if modulo_isolado not in palavras_chave_por_modulo:
                continue

            palavras_isolado = palavras_chave_por_modulo[modulo_isolado]

            for modulo_central in self.modulos_centrais:
                modulo_central_arquivo = self._converter_modulo_para_arquivo(
                    modulo_central
                )
                if modulo_central_arquivo not in palavras_chave_por_modulo:
                    continue

                palavras_central = palavras_chave_por_modulo[modulo_central_arquivo]

                # Calcular similaridade
                sim_funcoes = len(
                    palavras_isolado["funcoes"].intersection(
                        palavras_central["funcoes"]
                    )
                ) / max(
                    1,
                    len(palavras_isolado["funcoes"].union(palavras_central["funcoes"])),
                )
                sim_classes = len(
                    palavras_isolado["classes"].intersection(
                        palavras_central["classes"]
                    )
                ) / max(
                    1,
                    len(palavras_isolado["classes"].union(palavras_central["classes"])),
                )
                sim_variaveis = len(
                    palavras_isolado["variaveis"].intersection(
                        palavras_central["variaveis"]
                    )
                ) / max(
                    1,
                    len(
                        palavras_isolado["variaveis"].union(
                            palavras_central["variaveis"]
                        )
                    ),
                )

                # Média ponderada
                similaridade = (
                    (0.5 * sim_funcoes) + (0.3 * sim_classes) + (0.2 * sim_variaveis)
                )

                similaridades.append(
                    {
                        "modulo_isolado": modulo_isolado,
                        "modulo_central": modulo_central_arquivo,
                        "similaridade": similaridade,
                    }
                )

        # Ordenar por similaridade
        similaridades.sort(key=lambda x: x["similaridade"], reverse=True)

        logger.info(
            f"Análise de similaridade concluída. {len(similaridades)} pares analisados."
        )
        return similaridades

    def gerar_sugestoes_coesao(self):
        """Gera sugestões para melhorar a coesão do código"""
        logger.info("Gerando sugestões para melhorar a coesão do código...")

        # Se não temos análise de similaridade, fazer agora
        similaridades = self.analisar_similaridade_funcional()

        # Gerar sugestões com base nas similaridades
        for similaridade in similaridades:
            if similaridade["similaridade"] > 0.1:  # Limiar de similaridade
                modulo_isolado = similaridade["modulo_isolado"]
                modulo_central = similaridade["modulo_central"]

                # Analisar o conteúdo dos módulos
                try:
                    caminho_isolado = os.path.join(self.diretorio_base, modulo_isolado)
                    caminho_central = os.path.join(self.diretorio_base, modulo_central)

                    with open(caminho_isolado, "r", encoding="utf-8") as f:
                        conteudo_isolado = f.read()

                    with open(caminho_central, "r", encoding="utf-8") as f:
                        conteudo_central = f.read()

                    # Extrair funções e classes do módulo isolado
                    funcoes_isolado = re.findall(
                        r"(def\s+\w+\s*\([^)]*\)\s*(?:->\s*[^:]+)?\s*:[\s\S]*?(?=\n\S|$))",
                        conteudo_isolado,
                    )
                    classes_isolado = re.findall(
                        r"(class\s+\w+(?:\([^)]*\))?\s*:[\s\S]*?(?=\n\S|$))",
                        conteudo_isolado,
                    )

                    # Gerar sugestão
                    sugestao = {
                        "modulo_isolado": modulo_isolado,
                        "modulo_central": modulo_central,
                        "similaridade": similaridade["similaridade"],
                        "tipo_sugestao": (
                            "importacao"
                            if similaridade["similaridade"] < 0.3
                            else "refatoracao"
                        ),
                        "detalhes": {
                            "funcoes": len(funcoes_isolado),
                            "classes": len(classes_isolado),
                        },
                    }

                    # Adicionar sugestões específicas
                    if sugestao["tipo_sugestao"] == "importacao":
                        # Sugerir importação do módulo central no isolado
                        modulo_central_nome = os.path.splitext(modulo_central)[
                            0
                        ].replace(os.path.sep, ".")
                        sugestao["acao"] = (
                            f"Adicionar 'import {modulo_central_nome}' ao módulo {modulo_isolado}"
                        )
                    else:
                        # Sugerir refatoração (mover funcionalidades)
                        sugestao["acao"] = (
                            f"Refatorar {modulo_isolado} movendo funcionalidades para {modulo_central}"
                        )

                    self.sugestoes_coesao.append(sugestao)
                except Exception as e:
                    logger.error(
                        f"Erro ao gerar sugestão para {modulo_isolado} e {modulo_central}: {str(e)}"
                    )

        # Salvar sugestões em um arquivo
        caminho_sugestoes = os.path.join(
            self.diretorio_base, "relatorios", "sugestoes_coesao.json"
        )
        os.makedirs(os.path.dirname(caminho_sugestoes), exist_ok=True)
        with open(caminho_sugestoes, "w", encoding="utf-8") as f:
            json.dump(
                self.sugestoes_coesao, f, indent=4, ensure_ascii=False, default=str
            )

        logger.info(
            f"Geradas {len(self.sugestoes_coesao)} sugestões de melhoria de coesão"
        )
        return self.sugestoes_coesao

    def aplicar_sugestoes_coesao(self, interativo=True):
        """Aplica as sugestões de melhoria de coesão"""
        logger.info("Aplicando sugestões de melhoria de coesão...")

        # Se não temos sugestões, gerar agora
        if not self.sugestoes_coesao:
            self.gerar_sugestoes_coesao()

        sugestoes_aplicadas = []

        for sugestao in self.sugestoes_coesao:
            modulo_isolado = sugestao["modulo_isolado"]
            modulo_central = sugestao["modulo_central"]
            tipo_sugestao = sugestao["tipo_sugestao"]
            acao = sugestao["acao"]

            print(f"\nSugestão para melhorar coesão:")
            print(f"  Módulo isolado: {modulo_isolado}")
            print(f"  Módulo central: {modulo_central}")
            print(f"  Tipo: {tipo_sugestao}")
            print(f"  Ação: {acao}")

            # Se modo interativo, perguntar ao usuário se deseja aplicar a sugestão
            aplicar = True
            if interativo:
                resposta = input("Aplicar esta sugestão? (s/n): ").lower()
                aplicar = resposta == "s" or resposta == "sim"

            if aplicar:
                try:
                    caminho_isolado = os.path.join(self.diretorio_base, modulo_isolado)
                    caminho_central = os.path.join(self.diretorio_base, modulo_central)

                    if tipo_sugestao == "importacao":
                        # Adicionar importação ao módulo isolado
                        modulo_central_nome = os.path.splitext(modulo_central)[
                            0
                        ].replace(os.path.sep, ".")

                        with open(caminho_isolado, "r", encoding="utf-8") as f:
                            conteudo = f.readlines()

                        # Encontrar a posição adequada para inserir a importação
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

                        # Inserir a importação
                        conteudo.insert(
                            pos_insercao,
                            f"import {modulo_central_nome}  # Adicionado para melhorar coesão\n",
                        )

                        # Escrever o conteúdo modificado de volta ao arquivo
                        with open(caminho_isolado, "w", encoding="utf-8") as f:
                            f.writelines(conteudo)

                        logger.info(f"Importação adicionada ao módulo {modulo_isolado}")
                        print(f"  ✓ Importação adicionada com sucesso")

                    elif tipo_sugestao == "refatoracao":
                        # Extrair funções e classes do módulo isolado
                        with open(caminho_isolado, "r", encoding="utf-8") as f:
                            conteudo_isolado = f.read()

                        funcoes_isolado = re.findall(
                            r"(def\s+\w+\s*\([^)]*\)\s*(?:->\s*[^:]+)?\s*:[\s\S]*?(?=\n\S|$))",
                            conteudo_isolado,
                        )
                        classes_isolado = re.findall(
                            r"(class\s+\w+(?:\([^)]*\))?\s*:[\s\S]*?(?=\n\S|$))",
                            conteudo_isolado,
                        )

                        # Adicionar funções e classes ao módulo central
                        with open(caminho_central, "a", encoding="utf-8") as f:
                            f.write(
                                "\n\n# Código movido do módulo "
                                + modulo_isolado
                                + " para melhorar coesão\n"
                            )

                            for funcao in funcoes_isolado:
                                f.write("\n" + funcao + "\n")

                            for classe in classes_isolado:
                                f.write("\n" + classe + "\n")

                        # Modificar o módulo isolado para importar do módulo central
                        modulo_central_nome = os.path.splitext(modulo_central)[
                            0
                        ].replace(os.path.sep, ".")

                        # Extrair nomes de funções e classes
                        nomes_funcoes = re.findall(r"def\s+(\w+)", conteudo_isolado)
                        nomes_classes = re.findall(r"class\s+(\w+)", conteudo_isolado)

                        # Criar novo conteúdo para o módulo isolado
                        novo_conteudo = f"""# Este módulo foi refatorado para melhorar a coesão do código
# As funcionalidades foram movidas para {modulo_central_nome}

import {modulo_central_nome}

# Re-exportar funcionalidades para manter compatibilidade
"""

                        for nome in nomes_funcoes:
                            novo_conteudo += f"{nome} = {modulo_central_nome}.{nome}\n"

                        for nome in nomes_classes:
                            novo_conteudo += f"{nome} = {modulo_central_nome}.{nome}\n"

                        # Escrever o novo conteúdo ao arquivo
                        with open(caminho_isolado, "w", encoding="utf-8") as f:
                            f.write(novo_conteudo)

                        logger.info(
                            f"Refatoração aplicada: {modulo_isolado} -> {modulo_central}"
                        )
                        print(f"  ✓ Refatoração aplicada com sucesso")

                    sugestoes_aplicadas.append(sugestao)

                except Exception as e:
                    logger.error(
                        f"Erro ao aplicar sugestão para {modulo_isolado}: {str(e)}"
                    )
                    print(f"  ! Erro ao aplicar sugestão: {str(e)}")

        # Salvar relatório das sugestões aplicadas
        if sugestoes_aplicadas:
            caminho_relatorio = os.path.join(
                self.diretorio_base, "relatorios", "sugestoes_coesao_aplicadas.json"
            )
            with open(caminho_relatorio, "w", encoding="utf-8") as f:
                json.dump(
                    sugestoes_aplicadas, f, indent=4, ensure_ascii=False, default=str
                )
            logger.info(
                f"Relatório de sugestões aplicadas salvo em {caminho_relatorio}"
            )

        logger.info(
            f"Processo de melhoria de coesão concluído. {len(sugestoes_aplicadas)} sugestões aplicadas."
        )
        return sugestoes_aplicadas


def main():
    # Obter o diretório base do projeto
    diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"Iniciando melhoria de coesão do código no projeto em: {diretorio_base}")
    melhorador = MelhoradorCoesao(diretorio_base)

    # Carregar dados de integração do relatório
    relatorio_path = os.path.join(diretorio_base, "relatorio_integracao.md")
    densidade = melhorador.carregar_dados_integracao(relatorio_path)
    print(f"Densidade atual do grafo de integração: {densidade:.4f}")

    # Se não temos arquivos Python, encontrar agora
    if not melhorador.arquivos_python:
        melhorador.encontrar_arquivos_python()
        melhorador.analisar_importacoes()

    # Identificar módulos isolados
    melhorador.identificar_modulos_isolados()

    # Gerar e aplicar sugestões de coesão
    sugestoes = melhorador.gerar_sugestoes_coesao()
    sugestoes_aplicadas = melhorador.aplicar_sugestoes_coesao()

    print("\nMelhoria de coesão do código concluída!")
    print(f"Foram geradas {len(sugestoes)} sugestões de melhoria de coesão")
    print(f"Foram aplicadas {len(sugestoes_aplicadas)} sugestões")
    print(
        f"\nRelatório de sugestões salvo em: {os.path.join(diretorio_base, 'relatorios', 'sugestoes_coesao.json')}"
    )
    if sugestoes_aplicadas:
        print(
            f"Relatório de sugestões aplicadas salvo em: {os.path.join(diretorio_base, 'relatorios', 'sugestoes_coesao_aplicadas.json')}"
        )


if __name__ == "__main__":
    main()
