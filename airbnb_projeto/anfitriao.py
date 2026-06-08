from flask import Blueprint, render_template, request, redirect, url_for
from db import get_connection
from datetime import datetime

anfitriao_bp = Blueprint('anfitriao', __name__, url_prefix='/anfitriao')

# Simulando o Anfitrião logado (Bruno Costa)
ANFITRIAO_ID = 2

@anfitriao_bp.route('/')
def dashboard():
    """Lê todos os dados necessários para o painel do anfitrião."""
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. Dados do Perfil e Telefones
    cur.execute("SELECT * FROM USUARIO WHERE UsrID = %s;", (ANFITRIAO_ID,))
    perfil = cur.fetchone()
    
    cur.execute("SELECT * FROM TELEFONE WHERE UsrID = %s;", (ANFITRIAO_ID,))
    telefones = cur.fetchall()
    
    # 2. Gestão de Estoque (Anúncios + Acomodações + Endereço)
    query_estoque = """
        SELECT an.AnID, an.AnTitulo, an.AnDesc, an.AnCustoDiaUtil, an.AnCustoFimSem,
               ac.AcID, ac.AcCapacPessoa, ac.AcQtdQuartos, ac.AcQtdBanheiros,
               endr.EndComplemento, endr.EndNumero, cep.CepRua, cep.CepCidade, cep.CepEstado, cep.CepID,
               (SELECT string_agg(c.ComNome, ', ') 
                FROM ACPOSSUICOM acp 
                JOIN COMODIDADE c ON acp.ComID = c.ComID 
                WHERE acp.AcID = ac.AcID) as comodidades
        FROM ANUNCIO an
        JOIN ACOMODACAO ac ON an.AnID = ac.AnID
        JOIN ENDERECO endr ON ac.EndID = endr.EndID
        JOIN CEP cep ON endr.CepID = cep.CepID
        WHERE an.AnfUsrID = %s
        ORDER BY an.AnID DESC;
    """
    cur.execute(query_estoque, (ANFITRIAO_ID,))
    estoque = cur.fetchall()

    # Busca lista global de comodidades para o anfitrião poder adicionar aos seus anúncios
    cur.execute("SELECT ComID, ComNome FROM COMODIDADE ORDER BY ComNome;")
    todas_comodidades = cur.fetchall()
    
    # 3. Gestão de Reservas (Inbound)
    query_reservas = """
        SELECT r.ResID, r.ResDtIn, r.ResDtOut, r.ResStatus, r.ResQtdAdultos,
               a.AnTitulo, u.UsrNome as HospedeNome, u.UsrID as HospedeID,
               EXISTS (
                   SELECT 1 FROM AVALIACAO av 
                   WHERE av.AnfUsrID = %s AND av.HosUsrID = u.UsrID AND av.AnID = a.AnID AND av.TipoAvID = 3
               ) as ja_avaliou_hospede
        FROM RESERVA r
        JOIN ANUNCIO a ON r.AnID = a.AnID
        JOIN USUARIO u ON r.HosUsrID = u.UsrID
        WHERE a.AnfUsrID = %s
        ORDER BY r.ResDtIn DESC;
    """
    cur.execute(query_reservas, (ANFITRIAO_ID, ANFITRIAO_ID))
    reservas = cur.fetchall()
    
    # 4. Avaliações Recebidas (Hóspede -> Anúncio)
    query_avaliacoes = """
        SELECT av.AvNota, av.AvComentario, av.AvData, a.AnTitulo, u.UsrNome as HospedeNome
        FROM AVALIACAO av
        JOIN ANUNCIO a ON av.AnID = a.AnID
        JOIN USUARIO u ON av.HosUsrID = u.UsrID
        WHERE av.AnfUsrID = %s AND av.TipoAvID = 1
        ORDER BY av.AvData DESC;
    """
    cur.execute(query_avaliacoes, (ANFITRIAO_ID,))
    avaliacoes_recebidas = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('anfitriao.html', 
                           perfil=perfil, telefones=telefones, 
                           estoque=estoque, reservas=reservas, 
                           avaliacoes=avaliacoes_recebidas, comodidades=todas_comodidades)


# ==========================================
# 1. GERENCIAMENTO DE CONTA
# ==========================================
@anfitriao_bp.route('/perfil/atualizar', methods=['POST'])
def atualizar_perfil():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE USUARIO SET UsrNome = %s, UsrCPF = %s WHERE UsrID = %s;", 
                (request.form['UsrNome'], request.form['UsrCPF'], ANFITRIAO_ID))
    conn.commit()
    conn.close()
    return redirect(url_for('anfitriao.dashboard'))

@anfitriao_bp.route('/telefone/adicionar', methods=['POST'])
def adicionar_telefone():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(TlfID), 0) + 1 AS prox_id FROM TELEFONE;")
    cur.execute("INSERT INTO TELEFONE (TlfID, TlfNumero, UsrID) VALUES (%s, %s, %s);", 
                (cur.fetchone()['prox_id'], request.form['TlfNumero'], ANFITRIAO_ID))
    conn.commit()
    conn.close()
    return redirect(url_for('anfitriao.dashboard'))

