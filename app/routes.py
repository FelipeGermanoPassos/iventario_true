from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, Equipamento, Emprestimo, Usuario
from datetime import datetime
from sqlalchemy import func
from functools import wraps

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

# ==================== ROTAS PRINCIPAIS ====================

@main.route('/')
@login_required
def index():
    """Página principal com dashboard"""
    return render_template('index.html')

@main.route('/dashboard-data')
@login_required
def dashboard_data():
    """Retorna dados para o dashboard"""
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
    
    # Valor total do inventário
    valor_total = db.session.query(func.sum(Equipamento.valor)).scalar() or 0
    
    return jsonify({
        'total_equipamentos': total_equipamentos,
        'equipamentos_estoque': equipamentos_estoque,
        'equipamentos_emprestados': equipamentos_emprestados,
        'status': [{'name': s[0], 'value': s[1]} for s in status_data],
        'tipos': [{'name': t[0], 'value': t[1]} for t in tipo_data],
        'valor_total': float(valor_total)
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

@main.route('/equipamento/adicionar', methods=['POST'])
@login_required
def adicionar_equipamento():
    """Adiciona um novo equipamento"""
    try:
        data = request.json
        
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
        data = request.json
        
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
