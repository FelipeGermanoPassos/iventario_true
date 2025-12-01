from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import db, Equipamento, Emprestimo
from datetime import datetime
from sqlalchemy import func

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Página principal com dashboard"""
    return render_template('index.html')

@main.route('/dashboard-data')
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
def listar_equipamentos():
    """Lista todos os equipamentos"""
    equipamentos = Equipamento.query.order_by(Equipamento.data_cadastro.desc()).all()
    return jsonify([eq.to_dict() for eq in equipamentos])

@main.route('/equipamento/<int:id>')
def obter_equipamento(id):
    """Obtém um equipamento específico"""
    equipamento = Equipamento.query.get_or_404(id)
    return jsonify(equipamento.to_dict())

@main.route('/equipamento/adicionar', methods=['POST'])
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
def listar_equipamentos_estoque():
    """Lista apenas equipamentos disponíveis em estoque"""
    equipamentos = Equipamento.query.filter_by(status='Estoque').order_by(Equipamento.nome).all()
    return jsonify([eq.to_dict() for eq in equipamentos])

@main.route('/emprestimos')
def listar_emprestimos():
    """Lista todos os empréstimos"""
    emprestimos = Emprestimo.query.order_by(Emprestimo.data_emprestimo.desc()).all()
    return jsonify([emp.to_dict() for emp in emprestimos])

@main.route('/emprestimos-ativos')
def listar_emprestimos_ativos():
    """Lista apenas empréstimos ativos"""
    emprestimos = Emprestimo.query.filter_by(status='Ativo').order_by(Emprestimo.data_emprestimo.desc()).all()
    return jsonify([emp.to_dict() for emp in emprestimos])

@main.route('/emprestimo/<int:id>')
def obter_emprestimo(id):
    """Obtém um empréstimo específico"""
    emprestimo = Emprestimo.query.get_or_404(id)
    return jsonify(emprestimo.to_dict())

@main.route('/emprestimo/adicionar', methods=['POST'])
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
