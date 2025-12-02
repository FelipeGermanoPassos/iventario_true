// JavaScript para Previsão de Demanda com IA
let chartTendencias = null;
let chartSazonalidade = null;
let chartPrioridades = null;
let chartUtilizacao = null;
let previsoesData = [];

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    carregarDados();
    
    // Botão atualizar
    document.getElementById('btnAtualizar').addEventListener('click', function() {
        carregarDados();
    });
    
    // Modal
    const modal = document.getElementById('modalDetalhes');
    const span = document.getElementsByClassName('close')[0];
    
    span.onclick = function() {
        modal.style.display = 'none';
    }
    
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
});

// Carregar dados da API
async function carregarDados() {
    try {
        mostrarLoading();
        
        const response = await fetch('/previsao-demanda/dados');
        const data = await response.json();
        
        if (data.success) {
            previsoesData = data.previsoes || [];
            
            // Atualizar header
            atualizarHeader(data);
            
            // Atualizar alertas
            gerarAlertas(previsoesData);
            
            // Atualizar tabela
            atualizarTabela(previsoesData);
            
            // Atualizar gráficos
            atualizarGraficos(previsoesData, data.sazonalidade);
            
            // Gerar insights
            gerarInsights(previsoesData, data.sazonalidade);
        } else {
            mostrarErro(data.message || 'Erro ao carregar dados');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarErro('Erro ao conectar com o servidor');
    }
}

// Atualizar header
function atualizarHeader(data) {
    document.getElementById('horizonte').textContent = `Próximos ${data.horizonte_dias || 90} dias`;
    document.getElementById('totalPrevisoes').textContent = (data.previsoes || []).length;
    
    if (data.data_analise) {
        const dataAnalise = new Date(data.data_analise);
        document.getElementById('dataAnalise').textContent = formatarHora(dataAnalise);
    }
}

// Gerar alertas de alta prioridade
function gerarAlertas(previsoes) {
    const container = document.getElementById('alertasContainer');
    container.innerHTML = '';
    
    const alertasAlta = previsoes.filter(p => p.recomendacao.prioridade === 'alta');
    
    if (alertasAlta.length === 0) {
        container.innerHTML = `
            <div class="alerta alerta-info">
                <span>✅</span>
                <span>Nenhuma ação urgente necessária no momento.</span>
            </div>
        `;
        return;
    }
    
    alertasAlta.forEach(prev => {
        const alerta = document.createElement('div');
        alerta.className = 'alerta alerta-alta';
        alerta.innerHTML = `
            <span>🚨</span>
            <span><strong>${prev.tipo}:</strong> ${prev.recomendacao.mensagem}</span>
        `;
        container.appendChild(alerta);
    });
}

// Atualizar tabela
function atualizarTabela(previsoes) {
    const tbody = document.getElementById('previsoesTableBody');
    
    if (previsoes.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="loading-row">
                    📊 Dados insuficientes para análise. Registre mais empréstimos para gerar previsões.
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = '';
    
    previsoes.forEach(prev => {
        const tr = document.createElement('tr');
        
        const classePrioridade = `badge-prioridade-${prev.recomendacao.prioridade}`;
        const classeTendencia = `badge-tendencia-${prev.tendencia}`;
        const classeAcao = `badge-acao-${prev.recomendacao.acao}`;
        
        const iconeTendencia = prev.tendencia === 'crescente' ? '📈' : 
                              prev.tendencia === 'decrescente' ? '📉' : '➡️';
        
        const iconeAcao = prev.recomendacao.acao === 'comprar' ? '🛒' :
                         prev.recomendacao.acao === 'planejar' ? '📋' : '👁️';
        
        tr.innerHTML = `
            <td><strong>${prev.tipo}</strong></td>
            <td>
                <div class="metrica">
                    <span class="metrica-valor">${prev.qtd_estoque}/${prev.qtd_total}</span>
                    <span class="metrica-label">disponível</span>
                </div>
            </td>
            <td>
                <span class="badge ${classeTendencia}">
                    ${iconeTendencia} ${prev.tendencia}
                </span>
            </td>
            <td>
                <div class="metrica">
                    <span class="metrica-valor">${prev.taxa_utilizacao}%</span>
                    <span class="metrica-label">últimos 30 dias</span>
                </div>
            </td>
            <td>
                <span class="metrica-valor" style="color: ${prev.taxa_crescimento > 0 ? 'var(--danger-color)' : 'var(--success-color)'}">
                    ${prev.taxa_crescimento > 0 ? '+' : ''}${prev.taxa_crescimento}%
                </span>
            </td>
            <td>
                <span class="badge ${classePrioridade}">
                    ${prev.recomendacao.prioridade.toUpperCase()}
                </span>
            </td>
            <td>
                <span class="badge ${classeAcao}">
                    ${iconeAcao} ${prev.recomendacao.mensagem}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-info" onclick="mostrarDetalhes('${prev.tipo}')">
                    📊 Ver Detalhes
                </button>
            </td>
        `;
        
        tbody.appendChild(tr);
    });
}

// Mostrar detalhes no modal
function mostrarDetalhes(tipo) {
    const previsao = previsoesData.find(p => p.tipo === tipo);
    if (!previsao) return;
    
    const modal = document.getElementById('modalDetalhes');
    const titulo = document.getElementById('modalTitulo');
    const body = document.getElementById('modalBody');
    
    titulo.textContent = `📊 Análise Detalhada: ${tipo}`;
    
    body.innerHTML = `
        <div class="detalhe-item">
            <h4>📈 Métricas Atuais</h4>
            <ul class="detalhe-lista">
                <li><strong>Quantidade Total:</strong> ${previsao.qtd_total} unidades</li>
                <li><strong>Em Estoque:</strong> ${previsao.qtd_estoque} unidades (${((previsao.qtd_estoque/previsao.qtd_total)*100).toFixed(0)}%)</li>
                <li><strong>Emprestados:</strong> ${previsao.qtd_total - previsao.qtd_estoque} unidades</li>
                <li><strong>Taxa de Utilização:</strong> ${previsao.taxa_utilizacao}% (últimos 30 dias)</li>
                <li><strong>Média Mensal:</strong> ${previsao.media_mensal} empréstimos</li>
            </ul>
        </div>
        
        <div class="detalhe-item">
            <h4>🔮 Previsão</h4>
            <ul class="detalhe-lista">
                <li><strong>Tendência:</strong> <span class="badge badge-tendencia-${previsao.tendencia}">${previsao.tendencia}</span></li>
                <li><strong>Taxa de Crescimento:</strong> ${previsao.taxa_crescimento}%</li>
                <li><strong>Previsão Mês 1:</strong> ${previsao.previsao_proximos_meses[0]} empréstimos</li>
                <li><strong>Previsão Mês 2:</strong> ${previsao.previsao_proximos_meses[1]} empréstimos</li>
                <li><strong>Previsão Mês 3:</strong> ${previsao.previsao_proximos_meses[2]} empréstimos</li>
            </ul>
        </div>
        
        <div class="detalhe-item">
            <h4>💡 Recomendação</h4>
            <ul class="detalhe-lista">
                <li><strong>Prioridade:</strong> <span class="badge badge-prioridade-${previsao.recomendacao.prioridade}">${previsao.recomendacao.prioridade.toUpperCase()}</span></li>
                <li><strong>Ação:</strong> <span class="badge badge-acao-${previsao.recomendacao.acao}">${previsao.recomendacao.acao}</span></li>
                <li><strong>Quantidade Sugerida:</strong> ${previsao.recomendacao.qtd_sugerida} unidade(s)</li>
                <li><strong>Mensagem:</strong> ${previsao.recomendacao.mensagem}</li>
            </ul>
        </div>
        
        <div class="detalhe-item">
            <h4>📋 Justificativas</h4>
            <ul class="detalhe-lista">
                ${previsao.recomendacao.justificativas.map(j => `<li>${j}</li>`).join('')}
            </ul>
        </div>
        
        <div class="detalhe-item">
            <h4>📊 Histórico Recente</h4>
            <table class="historico-table">
                <thead>
                    <tr>
                        <th>Mês</th>
                        <th>Empréstimos</th>
                    </tr>
                </thead>
                <tbody>
                    ${previsao.historico_meses.map(h => `
                        <tr>
                            <td>${h.mes}</td>
                            <td>${h.quantidade}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    modal.style.display = 'block';
}

// Atualizar gráficos
function atualizarGraficos(previsoes, sazonalidade) {
    // Destruir gráficos existentes
    if (chartTendencias) chartTendencias.destroy();
    if (chartSazonalidade) chartSazonalidade.destroy();
    if (chartPrioridades) chartPrioridades.destroy();
    if (chartUtilizacao) chartUtilizacao.destroy();
    
    // Gráfico de tendências
    criarGraficoTendencias(previsoes);
    
    // Gráfico de sazonalidade
    if (sazonalidade && sazonalidade.sucesso) {
        criarGraficoSazonalidade(sazonalidade);
    }
    
    // Gráfico de prioridades
    criarGraficoPrioridades(previsoes);
    
    // Gráfico de utilização
    criarGraficoUtilizacao(previsoes);
}

// Criar gráfico de tendências
function criarGraficoTendencias(previsoes) {
    const ctx = document.getElementById('chartTendencias').getContext('2d');
    
    const labels = previsoes.map(p => p.tipo);
    const crescimento = previsoes.map(p => p.taxa_crescimento);
    
    chartTendencias = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Taxa de Crescimento (%)',
                data: crescimento,
                backgroundColor: crescimento.map(v => 
                    v > 10 ? 'rgba(231, 76, 60, 0.7)' :
                    v > 5 ? 'rgba(243, 156, 18, 0.7)' :
                    'rgba(46, 204, 113, 0.7)'
                ),
                borderColor: crescimento.map(v => 
                    v > 10 ? 'rgba(231, 76, 60, 1)' :
                    v > 5 ? 'rgba(243, 156, 18, 1)' :
                    'rgba(46, 204, 113, 1)'
                ),
                borderWidth: 2
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
                    title: {
                        display: true,
                        text: 'Crescimento (%)'
                    }
                }
            }
        }
    });
}

