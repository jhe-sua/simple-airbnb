from flask import Blueprint, render_template, request, redirect, url_for
from db import get_connection
from datetime import datetime

hospede_bp = Blueprint('hospede', __name__, url_prefix='/hospede')

HOSPEDE_ID = 1 

@hospede_bp.route('/')
def dashboard():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM USUARIO WHERE UsrID = %s;", (HOSPEDE_ID,))
    perfil = cur.fetchone()
    
    cur.execute("SELECT * FROM TELEFONE WHERE UsrID = %s;", (HOSPEDE_ID,))
    telefones = cur.fetchall()
    
    query_catalogo = """
        SELECT an.AnID, an.AnTitulo, an.AnDesc, an.AnCustoDiaUtil, 
               ac.AcCapacPessoa, ac.AcQtdQuartos, ac.AcQtdBanheiros,
               endr.EndComplemento, cep.CepCidade, cep.CepEstado,
               (SELECT string_agg(c.ComNome, ', ') 
                FROM ACPOSSUICOM acp 
                JOIN COMODIDADE c ON acp.ComID = c.ComID 
                WHERE acp.AcID = ac.AcID) as comodidades,
               (SELECT json_agg(json_build_object('nota', av.AvNota, 'comentario', av.AvComentario)) 
                FROM AVALIACAO av 
                WHERE av.AnID = an.AnID AND av.TipoAvID = 1) as avaliacoes
        FROM ANUNCIO an
        JOIN ACOMODACAO ac ON an.AnID = ac.AnID
        JOIN ENDERECO endr ON ac.EndID = endr.EndID
        JOIN CEP cep ON endr.CepID = cep.CepID;
    """
    cur.execute(query_catalogo)
    catalogo = cur.fetchall()

    query_reservas = """
        SELECT r.ResID, r.ResDtIn, r.ResDtOut, r.ResStatus, a.AnTitulo, a.AnID
        FROM RESERVA r
        JOIN ANUNCIO a ON r.AnID = a.AnID
        WHERE r.HosUsrID = %s
        ORDER BY r.ResDtIn DESC;
    """
    cur.execute(query_reservas, (HOSPEDE_ID,))
    reservas = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('hospede.html', perfil=perfil, telefones=telefones, catalogo=catalogo, reservas=reservas)

@hospede_bp.route('/perfil/atualizar', methods=['POST'])
def atualizar_perfil():
    nome = request.form['UsrNome']
    cpf = request.form['UsrCPF']
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE USUARIO SET UsrNome = %s, UsrCPF = %s WHERE UsrID = %s;", (nome, cpf, HOSPEDE_ID))
    conn.commit()
    conn.close()
    return redirect(url_for('hospede.dashboard'))

@hospede_bp.route('/telefone/adicionar', methods=['POST'])
def adicionar_telefone():
    numero = request.form['TlfNumero']
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(TlfID), 0) + 1 AS prox_id FROM TELEFONE;")
    prox_id = cur.fetchone()['prox_id']
    cur.execute("INSERT INTO TELEFONE (TlfID, TlfNumero, UsrID) VALUES (%s, %s, %s);", (prox_id, numero, HOSPEDE_ID))
    conn.commit()
    conn.close()
    return redirect(url_for('hospede.dashboard'))

@hospede_bp.route('/telefone/deletar/<int:tlf_id>', methods=['POST'])
def deletar_telefone(tlf_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM TELEFONE WHERE TlfID = %s AND UsrID = %s;", (tlf_id, HOSPEDE_ID))
    conn.commit()
    conn.close()
    return redirect(url_for('hospede.dashboard'))

# ==========================================
# ATUALIZAÇÃO: ADICIONADOS OS NOVOS CAMPOS DE RESERVA
# ==========================================
@hospede_bp.route('/reserva/nova', methods=['POST'])
def criar_reserva():
    an_id = request.form['AnID']
    dt_in = request.form['ResDtIn']
    dt_out = request.form['ResDtOut']
    qtd_adultos = request.form['ResQtdAdultos']
    
    # Capturando os novos inputs do formulário
    qtd_criancas = request.form.get('ResQtdCriancas', 0)
    qtd_bebes = request.form.get('ResQtdBebes', 0)
    qtd_pets = request.form.get('ResQtdPets', 0)
    forma_paga = request.form['ResFormaPaga']
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(ResID), 0) + 1 AS prox_id FROM RESERVA;")
    prox_id = cur.fetchone()['prox_id']
    
    # Inserção completa com todas as colunas preenchidas pelo usuário
    query = """
        INSERT INTO RESERVA (ResID, ResDtIn, ResDtOut, ResStatus, ResFormaPaga, 
                             ResQtdAdultos, ResQtdCriancas, ResQtdBebes, ResQtdPets, HosUsrID, AnID)
        VALUES (%s, %s, %s, 'Confirmada', %s, %s, %s, %s, %s, %s, %s);
    """
    cur.execute(query, (prox_id, dt_in, dt_out, forma_paga, 
                        qtd_adultos, qtd_criancas, qtd_bebes, qtd_pets, HOSPEDE_ID, an_id))
    conn.commit()
    conn.close()
    return redirect(url_for('hospede.dashboard'))

@hospede_bp.route('/reserva/cancelar/<int:res_id>', methods=['POST'])
def cancelar_reserva(res_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE RESERVA SET ResStatus = 'Cancelada' WHERE ResID = %s AND HosUsrID = %s AND ResStatus != 'Cancelada';", (res_id, HOSPEDE_ID))
    conn.commit()
    conn.close()
    return redirect(url_for('hospede.dashboard'))

@hospede_bp.route('/avaliacao/nova', methods=['POST'])
def criar_avaliacao():
    an_id = request.form['AnID']
    res_id = request.form['ResID'] # NOVO: Captura qual reserva exata gerou a avaliação
    nota = request.form['AvNota']
    comentario = request.form['AvComentario']
    hoje = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Gera o ID da avaliação
    cur.execute("SELECT COALESCE(MAX(AvID), 0) + 1 AS prox_id FROM AVALIACAO;")
    prox_id = cur.fetchone()['prox_id']
    
    # Descobre quem é o dono do anúncio
    cur.execute("SELECT AnfUsrID FROM ANUNCIO WHERE AnID = %s;", (an_id,))
    anf_id = cur.fetchone()['anfusrid']
    
    # 1. Insere a avaliação normalmente
    query_insert = """
        INSERT INTO AVALIACAO (AvID, AvNota, AvComentario, AvData, TipoAvID, AnID, AnfUsrID, HosUsrID)
        VALUES (%s, %s, %s, %s, 1, %s, %s, %s);
    """
    cur.execute(query_insert, (prox_id, nota, comentario, hoje, an_id, anf_id, HOSPEDE_ID))
    
    # 2. O TRUQUE: Muda o status daquela reserva específica para que ela não possa ser reavaliada
    cur.execute("UPDATE RESERVA SET ResStatus = 'Avaliada' WHERE ResID = %s;", (res_id,))
    
    conn.commit()
    conn.close()
    return redirect(url_for('hospede.dashboard'))