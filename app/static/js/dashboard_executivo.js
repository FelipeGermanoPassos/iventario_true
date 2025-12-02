// Dashboard Executivo - JavaScript

// Estado global
let dadosDashboard = null;
let charts = {};

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    carregarDados();
    
    document.getElementById('btnAtualizar').addEventListener('click', () => {
        carregarDados();
    });
});

// Carregar dados do dashboard
async function carregarDados() {
    try {
        mostrarLoading(true);
        
        const response = await fetch('/dashboard-executivo/dados');
        const data = await response.json();
        
        if (data.success) {
            dadosDashboard = data;
            atualizarDashboard(data);
            atualizarUltimaAtualizacao();
        } else {
            mostrarErro('Erro ao carregar dados: ' + data.message);
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarErro('Erro ao carregar dados do dashboard');
    } finally {
        mostrarLoading(false);
    }
}

// Atualizar todo o dashboard
function atualizarDashboard(data) {
    atualizarKPIs(data);
    atualizarGraficos(data);
    atualizarTabelas(data);
    gerarInsights(data);
}

// Atualizar KPIs
function atualizarKPIs(data) {
    // Valor total do inventário
    document.getElementById('valorTotalInventario').textContent = 
        formatarMoeda(data.inventario.valor_total);
    document.getElementById('totalEquipamentos').textContent = 
        `${data.inventario.total_equipamentos} equipamentos`;
    
    // Taxa de utilização
    document.getElementById('taxaUtilizacao').textContent = 
        `${data.utilizacao.taxa_utilizacao}%`;
    document.getElementById('emprestimosAtivos').textContent = 
        `${data.utilizacao.emprestimos_ativos} empréstimos ativos`;
    
    // Custo de manutenções
    document.getElementById('custoManutencoes').textContent = 
        formatarMoeda(data.manutencoes.custo_total);
    document.getElementById('manutencoesPendentes').textContent = 
        `${data.manutencoes.pendentes} pendentes`;
    
    // ROI médio
    document.getElementById('roiMedio').textContent = 
        `${data.roi.roi_medio}%`;
}

// Atualizar gráficos
function atualizarGraficos(data) {
    // Destruir gráficos existentes
    Object.values(charts).forEach(chart => chart.destroy());
    charts = {};
    
    // Gráfico: Investimento por Departamento
    criarGraficoInvestimentoDept(data.inventario.equipamentos_por_departamento);
    
    // Gráfico: Empréstimos por Mês
    criarGraficoEmprestimosMes(data.utilizacao.emprestimos_por_mes);
    
    // Gráfico: Custos de Manutenção por Mês
    criarGraficoCustosMes(data.manutencoes.custos_por_mes);
    
    // Gráfico: Tempo Médio por Departamento
    criarGraficoTempoDept(data.utilizacao.tempo_medio_por_departamento);
}

// Gráfico: Investimento por Departamento
function criarGraficoInvestimentoDept(dados) {
    const ctx = document.getElementById('chartInvestimentoDept').getContext('2d');
    
    const labels = dados.map(d => d.departamento);
    const valores = dados.map(d => d.valor_total);
    
    charts.investimentoDept = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Investimento Total (R$)',
                data: valores,
                backgroundColor: 'rgba(239, 125, 45, 0.6)',
                borderColor: 'rgba(239, 125, 45, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'R$ ' + context.parsed.y.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value.toLocaleString('pt-BR');
                        }
                    }
                }
            }
        }
    });
}

// Gráfico: Empréstimos por Mês
function criarGraficoEmprestimosMes(dados) {
    const ctx = document.getElementById('chartEmprestimosMes').getContext('2d');
    
    const labels = dados.map(d => formatarMesAno(d.mes));
    const quantidades = dados.map(d => d.quantidade);
    
    charts.emprestimosMes = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Empréstimos',
                data: quantidades,
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
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
}

// Gráfico: Custos de Manutenção por Mês
function criarGraficoCustosMes(dados) {
    const ctx = document.getElementById('chartCustosMes').getContext('2d');
    
    const labels = dados.map(d => formatarMesAno(d.mes));
    const custos = dados.map(d => d.custo);
    
    charts.custosMes = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Custo de Manutenção (R$)',
                data: custos,
                backgroundColor: 'rgba(245, 158, 11, 0.6)',
                borderColor: 'rgba(245, 158, 11, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'R$ ' + context.parsed.y.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value.toLocaleString('pt-BR');
                        }
                    }
                }
            }
        }
    });
}

// Gráfico: Tempo Médio por Departamento
function criarGraficoTempoDept(dados) {
    const ctx = document.getElementById('chartTempoDept').getContext('2d');
    
    const labels = dados.map(d => d.departamento);
    const tempos = dados.map(d => d.tempo_medio_dias);
    
    charts.tempoDept = new Chart(ctx, {
        type: 'horizontalBar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Tempo Médio (dias)',
                data: tempos,
                backgroundColor: 'rgba(16, 185, 129, 0.6)',
                borderColor: 'rgba(16, 185, 129, 1)',
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
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.parsed.x.toFixed(1) + ' dias';
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value + ' dias';
                        }
                    }
                }
            }
        }
    });
}

// Atualizar tabelas
function atualizarTabelas(data) {
    // Top 10 ROI
    atualizarTabelaROI('tabelaTopROI', data.roi.top_10);
    
    // Bottom 10 ROI
    atualizarTabelaROI('tabelaBottomROI', data.roi.bottom_10);
    
    // Equipamentos Problemáticos
    atualizarTabelaProblematicos(data.manutencoes.equipamentos_problematicos);
}

