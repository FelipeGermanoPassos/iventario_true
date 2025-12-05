"""
Cliente Supabase para substituir SQLAlchemy
Usa a API REST do Supabase ao invés de conexão direta PostgreSQL
"""
import os
from supabase import create_client, Client
from typing import Optional

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Retorna instância singleton do cliente Supabase
    """
    global _supabase_client
    
    if _supabase_client is None:
        # Configuração a partir de variáveis de ambiente
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL e SUPABASE_KEY devem estar definidos nas variáveis de ambiente. "
                "Configure no painel da Vercel: Settings → Environment Variables"
            )
        
        _supabase_client = create_client(supabase_url, supabase_key)
    
    return _supabase_client

def init_supabase():
    """
    Inicializa o cliente Supabase (chamado na inicialização do app)
    """
    try:
        client = get_supabase_client()
        # Testa a conexão fazendo uma query simples
        client.table('usuarios').select('id').limit(1).execute()
        return True
    except Exception as e:
        print(f"Erro ao inicializar Supabase: {e}")
        return False
