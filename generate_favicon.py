#!/usr/bin/env python3
"""Gera favicon.ico para a aplicação"""
from PIL import Image, ImageDraw

# Criar um favicon simples (16x16)
img = Image.new('RGB', (16, 16), '#EF7D2D')
draw = ImageDraw.Draw(img)

# Desenhar um quadrado branco pequeno no centro (representando uma caixa)
draw.rectangle((4, 4, 12, 12), fill='white')

# Salvar como ICO
img.save('app/static/favicon.ico', 'ICO')
print('✅ Favicon criado: app/static/favicon.ico')
