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

### Dashboard Interativo
- 📊 **Estatísticas em Tempo Real**:
  - Total de equipamentos
  - Equipamentos em estoque
  - Equipamentos emprestados
  - Valor total do inventário
- 📈 **Gráficos Visuais**:
  - Equipamentos por status (rosca)
  - Equipamentos por tipo (barras)
  
### Recursos Adicionais
- 🔍 **Busca em Tempo Real**: Filtragem rápida de equipamentos e empréstimos
- 🏷️ **Categorização Inteligente**: Campos dinâmicos por tipo (Computador, Notebook, Periférico)
- 💾 **Banco de Dados Relacional**: SQLite com relacionamentos entre tabelas

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python Flask
- **Banco de Dados**: SQLite com SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript
- **Gráficos**: Chart.js
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
│   │   │   └── login.css    # Estilos da tela de login
│   │   └── js/
│   │       ├── app.js       # JavaScript principal
│   │       └── login.js     # JavaScript do login
│   └── templates/
│       ├── index.html       # Template principal
│       └── login.html       # Template de login
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

## 🚀 Próximas Melhorias Sugeridas

- [x] Autenticação de usuários
- [ ] Perfil de usuário com alteração de senha
- [ ] Painel administrativo para gerenciar usuários
- [ ] Relatórios de empréstimos (ativos, histórico, atrasados)
- [ ] Exportação de dados (PDF, Excel)
- [ ] Upload de fotos dos equipamentos
- [ ] Histórico de manutenções
- [ ] Notificações de devolução próxima ao vencimento
- [ ] Alertas de empréstimos atrasados
- [ ] QR Code para identificação rápida
- [ ] Backup automático do banco de dados
- [ ] Dashboard com mais métricas (empréstimos por departamento, etc.)

## 📝 Licença

Este projeto está disponível para uso livre.

## 👨‍💻 Suporte

Para dúvidas ou sugestões, consulte a documentação do Flask em: https://flask.palletsprojects.com/
