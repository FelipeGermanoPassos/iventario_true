"""
Script para atualizar o banco de dados com campos do Dashboard Executivo
Adiciona: vida_util_anos e departamento_atual à tabela equipamentos
"""

from app import create_app
from app.models import db
from sqlalchemy import text

def atualizar_banco():
    """Adiciona novos campos à tabela equipamentos"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Iniciando atualização do banco de dados...")
            
            # Verificar se as colunas já existem
            inspector = db.inspect(db.engine)
            colunas_existentes = [col['name'] for col in inspector.get_columns('equipamentos')]
            
            # Adicionar coluna vida_util_anos se não existir
            if 'vida_util_anos' not in colunas_existentes:
                print("📝 Adicionando coluna 'vida_util_anos'...")
                db.session.execute(text(
                    "ALTER TABLE equipamentos ADD COLUMN vida_util_anos INTEGER DEFAULT 5"
                ))
                print("✅ Coluna 'vida_util_anos' adicionada!")
            else:
                print("ℹ️  Coluna 'vida_util_anos' já existe.")
            
            # Adicionar coluna departamento_atual se não existir
            if 'departamento_atual' not in colunas_existentes:
                print("📝 Adicionando coluna 'departamento_atual'...")
                db.session.execute(text(
                    "ALTER TABLE equipamentos ADD COLUMN departamento_atual VARCHAR(100)"
                ))
                print("✅ Coluna 'departamento_atual' adicionada!")
            else:
                print("ℹ️  Coluna 'departamento_atual' já existe.")
            
            db.session.commit()
            
            # Contar equipamentos
            result = db.session.execute(text("SELECT COUNT(*) FROM equipamentos"))
            total = result.scalar()
            
            print(f"\n✅ Atualização concluída com sucesso!")
            print(f"📊 Total de equipamentos no banco: {total}")
            print(f"\n💡 Novos campos disponíveis:")
            print(f"   - vida_util_anos: Para cálculo de depreciação (padrão: 5 anos)")
            print(f"   - departamento_atual: Para rastreamento por departamento")
            print(f"\n🎯 Agora você pode usar o Dashboard Executivo com métricas de ROI!")
            
        except Exception as e:
            print(f"\n❌ Erro ao atualizar banco: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    atualizar_banco()
