"""
Serviço de envio de e-mails para notificações do sistema de inventário.
"""
from flask import render_template_string
from flask_mail import Message, Mail
from datetime import datetime, date, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verificar_e_enviar_notificacoes(app):
    """
    Verifica empréstimos e envia notificações por e-mail e push.
    Chamado diariamente pelo scheduler.
    """
    with app.app_context():
        from app.models import Emprestimo, Usuario, db
        from app.push_service import PushNotificationService
        
        if not app.config.get('MAIL_ENABLED'):
            logger.info('Sistema de e-mail desabilitado. Configure MAIL_ENABLED=true para habilitar.')
        
        hoje = date.today()
        
        # Buscar empréstimos ativos
        emprestimos_ativos = Emprestimo.query.filter_by(status='Ativo').all()
        
        emails_enviados = 0
        push_enviadas = 0
        
        for emprestimo in emprestimos_ativos:
            # Calcular dias até devolução
            if emprestimo.data_devolucao_prevista:
                dias_ate_devolucao = (emprestimo.data_devolucao_prevista - hoje).days
                
                # Empréstimo atrasado
                if dias_ate_devolucao < 0:
                    dias_atraso = abs(dias_ate_devolucao)
                    
                    # Enviar e-mail se disponível
                    if app.config.get('MAIL_ENABLED') and emprestimo.email_responsavel:
                        enviar_email_atraso(app, emprestimo, dias_atraso)
                        emails_enviados += 1
                    
                    # Enviar push notification
                    usuario = Usuario.query.filter_by(email=emprestimo.email_responsavel).first()
                    if usuario:
                        count = PushNotificationService.send_to_user(
                            usuario_id=usuario.id,
                            title='🚨 Devolução Atrasada',
                            body=f'Equipamento {emprestimo.equipamento.nome} está atrasado há {dias_atraso} dia(s)',
                            url='/',
                            tag=f'atraso-{emprestimo.id}'
                        )
                        push_enviadas += count
                
                # Devolução próxima (3 dias antes)
                elif dias_ate_devolucao <= 3 and dias_ate_devolucao > 0:
                    # Enviar e-mail se disponível
                    if app.config.get('MAIL_ENABLED') and emprestimo.email_responsavel:
                        enviar_email_lembrete(app, emprestimo, dias_ate_devolucao)
                        emails_enviados += 1
                    
                    # Enviar push notification
                    usuario = Usuario.query.filter_by(email=emprestimo.email_responsavel).first()
                    if usuario:
                        count = PushNotificationService.send_to_user(
                            usuario_id=usuario.id,
                            title='⏰ Lembrete de Devolução',
                            body=f'Equipamento {emprestimo.equipamento.nome} deve ser devolvido em {dias_ate_devolucao} dia(s)',
                            url='/',
                            tag=f'lembrete-{emprestimo.id}'
                        )
                        push_enviadas += count
        
        logger.info(f'Verificação de notificações concluída. {emails_enviados} e-mails e {push_enviadas} push notifications enviadas.')


