// Variável global para armazenar usuários
let todosUsuarios = [];
let todosBackups = [];
let tabAtual = 'usuarios';
let CURRENT_USER_ID; // Será inicializado no DOMContentLoaded

// Controle de tabs
function mostrarTab(nomeTab, event) {
    tabAtual = nomeTab;
    
    // Atualiza botões das tabs
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    if (event && event.target) {
        event.target.classList.add('active');
    }
    
    // Atualiza conteúdo das tabs
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    if (nomeTab === 'usuarios') {
        document.getElementById('tabUsuarios').classList.add('active');
    } else if (nomeTab === 'backups') {
        document.getElementById('tabBackups').classList.add('active');
        carregarBackups();
    } else if (nomeTab === 'email') {
        document.getElementById('tabEmail').classList.add('active');
        carregarStatusEmail();
    } else if (nomeTab === 'whatsapp') {
        document.getElementById('tabWhatsApp').classList.add('active');
        carregarStatusWhatsApp();
    }
}

// Carrega dados ao iniciar
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded - iniciando');
    
    // Inicializa o ID do usuário atual (pegando do atributo data do body)
    CURRENT_USER_ID = parseInt(document.body.dataset.currentUserId);
    
    carregarUsuarios();
    
    // Event listeners
    const btnNovoUsuario = document.getElementById('btnNovoUsuario');
    console.log('Botão Novo Usuário encontrado:', btnNovoUsuario);
    
    if (btnNovoUsuario) {
        btnNovoUsuario.addEventListener('click', abrirModalNovoUsuario);
        console.log('Event listener adicionado ao botão');
    } else {
        console.error('Botão btnNovoUsuario não encontrado!');
    }
    
    const closeBtn = document.querySelector('.close');
    if (closeBtn) {
        closeBtn.addEventListener('click', fecharModalUsuario);
    }
    
    const formUsuario = document.getElementById('formUsuario');
    if (formUsuario) {
        formUsuario.addEventListener('submit', salvarUsuario);
    }
    
    // Fecha modal ao clicar fora
    window.addEventListener('click', (e) => {
        const modal = document.getElementById('modalUsuario');
        if (modal && e.target === modal) {
            fecharModalUsuario();
        }
    });
    
    // Máscara de telefone
    const telefoneInput = document.getElementById('usuarioTelefone');
    if (telefoneInput) {
        telefoneInput.addEventListener('input', aplicarMascaraTelefone);
    }
    
    // Event listeners para backups
    const btnCriarBackup = document.getElementById('btnCriarBackup');
    if (btnCriarBackup) {
        btnCriarBackup.addEventListener('click', criarBackupManual);
    }
    
    const btnAtualizarBackups = document.getElementById('btnAtualizarBackups');
    if (btnAtualizarBackups) {
        btnAtualizarBackups.addEventListener('click', carregarBackups);
    }
    
    const btnTestarEmail = document.getElementById('btnTestarEmail');
    if (btnTestarEmail) {
        btnTestarEmail.addEventListener('click', testarEmail);
    }
    
    const btnTestarWhatsApp = document.getElementById('btnTestarWhatsApp');
    if (btnTestarWhatsApp) {
        btnTestarWhatsApp.addEventListener('click', testarWhatsApp);
    }
    
    // Configurar busca de usuários
    configurarBuscaUsuarios();
    
    console.log('DOMContentLoaded - concluído');
});

// Exibe mensagens de feedback
function mostrarMensagem(texto, tipo = 'info') {
    const mensagemDiv = document.getElementById('mensagem');
    mensagemDiv.textContent = texto;
    mensagemDiv.className = `message-admin ${tipo} show`;
    
    setTimeout(() => {
        limparMensagem();
    }, 5000);
}

function limparMensagem() {
    const mensagemDiv = document.getElementById('mensagem');
    mensagemDiv.className = 'message-admin';
    mensagemDiv.textContent = '';
}

// Carrega lista de usuários
async function carregarUsuarios() {
    try {
        console.log('Iniciando carregamento de usuários...');
        const response = await fetch('/admin/usuarios');
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Erro HTTP:', response.status, errorText);
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        const usuarios = await response.json();
        console.log('Usuários carregados:', usuarios.length);
        
        todosUsuarios = usuarios;
        atualizarEstatisticas(usuarios);
        renderizarUsuarios(usuarios);
        
    } catch (error) {
        mostrarMensagem('Erro ao carregar usuários: ' + error.message, 'error');
        console.error('Erro detalhado:', error);
    }
}

