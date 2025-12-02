"""
Serviço de integração com WhatsApp Business API
Suporta múltiplos provedores: Twilio, MessageBird, e Meta WhatsApp Business API
"""
import requests
import os
import logging
from flask import current_app
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Serviço para envio de mensagens via WhatsApp Business API"""
    
    @staticmethod
    def _get_config_value(key: str, default: str = '') -> str:
        """
        Obtém valor de configuração, verificando primeiro environment e depois config file
        """
        # Tenta pegar do environment primeiro
        env_value = os.environ.get(key)
        if env_value:
            return env_value
        
        # Se não encontrou, tenta do config_manager
        try:
            from app.config_manager import ConfigManager
            config = ConfigManager.get_config()
            return config.get(key, default)
        except:
            return default
    
    @staticmethod
    def get_provider():
        """Retorna o provedor configurado: twilio, messagebird ou meta"""
        return WhatsAppService._get_config_value('WHATSAPP_PROVIDER', 'twilio').lower()
    
    @staticmethod
    def is_enabled():
        """Verifica se o WhatsApp está habilitado"""
        return WhatsAppService._get_config_value('WHATSAPP_ENABLED', 'false').lower() == 'true'
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """
        Formata número de telefone para o formato internacional
        Remove caracteres especiais e adiciona código do país se necessário
        """
        if not phone:
            return ''
        
        # Remove caracteres especiais
        phone = ''.join(filter(str.isdigit, phone))
        
        # Se não começa com código do país, adiciona +55 (Brasil)
        if not phone.startswith('55'):
            phone = '55' + phone
        
        return '+' + phone
    
    @staticmethod
    def send_message_twilio(to: str, message: str) -> dict:
        """
        Envia mensagem via Twilio WhatsApp API
        
        Returns:
            dict: {'success': bool, 'message': str, 'details': str (opcional)}
        """
        try:
            account_sid = WhatsAppService._get_config_value('TWILIO_ACCOUNT_SID')
            auth_token = WhatsAppService._get_config_value('TWILIO_AUTH_TOKEN')
            from_number = WhatsAppService._get_config_value('TWILIO_WHATSAPP_NUMBER')
            
            if not all([account_sid, auth_token, from_number]):
                logger.error('Credenciais Twilio não configuradas')
                return {
                    'success': False,
                    'message': 'Credenciais Twilio incompletas. Verifique Account SID, Auth Token e Número.',
                    'details': f'SID: {"✓" if account_sid else "✗"}, Token: {"✓" if auth_token else "✗"}, Número: {"✗" if not from_number else from_number}'
                }
            
            # Valida código do país
            if not from_number.startswith('+'):
                from_number = '+' + from_number
            
            # Verifica se é o número do sandbox do Twilio
            is_sandbox = from_number.startswith('+1415')  # Twilio sandbox number
            
            if not is_sandbox:
                # Alerta se parece código errado (ex: +27 ao invés de +55)
                country_code = from_number[1:3]
                if country_code not in ['14', '55']:  # Números USA ou Brasil
                    logger.warning(f'Código do país suspeito: {country_code}. Brasil deve usar +55')
                
                # Aviso importante sobre número não ser sandbox
                logger.warning(f'Usando número próprio {from_number}. Certifique-se de que está aprovado pelo WhatsApp Business API.')
            
            url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json'
            
            data = {
                'From': f'whatsapp:{from_number}',
                'To': f'whatsapp:{to}',
                'Body': message
            }
            
            logger.info(f'Enviando WhatsApp Twilio: De {from_number} para {to}')
            
            response = requests.post(
                url,
                data=data,
                auth=(account_sid, auth_token)
            )
            
            if response.status_code == 201:
                logger.info(f'WhatsApp enviado via Twilio para {to}')
                return {'success': True, 'message': f'Mensagem enviada com sucesso para {to}!'}
            else:
                error_msg = response.text
                logger.error(f'Erro Twilio: {response.status_code} - {error_msg}')
                
                # Parse do erro do Twilio
                try:
                    import json
                    error_json = json.loads(error_msg)
                    error_detail = error_json.get('message', error_msg)
                    
                    # Mensagem específica para erro de Channel não encontrado
                    if 'Channel' in error_detail and 'From address' in error_detail:
                        error_detail = (
                            f"❌ Número {from_number} não está registrado no Twilio.\n\n"
                            "📋 Soluções:\n"
                            "1. Para TESTES: Use o Twilio Sandbox (+14155238886)\n"
                            "   • Acesse: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn\n"
                            "   • Envie mensagem do seu WhatsApp para ativar\n\n"
                            "2. Para PRODUÇÃO: Configure um número próprio\n"
                            "   • Vá em: Messaging > Try it out > Send a WhatsApp message\n"
                            "   • Siga o processo de aprovação do WhatsApp Business"
                        )
                except:
                    error_detail = error_msg
                
                return {
                    'success': False,
                    'message': f'Erro ao enviar via Twilio (código {response.status_code})',
                    'details': error_detail
                }
                
        except Exception as e:
            logger.error(f'Erro ao enviar WhatsApp via Twilio: {str(e)}')
            return {
                'success': False,
                'message': f'Erro de sistema: {str(e)}',
                'details': 'Verifique os logs do servidor'
            }
    
    @staticmethod
    def send_message_messagebird(to: str, message: str) -> bool:
        """Envia mensagem via MessageBird WhatsApp API"""
        try:
            api_key = WhatsAppService._get_config_value('MESSAGEBIRD_API_KEY')
            channel_id = WhatsAppService._get_config_value('MESSAGEBIRD_CHANNEL_ID')
            
            if not all([api_key, channel_id]):
                logger.error('Credenciais MessageBird não configuradas')
                return False
            
            url = 'https://conversations.messagebird.com/v1/send'
            
            headers = {
                'Authorization': f'AccessKey {api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'to': to,
                'from': channel_id,
                'type': 'text',
                'content': {
                    'text': message
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                logger.info(f'WhatsApp enviado via MessageBird para {to}')
                return True
            else:
                logger.error(f'Erro MessageBird: {response.status_code} - {response.text}')
                return False
                
        except Exception as e:
            logger.error(f'Erro ao enviar WhatsApp via MessageBird: {str(e)}')
            return False
    
    @staticmethod
    def send_message_meta(to: str, message: str) -> bool:
        """Envia mensagem via Meta (Facebook) WhatsApp Business API"""
        try:
            access_token = WhatsAppService._get_config_value('META_ACCESS_TOKEN')
            phone_number_id = WhatsAppService._get_config_value('META_PHONE_NUMBER_ID')
            
            if not all([access_token, phone_number_id]):
                logger.error('Credenciais Meta WhatsApp não configuradas')
                return False
            
            url = f'https://graph.facebook.com/v18.0/{phone_number_id}/messages'
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'messaging_product': 'whatsapp',
                'to': to,
                'type': 'text',
                'text': {
                    'body': message
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                logger.info(f'WhatsApp enviado via Meta para {to}')
                return True
            else:
                logger.error(f'Erro Meta: {response.status_code} - {response.text}')
                return False
                
        except Exception as e:
            logger.error(f'Erro ao enviar WhatsApp via Meta: {str(e)}')
            return False
    
    @staticmethod
    def send_message(to: str, message: str) -> bool:
        """
        Envia mensagem via WhatsApp usando o provedor configurado
        
        Args:
            to: Número de telefone no formato internacional (+5511999999999)
            message: Texto da mensagem
            
        Returns:
            bool: True se enviado com sucesso (retrocompatibilidade)
        """
        result = WhatsAppService.send_message_detailed(to, message)
        return result['success'] if isinstance(result, dict) else result
    
    @staticmethod
    def send_message_detailed(to: str, message: str) -> dict:
        """
        Envia mensagem via WhatsApp usando o provedor configurado (versão com detalhes)
        
        Args:
            to: Número de telefone no formato internacional (+5511999999999)
            message: Texto da mensagem
            
        Returns:
            dict: {'success': bool, 'message': str, 'details': str (opcional)}
        """
        if not WhatsAppService.is_enabled():
            logger.info('WhatsApp desabilitado')
            return {'success': False, 'message': 'WhatsApp não está habilitado'}
        
        # Formata o número
        formatted_phone = WhatsAppService.format_phone(to)
        
        if not formatted_phone:
            logger.error('Número de telefone inválido')
            return {'success': False, 'message': 'Número de telefone inválido'}
        
        # Determina o provedor e envia
        provider = WhatsAppService.get_provider()
        
        if provider == 'twilio':
            return WhatsAppService.send_message_twilio(formatted_phone, message)
        elif provider == 'messagebird':
            result = WhatsAppService.send_message_messagebird(formatted_phone, message)
            return {'success': result, 'message': 'Enviado com sucesso' if result else 'Erro ao enviar'}
        elif provider == 'meta':
            result = WhatsAppService.send_message_meta(formatted_phone, message)
            return {'success': result, 'message': 'Enviado com sucesso' if result else 'Erro ao enviar'}
        else:
            logger.error(f'Provedor desconhecido: {provider}')
            return {'success': False, 'message': f'Provedor desconhecido: {provider}'}
    
    @staticmethod
    def send_loan_confirmation(emprestimo) -> bool:
        """Envia confirmação de empréstimo via WhatsApp"""
        if not emprestimo.telefone_responsavel:
            return False
        
        message = f"""
