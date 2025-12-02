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

// ===== PUSH NOTIFICATIONS =====

async function verificarStatusPush() {
    const statusText = document.getElementById('pushStatusText');
    const btnAtivar = document.getElementById('btnAtivarPush');
    const btnDesativar = document.getElementById('btnDesativarPush');
    const btnTestar = document.getElementById('btnTestarPush');
    
    // Verifica se o navegador suporta
    if (!('Notification' in window) || !('PushManager' in window)) {
        statusText.textContent = '❌ Seu navegador não suporta notificações push';
        statusText.style.color = '#dc2626';
        return;
    }
    
    // Verifica a permissão
    const permission = Notification.permission;
    
    if (permission === 'denied') {
        statusText.textContent = '🚫 Notificações bloqueadas. Altere nas configurações do navegador.';
        statusText.style.color = '#dc2626';
        return;
    }
    
    // Verifica se está subscrito
    const isSubscribed = await window.PushNotifications.isSubscribed();
    
    if (isSubscribed) {
        statusText.textContent = '✅ Notificações ativadas';
        statusText.style.color = '#059669';
        btnDesativar.style.display = 'inline-block';
        btnTestar.style.display = 'inline-block';
    } else {
        statusText.textContent = '🔕 Notificações desativadas';
        statusText.style.color = '#92400e';
        btnAtivar.style.display = 'inline-block';
    }
}

async function ativarNotificacoes() {
    const btnAtivar = document.getElementById('btnAtivarPush');
    btnAtivar.disabled = true;
    btnAtivar.textContent = '⏳ Ativando...';
    
    try {
        await window.PushNotifications.initialize();
        mostrarMensagem('✅ Notificações ativadas com sucesso!', 'success');
        await verificarStatusPush();
    } catch (error) {
        console.error('Erro ao ativar notificações:', error);
        mostrarMensagem('❌ Erro ao ativar notificações. Tente novamente.', 'error');
    } finally {
        btnAtivar.disabled = false;
        btnAtivar.textContent = '🔔 Ativar Notificações';
    }
}

async function desativarNotificacoes() {
    const btnDesativar = document.getElementById('btnDesativarPush');
    btnDesativar.disabled = true;
    btnDesativar.textContent = '⏳ Desativando...';
    
    try {
        await window.PushNotifications.unsubscribe();
        mostrarMensagem('🔕 Notificações desativadas', 'info');
        await verificarStatusPush();
    } catch (error) {
        console.error('Erro ao desativar notificações:', error);
        mostrarMensagem('❌ Erro ao desativar notificações', 'error');
    } finally {
        btnDesativar.disabled = false;
        btnDesativar.textContent = '🔕 Desativar Notificações';
    }
}

async function testarNotificacao() {
    const btnTestar = document.getElementById('btnTestarPush');
    btnTestar.disabled = true;
    btnTestar.textContent = '⏳ Enviando...';
    
    try {
        const response = await fetch('/push/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensagem('📨 Notificação de teste enviada!', 'success');
        } else {
            mostrarMensagem(`❌ ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('Erro ao enviar notificação de teste:', error);
        mostrarMensagem('❌ Erro ao enviar notificação de teste', 'error');
    } finally {
        btnTestar.disabled = false;
        btnTestar.textContent = '📨 Enviar Notificação de Teste';
    }
}

// Event listeners para botões de push
document.getElementById('btnAtivarPush').addEventListener('click', ativarNotificacoes);
document.getElementById('btnDesativarPush').addEventListener('click', desativarNotificacoes);
document.getElementById('btnTestarPush').addEventListener('click', testarNotificacao);

// Verifica status ao carregar
if (window.PushNotifications) {
    verificarStatusPush();
} else {
    // Aguarda o carregamento do pwa.js
    window.addEventListener('load', () => {
        setTimeout(verificarStatusPush, 500);
    });
}
