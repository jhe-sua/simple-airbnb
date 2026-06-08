# Criar data base

Entre no psql e crie o seguinte data base:

```SQL
CREATE DATABASE airbnb;
```

Va pra a pasta ddl_dml, então digite no terminal:

```bash
psql airbnb -f DDL_Airbnb.sql
```

A saida deve ser a seguinte:

```text
CREATE SCHEMA
SET
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
```

Se for assim agora digite no terminal:

```bash
psql airbnb -f DML_Airbnb.sql
```

a saida deveria ser:

```text
SET
INSERT 0 10
INSERT 0 9
INSERT 0 20
INSERT 0 3
INSERT 0 11
INSERT 0 5
INSERT 0 5
INSERT 0 15
INSERT 0 15
INSERT 0 15
INSERT 0 50
INSERT 0 13
INSERT 0 12
```

Pronto o banco de dados esta montado.

# Iniciar sistema

Va no arquivo .env, ele tem o seguinte:

```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=airbnb
DB_USER=<seu usuario>
DB_PASSWORD=<sua senha>
```

modifique DB_USER pelo seu usuario do psql e DB_password pela senha do seu usuario. Ficando, por exemplo, assim:

```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=airbnb
DB_USER=vscode
DB_PASSWORD=vscode2026
```

com o seu usuario pronto, configure o seu ambiente python baixando as bibliotecas no arquivo requeirements.txt

finalmente, dentro da pasta airbnb_projeto, execute o seguinte comando no terminal:

```bash
python app.py
```

agora basta entrar no google e entar em localhost:5000



