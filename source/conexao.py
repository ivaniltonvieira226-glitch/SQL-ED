import psycopg
import sys

#Isso vai fazer que o retorno das funções sejam JSON para uso da UI
from psycopg.rows import dict_row

dados_conexao = (
    "host=localhost "
    "port=5432 "
    "dbname=meu_banco_local "
    "user=postgres "
    "password=minhasenha123"
)

def conectar():
    try:
        return psycopg.connect(dados_conexao,
                         row_factory=dict_row)
    except psycopg.OperationalError:
        print("Não foi possível conectar ao banco.")
        sys.exit(1)

def inicializar_banco():
    """Cria as tabelas e tipos necessários se eles não existirem."""
    conn = conectar()
    
    try:
        with conn.cursor() as cur:
            # 1. Tabela de Livros
            cur.execute("""
            CREATE TABLE IF NOT EXISTS livros(
                id SERIAL PRIMARY KEY,
                titulo VARCHAR(200) NOT NULL,
                autor VARCHAR(100) NOT NULL,
                ano INTEGER NOT NULL,
                paginas INTEGER NOT NULL
            );
            """)
            
            # 2. Criação do ENUM com verificação manual para evitar quebra de transação
            cur.execute("SELECT 1 FROM pg_type WHERE typname = 'status_leitura';")
            if not cur.fetchone():
                cur.execute("""
                    CREATE TYPE status_leitura AS ENUM (
                        'CONCLUIDO', 'LENDO', 'NAO_LIDO', 'ABANDONADO'    
                    );
                """)
            
            # 3. Tabela de Leituras
            cur.execute("""
            CREATE TABLE IF NOT EXISTS leituras (
                livro_id INTEGER PRIMARY KEY,
                status status_leitura NOT NULL,
                pagina_atual INTEGER DEFAULT 0,
                CONSTRAINT fk_livro
                    FOREIGN KEY (livro_id)
                    REFERENCES livros(id)
                    ON DELETE CASCADE
            );
            """)
            
            conn.commit()
            print("📦 Banco de dados verificado/inicializado com sucesso.")
            
    except Exception as e:
        conn.rollback()
        print(f"Erro ao inicializar o banco: {e}")
        sys.exit(1)
    finally:
        conn.close() # Aqui faz sentido fechar, pois a inicialização acabou

# Quando este arquivo for importado, ele garante que o banco está pronto
inicializar_banco()