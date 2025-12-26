class KGRetriever:
    def __init__(self, neo4j_client):
        self.neo4j = neo4j_client

    def get_framework_by_question(self, question: str):
        # Simple heuristic (good enough for now)
        keywords = ["promotion", "marketing communication", "communication"]
        for kw in keywords:
            if kw in question.lower():
                return self.neo4j.get_framework_by_name("Promotion Mix")
        return None

    def get_framework_components(self, framework_name: str):
        return self.neo4j.get_components_of_framework(framework_name)