// Atualiza estatísticas
function atualizarEstatisticas(usuarios) {
    const totalUsuarios = usuarios.length;
    const usuariosAtivos = usuarios.filter(u => u.ativo).length;
    const administradores = usuarios.filter(u => u.is_admin).length;
    const usuariosInativos = usuarios.filter(u => !u.ativo).length;
    
    document.getElementById('totalUsuarios').textContent = totalUsuarios;
    document.getElementById('usuariosAtivos').textContent = usuariosAtivos;
    document.getElementById('administradores').textContent = administradores;
    document.getElementById('usuariosInativos').textContent = usuariosInativos;
}

// Renderiza tabela de usuários
function renderizarUsuarios(usuarios) {
    const tbody = document.getElementById('usuariosTableBody');
    tbody.innerHTML = '';
    
    if (usuarios.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 30px;">Nenhum usuário encontrado</td></tr>';
        return;
    }
    
    usuarios.forEach(usuario => {
        const tr = document.createElement('tr');
        
        // Destaca usuário atual (verifica se CURRENT_USER_ID foi inicializado)
        if (CURRENT_USER_ID && usuario.id === CURRENT_USER_ID) {
            tr.classList.add('usuario-atual');
        }
        
        const statusClass = usuario.ativo ? 'status-ativo' : 'status-inativo';
        const statusText = usuario.ativo ? 'Ativo' : 'Inativo';
        
        const tipoClass = usuario.is_admin ? 'tipo-admin' : 'tipo-usuario';
        const tipoText = usuario.is_admin ? '⭐ Admin' : '👤 Usuário';
        
        const dataCadastro = new Date(usuario.data_cadastro).toLocaleDateString('pt-BR');
        const ultimoAcesso = usuario.ultimo_acesso ? 
            new Date(usuario.ultimo_acesso).toLocaleDateString('pt-BR') : 
            'Nunca';
        
        tr.innerHTML = `
            <td><strong>${usuario.nome}</strong></td>
            <td>${usuario.email}</td>
            <td>${usuario.departamento || '-'}</td>
            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            <td><span class="tipo-badge ${tipoClass}">${tipoText}</span></td>
            <td class="data-text">${dataCadastro}</td>
            <td class="data-text">${ultimoAcesso}</td>
            <td>
                <div class="acoes-cell">
                    ${CURRENT_USER_ID && usuario.id !== CURRENT_USER_ID ? `
                        <button class="btn btn-sm btn-toggle-ativo" onclick="toggleAtivo(${usuario.id})" title="${usuario.ativo ? 'Desativar' : 'Ativar'}">
                            ${usuario.ativo ? '🚫' : '✅'}
                        </button>
                        <button class="btn btn-sm btn-toggle-admin" onclick="toggleAdmin(${usuario.id})" title="${usuario.is_admin ? 'Remover Admin' : 'Tornar Admin'}">
                            ${usuario.is_admin ? '👤' : '⭐'}
                        </button>
                        <button class="btn btn-sm btn-primary" onclick="editarUsuario(${usuario.id})" title="Editar">
                            ✏️
                        </button>
                        <button class="btn btn-sm btn-delete" onclick="deletarUsuario(${usuario.id}, '${usuario.nome}')" title="Deletar">
                            🗑️
                        </button>
                    ` : CURRENT_USER_ID && usuario.id === CURRENT_USER_ID ? '<span style="color: #64748b;">Você</span>' : `
                        <button class="btn btn-sm btn-primary" onclick="editarUsuario(${usuario.id})" title="Editar">
                            ✏️
                        </button>
                    `}
                </div>
            </td>
        `;
        
        tbody.appendChild(tr);
    });
}

// Busca de usuários
function configurarBuscaUsuarios() {
    const searchInput = document.getElementById('searchUsuario');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const termo = e.target.value.toLowerCase();
            
            if (!termo) {
                renderizarUsuarios(todosUsuarios);
                return;
            }
            
            const usuariosFiltrados = todosUsuarios.filter(usuario => 
                usuario.nome.toLowerCase().includes(termo) ||
                usuario.email.toLowerCase().includes(termo) ||
                (usuario.departamento && usuario.departamento.toLowerCase().includes(termo))
            );
            
            renderizarUsuarios(usuariosFiltrados);
        });
    }
}

