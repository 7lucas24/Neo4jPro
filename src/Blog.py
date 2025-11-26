from neo4j import GraphDatabase

class BlogAppNeo4j:
    # --- Configuración y Conexión ---
    def __init__(self, uri="neo4j://localhost:7687", user="neo4j", password="12345678"):
        """Inicializa la conexión al driver de Neo4j."""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """Cierra el driver de conexión."""
        self.driver.close()

#CREAR
    def create_user(self, n, e):
        query = (
        "MERGE (u:User {email: $email})"
        "ON CREATE SET u.name = $name, u.url = '/users/' + replace($name, ' ', '-')"
        "RETURN u"
        )
        with self.driver.session() as session:
                result = session.run(query, name=n, email=e).single()
                return result

    def create_category(self, name):
        url = "/categories/" + name.lower().replace(" ", "-")
        query = (
            "MERGE (c:Category {name: $name}) "
            "ON CREATE SET c.url = $url "
            "RETURN c"
        )
        with self.driver.session() as session:
            return session.run(query, name=name, url=url).single()

    def create_tag(self, name):
        url = "/tags/" + name.lower().replace(" ", "-")
        query = (
            "MERGE (t:Tag {name: $name}) "
            "ON CREATE SET t.url = $url "
            "RETURN t"
        )
        with self.driver.session() as session:
            return session.run(query, name=name, url=url).single()
    
    def create_com(self, article, user, text):
        query = """
        // 1. MATCH: Buscar el Usuario (Comentarista) y el Artículo
        MATCH (u:User {name: $user})
        MATCH (a:Article {title: $article_title})
        
        // 2. CREATE: Crear el nodo Comment con propiedades
        CREATE (com:Comment {
            text: $comment_text,
            date: datetime() // Usamos datetime() para un timestamp preciso
        })
        
        // 3. CREATE RELATIONSHIPS: Conectar el Comentario
        CREATE (u)-[:WROTE_COMMENT]->(com)
        CREATE (com)-[:COMMENTED_ON]->(a)
        
        RETURN com
        """
        
        with self.driver.session() as session:
            result = session.run(query,
                                user=user,
                                article_title=article,
                                comment_text=text)
            return result.single()

    def create_article(self, title, text, author_name, category_name, tag_names): # Aceptar lista
        url = "/articles/" + title.lower().replace(" ", "-")
        
        query = """
        MERGE (a:Article {title: $title})
        ON CREATE SET 
            a.text = $text, 
            a.url = $url, 
            a.date = date() 
        
        // Conectar Autor======================================================================
        WITH a
        MATCH (u:User {name: $author_name})
        MERGE (u)-[:WROTE]->(a)
        
        // Conectar Categoría=================================================================
        WITH a
        MATCH (c:Category {name: $category_name})
        MERGE (a)-[:IN_CATEGORY]->(c)
        
        // Conectar Múltiples Tags usando UNWIND================================================
        WITH a
        UNWIND $tag_names AS tagName // UNWIND itera sobre la lista
        MATCH (t:Tag {name: tagName})
        MERGE (a)-[:TAGGED_WITH]->(t)
        
        RETURN properties(a) AS article_data
        """
        
        with self.driver.session() as session:
            result = session.run(query, 
                                title=title, 
                                text=text, 
                                url=url, 
                                author_name=author_name, 
                                category_name=category_name, 
                                tag_names=tag_names) # Pasar la lista como parámetro
            return result.single()
