#!/usr/bin/env python3
"""Gera ícones PNG para a aplicação"""
import os
from PIL import Image, ImageDraw, ImageFont

# Criar pasta se não existir
os.makedirs('app/static/icons', exist_ok=True)

# Cores
cor_fundo = '#ffffff'
cor_principal = '#EF7D2D'
cor_destaque = '#D96B1F'

def criar_icone(tamanho):
    """Cria um ícone PNG com o tamanho especificado"""
    # Criar imagem com fundo branco
    img = Image.new('RGB', (tamanho, tamanho), cor_fundo)
    draw = ImageDraw.Draw(img)
    
    # Desenhar um quadrado arredondado como fundo
    margem = int(tamanho * 0.1)
    raio = int(tamanho * 0.15)
    
    # Retângulo arredondado (simulado com quadrado + arredondamento)
    x0, y0 = margem, margem
    x1, y1 = tamanho - margem, tamanho - margem
    
    # Desenhar fundo gradualmente (usando tons)
    for i in range(0, 100, 5):
        alpha = i / 100.0
        # Misturar cores para gradiente
        r = int(0xEF * alpha + 0xFF * (1 - alpha))
        g = int(0x7D * alpha + 0xFF * (1 - alpha))
        b = int(0x2D * alpha + 0xFF * (1 - alpha))
        color = f'#{r:02x}{g:02x}{b:02x}'
        offset = int(tamanho * 0.1 * (1 - alpha))
        draw.rectangle(
            (offset, offset, tamanho - offset, tamanho - offset),
            fill=color
        )
    
    # Desenhar um símbolo simples (caixa/equipamento)
    # Caixa com ponto (representando um equipamento)
    box_size = int(tamanho * 0.5)
    box_x = (tamanho - box_size) // 2
    box_y = (tamanho - box_size) // 2
    
    draw.rectangle(
        (box_x, box_y, box_x + box_size, box_y + box_size),
        outline='white',
        width=3
    )
    
    # Círculo no centro (representando inventário)
    circle_size = int(box_size * 0.3)
    cx = tamanho // 2
    cy = tamanho // 2
    draw.ellipse(
        (cx - circle_size, cy - circle_size, cx + circle_size, cy + circle_size),
        fill='white'
    )
    
    # Salvar imagem
    arquivo = f'app/static/icons/icon-{tamanho}.png'
    img.save(arquivo, 'PNG')
    print(f'✅ Ícone criado: {arquivo}')

# Gerar ícones
criar_icone(192)
criar_icone(512)

print('\n✅ Ícones gerados com sucesso!')
