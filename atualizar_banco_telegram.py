"""
Script para adicionar coluna telegram_chat_id na tabela de empréstimos
"""
from app import create_app
from app.models import db
from sqlalchemy import text

def atualizar_banco():
    app = create_app()
    
    with app.app_context():
        try:
            # Verifica se a coluna já existe
            result = db.session.execute(text("PRAGMA table_info(emprestimos)"))
            columns = [row[1] for row in result]
            
            if 'telegram_chat_id' not in columns:
                print("Adicionando coluna telegram_chat_id...")
                db.session.execute(text(
                    "ALTER TABLE emprestimos ADD COLUMN telegram_chat_id VARCHAR(50)"
                ))
                db.session.commit()
                print("✅ Coluna telegram_chat_id adicionada com sucesso!")
            else:
                print("ℹ️  Coluna telegram_chat_id já existe no banco de dados.")
            
            # Mostra estatísticas
            result = db.session.execute(text("SELECT COUNT(*) FROM emprestimos"))
            total = result.scalar()
            print(f"📊 Total de empréstimos no banco: {total}")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar banco: {e}")
            db.session.rollback()

if __name__ == '__main__':
    print("🔧 Atualizando banco de dados para suportar Telegram...")
    print()
    atualizar_banco()
    print()
    print("✨ Atualização concluída!")
