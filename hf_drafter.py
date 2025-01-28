from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from phoenix.otel import register

from smolagents import (
    CodeAgent,
    DuckDuckGoSearchTool,
    LiteLLMModel,
    ManagedAgent,
    ToolCallingAgent,
    VisitWebpageTool,
)

from smolagents import tool 
# import packages that are used in our tools
import requests
from bs4 import BeautifulSoup
import json
import gh_draft, hf_draft


trace_provider = TracerProvider()
trace_provider = register(
  endpoint="http://localhost:4317",  # Sends traces using gRPC
)
trace_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter("http://0.0.0.0:6006/v1/traces")))

SmolagentsInstrumentor().instrument(tracer_provider=trace_provider)

# Then we run the agentic part!
# model = HfApiModel()
model = LiteLLMModel(
    # model_id="ollama/qwen2.5-coder:32b-instruct-q4_K_M",
    model_id="ollama/llama3.3:70b-instruct-q4_K_S",
    api_base="http://localhost:11434",  # replace with remote open-ai compatible server if necessary
    api_key="your-api-key",  # replace with API key if necessary
)


@tool
def final_answer(answer: str) -> None:
    """
    Presents final answer on your task to manager
    Args:
        answer: string with all nessesary information on task
    """
    print(answer)
    return None


add_imports = ['bs4', 'requests', 'json']

agent = CodeAgent(
    # tools=[
        # DuckDuckGoSearchTool(), 
        # VisitWebpageTool()
        # ],
    tools=[hf_draft.get_hugging_face_top_daily_paper,
                         hf_draft.get_paper_id_by_title,
                         hf_draft.download_paper_by_id,
                         hf_draft.read_pdf_file,
                         final_answer],
    model=model,
    additional_authorized_imports=add_imports
)
managed_hf_agent = ManagedAgent(
    agent=agent,
    name="managed_hf_agent",
    description="This is an agent that can parse hf papers",
)

agent = CodeAgent(
    # tools=[
        # DuckDuckGoSearchTool(), 
        # VisitWebpageTool()
        # ],
    tools=[
        gh_draft.get_repo_info,
        gh_draft.get_file_content,
        gh_draft.get_repo_structure,
        final_answer
           ],
    model=model,
    additional_authorized_imports=add_imports
)
managed_gh_agent = ManagedAgent(
    agent=agent,
    name="managed_gh_agent",
    description="This is an agent that gets info about github repositories",
)


manager_agent = CodeAgent(
    # tools=[DuckDuckGoSearchTool(), VisitWebpageTool()],
    tools=[],
    model=model,
    managed_agents=[managed_hf_agent, managed_gh_agent],
)

manager_agent.run(
    # "If the US keeps it 2024 growth rate, how many years would it take for the GDP to double?"
    # "Summarize today's top paper on Hugging Face daily papers by reading it.",
    # "Get general info and structure of hummingbot/hummingbot repo"
    # "Make deep investigation of github repo missglory/agent-drafters with your team. Compose detailed explanation of overall architecture of this project."
    # "Make deep analysis of github repo missglory/agent-drafters with your team. Use your gh agent in order to gather all actual info. Make sure that"
    # "You are investigating github project missglory/agent-drafters with your team. Make step by step analysis. First, get actual directory structure, then based on that information read all existing file contents and create summary for each file"
    # "Get structure of repo missglory/agent-drafters with your team. What file might be most interesting?"
    "Get structure info on github repo missglory/agent-drafters with your team. Once done, read contents of next most interesting file on your opinion, compose summary after reading it"
)


# agent = CodeAgent(tools=[get_hugging_face_top_daily_paper,
#                          get_paper_id_by_title,
#                          download_paper_by_id,
#                          read_pdf_file],
#                   model=model,
#                   add_base_tools=True)

# agent.run(
#     "Summarize today's top paper on Hugging Face daily papers by reading it.",
# )


