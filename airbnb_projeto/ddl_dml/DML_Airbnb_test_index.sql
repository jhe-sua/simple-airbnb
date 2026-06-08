SET SEARCH_PATH TO airbnb;

-- 1. Gerar 10.000 Novos Usuários (IDs de 100 a 10099)
INSERT INTO USUARIO (UsrID, UsrNome, UsrCPF, UsrDtNasc)
SELECT
    i,
    'Usuario Teste ' || i,
    LPAD((i % 99999999999)::text, 11, '0'), -- Gera um CPF falso
    DATE '1970-01-01' + (random() * 15000)::integer -- Data de nascimento aleatória
FROM generate_series(100, 10099) AS i;

-- 2. Transformar 2.000 desses Usuários em Anfitriões (IDs de 100 a 2099)
INSERT INTO ANFITRIAO (UsrID, AnfDataInicio)
SELECT
    i,
    DATE '2020-01-01' + (random() * 1000)::integer
FROM generate_series(100, 2099) AS i;

-- 3. Gerar 5.000 Endereços aleatórios distribuídos pelos CEPs já existentes
INSERT INTO ENDERECO (EndID, EndNumero, EndComplemento, CepID)
SELECT
    i,
    (random() * 2000 + 1)::integer,
    'Apto ' || (random() * 100 + 1)::integer,
    (ARRAY['20031-170', '21030-001', '01305-000', '01311-000', '80020-310', '22070-000', '22250-040', '30130-010', '40020-000', '60165-121'])[floor(random() * 10 + 1)]
FROM generate_series(100, 5099) AS i;

-- 4. Gerar 5.000 Anúncios associados aos 2.000 Anfitriões
INSERT INTO ANUNCIO (AnID, AnTitulo, AnDesc, AnCustoDiaUtil, AnCustoFimSem, AnfUsrID)
SELECT
    i,
    'Anúncio Gerado ' || i,
    'Descrição automática para o anúncio ' || i,
    (random() * 300 + 50)::integer,
    (random() * 400 + 100)::integer,
    (i % 2000) + 100 -- Distribui o AnfUsrID de forma circular entre os 2000 anfitriões
FROM generate_series(100, 5099) AS i;

-- 5. Associar os 5.000 Anúncios a 5.000 Acomodações
INSERT INTO ACOMODACAO (AcID, AcCapacPessoa, AcQtdQuartos, AcQtdBanheiros, AnID, EndID)
SELECT
    i,
    (random() * 8 + 1)::integer,
    (random() * 4 + 1)::integer,
    (random() * 3 + 1)::integer,
    i, -- Relaciona com o Anuncio de mesmo ID
    i  -- Relaciona com o Endereco de mesmo ID
FROM generate_series(100, 5099) AS i;