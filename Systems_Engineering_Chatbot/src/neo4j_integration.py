import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

class Neo4jConnection:
    def __init__(self):
        self.uri = os.environ.get("NEO4J_URI")
        self.user = os.environ.get("NEO4J_USERNAME")
        self.password = os.environ.get("NEO4J_PASSWORD")
        self.database = os.environ.get("NEO4J_DATABASE")
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        except Exception as e:
            print(f"Failed to create Neo4j driver: {e}")

    def close(self):
        if self.driver is not None:
            self.driver.close()

    def query(self, query, parameters=None, db=None):
        if self.driver is None:
            print("Driver not initialized, cannot run query")
            return []
        
        db = db if db is not None else self.database
        with self.driver.session(database=db) as session:
            result = session.run(query, parameters)
            return [record for record in result]

    def get_graph_data(self, system_topic):
        """
        Fetches graph data for a specific system from Neo4j.
        """
        query = """
        MATCH (s {system_topic: $system_topic})-[r]->(t)
        RETURN s, r, t
        """
        records = self.query(query, parameters={"system_topic": system_topic})
        
        nodes = []
        edges = []
        node_ids = set()

        for record in records:
            source_node = record["s"]
            target_node = record["t"]
            relationship = record["r"]

            if source_node.id not in node_ids:
                nodes.append({
                    "id": source_node.id,
                    "label": source_node.get("label", "Node"),
                    "group": source_node.get("group", "Default"),
                    "title": source_node.get("title", "")
                })
                node_ids.add(source_node.id)

            if target_node.id not in node_ids:
                nodes.append({
                    "id": target_node.id,
                    "label": target_node.get("label", "Node"),
                    "group": target_node.get("group", "Default"),
                    "title": target_node.get("title", "")
                })
                node_ids.add(target_node.id)

            edges.append({
                "from": source_node.id,
                "to": target_node.id,
                "label": type(relationship).__name__
            })
            
        return {"nodes": nodes, "edges": edges}

    def save_graph_data(self, system_topic, graph_data):
        """
        Saves the complete graph data (nodes and edges) to Neo4j.
        """
        # Clear existing graph data for this system topic to prevent duplicates
        self.query(
            "MATCH (s {system_topic: $system_topic})-[r]-() DETACH DELETE r",
            parameters={"system_topic": system_topic}
        )
        self.query(
            "MATCH (n {system_topic: $system_topic}) DETACH DELETE n",
            parameters={"system_topic": system_topic}
        )

        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])

        # Create nodes
        for node in nodes:
            self.query(
                """
                CREATE (n:`{group}` {{id: $id, label: $label, title: $title, system_topic: $system_topic}})
                """.format(group=node.get("group", "Artifact")),
                parameters={
                    "id": node.get("id"),
                    "label": node.get("label"),
                    "title": node.get("title"),
                    "system_topic": system_topic
                }
            )

        # Create edges
        for edge in edges:
            self.query(
                """
                MATCH (a), (b)
                WHERE a.id = $from AND b.id = $to
                CREATE (a)-[r:RELATES_TO {{label: $label}}]->(b)
                RETURN type(r)
                """,
                parameters={
                    "from": edge.get("from"),
                    "to": edge.get("to"),
                    "label": edge.get("label", "relates to")
                }
            )

    def save_mathematical_model(self, system_topic, model_name, model_definition):
        """
        Saves a mathematical model or concept to Neo4j.
        """
        query = """
        MERGE (s:System {name: $system_topic})
        MERGE (m:MathematicalModel {name: $model_name, definition: $model_definition})
        MERGE (s)-[:HAS_MODEL]->(m)
        """
        self.query(query, parameters={"system_topic": system_topic, "model_name": model_name, "model_definition": model_definition})

    def get_mathematical_models(self, system_topic):
        """
        Fetches all mathematical models for a specific system from Neo4j.
        """
        query = """
        MATCH (s:System {name: $system_topic})-[:HAS_MODEL]->(m:MathematicalModel)
        RETURN m
        """
        records = self.query(query, parameters={"system_topic": system_topic})
        
        models = []
        for record in records:
            node = record["m"]
            models.append({
                "name": node.get("name"),
                "definition": node.get("definition")
            })
        return models

if __name__ == '__main__':
    # Example usage
    conn = Neo4jConnection()
    
    # Example: Add a new artifact
    # conn.add_artifact_to_graph("System Requirement", "The system shall be awesome.", "Awesome System")

    # Example: Fetch graph data
    # graph_data = conn.get_graph_data("Awesome System")
    # print(graph_data)

    conn.close()
