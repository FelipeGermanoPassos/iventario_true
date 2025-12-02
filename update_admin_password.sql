-- Atualizar senha do administrador para 'admin123'
-- Execute este script no SQL Editor do Supabase

UPDATE usuarios 
SET senha_hash = 'scrypt:32768:8:1$XN02Gfv9JnFVXCaf$47c5433cfe8cc05465a61986e5fe17526ef5669e5075ede04f81c0b442d12f6e65c32417e22f87d04afc29dc6fd15d5d90e1ffebf9c7db7ef5a6a44ecd29f132'
WHERE email = 'admin@inventario.com';

-- Verificar se foi atualizado
SELECT 
    id, 
    nome, 
    email, 
    is_admin, 
    ativo,
    'Senha atualizada com sucesso! Use: admin123' as status
FROM usuarios 
WHERE email = 'admin@inventario.com';
