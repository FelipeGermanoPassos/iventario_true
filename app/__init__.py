from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os
import tempfile

def create_app():
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sua-chave-secreta-aqui-mude-em-producao')
    
    # Permite substituir o banco via variável de ambiente (necessário para Vercel/Postgres)
    db_url = os.environ.get('DATABASE_URL') or os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///inventario.db'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configurações otimizadas para serverless (Vercel)
    is_vercel = bool(os.environ.get('VERCEL'))
    if is_vercel:
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 1,
            'max_overflow': 0,
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_timeout': 30,
            'connect_args': {
                'connect_timeout': 30,
                'keepalives': 1,
            }
        }
    else:
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 5,
            'max_overflow': 10,
            'pool_pre_ping': True,
            'pool_recycle': 3600,
        }
    
    # Configurações de E-mail
    # Carrega do arquivo .env se existir, senão usa variáveis de ambiente
    try:
        from app.config_manager import EmailConfigManager
        config_manager = EmailConfigManager()
        
        # Tenta carregar do .env primeiro
        if config_manager.env_path.exists():
            email_config = config_manager.load_config()
            config_manager.apply_to_app(app, email_config)
        else:
            # Fallback para variáveis de ambiente
            app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
            app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
            app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
            app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
            app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
            app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
            app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config.get('MAIL_USERNAME', ''))
            app.config['MAIL_ENABLED'] = os.environ.get('MAIL_ENABLED', 'false').lower() == 'true'
    except Exception as e:
        app.logger.warning(f'Email config manager não disponível: {str(e)}. Usando variáveis de ambiente.')
        # Fallback para variáveis de ambiente
        app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
        app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
        app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
        app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
        app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
        app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config.get('MAIL_USERNAME', ''))
        app.config['MAIL_ENABLED'] = os.environ.get('MAIL_ENABLED', 'false').lower() == 'true'
    
    # Uploads de fotos (armazenadas em static/uploads/equipamentos)
    # Em ambientes serverless (ex.: Vercel) o filesystem é efêmero/readonly; usa tempdir
    if is_vercel:
        uploads_dir = os.path.join(tempfile.gettempdir(), 'uploads_equipamentos')
    else:
        uploads_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'equipamentos')
    os.makedirs(uploads_dir, exist_ok=True)
    app.config['UPLOAD_FOLDER_EQUIPAMENTOS'] = uploads_dir
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB por requisição
    
    # Backups do banco de dados
    if is_vercel:
        backup_dir = os.path.join(tempfile.gettempdir(), 'backups')
    else:
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
    
    # Cria as tabelas se não existirem (com tratamento de erro para evitar crash no Vercel)
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            # Em produção serverless, as tabelas devem ser criadas via SQL script
            # Logando o erro mas não quebrando a aplicação
            app.logger.warning(f'Não foi possível criar tabelas automaticamente: {str(e)}')
            app.logger.info('Se as tabelas não existem, execute o script supabase_init.sql no painel do Supabase')
    
    # Registra as rotas
    from app.routes import main
    app.register_blueprint(main)
    
    # Configura tarefas agendadas (desabilitadas em ambientes serverless como Vercel)
    if not is_vercel and os.environ.get('SCHEDULER_ENABLED', 'true').lower() == 'true':
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
