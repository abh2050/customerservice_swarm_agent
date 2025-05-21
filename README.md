# Agent Swarm Implementation

This project implements a multi-agent system (Agent Swarm) that processes user requests through specialized agents working together. The system includes a Router Agent, Knowledge Agent with RAG capabilities, Customer Support Agent with custom tools, and a Personality Layer for human-like responses.

![alt text](image.png)

## Architecture Overview

The Agent Swarm consists of the following components:

1. **Router Agent**: Entry point for user messages that analyzes content and routes to specialized agents
2. **Knowledge Agent**: Handles information retrieval using RAG from InfinitePay website content
3. **Customer Support Agent**: Provides assistance for account-related issues with custom tools
4. **Personality Agent**: Transforms responses to be more human-like and engaging

The agents communicate through a well-defined workflow managed by the Router Agent, with a FastAPI endpoint exposing the functionality.

## Features

- **Message Routing**: Intelligent routing of messages to specialized agents
- **RAG Implementation**: Knowledge retrieval from InfinitePay website content
- **Custom Support Tools**: Account status and troubleshooting tools
- **Personality Layer**: Human-like response transformation
- **API Endpoint**: HTTP interface for message processing
- **Dockerization**: Containerized deployment
- **Comprehensive Testing**: Unit and end-to-end tests

## Getting Started

### Prerequisites

- Docker and Docker Compose
- OpenAI API key (for the Knowledge Agent)

### Installation and Running

1. Clone the repository
2. Set your OpenAI API key in an `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
3. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```
4. The API will be available at `http://localhost:8000`

### API Usage

Send POST requests to `/api/message` with the following JSON payload:

```json
{
  "message": "Your query or statement here",
  "user_id": "some_user_identifier"
}
```

Example response:

```json
{
  "response": "The personality-infused reply or final output",
  "source_agent_response": "The original response from RAG Agent before personality was applied.",
  "agent_workflow": [{"agent_name": "agent_one", "tool_calls": {"tool_a": "tool answer"}}]
}
```

## Project Structure

```
agent_swarm/
├── src/
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── router_agent.py
│   │   ├── knowledge_agent.py
│   │   ├── customer_support_agent.py
│   │   └── personality_agent.py
│   ├── api/
│   │   └── main.py
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_router_agent.py
│   │   │   ├── test_knowledge_agent.py
│   │   │   ├── test_customer_support_agent.py
│   │   │   └── test_personality_agent.py
│   │   └── e2e/
│   │       └── test_api.py
│   └── data/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Implementation Details

### Router Agent

The Router Agent analyzes incoming messages using pattern matching to determine the appropriate specialized agent. It manages the workflow between agents and applies the Personality Layer to responses.

### Knowledge Agent with RAG

The Knowledge Agent uses Retrieval Augmented Generation (RAG) to answer queries about InfinitePay products and services. It scrapes content from the InfinitePay website, creates a vector database, and retrieves relevant information to generate responses.

For general knowledge questions, it uses a simulated web search capability.

### Customer Support Agent

The Customer Support Agent handles account-related issues using two custom tools:

1. **Account Status Tool**: Retrieves account information and recent transactions
2. **Troubleshooting Tool**: Identifies common issues and provides solutions

The agent generates personalized support responses based on the user's account status and identified issues.

### Personality Agent

The Personality Agent transforms responses from other agents to make them more human-like and engaging. It supports multiple personality types (friendly, professional, casual) and applies various transformations like adding greetings, acknowledgments, and conversational elements.

## Testing Strategy

The testing suite includes:

1. **Unit Tests**: Individual tests for each agent, mocking dependencies to isolate functionality
2. **End-to-End Tests**: Tests for the API endpoint, covering various query types and edge cases

The tests ensure that:
- Each agent functions correctly in isolation
- The Router Agent correctly routes messages
- The Knowledge Agent retrieves and generates appropriate responses
- The Customer Support Agent correctly identifies issues and provides solutions
- The Personality Agent properly transforms responses
- The API endpoint handles requests and responses correctly

---

## Testing the Application

### 1. Run Unit and End-to-End Tests

You can run all tests using [pytest](https://docs.pytest.org/):

```bash
# From the project root directory
pip install -r requirements.txt
pip install pytest pytest-asyncio
pytest src/tests/unit
pytest src/tests/e2e
```

All tests should pass, confirming the core functionality of each agent and the API endpoint.

---

## Using the API from the Terminal

### 1. Health Check

Check if the API is running and healthy:

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{"status": "healthy"}
```

### 2. Send a Message to the Agent Swarm

Use a POST request to `/api/message` with your query and user ID:

```bash
curl -X POST http://localhost:8000/api/message \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the fees of the Maquininha Smart?", "user_id": "client789"}'
```

Example response:
```json
{
  "response": "The personality-infused reply or final output",
  "source_agent_response": "The original response from RAG Agent before personality was applied.",
  "agent_workflow": [
    {"agent_name": "Router", "tool_calls": {"message_analysis": {"message": "What are the fees of the Maquininha Smart?"}}},
    {"agent_name": "Knowledge", "tool_calls": {"rag_query": {"query": "What are the fees of the Maquininha Smart?"}}},
    {"agent_name": "Personality", "tool_calls": {"personality_transform": {"personality_type": "friendly"}}}
  ]
}
```

**Tip:**  
If your message contains single quotes, escape them or use double quotes for the outer string:
```bash
curl -X POST http://localhost:8000/api/message \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"I can't sign in to my account.\", \"user_id\": \"client789\"}"
```

---

## Running with Docker

### 1. Build and Start the Application

Make sure you have Docker and Docker Compose installed.  
Set your OpenAI API key in a `.env` file in the project root:

```
OPENAI_API_KEY=your_api_key_here
```

Then build and run the service:

```bash
docker-compose up --build
```

The API will be available at [http://localhost:8000](http://localhost:8000).

### 2. Stopping the Application

To stop the service, press `CTRL+C` in the terminal running Docker Compose, or run:

```bash
docker-compose down
```

---

## Troubleshooting

- If you see `Address already in use`, stop any previous server or use a different port.
- If you get a `dquote>` prompt in the terminal, press `CTRL+C` and re-enter your curl command on a single line, ensuring all quotes and braces are closed.

---

## Docker Configuration

The project includes:
- **Dockerfile**: Builds the application image
- **docker-compose.yml**: Orchestrates the application deployment
- **requirements.txt**: Lists all Python dependencies

The Docker setup ensures the application is easily deployable and includes health checks for monitoring.

## Future Enhancements

Potential enhancements for the system include:

1. **Additional Agents**: Implementing specialized agents for specific tasks
2. **Guardrails**: Adding mechanisms to handle undesired questions/responses
3. **Human Redirection**: Implementing a system to redirect complex queries to human operators
4. **Improved RAG**: Enhancing the knowledge retrieval with more sophisticated techniques
5. **Persistent Storage**: Adding database integration for user data and conversation history

## License

This project is licensed under the MIT License - see the LICENSE file for details.
