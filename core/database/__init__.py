import logging

logger = logging.getLogger(__name__)

# Este arquivo marca o diretório 'core/database' como um pacote Python.
# Geralmente, este arquivo pode ficar vazio ou pode ser usado para
# expor partes selecionadas do pacote.

# Por exemplo, o script iniciar_projeto.py importa 'from core.database.database import check_database_connection'.
# Se quiséssemos que 'from core.database import check_database_connection' funcionasse,
# poderíamos adicionar aqui: 'from .database import check_database_connection'
# No entanto, a forma atual de importação em iniciar_projeto.py é mais explícita e está correta.

if __name__ == "__main__":
    logger.warning(
        "O pacote 'core.database' está sendo executado como script, o que geralmente não é o esperado."
    )