def enviar_email_lembrete(app, emprestimo, dias_restantes):
    """
    Envia e-mail de lembrete sobre devolução próxima.
    """
    try:
        mail = Mail(app)
        
        assunto = f'⏰ Lembrete: Devolução de Equipamento em {dias_restantes} dia(s)'
        
        corpo_html = render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #EF7D2D 0%, #D96B1F 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }
        .info-box { background: white; padding: 15px; border-left: 4px solid #EF7D2D; margin: 20px 0; border-radius: 4px; }
        .footer { text-align: center; color: #666; font-size: 12px; margin-top: 20px; }
        .button { display: inline-block; background: #EF7D2D; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin-top: 15px; }
        .alert { color: #f59e0b; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🔔 Sistema de Inventário TI</h2>
        </div>
        <div class="content">
            <h3>Olá, {{ emprestimo.responsavel }}!</h3>
            
            <p>Este é um lembrete amigável sobre a devolução de equipamento:</p>
            
            <div class="info-box">
                <p><strong>📦 Equipamento:</strong> {{ emprestimo.equipamento.nome }}</p>
                <p><strong>🏷️ Tipo:</strong> {{ emprestimo.equipamento.tipo }}</p>
                <p><strong>🔢 Nº Série:</strong> {{ emprestimo.equipamento.numero_serie }}</p>
                <p><strong>📅 Data do Empréstimo:</strong> {{ emprestimo.data_emprestimo.strftime('%d/%m/%Y') }}</p>
                <p class="alert"><strong>⏰ Devolução Prevista:</strong> {{ emprestimo.data_devolucao_prevista.strftime('%d/%m/%Y') }} (em {{ dias_restantes }} dia{% if dias_restantes > 1 %}s{% endif %})</p>
            </div>
            
            <p>Por favor, providencie a devolução do equipamento na data prevista.</p>
            
            <p>Se precisar de uma prorrogação, entre em contato com o departamento de TI.</p>
            
            <div class="footer">
                <p>Este é um e-mail automático. Por favor, não responda.</p>
                <p>Sistema de Inventário de Equipamentos TI - TrueSource</p>
            </div>
        </div>
    </div>
</body>
</html>
        ''', emprestimo=emprestimo, dias_restantes=dias_restantes)
        
        msg = Message(
            subject=assunto,
            recipients=[emprestimo.email_responsavel],
            html=corpo_html
        )
        
        mail.send(msg)
        logger.info(f'E-mail de lembrete enviado para {emprestimo.email_responsavel} - Equipamento: {emprestimo.equipamento.nome}')
        
    except Exception as e:
        logger.error(f'Erro ao enviar e-mail de lembrete: {str(e)}')


def enviar_email_atraso(app, emprestimo, dias_atraso):
    """
    Envia e-mail notificando sobre empréstimo atrasado.
    """
    try:
        mail = Mail(app)
        
        assunto = f'🚨 URGENTE: Devolução de Equipamento Atrasada ({dias_atraso} dia(s))'
        
        corpo_html = render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }
        .info-box { background: white; padding: 15px; border-left: 4px solid #ef4444; margin: 20px 0; border-radius: 4px; }
        .footer { text-align: center; color: #666; font-size: 12px; margin-top: 20px; }
        .alert { color: #ef4444; font-weight: bold; font-size: 18px; }
        .warning-box { background: #fee2e2; border: 2px solid #ef4444; padding: 15px; border-radius: 4px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🚨 Sistema de Inventário TI - ALERTA</h2>
        </div>
        <div class="content">
            <h3>Atenção, {{ emprestimo.responsavel }}!</h3>
            
            <div class="warning-box">
                <p class="alert">⚠️ DEVOLUÇÃO ATRASADA EM {{ dias_atraso }} DIA{% if dias_atraso > 1 %}S{% endif %}</p>
            </div>
            
            <p>O equipamento abaixo deveria ter sido devolvido e está <strong>atrasado</strong>:</p>
            
            <div class="info-box">
                <p><strong>📦 Equipamento:</strong> {{ emprestimo.equipamento.nome }}</p>
                <p><strong>🏷️ Tipo:</strong> {{ emprestimo.equipamento.tipo }}</p>
                <p><strong>🔢 Nº Série:</strong> {{ emprestimo.equipamento.numero_serie }}</p>
                <p><strong>📅 Data do Empréstimo:</strong> {{ emprestimo.data_emprestimo.strftime('%d/%m/%Y') }}</p>
                <p style="color: #ef4444;"><strong>⏰ Devolução Prevista:</strong> {{ emprestimo.data_devolucao_prevista.strftime('%d/%m/%Y') }}</p>
                <p style="color: #ef4444;"><strong>📌 Status:</strong> Atrasado há {{ dias_atraso }} dia{% if dias_atraso > 1 %}s{% endif %}</p>
            </div>
            
            <p><strong>Por favor, providencie a devolução URGENTE do equipamento.</strong></p>
            
            <p>Entre em contato com o departamento de TI imediatamente caso haja algum problema.</p>
            
            <div class="footer">
                <p>Este é um e-mail automático. Por favor, não responda.</p>
                <p>Sistema de Inventário de Equipamentos TI - TrueSource</p>
            </div>
        </div>
    </div>
</body>
</html>
        ''', emprestimo=emprestimo, dias_atraso=dias_atraso)
        
        msg = Message(
            subject=assunto,
            recipients=[emprestimo.email_responsavel],
            html=corpo_html
        )
        
        mail.send(msg)
        logger.info(f'E-mail de atraso enviado para {emprestimo.email_responsavel} - Equipamento: {emprestimo.equipamento.nome} ({dias_atraso} dias)')
        
    except Exception as e:
        logger.error(f'Erro ao enviar e-mail de atraso: {str(e)}')


def enviar_email_confirmacao_emprestimo(app, emprestimo):
    """
    Envia e-mail e push notification de confirmação quando um empréstimo é registrado.
    """
    # Enviar push notification
    from app.models import Usuario
    from app.push_service import PushNotificationService
    
    if emprestimo.email_responsavel:
        usuario = Usuario.query.filter_by(email=emprestimo.email_responsavel).first()
        if usuario:
            PushNotificationService.send_to_user(
                usuario_id=usuario.id,
                title='✅ Empréstimo Registrado',
                body=f'Equipamento {emprestimo.equipamento.nome} emprestado com sucesso',
                url='/',
                tag=f'emprestimo-{emprestimo.id}'
            )
    
    # Enviar e-mail
    if not app.config.get('MAIL_ENABLED') or not emprestimo.email_responsavel:
        return
    
    try:
        mail = Mail(app)
        
        assunto = f'✅ Confirmação de Empréstimo de Equipamento'
        
        corpo_html = render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }
        .info-box { background: white; padding: 15px; border-left: 4px solid #10b981; margin: 20px 0; border-radius: 4px; }
        .footer { text-align: center; color: #666; font-size: 12px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>✅ Sistema de Inventário TI</h2>
        </div>
        <div class="content">
            <h3>Olá, {{ emprestimo.responsavel }}!</h3>
            
            <p>Seu empréstimo de equipamento foi registrado com sucesso:</p>
            
            <div class="info-box">
                <p><strong>📦 Equipamento:</strong> {{ emprestimo.equipamento.nome }}</p>
                <p><strong>🏷️ Tipo:</strong> {{ emprestimo.equipamento.tipo }}</p>
                <p><strong>🔢 Nº Série:</strong> {{ emprestimo.equipamento.numero_serie }}</p>
                <p><strong>📅 Data do Empréstimo:</strong> {{ emprestimo.data_emprestimo.strftime('%d/%m/%Y às %H:%M') }}</p>
                {% if emprestimo.data_devolucao_prevista %}
                <p><strong>⏰ Devolução Prevista:</strong> {{ emprestimo.data_devolucao_prevista.strftime('%d/%m/%Y') }}</p>
                {% endif %}
                <p><strong>🏢 Departamento:</strong> {{ emprestimo.departamento }}</p>
            </div>
            
            {% if emprestimo.observacoes %}
            <p><strong>📝 Observações:</strong> {{ emprestimo.observacoes }}</p>
            {% endif %}
            
            <p>Você receberá lembretes automáticos sobre a devolução.</p>
            
            <div class="footer">
                <p>Este é um e-mail automático. Por favor, não responda.</p>
                <p>Sistema de Inventário de Equipamentos TI - TrueSource</p>
            </div>
        </div>
    </div>
</body>
</html>
        ''', emprestimo=emprestimo)
        
        msg = Message(
            subject=assunto,
            recipients=[emprestimo.email_responsavel],
            html=corpo_html
        )
        
        mail.send(msg)
        logger.info(f'E-mail de confirmação enviado para {emprestimo.email_responsavel}')
        
    except Exception as e:
        logger.error(f'Erro ao enviar e-mail de confirmação: {str(e)}')


def enviar_email_confirmacao_devolucao(app, emprestimo):
    """
    Envia e-mail e push notification de confirmação quando um equipamento é devolvido.
    """
    # Enviar push notification
    from app.models import Usuario
    from app.push_service import PushNotificationService
    
    if emprestimo.email_responsavel:
        usuario = Usuario.query.filter_by(email=emprestimo.email_responsavel).first()
        if usuario:
            PushNotificationService.send_to_user(
                usuario_id=usuario.id,
                title='✅ Devolução Registrada',
                body=f'Devolução do equipamento {emprestimo.equipamento.nome} confirmada',
                url='/',
                tag=f'devolucao-{emprestimo.id}'
            )
    
    # Enviar e-mail
    if not app.config.get('MAIL_ENABLED') or not emprestimo.email_responsavel:
        return
    
    try:
        mail = Mail(app)
        
        # Calcular duração do empréstimo
        duracao = (emprestimo.data_devolucao_real.date() - emprestimo.data_emprestimo.date()).days
        
        assunto = f'✅ Confirmação de Devolução de Equipamento'
        
        corpo_html = render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }
        .info-box { background: white; padding: 15px; border-left: 4px solid #10b981; margin: 20px 0; border-radius: 4px; }
        .footer { text-align: center; color: #666; font-size: 12px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>✅ Sistema de Inventário TI</h2>
        </div>
        <div class="content">
            <h3>Olá, {{ emprestimo.responsavel }}!</h3>
            
            <p>A devolução do equipamento foi registrada com sucesso:</p>
            
            <div class="info-box">
                <p><strong>📦 Equipamento:</strong> {{ emprestimo.equipamento.nome }}</p>
                <p><strong>🏷️ Tipo:</strong> {{ emprestimo.equipamento.tipo }}</p>
                <p><strong>🔢 Nº Série:</strong> {{ emprestimo.equipamento.numero_serie }}</p>
                <p><strong>📅 Data do Empréstimo:</strong> {{ emprestimo.data_emprestimo.strftime('%d/%m/%Y') }}</p>
                <p><strong>📅 Data da Devolução:</strong> {{ emprestimo.data_devolucao_real.strftime('%d/%m/%Y às %H:%M') }}</p>
                <p><strong>⏱️ Duração:</strong> {{ duracao }} dia{% if duracao != 1 %}s{% endif %}</p>
            </div>
            
            <p>Obrigado por utilizar nossos equipamentos de forma responsável!</p>
            
            <div class="footer">
                <p>Este é um e-mail automático. Por favor, não responda.</p>
                <p>Sistema de Inventário de Equipamentos TI - TrueSource</p>
            </div>
        </div>
    </div>
</body>
</html>
        ''', emprestimo=emprestimo, duracao=duracao)
        
        msg = Message(
            subject=assunto,
            recipients=[emprestimo.email_responsavel],
            html=corpo_html
        )
        
        mail.send(msg)
        logger.info(f'E-mail de devolução enviado para {emprestimo.email_responsavel}')
        
    except Exception as e:
        logger.error(f'Erro ao enviar e-mail de devolução: {str(e)}')
