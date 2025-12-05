from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
import os
import tempfile

def create_app():
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sua-chave-secreta-aqui-mude-em-producao')
    
    # Configuração Supabase (REST API)
    app.config['SUPABASE_URL'] = os.environ.get('SUPABASE_URL')
    app.config['SUPABASE_KEY'] = os.environ.get('SUPABASE_KEY')
    
    # Verifica se está na Vercel
    is_vercel = bool(os.environ.get('VERCEL'))
    
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
    
    # Inicializa o Supabase client
    try:
        from app.supabase_client import init_supabase
        if not init_supabase():
            app.logger.warning('Falha ao conectar com Supabase. Verifique SUPABASE_URL e SUPABASE_KEY.')
    except Exception as e:
        app.logger.error(f'Erro ao inicializar Supabase: {e}')
    
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
        # Usa o novo modelo Supabase
        from app.models_supabase import Usuario
        return Usuario.get_by_id(int(user_id))
    
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
