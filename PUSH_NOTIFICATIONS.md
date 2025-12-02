# Configuração de Notificações Push - Sistema de Inventário TI

## 📋 Visão Geral

As notificações push permitem que o sistema envie alertas instantâneos para os dispositivos dos usuários, mesmo quando o app PWA está fechado. Isso é especialmente útil para:

- ✅ Confirmações de empréstimos e devoluções
- ⏰ Lembretes de devolução (3 dias antes)
- 🚨 Alertas de empréstimos atrasados
- 📊 Notificações administrativas

## 🔧 Requisitos

- Navegador moderno com suporte a Push API:
  - Chrome 50+
  - Edge 79+
  - Firefox 44+
  - Safari 16+ (macOS, iOS)
  - Opera 37+
  
- Conexão HTTPS (obrigatório para Service Workers e Push API)
- Python 3.8+
- Biblioteca pywebpush instalada

## 📦 Instalação

### 1. Instalar dependências

```bash
pip install pywebpush
```

Ou instale todas as dependências do projeto:

```bash
pip install -r requirements.txt
```

### 2. Gerar chaves VAPID

As chaves VAPID (Voluntary Application Server Identification) são necessárias para identificar seu servidor nos serviços de push.

Execute o script de geração:

```bash
python gerar_vapid_keys.py
```

Você verá uma saída similar a:

```
============================================================
Gerador de Chaves VAPID para Push Notifications
============================================================

Gerando chaves VAPID...
✅ Chaves geradas com sucesso!

============================================================
CHAVE PRIVADA (mantenha em segredo):
============================================================
BNpXJ...exemplo...xyz

============================================================
CHAVE PÚBLICA:
============================================================
BOgz...exemplo...abc
============================================================
```

⚠️ **IMPORTANTE:** A chave privada deve ser mantida em SEGREDO! Não compartilhe nem publique no repositório Git.

### 3. Configurar variáveis de ambiente

#### Windows PowerShell:

```powershell
$env:VAPID_PRIVATE_KEY="sua-chave-privada-aqui"
$env:VAPID_PUBLIC_KEY="sua-chave-publica-aqui"
```

#### Linux/Mac:

```bash
export VAPID_PRIVATE_KEY="sua-chave-privada-aqui"
export VAPID_PUBLIC_KEY="sua-chave-publica-aqui"
```

#### Arquivo .env (recomendado):

Crie ou edite o arquivo `.env` na raiz do projeto:

```
VAPID_PRIVATE_KEY=sua-chave-privada-aqui
VAPID_PUBLIC_KEY=sua-chave-publica-aqui
```

### 4. Atualizar banco de dados

Execute o script de migração para criar a tabela de subscrições:

```bash
python atualizar_banco_push.py
```

Saída esperada:

```
============================================================
Atualização do Banco de Dados - Push Notifications
============================================================

Criando novas tabelas...
✅ Tabelas criadas/atualizadas com sucesso!

Nova tabela adicionada:
  - push_subscriptions: Armazena subscrições de notificações push
============================================================
```

### 5. Iniciar o servidor

```bash
python run.py
```

## 👤 Uso - Perspectiva do Usuário

### Ativar notificações no perfil

1. Faça login no sistema
2. Clique no seu nome no header → **"Meu Perfil"**
3. Role até a seção **"🔔 Notificações Push"**
4. Clique no botão **"🔔 Ativar Notificações"**
5. Quando o navegador solicitar, clique em **"Permitir"**
6. Pronto! Você está inscrito para receber notificações

### Testar notificações

No perfil, após ativar as notificações:
- Clique em **"📨 Enviar Notificação de Teste"**
- Você deve receber uma notificação instantânea

### Desativar notificações

- Acesse seu perfil
- Clique em **"🔕 Desativar Notificações"**

## 👨‍💼 Uso - Perspectiva do Administrador

### Enviar notificação para todos os usuários (broadcast)

```bash
POST /admin/push/broadcast
Content-Type: application/json

{
  "title": "Manutenção Agendada",
  "body": "O sistema ficará offline das 22h às 23h",
  "url": "/"
}
```

Resposta:
```json
{
  "success": true,
  "message": "Notificação enviada para 15 usuário(s)"
}
```

## 🔔 Tipos de Notificações Automáticas

O sistema envia automaticamente as seguintes notificações:

### 1. Confirmação de Empréstimo
- **Quando:** Ao registrar um empréstimo
- **Para:** Responsável pelo empréstimo
- **Título:** ✅ Empréstimo Registrado
- **Mensagem:** "Equipamento [nome] emprestado com sucesso"

### 2. Confirmação de Devolução
- **Quando:** Ao devolver um equipamento
- **Para:** Responsável pelo empréstimo
- **Título:** ✅ Devolução Registrada
- **Mensagem:** "Devolução do equipamento [nome] confirmada"

### 3. Lembrete de Devolução
- **Quando:** 3 dias antes da data prevista
- **Para:** Responsável pelo empréstimo
- **Título:** ⏰ Lembrete de Devolução
- **Mensagem:** "Equipamento [nome] deve ser devolvido em X dia(s)"

