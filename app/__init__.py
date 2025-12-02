from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os

def create_app():
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui-mude-em-producao'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configurações de E-mail
    # Para Gmail: use smtp.gmail.com, porta 587, e senha de app (não senha normal)
    # Para Outlook: use smtp-mail.outlook.com, porta 587
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Seu email
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Senha de app
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])
    app.config['MAIL_ENABLED'] = os.environ.get('MAIL_ENABLED', 'false').lower() == 'true'
    
    # Uploads de fotos (armazenadas em static/uploads/equipamentos)
    uploads_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'equipamentos')
    os.makedirs(uploads_dir, exist_ok=True)
    app.config['UPLOAD_FOLDER_EQUIPAMENTOS'] = uploads_dir
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB por requisição
    
    # Backups do banco de dados
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    app.config['BACKUP_FOLDER'] = backup_dir
    
    # Inicializa o banco de dados
    from app.models import db, Usuario
    db.init_app(app)
    
    # Inicializa o Flask-Mail
    mail = Mail()
    mail.init_app(app)
    
    # Inicializa o Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Cria as tabelas se não existirem
    with app.app_context():
        db.create_all()
    
    # Registra as rotas
    from app.routes import main
    app.register_blueprint(main)
    
    # Configura tarefas agendadas
    from apscheduler.schedulers.background import BackgroundScheduler
    from app.routes import realizar_backup_automatico
    from app.email_service import verificar_e_enviar_notificacoes
    
    scheduler = BackgroundScheduler()
    
    # Backup diário às 02:00
    scheduler.add_job(
        func=lambda: realizar_backup_automatico(app),
        trigger='cron',
        hour=2,
        minute=0,
        id='backup_diario',
        name='Backup Diário do Banco de Dados',
        replace_existing=True
    )
    
    # Verificar notificações de email diariamente às 09:00
    if app.config['MAIL_ENABLED']:
        scheduler.add_job(
            func=lambda: verificar_e_enviar_notificacoes(app),
            trigger='cron',
            hour=9,
            minute=0,
            id='notificacoes_email',
            name='Verificar e Enviar Notificações de Email',
            replace_existing=True
        )
    
    scheduler.start()
    
    # Shutdown do scheduler quando a app terminar
    import atexit
    atexit.register(lambda: scheduler.shutdown())
    
    return app
