"""
Modelos usando Supabase REST API
Substitui SQLAlchemy models.py
"""
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.supabase_client import get_supabase_client


class Usuario:
    """Modelo para usuários do sistema"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id')
        self.nome = data.get('nome')
        self.email = data.get('email')
        self.senha_hash = data.get('senha_hash')
        self.departamento = data.get('departamento')
        self.telefone = data.get('telefone')
        self.is_admin = data.get('is_admin', False)
        self.ativo = data.get('ativo', True)
        self.data_cadastro = data.get('data_cadastro')
        self.ultimo_acesso = data.get('ultimo_acesso')
    
    # Flask-Login requirements
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return self.ativo
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)
    
    def set_password(self, senha: str):
        """Define a senha do usuário (com hash)"""
        self.senha_hash = generate_password_hash(senha)
    
    def check_password(self, senha: str) -> bool:
        """Verifica se a senha está correta"""
        try:
            return check_password_hash(self.senha_hash, senha)
        except Exception as e:
            print(f"Erro ao verificar senha: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'departamento': self.departamento,
            'telefone': self.telefone,
            'is_admin': self.is_admin,
            'ativo': self.ativo,
            'data_cadastro': self.data_cadastro,
            'ultimo_acesso': self.ultimo_acesso
        }
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional['Usuario']:
        """Busca usuário por ID"""
        try:
            client = get_supabase_client()
            response = client.table('usuarios').select('*').eq('id', user_id).execute()
            if response.data and len(response.data) > 0:
                return Usuario(response.data[0])
            return None
        except Exception as e:
            print(f"Erro ao buscar usuário por ID: {e}")
            return None
    
    @staticmethod
    def get_by_email(email: str) -> Optional['Usuario']:
        """Busca usuário por email"""
        try:
            client = get_supabase_client()
            response = client.table('usuarios').select('*').eq('email', email).execute()
            if response.data and len(response.data) > 0:
                return Usuario(response.data[0])
            return None
        except Exception as e:
            print(f"Erro ao buscar usuário por email: {e}")
            return None
    
    @staticmethod
    def create(nome: str, email: str, senha: str, **kwargs) -> 'Usuario':
        """Cria um novo usuário"""
        senha_hash = generate_password_hash(senha)
        data = {
            'nome': nome,
            'email': email,
            'senha_hash': senha_hash,
            'departamento': kwargs.get('departamento'),
            'telefone': kwargs.get('telefone'),
            'is_admin': kwargs.get('is_admin', False),
            'ativo': kwargs.get('ativo', True),
            'data_cadastro': datetime.utcnow().isoformat()
        }
        
        client = get_supabase_client()
        response = client.table('usuarios').insert(data).execute()
        return Usuario(response.data[0])
    
    def update(self, **kwargs):
        """Atualiza dados do usuário"""
        client = get_supabase_client()
        update_data = {}
        
        if 'nome' in kwargs:
            update_data['nome'] = kwargs['nome']
            self.nome = kwargs['nome']
        if 'email' in kwargs:
            update_data['email'] = kwargs['email']
            self.email = kwargs['email']
        if 'departamento' in kwargs:
            update_data['departamento'] = kwargs['departamento']
            self.departamento = kwargs['departamento']
        if 'telefone' in kwargs:
            update_data['telefone'] = kwargs['telefone']
            self.telefone = kwargs['telefone']
        if 'senha' in kwargs:
            senha_hash = generate_password_hash(kwargs['senha'])
            update_data['senha_hash'] = senha_hash
            self.senha_hash = senha_hash
        if 'is_admin' in kwargs:
            update_data['is_admin'] = kwargs['is_admin']
            self.is_admin = kwargs['is_admin']
        if 'ativo' in kwargs:
            update_data['ativo'] = kwargs['ativo']
            self.ativo = kwargs['ativo']
        if 'ultimo_acesso' in kwargs:
            update_data['ultimo_acesso'] = kwargs['ultimo_acesso'].isoformat()
            self.ultimo_acesso = kwargs['ultimo_acesso'].isoformat()
        
        if update_data:
            client.table('usuarios').update(update_data).eq('id', self.id).execute()
    
    def delete(self):
        """Deleta o usuário"""
        client = get_supabase_client()
        client.table('usuarios').delete().eq('id', self.id).execute()
    
    @staticmethod
    def get_all() -> List['Usuario']:
        """Retorna todos os usuários"""
        client = get_supabase_client()
        response = client.table('usuarios').select('*').execute()
        return [Usuario(user) for user in response.data]
    
    @staticmethod
    def count() -> int:
        """Conta total de usuários"""
        client = get_supabase_client()
        response = client.table('usuarios').select('id', count='exact').execute()
        return response.count


class Equipamento:
    """Modelo para equipamentos de TI"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id')
        self.nome = data.get('nome')
        self.tipo = data.get('tipo')
        self.marca = data.get('marca')
        self.modelo = data.get('modelo')
        self.numero_serie = data.get('numero_serie')
        self.processador = data.get('processador')
        self.memoria_ram = data.get('memoria_ram')
        self.armazenamento = data.get('armazenamento')
        self.sistema_operacional = data.get('sistema_operacional')
        self.status = data.get('status')
        self.data_aquisicao = data.get('data_aquisicao')
        self.valor = data.get('valor')
        self.vida_util_anos = data.get('vida_util_anos', 5)
        self.departamento_atual = data.get('departamento_atual')
        self.observacoes = data.get('observacoes')
        self.data_cadastro = data.get('data_cadastro')
        self.data_atualizacao = data.get('data_atualizacao')
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto para dicionário"""
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
            'data_aquisicao': self.data_aquisicao,
            'valor': self.valor,
            'vida_util_anos': self.vida_util_anos,
            'departamento_atual': self.departamento_atual,
            'observacoes': self.observacoes,
            'data_cadastro': self.data_cadastro,
            'data_atualizacao': self.data_atualizacao
        }
    
    @staticmethod
    def get_by_id(equip_id: int) -> Optional['Equipamento']:
        """Busca equipamento por ID"""
        try:
            client = get_supabase_client()
            response = client.table('equipamentos').select('*').eq('id', equip_id).execute()
            if response.data and len(response.data) > 0:
                return Equipamento(response.data[0])
            return None
        except Exception as e:
            print(f"Erro ao buscar equipamento por ID: {e}")
            return None
    
    @staticmethod
    def get_all() -> List['Equipamento']:
        """Retorna todos os equipamentos"""
        client = get_supabase_client()
        response = client.table('equipamentos').select('*').execute()
        return [Equipamento(eq) for eq in response.data]
    
    @staticmethod
    def create(**kwargs) -> 'Equipamento':
        """Cria um novo equipamento"""
        data = {
            'nome': kwargs.get('nome'),
            'tipo': kwargs.get('tipo'),
            'marca': kwargs.get('marca'),
            'modelo': kwargs.get('modelo'),
            'numero_serie': kwargs.get('numero_serie'),
            'processador': kwargs.get('processador'),
            'memoria_ram': kwargs.get('memoria_ram'),
            'armazenamento': kwargs.get('armazenamento'),
            'sistema_operacional': kwargs.get('sistema_operacional'),
            'status': kwargs.get('status', 'Estoque'),
            'data_aquisicao': kwargs.get('data_aquisicao'),
            'valor': kwargs.get('valor'),
            'vida_util_anos': kwargs.get('vida_util_anos', 5),
            'departamento_atual': kwargs.get('departamento_atual'),
            'observacoes': kwargs.get('observacoes'),
            'data_cadastro': datetime.utcnow().isoformat()
        }
        
        client = get_supabase_client()
        response = client.table('equipamentos').insert(data).execute()
        return Equipamento(response.data[0])
    
    def update(self, **kwargs):
        """Atualiza dados do equipamento"""
        client = get_supabase_client()
        update_data = {k: v for k, v in kwargs.items() if k != 'id'}
        update_data['data_atualizacao'] = datetime.utcnow().isoformat()
        
        if update_data:
            client.table('equipamentos').update(update_data).eq('id', self.id).execute()
            # Atualiza o objeto local
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
    
    def delete(self):
        """Deleta o equipamento"""
        client = get_supabase_client()
        client.table('equipamentos').delete().eq('id', self.id).execute()
    
    @staticmethod
    def count_by_status() -> Dict[str, int]:
        """Conta equipamentos por status"""
        client = get_supabase_client()
        response = client.table('equipamentos').select('status').execute()
        
        counts = {}
        for item in response.data:
            status = item.get('status', 'Desconhecido')
            counts[status] = counts.get(status, 0) + 1
        return counts


# Placeholder para outros modelos (Emprestimo, etc)
# Implementar conforme necessário usando o mesmo padrão
