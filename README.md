# Sistema de Inventário de Equipamentos TI

Sistema web completo para gerenciamento de equipamentos de TI com controle de estoque e empréstimos.

## 📋 Funcionalidades

### Gestão de Estoque
- ✅ **Adicionar Equipamentos**: Cadastro completo com detalhes técnicos
- ✏️ **Editar Equipamentos**: Atualização de informações cadastradas
- 🗑️ **Deletar Equipamentos**: Remoção de equipamentos do inventário
- 📦 **Controle de Status**: Estoque, Emprestado, Manutenção, Inativo

### Gestão de Empréstimos
- 📋 **Novo Empréstimo**: Registre empréstimos com responsável e departamento
- 🔍 **Buscar Equipamentos**: Pesquise equipamentos disponíveis em estoque
- ✓ **Registrar Devolução**: Marque devoluções e retorne equipamento ao estoque
- 📅 **Data Prevista**: Controle de datas de devolução prevista
- 📧 **Contatos**: E-mail e telefone do responsável

### Relatórios e Análises
- 📊 **Relatórios Completos**: Visualize empréstimos com filtros avançados
- 🎯 **Filtros Inteligentes**: Ativos, histórico, atrasados, por período e departamento
- 📈 **Gráficos Interativos**: 
  - Empréstimos por departamento
  - Top 10 equipamentos mais emprestados
- 📊 **Estatísticas Detalhadas**: Total, ativos, devolvidos, atrasados e duração média
- 📥 **Exportação CSV**: Exporte relatórios para planilhas
- 📄 **Exportação PDF**: Gere relatórios profissionais em PDF com tabelas e estatísticas
- ⚠️ **Alertas Visuais**: Identificação de empréstimos atrasados

### Dashboard Interativo
- 📊 **Estatísticas em Tempo Real**:
  - Total de equipamentos
  - Equipamentos em estoque
  - Equipamentos emprestados
  - Equipamentos em manutenção
  - Taxa de utilização de equipamentos
  - Valor total do inventário
  - Valor médio por equipamento
  - Custo total de manutenções
  - Manutenções pendentes
  - Empréstimos recentes (últimos 30 dias)
  - Devoluções pendentes
- 📈 **Gráficos Visuais**:
  - Equipamentos por status (rosca)
  - Equipamentos por tipo (barras)
  - Empréstimos ativos por departamento (barras horizontais)
  - Top 5 equipamentos mais emprestados (barras horizontais)
  
### Recursos Adicionais
- 🔍 **Busca em Tempo Real**: Filtragem rápida de equipamentos e empréstimos
- 🏷️ **Categorização Inteligente**: Campos dinâmicos por tipo (Computador, Notebook, Periférico)
- 💾 **Banco de Dados Relacional**: SQLite com relacionamentos entre tabelas

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python Flask
- **Banco de Dados**: SQLite com SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript
- **Gráficos**: Chart.js
- **Relatórios PDF**: ReportLab
- **Design**: Responsivo e moderno

## 📦 Instalação

### 1. Instalar dependências

```powershell
pip install -r requirements.txt
```

### 2. Criar usuário administrador

```powershell
python criar_admin.py
```

**Credenciais padrão:**
- Email: `admin@inventario.com`
- Senha: `admin123`
- ⚠️ **IMPORTANTE**: Altere a senha após o primeiro login!

### 3. Executar o servidor

```powershell
python run.py
```

### 4. Acessar o sistema

Abra seu navegador em: **http://localhost:5000**

### 5. Instalar no Android (PWA)

Para instalar o sistema como aplicativo no Android (PWA), é necessário acessar via HTTPS no celular.

1) Execute o servidor local no PC

```powershell
python run.py
```

2) Exponha o servidor com HTTPS (ex.: ngrok)

Instale e rode o ngrok (ou similar) para gerar uma URL HTTPS pública que aponte para seu servidor local.

```powershell
ngrok http http://localhost:5000
```

3) No Android (Chrome)
- Abra a URL HTTPS gerada pelo ngrok (ex.: https://xxxxx.ngrok-free.app)
- Aguarde carregar e toque em “Instalar app” (ou abra o menu do Chrome › “Adicionar à tela inicial”)
- Abra o app instalado da tela inicial (modo tela cheia)

4) Dicas e permissões
- Conceda permissão de câmera ao app para tirar fotos dos equipamentos direto do celular
- Para melhor experiência, adicione ícones PNG em `app/static/icons`:
   - `icon-192.png` (192x192)
   - `icon-512.png` (512x512)

