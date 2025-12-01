// Variáveis globais
let todosEmprestimos = [];
let chartDepartamentos = null;
let chartEquipamentos = null;

// Carrega dados ao iniciar
document.addEventListener('DOMContentLoaded', () => {
    carregarDepartamentos();
    aplicarFiltros();
    
    // Event listeners
    document.getElementById('btnAplicarFiltros').addEventListener('click', aplicarFiltros);
    document.getElementById('btnLimparFiltros').addEventListener('click', limparFiltros);
    document.getElementById('btnExportar').addEventListener('click', exportarCSV);
});

// Carrega lista de departamentos para o filtro
async function carregarDepartamentos() {
    try {
        const response = await fetch('/relatorios/departamentos');
        const data = await response.json();
        
        if (data.success) {
            const select = document.getElementById('filtroDepartamento');
            data.departamentos.forEach(dept => {
                const option = document.createElement('option');
                option.value = dept;
                option.textContent = dept;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar departamentos:', error);
    }
}

// Aplica filtros e carrega relatório
async function aplicarFiltros() {
    try {
        const filtroTipo = document.getElementById('filtroTipo').value;
        const filtroDepartamento = document.getElementById('filtroDepartamento').value;
        const dataInicio = document.getElementById('dataInicio').value;
        const dataFim = document.getElementById('dataFim').value;
        
        // Monta a URL com os parâmetros
        const params = new URLSearchParams({
            filtro: filtroTipo
        });
        
        if (filtroDepartamento && filtroDepartamento !== 'todos') {
            params.append('departamento', filtroDepartamento);
        }
        
        if (dataInicio) {
            params.append('data_inicio', dataInicio);
        }
        
        if (dataFim) {
            params.append('data_fim', dataFim);
        }
        
        const response = await fetch(`/relatorios/emprestimos?${params.toString()}`);
        const data = await response.json();
        
        if (data.success) {
            todosEmprestimos = data.emprestimos;
            atualizarEstatisticas(data.estatisticas);
            renderizarTabela(data.emprestimos);
            renderizarGraficos(data.emprestimos_por_departamento, data.top_equipamentos);
            
            document.getElementById('totalRegistros').textContent = 
                `${data.emprestimos.length} ${data.emprestimos.length === 1 ? 'registro encontrado' : 'registros encontrados'}`;
        } else {
            mostrarMensagem(data.message, 'error');
        }
        
    } catch (error) {
        mostrarMensagem('Erro ao carregar relatório.', 'error');
        console.error('Erro:', error);
    }
}

// Limpa todos os filtros
function limparFiltros() {
    document.getElementById('filtroTipo').value = 'todos';
    document.getElementById('filtroDepartamento').value = 'todos';
    document.getElementById('dataInicio').value = '';
    document.getElementById('dataFim').value = '';
    aplicarFiltros();
}

// Atualiza estatísticas
function atualizarEstatisticas(stats) {
    document.getElementById('statTotal').textContent = stats.total;
    document.getElementById('statAtivos').textContent = stats.ativos;
    document.getElementById('statDevolvidos').textContent = stats.devolvidos;
    document.getElementById('statAtrasados').textContent = stats.atrasados;
    document.getElementById('statDuracaoMedia').textContent = stats.duracao_media;
}

// Renderiza tabela de empréstimos
function renderizarTabela(emprestimos) {
    const tbody = document.getElementById('emprestimosTableBody');
    tbody.innerHTML = '';
    
    if (emprestimos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 30px;">Nenhum empréstimo encontrado com os filtros aplicados</td></tr>';
        return;
    }
    
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    
    emprestimos.forEach(emprestimo => {
        const tr = document.createElement('tr');
        
        // Verifica se está atrasado
        const dataPrevisao = emprestimo.data_devolucao_prevista ? new Date(emprestimo.data_devolucao_prevista) : null;
        const isAtrasado = emprestimo.status === 'Ativo' && dataPrevisao && dataPrevisao < hoje;
        
        if (isAtrasado) {
            tr.classList.add('atrasado');
        }
        
        // Formata datas
        const dataEmprestimo = new Date(emprestimo.data_emprestimo).toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const dataPrevista = dataPrevisao ? 
            dataPrevisao.toLocaleDateString('pt-BR') : '-';
        
        const dataDevolucao = emprestimo.data_devolucao_real ? 
            new Date(emprestimo.data_devolucao_real).toLocaleDateString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            }) : '-';
        
        // Calcula dias
        let dias = '-';
        let diasClass = 'normal';
        
        if (emprestimo.status === 'Ativo') {
            const dataEmp = new Date(emprestimo.data_emprestimo);
            const diffTime = hoje - dataEmp;
            const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
            dias = diffDays;
            
            if (isAtrasado) {
                diasClass = 'critico';
            } else if (diffDays > 30) {
                diasClass = 'alerta';
            }
        } else if (emprestimo.data_devolucao_real) {
            const dataEmp = new Date(emprestimo.data_emprestimo);
            const dataDev = new Date(emprestimo.data_devolucao_real);
            const diffTime = dataDev - dataEmp;
            const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
            dias = diffDays;
        }
        
        // Status badge
        let statusClass = 'ativo';
        let statusText = emprestimo.status;
        
        if (emprestimo.status === 'Devolvido') {
            statusClass = 'devolvido';
        } else if (isAtrasado) {
            statusClass = 'atrasado';
            statusText = 'Atrasado';
        }
        
        tr.innerHTML = `
            <td><strong>${emprestimo.equipamento_nome || 'N/A'}</strong></td>
            <td>${emprestimo.responsavel}</td>
            <td>${emprestimo.departamento || '-'}</td>
            <td>${dataEmprestimo}</td>
            <td>${dataPrevista}</td>
            <td>${dataDevolucao}</td>
            <td><span class="status-badge-relatorio ${statusClass}">${statusText}</span></td>
            <td><span class="dias-badge ${diasClass}">${dias}</span></td>
        `;
        
        tbody.appendChild(tr);
    });
}

// Renderiza gráficos
function renderizarGraficos(emprestimosPorDept, topEquipamentos) {
    // Gráfico de Departamentos
    const ctxDept = document.getElementById('chartDepartamentos');
    
    if (chartDepartamentos) {
        chartDepartamentos.destroy();
    }
    
    const labelsDept = Object.keys(emprestimosPorDept);
    const dataDept = Object.values(emprestimosPorDept);
    
    chartDepartamentos = new Chart(ctxDept, {
        type: 'bar',
        data: {
            labels: labelsDept,
            datasets: [{
                label: 'Número de Empréstimos',
                data: dataDept,
                backgroundColor: 'rgba(59, 130, 246, 0.7)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 2,
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
                        stepSize: 1
                    }
                }
            }
        }
    });
    
    // Gráfico de Top Equipamentos
    const ctxEquip = document.getElementById('chartEquipamentos');
    
    if (chartEquipamentos) {
        chartEquipamentos.destroy();
    }
    
    const labelsEquip = topEquipamentos.map(e => e.nome);
    const dataEquip = topEquipamentos.map(e => e.quantidade);
    
    chartEquipamentos = new Chart(ctxEquip, {
        type: 'horizontalBar',
        data: {
            labels: labelsEquip,
            datasets: [{
                label: 'Número de Empréstimos',
                data: dataEquip,
                backgroundColor: [
                    'rgba(239, 68, 68, 0.7)',
                    'rgba(251, 191, 36, 0.7)',
                    'rgba(16, 185, 129, 0.7)',
                    'rgba(59, 130, 246, 0.7)',
                    'rgba(139, 92, 246, 0.7)',
                    'rgba(236, 72, 153, 0.7)',
                    'rgba(14, 165, 233, 0.7)',
                    'rgba(34, 197, 94, 0.7)',
                    'rgba(249, 115, 22, 0.7)',
                    'rgba(168, 85, 247, 0.7)'
                ],
                borderColor: [
                    'rgba(239, 68, 68, 1)',
                    'rgba(251, 191, 36, 1)',
                    'rgba(16, 185, 129, 1)',
                    'rgba(59, 130, 246, 1)',
                    'rgba(139, 92, 246, 1)',
                    'rgba(236, 72, 153, 1)',
                    'rgba(14, 165, 233, 1)',
                    'rgba(34, 197, 94, 1)',
                    'rgba(249, 115, 22, 1)',
                    'rgba(168, 85, 247, 1)'
                ],
                borderWidth: 2,
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
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Exporta dados para CSV
function exportarCSV() {
    if (todosEmprestimos.length === 0) {
        mostrarMensagem('Não há dados para exportar.', 'info');
        return;
    }
    
    // Cabeçalho do CSV
    let csv = 'Equipamento,Responsável,Departamento,Data Empréstimo,Devolução Prevista,Devolução Real,Status,Email,Telefone,Observações\n';
    
    // Adiciona os dados
    todosEmprestimos.forEach(emprestimo => {
        const dataEmprestimo = new Date(emprestimo.data_emprestimo).toLocaleDateString('pt-BR');
        const dataPrevista = emprestimo.data_devolucao_prevista ? 
            new Date(emprestimo.data_devolucao_prevista).toLocaleDateString('pt-BR') : '';
        const dataDevolucao = emprestimo.data_devolucao_real ? 
            new Date(emprestimo.data_devolucao_real).toLocaleDateString('pt-BR') : '';
        
        // Escapa aspas e vírgulas nos dados
        const equipamento = (emprestimo.equipamento_nome || '').replace(/"/g, '""');
        const responsavel = emprestimo.responsavel.replace(/"/g, '""');
        const departamento = (emprestimo.departamento || '').replace(/"/g, '""');
        const email = (emprestimo.email_responsavel || '').replace(/"/g, '""');
        const telefone = (emprestimo.telefone_responsavel || '').replace(/"/g, '""');
        const observacoes = (emprestimo.observacoes || '').replace(/"/g, '""');
        
        csv += `"${equipamento}","${responsavel}","${departamento}","${dataEmprestimo}","${dataPrevista}","${dataDevolucao}","${emprestimo.status}","${email}","${telefone}","${observacoes}"\n`;
    });
    
    // Cria o blob e faz o download
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    const dataAtual = new Date().toISOString().split('T')[0];
    link.setAttribute('href', url);
    link.setAttribute('download', `relatorio_emprestimos_${dataAtual}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    mostrarMensagem('Relatório exportado com sucesso!', 'success');
}

// Exibe mensagens de feedback
function mostrarMensagem(texto, tipo = 'info') {
    const mensagemDiv = document.getElementById('mensagem');
    mensagemDiv.textContent = texto;
    mensagemDiv.className = `message-relatorio ${tipo} show`;
    
    setTimeout(() => {
        mensagemDiv.className = 'message-relatorio';
    }, 5000);
}