✅ *Empréstimo Confirmado - Inventário TI*

📦 *Equipamento:* {emprestimo.equipamento.nome}
🏷️ *Tipo:* {emprestimo.equipamento.tipo}
🔢 *Nº Série:* {emprestimo.equipamento.numero_serie}

👤 *Responsável:* {emprestimo.responsavel}
🏢 *Departamento:* {emprestimo.departamento}

📅 *Data:* {emprestimo.data_emprestimo.strftime('%d/%m/%Y às %H:%M')}
"""
        
        if emprestimo.data_devolucao_prevista:
            message += f"⏰ *Devolução prevista:* {emprestimo.data_devolucao_prevista.strftime('%d/%m/%Y')}\n"
        
        message += "\nVocê receberá lembretes automáticos sobre a devolução."
        
        return WhatsAppService.send_message(
            emprestimo.telefone_responsavel,
            message
        )
    
    @staticmethod
    def send_return_confirmation(emprestimo) -> bool:
        """Envia confirmação de devolução via WhatsApp"""
        if not emprestimo.telefone_responsavel:
            return False
        
        duracao = (emprestimo.data_devolucao_real.date() - emprestimo.data_emprestimo.date()).days
        
        message = f"""
✅ *Devolução Confirmada - Inventário TI*

📦 *Equipamento:* {emprestimo.equipamento.nome}
🏷️ *Tipo:* {emprestimo.equipamento.tipo}

