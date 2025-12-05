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


class Emprestimo:
    """Modelo para empréstimos de equipamentos"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id')
        self.equipamento_id = data.get('equipamento_id')
        self.responsavel = data.get('responsavel')
        self.departamento = data.get('departamento')
        self.email_responsavel = data.get('email_responsavel')
        self.telefone_responsavel = data.get('telefone_responsavel')
        self.telegram_chat_id = data.get('telegram_chat_id')
        self.data_emprestimo = data.get('data_emprestimo')
        self.data_devolucao_prevista = data.get('data_devolucao_prevista')
        self.data_devolucao_real = data.get('data_devolucao_real')
        self.status = data.get('status', 'Ativo')
        self.observacoes = data.get('observacoes')
        # Relacionamento com equipamento (se incluído no select)
        self.equipamento = None
        if 'equipamentos' in data:
            self.equipamento = Equipamento(data['equipamentos'])
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            'id': self.id,
            'equipamento_id': self.equipamento_id,
            'responsavel': self.responsavel,
            'departamento': self.departamento,
            'email_responsavel': self.email_responsavel,
            'telefone_responsavel': self.telefone_responsavel,
            'telegram_chat_id': self.telegram_chat_id,
            'data_emprestimo': self.data_emprestimo,
            'data_devolucao_prevista': self.data_devolucao_prevista,
            'data_devolucao_real': self.data_devolucao_real,
            'status': self.status,
            'observacoes': self.observacoes
        }
        # Sempre incluir equipamento_nome (se disponível)
        if self.equipamento:
            result['equipamento'] = self.equipamento.to_dict()
            result['equipamento_nome'] = f"{self.equipamento.nome} - {self.equipamento.marca} {self.equipamento.modelo}"
        else:
            # Fallback: tentar buscar o equipamento se não estiver disponível
            try:
                equip = Equipamento.get_by_id(self.equipamento_id)
                if equip:
                    result['equipamento'] = equip.to_dict()
                    result['equipamento_nome'] = f"{equip.nome} - {equip.marca} {equip.modelo}"
                else:
                    result['equipamento_nome'] = 'Equipamento desconhecido'
            except:
                result['equipamento_nome'] = 'Equipamento desconhecido'
        return result
    
    @staticmethod
    def get_by_id(emprestimo_id: int) -> Optional['Emprestimo']:
        try:
            client = get_supabase_client()
            response = client.table('emprestimos').select('*, equipamentos(*)').eq('id', emprestimo_id).execute()
            if response.data and len(response.data) > 0:
                return Emprestimo(response.data[0])
            return None
        except Exception as e:
            print(f"Erro ao buscar empréstimo: {e}")
            return None
    
    @staticmethod
    def get_all() -> List['Emprestimo']:
        client = get_supabase_client()
        response = client.table('emprestimos').select('*, equipamentos(*)').execute()
        return [Emprestimo(emp) for emp in response.data]
    
    @staticmethod
    def create(**kwargs) -> 'Emprestimo':
        data = {
            'equipamento_id': kwargs.get('equipamento_id'),
            'responsavel': kwargs.get('responsavel'),
            'departamento': kwargs.get('departamento'),
            'email_responsavel': kwargs.get('email_responsavel'),
            'telefone_responsavel': kwargs.get('telefone_responsavel'),
            'telegram_chat_id': kwargs.get('telegram_chat_id'),
            'data_emprestimo': kwargs.get('data_emprestimo', datetime.utcnow().isoformat()),
            'data_devolucao_prevista': kwargs.get('data_devolucao_prevista'),
            'status': kwargs.get('status', 'Ativo'),
            'observacoes': kwargs.get('observacoes')
        }
        client = get_supabase_client()
        response = client.table('emprestimos').insert(data).execute()
        return Emprestimo(response.data[0])
    
    def update(self, **kwargs):
        client = get_supabase_client()
        update_data = {k: v for k, v in kwargs.items() if k != 'id'}
        if update_data:
            client.table('emprestimos').update(update_data).eq('id', self.id).execute()
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
    
    def delete(self):
        client = get_supabase_client()
        client.table('emprestimos').delete().eq('id', self.id).execute()


class EquipamentoFoto:
    """Fotos associadas a equipamentos"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id')
        self.equipamento_id = data.get('equipamento_id')
        self.url = data.get('url')
        self.principal = data.get('principal', True)
        self.data_upload = data.get('data_upload')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'equipamento_id': self.equipamento_id,
            'url': self.url,
            'principal': self.principal,
            'data_upload': self.data_upload
        }
    
    @staticmethod
    def get_by_equipamento(equipamento_id: int) -> List['EquipamentoFoto']:
        client = get_supabase_client()
        response = client.table('equipamentos_fotos').select('*').eq('equipamento_id', equipamento_id).execute()
        return [EquipamentoFoto(foto) for foto in response.data]
    
    @staticmethod
    def create(**kwargs) -> 'EquipamentoFoto':
        data = {
            'equipamento_id': kwargs.get('equipamento_id'),
            'url': kwargs.get('url'),
            'principal': kwargs.get('principal', True),
            'data_upload': datetime.utcnow().isoformat()
        }
        client = get_supabase_client()
        response = client.table('equipamentos_fotos').insert(data).execute()
        return EquipamentoFoto(response.data[0])
    
    def delete(self):
        client = get_supabase_client()
        client.table('equipamentos_fotos').delete().eq('id', self.id).execute()


