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
    
    # Verifica com base no ResID se já existe avaliação do Tipo 1 (Hóspede -> Anúncio)
    query_reservas = """
        SELECT r.ResID, r.ResDtIn, r.ResDtOut, r.ResStatus, a.AnTitulo, a.AnID,
               EXISTS (
                   SELECT 1 FROM AVALIACAO av 
                   WHERE av.ResID = r.ResID AND av.TipoAvID = 1
               ) as ja_avaliou
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
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE USUARIO SET UsrNome = %s, UsrCPF = %s WHERE UsrID = %s;", (request.form['UsrNome'], request.form['UsrCPF'], HOSPEDE_ID))
    conn.commit(); conn.close()
    return redirect(url_for('hospede.dashboard'))

@hospede_bp.route('/telefone/adicionar', methods=['POST'])
def adicionar_telefone():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(TlfID), 0) + 1 AS prox_id FROM TELEFONE;")
    cur.execute("INSERT INTO TELEFONE (TlfID, TlfNumero, UsrID) VALUES (%s, %s, %s);", (cur.fetchone()['prox_id'], request.form['TlfNumero'], HOSPEDE_ID))
    conn.commit(); conn.close()
    return redirect(url_for('hospede.dashboard'))

@hospede_bp.route('/telefone/deletar/<int:tlf_id>', methods=['POST'])
def deletar_telefone(tlf_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM TELEFONE WHERE TlfID = %s AND UsrID = %s;", (tlf_id, HOSPEDE_ID))
    conn.commit(); conn.close()
    return redirect(url_for('hospede.dashboard'))

@hospede_bp.route('/reserva/nova', methods=['POST'])
def criar_reserva():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(ResID), 0) + 1 AS prox_id FROM RESERVA;")
    prox_id = cur.fetchone()['prox_id']
    query = """
        INSERT INTO RESERVA (ResID, ResDtIn, ResDtOut, ResStatus, ResFormaPaga, 
                             ResQtdAdultos, ResQtdCriancas, ResQtdBebes, ResQtdPets, HosUsrID, AnID)
        VALUES (%s, %s, %s, 'Confirmada', %s, %s, %s, %s, %s, %s, %s);
    """
    cur.execute(query, (prox_id, request.form['ResDtIn'], request.form['ResDtOut'], request.form['ResFormaPaga'], 
                        request.form['ResQtdAdultos'], request.form.get('ResQtdCriancas', 0), 
                        request.form.get('ResQtdBebes', 0), request.form.get('ResQtdPets', 0), HOSPEDE_ID, request.form['AnID']))
    conn.commit(); conn.close()
    return redirect(url_for('hospede.dashboard'))

@hospede_bp.route('/reserva/cancelar/<int:res_id>', methods=['POST'])
def cancelar_reserva(res_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE RESERVA SET ResStatus = 'Cancelada' WHERE ResID = %s AND HosUsrID = %s;", (res_id, HOSPEDE_ID))
    conn.commit(); conn.close()
    return redirect(url_for('hospede.dashboard'))

@hospede_bp.route('/avaliacao/nova', methods=['POST'])
def criar_avaliacao():
    """Gera em simultâneo a avaliação do Anúncio (Tipo 1) e do Anfitrião (Tipo 2)."""
    an_id = request.form['AnID']
    res_id = request.form['ResID']
    hoje = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT AnfUsrID FROM ANUNCIO WHERE AnID = %s;", (an_id,))
    anf_id = cur.fetchone()['anfusrid']
    
    # 1. Inserir Avaliação do Espaço (TipoAvID = 1)
    cur.execute("SELECT COALESCE(MAX(AvID), 0) + 1 AS prox_id FROM AVALIACAO;")
    id_anuncio = cur.fetchone()['prox_id']
    cur.execute("""
        INSERT INTO AVALIACAO (AvID, AvNota, AvComentario, AvData, AnID, AnfUsrID, HosUsrID, TipoAvID, ResID)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 1, %s);
    """, (id_anuncio, request.form['AvNotaAnuncio'], request.form['AvComentarioAnuncio'], hoje, an_id, anf_id, HOSPEDE_ID, res_id))
    
    # 2. Inserir Avaliação do Anfitrião (TipoAvID = 2)
    cur.execute("SELECT COALESCE(MAX(AvID), 0) + 1 AS prox_id FROM AVALIACAO;")
    id_anfitriao = cur.fetchone()['prox_id']
    cur.execute("""
        INSERT INTO AVALIACAO (AvID, AvNota, AvComentario, AvData, AnID, AnfUsrID, HosUsrID, TipoAvID, ResID)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 2, %s);
    """, (id_anfitriao, request.form['AvNotaAnfitriao'], request.form['AvComentarioAnfitriao'], hoje, an_id, anf_id, HOSPEDE_ID, res_id))
    
    conn.commit()
    conn.close()
    return redirect(url_for('hospede.dashboard'))