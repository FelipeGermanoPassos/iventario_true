"""
Script para gerar chaves VAPID para Push Notifications
Execute este script para gerar um par de chaves público/privada VAPID
"""
from pywebpush import webpush
import base64
import os

try:
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
except ImportError:
    print("Instalando dependência necessária: cryptography")
    os.system("pip install cryptography")
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend


def gerar_chaves_vapid():
    """Gera um par de chaves VAPID (público e privada)"""
    
    # Gera chave privada
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    
    # Serializa chave privada
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Gera chave pública
    public_key = private_key.public_key()
    
    # Serializa chave pública
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )
    
    # Converte para base64 URL-safe
    private_key_b64 = base64.urlsafe_b64encode(private_bytes).decode('utf-8').rstrip('=')
    public_key_b64 = base64.urlsafe_b64encode(public_bytes).decode('utf-8').rstrip('=')
    
    return private_key_b64, public_key_b64


def main():
    print("=" * 60)
    print("Gerador de Chaves VAPID para Push Notifications")
    print("=" * 60)
    print()
    
    print("Gerando chaves VAPID...")
    private_key, public_key = gerar_chaves_vapid()
    
    print("✅ Chaves geradas com sucesso!")
    print()
    print("=" * 60)
    print("CHAVE PRIVADA (mantenha em segredo):")
    print("=" * 60)
    print(private_key)
    print()
    print("=" * 60)
    print("CHAVE PÚBLICA:")
    print("=" * 60)
    print(public_key)
    print()
    print("=" * 60)
    print()
    print("📝 INSTRUÇÕES:")
    print()
    print("1. Adicione estas variáveis de ambiente ao seu sistema:")
    print()
    print("   Windows PowerShell:")
    print(f'   $env:VAPID_PRIVATE_KEY="{private_key}"')
    print(f'   $env:VAPID_PUBLIC_KEY="{public_key}"')
    print()
    print("   Linux/Mac:")
    print(f'   export VAPID_PRIVATE_KEY="{private_key}"')
    print(f'   export VAPID_PUBLIC_KEY="{public_key}"')
    print()
    print("2. ⚠️  IMPORTANTE: A chave privada deve ser mantida em SEGREDO!")
    print("   Não compartilhe nem publique no repositório Git.")
    print()
    print("3. Adicione estas variáveis ao arquivo .env (se estiver usando):")
    print()
    print(f"   VAPID_PRIVATE_KEY={private_key}")
    print(f"   VAPID_PUBLIC_KEY={public_key}")
    print()
    print("4. Reinicie o servidor Flask após configurar as variáveis.")
    print()
    print("=" * 60)
    
    # Opção de salvar em arquivo
    salvar = input("\n💾 Deseja salvar as chaves em um arquivo? (s/n): ").lower().strip()
    
    if salvar == 's':
        filename = "vapid_keys.txt"
        with open(filename, 'w') as f:
            f.write("CHAVES VAPID PARA PUSH NOTIFICATIONS\n")
            f.write("=" * 60 + "\n\n")
            f.write("⚠️  MANTENHA ESTE ARQUIVO EM SEGREDO!\n")
            f.write("Não compartilhe nem publique no repositório Git.\n\n")
            f.write("=" * 60 + "\n")
            f.write("CHAVE PRIVADA:\n")
            f.write("=" * 60 + "\n")
            f.write(private_key + "\n\n")
            f.write("=" * 60 + "\n")
            f.write("CHAVE PÚBLICA:\n")
            f.write("=" * 60 + "\n")
            f.write(public_key + "\n\n")
            f.write("=" * 60 + "\n")
            f.write("VARIÁVEIS DE AMBIENTE:\n")
            f.write("=" * 60 + "\n\n")
            f.write("Windows PowerShell:\n")
            f.write(f'$env:VAPID_PRIVATE_KEY="{private_key}"\n')
            f.write(f'$env:VAPID_PUBLIC_KEY="{public_key}"\n\n')
            f.write("Linux/Mac:\n")
            f.write(f'export VAPID_PRIVATE_KEY="{private_key}"\n')
            f.write(f'export VAPID_PUBLIC_KEY="{public_key}"\n\n')
            f.write(".env file:\n")
            f.write(f"VAPID_PRIVATE_KEY={private_key}\n")
            f.write(f"VAPID_PUBLIC_KEY={public_key}\n")
        
        print(f"\n✅ Chaves salvas em: {filename}")
        print("⚠️  Lembre-se de adicionar este arquivo ao .gitignore!")
    
    print("\n✨ Configuração concluída!")


if __name__ == '__main__':
    main()