5) Observações importantes
- Service Worker (necessário para PWA) exige HTTPS em dispositivos móveis
- Se atualizou o sistema e não viu mudanças no app, feche e reabra o aplicativo (o SW atualiza em segundo plano)

## 📂 Estrutura do Projeto

```
iventario_true/
├── app/
│   ├── __init__.py          # Inicialização do Flask e Login
│   ├── models.py            # Modelos do banco de dados
│   ├── routes.py            # Rotas e APIs
│   ├── static/
│   │   ├── css/
│   │   │   ├── style.css    # Estilos principais
│   │   │   ├── login.css    # Estilos da tela de login
│   │   │   ├── perfil.css   # Estilos da tela de perfil
│   │   │   ├── admin.css    # Estilos do painel admin
│   │   │   └── relatorios.css # Estilos da página de relatórios
│   │   └── js/
│   │       ├── app.js       # JavaScript principal
│   │       ├── login.js     # JavaScript do login
│   │       ├── perfil.js    # JavaScript do perfil
│   │       ├── admin.js     # JavaScript do painel admin
│   │       └── relatorios.js # JavaScript dos relatórios
│   └── templates/
│       ├── index.html       # Template principal
│       ├── login.html       # Template de login
│       ├── perfil.html      # Template de perfil
│       ├── admin.html       # Template do painel admin
│       └── relatorios.html  # Template de relatórios
├── instance/
│   └── inventario.db        # Banco de dados SQLite
├── criar_admin.py           # Script para criar admin
├── run.py                   # Arquivo principal para executar
├── requirements.txt         # Dependências do projeto
└── README.md               # Este arquivo
```

## 💻 Uso do Sistema

### Primeiro Acesso

1. Acesse **http://localhost:5000**
2. Faça login com as credenciais do administrador:
   - Email: `admin@inventario.com`
   - Senha: `admin123`
3. Ou crie uma nova conta clicando em **"Cadastre-se"**

### Registrar Novo Usuário

1. Na tela de login, clique em **"Cadastre-se"**
2. Preencha os dados:
   - Nome completo (obrigatório)
   - Email (obrigatório)
   - Departamento (opcional)
   - Telefone (opcional)
   - Senha (mínimo 6 caracteres)
   - Confirmar senha
3. Clique em **"Cadastrar"**
4. Após o cadastro, faça login com suas credenciais

### Acessar Perfil

1. No header, clique no seu nome (👤 Seu Nome)
2. Na página de perfil você pode:
   - **Atualizar dados pessoais**: Nome, email, departamento, telefone
   - **Alterar senha**: Digite a senha atual e a nova senha
   - Ver informações da conta (data de cadastro, último acesso)
3. Clique em **"💾 Salvar Alterações"** para atualizar dados
4. Clique em **"🔑 Alterar Senha"** para mudar a senha

### Painel Administrativo (Apenas para Admins)

1. No header, clique no botão **"⚙️ Admin"** (visível apenas para administradores)
2. No painel você pode:
   - **Visualizar estatísticas**: Total de usuários, ativos, inativos e administradores
   - **Listar todos os usuários**: Nome, email, departamento, status, tipo
   - **Buscar usuários**: Filtrar por nome, email ou departamento
   - **Ativar/Desativar usuário**: Botão 🚫/✅
   - **Promover a Admin**: Botão ⭐ (torna usuário administrador)
   - **Remover Admin**: Botão 👤 (remove privilégios de admin)
   - **Deletar usuário**: Botão 🗑️ (requer confirmação)
3. **Restrições de segurança**:
   - Não é possível desativar, remover admin ou deletar sua própria conta
   - Todas as ações requerem confirmação

### Relatórios de Empréstimos

1. No header, clique no botão **"📊 Relatórios"**
2. Use os filtros para visualizar:
   - **Tipo de Relatório**: Todos, Ativos, Histórico (Devolvidos), Atrasados
   - **Departamento**: Filtre por departamento específico
   - **Período**: Defina data inicial e final
3. Visualize as estatísticas:
   - Total de empréstimos no período
   - Empréstimos ativos, devolvidos e atrasados
   - Duração média dos empréstimos
4. Analise os gráficos:
   - Empréstimos por departamento (barras)
   - Top 10 equipamentos mais emprestados (barras horizontais)