👤 *Responsável:* {emprestimo.responsavel}

📅 *Emprestado em:* {emprestimo.data_emprestimo.strftime('%d/%m/%Y')}
📅 *Devolvido em:* {emprestimo.data_devolucao_real.strftime('%d/%m/%Y às %H:%M')}
⏱️ *Duração:* {duracao} dia{'s' if duracao != 1 else ''}

Obrigado por utilizar nossos equipamentos de forma responsável! 🙏
"""
        
        return WhatsAppService.send_message(
            emprestimo.telefone_responsavel,
            message
        )
    
    @staticmethod
    def send_reminder(emprestimo, dias_restantes: int) -> bool:
        """Envia lembrete de devolução via WhatsApp"""
        if not emprestimo.telefone_responsavel:
            return False
        
        message = f"""
⏰ *Lembrete de Devolução - Inventário TI*

Olá {emprestimo.responsavel}!

📦 *Equipamento:* {emprestimo.equipamento.nome}
🏷️ *Tipo:* {emprestimo.equipamento.tipo}
🔢 *Nº Série:* {emprestimo.equipamento.numero_serie}

📅 *Emprestado em:* {emprestimo.data_emprestimo.strftime('%d/%m/%Y')}
⏰ *Devolução prevista:* {emprestimo.data_devolucao_prevista.strftime('%d/%m/%Y')}

⚠️ *Faltam {dias_restantes} dia{'s' if dias_restantes != 1 else ''}!*

Por favor, providencie a devolução na data prevista.
Se precisar de prorrogação, entre em contato com o TI.
"""
        
        return WhatsAppService.send_message(
            emprestimo.telefone_responsavel,
            message
        )
    
    @staticmethod
    def send_overdue_alert(emprestimo, dias_atraso: int) -> bool:
        """Envia alerta de atraso via WhatsApp"""
        if not emprestimo.telefone_responsavel:
            return False
        
        message = f"""
🚨 *ALERTA: Devolução Atrasada - Inventário TI*

⚠️ *ATENÇÃO {emprestimo.responsavel.upper()}!*

📦 *Equipamento:* {emprestimo.equipamento.nome}
🏷️ *Tipo:* {emprestimo.equipamento.tipo}
🔢 *Nº Série:* {emprestimo.equipamento.numero_serie}

📅 *Data do empréstimo:* {emprestimo.data_emprestimo.strftime('%d/%m/%Y')}
⏰ *Devolução prevista:* {emprestimo.data_devolucao_prevista.strftime('%d/%m/%Y')}

🚨 *ATRASADO HÁ {dias_atraso} DIA{'S' if dias_atraso != 1 else ''}!*

Por favor, providencie a devolução URGENTE do equipamento.
Entre em contato com o TI imediatamente.
"""
        
        return WhatsAppService.send_message(
            emprestimo.telefone_responsavel,
            message
        )
    
    @staticmethod
    def send_test_message(phone: str) -> Dict[str, Any]:
        """
        Envia mensagem de teste
        
        Returns:
            dict: {'success': bool, 'message': str, 'details': str (opcional)}
        """
        message = """
🧪 *Teste de Mensagem - Inventário TI*

Esta é uma mensagem de teste do sistema de notificações via WhatsApp.

Se você recebeu esta mensagem, o sistema está configurado corretamente! ✅

Sistema de Inventário de Equipamentos TI
"""
        
        # Usa o método detalhado para obter informações completas
        result = WhatsAppService.send_message_detailed(phone, message)
        
        # Se sucesso, personaliza a mensagem
        if result['success']:
            result['message'] = 'Mensagem de teste enviada com sucesso! Verifique seu WhatsApp.'
        
        return result
