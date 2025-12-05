"""
Patch para forçar IPv4-only em todas as conexões socket
DEVE ser importado ANTES de qualquer outro módulo que use socket/networking
"""
import socket
import logging

logger = logging.getLogger(__name__)

# Guarda o getaddrinfo original
_original_getaddrinfo = socket.getaddrinfo

def _ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    """
    Wrapper que força socket.AF_INET (IPv4) ao invés de AF_UNSPEC.
    Isso evita que a biblioteca tente conectar via IPv6 primeiro (que falha na Vercel).
    """
    # Força family para IPv4 (AF_INET = 2)
    if family == 0:  # AF_UNSPEC
        family = socket.AF_INET
    elif family == socket.AF_UNSPEC:
        family = socket.AF_INET
    
    try:
        result = _original_getaddrinfo(host, port, family, type, proto, flags)
        logger.debug(f"getaddrinfo({host}, {port}) forced to IPv4: {result}")
        return result
    except Exception as e:
        logger.warning(f"Error in IPv4-only getaddrinfo for {host}:{port}: {e}")
        raise

# Substitui globalmente ANTES de qualquer import de psycopg2
socket.getaddrinfo = _ipv4_only_getaddrinfo
logger.info("IPv4-only socket patch applied successfully")
