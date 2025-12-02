"""
Script para atualizar o banco de dados com a nova tabela de push subscriptions
"""
from app import create_app
from app.models import db

def main():
    print("=" * 60)
    print("Atualização do Banco de Dados - Push Notifications")
    print("=" * 60)
    print()
    
    app = create_app()
    
    with app.app_context():
        print("Criando novas tabelas...")
        db.create_all()
        print("✅ Tabelas criadas/atualizadas com sucesso!")
        print()
        print("Nova tabela adicionada:")
        print("  - push_subscriptions: Armazena subscrições de notificações push")
        print()
        print("=" * 60)
        print("✨ Banco de dados atualizado com sucesso!")
        print("=" * 60)

if __name__ == '__main__':
    main()
