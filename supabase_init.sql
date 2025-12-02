-- Script SQL para criar todas as tabelas do Sistema de Inventário no Supabase
-- Execute este script no SQL Editor do painel do Supabase

-- Tabela de Usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    departamento VARCHAR(100),
    telefone VARCHAR(20),
    is_admin BOOLEAN DEFAULT FALSE,
    ativo BOOLEAN DEFAULT TRUE,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acesso TIMESTAMP
);

-- Tabela de Equipamentos
CREATE TABLE IF NOT EXISTS equipamentos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(100) NOT NULL,
    numero_serie VARCHAR(100) UNIQUE NOT NULL,
    processador VARCHAR(100),
    memoria_ram VARCHAR(50),
    armazenamento VARCHAR(50),
    sistema_operacional VARCHAR(50),
    status VARCHAR(20) NOT NULL,
    data_aquisicao DATE,
    valor FLOAT,
    vida_util_anos INTEGER DEFAULT 5,
    departamento_atual VARCHAR(100),
    observacoes TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Empréstimos
CREATE TABLE IF NOT EXISTS emprestimos (
    id SERIAL PRIMARY KEY,
    equipamento_id INTEGER NOT NULL REFERENCES equipamentos(id),
    responsavel VARCHAR(100) NOT NULL,
    departamento VARCHAR(100) NOT NULL,
    email_responsavel VARCHAR(100),
    telefone_responsavel VARCHAR(20),
    telegram_chat_id VARCHAR(50),
    data_emprestimo TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_devolucao_prevista DATE,
    data_devolucao_real TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'Ativo',
    observacoes TEXT
);

-- Tabela de Fotos de Equipamentos
CREATE TABLE IF NOT EXISTS equipamentos_fotos (
    id SERIAL PRIMARY KEY,
    equipamento_id INTEGER NOT NULL REFERENCES equipamentos(id) ON DELETE CASCADE,
    url VARCHAR(255) NOT NULL,
    principal BOOLEAN DEFAULT TRUE,
    data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Manutenções
CREATE TABLE IF NOT EXISTS manutencoes (
    id SERIAL PRIMARY KEY,
    equipamento_id INTEGER NOT NULL REFERENCES equipamentos(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL,
    descricao TEXT,
    data_inicio DATE,
    data_fim DATE,
    custo FLOAT,
    responsavel VARCHAR(100),
    fornecedor VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Em Andamento',
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Subscrições Push
CREATE TABLE IF NOT EXISTS push_subscriptions (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    endpoint VARCHAR(500) UNIQUE NOT NULL,
    p256dh VARCHAR(255) NOT NULL,
    auth VARCHAR(255) NOT NULL,
    user_agent VARCHAR(255),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativa BOOLEAN DEFAULT TRUE
);

-- Criar índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_equipamentos_numero_serie ON equipamentos(numero_serie);
CREATE INDEX IF NOT EXISTS idx_equipamentos_status ON equipamentos(status);
CREATE INDEX IF NOT EXISTS idx_emprestimos_equipamento_id ON emprestimos(equipamento_id);
CREATE INDEX IF NOT EXISTS idx_emprestimos_status ON emprestimos(status);
CREATE INDEX IF NOT EXISTS idx_push_subscriptions_usuario_id ON push_subscriptions(usuario_id);

-- Criar usuário administrador inicial
-- IMPORTANTE: Altere a senha após o primeiro login!
INSERT INTO usuarios (nome, email, senha_hash, departamento, is_admin, ativo)
VALUES (
    'Administrador',
    'admin@inventario.com',
    'scrypt:32768:8:1$m1dPZ3HqslOJ7DfZ$87c8cf0ca5e33d3f43e7e2f9f5fc3f55c77a9e79dd3be7e5b9b0a5c2f6b8d4a2c0fb8e6a5d9c7f2e8a3b5d7c0f1e9a4b8c6d2f5e0a7c3b9d1f4e8a2c5b7d0',
    'TI',
    TRUE,
    TRUE
)
ON CONFLICT (email) DO NOTHING;

-- Mensagem de conclusão
SELECT 
    '✅ Tabelas criadas com sucesso!' as status,
    COUNT(*) as total_tabelas
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('usuarios', 'equipamentos', 'emprestimos', 'equipamentos_fotos', 'manutencoes', 'push_subscriptions');