// Criar gráfico de sazonalidade
function criarGraficoSazonalidade(sazonalidade) {
    const ctx = document.getElementById('chartSazonalidade').getContext('2d');
    
    const labels = sazonalidade.sazonalidade.map(s => s.nome_mes);
    const valores = sazonalidade.sazonalidade.map(s => s.quantidade);
    
    chartSazonalidade = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Empréstimos por Mês',
                data: valores,
                borderColor: 'rgba(102, 126, 234, 1)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                fill: true,
                tension: 0.4,
                borderWidth: 3,
                pointRadius: 5,
                pointBackgroundColor: 'rgba(102, 126, 234, 1)'
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
                    title: {
                        display: true,
                        text: 'Quantidade'
                    }
                }
            }
        }
    });
}

// Criar gráfico de prioridades
function criarGraficoPrioridades(previsoes) {
    const ctx = document.getElementById('chartPrioridades').getContext('2d');
    
    const prioridades = {
        'alta': previsoes.filter(p => p.recomendacao.prioridade === 'alta').length,
        'media': previsoes.filter(p => p.recomendacao.prioridade === 'media').length,
        'baixa': previsoes.filter(p => p.recomendacao.prioridade === 'baixa').length
    };
    
    chartPrioridades = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Alta Prioridade', 'Média Prioridade', 'Baixa Prioridade'],
            datasets: [{
                data: [prioridades.alta, prioridades.media, prioridades.baixa],
                backgroundColor: [
                    'rgba(231, 76, 60, 0.8)',
                    'rgba(243, 156, 18, 0.8)',
                    'rgba(46, 204, 113, 0.8)'
                ],
                borderWidth: 2
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
}

// Criar gráfico de utilização
function criarGraficoUtilizacao(previsoes) {
    const ctx = document.getElementById('chartUtilizacao').getContext('2d');
    
    const labels = previsoes.map(p => p.tipo);
    const utilizacao = previsoes.map(p => p.taxa_utilizacao);
    
    chartUtilizacao = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Taxa de Utilização (%)',
                data: utilizacao,
                backgroundColor: 'rgba(52, 152, 219, 0.7)',
                borderColor: 'rgba(52, 152, 219, 1)',
                borderWidth: 2
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
                    max: 100,
                    title: {
                        display: true,
                        text: 'Utilização (%)'
                    }
                }
            }
        }
    });
}