5. Consulte a tabela detalhada com:
   - Nome do equipamento
   - Responsável e departamento
   - Datas de empréstimo, previsão e devolução
   - Status com identificação visual de atrasados
   - Quantidade de dias do empréstimo
6. **Exportar dados**: 
   - Clique em "📥 Exportar CSV" para baixar planilha
   - Clique em "📄 Exportar PDF" para gerar relatório profissional em PDF

### Adicionar Equipamento

1. Na aba **"📦 Estoque"**, clique no botão **"+ Novo Equipamento"**
2. Selecione a categoria: **Computador**, **Notebook** ou **Periférico**
3. Preencha o formulário com as informações:
   - **Obrigatórios**: Nome, Tipo, Marca, Modelo, Número de Série, Status
   - **Computador/Notebook**: Processador, RAM (obrigatório), Armazenamento (obrigatório), SO
   - **Periférico**: Conectividade, Compatibilidade
   - **Opcionais**: Data de Aquisição, Valor, Observações
4. Clique em **"Salvar"**

### Registrar Empréstimo

1. Vá para a aba **"📋 Empréstimos"**
2. Clique no botão **"📦 Novo Empréstimo"**
3. Busque e selecione o equipamento disponível em estoque
4. Preencha os dados do empréstimo:
   - **Responsável** (obrigatório)
   - **Departamento** (obrigatório)
   - E-mail e telefone (opcionais)
   - Data de devolução prevista
   - Observações
5. Clique em **"Registrar Empréstimo"**
6. O equipamento automaticamente muda o status para "Emprestado"

### Devolver Equipamento

1. Na aba **"📋 Empréstimos"**, localize o empréstimo ativo
2. Clique no botão **"✓ Devolver"**
3. Confirme a devolução
4. O equipamento volta automaticamente para o status "Estoque"

### Deletar Equipamento

1. Na lista de equipamentos, clique no botão **"🗑️ Deletar"**
2. Confirme a exclusão

### Buscar

**Equipamentos**: Use o campo de busca na aba Estoque para filtrar por nome, tipo, marca, modelo ou número de série

**Empréstimos**: Use o campo de busca na aba Empréstimos para filtrar por equipamento, responsável ou departamento

## 🎨 Características do Dashboard

- **Tabs de Navegação**: Alterne facilmente entre Estoque e Empréstimos
- **Cards Estatísticos**: Visualização rápida de totais e métricas importantes
- **Gráficos Interativos**: 
  - Rosca para distribuição por status
  - Barras para tipos de equipamentos
- **Atualização Automática**: Dashboard se atualiza após cada operação
- **Busca Inteligente**: Filtros em tempo real para equipamentos disponíveis

## 🗄️ Modelo de Dados

### Usuário

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | ID único |
| nome | String | Nome completo |
| email | String | Email (único) |
| senha_hash | String | Senha criptografada |
| departamento | String | Departamento/Setor |
| telefone | String | Telefone de contato |
| is_admin | Boolean | Administrador (padrão: false) |
| ativo | Boolean | Conta ativa (padrão: true) |
| data_cadastro | DateTime | Data de cadastro |
| ultimo_acesso | DateTime | Data do último acesso |

### Equipamento

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | ID único |
| nome | String | Nome do equipamento |
| tipo | String | Tipo (Desktop, Notebook, Monitor, etc.) |
| marca | String | Marca/fabricante |
| modelo | String | Modelo específico |
| numero_serie | String | Número de série (único) |
| processador | String | Informações do processador |
| memoria_ram | String | Quantidade de RAM |
| armazenamento | String | Capacidade de armazenamento |
| sistema_operacional | String | Sistema operacional |
| status | String | Status (Estoque, Emprestado, Manutenção, Inativo) |
| data_aquisicao | Date | Data de aquisição |
| valor | Float | Valor do equipamento |
| observacoes | Text | Observações adicionais |
| data_cadastro | DateTime | Data de cadastro no sistema |
| data_atualizacao | DateTime | Última atualização |

### Empréstimo

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | ID único |
| equipamento_id | Integer | ID do equipamento (FK) |
| responsavel | String | Nome do responsável |
| departamento | String | Departamento/Setor |
| email_responsavel | String | E-mail para contato |
| telefone_responsavel | String | Telefone para contato |
| data_emprestimo | DateTime | Data/hora do empréstimo |
| data_devolucao_prevista | Date | Data prevista de devolução |
| data_devolucao_real | DateTime | Data/hora da devolução real |
| status | String | Status (Ativo, Devolvido, Atrasado) |
| observacoes | Text | Observações sobre o empréstimo |

