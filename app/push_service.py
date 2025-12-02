"""
Serviço de envio de Push Notifications
"""
from flask import current_app
import json
import os

try:
    from pywebpush import webpush, WebPushException
except Exception:  # pywebpush ausente no ambiente serverless
    webpush = None
    class WebPushException(Exception):
        pass


class PushNotificationService:
    """Gerencia o envio de push notifications"""
    @staticmethod
    def is_available():
        return webpush is not None
    
    @staticmethod
    def get_vapid_keys():
        """Retorna as chaves VAPID configuradas"""
        private_key = os.environ.get('VAPID_PRIVATE_KEY', '')
        public_key = os.environ.get('VAPID_PUBLIC_KEY', '')
        
        if not private_key or not public_key:
            current_app.logger.warning('VAPID keys não configuradas')
            return None, None
            
        return private_key, public_key
    
    @staticmethod
    def send_notification(subscription_info, title, body, url='/', tag=None, require_interaction=False):
        """
        Envia uma push notification para uma subscrição específica
        
        Args:
            subscription_info: Dict com endpoint, p256dh e auth
            title: Título da notificação
            body: Corpo da mensagem
            url: URL para redirecionar ao clicar (default: '/')
            tag: Tag para agrupar notificações
            require_interaction: Se a notificação requer interação
            
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        private_key, public_key = PushNotificationService.get_vapid_keys()
        
        if not private_key or not public_key:
            current_app.logger.error('Não foi possível enviar push: VAPID keys não configuradas')
            return False
        
        try:
            if webpush is None:
                current_app.logger.warning('pywebpush não está instalado neste deploy; push desabilitado.')
                return False
            # Prepara o payload da notificação
            payload = {
                'title': title,
                'body': body,
                'url': url
            }
            
            if tag:
                payload['tag'] = tag
            if require_interaction:
                payload['requireInteraction'] = require_interaction
            
            # Monta o subscription_info no formato esperado
            subscription = {
                'endpoint': subscription_info['endpoint'],
                'keys': {
                    'p256dh': subscription_info['p256dh'],
                    'auth': subscription_info['auth']
                }
            }
            
            # Envia a notificação
            response = webpush(
                subscription_info=subscription,
                data=json.dumps(payload),
                vapid_private_key=private_key,
                vapid_claims={
                    "sub": f"mailto:{os.environ.get('MAIL_USERNAME', 'admin@inventario.com')}"
                }
            )
            
            current_app.logger.info(f'Push notification enviada com sucesso: {response.status_code}')
            return True
            
        except WebPushException as e:
            current_app.logger.error(f'Erro ao enviar push notification: {str(e)}')
            
            # Se o endpoint não é mais válido (410 Gone), retorna False para remover a subscrição
            if e.response and e.response.status_code == 410:
                current_app.logger.info('Subscription expirada, deve ser removida')
                return False
            
            return False
        except Exception as e:
            current_app.logger.error(f'Erro inesperado ao enviar push: {str(e)}')
            return False
    
    @staticmethod
    def send_to_user(usuario_id, title, body, url='/', tag=None):
        """
        Envia notificação para todas as subscrições ativas de um usuário
        
        Args:
            usuario_id: ID do usuário
            title: Título da notificação
            body: Corpo da mensagem
            url: URL para redirecionar
            tag: Tag para agrupar notificações
            
        Returns:
            int: Número de notificações enviadas com sucesso
        """
        from app.models import PushSubscription, db
        
        # Busca todas as subscrições ativas do usuário
        subscriptions = PushSubscription.query.filter_by(
            usuario_id=usuario_id,
            ativa=True
        ).all()
        
        if not subscriptions:
            current_app.logger.info(f'Usuário {usuario_id} não possui subscrições ativas')
            return 0
        
        success_count = 0
        
        for subscription in subscriptions:
            subscription_info = {
                'endpoint': subscription.endpoint,
                'p256dh': subscription.p256dh,
                'auth': subscription.auth
            }
            
            success = PushNotificationService.send_notification(
                subscription_info, title, body, url, tag
            )
            
            if success:
                success_count += 1
            else:
                # Se a subscrição falhou, marca como inativa
                subscription.ativa = False
                db.session.commit()
                current_app.logger.info(f'Subscription {subscription.id} marcada como inativa')
        
        return success_count
    
    @staticmethod
    def send_to_all_users(title, body, url='/', tag=None):
        """
        Envia notificação para todos os usuários com subscrições ativas
        
        Args:
            title: Título da notificação
            body: Corpo da mensagem
            url: URL para redirecionar
            tag: Tag para agrupar notificações
            
        Returns:
            int: Número de notificações enviadas com sucesso
        """
        from app.models import PushSubscription, db
        
        subscriptions = PushSubscription.query.filter_by(ativa=True).all()
        
        if not subscriptions:
            current_app.logger.info('Nenhuma subscrição ativa encontrada')
            return 0
        
        success_count = 0
        
        for subscription in subscriptions:
            subscription_info = {
                'endpoint': subscription.endpoint,
                'p256dh': subscription.p256dh,
                'auth': subscription.auth
            }
            
            success = PushNotificationService.send_notification(
                subscription_info, title, body, url, tag
            )
            
            if success:
                success_count += 1
            else:
                subscription.ativa = False
                db.session.commit()
        
        current_app.logger.info(f'{success_count}/{len(subscriptions)} notificações enviadas')
        return success_count
