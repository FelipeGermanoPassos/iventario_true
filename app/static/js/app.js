// Variáveis globais
let equipamentos = [];
let emprestimos = [];
let equipamentosEstoque = [];
let editandoId = null;
let charts = {};
let categoriaAtual = null;
let manutencaoEquipamentoId = null;
let manutencaoEditandoId = null;
let manutencoesCache = [];

// Categorias e seus tipos
const tiposPorCategoria = {
    computador: ['Desktop', 'All-in-One', 'Workstation', 'Servidor', 'Mini PC'],
    notebook: ['Notebook', 'Ultrabook', 'Chromebook', '2 em 1'],
    periferico: ['Monitor', 'Impressora', 'Scanner', 'Teclado', 'Mouse', 'Webcam', 'Headset', 'Switch', 'Roteador', 'Nobreak']
};

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    carregarDashboard();
    carregarEquipamentos();
    carregarEmprestimos();
    configurarEventos();
});

// Configurar eventos
function configurarEventos() {
    const modal = document.getElementById('modalEquipamento');
    const modalCategoria = document.getElementById('modalCategoria');
    const modalEmprestimo = document.getElementById('modalEmprestimo');
    const modalManutencao = document.getElementById('modalManutencao');
    
    const btnNovo = document.getElementById('btnNovoEquipamento');
    const btnNovoEmprestimo = document.getElementById('btnNovoEmprestimo');
    const btnCancelar = document.getElementById('btnCancelar');
    
    const closeEquipamento = document.querySelector('.close-equipamento');
    const closeCategoria = document.querySelector('.close-categoria');
    const closeEmprestimo = document.querySelector('.close-emprestimo');
    const closeManutencao = document.querySelector('.close-manutencao');
    
    const form = document.getElementById('formEquipamento');
    const formEmprestimo = document.getElementById('formEmprestimo');
    const formManutencao = document.getElementById('formManutencao');
    const searchInput = document.getElementById('searchInput');
    const searchEmprestimoInput = document.getElementById('searchEmprestimoInput');
    const fotoInput = document.getElementById('foto');
    const fotoPreview = document.getElementById('fotoPreview');

    // Botões de ação
    btnNovo.onclick = () => abrirModalCategoria();
    btnNovoEmprestimo.onclick = () => abrirModalEmprestimo();
    btnCancelar.onclick = () => fecharModal();
    
    // Botões X de fechar
    if (closeEquipamento) closeEquipamento.onclick = () => fecharModal();
    if (closeCategoria) closeCategoria.onclick = () => fecharModalCategoria();
    if (closeEmprestimo) closeEmprestimo.onclick = () => fecharModalEmprestimo();
    if (closeManutencao) closeManutencao.onclick = () => fecharModalManutencao();
    
    // Clique fora do modal
    window.onclick = (event) => {
        if (event.target === modal) {
            fecharModal();
        }
        if (event.target === modalCategoria) {
            fecharModalCategoria();
        }
        if (event.target === modalEmprestimo) {
            fecharModalEmprestimo();
        }
        if (event.target === modalManutencao) {
            fecharModalManutencao();
        }
    };

    // Formulários
    form.onsubmit = (e) => {
        e.preventDefault();
        salvarEquipamento();
    };
    
    formEmprestimo.onsubmit = (e) => {
        e.preventDefault();
        salvarEmprestimo();
    };
    if (formManutencao) {
        formManutencao.onsubmit = (e) => {
            e.preventDefault();
            salvarManutencao();
        };
        const btnCancelarManutencao = document.getElementById('btnCancelarManutencao');
        if (btnCancelarManutencao) btnCancelarManutencao.onclick = () => fecharModalManutencao();
    }

    // Buscas
    searchInput.oninput = (e) => filtrarEquipamentos(e.target.value);
    if (searchEmprestimoInput) {
        searchEmprestimoInput.oninput = (e) => filtrarEmprestimos(e.target.value);
    }

    // Preview da foto
    if (fotoInput) {
        fotoInput.onchange = () => {
            const file = fotoInput.files && fotoInput.files[0];
            if (!file) {
                if (fotoPreview) { fotoPreview.style.display = 'none'; fotoPreview.src = ''; }
                return;
            }
            const url = URL.createObjectURL(file);
            if (fotoPreview) {
                fotoPreview.src = url;
                fotoPreview.style.display = 'inline-block';
            }
        };
    }
}

// Tabs
function mostrarTab(tab) {
    console.log('Mudando para tab:', tab);
    
    // Ocultar todas as tabs
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
    
    // Mostrar tab selecionada
    if (tab === 'estoque') {
        const tabEstoque = document.getElementById('tabEstoque');
        if (tabEstoque) tabEstoque.classList.add('active');
        document.querySelectorAll('.tab-button')[0].classList.add('active');
    } else if (tab === 'emprestimos') {
        const tabEmprestimos = document.getElementById('tabEmprestimos');
        if (tabEmprestimos) tabEmprestimos.classList.add('active');
        document.querySelectorAll('.tab-button')[1].classList.add('active');
        carregarEmprestimos();
    }
}