// Gerar insights
function gerarInsights(previsoes, sazonalidade) {
    const container = document.getElementById('insightsContainer');
    container.innerHTML = '';
    
    const insights = [];
    
    // Insights de prioridade alta
    const altaPrioridade = previsoes.filter(p => p.recomendacao.prioridade === 'alta');
    if (altaPrioridade.length > 0) {
        insights.push({
            icon: '🚨',
            tipo: 'Ação Urgente',
            texto: `${altaPrioridade.length} tipo(s) de equipamento necessitam compra imediata: ${altaPrioridade.map(p => p.tipo).join(', ')}`
        });
    }
    
    // Insights de crescimento
    const crescimentoAlto = previsoes.filter(p => p.taxa_crescimento > 20);
    if (crescimentoAlto.length > 0) {
        insights.push({
            icon: '📈',
            tipo: 'Crescimento Acelerado',
            texto: `${crescimentoAlto[0].tipo} apresenta crescimento de ${crescimentoAlto[0].taxa_crescimento}%. Demanda está aumentando rapidamente.`
        });
    }
    
    // Insights de utilização
    const altaUtilizacao = previsoes.filter(p => p.taxa_utilizacao > 80);
    if (altaUtilizacao.length > 0) {
        insights.push({
            icon: '⚡',
            tipo: 'Alta Demanda',
            texto: `${altaUtilizacao.map(p => p.tipo).join(', ')} com taxa de utilização acima de 80%. Considere aumentar estoque.`
        });
    }
    
    // Insights de sazonalidade
    if (sazonalidade && sazonalidade.sucesso && sazonalidade.meses_pico) {
        insights.push({
            icon: '📅',
            tipo: 'Padrão Sazonal',
            texto: `Picos de demanda em ${sazonalidade.meses_pico.join(', ')}. Planeje compras antecipadamente.`
        });
    }
    
    // Insights positivos
    const baixaPrioridade = previsoes.filter(p => p.recomendacao.prioridade === 'baixa');
    if (baixaPrioridade.length > 0 && previsoes.length === baixaPrioridade.length) {
        insights.push({
            icon: '✅',
            tipo: 'Estoque Saudável',
            texto: 'Todos os tipos de equipamento estão com estoque adequado. Continue monitorando tendências.'
        });
    }
    
    // Se não houver insights
    if (insights.length === 0) {
        insights.push({
            icon: '📊',
            tipo: 'Análise em Andamento',
            texto: 'Registre mais empréstimos para obter insights mais precisos sobre tendências de demanda.'
        });
    }
    
    // Renderizar insights
    insights.forEach(insight => {
        const card = document.createElement('div');
        card.className = 'insight-card';
        card.innerHTML = `
            <div class="insight-icon">${insight.icon}</div>
            <p>
                <span class="insight-tipo">${insight.tipo}:</span>
                ${insight.texto}
            </p>
        `;
        container.appendChild(card);
    });
}

// Helpers
function mostrarLoading() {
    document.getElementById('previsoesTableBody').innerHTML = `
        <tr>
            <td colspan="8" class="loading-row">
                🔄 Analisando dados históricos com Machine Learning...
            </td>
        </tr>
    `;
}

function mostrarErro(mensagem) {
    document.getElementById('previsoesTableBody').innerHTML = `
        <tr>
            <td colspan="8" class="loading-row" style="color: var(--danger-color);">
                ❌ ${mensagem}
            </td>
        </tr>
    `;
}

function formatarHora(data) {
    return data.toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit'
    });
}
