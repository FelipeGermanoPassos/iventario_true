from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, make_response, current_app, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, Equipamento, Emprestimo, Usuario, EquipamentoFoto, Manutencao
from datetime import datetime
from sqlalchemy import func
from functools import wraps
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from werkzeug.utils import secure_filename
import os
import uuid
import qrcode
import base64

main = Blueprint('main', __name__)

# Decorator para verificar se usuário é admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'success': False, 'message': 'Acesso negado. Apenas administradores.'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROTAS DE AUTENTICAÇÃO ====================

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_password(senha):
            if not usuario.ativo:
                return jsonify({'success': False, 'message': 'Usuário inativo. Contate o administrador.'}), 403
            
            login_user(usuario, remember=data.get('lembrar', False))
            usuario.ultimo_acesso = datetime.utcnow()
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Login realizado com sucesso!'})
        
        return jsonify({'success': False, 'message': 'Email ou senha incorretos.'}), 401
    
    return render_template('login.html')

@main.route('/registro', methods=['GET', 'POST'])
def registro():
    """Página de registro de novos usuários"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        data = request.get_json()
        
        # Valida se o email já existe
        if Usuario.query.filter_by(email=data.get('email')).first():
            return jsonify({'success': False, 'message': 'Email já cadastrado.'}), 400
        
        # Cria novo usuário
        novo_usuario = Usuario(
            nome=data.get('nome'),
            email=data.get('email'),
            departamento=data.get('departamento'),
            telefone=data.get('telefone')
        )
        novo_usuario.set_password(data.get('senha'))
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Usuário cadastrado com sucesso! Faça login para continuar.'})
    
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """Página de perfil do usuário"""
    if request.method == 'POST':
        data = request.get_json()
        acao = data.get('acao')
        
        if acao == 'atualizar_dados':
            # Atualiza dados pessoais
            current_user.nome = data.get('nome', current_user.nome)
            current_user.departamento = data.get('departamento', current_user.departamento)
            current_user.telefone = data.get('telefone', current_user.telefone)
            
            # Verifica se o email mudou e se já não está em uso
            novo_email = data.get('email')
            if novo_email and novo_email != current_user.email:
                if Usuario.query.filter_by(email=novo_email).first():
                    return jsonify({'success': False, 'message': 'Este email já está em uso.'}), 400
                current_user.email = novo_email
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Dados atualizados com sucesso!'})
        
        elif acao == 'alterar_senha':
            # Altera senha
            senha_atual = data.get('senha_atual')
            senha_nova = data.get('senha_nova')
            senha_confirmar = data.get('senha_confirmar')
            
            # Validações
            if not current_user.check_password(senha_atual):
                return jsonify({'success': False, 'message': 'Senha atual incorreta.'}), 400
            
            if len(senha_nova) < 6:
                return jsonify({'success': False, 'message': 'A nova senha deve ter no mínimo 6 caracteres.'}), 400
            
            if senha_nova != senha_confirmar:
                return jsonify({'success': False, 'message': 'As senhas não coincidem.'}), 400
            
            current_user.set_password(senha_nova)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Senha alterada com sucesso!'})
        
        return jsonify({'success': False, 'message': 'Ação inválida.'}), 400
    
    return render_template('perfil.html')

# ==================== ROTAS ADMINISTRATIVAS ====================

@main.route('/admin')
@login_required
@admin_required
def admin():
    """Painel administrativo"""
    return render_template('admin.html')

@main.route('/admin/usuarios')
@login_required
@admin_required
def listar_usuarios():
    """Lista todos os usuários"""
    usuarios = Usuario.query.order_by(Usuario.data_cadastro.desc()).all()
    return jsonify([usuario.to_dict() for usuario in usuarios])

@main.route('/admin/usuario/<int:id>/toggle-ativo', methods=['PUT'])
@login_required
@admin_required
def toggle_usuario_ativo(id):
    """Ativa ou desativa um usuário"""
    try:
        usuario = Usuario.query.get_or_404(id)
        
        # Não permite desativar a si mesmo
        if usuario.id == current_user.id:
            return jsonify({'success': False, 'message': 'Você não pode desativar sua própria conta.'}), 400
        
        usuario.ativo = not usuario.ativo
        db.session.commit()
        
        status = 'ativado' if usuario.ativo else 'desativado'
        return jsonify({
            'success': True,
            'message': f'Usuário {status} com sucesso!',
            'usuario': usuario.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao alterar status: {str(e)}'}), 400

@main.route('/admin/usuario/<int:id>/toggle-admin', methods=['PUT'])
@login_required
@admin_required
def toggle_usuario_admin(id):
    """Torna um usuário admin ou remove privilégios de admin"""
    try:
        usuario = Usuario.query.get_or_404(id)
        
        # Não permite remover admin de si mesmo
        if usuario.id == current_user.id:
            return jsonify({'success': False, 'message': 'Você não pode remover seus próprios privilégios de administrador.'}), 400
        
        usuario.is_admin = not usuario.is_admin
        db.session.commit()
        
        status = 'promovido a administrador' if usuario.is_admin else 'removido de administrador'
        return jsonify({
            'success': True,
            'message': f'Usuário {status} com sucesso!',
            'usuario': usuario.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao alterar privilégios: {str(e)}'}), 400

@main.route('/admin/usuario/<int:id>/deletar', methods=['DELETE'])
@login_required
@admin_required
def deletar_usuario(id):
    """Deleta um usuário"""
    try:
        usuario = Usuario.query.get_or_404(id)
        
        # Não permite deletar a si mesmo
        if usuario.id == current_user.id:
            return jsonify({'success': False, 'message': 'Você não pode deletar sua própria conta.'}), 400
        
        db.session.delete(usuario)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Usuário deletado com sucesso!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao deletar usuário: {str(e)}'}), 400

@main.route('/admin/usuario/adicionar', methods=['POST'])
@login_required
@admin_required
def adicionar_usuario():
    """Adiciona um novo usuário pelo admin"""
    try:
        data = request.get_json()
        
        # Valida se o email já existe
        if Usuario.query.filter_by(email=data.get('email')).first():
            return jsonify({'success': False, 'message': 'Email já cadastrado.'}), 400
        
        # Valida senha
        if not data.get('senha') or len(data.get('senha')) < 6:
            return jsonify({'success': False, 'message': 'Senha deve ter no mínimo 6 caracteres.'}), 400
        
        # Cria novo usuário
        novo_usuario = Usuario(
            nome=data.get('nome'),
            email=data.get('email'),
            departamento=data.get('departamento'),
            telefone=data.get('telefone'),
            is_admin=data.get('is_admin', False),
            ativo=data.get('ativo', True)
        )
        novo_usuario.set_password(data.get('senha'))
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usuário criado com sucesso!',
            'usuario': novo_usuario.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao criar usuário: {str(e)}'}), 400

@main.route('/admin/usuario/<int:id>/editar', methods=['PUT'])
@login_required
@admin_required
def editar_usuario(id):
    """Edita um usuário existente"""
    try:
        usuario = Usuario.query.get_or_404(id)
        data = request.get_json()
        
        # Atualiza dados básicos
        usuario.nome = data.get('nome', usuario.nome)
        usuario.departamento = data.get('departamento', usuario.departamento)
        usuario.telefone = data.get('telefone', usuario.telefone)
        
        # Verifica email único se mudou
        novo_email = data.get('email')
        if novo_email and novo_email != usuario.email:
            if Usuario.query.filter_by(email=novo_email).first():
                return jsonify({'success': False, 'message': 'Email já está em uso.'}), 400
            usuario.email = novo_email
        
        # Atualiza senha se fornecida
        if data.get('senha'):
            if len(data.get('senha')) < 6:
                return jsonify({'success': False, 'message': 'Senha deve ter no mínimo 6 caracteres.'}), 400
            usuario.set_password(data.get('senha'))
        
        # Atualiza status e privilégios (exceto para si mesmo)
        if usuario.id != current_user.id:
            if 'is_admin' in data:
                usuario.is_admin = data.get('is_admin')
            if 'ativo' in data:
                usuario.ativo = data.get('ativo')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usuário atualizado com sucesso!',
            'usuario': usuario.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao atualizar usuário: {str(e)}'}), 400


# ==================== ROTAS DE BACKUP ====================

def realizar_backup_automatico(app):
    """Função para realizar backup automático (chamada pelo scheduler)"""
    with app.app_context():
        try:
            import shutil
            from datetime import datetime
            
            # Caminho do banco de dados
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'inventario.db')
            
            # Pasta de backups
            backup_folder = app.config['BACKUP_FOLDER']
            
            # Nome do arquivo de backup com timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'backup_auto_{timestamp}.db'
            backup_path = os.path.join(backup_folder, backup_filename)
            
            # Copia o arquivo do banco de dados
            shutil.copy2(db_path, backup_path)
            
            # Remove backups antigos (mantém apenas os últimos 30 dias)
            limpar_backups_antigos(backup_folder, dias=30)
            
            print(f'[BACKUP] Backup automático realizado com sucesso: {backup_filename}')
            return True
        except Exception as e:
            print(f'[BACKUP] Erro ao realizar backup automático: {str(e)}')
            return False

def limpar_backups_antigos(backup_folder, dias=30):
    """Remove backups mais antigos que X dias"""
    try:
        from datetime import datetime, timedelta
        import glob
        
        # Data limite
        data_limite = datetime.now() - timedelta(days=dias)
        
        # Lista todos os arquivos de backup
        arquivos_backup = glob.glob(os.path.join(backup_folder, 'backup_*.db'))
        
        for arquivo in arquivos_backup:
            # Obtém a data de modificação do arquivo
            data_arquivo = datetime.fromtimestamp(os.path.getmtime(arquivo))
            
            # Remove se for mais antigo que a data limite
            if data_arquivo < data_limite:
                os.remove(arquivo)
                print(f'[BACKUP] Backup antigo removido: {os.path.basename(arquivo)}')
    except Exception as e:
        print(f'[BACKUP] Erro ao limpar backups antigos: {str(e)}')

@main.route('/admin/backup/criar', methods=['POST'])
@login_required
@admin_required
def criar_backup_manual():
    """Cria um backup manual do banco de dados"""
    try:
        import shutil
        from datetime import datetime
        
        # Caminho do banco de dados
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'inventario.db')
        
        # Pasta de backups
        backup_folder = current_app.config['BACKUP_FOLDER']
        
        # Nome do arquivo de backup com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_manual_{timestamp}.db'
        backup_path = os.path.join(backup_folder, backup_filename)
        
        # Copia o arquivo do banco de dados
        shutil.copy2(db_path, backup_path)
        
        # Obtém tamanho do arquivo
        tamanho = os.path.getsize(backup_path)
        tamanho_mb = tamanho / (1024 * 1024)
        
        return jsonify({
            'success': True,
            'message': 'Backup criado com sucesso!',
            'backup': {
                'nome': backup_filename,
                'tamanho': f'{tamanho_mb:.2f} MB',
                'data': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao criar backup: {str(e)}'
        }), 400

@main.route('/admin/backup/listar')
@login_required
@admin_required
def listar_backups():
    """Lista todos os backups disponíveis"""
    try:
        import glob
        from datetime import datetime
        
        backup_folder = current_app.config['BACKUP_FOLDER']
        
        # Lista todos os arquivos de backup
        arquivos_backup = glob.glob(os.path.join(backup_folder, 'backup_*.db'))
        
        backups = []
        for arquivo in sorted(arquivos_backup, reverse=True):
            nome = os.path.basename(arquivo)
            tamanho = os.path.getsize(arquivo)
            tamanho_mb = tamanho / (1024 * 1024)
            data_modificacao = datetime.fromtimestamp(os.path.getmtime(arquivo))
            
            backups.append({
                'nome': nome,
                'tamanho': f'{tamanho_mb:.2f} MB',
                'data': data_modificacao.strftime('%d/%m/%Y %H:%M:%S'),
                'timestamp': data_modificacao.timestamp(),
                'tipo': 'Manual' if 'manual' in nome else 'Automático'
            })
        
        return jsonify({
            'success': True,
            'backups': backups
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar backups: {str(e)}'
        }), 400

@main.route('/admin/backup/baixar/<nome>')
@login_required
@admin_required
def baixar_backup(nome):
    """Baixa um arquivo de backup"""
    try:
        backup_folder = current_app.config['BACKUP_FOLDER']
        return send_from_directory(backup_folder, nome, as_attachment=True)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao baixar backup: {str(e)}'
        }), 400

@main.route('/admin/backup/deletar/<nome>', methods=['DELETE'])
@login_required
@admin_required
def deletar_backup(nome):
    """Deleta um arquivo de backup"""
    try:
        backup_folder = current_app.config['BACKUP_FOLDER']
        backup_path = os.path.join(backup_folder, nome)
        
        # Verifica se o arquivo existe
        if not os.path.exists(backup_path):
            return jsonify({
                'success': False,
                'message': 'Backup não encontrado.'
            }), 404
        
        # Remove o arquivo
        os.remove(backup_path)
        
        return jsonify({
            'success': True,
            'message': 'Backup deletado com sucesso!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar backup: {str(e)}'
        }), 400

# ==================== ROTAS PRINCIPAIS ====================

@main.route('/')
@login_required
def index():
    """Página principal com dashboard"""
    return render_template('index.html')


@main.route('/sw.js')
def service_worker():
    """Serve o Service Worker na raiz para escopo global."""
    sw_dir = os.path.join(current_app.root_path, 'static', 'js')
    return send_from_directory(sw_dir, 'sw.js', mimetype='application/javascript')

@main.route('/dashboard-data')
@login_required
def dashboard_data():
    """Retorna dados para o dashboard"""
    from datetime import timedelta
    
    # Total de equipamentos
    total_equipamentos = Equipamento.query.count()
    
    # Equipamentos por status
    status_data = db.session.query(
        Equipamento.status, 
        func.count(Equipamento.id)
    ).group_by(Equipamento.status).all()
    
    # Equipamentos por tipo
    tipo_data = db.session.query(
        Equipamento.tipo, 
        func.count(Equipamento.id)
    ).group_by(Equipamento.tipo).all()
    
    # Equipamentos em estoque (disponíveis)
    equipamentos_estoque = Equipamento.query.filter_by(status='Estoque').count()
    
    # Equipamentos emprestados
    equipamentos_emprestados = Equipamento.query.filter_by(status='Emprestado').count()
    
    # Equipamentos em manutenção
    equipamentos_manutencao = Equipamento.query.filter_by(status='Manutenção').count()
    
    # Valor total do inventário
    valor_total = db.session.query(func.sum(Equipamento.valor)).scalar() or 0
    
    # Empréstimos ativos
    emprestimos_ativos = Emprestimo.query.filter_by(status='Ativo').count()
    
    # Empréstimos por departamento (ativos)
    emprestimos_por_dept = db.session.query(
        Emprestimo.departamento,
        func.count(Emprestimo.id)
    ).filter(Emprestimo.status == 'Ativo').group_by(
        Emprestimo.departamento
    ).order_by(func.count(Emprestimo.id).desc()).limit(10).all()
    
    # Taxa de utilização (emprestados / total)
    taxa_utilizacao = (equipamentos_emprestados / total_equipamentos * 100) if total_equipamentos > 0 else 0
    
    # Equipamentos mais emprestados (histórico completo)
    equipamentos_populares = db.session.query(
        Equipamento.nome,
        Equipamento.tipo,
        func.count(Emprestimo.id).label('total_emprestimos')
    ).join(Emprestimo, Equipamento.id == Emprestimo.equipamento_id).group_by(
        Equipamento.id
    ).order_by(func.count(Emprestimo.id).desc()).limit(5).all()
    
    # Empréstimos nos últimos 30 dias
    trinta_dias_atras = datetime.utcnow() - timedelta(days=30)
    emprestimos_recentes = Emprestimo.query.filter(
        Emprestimo.data_emprestimo >= trinta_dias_atras
    ).count()
    
    # Custo total de manutenções
    custo_manutencoes = db.session.query(func.sum(Manutencao.custo)).scalar() or 0
    
    # Manutenções pendentes (em andamento)
    manutencoes_pendentes = Manutencao.query.filter_by(status='Em Andamento').count()
    
    # Valor médio dos equipamentos
    valor_medio = (valor_total / total_equipamentos) if total_equipamentos > 0 else 0
    
    return jsonify({
        'total_equipamentos': total_equipamentos,
        'equipamentos_estoque': equipamentos_estoque,
        'equipamentos_emprestados': equipamentos_emprestados,
        'equipamentos_manutencao': equipamentos_manutencao,
        'emprestimos_ativos': emprestimos_ativos,
        'emprestimos_recentes': emprestimos_recentes,
        'manutencoes_pendentes': manutencoes_pendentes,
        'taxa_utilizacao': round(taxa_utilizacao, 1),
        'valor_total': float(valor_total),
        'valor_medio': float(valor_medio),
        'custo_manutencoes': float(custo_manutencoes),
        'status': [{'name': s[0], 'value': s[1]} for s in status_data],
        'tipos': [{'name': t[0], 'value': t[1]} for t in tipo_data],
        'emprestimos_por_departamento': [{'name': d[0] or 'Sem Departamento', 'value': d[1]} for d in emprestimos_por_dept],
        'equipamentos_populares': [{'nome': e[0], 'tipo': e[1], 'emprestimos': e[2]} for e in equipamentos_populares]
    })

@main.route('/equipamentos')
@login_required
def listar_equipamentos():
    """Lista todos os equipamentos"""
    equipamentos = Equipamento.query.order_by(Equipamento.data_cadastro.desc()).all()
    return jsonify([eq.to_dict() for eq in equipamentos])

@main.route('/equipamento/<int:id>')
@login_required
def obter_equipamento(id):
    """Obtém um equipamento específico"""
    equipamento = Equipamento.query.get_or_404(id)
    return jsonify(equipamento.to_dict())

def _allowed_image(filename: str):
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def _save_equip_photo(file_storage):
    """Salva a foto enviada e retorna a URL pública (em /static/uploads/equipamentos)."""
    if not file_storage or file_storage.filename == '':
        return None
    if not _allowed_image(file_storage.filename):
        raise ValueError('Formato de imagem não permitido. Use PNG, JPG, JPEG, GIF ou WEBP.')
    filename = secure_filename(file_storage.filename)
    # Garante um nome único
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    upload_dir = current_app.config.get('UPLOAD_FOLDER_EQUIPAMENTOS')
    os.makedirs(upload_dir, exist_ok=True)
    full_path = os.path.join(upload_dir, unique_name)
    file_storage.save(full_path)
    # URL estática
    return f"/static/uploads/equipamentos/{unique_name}"


@main.route('/equipamento/adicionar', methods=['POST'])
@login_required
def adicionar_equipamento():
    """Adiciona um novo equipamento"""
    try:
        data = None
        is_multipart = request.content_type and 'multipart/form-data' in request.content_type
        if is_multipart:
            form = request.form
            data = {k: form.get(k) for k in form.keys()}
        else:
            data = request.get_json(silent=True) or {}
        
        # Converte a data de aquisição se fornecida
        data_aquisicao = None
        if data.get('data_aquisicao'):
            data_aquisicao = datetime.strptime(data['data_aquisicao'], '%Y-%m-%d').date()
        
        equipamento = Equipamento(
            nome=data['nome'],
            tipo=data['tipo'],
            marca=data['marca'],
            modelo=data['modelo'],
            numero_serie=data['numero_serie'],
            processador=data.get('processador'),
            memoria_ram=data.get('memoria_ram'),
            armazenamento=data.get('armazenamento'),
            sistema_operacional=data.get('sistema_operacional'),
            status=data['status'],
            data_aquisicao=data_aquisicao,
            valor=float(data.get('valor', 0)) if data.get('valor') else None,
            observacoes=data.get('observacoes')
        )
        
        db.session.add(equipamento)
        db.session.flush()  # obter ID antes de possível foto

        # Foto (opcional)
        if is_multipart and 'foto' in request.files:
            foto_file = request.files.get('foto')
            if foto_file and foto_file.filename:
                url = _save_equip_photo(foto_file)
                if url:
                    # Desmarcar outras principais por segurança (novo equipamento não terá)
                    foto = EquipamentoFoto(equipamento_id=equipamento.id, url=url, principal=True)
                    db.session.add(foto)

        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Equipamento adicionado com sucesso!',
            'equipamento': equipamento.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao adicionar equipamento: {str(e)}'
        }), 400

@main.route('/equipamento/editar/<int:id>', methods=['PUT'])
@login_required
def editar_equipamento(id):
    """Edita um equipamento existente"""
    try:
        equipamento = Equipamento.query.get_or_404(id)
        is_multipart = request.content_type and 'multipart/form-data' in request.content_type
        if is_multipart:
            form = request.form
            data = {k: form.get(k) for k in form.keys()}
        else:
            data = request.get_json(silent=True) or {}
        
        # Atualiza os campos
        equipamento.nome = data.get('nome', equipamento.nome)
        equipamento.tipo = data.get('tipo', equipamento.tipo)
        equipamento.marca = data.get('marca', equipamento.marca)
        equipamento.modelo = data.get('modelo', equipamento.modelo)
        equipamento.numero_serie = data.get('numero_serie', equipamento.numero_serie)
        equipamento.processador = data.get('processador', equipamento.processador)
        equipamento.memoria_ram = data.get('memoria_ram', equipamento.memoria_ram)
        equipamento.armazenamento = data.get('armazenamento', equipamento.armazenamento)
        equipamento.sistema_operacional = data.get('sistema_operacional', equipamento.sistema_operacional)
        equipamento.status = data.get('status', equipamento.status)
        equipamento.observacoes = data.get('observacoes', equipamento.observacoes)
        
        if data.get('data_aquisicao'):
            equipamento.data_aquisicao = datetime.strptime(data['data_aquisicao'], '%Y-%m-%d').date()
        
        if data.get('valor'):
            equipamento.valor = float(data['valor'])

        # Substituição de foto (opcional)
        if is_multipart and 'foto' in request.files:
            foto_file = request.files.get('foto')
            if foto_file and foto_file.filename:
                url = _save_equip_photo(foto_file)
                if url:
                    # Desmarca anteriores como principal e adiciona nova principal
                    for f in equipamento.fotos:
                        f.principal = False
                    nova = EquipamentoFoto(equipamento_id=equipamento.id, url=url, principal=True)
                    db.session.add(nova)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Equipamento atualizado com sucesso!',
            'equipamento': equipamento.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar equipamento: {str(e)}'
        }), 400

@main.route('/equipamento/deletar/<int:id>', methods=['DELETE'])
@login_required
def deletar_equipamento(id):
    """Deleta um equipamento"""
    try:
        equipamento = Equipamento.query.get_or_404(id)
        db.session.delete(equipamento)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Equipamento deletado com sucesso!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar equipamento: {str(e)}'
        }), 400


@main.route('/equipamento/<int:id>/qrcode')
@login_required
def gerar_qrcode(id):
    """Gera QR Code para um equipamento"""
    try:
        equipamento = Equipamento.query.get_or_404(id)
        
        # Dados para o QR Code (ID e número de série)
        dados_qr = f"ID: {equipamento.id}\nNome: {equipamento.nome}\nN° Série: {equipamento.numero_serie}\nMarca: {equipamento.marca}\nModelo: {equipamento.modelo}"
        
        # Gera o QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(dados_qr)
        qr.make(fit=True)
        
        # Cria a imagem
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Converte para base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'qrcode': f'data:image/png;base64,{img_base64}',
            'equipamento': equipamento.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao gerar QR Code: {str(e)}'
        }), 400


# ===== ROTAS DE MANUTENÇÕES =====

@main.route('/equipamento/<int:equipamento_id>/manutencoes')
@login_required
def listar_manutencoes(equipamento_id):
    """Lista manutenções de um equipamento (mais recentes primeiro)"""
    try:
        equipamento = Equipamento.query.get_or_404(equipamento_id)
        manutencoes = Manutencao.query.filter_by(equipamento_id=equipamento.id).order_by(Manutencao.data_registro.desc()).all()
        return jsonify({'success': True, 'manutencoes': [m.to_dict() for m in manutencoes]})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao listar manutenções: {str(e)}'}), 400


@main.route('/equipamento/<int:equipamento_id>/manutencao/adicionar', methods=['POST'])
@login_required
def adicionar_manutencao(equipamento_id):
    """Adiciona uma manutenção ao equipamento"""
    try:
        equipamento = Equipamento.query.get_or_404(equipamento_id)
        data = request.get_json()

        # Parse datas e campos opcionais
        data_inicio = datetime.strptime(data['data_inicio'], '%Y-%m-%d').date() if data.get('data_inicio') else None
        data_fim = datetime.strptime(data['data_fim'], '%Y-%m-%d').date() if data.get('data_fim') else None
        custo = float(data['custo']) if data.get('custo') not in (None, '') else None

        manutencao = Manutencao(
            equipamento_id=equipamento.id,
            tipo=data.get('tipo', 'Corretiva'),
            descricao=data.get('descricao'),
            data_inicio=data_inicio,
            data_fim=data_fim,
            custo=custo,
            responsavel=data.get('responsavel'),
            fornecedor=data.get('fornecedor'),
            status=data.get('status', 'Em Andamento')
        )

        # Atualiza status do equipamento se solicitado
        if data.get('atualizar_status_equipamento', True):
            if manutencao.status == 'Em Andamento':
                equipamento.status = 'Manutenção'
            elif manutencao.status == 'Concluída' and equipamento.status == 'Manutenção':
                # Não forçamos retorno ao Estoque automaticamente sem contexto; opcional
                pass

        db.session.add(manutencao)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Manutenção registrada com sucesso!', 'manutencao': manutencao.to_dict()})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao adicionar manutenção: {str(e)}'}), 400


@main.route('/manutencao/deletar/<int:id>', methods=['DELETE'])
@login_required
def deletar_manutencao(id):
    """Remove um registro de manutenção"""
    try:
        manutencao = Manutencao.query.get_or_404(id)
        db.session.delete(manutencao)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Manutenção deletada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao deletar manutenção: {str(e)}'}), 400


@main.route('/manutencao/<int:id>', methods=['GET'])
@login_required
def obter_manutencao(id):
    """Obtém uma manutenção específica"""
    try:
        manutencao = Manutencao.query.get_or_404(id)
        return jsonify({'success': True, 'manutencao': manutencao.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao obter manutenção: {str(e)}'}), 400


@main.route('/manutencao/editar/<int:id>', methods=['PUT'])
@login_required
def editar_manutencao(id):
    """Edita uma manutenção existente"""
    try:
        manutencao = Manutencao.query.get_or_404(id)
        data = request.get_json()

        # Parse datas e campos
        if 'data_inicio' in data:
            manutencao.data_inicio = datetime.strptime(data['data_inicio'], '%Y-%m-%d').date() if data['data_inicio'] else None
        if 'data_fim' in data:
            manutencao.data_fim = datetime.strptime(data['data_fim'], '%Y-%m-%d').date() if data['data_fim'] else None
        if 'custo' in data:
            manutencao.custo = float(data['custo']) if data['custo'] not in (None, '') else None
        if 'tipo' in data:
            manutencao.tipo = data['tipo'] or manutencao.tipo
        if 'descricao' in data:
            manutencao.descricao = data['descricao']
        if 'responsavel' in data:
            manutencao.responsavel = data['responsavel']
        if 'fornecedor' in data:
            manutencao.fornecedor = data['fornecedor']
        if 'status' in data:
            manutencao.status = data['status'] or manutencao.status

        # Atualiza status do equipamento se solicitado
        if data.get('atualizar_status_equipamento', True):
            equipamento = Equipamento.query.get(manutencao.equipamento_id)
            if equipamento:
                if manutencao.status == 'Em Andamento':
                    equipamento.status = 'Manutenção'
                # Mantemos a lógica conservadora; não alteramos automaticamente em 'Concluída'

        db.session.commit()
        return jsonify({'success': True, 'message': 'Manutenção atualizada com sucesso!', 'manutencao': manutencao.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao atualizar manutenção: {str(e)}'}), 400


# ===== ROTAS DE EMPRÉSTIMOS =====

@main.route('/equipamentos-estoque')
@login_required
def listar_equipamentos_estoque():
    """Lista apenas equipamentos disponíveis em estoque"""
    equipamentos = Equipamento.query.filter_by(status='Estoque').order_by(Equipamento.nome).all()
    return jsonify([eq.to_dict() for eq in equipamentos])

@main.route('/emprestimos')
@login_required
def listar_emprestimos():
    """Lista todos os empréstimos"""
    emprestimos = Emprestimo.query.order_by(Emprestimo.data_emprestimo.desc()).all()
    return jsonify([emp.to_dict() for emp in emprestimos])

@main.route('/emprestimos-ativos')
@login_required
def listar_emprestimos_ativos():
    """Lista apenas empréstimos ativos"""
    emprestimos = Emprestimo.query.filter_by(status='Ativo').order_by(Emprestimo.data_emprestimo.desc()).all()
    return jsonify([emp.to_dict() for emp in emprestimos])

@main.route('/emprestimo/<int:id>')
@login_required
def obter_emprestimo(id):
    """Obtém um empréstimo específico"""
    emprestimo = Emprestimo.query.get_or_404(id)
    return jsonify(emprestimo.to_dict())

@main.route('/emprestimo/adicionar', methods=['POST'])
@login_required
def adicionar_emprestimo():
    """Registra um novo empréstimo"""
    try:
        data = request.json
        
        # Verifica se o equipamento existe e está em estoque
        equipamento = Equipamento.query.get(data['equipamento_id'])
        if not equipamento:
            return jsonify({
                'success': False,
                'message': 'Equipamento não encontrado'
            }), 404
            
        if equipamento.status != 'Estoque':
            return jsonify({
                'success': False,
                'message': f'Equipamento não está disponível. Status atual: {equipamento.status}'
            }), 400
        
        # Converte a data de devolução prevista se fornecida
        data_devolucao_prevista = None
        if data.get('data_devolucao_prevista'):
            data_devolucao_prevista = datetime.strptime(data['data_devolucao_prevista'], '%Y-%m-%d').date()
        
        # Cria o empréstimo
        emprestimo = Emprestimo(
            equipamento_id=data['equipamento_id'],
            responsavel=data['responsavel'],
            departamento=data['departamento'],
            email_responsavel=data.get('email_responsavel'),
            telefone_responsavel=data.get('telefone_responsavel'),
            data_devolucao_prevista=data_devolucao_prevista,
            observacoes=data.get('observacoes')
        )
        
        # Atualiza o status do equipamento para Emprestado
        equipamento.status = 'Emprestado'
        
        db.session.add(emprestimo)
        db.session.commit()
        
        # Envia e-mail de confirmação
        from app.email_service import enviar_email_confirmacao_emprestimo
        try:
            enviar_email_confirmacao_emprestimo(current_app._get_current_object(), emprestimo)
        except Exception as e:
            # Não falha a operação se o email não for enviado
            current_app.logger.warning(f'Falha ao enviar e-mail de confirmação: {str(e)}')
        
        return jsonify({
            'success': True,
            'message': 'Empréstimo registrado com sucesso!',
            'emprestimo': emprestimo.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao registrar empréstimo: {str(e)}'
        }), 400

@main.route('/emprestimo/devolver/<int:id>', methods=['PUT'])
@login_required
def devolver_emprestimo(id):
    """Registra a devolução de um empréstimo"""
    try:
        emprestimo = Emprestimo.query.get_or_404(id)
        
        if emprestimo.status == 'Devolvido':
            return jsonify({
                'success': False,
                'message': 'Este empréstimo já foi devolvido'
            }), 400
        
        # Registra a devolução
        emprestimo.data_devolucao_real = datetime.utcnow()
        emprestimo.status = 'Devolvido'
        
        # Atualiza o status do equipamento de volta para Estoque
        equipamento = Equipamento.query.get(emprestimo.equipamento_id)
        if equipamento:
            equipamento.status = 'Estoque'
        
        db.session.commit()
        
        # Envia e-mail de confirmação de devolução
        from app.email_service import enviar_email_confirmacao_devolucao
        try:
            enviar_email_confirmacao_devolucao(current_app._get_current_object(), emprestimo)
        except Exception as e:
            # Não falha a operação se o email não for enviado
            current_app.logger.warning(f'Falha ao enviar e-mail de devolução: {str(e)}')
        
        return jsonify({
            'success': True,
            'message': 'Devolução registrada com sucesso!',
            'emprestimo': emprestimo.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao registrar devolução: {str(e)}'
        }), 400

@main.route('/emprestimo/deletar/<int:id>', methods=['DELETE'])
@login_required
def deletar_emprestimo(id):
    """Deleta um empréstimo"""
    try:
        emprestimo = Emprestimo.query.get_or_404(id)
        
        # Se o empréstimo estava ativo, retorna o equipamento ao estoque
        if emprestimo.status == 'Ativo':
            equipamento = Equipamento.query.get(emprestimo.equipamento_id)
            if equipamento and equipamento.status == 'Emprestado':
                equipamento.status = 'Estoque'
        
        db.session.delete(emprestimo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Empréstimo deletado com sucesso!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar empréstimo: {str(e)}'
        }), 400


@main.route('/emprestimos/notificacoes')
@login_required
def emprestimos_notificacoes():
    """Retorna empréstimos próximos ao vencimento e atrasados"""
    try:
        dias_alerta = int(request.args.get('dias', 3))  # Padrão: 3 dias antes
        hoje = datetime.utcnow().date()
        data_limite = hoje + datetime.timedelta(days=dias_alerta)
        
        # Empréstimos ativos próximos ao vencimento (dentro dos próximos N dias)
        proximos_vencimento = Emprestimo.query.filter(
            Emprestimo.status == 'Ativo',
            Emprestimo.data_devolucao_prevista.isnot(None),
            Emprestimo.data_devolucao_prevista > hoje,
            Emprestimo.data_devolucao_prevista <= data_limite
        ).order_by(Emprestimo.data_devolucao_prevista).all()
        
        # Empréstimos atrasados (data prevista já passou)
        atrasados = Emprestimo.query.filter(
            Emprestimo.status == 'Ativo',
            Emprestimo.data_devolucao_prevista.isnot(None),
            Emprestimo.data_devolucao_prevista < hoje
        ).order_by(Emprestimo.data_devolucao_prevista).all()
        
        return jsonify({
            'success': True,
            'proximos_vencimento': [e.to_dict() for e in proximos_vencimento],
            'atrasados': [e.to_dict() for e in atrasados],
            'total_notificacoes': len(proximos_vencimento) + len(atrasados)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar notificações: {str(e)}'
        }), 400

# ==================== ROTAS DE RELATÓRIOS ====================

@main.route('/relatorios')
@login_required
def relatorios():
    """Página de relatórios de empréstimos"""
    return render_template('relatorios.html')

@main.route('/relatorios/emprestimos')
@login_required
def relatorios_emprestimos():
    """Retorna dados de empréstimos para relatórios"""
    try:
        filtro = request.args.get('filtro', 'todos')  # todos, ativos, historico, atrasados
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        departamento = request.args.get('departamento')
        
        # Query base com join para trazer equipamento junto
        query = Emprestimo.query.join(Equipamento, Emprestimo.equipamento_id == Equipamento.id)
        
        # Aplicar filtros
        if filtro == 'ativos':
            query = query.filter(Emprestimo.status == 'Ativo')
        elif filtro == 'historico':
            query = query.filter(Emprestimo.status == 'Devolvido')
        elif filtro == 'atrasados':
            hoje = datetime.utcnow().date()
            query = query.filter(
                Emprestimo.status == 'Ativo',
                Emprestimo.data_devolucao_prevista < hoje
            )
        
        # Filtro por período
        if data_inicio:
            data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(Emprestimo.data_emprestimo >= data_inicio_dt)
        
        if data_fim:
            data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
            # Adiciona 23:59:59 para incluir todo o dia
            data_fim_dt = data_fim_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(Emprestimo.data_emprestimo <= data_fim_dt)
        
        # Filtro por departamento
        if departamento and departamento != 'todos':
            query = query.filter(Emprestimo.departamento == departamento)
        
        # Ordenar por data de empréstimo (mais recentes primeiro)
        emprestimos = query.order_by(Emprestimo.data_emprestimo.desc()).all()
        
        # Calcular estatísticas
        hoje = datetime.utcnow().date()
        total_emprestimos = len(emprestimos)
        ativos = sum(1 for e in emprestimos if e.status == 'Ativo')
        devolvidos = sum(1 for e in emprestimos if e.status == 'Devolvido')
        atrasados = sum(1 for e in emprestimos if e.status == 'Ativo' and e.data_devolucao_prevista and e.data_devolucao_prevista < hoje)
        
        # Calcular duração média dos empréstimos devolvidos
        duracoes = []
        for e in emprestimos:
            if e.status == 'Devolvido' and e.data_devolucao_real:
                duracao = (e.data_devolucao_real - e.data_emprestimo).days
                duracoes.append(duracao)
        
        duracao_media = sum(duracoes) / len(duracoes) if duracoes else 0
        
        # Empréstimos por departamento
        emprestimos_por_dept = {}
        for e in emprestimos:
            dept = e.departamento or 'Não informado'
            emprestimos_por_dept[dept] = emprestimos_por_dept.get(dept, 0) + 1
        
        # Equipamentos mais emprestados
        equipamentos_count = {}
        for e in emprestimos:
            if e.equipamento:
                nome = e.equipamento.nome
                equipamentos_count[nome] = equipamentos_count.get(nome, 0) + 1
        
        # Top 10 equipamentos
        top_equipamentos = sorted(equipamentos_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return jsonify({
            'success': True,
            'emprestimos': [e.to_dict() for e in emprestimos],
            'estatisticas': {
                'total': total_emprestimos,
                'ativos': ativos,
                'devolvidos': devolvidos,
                'atrasados': atrasados,
                'duracao_media': round(duracao_media, 1)
            },
            'emprestimos_por_departamento': emprestimos_por_dept,
            'top_equipamentos': [{'nome': nome, 'quantidade': qtd} for nome, qtd in top_equipamentos]
        })
        
    except Exception as e:
        print(f"Erro ao gerar relatório: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro ao gerar relatório: {str(e)}'
        }), 400

@main.route('/relatorios/departamentos')
@login_required
def listar_departamentos():
    """Lista todos os departamentos únicos dos empréstimos"""
    try:
        departamentos = db.session.query(Emprestimo.departamento).distinct().filter(
            Emprestimo.departamento.isnot(None),
            Emprestimo.departamento != ''
        ).order_by(Emprestimo.departamento).all()
        
        return jsonify({
            'success': True,
            'departamentos': [d[0] for d in departamentos]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar departamentos: {str(e)}'
        }), 400

@main.route('/relatorios/exportar-pdf')
@login_required
def exportar_relatorio_pdf():
    """Exporta relatório de empréstimos em PDF"""
    try:
        filtro = request.args.get('filtro', 'todos')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        departamento = request.args.get('departamento')
        
        # Query base com join
        query = Emprestimo.query.join(Equipamento, Emprestimo.equipamento_id == Equipamento.id)
        
        # Aplicar filtros
        if filtro == 'ativos':
            query = query.filter(Emprestimo.status == 'Ativo')
        elif filtro == 'historico':
            query = query.filter(Emprestimo.status == 'Devolvido')
        elif filtro == 'atrasados':
            hoje = datetime.utcnow().date()
            query = query.filter(
                Emprestimo.status == 'Ativo',
                Emprestimo.data_devolucao_prevista < hoje
            )
        
        if data_inicio:
            data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(Emprestimo.data_emprestimo >= data_inicio_dt)
        
        if data_fim:
            data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
            data_fim_dt = data_fim_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(Emprestimo.data_emprestimo <= data_fim_dt)
        
        if departamento and departamento != 'todos':
            query = query.filter(Emprestimo.departamento == departamento)
        
        emprestimos = query.order_by(Emprestimo.data_emprestimo.desc()).all()
        
        # Calcular estatísticas
        hoje = datetime.utcnow().date()
        total = len(emprestimos)
        ativos = sum(1 for e in emprestimos if e.status == 'Ativo')
        devolvidos = sum(1 for e in emprestimos if e.status == 'Devolvido')
        atrasados = sum(1 for e in emprestimos if e.status == 'Ativo' and e.data_devolucao_prevista and e.data_devolucao_prevista < hoje)
        
        # Criar PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitulo_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.grey,
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        # Elementos do PDF
        elements = []
        
        # Título
        titulo = Paragraph("📊 Relatório de Empréstimos de Equipamentos", titulo_style)
        elements.append(titulo)
        
        # Data de geração
        data_geracao = datetime.now().strftime('%d/%m/%Y às %H:%M')
        subtitulo = Paragraph(f"Gerado em {data_geracao} por {current_user.nome}", subtitulo_style)
        elements.append(subtitulo)
        
        # Filtros aplicados
        filtros_texto = f"<b>Filtros:</b> Tipo: {filtro.capitalize()}"
        if departamento and departamento != 'todos':
            filtros_texto += f" | Departamento: {departamento}"
        if data_inicio:
            filtros_texto += f" | Início: {datetime.strptime(data_inicio, '%Y-%m-%d').strftime('%d/%m/%Y')}"
        if data_fim:
            filtros_texto += f" | Fim: {datetime.strptime(data_fim, '%Y-%m-%d').strftime('%d/%m/%Y')}"
        
        filtros_p = Paragraph(filtros_texto, styles['Normal'])
        elements.append(filtros_p)
        elements.append(Spacer(1, 0.5*cm))
        
        # Estatísticas
        stats_data = [
            ['Total', 'Ativos', 'Devolvidos', 'Atrasados'],
            [str(total), str(ativos), str(devolvidos), str(atrasados)]
        ]
        
        stats_table = Table(stats_data, colWidths=[5*cm, 5*cm, 5*cm, 5*cm])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 0.8*cm))
        
        # Tabela de empréstimos
        if emprestimos:
            # Cabeçalho
            table_data = [['Equipamento', 'Responsável', 'Depto', 'Data Emp.', 'Prev. Dev.', 'Status', 'Dias']]
            
            # Dados
            for e in emprestimos:
                equipamento_nome = e.equipamento.nome if e.equipamento else 'N/A'
                data_emp = e.data_emprestimo.strftime('%d/%m/%Y')
                prev_dev = e.data_devolucao_prevista.strftime('%d/%m/%Y') if e.data_devolucao_prevista else '-'
                
                # Status
                is_atrasado = e.status == 'Ativo' and e.data_devolucao_prevista and e.data_devolucao_prevista < hoje
                status_text = 'Atrasado' if is_atrasado else e.status
                
                # Dias
                if e.status == 'Ativo':
                    dias = (datetime.utcnow().date() - e.data_emprestimo.date()).days
                elif e.data_devolucao_real:
                    dias = (e.data_devolucao_real.date() - e.data_emprestimo.date()).days
                else:
                    dias = '-'
                
                table_data.append([
                    equipamento_nome[:25],
                    e.responsavel[:20],
                    (e.departamento or '-')[:15],
                    data_emp,
                    prev_dev,
                    status_text,
                    str(dias)
                ])
            
            # Criar tabela
            emprestimos_table = Table(table_data, colWidths=[5.5*cm, 4*cm, 3*cm, 2.5*cm, 2.5*cm, 2.5*cm, 1.5*cm])
            
            # Estilo da tabela
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (3, 0), (6, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]
            
            # Destacar linhas atrasadas
            for i, e in enumerate(emprestimos, 1):
                is_atrasado = e.status == 'Ativo' and e.data_devolucao_prevista and e.data_devolucao_prevista < hoje
                if is_atrasado:
                    table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#fee2e2')))
            
            emprestimos_table.setStyle(TableStyle(table_style))
            elements.append(emprestimos_table)
        else:
            elements.append(Paragraph("Nenhum empréstimo encontrado com os filtros aplicados.", styles['Normal']))
        
        # Rodapé
        elements.append(Spacer(1, 1*cm))
        rodape = Paragraph(
            f"<i>Sistema de Inventário de Equipamentos TI - {current_user.nome}</i>",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        )
        elements.append(rodape)
        
        # Gerar PDF
        doc.build(elements)
        
        # Preparar resposta
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        
        # Nome do arquivo
        data_arquivo = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f'relatorio_emprestimos_{filtro}_{data_arquivo}.pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={nome_arquivo}'
        
        buffer.close()
        return response
        
    except Exception as e:
        print(f"Erro ao gerar PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Erro ao gerar PDF: {str(e)}'
        }), 400

# ====== ROTAS DE E-MAIL ======

@main.route('/admin/email-status', methods=['GET'])
@login_required
@admin_required
def email_status():
    """Retorna o status da configuração de e-mail"""
    return jsonify({
        'enabled': current_app.config.get('MAIL_ENABLED', False),
        'server': current_app.config.get('MAIL_SERVER', ''),
        'port': current_app.config.get('MAIL_PORT', ''),
        'sender': current_app.config.get('MAIL_DEFAULT_SENDER', '')
    })

@main.route('/admin/testar-email', methods=['POST'])
@login_required
@admin_required
def testar_email():
    """Envia um e-mail de teste para verificar configuração"""
    try:
        data = request.json
        email_destino = data.get('email')
        
        if not email_destino:
            return jsonify({
                'success': False,
                'message': 'E-mail de destino não fornecido'
            }), 400
        
        if not current_app.config.get('MAIL_ENABLED'):
            return jsonify({
                'success': False,
                'message': 'Sistema de e-mail está desabilitado. Configure MAIL_ENABLED=true'
            }), 400
        
        from flask_mail import Mail, Message
        mail = Mail(current_app)
        
        msg = Message(
            subject='🧪 Teste de E-mail - Sistema de Inventário',
            recipients=[email_destino],
            html='''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #EF7D2D 0%, #D96B1F 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }
        .success { background: #d1fae5; border: 2px solid #10b981; padding: 15px; border-radius: 4px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🧪 Teste de E-mail</h2>
        </div>
        <div class="content">
            <div class="success">
                <h3>✅ Configuração de E-mail Funcionando!</h3>
            </div>
            
            <p>Se você está lendo este e-mail, significa que o sistema de notificações por e-mail está configurado corretamente.</p>
            
            <p><strong>Recursos habilitados:</strong></p>
            <ul>
                <li>✅ Confirmação de empréstimos</li>
                <li>✅ Confirmação de devoluções</li>
                <li>✅ Lembretes de devolução próxima (3 dias antes)</li>
                <li>✅ Alertas de empréstimos atrasados</li>
            </ul>
            
            <p><strong>Horário das verificações:</strong> Diariamente às 09:00</p>
            
            <p style="text-align: center; color: #666; font-size: 12px; margin-top: 30px;">
                Sistema de Inventário de Equipamentos TI - TrueSource
            </p>
        </div>
    </div>
</body>
</html>
            '''
        )
        
        mail.send(msg)
        
        return jsonify({
            'success': True,
            'message': f'E-mail de teste enviado com sucesso para {email_destino}'
        })
        
    except Exception as e:
        current_app.logger.error(f'Erro ao enviar e-mail de teste: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'Erro ao enviar e-mail: {str(e)}'
        }), 400


@main.route('/admin/email-configuracao')
@login_required
@admin_required
def email_configuracao():
    """Página de configuração de e-mail"""
    return render_template('email_config.html')


@main.route('/admin/email-config', methods=['GET'])
@login_required
@admin_required
def get_email_config():
    """Retorna a configuração atual de e-mail"""
    try:
        from app.config_manager import EmailConfigManager
        manager = EmailConfigManager()
        config = manager.load_config()
        
        return jsonify(config)
    except Exception as e:
        current_app.logger.error(f'Erro ao carregar configuração: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'Erro ao carregar configuração: {str(e)}'
        }), 400


@main.route('/admin/email-config', methods=['POST'])
@login_required
@admin_required
def save_email_config():
    """Salva a configuração de e-mail no arquivo .env"""
    try:
        from app.config_manager import EmailConfigManager
        
        data = request.json
        
        # Valida os campos obrigatórios
        if not data.get('MAIL_SERVER'):
            return jsonify({
                'success': False,
                'message': 'Servidor SMTP é obrigatório'
            }), 400
        
        if not data.get('MAIL_PORT'):
            return jsonify({
                'success': False,
                'message': 'Porta SMTP é obrigatória'
            }), 400
        
        if not data.get('MAIL_USERNAME'):
            return jsonify({
                'success': False,
                'message': 'E-mail de remetente é obrigatório'
            }), 400
        
        if not data.get('MAIL_PASSWORD'):
            return jsonify({
                'success': False,
                'message': 'Senha é obrigatória'
            }), 400
        
        # Salva a configuração no arquivo .env
        manager = EmailConfigManager()
        manager.save_config(data)
        
        # Aplica a configuração à aplicação atual (sem reiniciar)
        manager.apply_to_app(current_app, data)
        
        # Reinicializa o Flask-Mail com as novas configurações
        try:
            from flask_mail import Mail
            # Cria uma nova instância do Mail com a configuração atualizada
            mail = Mail(current_app)
        except Exception as mail_error:
            current_app.logger.warning(f'Não foi possível reinicializar Flask-Mail: {str(mail_error)}')
        
        return jsonify({
            'success': True,
            'message': 'Configurações salvas com sucesso! Para garantir que todas as mudanças sejam aplicadas, reinicie o servidor.'
        })
        
    except Exception as e:
        current_app.logger.error(f'Erro ao salvar configuração: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'Erro ao salvar configuração: {str(e)}'
        }), 400


# ==================== ROTAS DE PUSH NOTIFICATIONS ====================

@main.route('/push/vapid-public-key')
@login_required
def get_vapid_public_key():
    """Retorna a chave pública VAPID para subscrição de push"""
    public_key = os.environ.get('VAPID_PUBLIC_KEY', '')
    
    if not public_key:
        return jsonify({
            'success': False,
            'message': 'Chave pública VAPID não configurada'
        }), 400
    
    return jsonify({
        'success': True,
        'publicKey': public_key
    })

@main.route('/push/subscribe', methods=['POST'])
@login_required
def subscribe_push():
    """Salva uma nova subscrição de push notification"""
    try:
        from app.models import PushSubscription
        
        data = request.get_json()
        subscription = data.get('subscription')
        user_agent = data.get('userAgent', '')
        
        if not subscription:
            return jsonify({
                'success': False,
                'message': 'Dados de subscrição inválidos'
            }), 400
        
        endpoint = subscription.get('endpoint')
        keys = subscription.get('keys', {})
        p256dh = keys.get('p256dh')
        auth = keys.get('auth')
        
        if not endpoint or not p256dh or not auth:
            return jsonify({
                'success': False,
                'message': 'Dados de subscrição incompletos'
            }), 400
        
        # Verifica se já existe uma subscrição com esse endpoint
        existing = PushSubscription.query.filter_by(endpoint=endpoint).first()
        
        if existing:
            # Atualiza a subscrição existente
            existing.usuario_id = current_user.id
            existing.p256dh = p256dh
            existing.auth = auth
            existing.user_agent = user_agent
            existing.ativa = True
            existing.data_criacao = datetime.utcnow()
        else:
            # Cria nova subscrição
            new_subscription = PushSubscription(
                usuario_id=current_user.id,
                endpoint=endpoint,
                p256dh=p256dh,
                auth=auth,
                user_agent=user_agent
            )
            db.session.add(new_subscription)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Subscrição salva com sucesso'
        })
        
    except Exception as e:
        current_app.logger.error(f'Erro ao salvar subscrição: {str(e)}')
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao salvar subscrição: {str(e)}'
        }), 400

@main.route('/push/unsubscribe', methods=['POST'])
@login_required
def unsubscribe_push():
    """Remove uma subscrição de push notification"""
    try:
        from app.models import PushSubscription
        
        data = request.get_json()
        endpoint = data.get('endpoint')
        
        if not endpoint:
            return jsonify({
                'success': False,
                'message': 'Endpoint não fornecido'
            }), 400
        
        # Busca e remove a subscrição
        subscription = PushSubscription.query.filter_by(
            endpoint=endpoint,
            usuario_id=current_user.id
        ).first()
        
        if subscription:
            db.session.delete(subscription)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Subscrição removida com sucesso'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Subscrição não encontrada'
            }), 404
            
    except Exception as e:
        current_app.logger.error(f'Erro ao remover subscrição: {str(e)}')
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao remover subscrição: {str(e)}'
        }), 400

@main.route('/push/test', methods=['POST'])
@login_required
def test_push():
    """Envia uma notificação de teste para o usuário atual"""
    try:
        from app.push_service import PushNotificationService
        
        count = PushNotificationService.send_to_user(
            usuario_id=current_user.id,
            title='Teste de Notificação',
            body='Esta é uma notificação de teste do Sistema de Inventário TI! 🔔',
            url='/',
            tag='test'
        )
        
        if count > 0:
            return jsonify({
                'success': True,
                'message': f'Notificação de teste enviada para {count} dispositivo(s)'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Não foi possível enviar a notificação. Verifique se você está inscrito para receber notificações.'
            }), 400
            
    except Exception as e:
        current_app.logger.error(f'Erro ao enviar notificação de teste: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'Erro ao enviar notificação: {str(e)}'
        }), 400

@main.route('/admin/push/broadcast', methods=['POST'])
@admin_required
def broadcast_push():
    """Envia uma notificação para todos os usuários (apenas admin)"""
    try:
        from app.push_service import PushNotificationService
        
        data = request.get_json()
        title = data.get('title', 'Inventário TI')
        body = data.get('body')
        url = data.get('url', '/')
        
        if not body:
            return jsonify({
                'success': False,
                'message': 'Mensagem é obrigatória'
            }), 400
        
        count = PushNotificationService.send_to_all_users(
            title=title,
            body=body,
            url=url,
            tag='broadcast'
        )
        
        return jsonify({
            'success': True,
            'message': f'Notificação enviada para {count} usuário(s)'
        })
        
    except Exception as e:
        current_app.logger.error(f'Erro ao enviar broadcast: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'Erro ao enviar notificação: {str(e)}'
        }), 400


# ==================== ROTAS DE WHATSAPP ====================

@main.route('/whatsapp/test', methods=['POST'])
@login_required
def test_whatsapp():
    """Envia uma mensagem de teste via WhatsApp"""
    try:
        from app.whatsapp_service import WhatsAppService
        
        data = request.get_json()
        phone = data.get('phone')
        
        current_app.logger.info(f'Teste WhatsApp - Telefone: {phone}')
        current_app.logger.info(f'WhatsApp Enabled: {WhatsAppService.is_enabled()}')
        current_app.logger.info(f'WhatsApp Provider: {WhatsAppService.get_provider()}')
        
        if not phone:
            return jsonify({
                'success': False,
                'message': 'Número de telefone é obrigatório'
            }), 400
        
        # Verifica se está habilitado
        if not WhatsAppService.is_enabled():
            return jsonify({
                'success': False,
                'message': 'WhatsApp não está habilitado. Configure e habilite na página de configuração.'
            }), 400
        
        result = WhatsAppService.send_test_message(phone)
        
        current_app.logger.info(f'Resultado do teste: {result}')
        
        # Adiciona detalhes formatados na mensagem se houver
        if not result['success'] and 'details' in result:
            result['message'] = f"{result['message']}\n\nDetalhes: {result['details']}"
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        current_app.logger.error(f'Erro ao enviar teste WhatsApp: {str(e)}\n{error_details}')
        return jsonify({
            'success': False,
            'message': f'Erro ao enviar teste: {str(e)}'
        }), 500

@main.route('/admin/whatsapp/status')
@admin_required
def whatsapp_status():
    """Retorna o status da configuração do WhatsApp"""
    try:
        from app.whatsapp_service import WhatsAppService
        
        enabled = WhatsAppService.is_enabled()
        provider = WhatsAppService.get_provider()
        
        # Verifica quais credenciais estão configuradas
        credentials_ok = False
        
        if provider == 'twilio':
            credentials_ok = bool(
                WhatsAppService._get_config_value('TWILIO_ACCOUNT_SID') and
                WhatsAppService._get_config_value('TWILIO_AUTH_TOKEN') and
                WhatsAppService._get_config_value('TWILIO_WHATSAPP_NUMBER')
            )
        elif provider == 'messagebird':
            credentials_ok = bool(
                WhatsAppService._get_config_value('MESSAGEBIRD_API_KEY') and
                WhatsAppService._get_config_value('MESSAGEBIRD_CHANNEL_ID')
            )
        elif provider == 'meta':
            credentials_ok = bool(
                WhatsAppService._get_config_value('META_ACCESS_TOKEN') and
                WhatsAppService._get_config_value('META_PHONE_NUMBER_ID')
            )
        
        return jsonify({
            'success': True,
            'enabled': enabled,
            'provider': provider,
            'configured': credentials_ok
        })
        
    except Exception as e:
        current_app.logger.error(f'Erro ao verificar status WhatsApp: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'Erro ao verificar status: {str(e)}'
        }), 400

@main.route('/admin/whatsapp-configuracao')
@admin_required
def whatsapp_configuracao():
    """Página de configuração do WhatsApp"""
    return render_template('whatsapp_config.html')

@main.route('/admin/whatsapp-config', methods=['GET', 'POST'])
@admin_required
def whatsapp_config():
    """Gerencia configurações do WhatsApp"""
    from app.config_manager import ConfigManager
    
    if request.method == 'GET':
        # Retorna configurações atuais
        config = ConfigManager.get_config()
        
        # Filtra apenas as configurações do WhatsApp
        whatsapp_config = {
            'WHATSAPP_ENABLED': config.get('WHATSAPP_ENABLED', 'false'),
            'WHATSAPP_PROVIDER': config.get('WHATSAPP_PROVIDER', ''),
            'TWILIO_ACCOUNT_SID': config.get('TWILIO_ACCOUNT_SID', ''),
            'TWILIO_AUTH_TOKEN': config.get('TWILIO_AUTH_TOKEN', ''),
            'TWILIO_WHATSAPP_NUMBER': config.get('TWILIO_WHATSAPP_NUMBER', ''),
            'MESSAGEBIRD_API_KEY': config.get('MESSAGEBIRD_API_KEY', ''),
            'MESSAGEBIRD_CHANNEL_ID': config.get('MESSAGEBIRD_CHANNEL_ID', ''),
            'META_ACCESS_TOKEN': config.get('META_ACCESS_TOKEN', ''),
            'META_PHONE_NUMBER_ID': config.get('META_PHONE_NUMBER_ID', '')
        }
        
        return jsonify(whatsapp_config)
    
    elif request.method == 'POST':
        # Salva novas configurações
        try:
            new_config = request.get_json()
            
            current_app.logger.info(f'Recebendo configurações: {new_config}')
            
            # Valida dados
            if not new_config:
                return jsonify({
                    'success': False,
                    'message': 'Dados de configuração não fornecidos'
                }), 400
            
            # Salva configurações
            success = ConfigManager.save_config(new_config)
            
            current_app.logger.info(f'Resultado do salvamento: {success}')
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Configurações salvas com sucesso'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Erro ao salvar configurações no arquivo'
                }), 500
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            current_app.logger.error(f'Erro ao salvar configurações WhatsApp: {str(e)}\n{error_details}')
            return jsonify({
                'success': False,
                'message': f'Erro ao salvar: {str(e)}'
            }), 500