// Dashboard
async function carregarDashboard() {
    try {
        const response = await fetch('/dashboard-data');
        const data = await response.json();

        // Atualizar estatísticas básicas
        document.getElementById('totalEquipamentos').textContent = data.total_equipamentos;
        document.getElementById('equipamentosEstoque').textContent = data.equipamentos_estoque;
        document.getElementById('equipamentosEmprestados').textContent = data.equipamentos_emprestados;
        
        // Novas métricas
        document.getElementById('equipamentosManutencao').textContent = data.equipamentos_manutencao || 0;
        document.getElementById('taxaUtilizacao').textContent = `${data.taxa_utilizacao || 0}%`;
        document.getElementById('emprestimosRecentes').textContent = data.emprestimos_recentes || 0;
        document.getElementById('manutencoesPendentes').textContent = data.manutencoes_pendentes || 0;
        
        // Valores monetários
        document.getElementById('valorTotal').textContent = 
            `R$ ${data.valor_total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
        document.getElementById('valorMedio').textContent = 
            `R$ ${data.valor_medio.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
        document.getElementById('custoManutencoes').textContent = 
            `R$ ${data.custo_manutencoes.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;

        // Criar gráficos
        criarGraficos(data);
        
        // Carregar notificações
        await carregarNotificacoes();
    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
        mostrarAlerta('Erro ao carregar dashboard', 'error');
    }
}

async function carregarNotificacoes() {
    try {
        const res = await fetch('/emprestimos/notificacoes?dias=3');
        const data = await res.json();
        if (data.success) {
            const total = data.total_notificacoes || 0;
            const badge = document.getElementById('totalNotificacoes');
            if (badge) badge.textContent = total;
            const card = document.getElementById('statNotificacoes');
            if (card) {
                card.style.background = total > 0 ? '#fef3c7' : '';
                card.style.borderLeft = total > 0 ? '4px solid #f59e0b' : '';
            }
            // Armazenar para mostrar detalhes
            window.notificacoesData = data;
        }
    } catch (e) {
        console.error('Erro ao carregar notificações:', e);
    }
}

function mostrarNotificacoes() {
    const data = window.notificacoesData;
    if (!data || data.total_notificacoes === 0) {
        mostrarAlerta('Nenhuma devolução pendente no momento! 🎉', 'success');
        return;
    }
    let msg = '<div style="text-align:left;max-height:400px;overflow-y:auto;">';
    if (data.atrasados && data.atrasados.length > 0) {
        msg += '<h3 style="color:#dc2626;">⚠️ Empréstimos Atrasados (' + data.atrasados.length + ')</h3><ul>';
        data.atrasados.forEach(e => {
            if (!e.data_devolucao_prevista) return; // Skip if no date
            const dias = Math.floor((new Date() - new Date(e.data_devolucao_prevista)) / 86400000);
            const dataFormatada = new Date(e.data_devolucao_prevista).toLocaleDateString('pt-BR');
            msg += `<li><b>${e.equipamento_nome || 'Equipamento'}</b> - ${e.responsavel}<br>Venceu há ${dias} dia(s) (${dataFormatada})</li>`;
        });
        msg += '</ul>';
    }
    if (data.proximos_vencimento && data.proximos_vencimento.length > 0) {
        msg += '<h3 style="color:#f59e0b;">🔔 Devoluções Próximas (' + data.proximos_vencimento.length + ')</h3><ul>';
        data.proximos_vencimento.forEach(e => {
            if (!e.data_devolucao_prevista) return; // Skip if no date
            const dias = Math.ceil((new Date(e.data_devolucao_prevista) - new Date()) / 86400000);
            const dataFormatada = new Date(e.data_devolucao_prevista).toLocaleDateString('pt-BR');
            msg += `<li><b>${e.equipamento_nome || 'Equipamento'}</b> - ${e.responsavel}<br>Vence em ${dias} dia(s) (${dataFormatada})</li>`;
        });
        msg += '</ul>';
    }
    msg += '</div>';
    // Criar modal temporário
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.display = 'block';
    modal.innerHTML = `<div class="modal-content" style="max-width:600px;"><span class="close" onclick="this.parentElement.parentElement.remove()">&times;</span><h2>🔔 Notificações de Devolução</h2>${msg}<div style="text-align:center;margin-top:20px;"><button class="btn btn-primary" onclick="this.closest('.modal').remove();mostrarTab('emprestimos');">Ver Empréstimos</button></div></div>`;
    document.body.appendChild(modal);
    modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
}

function criarGraficos(data) {
    // Gráfico de Status
    const statusCtx = document.getElementById('statusChart').getContext('2d');
    if (charts.status) charts.status.destroy();
    charts.status = new Chart(statusCtx, {
        type: 'doughnut',
        data: {
            labels: data.status.map(s => s.name),
            datasets: [{
                data: data.status.map(s => s.value),
                backgroundColor: ['#10b981', '#EF7D2D', '#ef4444', '#f59e0b'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });

    // Gráfico de Tipos
    const tipoCtx = document.getElementById('tipoChart').getContext('2d');
    if (charts.tipo) charts.tipo.destroy();
    charts.tipo = new Chart(tipoCtx, {
        type: 'bar',
        data: {
            labels: data.tipos.map(t => t.name),
            datasets: [{
                label: 'Quantidade',
                data: data.tipos.map(t => t.value),
                backgroundColor: '#EF7D2D',
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });

    // Gráfico de Empréstimos por Departamento
    const deptCtx = document.getElementById('departamentoChart').getContext('2d');
    if (charts.departamento) charts.departamento.destroy();
    charts.departamento = new Chart(deptCtx, {
        type: 'bar',
        data: {
            labels: data.emprestimos_por_departamento.map(d => d.name),
            datasets: [{
                label: 'Empréstimos Ativos',
                data: data.emprestimos_por_departamento.map(d => d.value),
                backgroundColor: '#10b981',
                borderRadius: 8
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });

    // Gráfico de Equipamentos Mais Populares
    const popularCtx = document.getElementById('popularesChart').getContext('2d');
    if (charts.populares) charts.populares.destroy();
    charts.populares = new Chart(popularCtx, {
        type: 'bar',
        data: {
            labels: data.equipamentos_populares.map(e => e.nome),
            datasets: [{
                label: 'Total de Empréstimos',
                data: data.equipamentos_populares.map(e => e.emprestimos),
                backgroundColor: '#f59e0b',
                borderRadius: 8
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });

    // Remover gráfico de localizações (não usado mais)
    if (charts.localizacao) {
        charts.localizacao.destroy();
        charts.localizacao = null;
    }
}

// Equipamentos
async function carregarEquipamentos() {
    try {
        const response = await fetch('/equipamentos');
        equipamentos = await response.json();
        renderizarEquipamentos(equipamentos);
    } catch (error) {
        console.error('Erro ao carregar equipamentos:', error);
        mostrarAlerta('Erro ao carregar equipamentos', 'error');
    }
}

function renderizarEquipamentos(lista) {
    const tbody = document.getElementById('equipamentosBody');
    
    if (lista.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Nenhum equipamento cadastrado</td></tr>';
        return;
    }

    tbody.innerHTML = lista.map(eq => `
        <tr>
            <td>${eq.nome}</td>
            <td>${eq.tipo}</td>
            <td>${eq.marca}</td>
            <td>${eq.modelo}</td>
            <td>${eq.numero_serie}</td>
            <td><span class="status-badge status-${eq.status.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')}">${eq.status}</span></td>
            <td>
                <div class="action-buttons">
                    <button class="btn" onclick="abrirModalManutencao(${eq.id})">🛠️ Manutenção</button>
                    <button class="btn" onclick="mostrarQRCode(${eq.id})">📱 QR Code</button>
                    <button class="btn btn-edit" onclick="editarEquipamento(${eq.id})">✏️ Editar</button>
                    <button class="btn btn-danger" onclick="deletarEquipamento(${eq.id})">🗑️ Deletar</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function filtrarEquipamentos(termo) {
    const termoLower = termo.toLowerCase();
    const filtrados = equipamentos.filter(eq => 
        eq.nome.toLowerCase().includes(termoLower) ||
        eq.tipo.toLowerCase().includes(termoLower) ||
        eq.marca.toLowerCase().includes(termoLower) ||
        eq.modelo.toLowerCase().includes(termoLower) ||
        eq.numero_serie.toLowerCase().includes(termoLower) ||
        eq.status.toLowerCase().includes(termoLower)
    );
    renderizarEquipamentos(filtrados);
}

// Modal de Categoria
function abrirModalCategoria() {
    const modalCategoria = document.getElementById('modalCategoria');
    modalCategoria.style.display = 'block';
}

function fecharModalCategoria() {
    const modalCategoria = document.getElementById('modalCategoria');
    modalCategoria.style.display = 'none';
}

function selecionarCategoria(categoria) {
    categoriaAtual = categoria;
    fecharModalCategoria();
    abrirModal(null, categoria);
}

// Modal
function abrirModal(equipamento = null, categoria = null) {
    const modal = document.getElementById('modalEquipamento');
    const title = document.getElementById('modalTitle');
    const form = document.getElementById('formEquipamento');

    if (equipamento) {
        title.textContent = 'Editar Equipamento';
        editandoId = equipamento.id;
        // Detectar categoria baseada no tipo do equipamento
        for (let cat in tiposPorCategoria) {
            if (tiposPorCategoria[cat].includes(equipamento.tipo)) {
                categoriaAtual = cat;
                break;
            }
        }
        // Primeiro configura os campos e depois preenche
        configurarCamposPorCategoria(categoriaAtual);
        preencherFormulario(equipamento);
    } else {
        title.textContent = 'Adicionar Equipamento';
        editandoId = null;
        form.reset();
        categoriaAtual = categoria;
        configurarCamposPorCategoria(categoria);
    }

    modal.style.display = 'block';
}

function configurarCamposPorCategoria(categoria) {
    // Ocultar todos os campos específicos
    document.querySelectorAll('.campo-computador, .campo-notebook, .campo-periferico').forEach(el => {
        el.style.display = 'none';
        const input = el.querySelector('input, select, textarea');
        if (input) input.removeAttribute('required');
    });
    
    // Mostrar campos específicos da categoria
    if (categoria === 'computador' || categoria === 'notebook') {
        document.querySelectorAll(`.campo-${categoria}`).forEach(el => {
            el.style.display = 'block';
        });
        
        // Tornar RAM e Armazenamento obrigatórios para computadores e notebooks
        const ramInput = document.getElementById('memoria_ram');
        const armazenamentoInput = document.getElementById('armazenamento');
        if (ramInput) ramInput.setAttribute('required', 'required');
        if (armazenamentoInput) armazenamentoInput.setAttribute('required', 'required');
    } else if (categoria === 'periferico') {
        document.querySelectorAll('.campo-periferico').forEach(el => {
            el.style.display = 'block';
        });
    }
    
    // Preencher opções de tipo baseado na categoria
    const tipoSelect = document.getElementById('tipo');
    tipoSelect.innerHTML = '<option value="">Selecione...</option>';
    
    if (categoria && tiposPorCategoria[categoria]) {
        tiposPorCategoria[categoria].forEach(tipo => {
            const option = document.createElement('option');
            option.value = tipo;
            option.textContent = tipo;
            tipoSelect.appendChild(option);
        });
    }
}

function fecharModal() {
    const modal = document.getElementById('modalEquipamento');
    modal.style.display = 'none';
    editandoId = null;
    categoriaAtual = null;
    document.getElementById('formEquipamento').reset();
    const fotoPreview = document.getElementById('fotoPreview');
    const fotoInput = document.getElementById('foto');
    if (fotoPreview) { fotoPreview.style.display = 'none'; fotoPreview.src = ''; }
    if (fotoInput) { fotoInput.value = ''; }
    
    // Limpar campos específicos
    document.querySelectorAll('.campo-computador, .campo-notebook, .campo-periferico').forEach(el => {
        el.style.display = 'none';
    });
    
    // Resetar opções do status para o padrão
    const statusSelect = document.getElementById('status');
    statusSelect.innerHTML = `
        <option value="Estoque">Estoque</option>
        <option value="Manutenção">Manutenção</option>
        <option value="Inativo">Inativo</option>
    `;
}

function preencherFormulario(equipamento) {
    document.getElementById('nome').value = equipamento.nome;
    document.getElementById('tipo').value = equipamento.tipo;
    document.getElementById('marca').value = equipamento.marca;
    document.getElementById('modelo').value = equipamento.modelo;
    document.getElementById('numero_serie').value = equipamento.numero_serie;
    
    // Preencher status - adicionar opção se não existir (como "Emprestado")
    const statusSelect = document.getElementById('status');
    const statusValue = equipamento.status;
    
    // Verificar se a opção existe
    let optionExists = false;
    for (let i = 0; i < statusSelect.options.length; i++) {
        if (statusSelect.options[i].value === statusValue) {
            optionExists = true;
            break;
        }
    }
    
    // Se não existe, adicionar temporariamente
    if (!optionExists) {
        const option = document.createElement('option');
        option.value = statusValue;
        option.textContent = statusValue;
        statusSelect.appendChild(option);
    }
    
    statusSelect.value = statusValue;
    
    document.getElementById('processador').value = equipamento.processador || '';
    document.getElementById('memoria_ram').value = equipamento.memoria_ram || '';
    document.getElementById('armazenamento').value = equipamento.armazenamento || '';
    document.getElementById('sistema_operacional').value = equipamento.sistema_operacional || '';
    document.getElementById('data_aquisicao').value = equipamento.data_aquisicao || '';
    document.getElementById('valor').value = equipamento.valor || '';
    document.getElementById('observacoes').value = equipamento.observacoes || '';
    // Foto existente
    const fotoPreview = document.getElementById('fotoPreview');
    const fotoInput = document.getElementById('foto');
    if (fotoInput) { fotoInput.value = ''; }
    if (equipamento.foto_url && fotoPreview) {
        fotoPreview.src = equipamento.foto_url;
        fotoPreview.style.display = 'inline-block';
    } else if (fotoPreview) {
        fotoPreview.style.display = 'none';
        fotoPreview.src = '';
    }
}

// CRUD
async function salvarEquipamento() {
    const fd = new FormData();
    fd.append('nome', document.getElementById('nome').value);
    fd.append('tipo', document.getElementById('tipo').value);
    fd.append('marca', document.getElementById('marca').value);
    fd.append('modelo', document.getElementById('modelo').value);
    fd.append('numero_serie', document.getElementById('numero_serie').value);
    fd.append('status', document.getElementById('status').value);
    fd.append('data_aquisicao', document.getElementById('data_aquisicao').value);
    fd.append('valor', document.getElementById('valor').value);
    fd.append('observacoes', document.getElementById('observacoes').value);
    
    // Adicionar campos específicos baseado na categoria
    if (categoriaAtual === 'computador' || categoriaAtual === 'notebook') {
        fd.append('processador', document.getElementById('processador').value);
        fd.append('memoria_ram', document.getElementById('memoria_ram').value);
        fd.append('armazenamento', document.getElementById('armazenamento').value);
        fd.append('sistema_operacional', document.getElementById('sistema_operacional').value);
    } else if (categoriaAtual === 'periferico') {
        // Para periféricos, armazenar conectividade e compatibilidade nas observações
        const conectividade = document.getElementById('conectividade')?.value;
        const compatibilidade = document.getElementById('compatibilidade')?.value;
        
        let obsExtra = '';
        if (conectividade) obsExtra += `Conectividade: ${conectividade}\n`;
        if (compatibilidade) obsExtra += `Compatibilidade: ${compatibilidade}`;
        
        if (obsExtra) {
            const atual = document.getElementById('observacoes').value;
            fd.set('observacoes', obsExtra + (atual ? '\n\n' + atual : ''));
        }
    }
    // Foto (se selecionada)
    const fotoInput = document.getElementById('foto');
    if (fotoInput && fotoInput.files && fotoInput.files[0]) {
        fd.append('foto', fotoInput.files[0]);
    }

    try {
        const url = editandoId ? `/equipamento/editar/${editandoId}` : '/equipamento/adicionar';
        const method = editandoId ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            body: fd
        });

        const data = await response.json();

        if (data.success) {
            mostrarAlerta(data.message, 'success');
            fecharModal();
            carregarEquipamentos();
            carregarDashboard();
        } else {
            mostrarAlerta(data.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao salvar equipamento:', error);
        mostrarAlerta('Erro ao salvar equipamento', 'error');
    }
}

async function editarEquipamento(id) {
    try {
        const response = await fetch(`/equipamento/${id}`);
        const equipamento = await response.json();
        abrirModal(equipamento);
    } catch (error) {
        console.error('Erro ao carregar equipamento:', error);
        mostrarAlerta('Erro ao carregar equipamento', 'error');
    }
}

async function deletarEquipamento(id) {
    if (!confirm('Tem certeza que deseja deletar este equipamento?')) {
        return;
    }

    try {
        const response = await fetch(`/equipamento/deletar/${id}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            mostrarAlerta(data.message, 'success');
            carregarEquipamentos();
            carregarDashboard();
        } else {
            mostrarAlerta(data.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao deletar equipamento:', error);
        mostrarAlerta('Erro ao deletar equipamento', 'error');
    }
}

// Alertas
function mostrarAlerta(mensagem, tipo) {
    const alertaExistente = document.querySelector('.alert');
    if (alertaExistente) {
        alertaExistente.remove();
    }

    const alerta = document.createElement('div');
    alerta.className = `alert alert-${tipo}`;
    alerta.textContent = mensagem;

    const container = document.querySelector('.container');
    container.insertBefore(alerta, container.firstChild);

    setTimeout(() => {
        alerta.remove();
    }, 5000);
}


// ===== FUNÇÕES DE EMPRÉSTIMO =====

async function carregarEmprestimos() {
    try {
        const response = await fetch('/emprestimos-ativos');
        emprestimos = await response.json();
        renderizarEmprestimos(emprestimos);
    } catch (error) {
        console.error('Erro ao carregar empréstimos:', error);
        mostrarAlerta('Erro ao carregar empréstimos', 'error');
    }
}

function renderizarEmprestimos(lista) {
    const tbody = document.getElementById('emprestimosBody');
    
    if (!tbody) {
        console.error('Elemento emprestimosBody não encontrado');
        return;
    }
    
    if (lista.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; padding: 40px;">Nenhum empréstimo ativo no momento</td></tr>';
        return;
    }

    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    
    tbody.innerHTML = lista.map(emp => {
        const eq = emp.equipamento;
        const dataEmprestimo = emp.data_emprestimo ? new Date(emp.data_emprestimo).toLocaleDateString('pt-BR') : '-';
        const dataPrevista = emp.data_devolucao_prevista ? new Date(emp.data_devolucao_prevista).toLocaleDateString('pt-BR') : '-';
        
        // Verificar se está atrasado ou próximo ao vencimento
        let rowClass = '';
        let statusBadge = 'status-ativo';
        let statusText = 'Ativo';
        let alertIcon = '';
        if (emp.data_devolucao_prevista) {
            const dataPrev = new Date(emp.data_devolucao_prevista);
            dataPrev.setHours(0, 0, 0, 0);
            const diffDias = Math.ceil((dataPrev - hoje) / 86400000);
            if (diffDias < 0) {
                rowClass = 'style="background-color:#fee2e2;"';
                statusBadge = 'status-atrasado';
                statusText = 'Atrasado';
                alertIcon = '⚠️ ';
            } else if (diffDias <= 3) {
                rowClass = 'style="background-color:#fef3c7;"';
                alertIcon = '🔔 ';
            }
        }
        
        return `
            <tr ${rowClass}>
                <td>${alertIcon}${eq.nome}</td>
                <td>${eq.tipo}</td>
                <td>${eq.numero_serie}</td>
                <td>${emp.responsavel}</td>
                <td>${emp.departamento}</td>
                <td>${dataEmprestimo}</td>
                <td>${dataPrevista}</td>
                <td><span class="status-badge ${statusBadge}">${statusText}</span></td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-success" onclick="devolverEquipamento(${emp.id})">✓ Devolver</button>
                        <button class="btn btn-danger" onclick="deletarEmprestimo(${emp.id})">🗑️ Deletar</button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function filtrarEmprestimos(termo) {
    const termoLower = termo.toLowerCase();
    const filtrados = emprestimos.filter(emp => {
        const eq = emp.equipamento;
        return eq.nome.toLowerCase().includes(termoLower) ||
               eq.tipo.toLowerCase().includes(termoLower) ||
               eq.numero_serie.toLowerCase().includes(termoLower) ||
               emp.responsavel.toLowerCase().includes(termoLower) ||
               emp.departamento.toLowerCase().includes(termoLower);
    });
    renderizarEmprestimos(filtrados);
}

async function abrirModalEmprestimo() {
    const modal = document.getElementById('modalEmprestimo');
    
    // Carregar equipamentos disponíveis em estoque
    try {
        const response = await fetch('/equipamentos-estoque');
        equipamentosEstoque = await response.json();
        
        if (equipamentosEstoque.length === 0) {
            mostrarAlerta('Não há equipamentos disponíveis em estoque para empréstimo', 'error');
            return;
        }
        
        preencherSelectEquipamentos(equipamentosEstoque);
        modal.style.display = 'block';
    } catch (error) {
        console.error('Erro ao carregar equipamentos:', error);
        mostrarAlerta('Erro ao carregar equipamentos disponíveis', 'error');
    }
}

function preencherSelectEquipamentos(lista) {
    const select = document.getElementById('equipamento_select');
    select.innerHTML = lista.map(eq => 
        `<option value="${eq.id}">${eq.nome} - ${eq.tipo} (${eq.numero_serie})</option>`
    ).join('');
}

function filtrarEquipamentosEstoque() {
    const termo = document.getElementById('equipamento_search').value.toLowerCase();
    const filtrados = equipamentosEstoque.filter(eq => 
        eq.nome.toLowerCase().includes(termo) ||
        eq.tipo.toLowerCase().includes(termo) ||
        eq.numero_serie.toLowerCase().includes(termo)
    );
    preencherSelectEquipamentos(filtrados);
}

function fecharModalEmprestimo() {
    const modal = document.getElementById('modalEmprestimo');
    modal.style.display = 'none';
    document.getElementById('formEmprestimo').reset();
}

async function salvarEmprestimo() {
    const formData = {
        equipamento_id: parseInt(document.getElementById('equipamento_select').value),
        responsavel: document.getElementById('responsavel').value,
        departamento: document.getElementById('departamento').value,
        email_responsavel: document.getElementById('email_responsavel').value,
        telefone_responsavel: document.getElementById('telefone_responsavel').value,
        data_devolucao_prevista: document.getElementById('data_devolucao_prevista').value,
        observacoes: document.getElementById('observacoes_emprestimo').value
    };

    try {
        const response = await fetch('/emprestimo/adicionar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            mostrarAlerta(data.message, 'success');
            fecharModalEmprestimo();
            carregarEmprestimos();
            carregarEquipamentos();
            carregarDashboard();
        } else {
            mostrarAlerta(data.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao salvar empréstimo:', error);
        mostrarAlerta('Erro ao registrar empréstimo', 'error');
    }
}

async function devolverEquipamento(id) {
    if (!confirm('Confirma a devolução deste equipamento?')) {
        return;
    }

    try {
        const response = await fetch(`/emprestimo/devolver/${id}`, {
            method: 'PUT'
        });

        const data = await response.json();

        if (data.success) {
            mostrarAlerta(data.message, 'success');
            carregarEmprestimos();
            carregarEquipamentos();
            carregarDashboard();
        } else {
            mostrarAlerta(data.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao devolver equipamento:', error);
        mostrarAlerta('Erro ao registrar devolução', 'error');
    }
}

async function deletarEmprestimo(id) {
    if (!confirm('Tem certeza que deseja deletar este empréstimo?')) {
        return;
    }

    try {
        const response = await fetch(`/emprestimo/deletar/${id}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            mostrarAlerta(data.message, 'success');
            carregarEmprestimos();
            carregarEquipamentos();
            carregarDashboard();
        } else {
            mostrarAlerta(data.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao deletar empréstimo:', error);
        mostrarAlerta('Erro ao deletar empréstimo', 'error');
    }
}

// ===== QR CODE =====

let qrcodeAtual = null;

async function mostrarQRCode(equipamentoId) {
    try {
        const response = await fetch(`/equipamento/${equipamentoId}/qrcode`);
        const data = await response.json();
        
        if (data.success) {
            qrcodeAtual = data;
            
            // Exibe informações do equipamento
            const info = `
                <strong>Nome:</strong> ${data.equipamento.nome}<br>
                <strong>Marca:</strong> ${data.equipamento.marca}<br>
                <strong>Modelo:</strong> ${data.equipamento.modelo}<br>
                <strong>Nº Série:</strong> ${data.equipamento.numero_serie}
            `;
            document.getElementById('qrcodeInfo').innerHTML = info;
            document.getElementById('qrcodeImage').src = data.qrcode;
            document.getElementById('modalQRCode').style.display = 'block';
        } else {
            alert(data.message || 'Erro ao gerar QR Code');
        }
    } catch (error) {
        console.error('Erro ao gerar QR Code:', error);
        alert('Erro ao gerar QR Code');
    }
}

function fecharModalQRCode() {
    document.getElementById('modalQRCode').style.display = 'none';
    qrcodeAtual = null;
}

function baixarQRCode() {
    if (!qrcodeAtual) return;
    
    const link = document.createElement('a');
    link.href = qrcodeAtual.qrcode;
    link.download = `qrcode_${qrcodeAtual.equipamento.numero_serie}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function imprimirQRCode() {
    if (!qrcodeAtual) return;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html>
        <head>
            <title>QR Code - ${qrcodeAtual.equipamento.nome}</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 20px;
                }
                img { 
                    max-width: 300px; 
                    border: 2px solid #333;
                    padding: 10px;
                    background: white;
                }
                .info { 
                    margin: 20px 0; 
                    text-align: left;
                    display: inline-block;
                }
            </style>
        </head>
        <body>
            <h2>Equipamento: ${qrcodeAtual.equipamento.nome}</h2>
            <div class="info">
                <strong>Marca:</strong> ${qrcodeAtual.equipamento.marca}<br>
                <strong>Modelo:</strong> ${qrcodeAtual.equipamento.modelo}<br>
                <strong>Nº Série:</strong> ${qrcodeAtual.equipamento.numero_serie}<br>
                <strong>ID:</strong> ${qrcodeAtual.equipamento.id}
            </div><br>
            <img src="${qrcodeAtual.qrcode}" />
        </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
        printWindow.print();
        printWindow.close();
    }, 250);
}

// ===== MANUTENÇÕES =====
async function abrirModalManutencao(equipamentoId) {
    manutencaoEquipamentoId = equipamentoId;
    const modal = document.getElementById('modalManutencao');
    await carregarManutencoes(equipamentoId);
    modal.style.display = 'block';
}

function fecharModalManutencao() {
    const modal = document.getElementById('modalManutencao');
    modal.style.display = 'none';
    manutencaoEquipamentoId = null;
    document.getElementById('formManutencao')?.reset();
    document.getElementById('manutencoesBody').innerHTML = '<tr><td colspan="9" style="text-align:center;padding:24px;">Carregando histórico...</td></tr>';
}

async function carregarManutencoes(equipamentoId) {
    try {
        const res = await fetch(`/equipamento/${equipamentoId}/manutencoes`);
        const data = await res.json();
        if (data.success) {
            manutencoesCache = data.manutencoes || [];
            renderizarManutencoes(manutencoesCache);
        } else {
            renderizarManutencoes([]);
            mostrarAlerta(data.message || 'Erro ao carregar manutenções', 'error');
        }
    } catch (e) {
        console.error(e);
        mostrarAlerta('Erro ao carregar manutenções', 'error');
    }
}

function renderizarManutencoes(lista) {
    const tbody = document.getElementById('manutencoesBody');
    if (!lista || lista.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;padding:24px;">Sem registros de manutenção</td></tr>';
        return;
    }
    tbody.innerHTML = lista.map(m => {
        const inicio = m.data_inicio && m.data_inicio !== 'undefined' ? new Date(m.data_inicio).toLocaleDateString('pt-BR') : '-';
        const fim = m.data_fim && m.data_fim !== 'undefined' ? new Date(m.data_fim).toLocaleDateString('pt-BR') : '-';
        const custo = (m.custo || m.custo === 0) ? Number(m.custo).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) : '-';
        const desc = (m.descricao || '').replace(/\n/g, '<br>');
        return `
            <tr>
                <td>${inicio}</td>
                <td>${fim}</td>
                <td>${m.tipo}</td>
                <td><span class="status-badge">${m.status}</span></td>
                <td>${m.responsavel || '-'}</td>
                <td>${m.fornecedor || '-'}</td>
                <td>${custo === '-' ? '-' : 'R$ ' + custo}</td>
                <td style="max-width:260px;">${desc || '-'}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-edit" onclick="iniciarEdicaoManutencao(${m.id})">✏️</button>
                        <button class="btn btn-danger" onclick="deletarManutencao(${m.id})">🗑️</button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

async function salvarManutencao() {
    if (!manutencaoEquipamentoId) return;
    const payload = {
        tipo: document.getElementById('manTipo').value,
        status: document.getElementById('manStatus').value,
        data_inicio: document.getElementById('manDataInicio').value,
        data_fim: document.getElementById('manDataFim').value,
        custo: document.getElementById('manCusto').value,
        responsavel: document.getElementById('manResponsavel').value,
        fornecedor: document.getElementById('manFornecedor').value,
        descricao: document.getElementById('manDescricao').value,
        atualizar_status_equipamento: true
    };
    try {
        const isEditing = !!manutencaoEditandoId;
        const url = isEditing ? `/manutencao/editar/${manutencaoEditandoId}` : `/equipamento/${manutencaoEquipamentoId}/manutencao/adicionar`;
        const method = isEditing ? 'PUT' : 'POST';
        const res = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            mostrarAlerta(data.message, 'success');
            await carregarManutencoes(manutencaoEquipamentoId);
            resetFormularioManutencao();
            // Atualizar lista e dashboard (status pode mudar para Manutenção)
            await carregarEquipamentos();
            await carregarDashboard();
            // Fechar o modal após salvar com sucesso
            fecharModalManutencao();
        } else {
            mostrarAlerta(data.message || 'Erro ao salvar manutenção', 'error');
        }
    } catch (e) {
        console.error(e);
        mostrarAlerta('Erro ao salvar manutenção', 'error');
    }
}

async function deletarManutencao(id) {
    if (!confirm('Tem certeza que deseja deletar este registro de manutenção?')) return;
    try {
        const res = await fetch(`/manutencao/deletar/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            mostrarAlerta(data.message, 'success');
            if (manutencaoEquipamentoId) await carregarManutencoes(manutencaoEquipamentoId);
            if (manutencaoEditandoId === id) resetFormularioManutencao();
        } else {
            mostrarAlerta(data.message || 'Erro ao deletar manutenção', 'error');
        }
    } catch (e) {
        console.error(e);
        mostrarAlerta('Erro ao deletar manutenção', 'error');
    }
}

function iniciarEdicaoManutencao(id) {
    const m = manutencoesCache.find(x => x.id === id);
    if (!m) return;
    manutencaoEditandoId = id;
    document.getElementById('manTipo').value = m.tipo || 'Corretiva';
    document.getElementById('manStatus').value = m.status || 'Em Andamento';
    document.getElementById('manDataInicio').value = m.data_inicio || '';
    document.getElementById('manDataFim').value = m.data_fim || '';
    document.getElementById('manCusto').value = m.custo != null ? m.custo : '';
    document.getElementById('manResponsavel').value = m.responsavel || '';
    document.getElementById('manFornecedor').value = m.fornecedor || '';
    document.getElementById('manDescricao').value = m.descricao || '';
    const submitBtn = document.querySelector('#formManutencao .btn.btn-primary');
    if (submitBtn) submitBtn.textContent = 'Atualizar';
}

function resetFormularioManutencao() {
    manutencaoEditandoId = null;
    const form = document.getElementById('formManutencao');
    if (form) form.reset();
    const submitBtn = document.querySelector('#formManutencao .btn.btn-primary');
    if (submitBtn) submitBtn.textContent = 'Salvar';
}