## 🔒 APIs Disponíveis

### Autenticação
- `GET /login` - Página de login
- `POST /login` - Autenticar usuário
- `GET /registro` - Página de registro
- `POST /registro` - Registrar novo usuário
- `GET /logout` - Deslogar usuário
- `GET /perfil` - Página de perfil (requer autenticação)
- `POST /perfil` - Atualizar dados ou alterar senha (requer autenticação)

### Administração (Requer Admin)
- `GET /admin` - Painel administrativo
- `GET /admin/usuarios` - Lista todos os usuários
- `PUT /admin/usuario/<id>/toggle-ativo` - Ativa/desativa usuário
- `PUT /admin/usuario/<id>/toggle-admin` - Promove/remove admin
- `DELETE /admin/usuario/<id>/deletar` - Deleta usuário
- `POST /admin/usuario/adicionar` - Adiciona novo usuário
- `PUT /admin/usuario/<id>/editar` - Edita usuário

### Relatórios
- `GET /relatorios` - Página de relatórios
- `GET /relatorios/emprestimos` - Dados de empréstimos com filtros (query params: filtro, data_inicio, data_fim, departamento)
- `GET /relatorios/departamentos` - Lista departamentos únicos
- `GET /relatorios/exportar-pdf` - Gera e baixa relatório em PDF (query params: filtro, data_inicio, data_fim, departamento)

### Equipamentos
- `GET /` - Página principal (requer autenticação)
- `GET /dashboard-data` - Dados para o dashboard
- `GET /equipamentos` - Lista todos os equipamentos
- `GET /equipamentos-estoque` - Lista apenas equipamentos em estoque
- `GET /equipamento/<id>` - Obtém um equipamento específico
- `POST /equipamento/adicionar` - Adiciona novo equipamento
- `PUT /equipamento/editar/<id>` - Edita equipamento existente
- `DELETE /equipamento/deletar/<id>` - Deleta equipamento

### Empréstimos
- `GET /emprestimos` - Lista todos os empréstimos
- `GET /emprestimos-ativos` - Lista apenas empréstimos ativos
- `GET /emprestimo/<id>` - Obtém um empréstimo específico
- `POST /emprestimo/adicionar` - Registra novo empréstimo
- `PUT /emprestimo/devolver/<id>` - Registra devolução
- `DELETE /emprestimo/deletar/<id>` - Deleta empréstimo

## 📱 Responsividade

O sistema é totalmente responsivo e funciona em:
- 💻 Desktop
- 📱 Tablet
- 📱 Smartphone

## 🚀 Melhorias Implementadas