### 4. Alerta de Atraso
- **Quando:** Após a data de devolução prevista
- **Para:** Responsável pelo empréstimo
- **Título:** 🚨 Devolução Atrasada
- **Mensagem:** "Equipamento [nome] está atrasado há X dia(s)"

## 🛠️ Arquitetura Técnica

### Componentes principais

1. **Service Worker** (`sw.js`):
   - Intercepta eventos de push
   - Exibe notificações no dispositivo
   - Gerencia cliques em notificações

2. **PWA.js** (`pwa.js`):
   - Solicita permissão ao usuário
   - Cria subscrições de push
   - Comunica com o servidor

3. **PushService** (`push_service.py`):
   - Envia notificações via Web Push Protocol
   - Gerencia subscrições expiradas
   - Formata payloads de notificação

4. **Modelo PushSubscription** (`models.py`):
   - Armazena endpoints de subscrição
   - Chaves de criptografia (p256dh, auth)
   - Status de ativação

### Fluxo de funcionamento

```
1. Usuário solicita permissão → Browser
2. Browser gera endpoint → Push Service (Google/Mozilla)
3. Frontend envia endpoint → Backend
4. Backend salva no banco de dados
5. Sistema envia notificação → pywebpush
6. pywebpush envia → Push Service
7. Push Service envia → Dispositivo do usuário
8. Service Worker exibe → Notificação na tela
```

## 🔒 Segurança

### Chaves VAPID

- **Chave Privada:** Mantida apenas no servidor, usada para assinar mensagens
- **Chave Pública:** Compartilhada com o navegador, usada para validar origem

### Criptografia End-to-End

- Todas as mensagens são criptografadas com as chaves p256dh e auth
- Apenas o navegador do usuário pode descriptografar

### HTTPS Obrigatório

- Push API só funciona em conexões seguras (HTTPS)
- Exceção: localhost para desenvolvimento

## 🐛 Solução de Problemas

### "Chave pública VAPID não configurada"

**Problema:** Variáveis de ambiente não definidas

**Solução:**
```bash
# Verifique se as variáveis estão definidas
echo $env:VAPID_PUBLIC_KEY  # Windows
echo $VAPID_PUBLIC_KEY      # Linux/Mac

# Se vazias, defina novamente ou adicione ao .env
```

### "Seu navegador não suporta notificações push"

**Problema:** Navegador muito antigo ou não compatível

**Solução:** Atualize para uma versão recente do Chrome, Firefox, Edge ou Safari 16+

### "Notificações bloqueadas"

**Problema:** Usuário negou permissão anteriormente

**Solução:** 
1. Acesse as configurações do site no navegador
2. Encontre "Notificações"
3. Altere para "Permitir"
4. Recarregue a página

### Subscrição expirada (410 Gone)

**Problema:** Endpoint não é mais válido

**Solução:** O sistema automaticamente marca a subscrição como inativa. Usuário precisa reativar no perfil.

## 📊 Monitoramento

### Verificar subscrições ativas

```python
from app.models import PushSubscription

# Total de subscrições
total = PushSubscription.query.count()

# Subscrições ativas
ativas = PushSubscription.query.filter_by(ativa=True).count()

print(f"Total: {total} | Ativas: {ativas}")
```

### Logs de envio

Verifique os logs da aplicação para monitorar envios:

```
INFO - Push notification enviada com sucesso: 201
INFO - Subscription 42 marcada como inativa
INFO - 15/20 notificações enviadas
```

## 🎯 Boas Práticas

1. **Não envie spam:** Use notificações apenas para informações importantes
2. **Seja específico:** Inclua detalhes relevantes no corpo da mensagem
3. **Use URLs:** Direcione o usuário para a página correta ao clicar
4. **Teste regularmente:** Envie notificações de teste após mudanças
5. **Monitore taxas:** Acompanhe quantas subscrições ficam inativas
6. **Respeite escolhas:** Permita que usuários desativem facilmente

## 📚 Referências

- [Web Push Protocol](https://tools.ietf.org/html/rfc8030)
- [Push API - MDN](https://developer.mozilla.org/pt-BR/docs/Web/API/Push_API)
- [Service Worker - MDN](https://developer.mozilla.org/pt-BR/docs/Web/API/Service_Worker_API)
- [VAPID Specification](https://tools.ietf.org/html/rfc8292)
- [pywebpush Documentation](https://github.com/web-push-libs/pywebpush)

## 💡 Dicas

- Em desenvolvimento, teste com localhost (funciona sem HTTPS)
- Em produção, use ngrok ou similar para ter HTTPS
- Mantenha backup das chaves VAPID (se perder, todos os usuários precisam se reinscrever)
- Monitore o tamanho das mensagens (limite: 4KB)
- Use tags para agrupar notificações relacionadas

## ✅ Checklist de Implementação

- [x] Instalar pywebpush
- [x] Gerar chaves VAPID
- [x] Configurar variáveis de ambiente
- [x] Atualizar banco de dados
- [x] Testar em localhost
- [x] Testar com HTTPS (ngrok)
- [x] Ativar notificações no perfil
- [x] Enviar notificação de teste
- [x] Testar em diferentes navegadores
- [x] Verificar funcionamento com app fechado
- [x] Documentar para equipe

---

**🎉 Parabéns!** Seu sistema agora está equipado com notificações push instantâneas!