class Manutencao:
    """Histórico de manutenções de equipamentos"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id')
        self.equipamento_id = data.get('equipamento_id')
        self.tipo = data.get('tipo')
        self.descricao = data.get('descricao')
        self.data_inicio = data.get('data_inicio')
        self.data_fim = data.get('data_fim')
        self.custo = data.get('custo')
        self.responsavel = data.get('responsavel')
        self.fornecedor = data.get('fornecedor')
        self.status = data.get('status', 'Em Andamento')
        self.data_registro = data.get('data_registro')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'equipamento_id': self.equipamento_id,
            'tipo': self.tipo,
            'descricao': self.descricao,
            'data_inicio': self.data_inicio,
            'data_fim': self.data_fim,
            'custo': self.custo,
            'responsavel': self.responsavel,
            'fornecedor': self.fornecedor,
            'status': self.status,
            'data_registro': self.data_registro
        }
    
    @staticmethod
    def get_by_id(manutencao_id: int) -> Optional['Manutencao']:
        try:
            client = get_supabase_client()
            response = client.table('manutencoes').select('*').eq('id', manutencao_id).execute()
            if response.data and len(response.data) > 0:
                return Manutencao(response.data[0])
            return None
        except Exception as e:
            print(f"Erro ao buscar manutenção: {e}")
            return None
    
    @staticmethod
    def get_by_equipamento(equipamento_id: int) -> List['Manutencao']:
        client = get_supabase_client()
        response = client.table('manutencoes').select('*').eq('equipamento_id', equipamento_id).execute()
        return [Manutencao(man) for man in response.data]
    
    @staticmethod
    def create(**kwargs) -> 'Manutencao':
        data = {
            'equipamento_id': kwargs.get('equipamento_id'),
            'tipo': kwargs.get('tipo'),
            'descricao': kwargs.get('descricao'),
            'data_inicio': kwargs.get('data_inicio'),
            'data_fim': kwargs.get('data_fim'),
            'custo': kwargs.get('custo'),
            'responsavel': kwargs.get('responsavel'),
            'fornecedor': kwargs.get('fornecedor'),
            'status': kwargs.get('status', 'Em Andamento'),
            'data_registro': datetime.utcnow().isoformat()
        }
        client = get_supabase_client()
        response = client.table('manutencoes').insert(data).execute()
        return Manutencao(response.data[0])
    
    def update(self, **kwargs):
        client = get_supabase_client()
        update_data = {k: v for k, v in kwargs.items() if k != 'id'}
        if update_data:
            client.table('manutencoes').update(update_data).eq('id', self.id).execute()
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
    
    def delete(self):
        client = get_supabase_client()
        client.table('manutencoes').delete().eq('id', self.id).execute()


class PushSubscription:
    """Armazena subscrições de push notifications dos usuários"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id')
        self.usuario_id = data.get('usuario_id')
        self.endpoint = data.get('endpoint')
        self.p256dh = data.get('p256dh')
        self.auth = data.get('auth')
        self.user_agent = data.get('user_agent')
        self.data_criacao = data.get('data_criacao')
        self.ativa = data.get('ativa', True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'endpoint': self.endpoint,
            'keys': {
                'p256dh': self.p256dh,
                'auth': self.auth
            },
            'data_criacao': self.data_criacao,
            'ativa': self.ativa
        }
    
    @staticmethod
    def get_by_endpoint(endpoint: str) -> Optional['PushSubscription']:
        try:
            client = get_supabase_client()
            response = client.table('push_subscriptions').select('*').eq('endpoint', endpoint).execute()
            if response.data and len(response.data) > 0:
                return PushSubscription(response.data[0])
            return None
        except Exception as e:
            print(f"Erro ao buscar subscription: {e}")
            return None
    
    @staticmethod
    def get_by_usuario(usuario_id: int) -> List['PushSubscription']:
        client = get_supabase_client()
        response = client.table('push_subscriptions').select('*').eq('usuario_id', usuario_id).eq('ativa', True).execute()
        return [PushSubscription(sub) for sub in response.data]
    
    @staticmethod
    def create(**kwargs) -> 'PushSubscription':
        data = {
            'usuario_id': kwargs.get('usuario_id'),
            'endpoint': kwargs.get('endpoint'),
            'p256dh': kwargs.get('p256dh'),
            'auth': kwargs.get('auth'),
            'user_agent': kwargs.get('user_agent'),
            'data_criacao': datetime.utcnow().isoformat(),
            'ativa': True
        }
        client = get_supabase_client()
        response = client.table('push_subscriptions').insert(data).execute()
        return PushSubscription(response.data[0])
    
    def update(self, **kwargs):
        client = get_supabase_client()
        update_data = {k: v for k, v in kwargs.items() if k != 'id'}
        if update_data:
            client.table('push_subscriptions').update(update_data).eq('id', self.id).execute()
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
    
    def delete(self):
        client = get_supabase_client()
        client.table('push_subscriptions').delete().eq('id', self.id).execute()
