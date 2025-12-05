# Guia de Debug - Problema de Equipamentos em Produção

## 🔍 Como Diagnosticar o Problema

### Passo 1: Verificar Configuração do Vercel

1. Acesse: https://vercel.com/dashboard
2. Clique no seu projeto: **iventario-true**
3. Vá para **Settings → Environment Variables**
4. Verifique se existem:

   ```
   ✅ SUPABASE_URL=https://ttfpqsdctnkzwrrhfssb.supabase.co
   ✅ SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ✅ SECRET_KEY=<seu-valor>
   ```

### Passo 2: Acessar Rotas de Debug em Produção

Acesse estas URLs no seu app Vercel para diagnóstico:

**URL do seu app:** https://iventario-true.vercel.app

**Rotas de Debug:**

1. **Verificar Config:**
   ```
   https://iventario-true.vercel.app/debug/config
   ```
   Deve retornar algo como:
   ```json
   {
     "supabase_url": "https://ttfpqsdctnkzwrrhf...",
     "supabase_key": "SET",
     "secret_key_configured": true,
     "is_vercel": true
   }
   ```

2. **Verificar Conexão com DB:**
   ```
   https://iventario-true.vercel.app/debug/db
   ```
   Deve retornar:
   ```json
   {
     "success": true,
     "db": {
       "can_connect": true,
       "error": null
     }
   }
   ```

### Passo 3: Se Ambos Retornarem SUCCESS

Seu app está correto. O problema pode estar no cliente (frontend).

**Verificar no Console do Browser (F12):**

1. Abra o DevTools (F12)
2. Vá para **Console**
3. Tente cadastrar um equipamento
4. Procure por mensagens de erro
5. Vá para a aba **Network**
6. Procure pela requisição POST para `/equipamento/adicionar`
7. Verifique:
   - **Status**: Deve ser 201 (Created) ou 200 (OK)
   - **Response**: Deve ter `"success": true`

### Passo 4: Se Retornar ERRO de Conexão

Você precisa:

1. Acessar **https://supabase.com/dashboard**
2. Selecionar projeto: **ttfpqsdctnkzwrrhfssb**
3. Ir para **Settings → API**
4. Copiar:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** → `SUPABASE_KEY`
5. Atualizar no Vercel:
   - **Project Settings → Environment Variables**
   - Cole os novos valores
   - Clique **Save**

6. Faça um **Redeploy** (ou push para GitHub)
   - Em **Deployments**, clique nos **...** ao lado do último deploy
   - Selecione **Redeploy**

## 📝 Logs para Verificar

No Vercel, você pode ver logs detalhados:

1. **Deployments → Função**
2. **Clique no seu deployment mais recente**
3. **Vá para "Logs"**
4. **Procure por linhas com**:
   - `❌ Erro ao criar equipamento`
   - `Criando equipamento com dados`
   - `Invalid API key`

## 🚀 Checklist de Resolução

- [ ] SUPABASE_URL está configurado em Vercel
- [ ] SUPABASE_KEY está configurado em Vercel
- [ ] `/debug/config` retorna SUCCESS
- [ ] `/debug/db` retorna SUCCESS
- [ ] Você fez Redeploy após configurar variáveis
- [ ] Aguardou 60 segundos após Redeploy
- [ ] Limpou cache do Browser (Ctrl+Shift+Delete)
- [ ] Tentou em uma aba incógnita

## 💡 Dicas Extras

**Se ainda não funcionar:**

1. Verifique permissões RLS no Supabase:
   - **Supabase Dashboard → Authentication → Policies**
   - A tabela `equipamentos` deve permitir INSERT

2. Teste localmente:
   ```bash
   python -c "
   from dotenv import load_dotenv
   load_dotenv()
   from app.models_supabase import Equipamento
   eq = Equipamento.create(
     nome='Test',
     tipo='Test',
     marca='Test',
     modelo='Test',
     numero_serie='TEST-123',
     status='Estoque'
   )
   print(f'✅ Equipamento criado: {eq.id}')
   "
   ```

3. Abra uma issue no GitHub com:
   - Output do `/debug/config`
   - Output do `/debug/db`
   - Erro completo do `/equipamento/adicionar`
   - Logs do Vercel (se possível)

---

**Última atualização**: 2025-12-05
**Status**: Em diagnóstico
