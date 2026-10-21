from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph
from src.application.graph.nodes import DockerfileAnalysisNodes
from src.application.graph.state import DockerfileState


class DockerfileGraphBuilder:

  def __init__(self, llm: ChatGoogleGenerativeAI):
    self.nodes = DockerfileAnalysisNodes(llm)

  def build(self):
    workflow = StateGraph(DockerfileState)

    workflow.add_node("parse_dockerfile", self.nodes.parse_dockerfile)
    workflow.add_node("analyze_security", self.nodes.analyze_security)
    workflow.add_node("generate_report", self.nodes.generate_report)

    workflow.set_entry_point("parse_dockerfile")
    workflow.add_edge("parse_dockerfile", "analyze_security")
    workflow.add_edge("analyze_security", "generate_report")
    workflow.add_edge("generate_report", END)

    return workflow.compile()