"""
Script para criar usuário administrador inicial
Execute: python criar_admin.py
"""
from app import create_app
from app.models import db, Usuario

def criar_admin():
    app = create_app()
    
    with app.app_context():
        # Verifica se já existe um admin
        admin_existente = Usuario.query.filter_by(email='admin@inventario.com').first()
        
        if admin_existente:
            print('❌ Usuário administrador já existe!')
            print(f'   Email: {admin_existente.email}')
            return
        
        # Cria novo usuário administrador
        admin = Usuario(
            nome='Administrador',
            email='admin@inventario.com',
            departamento='TI',
            is_admin=True,
            ativo=True
        )
        admin.set_password('admin123')  # Senha padrão
        
        db.session.add(admin)
        db.session.commit()
        
        print('✅ Usuário administrador criado com sucesso!')
        print('   Email: admin@inventario.com')
        print('   Senha: admin123')
        print('   ⚠️  IMPORTANTE: Altere a senha após o primeiro login!')

if __name__ == '__main__':
    criar_admin()
