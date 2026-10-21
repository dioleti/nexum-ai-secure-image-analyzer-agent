from typing import List, TypedDict


class DockerfileState(TypedDict):
  dockerfile_content: str
  base_image: str
  parsed_steps: List[str]
  vulnerabilities: List[str]
  harmful_practices: List[str]
  report: str