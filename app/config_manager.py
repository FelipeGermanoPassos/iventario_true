"""
Gerenciador de configurações do sistema.
Permite salvar e carregar configurações do arquivo .env
"""
import os
from pathlib import Path


class ConfigManager:
    """Gerencia todas as configurações do sistema em arquivo .env"""
    
    def __init__(self, env_file='.env'):
        self.env_file = Path(env_file)
        self.base_dir = Path(__file__).parent.parent
        self.env_path = self.base_dir / self.env_file
    
    @classmethod
    def get_config(cls):
        """Carrega todas as configurações do arquivo .env"""
        manager = cls()
        config = {
            # Configurações de E-mail
            'MAIL_ENABLED': 'false',
            'MAIL_SERVER': 'smtp.gmail.com',
            'MAIL_PORT': '587',
            'MAIL_USE_TLS': 'true',
            'MAIL_USE_SSL': 'false',
            'MAIL_USERNAME': '',
            'MAIL_PASSWORD': '',
            'MAIL_DEFAULT_SENDER': '',
            
            # Configurações de WhatsApp
            'WHATSAPP_ENABLED': 'false',
            'WHATSAPP_PROVIDER': '',
            'TWILIO_ACCOUNT_SID': '',
            'TWILIO_AUTH_TOKEN': '',
            'TWILIO_WHATSAPP_NUMBER': '',
            'MESSAGEBIRD_API_KEY': '',
            'MESSAGEBIRD_CHANNEL_ID': '',
            'META_ACCESS_TOKEN': '',
            'META_PHONE_NUMBER_ID': ''
        }
        
        if manager.env_path.exists():
            with open(manager.env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if key in config:
                            config[key] = value
        
        return config
    
    @classmethod
    def save_config(cls, new_config):
        """Salva configurações no arquivo .env"""
        manager = cls()
        
        # Carrega configurações existentes
        current_config = cls.get_config()
        
        # Atualiza com novas configurações
        current_config.update(new_config)
        
        # Gera conteúdo do arquivo
        content = """# Configuração do Sistema de Inventário
# Este arquivo foi gerado automaticamente pela interface web

# ====== CONFIGURAÇÃO DE E-MAIL ======

# Habilitar/Desabilitar envio de e-mails (true ou false)
MAIL_ENABLED={MAIL_ENABLED}

# Servidor SMTP
MAIL_SERVER={MAIL_SERVER}

# Porta SMTP
MAIL_PORT={MAIL_PORT}

# Usar TLS (true ou false)
MAIL_USE_TLS={MAIL_USE_TLS}

# Usar SSL (true ou false)
MAIL_USE_SSL={MAIL_USE_SSL}

# E-mail remetente
MAIL_USERNAME={MAIL_USERNAME}

# Senha do e-mail (use senha de app para Gmail)
MAIL_PASSWORD={MAIL_PASSWORD}

# E-mail padrão do remetente (opcional)
MAIL_DEFAULT_SENDER={MAIL_DEFAULT_SENDER}

# ====== CONFIGURAÇÃO DE WHATSAPP ======

# Habilitar/Desabilitar envio via WhatsApp (true ou false)
WHATSAPP_ENABLED={WHATSAPP_ENABLED}

# Provedor WhatsApp (twilio, messagebird ou meta)
WHATSAPP_PROVIDER={WHATSAPP_PROVIDER}

# Credenciais Twilio
TWILIO_ACCOUNT_SID={TWILIO_ACCOUNT_SID}
TWILIO_AUTH_TOKEN={TWILIO_AUTH_TOKEN}
TWILIO_WHATSAPP_NUMBER={TWILIO_WHATSAPP_NUMBER}

# Credenciais MessageBird
MESSAGEBIRD_API_KEY={MESSAGEBIRD_API_KEY}
MESSAGEBIRD_CHANNEL_ID={MESSAGEBIRD_CHANNEL_ID}

# Credenciais Meta/Facebook
META_ACCESS_TOKEN={META_ACCESS_TOKEN}
META_PHONE_NUMBER_ID={META_PHONE_NUMBER_ID}
""".format(**current_config)
        
        try:
            with open(manager.env_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            return False


class EmailConfigManager:
    """Gerencia configurações de e-mail em arquivo .env"""
    
    def __init__(self, env_file='.env'):
        self.env_file = Path(env_file)
        self.base_dir = Path(__file__).parent.parent
        self.env_path = self.base_dir / self.env_file
    
    def load_config(self):
        """Carrega configurações do arquivo .env"""
        config = {
            'MAIL_ENABLED': 'false',
            'MAIL_SERVER': 'smtp.gmail.com',
            'MAIL_PORT': '587',
            'MAIL_USE_TLS': 'true',
            'MAIL_USE_SSL': 'false',
            'MAIL_USERNAME': '',
            'MAIL_PASSWORD': '',
            'MAIL_DEFAULT_SENDER': ''
        }
        
        if self.env_path.exists():
            with open(self.env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if key in config:
                            config[key] = value
        
        return config
    
    def save_config(self, config):
        """Salva configurações no arquivo .env"""
        content = """# Configuração de E-mail para o Sistema de Inventário
# Este arquivo foi gerado automaticamente pela interface web

# ====== CONFIGURAÇÃO DE E-MAIL ======

# Habilitar/Desabilitar envio de e-mails (true ou false)
MAIL_ENABLED={MAIL_ENABLED}

# Servidor SMTP
MAIL_SERVER={MAIL_SERVER}

# Porta SMTP
MAIL_PORT={MAIL_PORT}

# Usar TLS (true ou false)
MAIL_USE_TLS={MAIL_USE_TLS}

# Usar SSL (true ou false)
MAIL_USE_SSL={MAIL_USE_SSL}

# E-mail remetente
MAIL_USERNAME={MAIL_USERNAME}

# Senha do e-mail (use senha de app para Gmail)
MAIL_PASSWORD={MAIL_PASSWORD}

# E-mail padrão do remetente (opcional)
MAIL_DEFAULT_SENDER={MAIL_DEFAULT_SENDER}
""".format(**config)
        
        with open(self.env_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def apply_to_app(self, app, config):
        """Aplica configurações ao app Flask"""
        app.config['MAIL_ENABLED'] = config.get('MAIL_ENABLED', 'false').lower() == 'true'
        app.config['MAIL_SERVER'] = config.get('MAIL_SERVER', 'smtp.gmail.com')
        app.config['MAIL_PORT'] = int(config.get('MAIL_PORT', 587))
        app.config['MAIL_USE_TLS'] = config.get('MAIL_USE_TLS', 'true').lower() == 'true'
        app.config['MAIL_USE_SSL'] = config.get('MAIL_USE_SSL', 'false').lower() == 'true'
        app.config['MAIL_USERNAME'] = config.get('MAIL_USERNAME', '')
        app.config['MAIL_PASSWORD'] = config.get('MAIL_PASSWORD', '')
        app.config['MAIL_DEFAULT_SENDER'] = config.get('MAIL_DEFAULT_SENDER', '') or config.get('MAIL_USERNAME', '')