@anfitriao_bp.route('/telefone/deletar/<int:tlf_id>', methods=['POST'])
def deletar_telefone(tlf_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM TELEFONE WHERE TlfID = %s AND UsrID = %s;", (tlf_id, ANFITRIAO_ID))
    conn.commit()
    conn.close()
    return redirect(url_for('anfitriao.dashboard'))


# ==========================================
# 2. GESTÃO DE ESTOQUE E COMODIDADES
# ==========================================
@anfitriao_bp.route('/estoque/novo', methods=['POST'])
def criar_anuncio():
    """Transação completa: Cria CEP (se não existir), Endereço, Anúncio e Acomodação."""
    data = request.form
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # 1. Tratar CEP
        cur.execute("SELECT CepID FROM CEP WHERE CepID = %s;", (data['CepID'],))
        if not cur.fetchone():
            cur.execute("INSERT INTO CEP (CepID, CepRua, CepBairro, CepCidade, CepEstado) VALUES (%s, %s, %s, %s, %s);",
                        (data['CepID'], data['CepRua'], data['CepBairro'], data['CepCidade'], data['CepEstado']))
            
        # 2. Inserir Endereço
        cur.execute("SELECT COALESCE(MAX(EndID), 0) + 1 AS prox_id FROM ENDERECO;")
        end_id = cur.fetchone()['prox_id']
        cur.execute("INSERT INTO ENDERECO (EndID, EndNumero, EndComplemento, CepID) VALUES (%s, %s, %s, %s);",
                    (end_id, data['EndNumero'], data['EndComplemento'], data['CepID']))
        
        # 3. Inserir Anúncio
        cur.execute("SELECT COALESCE(MAX(AnID), 0) + 1 AS prox_id FROM ANUNCIO;")
        an_id = cur.fetchone()['prox_id']
        cur.execute("INSERT INTO ANUNCIO (AnID, AnTitulo, AnDesc, AnCustoDiaUtil, AnCustoFimSem, AnfUsrID) VALUES (%s, %s, %s, %s, %s, %s);",
                    (an_id, data['AnTitulo'], data['AnDesc'], data['AnCustoDiaUtil'], data['AnCustoFimSem'], ANFITRIAO_ID))
        
        # 4. Inserir Acomodação
        cur.execute("SELECT COALESCE(MAX(AcID), 0) + 1 AS prox_id FROM ACOMODACAO;")
        ac_id = cur.fetchone()['prox_id']
        cur.execute("INSERT INTO ACOMODACAO (AcID, AcCapacPessoa, AcQtdQuartos, AcQtdBanheiros, AnID, EndID) VALUES (%s, %s, %s, %s, %s, %s);",
                    (ac_id, data['AcCapacPessoa'], data['AcQtdQuartos'], data['AcQtdBanheiros'], an_id, end_id))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erro ao criar anúncio: {e}")
    finally:
        cur.close()
        conn.close()
        
    return redirect(url_for('anfitriao.dashboard'))

@anfitriao_bp.route('/estoque/deletar/<int:an_id>', methods=['POST'])
def deletar_anuncio(an_id):
    conn = get_connection()
    cur = conn.cursor()
    # O ON DELETE CASCADE configurado no DDL vai apagar a ACOMODACAO e AVALIAÇÕES vinculadas
    cur.execute("DELETE FROM ANUNCIO WHERE AnID = %s AND AnfUsrID = %s;", (an_id, ANFITRIAO_ID))
    conn.commit()
    conn.close()
    return redirect(url_for('anfitriao.dashboard'))

@anfitriao_bp.route('/estoque/comodidade/adicionar', methods=['POST'])
def adicionar_comodidade():
    """Adiciona uma comodidade à acomodação (ACPOSSUICOM)."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO ACPOSSUICOM (AcID, ComID) VALUES (%s, %s);", 
                    (request.form['AcID'], request.form['ComID']))
        conn.commit()
    except:
        conn.rollback() # Evita crash se tentar inserir duplicado
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('anfitriao.dashboard'))


# ==========================================
# 3. GESTÃO DE RESERVAS INBOUND
# ==========================================
@anfitriao_bp.route('/reserva/status/<int:res_id>', methods=['POST'])
def atualizar_status_reserva(res_id):
    novo_status = request.form['ResStatus']
    conn = get_connection()
    cur = conn.cursor()
    # Garante que o anfitrião só altere reservas dos SEUS anúncios
    query = """
        UPDATE RESERVA SET ResStatus = %s 
        WHERE ResID = %s AND AnID IN (SELECT AnID FROM ANUNCIO WHERE AnfUsrID = %s);
    """
    cur.execute(query, (novo_status, res_id, ANFITRIAO_ID))
    conn.commit()
    conn.close()
    return redirect(url_for('anfitriao.dashboard'))


# ==========================================
# 4. AVALIAÇÕES (Anfitrião -> Hóspede)
# ==========================================
@anfitriao_bp.route('/avaliacao/hospede/nova', methods=['POST'])
def avaliar_hospede():
    """Cria avaliação do Tipo 3 (Anfitrião -> Hóspede)."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COALESCE(MAX(AvID), 0) + 1 AS prox_id FROM AVALIACAO;")
    prox_id = cur.fetchone()['prox_id']
    hoje = datetime.now().strftime('%Y-%m-%d')
    
    query = """
        INSERT INTO AVALIACAO (AvID, AvNota, AvComentario, AvData, TipoAvID, AnID, AnfUsrID, HosUsrID)
        VALUES (%s, %s, %s, %s, 3, %s, %s, %s);
    """
    cur.execute(query, (prox_id, request.form['AvNota'], request.form['AvComentario'], hoje, 
                        request.form['AnID'], ANFITRIAO_ID, request.form['HosUsrID']))
    conn.commit()
    conn.close()
    return redirect(url_for('anfitriao.dashboard'))