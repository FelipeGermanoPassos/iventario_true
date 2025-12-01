// Exibe mensagens de feedback
function mostrarMensagem(texto, tipo = 'info') {
    const mensagemDiv = document.getElementById('mensagem');
    mensagemDiv.textContent = texto;
    mensagemDiv.className = `message-perfil ${tipo} show`;
    
    // Remove a mensagem após 5 segundos
    setTimeout(() => {
        limparMensagem();
    }, 5000);
}

function limparMensagem() {
    const mensagemDiv = document.getElementById('mensagem');
    mensagemDiv.className = 'message-perfil';
    mensagemDiv.textContent = '';
}

// Formulário de atualização de dados
document.getElementById('formDados').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const nome = document.getElementById('nome').value;
    const email = document.getElementById('email').value;
    const departamento = document.getElementById('departamento').value;
    const telefone = document.getElementById('telefone').value;
    
    try {
        const response = await fetch('/perfil', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                acao: 'atualizar_dados',
                nome,
                email,
                departamento,
                telefone
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensagem(data.message, 'success');
            // Atualiza o nome no header se mudou
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            mostrarMensagem(data.message, 'error');
        }
    } catch (error) {
        mostrarMensagem('Erro ao atualizar dados. Tente novamente.', 'error');
        console.error('Erro:', error);
    }
});

// Formulário de alteração de senha
document.getElementById('formSenha').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const senhaAtual = document.getElementById('senhaAtual').value;
    const senhaNova = document.getElementById('senhaNova').value;
    const senhaConfirmar = document.getElementById('senhaConfirmar').value;
    
    // Validação local
    if (senhaNova !== senhaConfirmar) {
        mostrarMensagem('As senhas não coincidem!', 'error');
        return;
    }
    
    if (senhaNova.length < 6) {
        mostrarMensagem('A nova senha deve ter no mínimo 6 caracteres!', 'error');
        return;
    }
    
    try {
        const response = await fetch('/perfil', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                acao: 'alterar_senha',
                senha_atual: senhaAtual,
                senha_nova: senhaNova,
                senha_confirmar: senhaConfirmar
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensagem(data.message, 'success');
            // Limpa o formulário
            document.getElementById('formSenha').reset();
        } else {
            mostrarMensagem(data.message, 'error');
        }
    } catch (error) {
        mostrarMensagem('Erro ao alterar senha. Tente novamente.', 'error');
        console.error('Erro:', error);
    }
});

// Máscara de telefone
document.getElementById('telefone').addEventListener('input', (e) => {
    let valor = e.target.value.replace(/\D/g, '');
    if (valor.length > 11) valor = valor.slice(0, 11);
    
    if (valor.length > 6) {
        valor = valor.replace(/^(\d{2})(\d{5})(\d{0,4}).*/, '($1) $2-$3');
    } else if (valor.length > 2) {
        valor = valor.replace(/^(\d{2})(\d{0,5})/, '($1) $2');
    } else if (valor.length > 0) {
        valor = valor.replace(/^(\d*)/, '($1');
    }
    
    e.target.value = valor;
});

// Previne espaços no campo de email
document.getElementById('email').addEventListener('keypress', (e) => {
    if (e.key === ' ') {
        e.preventDefault();
    }
});

// Indicador de força da senha
document.getElementById('senhaNova').addEventListener('input', (e) => {
    const senha = e.target.value;
    const requisitos = document.querySelector('.senha-requisitos p');
    
    if (senha.length === 0) {
        requisitos.textContent = '⚠️ A senha deve conter no mínimo 6 caracteres';
        requisitos.style.color = '#92400e';
    } else if (senha.length < 6) {
        requisitos.textContent = `❌ Faltam ${6 - senha.length} caracteres`;
        requisitos.style.color = '#dc2626';
    } else if (senha.length < 8) {
        requisitos.textContent = '⚠️ Senha fraca (recomendado: 8+ caracteres)';
        requisitos.style.color = '#d97706';
    } else {
        requisitos.textContent = '✅ Senha forte';
        requisitos.style.color = '#059669';
    }
});
