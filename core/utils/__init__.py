import logging

logging.basicConfig(level=logging.INFO)

try:
    # seu código principal aqui
    pass
except Exception as e:
    logging.error(f"Erro geral: {e}")

# Inicialização do pacote utils

if __name__ == "__main__":
    print("Rodando como script...")
    # TODO: Adicionar chamada a uma função principal se necessário
