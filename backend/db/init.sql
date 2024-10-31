DROP TABLE IF EXISTS "vendas";
DROP TABLE IF EXISTS "filmes";

CREATE TABLE "filmes" (
    "id" SERIAL PRIMARY KEY,
    "titulo" VARCHAR(255) NOT NULL,
    "diretor" VARCHAR(255) NOT NULL,
    "quantidade" INTEGER NOT NULL,
    "preco" FLOAT NOT NULL
);

CREATE TABLE "vendas" (
    "id" SERIAL PRIMARY KEY,
    "filme_id" INTEGER REFERENCES filmes(id) ON DELETE CASCADE,
    "quantidade_vendida" INTEGER NOT NULL,
    "valor_venda" FLOAT NOT NULL,
    "data_venda" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO "filmes" ("titulo", "diretor", "quantidade", "preco") VALUES ('O Senhor dos Anéis', 'J.R.R. Tolkien', 10, 50.00);
INSERT INTO "filmes" ("titulo", "diretor", "quantidade", "preco") VALUES ('Harry Potter', 'J.K. Rowling', 20, 30.00);
INSERT INTO "filmes" ("titulo", "diretor", "quantidade", "preco") VALUES ('1984', 'George Orwell', 15, 40.00)