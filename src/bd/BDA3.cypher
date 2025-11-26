// 1. Limpiar la base de datos (¡Solo si es necesario!)
MATCH (n) DETACH DELETE n;

// --- Crear Constraints (Mejora de Robustez) ---
// Aunque no es estrictamente necesario, es una buena práctica para asegurar la unicidad.
CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (a:Article) REQUIRE a.title IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (t:Tag) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE;

// 2. Crear Nodos de Usuarios (:User) usando MERGE
UNWIND [
  {name: "Alice", email: "alice@example.com"},
  {name: "Bob", email: "bob@example.com"},
  {name: "Carlos", email: "carlos@example.com"},
  {name: "Diana", email: "diana@example.com"},
  {name: "Eva", email: "eva@example.com"},
  {name: "Frank", email: "frank@example.com"},
  {name: "Gloria", email: "gloria@example.com"},
  {name: "Hugo", email: "hugo@example.com"},
  {name: "Irene", email: "irene@example.com"},
  {name: "Javier", email: "javier@example.com"}
] AS userData
MERGE (:User {email: userData.email, name: userData.name});

// 3. Crear Nodos de Etiquetas (:Tag) usando MERGE
UNWIND [
  "Python", "MongoDB", "Database", "Backend", "Frontend",
  "DevOps", "Cloud", "AI", "ML", "DataScience"
] AS tagName
MERGE (t:Tag {name: tagName})
ON CREATE SET t.url = "/tags/" + toLower(tagName);

// 4. Crear Nodos de Categorías (:Category) usando MERGE
UNWIND [
  "Programming", "Technology", "Education", "Data", "Cloud",
  "AI", "Machine Learning", "Cybersecurity", "Software", "Hardware"
] AS categoryName
MERGE (c:Category {name: categoryName})
ON CREATE SET c.url = "/categories/" + toLower(replace(categoryName, " ", "-"));


// --- 5. Creación de Artículos y Relaciones (Encadenado con WITH) ---
// Esta es la parte más compleja, la simplificaremos usando UNWIND para un solo bloque:
UNWIND [
  {title: "Introducción a Python", date: "2025-11-01", author: "Alice", tag: "Python", category: "Programming", text: "Python es un lenguaje popular y versátil."},
  {title: "Qué es MongoDB", date: "2025-11-02", author: "Bob", tag: "MongoDB", category: "Data", text: "MongoDB es una base de datos NoSQL orientada a documentos."},
  {title: "Backend con Flask", date: "2025-11-03", author: "Carlos", tag: "Backend", category: "Programming", text: "Flask es un microframework muy ligero."},
  {title: "Introducción a DevOps", date: "2025-11-04", author: "Diana", tag: "DevOps", category: "Cloud", text: "DevOps une el desarrollo y las operaciones."},
  {title: "Fundamentos de la nube", date: "2025-11-05", author: "Eva", tag: "Cloud", category: "Cloud", text: "El cloud computing permite escalar servicios fácilmente."},
  {title: "IA en el futuro", date: "2025-11-06", author: "Frank", tag: "AI", category: "AI", text: "La inteligencia artificial impactará todos los sectores."},
  {title: "Machine Learning desde cero", date: "2025-11-07", author: "Gloria", tag: "ML", category: "Machine Learning", text: "Aprende los fundamentos del ML con ejemplos simples."},
  {title: "Ciberseguridad en 2025", date: "2025-11-08", author: "Hugo", tag: "Cloud", category: "Cybersecurity", text: "Proteger la información es más importante que nunca."},
  {title: "Buenas prácticas de programación", date: "2025-11-09", author: "Irene", tag: "Backend", category: "Programming", text: "Escribir código limpio y mantenible es esencial."},
  {title: "Hardware moderno", date: "2025-11-10", author: "Javier", tag: "Database", category: "Hardware", text: "Los nuevos chips mejoran el rendimiento exponencialmente."}
] AS articleData
// 1. Crear el Artículo
CREATE (a:Article {
  title: articleData.title,
  url: "/articles/" + toLower(replace(articleData.title, " ", "-")),
  date: articleData.date,
  text: articleData.text
})
// 2. Conectar al Autor
WITH a, articleData
MATCH (u:User {name: articleData.author})
CREATE (u)-[:WROTE]->(a)
// 3. Conectar a la Etiqueta
WITH a, articleData
MATCH (t:Tag {name: articleData.tag})
CREATE (a)-[:TAGGED_WITH]->(t)
// 4. Conectar a la Categoría
WITH a, articleData
MATCH (c:Category {name: articleData.category})
CREATE (a)-[:IN_CATEGORY]->(c);

// --- 6. Creación de Comentarios y Relaciones ---
UNWIND [
  {author: "Alice", articleTitle: "Introducción a Python", date: "2025-11-01"},
  {author: "Bob", articleTitle: "Qué es MongoDB", date: "2025-11-02"},
  {author: "Carlos", articleTitle: "Backend con Flask", date: "2025-11-03"},
  {author: "Diana", articleTitle: "Introducción a DevOps", date: "2025-11-04"},
  {author: "Eva", articleTitle: "Fundamentos de la nube", date: "2025-11-05"},
  {author: "Frank", articleTitle: "IA en el futuro", date: "2025-11-06"},
  {author: "Gloria", articleTitle: "Machine Learning desde cero", date: "2025-11-07"},
  {author: "Hugo", articleTitle: "Ciberseguridad en 2025", date: "2025-11-08"},
  {author: "Irene", articleTitle: "Buenas prácticas de programación", date: "2025-11-09"},
  {author: "Javier", articleTitle: "Hardware moderno", date: "2025-11-10"}
] AS commentData
// 1. Buscar al Usuario (Autor del comentario) y al Artículo
MATCH (u:User {name: commentData.author})
MATCH (a:Article {title: commentData.articleTitle})
// 2. Crear el Nodo de Comentario
CREATE (c:Comment {
  name: commentData.author,
  url: "/users/" + toLower(commentData.author),
  text: "Excelente artículo, muy útil.",
  date: date(commentData.date)
})
// 3. Conectar el comentario al artículo y al usuario
CREATE (u)-[:WROTE_COMMENT]->(c)
CREATE (c)-[:COMMENTED_ON]->(a);