// Toggle ativo/inativo
async function toggleAtivo(id) {
    if (!confirm('Deseja alterar o status deste usuário?')) {
        return;
    }
    
    try {
        const response = await fetch(`/admin/usuario/${id}/toggle-ativo`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensagem(data.message, 'success');
            await carregarUsuarios();
        } else {
            mostrarMensagem(data.message, 'error');
        }
    } catch (error) {
        mostrarMensagem('Erro ao alterar status do usuário.', 'error');
        console.error('Erro:', error);
    }
}

// Toggle admin
async function toggleAdmin(id) {
    if (!confirm('Deseja alterar os privilégios deste usuário?')) {
        return;
    }
    
    try {
        const response = await fetch(`/admin/usuario/${id}/toggle-admin`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensagem(data.message, 'success');
            await carregarUsuarios();
        } else {
            mostrarMensagem(data.message, 'error');
        }
    } catch (error) {
        mostrarMensagem('Erro ao alterar privilégios do usuário.', 'error');
        console.error('Erro:', error);
    }
}

// Deletar usuário
async function deletarUsuario(id, nome) {
    if (!confirm(`Tem certeza que deseja DELETAR o usuário "${nome}"?\n\nEsta ação não pode ser desfeita!`)) {
        return;
    }
    
    try {
        const response = await fetch(`/admin/usuario/${id}/deletar`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensagem(data.message, 'success');
            await carregarUsuarios();
        } else {
            mostrarMensagem(data.message, 'error');
        }
    } catch (error) {
        mostrarMensagem('Erro ao deletar usuário.', 'error');
        console.error('Erro:', error);
    }
}

// Abre modal para novo usuário
function abrirModalNovoUsuario() {
    console.log('Função abrirModalNovoUsuario chamada');
    
    const modal = document.getElementById('modalUsuario');
    console.log('Modal encontrado:', modal);
    
    document.getElementById('modalTitulo').textContent = 'Novo Usuário';
    document.getElementById('usuarioId').value = '';
    document.getElementById('formUsuario').reset();
    document.getElementById('usuarioAtivo').checked = true;
    
    // Senha obrigatória para novo usuário
    document.getElementById('usuarioSenha').required = true;
    document.getElementById('usuarioConfirmarSenha').required = true;
    document.getElementById('senhaRequired').textContent = '*';
    document.getElementById('confirmarRequired').textContent = '*';
    
    console.log('Adicionando classe show ao modal');
    modal.classList.add('show');
    console.log('Classes do modal:', modal.className);
}

// Abre modal para editar usuário
async function editarUsuario(id) {
    try {
        // Busca dados do usuário
        const usuario = todosUsuarios.find(u => u.id === id);
        if (!usuario) {
            mostrarMensagem('Usuário não encontrado.', 'error');
            return;
        }
        
        document.getElementById('modalTitulo').textContent = 'Editar Usuário';
        document.getElementById('usuarioId').value = usuario.id;
        document.getElementById('usuarioNome').value = usuario.nome;
        document.getElementById('usuarioEmail').value = usuario.email;
        document.getElementById('usuarioDepartamento').value = usuario.departamento || '';
        document.getElementById('usuarioTelefone').value = usuario.telefone || '';
        document.getElementById('usuarioAdmin').checked = usuario.is_admin;
        document.getElementById('usuarioAtivo').checked = usuario.ativo;
        
        // Senha opcional para edição
        document.getElementById('usuarioSenha').required = false;
        document.getElementById('usuarioConfirmarSenha').required = false;
        document.getElementById('usuarioSenha').value = '';
        document.getElementById('usuarioConfirmarSenha').value = '';
        document.getElementById('senhaRequired').textContent = '';
        document.getElementById('confirmarRequired').textContent = '';
        
        document.getElementById('modalUsuario').classList.add('show');
    } catch (error) {
        mostrarMensagem('Erro ao carregar dados do usuário.', 'error');
        console.error('Erro:', error);
    }
}

// Fecha modal
function fecharModalUsuario() {
    document.getElementById('modalUsuario').classList.remove('show');
    document.getElementById('formUsuario').reset();
}

