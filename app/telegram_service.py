"""
Serviço de envio de mensagens via Telegram Bot para notificações do sistema de inventário.
"""
import requests
import logging
from typing import Dict, Any
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramService:
    """Serviço para envio de mensagens via Telegram Bot API"""
    
    @staticmethod
    def _get_config_value(key: str, default: str = '') -> str:
        """
        Obtém valor de configuração do ambiente ou do arquivo .env
        Prioriza variável de ambiente sobre arquivo .env
        """
        # Primeiro tenta pegar do ambiente
        value = os.environ.get(key)
        if value:
            return value
        
        # Se não encontrou, tenta pegar do ConfigManager
        try:
            from app.config_manager import ConfigManager
            config = ConfigManager.get_config()
            return config.get(key, default)
        except:
            return default
    
    @staticmethod
    def is_enabled() -> bool:
        """Verifica se o Telegram está habilitado"""
        return TelegramService._get_config_value('TELEGRAM_ENABLED', 'false').lower() == 'true'
    
    @staticmethod
    def get_bot_token() -> str:
        """Retorna o token do bot"""
        return TelegramService._get_config_value('TELEGRAM_BOT_TOKEN', '')
    
    @staticmethod
    def format_chat_id(chat_id: str) -> str:
        """
        Formata chat_id removendo caracteres especiais
        Chat ID pode ser um número ou @username
        """
        if not chat_id:
            return ''
        
        chat_id = str(chat_id).strip()
        
        # Se começa com @, mantém o formato de username
        if chat_id.startswith('@'):
            return chat_id
        
        # Remove tudo que não seja número ou sinal de menos (para IDs negativos de grupos)
        chat_id = ''.join(filter(lambda x: x.isdigit() or x == '-', chat_id))
        
        return chat_id
    
    @staticmethod
    def send_message(chat_id: str, message: str, parse_mode: str = 'Markdown') -> Dict[str, Any]:
        """
        Envia mensagem via Telegram Bot API
        
        Args:
            chat_id: ID do chat ou @username do destinatário
            message: Texto da mensagem (suporta Markdown ou HTML)
            parse_mode: Formato do texto ('Markdown', 'HTML' ou None)
        
        Returns:
            dict: {'success': bool, 'message': str, 'details': str (opcional)}
        """
        try:
            bot_token = TelegramService.get_bot_token()
            
            if not bot_token:
                logger.error('Token do bot Telegram não configurado')
                return {
                    'success': False,
                    'message': 'Token do bot não configurado',
                    'details': 'Configure TELEGRAM_BOT_TOKEN no .env ou nas variáveis de ambiente'
                }
            
            # Formata o chat_id
            formatted_chat_id = TelegramService.format_chat_id(chat_id)
            
            if not formatted_chat_id:
                logger.error('Chat ID inválido ou vazio')
                return {
                    'success': False,
                    'message': 'Chat ID inválido',
                    'details': 'Forneça um Chat ID válido (número) ou @username'
                }
            
            url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
            
            data = {
                'chat_id': formatted_chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            logger.info(f'Enviando mensagem Telegram para {formatted_chat_id}')
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                logger.info(f'Mensagem Telegram enviada com sucesso para {formatted_chat_id}')
                return {
                    'success': True,
                    'message': f'Mensagem enviada com sucesso para {formatted_chat_id}!'
                }
            else:
                error_msg = response.text
                logger.error(f'Erro Telegram: {response.status_code} - {error_msg}')
                
                # Parse do erro do Telegram
                try:
                    import json
                    error_json = json.loads(error_msg)
                    error_description = error_json.get('description', error_msg)
                    
                    # Mensagens de erro específicas
                    if 'bot was blocked' in error_description.lower():
                        error_description = (
                            f"❌ Bot foi bloqueado pelo usuário {formatted_chat_id}.\n\n"
                            "💡 Solução: O usuário precisa:\n"
                            "1. Abrir conversa com o bot no Telegram\n"
                            "2. Clicar em 'Iniciar' ou enviar /start\n"
                            "3. Desbloquear o bot se bloqueou anteriormente"
                        )
                    elif 'chat not found' in error_description.lower():
                        error_description = (
                            f"❌ Chat {formatted_chat_id} não encontrado.\n\n"
                            "💡 Possíveis causas:\n"
                            "1. Chat ID incorreto\n"
                            "2. Usuário ainda não iniciou conversa com o bot\n"
                            "3. Bot foi removido do grupo (se for chat de grupo)\n\n"
                            "📋 Como obter o Chat ID:\n"
                            "• Use o bot @userinfobot no Telegram\n"
                            "• Envie uma mensagem para seu bot e use /getUpdates"
                        )
                    elif 'unauthorized' in error_description.lower():
                        error_description = (
                            "❌ Token do bot inválido ou não autorizado.\n\n"
                            "💡 Solução:\n"
                            "1. Verifique se o token está correto\n"
                            "2. Obtenha um novo token com @BotFather\n"
                            "3. Atualize TELEGRAM_BOT_TOKEN no .env"
                        )
                except:
                    error_description = error_msg
                
                return {
                    'success': False,
                    'message': f'Erro ao enviar via Telegram (código {response.status_code})',
                    'details': error_description
                }
                
        except requests.exceptions.Timeout:
            logger.error('Timeout ao enviar mensagem Telegram')
            return {
                'success': False,
                'message': 'Timeout ao conectar com Telegram',
                'details': 'A API do Telegram não respondeu a tempo. Tente novamente.'
            }
        except requests.exceptions.ConnectionError:
            logger.error('Erro de conexão com Telegram')
            return {
                'success': False,
                'message': 'Erro de conexão',
                'details': 'Não foi possível conectar com a API do Telegram. Verifique sua internet.'
            }
        except Exception as e:
            logger.error(f'Erro ao enviar mensagem Telegram: {str(e)}')
            return {
                'success': False,
                'message': f'Erro de sistema: {str(e)}',
                'details': 'Verifique os logs do servidor'
            }
    
    @staticmethod
    def send_loan_confirmation(emprestimo) -> bool:
        """Envia confirmação de empréstimo via Telegram"""
        if not emprestimo.telegram_chat_id:
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
        
        result = TelegramService.send_message(emprestimo.telegram_chat_id, message)
        return result['success']
    
    @staticmethod
    def send_return_confirmation(emprestimo) -> bool:
        """Envia confirmação de devolução via Telegram"""
        if not emprestimo.telegram_chat_id:
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
        
        result = TelegramService.send_message(emprestimo.telegram_chat_id, message)
        return result['success']
    
    @staticmethod
    def send_reminder(emprestimo, dias_restantes: int) -> bool:
        """Envia lembrete de devolução via Telegram"""
        if not emprestimo.telegram_chat_id:
            return False
        
        message = f"""
⏰ *Lembrete de Devolução - Inventário TI*

Olá {emprestimo.responsavel}!

📦 *Equipamento:* {emprestimo.equipamento.nome}
🏷️ *Tipo:* {emprestimo.equipamento.tipo}
🔢 *Nº Série:* {emprestimo.equipamento.numero_serie}

📅 *Emprestado em:* {emprestimo.data_emprestimo.strftime('%d/%m/%Y')}
⏰ *Devolução prevista:* {emprestimo.data_devolucao_prevista.strftime('%d/%m/%Y')}

⚠️ *Faltam apenas {dias_restantes} dia{'s' if dias_restantes != 1 else ''}!*

Por favor, providencie a devolução do equipamento na data prevista.
Se precisar de prorrogação, entre em contato com o TI.
"""
        
        result = TelegramService.send_message(emprestimo.telegram_chat_id, message)
        return result['success']
    
    @staticmethod
    def send_overdue_alert(emprestimo, dias_atraso: int) -> bool:
        """Envia alerta de atraso via Telegram"""
        if not emprestimo.telegram_chat_id:
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
        
        result = TelegramService.send_message(emprestimo.telegram_chat_id, message)
        return result['success']
    
    @staticmethod
    def send_test_message(chat_id: str) -> Dict[str, Any]:
        """
        Envia mensagem de teste
        
        Returns:
            dict: {'success': bool, 'message': str, 'details': str (opcional)}
        """
        message = """
🧪 *Teste de Mensagem - Inventário TI*

Esta é uma mensagem de teste do sistema de notificações via Telegram.

Se você recebeu esta mensagem, o sistema está configurado corretamente! ✅

_Sistema de Inventário de Equipamentos TI_
"""
        
        result = TelegramService.send_message(chat_id, message)
        
        # Personaliza a mensagem de sucesso
        if result['success']:
            result['message'] = 'Mensagem de teste enviada com sucesso! Verifique seu Telegram.'
        
        return result
    
    @staticmethod
    def get_bot_info() -> Dict[str, Any]:
        """
        Obtém informações sobre o bot (útil para verificar se o token está correto)
        
        Returns:
            dict: {'success': bool, 'data': dict, 'message': str}
        """
        try:
            bot_token = TelegramService.get_bot_token()
            
            if not bot_token:
                return {
                    'success': False,
                    'message': 'Token do bot não configurado'
                }
            
            url = f'https://api.telegram.org/bot{bot_token}/getMe'
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data.get('result', {})
                    return {
                        'success': True,
                        'data': {
                            'username': bot_info.get('username'),
                            'first_name': bot_info.get('first_name'),
                            'id': bot_info.get('id'),
                            'can_read_all_group_messages': bot_info.get('can_read_all_group_messages'),
                            'supports_inline_queries': bot_info.get('supports_inline_queries')
                        },
                        'message': f"Bot @{bot_info.get('username')} está ativo!"
                    }
            
            return {
                'success': False,
                'message': 'Token inválido ou bot não encontrado'
            }
            
        except Exception as e:
            logger.error(f'Erro ao obter informações do bot: {str(e)}')
            return {
                'success': False,
                'message': f'Erro: {str(e)}'
            }
