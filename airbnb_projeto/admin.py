from flask import Blueprint, render_template, request, redirect, url_for
from db import get_connection
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def dashboard():
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. Dados de Domínio
    cur.execute("SELECT ComID, ComNome FROM COMODIDADE ORDER BY ComID;")
    comodidades = cur.fetchall()
    
    cur.execute("SELECT TipoAvID, TipoAvStr FROM TIPOAV ORDER BY TipoAvID;")
    tipos_av = cur.fetchall()
    
    # 2. Moderação (Anúncios e Avaliações)
    query_anuncios = "SELECT an.AnID, an.AnTitulo, u.UsrNome AS AnfitriaoNome FROM ANUNCIO an JOIN USUARIO u ON an.AnfUsrID = u.UsrID ORDER BY an.AnID DESC;"
    cur.execute(query_anuncios)
    anuncios = cur.fetchall()
    
    query_avaliacoes = "SELECT av.AvID, av.AvNota, av.AvComentario, av.TipoAvID, a.AnTitulo FROM AVALIACAO av JOIN ANUNCIO a ON av.AnID = a.AnID ORDER BY av.AvID DESC;"
    cur.execute(query_avaliacoes)
    avaliacoes = cur.fetchall()
    
    # 3. Suporte ao Cliente (Usuários e Reservas)
    # CORREÇÃO: Agora buscamos os papéis do usuário (Hóspede / Anfitrião)
    query_usuarios = """
        SELECT u.UsrID, u.UsrNome, u.UsrCPF, u.UsrDtNasc,
               (CASE WHEN h.UsrID IS NOT NULL THEN 1 ELSE 0 END) as is_hospede,
               (CASE WHEN a.UsrID IS NOT NULL THEN 1 ELSE 0 END) as is_anfitriao
        FROM USUARIO u
        LEFT JOIN HOSPEDE h ON u.UsrID = h.UsrID
        LEFT JOIN ANFITRIAO a ON u.UsrID = a.UsrID
        ORDER BY u.UsrID DESC;
    """
    cur.execute(query_usuarios)
    usuarios = cur.fetchall()
    
    query_reservas = """
        SELECT r.ResID, r.ResDtIn, r.ResDtOut, r.ResStatus, r.ResFormaPaga, r.ResDataPaga,
               a.AnTitulo, u.UsrNome AS HospedeNome
        FROM RESERVA r JOIN ANUNCIO a ON r.AnID = a.AnID JOIN USUARIO u ON r.HosUsrID = u.UsrID
        ORDER BY r.ResID DESC;
    """
    cur.execute(query_reservas)
    reservas = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin.html', 
                           comodidades=comodidades, tipos_av=tipos_av, 
                           anuncios=anuncios, avaliacoes=avaliacoes,
                           usuarios=usuarios, reservas=reservas)

# ==========================================
# ROTAS DE DOMÍNIO E MODERAÇÃO (Mantidas iguais)
# ==========================================
@admin_bp.route('/comodidade/nova', methods=['POST'])
def nova_comodidade():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(ComID), 0) + 1 AS prox_id FROM COMODIDADE;")
    cur.execute("INSERT INTO COMODIDADE (ComID, ComNome) VALUES (%s, %s);", (cur.fetchone()['prox_id'], request.form['ComNome']))
    conn.commit(); conn.close(); return redirect(url_for('admin.dashboard'))

