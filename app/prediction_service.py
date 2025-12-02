"""
Serviço de Previsão de Demanda com Machine Learning
Análise preditiva para necessidades de compra de equipamentos
"""

from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import pandas as pd
from app.models import Equipamento, Emprestimo
from sqlalchemy import func


class PredictionService:
    """Serviço de análise preditiva para demanda de equipamentos"""
    
    def __init__(self):
        self.prediction_horizon = 90  # Previsão para próximos 90 dias
        self.min_data_points = 3  # Mínimo de pontos para fazer previsão
        
    def analisar_demanda_por_tipo(self):
        """
        Analisa a demanda histórica e faz previsões por tipo de equipamento
        
        Returns:
            dict: Previsões e análises por tipo de equipamento
        """
        try:
            # Buscar todos os empréstimos
            emprestimos = Emprestimo.query.all()
            
            if not emprestimos:
                return self._resposta_sem_dados()
            
            # Agrupar por tipo de equipamento
            dados_por_tipo = defaultdict(list)
            
            for emp in emprestimos:
                if emp.equipamento and emp.equipamento.tipo:
                    tipo = emp.equipamento.tipo
                    mes = emp.data_emprestimo.strftime('%Y-%m')
                    dados_por_tipo[tipo].append({
                        'mes': mes,
                        'data': emp.data_emprestimo
                    })
            
            # Processar previsões para cada tipo
            previsoes = []
            
            for tipo, registros in dados_por_tipo.items():
                previsao = self._prever_demanda_tipo(tipo, registros)
                if previsao:
                    previsoes.append(previsao)
            
            # Ordenar por prioridade (taxa de crescimento)
            previsoes.sort(key=lambda x: x['taxa_crescimento'], reverse=True)
            
            return {
                'sucesso': True,
                'previsoes': previsoes,
                'horizonte_dias': self.prediction_horizon,
                'data_analise': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e),
                'previsoes': []
            }
    
    def _prever_demanda_tipo(self, tipo, registros):
        """
        Faz previsão de demanda para um tipo específico de equipamento
        
        Args:
            tipo (str): Tipo de equipamento
            registros (list): Lista de registros de empréstimos
            
        Returns:
            dict: Previsão detalhada ou None se não houver dados suficientes
        """
        if len(registros) < self.min_data_points:
            return None
        
        # Contar empréstimos por mês
        emprestimos_por_mes = defaultdict(int)
        for reg in registros:
            emprestimos_por_mes[reg['mes']] += 1
        
        # Ordenar por data
        meses_ordenados = sorted(emprestimos_por_mes.keys())
        
        if len(meses_ordenados) < self.min_data_points:
            return None
        
        # Preparar dados para regressão
        X = np.array(range(len(meses_ordenados))).reshape(-1, 1)
        y = np.array([emprestimos_por_mes[mes] for mes in meses_ordenados])
        
        # Regressão linear para tendência
        modelo = LinearRegression()
        modelo.fit(X, y)
        
        # Prever próximos 3 meses
        proximos_meses = 3
        X_futuro = np.array(range(len(meses_ordenados), len(meses_ordenados) + proximos_meses)).reshape(-1, 1)
        y_futuro = modelo.predict(X_futuro)
        
        # Calcular métricas
        media_atual = np.mean(y[-3:]) if len(y) >= 3 else np.mean(y)
        previsao_media = np.mean(y_futuro)
        taxa_crescimento = ((previsao_media - media_atual) / media_atual * 100) if media_atual > 0 else 0
        
        # Quantidade atual em estoque
        qtd_estoque = Equipamento.query.filter_by(
            tipo=tipo,
            status='Estoque'
        ).count()
        
        # Quantidade total
        qtd_total = Equipamento.query.filter_by(tipo=tipo).count()
        
        # Taxa de utilização média (últimos 30 dias)
        data_limite = datetime.now() - timedelta(days=30)
        emprestimos_recentes = Emprestimo.query.join(Equipamento).filter(
            Equipamento.tipo == tipo,
            Emprestimo.data_emprestimo >= data_limite
        ).count()
        
        taxa_utilizacao = (emprestimos_recentes / qtd_total * 100) if qtd_total > 0 else 0
        
        # Determinar recomendação
        recomendacao = self._gerar_recomendacao(
            tipo=tipo,
            taxa_crescimento=taxa_crescimento,
            taxa_utilizacao=taxa_utilizacao,
            qtd_estoque=qtd_estoque,
            qtd_total=qtd_total,
            previsao_demanda=previsao_media
        )
        
        return {
            'tipo': tipo,
            'qtd_total': int(qtd_total),
            'qtd_estoque': int(qtd_estoque),
            'emprestimos_mes_atual': int(y[-1]) if len(y) > 0 else 0,
            'media_mensal': round(float(media_atual), 1),
            'previsao_proximos_meses': [round(float(v), 1) for v in y_futuro],
            'taxa_crescimento': round(float(taxa_crescimento), 1),
            'taxa_utilizacao': round(float(taxa_utilizacao), 1),
            'tendencia': 'crescente' if taxa_crescimento > 5 else 'estavel' if taxa_crescimento > -5 else 'decrescente',
            'recomendacao': recomendacao,
            'historico_meses': [
                {
                    'mes': mes,
                    'quantidade': int(emprestimos_por_mes[mes])
                }
                for mes in meses_ordenados[-6:]  # Últimos 6 meses
            ]
        }
    
    def _gerar_recomendacao(self, tipo, taxa_crescimento, taxa_utilizacao, 
                           qtd_estoque, qtd_total, previsao_demanda):
        """
        Gera recomendação de compra baseada em múltiplos fatores
        
        Returns:
            dict: Recomendação com ação, prioridade e justificativa
        """
        prioridade = 'baixa'
        acao = 'monitorar'
        qtd_sugerida = 0
        justificativas = []
        
        # Critério 1: Taxa de crescimento
        if taxa_crescimento > 20:
            prioridade = 'alta'
            acao = 'comprar'
            justificativas.append(f'Crescimento acelerado de {taxa_crescimento:.0f}%')
            qtd_sugerida = max(2, int(qtd_total * 0.3))
        elif taxa_crescimento > 10:
            prioridade = 'media'
            acao = 'planejar'
            justificativas.append(f'Crescimento moderado de {taxa_crescimento:.0f}%')
            qtd_sugerida = max(1, int(qtd_total * 0.2))
        
        # Critério 2: Taxa de utilização
        if taxa_utilizacao > 80:
            if prioridade == 'baixa':
                prioridade = 'alta'
            acao = 'comprar'
            justificativas.append(f'Alta utilização ({taxa_utilizacao:.0f}%)')
            qtd_sugerida = max(qtd_sugerida, int(qtd_total * 0.25))
        elif taxa_utilizacao > 60:
            if prioridade == 'baixa':
                prioridade = 'media'
            if acao == 'monitorar':
                acao = 'planejar'
            justificativas.append(f'Utilização elevada ({taxa_utilizacao:.0f}%)')
        
        # Critério 3: Estoque baixo
        proporcao_estoque = (qtd_estoque / qtd_total * 100) if qtd_total > 0 else 0
        if proporcao_estoque < 20:
            if prioridade != 'alta':
                prioridade = 'alta' if proporcao_estoque < 10 else 'media'
            acao = 'comprar'
            justificativas.append(f'Estoque crítico ({proporcao_estoque:.0f}% disponível)')
            qtd_sugerida = max(qtd_sugerida, max(2, int(qtd_total * 0.3)))
        elif proporcao_estoque < 30:
            if prioridade == 'baixa':
                prioridade = 'media'
            if acao == 'monitorar':
                acao = 'planejar'
            justificativas.append(f'Estoque reduzido ({proporcao_estoque:.0f}% disponível)')
        
        # Critério 4: Previsão de demanda futura
        if previsao_demanda > qtd_estoque:
            justificativas.append(f'Demanda prevista ({previsao_demanda:.0f}) supera estoque')
            if prioridade == 'baixa':
                prioridade = 'media'
            if acao == 'monitorar':
                acao = 'planejar'
            qtd_sugerida = max(qtd_sugerida, int(previsao_demanda - qtd_estoque) + 1)
        
        # Se não há problemas
        if not justificativas:
            justificativas.append('Estoque adequado para demanda atual')
        
        # Mensagem de ação
        mensagens_acao = {
            'comprar': f'Comprar {qtd_sugerida} unidade(s) imediatamente',
            'planejar': f'Planejar compra de {qtd_sugerida} unidade(s) para próximo trimestre',
            'monitorar': 'Continuar monitorando tendências'
        }
        
        return {
            'acao': acao,
            'prioridade': prioridade,
            'qtd_sugerida': int(qtd_sugerida),
            'mensagem': mensagens_acao[acao],
            'justificativas': justificativas
        }
    
    def _resposta_sem_dados(self):
        """Retorna resposta padrão quando não há dados suficientes"""
        return {
            'sucesso': True,
            'previsoes': [],
            'mensagem': 'Dados insuficientes para análise preditiva. Registre mais empréstimos.',
            'horizonte_dias': self.prediction_horizon,
            'data_analise': datetime.now().isoformat()
        }
    
    def analisar_sazonalidade(self):
        """
        Analisa padrões sazonais nos empréstimos
        
        Returns:
            dict: Análise de sazonalidade por mês do ano
        """
        try:
            emprestimos = Emprestimo.query.all()
            
            if not emprestimos:
                return {'sucesso': False, 'mensagem': 'Sem dados suficientes'}
            
            # Agrupar por mês do ano (1-12)
            por_mes = defaultdict(list)
            for emp in emprestimos:
                mes_ano = emp.data_emprestimo.month
                por_mes[mes_ano].append(emp)
            
            # Calcular média por mês
            sazonalidade = []
            for mes in range(1, 13):
                qtd = len(por_mes.get(mes, []))
                sazonalidade.append({
                    'mes': mes,
                    'nome_mes': [
                        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
                    ][mes - 1],
                    'quantidade': qtd
                })
            
            # Identificar meses de pico e baixa
            quantidades = [s['quantidade'] for s in sazonalidade]
            media = np.mean(quantidades)
            pico = max(quantidades)
            baixa = min(quantidades)
            
            meses_pico = [s['nome_mes'] for s in sazonalidade if s['quantidade'] == pico]
            meses_baixa = [s['nome_mes'] for s in sazonalidade if s['quantidade'] == baixa]
            
            return {
                'sucesso': True,
                'sazonalidade': sazonalidade,
                'media': round(float(media), 1),
                'pico': int(pico),
                'baixa': int(baixa),
                'meses_pico': meses_pico,
                'meses_baixa': meses_baixa,
                'insights': self._gerar_insights_sazonalidade(sazonalidade, media)
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def _gerar_insights_sazonalidade(self, sazonalidade, media):
        """Gera insights sobre padrões sazonais"""
        insights = []
        
        for s in sazonalidade:
            if s['quantidade'] > media * 1.5:
                insights.append(f"{s['nome_mes']}: Alta demanda - prepare estoque antecipadamente")
            elif s['quantidade'] < media * 0.5 and s['quantidade'] > 0:
                insights.append(f"{s['nome_mes']}: Baixa demanda - período ideal para manutenções")
        
        return insights if insights else ['Demanda distribuída uniformemente ao longo do ano']


# Instância global do serviço
prediction_service = PredictionService()