// Atualizar tabela de ROI
function atualizarTabelaROI(tabelaId, dados) {
    const tbody = document.querySelector(`#${tabelaId} tbody`);
    
    if (!dados || dados.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">Nenhum dado disponível</td></tr>';
        return;
    }
    
    tbody.innerHTML = dados.map(eq => `
        <tr>
            <td><strong>${eq.nome}</strong></td>
            <td>${eq.tipo}</td>
            <td>${formatarMoeda(eq.valor_aquisicao)}</td>
            <td>${formatarMoeda(eq.valor_residual)}</td>
            <td>${eq.dias_uso}</td>
            <td>${formatarMoeda(eq.custo_manutencao)}</td>
            <td class="${getClasseROI(eq.roi_percentual)}">${eq.roi_percentual}%</td>
        </tr>
    `).join('');
}

// Atualizar tabela de equipamentos problemáticos
function atualizarTabelaProblematicos(dados) {
    const tbody = document.querySelector('#tabelaProblematicos tbody');
    
    if (!dados || dados.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Nenhum equipamento problemático identificado</td></tr>';
        return;
    }
    
    tbody.innerHTML = dados.map(eq => `
        <tr>
            <td><strong>${eq.nome}</strong></td>
            <td>${eq.tipo}</td>
            <td>${eq.marca} ${eq.modelo}</td>
            <td>${eq.quantidade_manutencoes}</td>
            <td>${formatarMoeda(eq.custo_total)}</td>
        </tr>
    `).join('');
}

// Gerar insights automáticos
function gerarInsights(data) {
    const container = document.getElementById('insightsContainer');
    const insights = [];
    
    // Insight 1: Taxa de utilização
    if (data.utilizacao.taxa_utilizacao < 50) {
        insights.push({
            icon: '⚠️',
            title: 'Baixa Utilização de Equipamentos',
            description: `Apenas ${data.utilizacao.taxa_utilizacao}% dos equipamentos estão em uso. Considere redistribuir ou realocar equipamentos ociosos.`
        });
    } else if (data.utilizacao.taxa_utilizacao > 80) {
        insights.push({
            icon: '📈',
            title: 'Alta Demanda de Equipamentos',
            description: `Taxa de utilização de ${data.utilizacao.taxa_utilizacao}%. Pode ser necessário adquirir mais equipamentos para atender a demanda.`
        });
    }
    
    // Insight 2: Custos de manutenção
    const custoMedioPorEquipamento = data.manutencoes.custo_total / data.inventario.total_equipamentos;
    if (custoMedioPorEquipamento > 500) {
        insights.push({
            icon: '💸',
            title: 'Custos Elevados de Manutenção',
            description: `Custo médio de R$ ${custoMedioPorEquipamento.toFixed(2)} por equipamento. Avalie a substituição de equipamentos com alto custo de manutenção.`
        });
    }
    
    // Insight 3: ROI negativo
    const equipamentosROINegativo = data.roi.bottom_10.filter(eq => eq.roi_percentual < 0).length;
    if (equipamentosROINegativo > 0) {
        insights.push({
            icon: '📉',
            title: 'Equipamentos com ROI Negativo',
            description: `${equipamentosROINegativo} equipamentos com retorno negativo. Revise a necessidade destes ativos ou planeje substituição.`
        });
    }
    
    // Insight 4: Equipamentos problemáticos
    if (data.manutencoes.equipamentos_problematicos.length > 0) {
        const topProblematico = data.manutencoes.equipamentos_problematicos[0];
        insights.push({
            icon: '🔧',
            title: 'Equipamento Requer Atenção',
            description: `${topProblematico.nome} possui ${topProblematico.quantidade_manutencoes} manutenções (R$ ${topProblematico.custo_total.toFixed(2)}). Considere substituição.`
        });
    }
    
    // Insight 5: Departamento com maior investimento
    if (data.inventario.equipamentos_por_departamento.length > 0) {
        const topDept = data.inventario.equipamentos_por_departamento[0];
        insights.push({
            icon: '💼',
            title: 'Maior Investimento por Departamento',
            description: `${topDept.departamento} concentra ${formatarMoeda(topDept.valor_total)} em equipamentos (${topDept.quantidade} unidades).`
        });
    }
    
    // Renderizar insights
    if (insights.length === 0) {
        container.innerHTML = '<p class="loading-text">✅ Todos os indicadores estão dentro dos parâmetros esperados.</p>';
    } else {
        container.innerHTML = insights.map(insight => `
            <div class="insight-item">
                <strong>${insight.icon} ${insight.title}</strong>
                <p>${insight.description}</p>
            </div>
        `).join('');
    }
}

// Funções auxiliares
function formatarMoeda(valor) {
    return 'R$ ' + valor.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function formatarMesAno(mesAno) {
    const [ano, mes] = mesAno.split('-');
    const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    return `${meses[parseInt(mes) - 1]}/${ano}`;
}

function getClasseROI(roi) {
    if (roi >= 0) return 'roi-positive';
    if (roi >= -10) return 'roi-neutral';
    return 'roi-negative';
}

function mostrarLoading(mostrar) {
    const container = document.querySelector('.dashboard-content');
    if (mostrar) {
        container.classList.add('loading');
    } else {
        container.classList.remove('loading');
    }
}

function atualizarUltimaAtualizacao() {
    const agora = new Date();
    const texto = `Última atualização: ${agora.toLocaleString('pt-BR')}`;
    document.getElementById('ultimaAtualizacao').textContent = texto;
}

function mostrarErro(mensagem) {
    alert(mensagem);
}