#BUSQUEDA
    def search_nodes(self, label, property_name, property_value): 
        """Busca nodos por etiqueta y propiedad."""
        query = (
            f"MATCH (n:{label} {{{property_name}: $value}}) "
            "RETURN properties(n) AS node_data"
        )
        # Abre y maneja la sesión aquí
        with self.driver.session() as session: 
            result = session.run(query, value=property_value)
            return [record["node_data"] for record in result]

    def update_article(self, title, new_data): # Cambia la firma para claridad
        """Actualiza las propiedades de un artículo usando su título como clave."""
        with self.driver.session() as session:
            # Cypher usa MAPS para actualizaciones 
            query = (
                "MATCH (a:Article {title: $title}) "
                "SET a += $set "
                "RETURN a"
            )
            session.run(query, title=title, set=new_data) # Usa los argumentos pasados
            return True

    def delete_node(self, node_label, property_name, property_value):
        """Elimina un nodo y sus relaciones por una propiedad (ej. Título o Nombre)."""
        with self.driver.session() as session:
            query = (
                f"MATCH (n:{node_label} {{{property_name}: $value}}) "
                "DETACH DELETE n" # DETACH DELETE elimina el nodo y todas sus relaciones
            )
            session.run(query, value=property_value)
            return True
    
    # --- Operaciones de Grafo (Relaciones) ---

    def get_article_with_details(self, article_title):
        query = """
        MATCH (a:Article {title: $title})
        // Autor
        MATCH (u:User)-[:WROTE]->(a)
        // Categorías
        OPTIONAL MATCH (a)-[:IN_CATEGORY]->(c:Category)
        // Tags
        OPTIONAL MATCH (a)-[:TAGGED_WITH]->(t:Tag)
        // Comentarios
        OPTIONAL MATCH (commenter:User)-[:WROTE_COMMENT]->(com:Comment)-[:COMMENTED_ON]->(a)
        
        RETURN a.title AS title, 
               a.url AS url,
               a.text AS text,
               u.name AS author,
               collect(DISTINCT c.name) AS categories,
               collect(DISTINCT t.name) AS tags,
               collect(DISTINCT {
                   name: commenter.name,
                   text: com.text,
                   date: com.date
               }) AS comments
        """
        with self.driver.session() as session:
            result = session.run(query, title=article_title).single()
            if result:
                # El resultado es un único registro que ya contiene todos los datos agregados
                return {
                    "title": result["title"],
                    "url": result["url"],
                    "text": result["text"],
                    "author": result["author"],
                    "categories": result["categories"],
                    "tags": result["tags"],
                    "comments": result["comments"]
                }
            return None

    def list_nodes(self, label):
        """Lista todos los nodos de una etiqueta (ej. Categorías, Tags)."""
        query = f"MATCH (n:{label}) RETURN properties(n) AS data"
        with self.driver.session() as session:
            result = session.run(query)
            return [record["data"] for record in result]

    def get_articles_by_node(self, node_label, node_name, relation_type):
        """Busca artículos conectados a un Tag o Categoría específica."""
        query = f"""
        MATCH (n:{node_label} {{name: $node_name}})
        <-[:{relation_type}]-
        (a:Article)
        RETURN properties(a) AS article_data
        """
        with self.driver.session() as session:
            result = session.run(query, node_name=node_name)
            return [record["article_data"] for record in result]

    def get_articles_by_category(self, category_name):
        # La relación es (Article)-[:IN_CATEGORY]->(Category)
        return self.get_articles_by_node("Category", category_name, "IN_CATEGORY")

    def get_articles_by_tag(self, tag_name):
        # La relación es (Article)-[:TAGGED_WITH]->(Tag)
        return self.get_articles_by_node("Tag", tag_name, "TAGGED_WITH")

    def update_article_relationships(self, title, new_author, new_category, new_tag_names): # Aceptar lista
        query = """
        MATCH (a:Article {title: $title})
        
        // ====Eliminar TODAS las relaciones existentes de Autor, Categoría y Tags====
        OPTIONAL MATCH (u:User)-[w:WROTE]->(a) DELETE w
        WITH a
        OPTIONAL MATCH (a)-[ic:IN_CATEGORY]->(c:Category) DELETE ic
        WITH a
        // Eliminar todas las relaciones TAGGED_WITH para cualquier Tag
        OPTIONAL MATCH (a)-[tw:TAGGED_WITH]->(t:Tag) DELETE tw
        
        // =========Crear las nuevas relaciones==============
        // Conectar Autor ===================================
        WITH a
        MATCH (new_u:User {name: $new_author})
        MERGE (new_u)-[:WROTE]->(a)
        
        // Conectar Categoría ======================================0
        WITH a
        MATCH (new_c:Category {name: $new_category})
        MERGE (a)-[:IN_CATEGORY]->(new_c)
        
        // Conectar Múltiples Tags usando UNWIND===========================0
        WITH a
        UNWIND $new_tag_names AS tagName // Iterar sobre la lista de Tags
        MATCH (new_t:Tag {name: tagName})
        MERGE (a)-[:TAGGED_WITH]->(new_t)
        
        RETURN a
        """
        with self.driver.session() as session:
            session.run(query, 
                        title=title, 
                        new_author=new_author, 
                        new_category=new_category, 
                        new_tag_names=new_tag_names) # Pasar la lista
        return True