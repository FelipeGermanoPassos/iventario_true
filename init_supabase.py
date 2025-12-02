"""
Script para inicializar o banco de dados no Supabase
Execute: python init_supabase.py
"""
import os

# Carrega variáveis de ambiente do arquivo .env manualmente
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    print('📁 Carregando variáveis do .env...')
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

from app import create_app
from app.models import db, Usuario

def init_database():
    """Inicializa o banco de dados criando todas as tabelas"""
    app = create_app()
    
    with app.app_context():
        print('🔄 Conectando ao banco de dados Supabase...')
        print(f'   URL: {app.config["SQLALCHEMY_DATABASE_URI"][:50]}...')
        
        try:
            # Cria todas as tabelas
            print('\n📦 Criando tabelas no banco de dados...')
            db.create_all()
            print('✅ Tabelas criadas com sucesso!')
            
            # Lista as tabelas criadas
            inspector = db.inspect(db.engine)
            tabelas = inspector.get_table_names()
            print(f'\n📋 Tabelas disponíveis ({len(tabelas)}):')
            for tabela in tabelas:
                print(f'   • {tabela}')
            
            # Verifica se já existe um admin
            print('\n👤 Verificando usuário administrador...')
            admin_existente = Usuario.query.filter_by(email='admin@inventario.com').first()
            
            if admin_existente:
                print('   ℹ️  Usuário administrador já existe')
                print(f'   Email: {admin_existente.email}')
            else:
                # Cria usuário administrador
                print('   📝 Criando usuário administrador...')
                admin = Usuario(
                    nome='Administrador',
                    email='admin@inventario.com',
                    departamento='TI',
                    is_admin=True,
                    ativo=True
                )
                admin.set_password('admin123')
                
                db.session.add(admin)
                db.session.commit()
                
                print('   ✅ Usuário administrador criado!')
                print('   Email: admin@inventario.com')
                print('   Senha: admin123')
                print('   ⚠️  IMPORTANTE: Altere a senha após o primeiro login!')
            
            print('\n✨ Banco de dados inicializado com sucesso!')
            print('🚀 Você já pode fazer deploy na Vercel!')
            
        except Exception as e:
            print(f'\n❌ Erro ao inicializar banco de dados:')
            print(f'   {str(e)}')
            print('\n💡 Dicas:')
            print('   • Verifique se a DATABASE_URL está correta no .env')
            print('   • Confirme que a URL termina com ?sslmode=require')
            print('   • Teste a conexão no painel do Supabase')
            raise

if __name__ == '__main__':
    init_database()
