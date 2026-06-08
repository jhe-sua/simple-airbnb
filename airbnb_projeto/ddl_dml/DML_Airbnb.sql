SET SEARCH_PATH TO airbnb;

-- 1. Tabelas Independentes (Sem dependências)
INSERT INTO CEP (CepID, CepRua, CepBairro, CepCidade, CepEstado) VALUES
('20031-170', 'Rua das Flores', 'Centro', 'Rio de Janeiro', 'RJ'),
('21030-001', 'Avenida Brasil', 'Penha', 'Rio de Janeiro', 'RJ'),
('01305-000', 'Rua Augusta', 'Consolação', 'São Paulo', 'SP'),
('01311-000', 'Avenida Paulista', 'Bela Vista', 'São Paulo', 'SP'),
('80020-310', 'Rua XV de Novembro', 'Centro', 'Curitiba', 'PR'),
('22070-000', 'Avenida Atlântica', 'Copacabana', 'Rio de Janeiro', 'RJ'),
('22250-040', 'Rua das Palmeiras', 'Botafogo', 'Rio de Janeiro', 'RJ'),
('30130-010', 'Avenida Afonso Pena', 'Centro', 'Belo Horizonte', 'MG'),
('40020-000', 'Rua Chile', 'Comércio', 'Salvador', 'BA'),
('60165-121', 'Avenida Beira Mar', 'Meireles', 'Fortaleza', 'CE');

INSERT INTO USUARIO (UsrID, UsrNome, UsrCPF, UsrDtNasc) VALUES
(1, 'Ana Silva', '111.111.111-11', '1990-01-15'),
(2, 'Bruno Costa', '222.222.222-22', '1985-05-20'),
(3, 'Carlos Dias', '333.333.333-33', '1992-08-10'),
(4, 'Daniela Rosa', '444.444.444-44', '1988-11-30'),
(5, 'Eduardo Lima', '555.555.555-55', '1995-02-25'),
(6, 'Fernanda Alves', '666.666.666-55', '1993-07-12'),
(7, 'Gustavo Pereira', '777.777.777-77', '1987-03-08'),
(8, 'Helena Martins', '888.888.888-88', '1991-09-17'),
(9, 'Igor Nogueira', '999.999.999-99', '1996-12-03');

INSERT INTO COMODIDADE (ComID, ComNome) VALUES
(1, 'Wi-Fi'), (2, 'Ar-condicionado'), (3, 'Aquecimento'),
(4, 'Cozinha equipada'), (5, 'Máquina de lavar'), (6, 'Secadora'),
(7, 'TV'), (8, 'TV a cabo'), (9, 'Estacionamento'),
(10, 'Piscina'), (11, 'Academia'), (12, 'Elevador'),
(13, 'Pet-friendly'), (14, 'Varanda'), (15, 'Vista para o mar'),
(16, 'Churrasqueira'), (17, 'Portaria 24h'), (18, 'Escritório/mesa de trabalho'),
(19, 'Roupas de cama incluídas'), (20, 'Toalhas incluídas');

INSERT INTO TIPOAV (TipoAvID, TipoAvStr) VALUES
(1, 'Hospede->Anuncio'),
(2, 'Hospede->Anfitriao'),
(3, 'Anfitriao->Hospede');


-- 2. Tabelas com Dependência de Nível 1 (Dependem de USUARIO ou CEP)
INSERT INTO TELEFONE (TlfID, TlfNumero, UsrID) VALUES
(1, '21987654321', 1), (2, '21976543210', 2), (3, '21965432109', 3),
(4, '21954321098', 4), (5, '21943210987', 5), (6, '21932109876', 6),
(7, '21921098765', 7), (8, '21910987654', 8), (9, '21999887766', 9),
(10, '21988776655', 1), (11, '21977665544', 2);

INSERT INTO HOSPEDE (UsrID, HosDataInicio) VALUES
(1, '2023-01-10'), (3, '2023-03-22'), (4, '2023-05-15'),
(6, '2023-07-01'), (8, '2023-09-18');

