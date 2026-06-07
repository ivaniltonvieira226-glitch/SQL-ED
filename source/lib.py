import psycopg
from psycopg.rows import dict_row
# Importamos apenas a função de conectar 
from conexao import conectar


# ==============================================================================
# FUNÇÃO AUXILIAR
# ==============================================================================
def verificar_status(status: str) -> bool:
    status_possiveis = {"NAO_LIDO", "LENDO", "CONCLUIDO", "ABANDONADO"}
    return status in status_possiveis


# ==============================================================================
# LEITURAS (SELECTs)
# ==============================================================================
def mostrar_livros():
    # Abrimos uma conexão limpa e garantimos o seu fechamento no final do bloco
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT l.titulo, l.id, l.autor, l.ano, l.paginas, le.status, le.pagina_atual
                FROM livros l 
                JOIN leituras le ON l.id = le.livro_id
            """)
            return cursor.fetchall()


def filtrar_ano(ano: int):
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute(""" 
                SELECT l.ano, l.titulo, le.status 
                FROM livros l 
                JOIN leituras le ON l.id = le.livro_id
                WHERE l.ano = %s; 
            """, (ano,))
            return cursor.fetchall()


def ordenar_cresc():
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT titulo, ano, le.status FROM livros l Join
                           leituras le ON l.id = le.livro_id
                           ORDER BY ano ASC;""")
            return cursor.fetchall()


def ordenar_desc():
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT l.titulo, l.ano, le.status FROM livros l JOIN 
                           leituras le ON l.id = le.livro_id
                            ORDER BY ano DESC;""")
            return cursor.fetchall()


def buscar_livro(nome: str):
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT l.titulo, le.status, le.pagina_atual 
                FROM livros l 
                JOIN leituras le ON l.id = le.livro_id
                WHERE l.titulo ILIKE %s
            """, (f"%{nome}%",))
            return cursor.fetchall()


def ordenar_alfabeto():
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT titulo FROM livros ORDER BY titulo ASC;")
            return cursor.fetchall()


def buscar_por_id(id_livro: int):
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT l.id, l.titulo, l.paginas, le.status, le.pagina_atual
                FROM livros l
                JOIN leituras le ON l.id = le.livro_id
                WHERE l.id = %s
            """, (id_livro,))
            return cursor.fetchone()


# ==============================================================================
# ESCRITAS (INSERT, UPDATE, DELETE) - Requerem Commit/Rollback explícitos
# ==============================================================================
def inserir_livro(titulo: str, pagina: int, ano: int, autor: str, status: str, pagina_atual: int):
    status = status.upper()

    if not verificar_status(status): raise ValueError("Status inválido.")
    if ano <= 0: raise ValueError("Ano inválido")
    if pagina <= 0: raise ValueError("Página não pode ser menor que 1")
    if pagina_atual < 0: raise ValueError("Página não pode ser negativa")
    if pagina_atual > pagina: raise ValueError("Página atual não pode ser maior que o número de páginas.")
    
    conn = conectar()
    try:
        with conn.cursor() as cursor:
            # Inserindo na tabela livros
            cursor.execute("""
                INSERT INTO livros(titulo, autor, ano, paginas) 
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (titulo, autor, ano, pagina))
            
            resultado = cursor.fetchone()
            livro_id = resultado["id"]

            # Inserindo na tabela leituras
            cursor.execute("""
                INSERT INTO leituras(livro_id, status, pagina_atual) 
                VALUES (%s, %s, %s)
            """, (livro_id, status, pagina_atual))
            
            conn.commit() # Salva as duas operações juntas
    except Exception:
        conn.rollback() # Se qualquer uma falhar, desfaz tudo
        raise
    finally:
        conn.close() # Fecha a conexão


def remover_livro(id_livro: int):
    conn = conectar()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM livros WHERE id = %s", (id_livro,))
            if cursor.rowcount == 0:
                raise ValueError("Livro não encontrado")
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def atualizar_leitura(livro_id: int, status: str, pagina_atual: int):
    status = status.upper()

    if not verificar_status(status): raise ValueError("Status inválido")
    if pagina_atual < 0: raise ValueError("Página Negativa.")
    
    conn = conectar()
    try:
        with conn.cursor() as cursor:
            # Busca o total de páginas para validar
            cursor.execute("SELECT paginas FROM livros WHERE id = %s", (livro_id,))
            #Está retornando um dicionario
            paginas = cursor.fetchone()
            resultado = paginas["id"]

            if resultado is None:
                raise ValueError("Livro não encontrado.")

            paginas = resultado[0]
            if pagina_atual > paginas:
                raise ValueError("Página atual maior que o total de páginas.")

            # Executa o update
            cursor.execute("""
                UPDATE leituras 
                SET status = %s, pagina_atual = %s
                WHERE livro_id = %s
            """, (status, pagina_atual, livro_id))

            if cursor.rowcount == 0:
                raise ValueError("Livro não encontrado")
                
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()