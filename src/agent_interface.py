"""
Public Agent Interface for BinusBrain
"""

from src.agent_runner import run_agent


class BinusBrainAgent:
    def upload(self, user_id: str, file_data: bytes, filename: str) -> dict:
        return run_agent({
            "action": "upload",
            "user_id": user_id,
            "file_data": file_data,
            "filename": filename
        })

    def ask(self, user_id: str, question: str) -> dict:
        return run_agent({
            "action": "query",
            "user_id": user_id,
            "question": question
        })

    def visualize(self, user_id: str) -> dict:
        return run_agent({
            "action": "visualize",
            "user_id": user_id
        })


# singleton
agent = BinusBrainAgent()