@admin_bp.route('/comodidade/editar/<int:com_id>', methods=['POST'])
def editar_comodidade(com_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("UPDATE COMODIDADE SET ComNome = %s WHERE ComID = %s;", (request.form['ComNome'], com_id))
    conn.commit(); conn.close(); return redirect(url_for('admin.dashboard'))

@admin_bp.route('/comodidade/deletar/<int:com_id>', methods=['POST'])
def deletar_comodidade(com_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM COMODIDADE WHERE ComID = %s;", (com_id,))
    conn.commit(); conn.close(); return redirect(url_for('admin.dashboard'))

@admin_bp.route('/tipoav/novo', methods=['POST'])
def novo_tipoav():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(TipoAvID), 0) + 1 AS prox_id FROM TIPOAV;")
    cur.execute("INSERT INTO TIPOAV (TipoAvID, TipoAvStr) VALUES (%s, %s);", (cur.fetchone()['prox_id'], request.form['TipoAvStr']))
    conn.commit(); conn.close(); return redirect(url_for('admin.dashboard'))

@admin_bp.route('/moderacao/avaliacao/deletar/<int:av_id>', methods=['POST'])
def deletar_avaliacao(av_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM AVALIACAO WHERE AvID = %s;", (av_id,))
    conn.commit(); conn.close(); return redirect(url_for('admin.dashboard'))

@admin_bp.route('/moderacao/anuncio/deletar/<int:an_id>', methods=['POST'])
def deletar_anuncio_fraude(an_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM ANUNCIO WHERE AnID = %s;", (an_id,))
    conn.commit(); conn.close(); return redirect(url_for('admin.dashboard'))

# ==========================================
# GESTÃO COMPLETA DE USUÁRIOS (NOVO)
# ==========================================
@admin_bp.route('/suporte/usuario/novo', methods=['POST'])
def novo_usuario():
    """Registra um novo usuário e já atribui os papéis selecionados."""
    conn = get_connection()
    cur = conn.cursor()
    hoje = datetime.now().strftime('%Y-%m-%d')
    try:
        cur.execute("SELECT COALESCE(MAX(UsrID), 0) + 1 AS prox_id FROM USUARIO;")
        usr_id = cur.fetchone()['prox_id']
        
        cur.execute("INSERT INTO USUARIO (UsrID, UsrNome, UsrCPF, UsrDtNasc) VALUES (%s, %s, %s, %s);",
                    (usr_id, request.form['UsrNome'], request.form['UsrCPF'], request.form['UsrDtNasc']))
        
        if 'role_hospede' in request.form:
            cur.execute("INSERT INTO HOSPEDE (UsrID, HosDataInicio) VALUES (%s, %s);", (usr_id, hoje))
            
        if 'role_anfitriao' in request.form:
            cur.execute("INSERT INTO ANFITRIAO (UsrID, AnfDataInicio) VALUES (%s, %s);", (usr_id, hoje))
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(e)
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/suporte/usuario/editar/<int:usr_id>', methods=['POST'])
def editar_usuario(usr_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("UPDATE USUARIO SET UsrNome = %s, UsrCPF = %s WHERE UsrID = %s;", (request.form['UsrNome'], request.form['UsrCPF'], usr_id))
    conn.commit(); conn.close(); return redirect(url_for('admin.dashboard'))

@admin_bp.route('/suporte/usuario/papeis/<int:usr_id>', methods=['POST'])
def atualizar_papeis(usr_id):
    """Adiciona papel de Hóspede ou Anfitrião a um usuário existente."""
    conn = get_connection()
    cur = conn.cursor()
    hoje = datetime.now().strftime('%Y-%m-%d')
    
    if 'role_hospede' in request.form:
        cur.execute("INSERT INTO HOSPEDE (UsrID, HosDataInicio) VALUES (%s, %s) ON CONFLICT (UsrID) DO NOTHING;", (usr_id, hoje))
        
    if 'role_anfitriao' in request.form:
        cur.execute("INSERT INTO ANFITRIAO (UsrID, AnfDataInicio) VALUES (%s, %s) ON CONFLICT (UsrID) DO NOTHING;", (usr_id, hoje))
        
    conn.commit()
    conn.close()
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/suporte/usuario/deletar/<int:usr_id>', methods=['POST'])
def banir_usuario(usr_id):
    """Deleta o usuário. O banco se encarregará de apagar em cascata o que for permitido."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM USUARIO WHERE UsrID = %s;", (usr_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        # Nota: Se o banco reclamar de chaves estrangeiras sem ON DELETE CASCADE 
        # (ex: em Reservas), a exclusão falhará, protegendo a integridade.
        print(f"Não foi possível banir devido a dependências: {e}")
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/suporte/reserva/editar/<int:res_id>', methods=['POST'])
def editar_reserva(res_id):
    status = request.form['ResStatus']
    forma_paga = request.form['ResFormaPaga']
    data_paga = request.form['ResDataPaga'] if request.form['ResDataPaga'] else None
    
    conn = get_connection(); cur = conn.cursor()
    cur.execute("UPDATE RESERVA SET ResStatus = %s, ResFormaPaga = %s, ResDataPaga = %s WHERE ResID = %s;", 
                (status, forma_paga, data_paga, res_id))
    conn.commit(); conn.close(); return redirect(url_for('admin.dashboard'))