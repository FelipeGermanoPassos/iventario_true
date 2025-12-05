# Guia de Deploy no Vercel - Inventário TRUE

## 📋 Pré-requisitos

1. ✅ Projeto Supabase configurado (REST API, não conexão direta TCP)
2. ✅ Código migrado para usar Supabase REST API (NÃO usa psycopg2)
3. ✅ Conta Vercel com GitHub conectado

## 🔧 Configuração de Variáveis de Ambiente (Vercel)

Acesse: **Project Settings → Environment Variables**

### Variáveis OBRIGATÓRIAS

```env
SUPABASE_URL=https://ttfpqsdctnkzwrrhfssb.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SECRET_KEY=seu-valor-aleatorio-muito-seguro
```

### Variáveis OPCIONAIS

```env
MAIL_ENABLED=false
TELEGRAM_ENABLED=false
WHATSAPP_ENABLED=false
DEBUG=false
```

## 🚀 Deploy

### Opção 1: Push Automático (Recomendado)

1. Faça push para a branch `main` no GitHub
2. Vercel detectará automaticamente e iniciará o deploy
3. Aguarde ~60 segundos para conclusão

```bash
git add -A
git commit -m "mensagem do commit"
git push origin main
```

### Opção 2: Deploy Manual via CLI

```bash
# Instalar CLI do Vercel (se necessário)
npm install -g vercel

# Deploy
vercel --prod
```

## ✅ Verificação de Deploy

1. **Acesse a URL**: https://iventario-true.vercel.app
2. **Console do Browser** (F12 → Console):
   - ✅ Sem erros vermelhos
   - ✅ "Service Worker registrado" mensagem
   - ✅ Sem 404 em `/static/icons/*`
   - ✅ Sem 404 em `favicon.ico`

3. **Testes Funcionais**:
   - ✅ Login com `admin@inventario.com / admin123`
   - ✅ Dashboard carrega com gráficos
   - ✅ Notificações aparecem (se houver empréstimos)
   - ✅ Equipamentos listam corretamente

## 🔍 Troubleshooting

### Erro: "SUPABASE_URL ou SUPABASE_KEY não encontrados"

**Solução**: Verifique em **Project Settings → Environment Variables**
- SUPABASE_URL deve estar preenchida
- SUPABASE_KEY deve estar preenchida
- Rebuildando o projeto: **Deployments → ... → Redeploy**

### Erro: 500 em `/dashboard-data`

**Solução**: 
- Verifique logs: **Deployments → Função → Logs**
- Confirme que SUPABASE_URL e SUPABASE_KEY estão corretos
- Verifique permissões RLS no Supabase

### Erro: 404 em `/static/favicon.ico`

**Status**: ✅ CORRIGIDO (v6b22ba3)
- Favicon agora servido via rota Flask `/favicon.ico`
- Não é necessário adicionar manualmente

### TypeError: "Cannot read properties of undefined (reading 'toLocaleDateString')"

**Status**: ✅ CORRIGIDO (v6b22ba3)
- Validação de datas adicionada
- Verificação de campos nulos/undefined

## 📊 Arquitetura (Verificação)

✅ **Stack Final (Vercel-Compatível)**:
- Flask (Python web framework)
- Supabase REST API (HTTP/HTTPS, sem TCP)
- PostgreSQL (hospedado no Supabase, acessado via REST)
- Service Worker (PWA offline-first)

❌ **Tecnologias REMOVIDAS**:
- ~~SQLAlchemy ORM~~
- ~~psycopg2-binary (conexão TCP direta)~~
- ~~DATABASE_URL (PostgreSQL direto)~~
- ~~Flask-SQLAlchemy~~

## 📈 Monitoramento

Para acompanhar performance do seu app:

1. **Vercel Dashboard**: https://vercel.com/dashboard
2. **Supabase Dashboard**: https://supabase.com/dashboard
3. **Browser DevTools** (F12):
   - Network: Verificar latência das requisições
   - Console: Verificar erros JavaScript
   - Performance: Verificar tempo de carregamento

## 🔐 Segurança

- ✅ SUPABASE_KEY: Usar `anon` key (não `service_role`)
- ✅ RLS (Row Level Security) habilitado no Supabase
- ✅ SECRET_KEY do Flask: Usar valor aleatório forte
- ✅ CORS: Configurado apenas para domínios autorizados

## 📞 Suporte

Para problemas específicos:
1. Verifique os **Deployment Logs** no Vercel
2. Verifique os **Logs** do Supabase
3. Abra uma issue no GitHub com:
   - Print do erro
   - URL do app
   - Passos para reproduzir

---

**Status da Migração**: ✅ 100% Completo
**Commits**: 11 (do SQLAlchemy para Supabase REST API)
**Última atualização**: 2025-12-05
