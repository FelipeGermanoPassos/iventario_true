from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class Usuario(UserMixin, db.Model):
    """Modelo para usuários do sistema"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    departamento = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acesso = db.Column(db.DateTime)
    
    def set_password(self, senha):
        """Define a senha do usuário (com hash)"""
        self.senha_hash = generate_password_hash(senha)
    
    def check_password(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'departamento': self.departamento,
            'telefone': self.telefone,
            'is_admin': self.is_admin,
            'ativo': self.ativo,
            'data_cadastro': self.data_cadastro.strftime('%Y-%m-%d %H:%M:%S'),
            'ultimo_acesso': self.ultimo_acesso.strftime('%Y-%m-%d %H:%M:%S') if self.ultimo_acesso else None
        }
    
    def __repr__(self):
        return f'<Usuario {self.email}>'


class Equipamento(db.Model):
    """Modelo para equipamentos de TI"""
    __tablename__ = 'equipamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # Desktop, Notebook, Servidor, Monitor, etc
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    numero_serie = db.Column(db.String(100), unique=True, nullable=False)
    processador = db.Column(db.String(100))
    memoria_ram = db.Column(db.String(50))
    armazenamento = db.Column(db.String(50))
    sistema_operacional = db.Column(db.String(50))
    status = db.Column(db.String(20), nullable=False)  # Estoque, Emprestado, Manutenção, Inativo
    data_aquisicao = db.Column(db.Date)
    valor = db.Column(db.Float)
    observacoes = db.Column(db.Text)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    fotos = db.relationship('EquipamentoFoto', backref='equipamento', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        # Foto principal (se existir)
        foto_principal = None
        if hasattr(self, 'fotos') and self.fotos:
            # Tenta achar a principal, senão pega a primeira
            principais = [f.url for f in self.fotos if f.principal]
            foto_principal = principais[0] if principais else self.fotos[0].url
        
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo,
            'marca': self.marca,
            'modelo': self.modelo,
            'numero_serie': self.numero_serie,
            'processador': self.processador,
            'memoria_ram': self.memoria_ram,
            'armazenamento': self.armazenamento,
            'sistema_operacional': self.sistema_operacional,
            'status': self.status,
            'data_aquisicao': self.data_aquisicao.strftime('%Y-%m-%d') if self.data_aquisicao else None,
            'valor': self.valor,
            'observacoes': self.observacoes,
            'data_cadastro': self.data_cadastro.strftime('%Y-%m-%d %H:%M:%S'),
            'data_atualizacao': self.data_atualizacao.strftime('%Y-%m-%d %H:%M:%S'),
            'foto_url': foto_principal
        }
    
    def __repr__(self):
        return f'<Equipamento {self.nome} - {self.numero_serie}>'


class Emprestimo(db.Model):
    """Modelo para empréstimos de equipamentos"""
    __tablename__ = 'emprestimos'
    
    id = db.Column(db.Integer, primary_key=True)
    equipamento_id = db.Column(db.Integer, db.ForeignKey('equipamentos.id'), nullable=False)
    responsavel = db.Column(db.String(100), nullable=False)
    departamento = db.Column(db.String(100), nullable=False)
    email_responsavel = db.Column(db.String(100))
    telefone_responsavel = db.Column(db.String(20))
    data_emprestimo = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_devolucao_prevista = db.Column(db.Date)
    data_devolucao_real = db.Column(db.DateTime)
    status = db.Column(db.String(20), nullable=False, default='Ativo')  # Ativo, Devolvido, Atrasado
    observacoes = db.Column(db.Text)
    
    # Relacionamento
    equipamento = db.relationship('Equipamento', backref=db.backref('emprestimos', lazy=True))
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        equipamento_nome = None
        if self.equipamento:
            equipamento_nome = f"{self.equipamento.nome} - {self.equipamento.marca} {self.equipamento.modelo}"
        
        return {
            'id': self.id,
            'equipamento_id': self.equipamento_id,
            'equipamento_nome': equipamento_nome,
            'equipamento': {
                'id': self.equipamento.id,
                'nome': self.equipamento.nome,
                'tipo': self.equipamento.tipo,
                'marca': self.equipamento.marca,
                'modelo': self.equipamento.modelo,
                'numero_serie': self.equipamento.numero_serie
            } if self.equipamento else None,
            'responsavel': self.responsavel,
            'departamento': self.departamento,
            'email_responsavel': self.email_responsavel,
            'telefone_responsavel': self.telefone_responsavel,
            'data_emprestimo': self.data_emprestimo.strftime('%Y-%m-%d %H:%M:%S'),
            'data_devolucao_prevista': self.data_devolucao_prevista.strftime('%Y-%m-%d') if self.data_devolucao_prevista else None,
            'data_devolucao_real': self.data_devolucao_real.strftime('%Y-%m-%d %H:%M:%S') if self.data_devolucao_real else None,
            'status': self.status,
            'observacoes': self.observacoes
        }
    
    def __repr__(self):
        return f'<Emprestimo {self.id} - {self.responsavel}>'


class EquipamentoFoto(db.Model):
    """Fotos associadas a equipamentos"""
    __tablename__ = 'equipamentos_fotos'

    id = db.Column(db.Integer, primary_key=True)
    equipamento_id = db.Column(db.Integer, db.ForeignKey('equipamentos.id'), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    principal = db.Column(db.Boolean, default=True)
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'equipamento_id': self.equipamento_id,
            'url': self.url,
            'principal': self.principal,
            'data_upload': self.data_upload.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self):
        return f'<EquipamentoFoto {self.id} - Eq {self.equipamento_id}>'
