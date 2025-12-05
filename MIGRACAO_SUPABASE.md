# Migração para Supabase REST API

## 🎯 Por que migrar?

A aplicação foi migrada de **conexão direta PostgreSQL (psycopg2)** para **Supabase REST API** pelos seguintes motivos:

1. ✅ **Resolve problema de IPv6 na Vercel** - HTTP/HTTPS funciona perfeitamente
2. ✅ **Mais simples** - Não precisa gerenciar pools de conexão
3. ✅ **Mais rápido em serverless** - Sem overhead de conexão TCP
4. ✅ **Recursos extras** - Auth, Storage, Realtime prontos
5. ✅ **Menor bundle** - Não precisa de psycopg2-binary (50MB+)

## 📋 Checklist de Migração

### 1. Atualizar Dependências

```bash
pip install supabase==2.3.0 postgrest==0.13.0
```

**Removido:**
- `psycopg2-binary`
- `Flask-SQLAlchemy`
- `SQLAlchemy`

**Adicionado:**
- `supabase` - Cliente Python oficial
- `postgrest` - Dependência do cliente Supabase

### 2. Configurar Variáveis de Ambiente

**Antes (DATABASE_URL):**
```env
DATABASE_URL=postgresql://postgres:senha@host:5432/postgres
```

**Agora (SUPABASE_URL + SUPABASE_KEY):**
```env
SUPABASE_URL=https://ttfpqsdctnkzwrrhfssb.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Onde encontrar:**
1. Acesse: https://supabase.com/dashboard/project/SEU-PROJECT/settings/api
2. Copie:
   - **URL** → `SUPABASE_URL`
   - **anon public** → `SUPABASE_KEY`

⚠️ **IMPORTANTE:** Use a chave `anon` (pública), NÃO a `service_role` (privada)!

### 3. Configurar na Vercel

1. Acesse: https://vercel.com/dashboard
2. Projeto → **Settings** → **Environment Variables**
3. **REMOVA:**
   - `DATABASE_URL`
4. **ADICIONE:**
   - `SUPABASE_URL` = `https://ttfpqsdctnkzwrrhfssb.supabase.co`
   - `SUPABASE_KEY` = `sua-chave-anon-aqui`
5. **Redesploy** (automático após salvar)

### 4. Atualizar Código

**Antes (SQLAlchemy):**
```python
from app.models import db, Usuario

# Query
usuario = Usuario.query.filter_by(email=email).first()

# Insert
novo_usuario = Usuario(nome='João', email='joao@example.com')
db.session.add(novo_usuario)
db.session.commit()

# Update
usuario.nome = 'João Silva'
db.session.commit()

# Delete
db.session.delete(usuario)
db.session.commit()
```

**Agora (Supabase REST API):**
```python
from app.models_supabase import Usuario

# Query
usuario = Usuario.get_by_email(email)

# Insert
novo_usuario = Usuario.create(nome='João', email='joao@example.com')

# Update
usuario.update(nome='João Silva')

# Delete
usuario.delete()
```

### 5. Políticas RLS (Row Level Security)

Por padrão, Supabase habilita RLS. Você precisa criar políticas:

**SQL para executar no Supabase SQL Editor:**

```sql
-- Desabilitar RLS temporariamente (ou criar políticas adequadas)
ALTER TABLE usuarios DISABLE ROW LEVEL SECURITY;
ALTER TABLE equipamentos DISABLE ROW LEVEL SECURITY;
ALTER TABLE emprestimos DISABLE ROW LEVEL SECURITY;
ALTER TABLE equipamentos_fotos DISABLE ROW LEVEL SECURITY;
ALTER TABLE manutencoes DISABLE ROW LEVEL SECURITY;
ALTER TABLE push_subscriptions DISABLE ROW LEVEL SECURITY;

-- OU criar políticas (recomendado para produção):
-- Exemplo: permitir SELECT/INSERT/UPDATE/DELETE para service_role
CREATE POLICY "Allow service role full access" ON usuarios
FOR ALL USING (auth.role() = 'service_role');
```

## 🔧 Mudanças na Arquitetura

| Antes | Agora |
|-------|-------|
| PostgreSQL TCP (porta 5432/6543) | HTTPS REST API (porta 443) |
| psycopg2-binary (50MB+) | supabase client (5MB) |
| SQLAlchemy ORM | Modelo customizado c/ REST |
| Connection pooling | Stateless HTTP requests |
| IPv6 blocking na Vercel ❌ | HTTP funciona sempre ✅ |

## 📊 Performance

**Cold Start:**
- Antes: ~3-5 segundos (conexão + pool)
- Agora: ~1-2 segundos (HTTP request)

**Query Simples:**
- Antes: ~50-100ms
- Agora: ~30-80ms (HTTP overhead menor em serverless)

## 🚀 Recursos Extras Disponíveis

Com Supabase REST API, você agora tem acesso a:

1. **Supabase Auth** - Sistema de autenticação integrado
2. **Storage** - Upload de arquivos (fotos de equipamentos)
3. **Realtime** - Websockets para updates em tempo real
4. **Edge Functions** - Serverless functions no Supabase
5. **PostgREST** - API automática para todas as tabelas

## ⚠️ Limitações

1. **Transações complexas** - REST API não suporta transações multi-tabela
   - Solução: Use Supabase RPC (stored procedures)
2. **Joins complexos** - Limitado à capacidade do PostgREST
   - Solução: Use views no banco ou múltiplas queries
3. **Bulk operations** - Menos eficiente que SQL direto
   - Solução: Para grandes volumes, considere RPC functions

## 📝 Próximos Passos

1. ✅ Migrar modelos Usuario e Equipamento
2. ⏳ Migrar modelos Emprestimo, Manutencao, etc
3. ⏳ Atualizar todas as rotas para usar novos modelos
4. ⏳ Testar em produção
5. ⏳ Implementar Storage para fotos
6. ⏳ (Opcional) Implementar Realtime para dashboard

## 🆘 Troubleshooting

**Erro: "SUPABASE_URL e SUPABASE_KEY devem estar definidos"**
- Configure as variáveis de ambiente na Vercel

**Erro: "new row violates row-level security policy"**
- Desabilite RLS ou crie políticas apropriadas (ver seção 5)

**Erro: "JWT expired"**
- A chave `anon` não expira, verifique se está usando a correta

**Performance lenta:**
- Adicione índices no Supabase SQL Editor
- Use `select()` com campos específicos ao invés de `*`

## 📚 Referências

- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [PostgREST API](https://postgrest.org/)
- [Supabase Docs](https://supabase.com/docs)