INSERT INTO ANFITRIAO (UsrID, AnfDataInicio) VALUES
(2, '2023-02-05'), (5, '2023-04-18'), (7, '2023-06-10'),
(9, '2023-08-25'), (3, '2023-10-01');

INSERT INTO ENDERECO (EndID, EndNumero, EndComplemento, CepID) VALUES
(1, 100, 'Apto 101', '20031-170'), (2, 250, 'Bloco B, Apto 202', '21030-001'),
(3, 45, 'Casa fundos', '01305-000'), (4, 780, 'Apto 303', '01311-000'),
(5, 60, 'Studio 12', '80020-310'), (6, 15, 'Loja 1', '22070-000'),
(7, 900, 'Cobertura', '22250-040'), (8, 33, 'Quarto 2', '30130-010'),
(9, 1200, 'Casa principal', '40020-000'), (10, 500, 'Apto 404', '60165-121'),
(11, 210, 'Flat 22', '20031-170'), (12, 320, 'Apto 505', '21030-001'),
(13, 75, 'Suíte 3', '01305-000'), (14, 640, 'Casa lateral', '01311-000'),
(15, 88, 'Studio 7', '80020-310');


-- 3. Tabelas com Dependência de Nível 2 (Dependem de ANFITRIAO e ENDERECO)
INSERT INTO ANUNCIO (AnID, AnTitulo, AnDesc, AnCustoDiaUtil, AnCustoFimSem, AnfUsrID) VALUES
(1, 'Kitnet no Centro', 'Próximo ao metrô e comércio', 120, 150, 2),
(2, 'Apto em Copacabana', 'Vista parcial para o mar', 250, 320, 3),
(3, 'Quarto simples', 'Ambiente tranquilo', 80, 100, 5),
(4, 'Casa ampla', 'Ideal para famílias', 300, 380, 7),
(5, 'Studio moderno', 'Recém reformado', 200, 260, 9),
(6, 'Loft aconchegante', 'Decoração minimalista', 180, 220, 2),
(7, 'Apto luxo', 'Alto padrão com varanda', 400, 500, 3),
(8, 'Quarto compartilhado', 'Econômico e bem localizado', 60, 80, 5),
(9, 'Cobertura', 'Vista panorâmica', 500, 650, 7),
(10, 'Casa de praia', 'Perto do mar', 350, 450, 9),
(11, 'Flat mobiliado', 'Completo e confortável', 220, 280, 2),
(12, 'Apto compacto', 'Ideal para casal', 150, 190, 3),
(13, 'Suíte privativa', 'Banheiro exclusivo', 170, 210, 5),
(14, 'Casa rústica', 'Clima de serra', 280, 340, 7),
(15, 'Studio econômico', 'Bom custo-benefício', 130, 160, 9);


-- 4. Tabelas com Dependência de Nível 3 (Dependem de ANUNCIO)
INSERT INTO ACOMODACAO (AcID, AcCapacPessoa, AcQtdQuartos, AcQtdBanheiros, AnID, EndID) VALUES
(1, 2, 1, 1, 1, 1), (2, 4, 2, 1, 2, 2), (3, 1, 1, 1, 3, 3),
(4, 6, 3, 2, 4, 4), (5, 2, 1, 1, 5, 5), (6, 2, 1, 1, 6, 6),
(7, 4, 2, 2, 7, 7), (8, 1, 1, 1, 8, 8), (9, 8, 4, 3, 9, 9),
(10, 6, 3, 2, 10, 10), (11, 3, 1, 1, 11, 11), (12, 2, 1, 1, 12, 12),
(13, 2, 1, 1, 13, 13), (14, 5, 2, 2, 14, 14), (15, 2, 1, 1, 15, 15);

INSERT INTO ACPOSSUICOM (AcID, ComID) VALUES
(1, 1), (1, 4), (1, 7), (2, 1), (2, 2), (2, 9), (2, 12),
(3, 1), (3, 4), (4, 1), (4, 2), (4, 4), (4, 9), (4, 16),
(5, 1), (5, 2), (5, 7), (6, 1), (6, 4), (6, 18),
(7, 1), (7, 2), (7, 7), (7, 10), (7, 11),
(8, 1), (8, 4), (9, 1), (9, 2), (9, 9), (9, 10), (9, 15),
(10, 1), (10, 4), (10, 16), (11, 1), (11, 7), (11, 12),
(12, 1), (12, 4), (12, 14), (13, 1), (13, 19), (13, 20),
(14, 1), (14, 2), (14, 16), (15, 1), (15, 4), (15, 13);


