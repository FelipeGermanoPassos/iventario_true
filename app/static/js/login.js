// Alterna entre formulário de login e registro
function mostrarLogin() {
    document.getElementById('formLogin').classList.add('active');
    document.getElementById('formRegistro').classList.remove('active');
    limparMensagem();
}

function mostrarRegistro() {
    document.getElementById('formLogin').classList.remove('active');
    document.getElementById('formRegistro').classList.add('active');
    limparMensagem();
}

// Exibe mensagens de feedback
function mostrarMensagem(texto, tipo = 'info') {
    const mensagemDiv = document.getElementById('mensagem');
    mensagemDiv.textContent = texto;
    mensagemDiv.className = `message ${tipo} show`;
    
    // Remove a mensagem após 5 segundos
    setTimeout(() => {
        limparMensagem();
    }, 5000);
}

function limparMensagem() {
    const mensagemDiv = document.getElementById('mensagem');
    mensagemDiv.className = 'message';
    mensagemDiv.textContent = '';
}

// Manipulador do formulário de login
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const senha = document.getElementById('loginSenha').value;
    const lembrar = document.getElementById('lembrar').checked;
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, senha, lembrar })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensagem('Login realizado com sucesso! Redirecionando...', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
        } else {
            mostrarMensagem(data.message, 'error');
        }
    } catch (error) {
        mostrarMensagem('Erro ao conectar com o servidor. Tente novamente.', 'error');
        console.error('Erro:', error);
    }
});

// Manipulador do formulário de registro
document.getElementById('registroForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const nome = document.getElementById('registroNome').value;
    const email = document.getElementById('registroEmail').value;
    const departamento = document.getElementById('registroDepartamento').value;
    const telefone = document.getElementById('registroTelefone').value;
    const senha = document.getElementById('registroSenha').value;
    const confirmarSenha = document.getElementById('registroConfirmarSenha').value;
    
    // Validações
    if (senha !== confirmarSenha) {
        mostrarMensagem('As senhas não coincidem!', 'error');
        return;
    }
    
    if (senha.length < 6) {
        mostrarMensagem('A senha deve ter no mínimo 6 caracteres!', 'error');
        return;
    }
    
    try {
        const response = await fetch('/registro', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nome, email, departamento, telefone, senha })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensagem(data.message, 'success');
            // Limpa o formulário
            document.getElementById('registroForm').reset();
            // Volta para o login após 2 segundos
            setTimeout(() => {
                mostrarLogin();
            }, 2000);
        } else {
            mostrarMensagem(data.message, 'error');
        }
    } catch (error) {
        mostrarMensagem('Erro ao conectar com o servidor. Tente novamente.', 'error');
        console.error('Erro:', error);
    }
});

// Adiciona máscaras de formatação
document.getElementById('registroTelefone').addEventListener('input', (e) => {
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
document.querySelectorAll('input[type="email"]').forEach(input => {
    input.addEventListener('keypress', (e) => {
        if (e.key === ' ') {
            e.preventDefault();
        }
    });
});