- [x] Autenticação de usuários
- [x] Perfil de usuário com alteração de senha
- [x] Painel administrativo para gerenciar usuários
- [x] Relatórios de empréstimos (ativos, histórico, atrasados)
- [x] Exportação de relatórios em PDF
- [x] Upload de fotos dos equipamentos
- [x] Histórico de manutenções
- [x] Notificações de devolução próxima ao vencimento
- [x] Alertas de empréstimos atrasados
- [x] QR Code para identificação rápida
- [x] Backup automático do banco de dados
- [x] Dashboard com mais métricas (empréstimos por departamento, taxa de utilização, custos de manutenção, equipamentos populares)
- [x] PWA (Progressive Web App) para instalação no Android
- [x] UI com paleta de cores TrueSource (laranja #EF7D2D)

## 💡 Sugestões para Evolução Futura

### 🔔 Notificações e Comunicação
- [ ] **Envio de e-mails automáticos**: Notificar responsáveis sobre devoluções próximas e atrasadas
- [ ] **Sistema de lembretes**: Alertas personalizados para usuários (3 dias antes, 1 dia antes, no vencimento)
- [ ] **Notificações push no PWA**: Alertas instantâneos no app mobile
- [ ] **WhatsApp/SMS**: Integração para envio de lembretes via WhatsApp Business API

### 📊 Análise e Inteligência
- [ ] **Dashboard executivo**: Métricas gerenciais e KPIs (custo por departamento, ROI de equipamentos)
- [ ] **Previsão de demanda**: IA para prever necessidades de compra baseado no histórico
- [ ] **Análise de uso**: Identificar equipamentos subutilizados ou mais requisitados
- [ ] **Relatórios agendados**: Envio automático de relatórios semanais/mensais por e-mail
- [ ] **Comparativo temporal**: Gráficos de evolução (mês a mês, ano a ano)

### 🔧 Gestão Avançada
- [ ] **Garantias**: Controle de prazo de garantia com alertas de vencimento
- [ ] **Depreciação**: Cálculo automático de depreciação de ativos
- [ ] **Contratos de manutenção**: Gestão de contratos com fornecedores e prazos
- [ ] **Agenda de manutenções preventivas**: Calendário com lembretes automáticos
- [ ] **Histórico de incidentes**: Registrar problemas e soluções aplicadas
- [ ] **Checklist de entrega/devolução**: Verificação de estado do equipamento

### 👥 Colaboração e Workflow
- [ ] **Sistema de solicitações**: Usuários podem solicitar equipamentos (workflow de aprovação)
- [ ] **Fila de espera**: Reserva de equipamentos emprestados
- [ ] **Avaliação pós-devolução**: Responsável avaliar estado do equipamento
- [ ] **Comentários e tags**: Colaboração entre usuários sobre equipamentos
- [ ] **Múltiplas localizações**: Gestão de equipamentos em diferentes prédios/cidades
- [ ] **Transferência entre departamentos**: Workflow de transferência de responsabilidade

### 🔒 Segurança e Auditoria
- [ ] **Log de auditoria**: Registrar todas as ações dos usuários
- [ ] **Autenticação em dois fatores (2FA)**: Maior segurança no acesso
- [ ] **Níveis de permissão**: Roles customizados (visualizador, operador, gerente, admin)
- [ ] **Backup em nuvem**: Integração com Google Drive, OneDrive ou S3
- [ ] **Termos de uso**: Aceite digital do termo de responsabilidade no empréstimo
- [ ] **Assinatura digital**: Registrar assinatura do responsável na retirada

### 📱 Mobile e Integração
- [ ] **App nativo**: Versão iOS (Swift) e Android (Kotlin)
- [ ] **Leitor de QR Code integrado**: Scan direto pelo app para identificar equipamentos
- [ ] **Modo offline**: Funcionalidade limitada sem internet
- [ ] **API REST documentada**: Swagger/OpenAPI para integrações externas
- [ ] **Integração com Active Directory/LDAP**: Autenticação corporativa
- [ ] **Integração com sistemas ERP**: Sincronização com SAP, Totvs, etc.

### 📦 Recursos de Estoque
- [ ] **Controle de acessórios**: Gerenciar cabos, fontes, mouses junto com equipamentos
- [ ] **Kits de equipamentos**: Agrupar itens (ex: notebook + mouse + case)
- [ ] **Estoque mínimo**: Alertas quando quantidade disponível fica baixa
- [ ] **Fornecedores**: Cadastro de fornecedores com histórico de compras
- [ ] **Ordem de compra**: Gerar pedidos de compra para reposição
- [ ] **Entrada/Saída física**: Controle de movimentação com código de barras

### 🎨 Interface e UX
- [ ] **Tema escuro**: Dark mode para conforto visual
- [ ] **Idiomas**: Suporte multilíngue (PT, EN, ES)
- [ ] **Personalização**: Usuário escolher cores, layout do dashboard
- [ ] **Atalhos de teclado**: Navegação rápida (Ctrl+N para novo, etc.)
- [ ] **Tutorial interativo**: Onboarding para novos usuários
- [ ] **Modo kiosko**: Tela de autoatendimento para empréstimos

### 📈 Otimização Técnica
- [ ] **Cache Redis**: Melhorar performance em consultas frequentes
- [ ] **PostgreSQL**: Migrar de SQLite para banco mais robusto
- [ ] **Docker**: Containerização para fácil deploy
- [ ] **CI/CD**: Pipeline automatizado (GitHub Actions, GitLab CI)
- [ ] **Testes automatizados**: Unitários, integração e E2E
- [ ] **Monitoramento**: Integração com Sentry, New Relic ou DataDog
- [ ] **CDN**: Servir assets estáticos via CDN para melhor performance

## 📝 Licença

Este projeto está disponível para uso livre.

## 👨‍💻 Suporte

Para dúvidas ou sugestões, consulte a documentação do Flask em: https://flask.palletsprojects.com/
