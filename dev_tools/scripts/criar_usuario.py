import argparse
import getpass
import sys
import os

# Adiciona o diretório raiz do projeto ao sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import auth_db

def main():
    """Função principal para criar um usuário."""
    parser = argparse.ArgumentParser(description="Cria um novo usuário no banco de dados de autenticação.")
    parser.add_argument("-u", "--username", help="Nome do usuário")
    parser.add_argument("-p", "--password", help="Senha do usuário")
    parser.add_argument("-r", "--role", default="user", help="Perfil do usuário (admin ou user)")

    args = parser.parse_args()

    print("=== Criador de Usuário (Autenticação SQLite) ===")
    auth_db.init_db()

    username = args.username or input("Usuário: ").strip()
    while not username:
        username = input("Usuário (não pode ser vazio): ").strip()

    password = args.password
    if not password:
        while True:
            password = getpass.getpass("Senha: ")
            password2 = getpass.getpass("Confirme a senha: ")
            if password != password2:
                print("As senhas não coincidem. Tente novamente.")
            elif len(password) < 6:
                print("A senha deve ter pelo menos 6 caracteres.")
            else:
                break
    
    role = args.role
    if role not in ("admin", "user"):
        print(f"Perfil '{role}' inválido. Usando 'user'.")
        role = "user"

    try:
        auth_db.criar_usuario(username, password, role=role)
        print(f"Usuário '{username}' criado com sucesso com perfil '{role}'.")
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")


if __name__ == "__main__":
    main()