// Salva usuário (criar ou editar)
async function salvarUsuario(e) {
    e.preventDefault();
    
    const id = document.getElementById('usuarioId').value;
    const nome = document.getElementById('usuarioNome').value;
    const email = document.getElementById('usuarioEmail').value;
    const departamento = document.getElementById('usuarioDepartamento').value;
    const telefone = document.getElementById('usuarioTelefone').value;
    const senha = document.getElementById('usuarioSenha').value;
    const confirmarSenha = document.getElementById('usuarioConfirmarSenha').value;
    const isAdmin = document.getElementById('usuarioAdmin').checked;
    const ativo = document.getElementById('usuarioAtivo').checked;
    
    // Validações
    if (!id && !senha) {
        mostrarMensagem('Senha é obrigatória para novo usuário.', 'error');
        return;
    }
    
    if (senha && senha !== confirmarSenha) {
        mostrarMensagem('As senhas não coincidem!', 'error');
        return;
    }
    
    if (senha && senha.length < 6) {
        mostrarMensagem('A senha deve ter no mínimo 6 caracteres!', 'error');
        return;
    }
    
    const dados = {
        nome,
        email,
        departamento,
        telefone,
        is_admin: isAdmin,
        ativo
    };
    
    // Adiciona senha apenas se foi preenchida
    if (senha) {
        dados.senha = senha;
    }
    
    try {
        const url = id ? `/admin/usuario/${id}/editar` : '/admin/usuario/adicionar';
        const method = id ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dados)
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensagem(data.message, 'success');
            fecharModalUsuario();
            await carregarUsuarios();
        } else {
            mostrarMensagem(data.message, 'error');
        }
    } catch (error) {
        mostrarMensagem('Erro ao salvar usuário.', 'error');
        console.error('Erro:', error);
    }
}

// Máscara de telefone
function aplicarMascaraTelefone(e) {
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
}

// ===== FUNÇÕES DE BACKUP =====

async function carregarBackups() {
    try {
        const response = await fetch('/admin/backup/listar');
        const data = await response.json();
        
        if (data.success) {
            todosBackups = data.backups;
            renderizarBackups(todosBackups);
        } else {
            mostrarMensagem(data.message || 'Erro ao carregar backups', 'error');
        }
    } catch (error) {
        console.error('Erro ao carregar backups:', error);
        mostrarMensagem('Erro ao carregar backups', 'error');
    }
}

function renderizarBackups(backups) {
    const tbody = document.getElementById('backupsTableBody');
    
    if (backups.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px;">Nenhum backup encontrado</td></tr>';
        return;
    }
    
    tbody.innerHTML = backups.map(backup => `
        <tr>
            <td><code>${backup.nome}</code></td>
            <td><span class="badge ${backup.tipo === 'Manual' ? 'badge-primary' : 'badge-secondary'}">${backup.tipo}</span></td>
            <td>${backup.tamanho}</td>
            <td>${backup.data}</td>
            <td>
                <div class="action-buttons">
                    <button onclick="baixarBackup('${backup.nome}')" class="btn btn-sm" title="Baixar">
                        📥 Baixar
                    </button>
                    <button onclick="deletarBackup('${backup.nome}')" class="btn btn-sm btn-danger" title="Deletar">
                        🗑️ Deletar
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

async function criarBackupManual() {
    if (!confirm('Deseja criar um backup manual do banco de dados?')) return;
    
    try {
        const btn = document.getElementById('btnCriarBackup');
        btn.disabled = true;
        btn.textContent = '⏳ Criando...';
        
        const response = await fetch('/admin/backup/criar', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            mostrarMensagem('Backup criado com sucesso!', 'success');
            carregarBackups(); // Recarrega a lista
        } else {
            mostrarMensagem(data.message || 'Erro ao criar backup', 'error');
        }
    } catch (error) {
        console.error('Erro ao criar backup:', error);
        mostrarMensagem('Erro ao criar backup', 'error');
    } finally {
        const btn = document.getElementById('btnCriarBackup');
        btn.disabled = false;
        btn.textContent = '📦 Criar Backup Manual';
    }
}

function baixarBackup(nome) {
    window.location.href = `/admin/backup/baixar/${nome}`;
    mostrarMensagem('Download iniciado', 'success');
}

async function deletarBackup(nome) {
    if (!confirm(`Deseja realmente deletar o backup:\n${nome}?`)) return;
    
    try {
        const response = await fetch(`/admin/backup/deletar/${nome}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        
        if (data.success) {
            mostrarMensagem('Backup deletado com sucesso!', 'success');
            carregarBackups(); // Recarrega a lista
        } else {
            mostrarMensagem(data.message || 'Erro ao deletar backup', 'error');
        }
    } catch (error) {
        console.error('Erro ao deletar backup:', error);
        mostrarMensagem('Erro ao deletar backup', 'error');
    }
}

