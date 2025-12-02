# Configuração do Telegram Bot para Notificações

## Como Configurar

### 1. Criar um Bot no Telegram

1. Abra o Telegram e procure por `@BotFather`
2. Envie o comando `/newbot`
3. Escolha um nome para o bot (ex: "Inventário TI Notificações")
4. Escolha um username para o bot (deve terminar com "bot", ex: "inventario_ti_bot")
5. O BotFather vai te dar um **Token**. Guarde-o!
   - Exemplo: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz123456789`

### 2. Configurar no Sistema

#### Opção A: Via Variáveis de Ambiente

**Windows PowerShell:**
```powershell
$env:TELEGRAM_ENABLED="true"
$env:TELEGRAM_BOT_TOKEN="8582112542:AAHyb8dNKC4N6Ae8m-iwahWObJDRuYKsByg"
python run.py
```

**Linux/Mac:**
```bash
export TELEGRAM_ENABLED=true
export TELEGRAM_BOT_TOKEN="8582112542:AAHyb8dNKC4N6Ae8m-iwahWObJDRuYKsByg"
python run.py
```

#### Opção B: Via Interface Web

1. Acesse: http://localhost:5000/admin
2. Clique na aba **"Telegram"**
3. Clique em **"⚙️ Configurar Sistema de Telegram"**
4. Cole o token do bot
5. Marque **"Habilitar Telegram"**
6. Clique em **"💾 Salvar Configurações"**

### 3. Obter o Chat ID dos Usuários

⚠️ **IMPORTANTE - ORDEM OBRIGATÓRIA:**

**🔴 PASSO 1 (OBRIGATÓRIO):** Inicie conversa com o bot primeiro!
1. Procure por `@truebrands_inventario_bot` no Telegram
2. **Clique em "Iniciar"** ou envie `/start`
3. ⚠️ Isso é OBRIGATÓRIO - o Telegram não permite que bots enviem mensagens para quem nunca iniciou conversa (política anti-spam)

**🔵 PASSO 2:** Descubra seu Chat ID:
- ✅ Correto: `123456789` ou `987654321` (NÚMEROS)
- ❌ Errado: `@Felipegerpassos` ou `@username`

Cada usuário precisa descobrir seu **Chat ID numérico** para receber notificações:

#### 🎯 Método 1: Usar @userinfobot (MAIS FÁCIL)
1. No Telegram, procure por `@userinfobot`
2. **Clique em "Iniciar"** ou envie qualquer mensagem
3. Ele responderá instantaneamente com:
   ```
   Id: 123456789
   First name: Seu Nome
   Username: @seuusername
   ```
4. **COPIE APENAS O NÚMERO** após "Id:" (ex: `123456789`)

#### 🔧 Método 2: Usar seu próprio bot
1. Primeiro, **inicie conversa com seu bot**:
   - Procure por `@truebrands_inventario_bot` (seu bot)
   - Clique em **"Iniciar"** ou envie `/start`
   - **IMPORTANTE:** Envie qualquer mensagem para ativar o chat

2. Acesse no navegador (substitua o token):
   ```
   https://api.telegram.org/bot8582112542:AAHyb8dNKC4N6Ae8m-iwahWObJDRuYKsByg/getUpdates
   ```

3. Procure no JSON retornado por:
   ```json
   "chat": {
     "id": 123456789,
     "first_name": "Seu Nome",
     "username": "seuusername"
   }
   ```

4. **COPIE APENAS O NÚMERO** do campo "id" (ex: `123456789`)

### 4. Cadastrar Chat ID no Sistema

1. Ao registrar um **novo empréstimo**, preencha o campo **"Chat ID Telegram"**
2. Use o número obtido na etapa anterior (ex: `123456789`)
3. O sistema enviará notificações automaticamente para esse usuário!

## Tipos de Notificações

O sistema envia mensagens Telegram automaticamente para:

- ✅ **Confirmação de empréstimos**: Quando um equipamento é emprestado
- ✅ **Confirmação de devoluções**: Quando um equipamento é devolvido
- ⏰ **Lembretes**: 3 dias antes da devolução prevista
- 🚨 **Alertas de atraso**: Quando a devolução está atrasada

## Teste de Envio

1. Acesse o painel admin
2. Vá na aba **"Telegram"**
3. Digite seu Chat ID
4. Clique em **"🧪 Testar Telegram"**
5. Você deve receber uma mensagem de teste no Telegram!

## Permissões do Bot

O bot precisa apenas de permissões básicas:
- ✅ Enviar mensagens
- ✅ Receber mensagens (para comandos futuros)

**Não precisa de:**
- ❌ Acesso a grupos
- ❌ Permissões de admin
- ❌ Inline mode (opcional)

## Solução de Problemas

### "Bot was blocked by the user"
**Causa:** Usuário bloqueou o bot ou deletou a conversa.
**Solução:** 
1. Procure o bot no Telegram
2. Clique em "Iniciar" ou envie `/start`
3. Se bloqueou, desbloqueie nas configurações

### "Chat not found"
**Causa:** Chat ID incorreto ou bot nunca iniciou conversa com usuário.
**Solução:**
1. Verifique se o Chat ID está correto
2. Certifique-se de que iniciou conversa com o bot (envie /start)
3. Use @userinfobot para confirmar seu Chat ID

### "Unauthorized"
**Causa:** Token do bot inválido ou revogado.
**Solução:**
1. Verifique se copiou o token completo
2. Se necessário, gere um novo token com @BotFather
3. Atualize o token no sistema

### "Timeout" ou "Connection Error"
**Causa:** Problemas de conexão com a internet ou API do Telegram.
**Solução:**
1. Verifique sua conexão com a internet
2. Tente novamente em alguns minutos
3. A API do Telegram pode estar temporariamente indisponível

## Recursos Avançados (Futuro)

- [ ] Comandos interativos (/status, /emprestimos, /solicitar)
- [ ] Botões inline para confirmar devoluções
- [ ] Notificações em grupos/canais
- [ ] Renovação de empréstimo via bot
- [ ] Consulta de equipamentos disponíveis

## Links Úteis

- **BotFather:** https://t.me/BotFather
- **Bot API Documentation:** https://core.telegram.org/bots/api
- **userinfobot:** https://t.me/userinfobot
- **Telegram Web:** https://web.telegram.org

## Exemplo de Arquivo .env

```env
# Telegram Bot Configuration
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz123456789
```

## Dicas

1. **Privacidade**: Chat IDs são números únicos e não expõem informações pessoais
2. **Gratuito**: Telegram Bot API é 100% gratuita, sem limites de mensagens
3. **Instantâneo**: Mensagens chegam em tempo real, mais rápido que e-mail
4. **Multi-plataforma**: Funciona em Android, iOS, Desktop e Web
5. **Sem número de telefone**: Usuários não precisam compartilhar número