-- 5. Tabelas Finais (RESERVA e AVALIACAO cruzam múltiplos IDs)
INSERT INTO RESERVA (ResID, ResDtIn, ResDtOut, ResStatus, ResFormaPaga, ResDataPaga, ResQtdAdultos, ResQtdCriancas, ResQtdBebes, ResQtdPets, HosUsrID, AnID) VALUES
(1, '2024-01-10', '2024-01-15', 'Confirmada', 'Cartão', '2024-01-05', 2, 0, 0, 0, 1, 1),
(2, '2024-01-12', '2024-01-14', 'Confirmada', 'Pix', '2024-01-10', 1, 0, 0, 0, 3, 2),
(3, '2024-01-20', '2024-01-25', 'Cancelada', 'Cartão', NULL, 2, 1, 0, 0, 4, 3),
(4, '2024-02-01', '2024-02-05', 'Confirmada', 'Boleto', '2024-01-28', 3, 1, 0, 0, 6, 4),
(5, '2024-02-03', '2024-02-06', 'Pendente', 'Pix', NULL, 2, 0, 0, 1, 8, 5),
(6, '2024-02-10', '2024-02-15', 'Confirmada', 'Cartão', '2024-02-01', 2, 0, 1, 0, 1, 6),
(7, '2024-02-12', '2024-02-18', 'Confirmada', 'Pix', '2024-02-05', 4, 2, 0, 0, 3, 7),
(8, '2024-02-20', '2024-02-22', 'Confirmada', 'Cartão', '2024-02-15', 1, 0, 0, 0, 4, 8),
(9, '2024-03-01', '2024-03-05', 'Pendente', 'Boleto', NULL, 2, 1, 0, 0, 6, 9),
(10, '2024-03-03', '2024-03-07', 'Confirmada', 'Cartão', '2024-02-25', 2, 0, 0, 1, 8, 10),
(11, '2024-03-10', '2024-03-12', 'Confirmada', 'Pix', '2024-03-05', 1, 0, 0, 0, 1, 11),
(12, '2024-03-15', '2024-03-20', 'Confirmada', 'Cartão', '2024-03-10', 3, 1, 1, 0, 3, 12),
(13, '2024-03-18', '2024-03-22', 'Cancelada', 'Pix', NULL, 2, 0, 0, 0, 4, 13);

INSERT INTO AVALIACAO (AvID, AvNota, AvComentario, AvData, AnID, AnfUsrID, HosUsrID, TipoAvID, ResID) VALUES
(1, 5, 'Ótima estadia', '2024-01-16', 1, 2, 1, 1, 1),
(2, 5, 'Anfitrião muito atencioso', '2024-01-16', 1, 2, 1, 2, 1),
(3, 5, 'Hóspede exemplar', '2024-01-16', 1, 2, 1, 3, 1),
(4, 4, 'Boa localização', '2024-01-14', 2, 3, 3, 1, 2),
(5, 4, 'Comunicação eficiente', '2024-01-14', 2, 3, 3, 2, 2),
(6, 5, 'Excelente casa', '2024-02-06', 4, 7, 6, 1, 4),
(7, 5, 'Tudo perfeito', '2024-02-06', 4, 7, 6, 2, 4),
(8, 5, 'Hóspede organizado', '2024-02-06', 4, 7, 6, 3, 4),
(9, 3, 'Razoável', '2024-02-16', 6, 2, 1, 1, 6),
(10, 5, 'Luxo incrível', '2024-02-19', 7, 3, 3, 1, 7),
(11, 5, 'Experiência top', '2024-02-19', 7, 3, 3, 2, 7),
(12, 5, 'Excelente hóspede', '2024-02-19', 7, 3, 3, 3, 7);