// ====== FUNÇÕES DE E-MAIL ======

async function carregarStatusEmail() {
    try {
        const response = await fetch('/admin/email-status');
        const data = await response.json();
        
        const statusText = document.getElementById('emailStatusText');
        const server = document.getElementById('emailServer');
        const port = document.getElementById('emailPort');
        const sender = document.getElementById('emailSender');
        
        if (data.enabled) {
            statusText.textContent = '✅ Habilitado';
            statusText.className = 'enabled';
            server.textContent = data.server || '-';
            port.textContent = data.port || '-';
            sender.textContent = data.sender || '-';
        } else {
            statusText.textContent = '❌ Desabilitado';
            statusText.className = 'disabled';
            server.textContent = '-';
            port.textContent = '-';
            sender.textContent = '-';
        }
    } catch (error) {
        console.error('Erro ao carregar status de e-mail:', error);
        document.getElementById('emailStatusText').textContent = '❓ Erro ao verificar';
    }
}

async function testarEmail() {
    const emailInput = document.getElementById('emailTeste');
    const email = emailInput.value.trim();
    
    if (!email) {
        mostrarMensagem('Por favor, informe um e-mail de destino', 'error');
        return;
    }
    
    // Validação básica de e-mail
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        mostrarMensagem('Por favor, informe um e-mail válido', 'error');
        return;
    }
    
    const btn = document.getElementById('btnTestarEmail');
    btn.disabled = true;
    btn.textContent = '📧 Enviando...';
    
    try {
        const response = await fetch('/admin/testar-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarMensagem(data.message, 'success');
            emailInput.value = ''; // Limpa o campo
        } else {
            mostrarMensagem(data.message || 'Erro ao enviar e-mail de teste', 'error');
        }
    } catch (error) {
        console.error('Erro ao testar e-mail:', error);
        mostrarMensagem('Erro ao testar e-mail. Verifique as configurações.', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = '📧 Enviar E-mail de Teste';
    }
}

// ===== WHATSAPP =====
async function carregarStatusWhatsApp() {
    try {
        const response = await fetch('/admin/whatsapp/status');
        const data = await response.json();
        
        const statusText = document.getElementById('whatsappStatusText');
        const provider = document.getElementById('whatsappProvider');
        const configured = document.getElementById('whatsappConfigured');
        
        if (data.enabled) {
            statusText.textContent = '✅ Habilitado';
            statusText.style.color = '#10b981';
        } else {
            statusText.textContent = '❌ Desabilitado';
            statusText.style.color = '#ef4444';
        }
        
        provider.textContent = data.provider || 'Não configurado';
        
        if (data.configured) {
            configured.textContent = '✅ Sim';
            configured.style.color = '#10b981';
        } else {
            configured.textContent = '❌ Não';
            configured.style.color = '#ef4444';
        }
        
    } catch (error) {
        console.error('Erro ao carregar status do WhatsApp:', error);
        document.getElementById('whatsappStatusText').textContent = 'Erro ao verificar';
    }
}

async function testarWhatsApp() {
    const btn = document.getElementById('btnTestarWhatsApp');
    const telefone = document.getElementById('whatsappTelefone').value.trim();
    
    if (!telefone) {
        mostrarMensagem('Por favor, digite um número de telefone.', 'error');
        return;
    }
    
    btn.disabled = true;
    btn.textContent = '📤 Enviando...';
    
    try {
        const response = await fetch('/whatsapp/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ phone: telefone })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            mostrarMensagem('✅ Mensagem de teste enviada com sucesso!', 'success');
        } else {
            mostrarMensagem(`❌ ${data.message || 'Erro ao enviar mensagem'}`, 'error');
        }
    } catch (error) {
        console.error('Erro ao testar WhatsApp:', error);
        mostrarMensagem('Erro ao testar WhatsApp. Verifique as configurações.', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = '💬 Enviar Mensagem de Teste';
    }
}
