from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

def create_app():
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui-mude-em-producao'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializa o banco de dados
    from app.models import db
    db.init_app(app)
    
    # Cria as tabelas se não existirem
    with app.app_context():
        db.create_all()
    
    # Registra as rotas
    from app.routes import main
    app.register_blueprint(main)
    
    return app
