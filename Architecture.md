# Invysia Store - System Architecture

## Executive Summary

Invysia Store is a sophisticated multi-agent AI system built on Google's Agent Development Kit (ADK) that automates the end-to-end process of custom calendar creation—from customer inquiry to design generation and payment processing. The system employs a dual-agent architecture where **Iris** (Assistant Sales Manager) handles customer interactions and requirements gathering, while **Daedalus** (Experienced Designer) manages the creative design and image generation workflow.

The architecture is designed for **independent scalability**, **asynchronous processing**, and **persona-driven specialization**, enabling both agents to operate autonomously while maintaining seamless collaboration when needed.

---

## System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│                    (Google ADK Web UI)                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
┌───────────────────────────┐   ┌───────────────────────────┐
│      Iris Agent           │   │    Daedalus Agent         │
│  (Assistant Sales Mgr)    │   │  (Experienced Designer)   │
│                           │   │                           │
│  Model: Gemini 2.5 Flash  │   │  Model: Gemini 2.5 Flash  │
│  Port: Independent        │   │  Port: Independent        │
│                           │   │                           │
│  ┌─────────────────────┐ │   │  ┌─────────────────────┐  │
│  │ Tools:              │ │   │  │ Tools:              │  │
│  │ • get_infographic   │ │   │  │ • generate_prompts  │  │
│  │ • fill_questionnaire│ │   │  │ • generate_calendar │  │
│  └─────────────────────┘ │   │  │ • get_payment_link  │  │
│                           │   │  └─────────────────────┘  │
│  ┌─────────────────────┐ │   │                           │
│  │ Sub-Agents:         │ │   │  ┌─────────────────────┐  │
│  │ • Daedalus (handoff)│─┼───┼─▶│ Sub-Agents:         │  │
│  └─────────────────────┘ │   │  │ • Prompt Generator  │  │
│                           │   │  └─────────────────────┘  │
│  ┌─────────────────────┐ │   │                           │
│  │ State Management:   │ │   │  ┌─────────────────────┐  │
│  │ • user:questionnaire│ │   │  │ State Management:   │  │
│  └─────────────────────┘ │   │  │ • user:prompts      │  │
│                           │   │  └─────────────────────┘  │
└───────────────────────────┘   └───────────────────────────┘
                                              │
                                              ▼
                                 ┌────────────────────────┐
                                 │  Gemini 3 Pro Image    │
                                 │  (Async Generation)    │
                                 │  12 concurrent tasks   │
                                 └────────────────────────┘
```

---

## Agent Personas and Design Rationale

### Why Two Separate Agents?

The dual-agent architecture is driven by **separation of concerns** and **persona specialization**:

1. **Domain Expertise Separation**: Sales and design are fundamentally different skill sets requiring different communication styles, knowledge bases, and decision-making patterns.

2. **Independent Scalability**: Iris and Daedalus can be deployed and scaled independently based on demand:
   - High inquiry volume → Scale Iris instances
   - High design generation load → Scale Daedalus instances

3. **Persona Authenticity**: Each agent maintains a distinct personality and expertise:
   - **Iris**: Polite, professional, customer-service oriented, uses emojis, mirrors user language
   - **Daedalus**: Creative, technical, design-focused, concise and clear

4. **Workflow Isolation**: Design generation is computationally expensive and time-consuming. Isolating it in Daedalus prevents blocking Iris from handling other customer inquiries.

### Iris - Assistant Sales Manager

**Persona Characteristics:**
- **Role**: Front-line customer interaction, requirements gathering, product education
- **Tone**: Polite, enthusiastic, patient, uses emojis (😊, 👍, 💡)
- **Communication Style**: Mirrors user language (casual/gen-z when appropriate), never defensive or all-knowing

**Core Responsibilities:**
1. **Customer Onboarding**: Introduces self, asks for user name (with sensitivity)
2. **Requirements Discovery**: Understands user needs and budget constraints
3. **Product Education**: Provides infographics for product tiers and buying process
4. **Questionnaire Management**: Collects structured data (name, email, resolution, aspect ratio, delivery date, purpose, package)
5. **Handoff Orchestration**: Transfers user to Daedalus when design work begins

**Knowledge Boundaries:**
- **Strict Source of Truth**: Product Brief document only
- **Forbidden Topics**: Final pricing, invoicing, payment link generation, detailed design discussions
- **Handoff Protocol**: Once transferred to Daedalus, Iris stops selling

**Why This Persona?**
- Sales requires empathy, patience, and adaptability—traits modeled through conversational AI
- Clear boundaries prevent scope creep and maintain agent specialization
- Questionnaire system ensures structured data collection for downstream processing

### Daedalus - Experienced Designer

**Persona Characteristics:**
- **Role**: Creative design generation, technical execution, payment processing
- **Tone**: Professional, clear, concise, helpful
- **Communication Style**: Short sentences, human-like, focused on design outcomes

**Core Responsibilities:**
1. **Theme Discussion**: Collaborates with user on design vision (excludes fonts/calligraphy)
2. **Prompt Generation**: Uses sub-agent to create 12 themed prompts
3. **Design Validation**: Explains prompts to user, iterates if needed
4. **Payment Processing**: Generates payment links
5. **Calendar Generation**: Orchestrates async image generation with Gemini 3 Pro

**Technical Capabilities:**
- Multi-resolution support (1K, 2K, 4K)
- Multiple aspect ratios (9:16, 3:4, 4:3)
- Template-based generation
- Concurrent image processing (12 images simultaneously)

**Why This Persona?**
- Design work requires technical precision and creative understanding
- Async architecture enables efficient resource utilization
- Sub-agent pattern offloads specialized prompt generation logic

---

## Tool Architecture

### Iris Tools

#### 1. `get_infographic`
**Purpose**: Delivers visual guides to users as artifacts

**Implementation Details:**
- **Type**: Async function
- **Parameters**: `process_name` (buying_process | product_tiers)
- **Artifact System**: Uses ADK's `save_artifact` to deliver images directly to user
- **Fallback**: Requests placeholder image if local asset missing

**Why This Tool?**
- Visual communication is more effective than text for process flows and pricing
- Artifact system ensures images are rendered in UI without LLM processing
- Async design prevents blocking during image loading

#### 2. `fill_questionnaire`
**Purpose**: Stores structured user data in session state

**Implementation Details:**
- **Type**: Synchronous function
- **State Key**: `user:questionnaire` (user-scoped persistence)
- **Data Structure**: List of `{question, answer}` dictionaries

**Why This Tool?**
- Structured data collection enables downstream processing by Daedalus
- Session state ensures data persists across conversation turns
- Prevents redundant questions by checking existing state

### Daedalus Tools

#### 1. `generate_prompts`
**Purpose**: Creates 12 themed image editing prompts using a sub-agent

**Implementation Details:**
- **Type**: Async function
- **Sub-Agent**: `prompt_generator` (Gemini 2.5 Flash)
- **Agent Tool Pattern**: Wraps sub-agent as `AgentTool` for invocation
- **Output Normalization**: Parses various formats (list, string, markdown code blocks) into Python list
- **State Storage**: Saves prompts to `user:prompts` for downstream use

**Why This Tool?**
- **Specialization**: Prompt generation requires creative expertise—delegating to a sub-agent maintains separation of concerns
- **Async Design**: Prevents blocking main agent during prompt generation
- **State Persistence**: Prompts are stored for later use by `generate_calendar`

**Sub-Agent: Prompt Generator**
- **Model**: Gemini 2.5 Flash
- **Instructions**: 
  - Generate exactly 12 prompts
  - Start each with "Edit this image"
  - Focus on background editing only
  - Preserve existing text (dates, months)
  - Allow font style/color adaptation for contrast

**Why a Sub-Agent?**
- Prompt generation is a specialized creative task
- Isolates prompt logic from main agent workflow
- Enables independent testing and refinement

#### 2. `generate_calendar`
**Purpose**: Orchestrates async generation of 12 calendar images

**Implementation Details:**
- **Type**: Async function
- **Parameters**: `aspect_ratio`, `resolution`
- **State Retrieval**: Fetches prompts from `user:prompts`
- **Template System**: Maps aspect ratio to template folder (e.g., `9:16` → `9_16`)
- **Async Orchestration**: 
  - Creates 12 `asyncio.create_task` instances
  - Each task calls `generate_images_gemini_3_pro`
  - `asyncio.gather` waits for all tasks with exception handling
- **Output Management**: Creates `output_XXX` folder with random 3-digit suffix

**Why This Tool?**
- **Async Architecture**: Generates all 12 images concurrently, reducing total time from ~12x to ~1x
- **Template-Based**: Ensures consistent calendar structure across months
- **Error Handling**: `return_exceptions=True` allows partial success reporting

#### 3. `get_payment_link`
**Purpose**: Generates payment link for completed orders

**Implementation Details:**
- **Type**: Synchronous function
- **Current Implementation**: Returns mock payment link

**Why This Tool?**
- Separates payment logic from design logic
- Placeholder for future payment gateway integration

---

## Asynchronous Architecture

### Why Async?

1. **Concurrent Image Generation**: Generating 12 calendar images sequentially would take ~12x longer than concurrent generation
2. **Non-Blocking I/O**: API calls to Gemini models don't block agent processing
3. **Resource Efficiency**: Better utilization of network and compute resources
4. **User Experience**: Faster response times for design generation

### Async Implementation Details

#### Tool-Level Async
```python
async def generate_prompts(theme: str, tool_context: ToolContext) -> List[str]:
    agent_tool = AgentTool(agent=prompt_generator)
    raw_output = await agent_tool.run_async(...)  # Non-blocking sub-agent call
    return prompts
```

#### Task-Level Async (Concurrent Execution)
```python
async def generate_calendar(...):
    tasks = []
    for i, prompt in enumerate(prompts):
        task = asyncio.create_task(
            generate_images_gemini_3_pro(...)  # Create task without awaiting
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)  # Wait for all
```

#### API-Level Async
```python
async def generate_images_gemini_3_pro(...):
    response = await client.aio.models.generate_content(...)  # Async API call
```

### Retry Logic with Exponential Backoff

**Agent-Level Retry** (HTTP Errors):
```python
retry_config = HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)
```

**Tool-Level Retry** (Image Generation):
```python
max_retries = 3
retry_delay = 1
for attempt in range(max_retries):
    try:
        response = await client.aio.models.generate_content(...)
        break
    except Exception as e:
        await asyncio.sleep(retry_delay)
        retry_delay *= 2  # Exponential backoff
```

**Why Retry Logic?**
- **API Resilience**: Handles transient network failures and rate limiting
- **Exponential Backoff**: Prevents overwhelming the API during outages
- **Partial Success**: Image generation continues even if some images fail

---

## State Management

### Session State Architecture

Google ADK provides persistent session state across conversation turns. Invysia Store uses **user-scoped state** with the `user:` prefix.

#### Iris State
```python
tool_context.state["user:questionnaire"] = [
    {"question": "What is your name?", "answer": "John"},
    {"question": "What resolution do you need?", "answer": "2K"},
    ...
]
```

**Why State?**
- Prevents asking duplicate questions
- Enables data handoff to Daedalus
- Maintains conversation context across turns

#### Daedalus State
```python
tool_context.state["user:prompts"] = [
    "Edit this image to have a futuristic space theme...",
    "Edit this image to show a Mars landscape...",
    ...  # 12 prompts total
]
```

**Why State?**
- Decouples prompt generation from image generation
- Allows user to review prompts before generation
- Enables regeneration without re-prompting

### State Lifecycle

1. **Iris** collects questionnaire data → stores in `user:questionnaire`
2. **Iris** transfers to **Daedalus** (state persists across agents)
3. **Daedalus** generates prompts → stores in `user:prompts`
4. **Daedalus** retrieves prompts from state → generates calendar

---

## Model Selection and Rationale

### Gemini 2.5 Flash (Agent Orchestration)

**Used By:**
- Iris root agent
- Daedalus root agent
- Prompt Generator sub-agent

**Why Gemini 2.5 Flash?**
1. **Speed**: Fast response times for conversational interactions
2. **Cost-Effectiveness**: Lower cost per token compared to Pro models
3. **Sufficient Capability**: Handles tool calling, reasoning, and persona maintenance
4. **Multimodal**: Supports text and image inputs (for infographics)

**Configuration:**
```python
model = Gemini(
    model="gemini-2.5-flash",
    retry_options=retry_config
)
```

### Gemini 3 Pro Image (Image Generation)

**Used By:**
- `generate_images_gemini_3_pro` function in Daedalus

**Why Gemini 3 Pro Image?**
1. **Image Generation Capability**: Specifically designed for image generation tasks
2. **High Quality**: Produces professional-grade calendar designs
3. **Resolution Support**: Handles 1K, 2K, and 4K outputs
4. **Aspect Ratio Flexibility**: Supports 9:16, 3:4, 4:3 ratios
5. **Template Editing**: Can edit existing images (calendar templates) while preserving structure

**Configuration:**
```python
response = await client.aio.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[prompt, template_image],
    config=types.GenerateContentConfig(
        response_modalities=['IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio=aspect_ratio,
            image_size=resolution
        )
    )
)
```

**Why Not Use Gemini 2.5 Flash for Images?**
- Flash models are optimized for text generation, not image synthesis
- Pro Image models provide significantly higher quality and control

---

## Independent Deployment and Scalability

### Deployment Architecture

Both agents are designed as **independent ADK applications**:

```
invysia-store/
├── iris/
│   ├── agent.py          # Iris root agent definition
│   ├── src/
│   │   ├── agent_tools.py
│   │   └── agent_persona.py
│   └── .env              # Independent API key configuration
└── daedalus/
    ├── agent.py          # Daedalus root agent definition
    ├── src/
    │   ├── agent_tools.py
    │   ├── agent_persona.py
    │   └── sub_agents.py
    └── .env              # Independent API key configuration
```

### Running Independently

**Iris Only:**
```bash
adk run iris
```

**Daedalus Only:**
```bash
adk run daedalus
```

**Both via Web UI:**
```bash
adk web  # Access both agents at http://localhost:8000
```

### Scalability Patterns

#### Horizontal Scaling
- Deploy multiple Iris instances behind a load balancer for high inquiry volume
- Deploy multiple Daedalus instances for parallel design generation
- Each instance maintains independent session state

#### Vertical Scaling
- Increase async task concurrency in Daedalus for more simultaneous image generation
- Adjust retry configuration based on API quota

#### Hybrid Deployment
- **Scenario 1**: User directly contacts Daedalus (bypasses Iris)
  - Daedalus operates fully independently
  - User provides theme directly
  
- **Scenario 2**: User starts with Iris (full workflow)
  - Iris collects requirements
  - Iris transfers to Daedalus via `sub_agents` relationship
  - Daedalus completes design generation

### Sub-Agent Relationship

```python
# In iris/agent.py
from daedalus.agent import root_agent as daedalus_agent

root_agent = Agent(
    ...
    sub_agents=[daedalus_agent],  # Iris can transfer to Daedalus
)
```

**Why Sub-Agent Pattern?**
- Enables seamless handoff from Iris to Daedalus
- Maintains conversation context during transfer
- Daedalus remains independently deployable (not tightly coupled)

---

## Data Flow: End-to-End Workflow

### Scenario 1: Full Customer Journey (Iris → Daedalus)

```
1. User initiates conversation
   ↓
2. Iris: Introduction and name collection
   ↓
3. Iris: Requirements discussion (budget, use case)
   ↓
4. Iris: Delivers product_tiers infographic (get_infographic tool)
   ↓
5. User: Selects package
   ↓
6. Iris: Explains buying process (get_infographic tool)
   ↓
7. Iris: Collects questionnaire data (fill_questionnaire tool × 7)
   State: user:questionnaire = [{q1, a1}, {q2, a2}, ...]
   ↓
8. Iris: Transfers to Daedalus (transfer_to_agent)
   ↓
9. Daedalus: Introduction and theme discussion
   ↓
10. Daedalus: Generates prompts (generate_prompts tool)
    → Calls prompt_generator sub-agent (async)
    → Parses and normalizes output
    State: user:prompts = [p1, p2, ..., p12]
    ↓
11. Daedalus: Explains prompts to user
    ↓
12. User: Approves prompts
    ↓
13. Daedalus: Generates payment link (get_payment_link tool)
    ↓
14. Daedalus: Generates calendar (generate_calendar tool)
    → Retrieves prompts from state
    → Creates 12 async tasks
    → Each task calls generate_images_gemini_3_pro
    → Gemini 3 Pro Image generates images concurrently
    → Saves to output_XXX folder
    ↓
15. Daedalus: Confirms completion to user
```

### Scenario 2: Direct Design Request (Daedalus Only)

```
1. User initiates conversation with Daedalus directly
   ↓
2. Daedalus: Introduction
   ↓
3. User: Provides theme (e.g., "Space exploration theme")
   ↓
4. Daedalus: Generates prompts (generate_prompts tool)
   State: user:prompts = [p1, p2, ..., p12]
   ↓
5. Daedalus: Explains prompts
   ↓
6. User: Approves and specifies aspect_ratio="9:16", resolution="2K"
   ↓
7. Daedalus: Generates payment link (get_payment_link tool)
   ↓
8. Daedalus: Generates calendar (generate_calendar tool)
   Output: output_XXX/ folder with 12 images + prompts.txt
   ↓
9. Daedalus: Confirms completion
```

---

## Template System

### Structure

```
daedalus/templates/
├── 9_16/          # Aspect ratio 9:16
│   ├── 1-2026.png
│   ├── 2-2026.png
│   └── ...        # 12 templates
├── 3_4/           # Aspect ratio 3:4
│   └── ...
└── 4_3/           # Aspect ratio 4:3
    └── ...
```

### Template Usage

1. User specifies aspect ratio (e.g., "9:16")
2. `generate_calendar` maps to folder: `9:16` → `9_16`
3. For each month (1-12), loads template: `templates/9_16/{month}-2026.png`
4. Passes template + prompt to Gemini 3 Pro Image
5. Model edits template background while preserving calendar structure

**Why Templates?**
- Ensures consistent calendar layout (dates, months, grid)
- Allows focus on background design rather than calendar structure
- Supports multiple aspect ratios without redesigning logic

---

## Error Handling and Resilience

### Agent-Level Resilience

**HTTP Retry Configuration:**
```python
retry_config = HttpRetryOptions(
    attempts=5,              # Retry up to 5 times
    exp_base=7,              # 7^n exponential backoff
    initial_delay=1,         # Start with 1 second delay
    http_status_codes=[429, 500, 503, 504]  # Rate limit, server errors
)
```

**Retry Sequence:**
- Attempt 1: Immediate
- Attempt 2: 1s delay
- Attempt 3: 7s delay
- Attempt 4: 49s delay
- Attempt 5: 343s delay

### Tool-Level Resilience

**Image Generation Retry:**
```python
max_retries = 3
retry_delay = 1  # Exponential: 1s, 2s, 4s
```

**Partial Failure Handling:**
```python
results = await asyncio.gather(*tasks, return_exceptions=True)
failures = [r for r in results if isinstance(r, Exception)]
if failures:
    return f"Calendar generation completed with some errors: {failures}"
```

**Why Partial Success?**
- User gets 9/12 images instead of 0/12 if 3 fail
- Enables manual retry of failed images
- Provides detailed error reporting

### Validation and Fallbacks

**Prompt Validation:**
```python
if not prompts or len(prompts) != 12:
    return "Error: Could not find exactly 12 prompts..."
```

**Template Validation:**
```python
try:
    template_image = Image.open(template_path)
except FileNotFoundError:
    return f"Error: Template file not found at {template_path}..."
```

**Infographic Fallback:**
```python
if not image_path.exists():
    # Fetch placeholder image from web
    response = requests.get("https://fastly.picsum.photos/...")
```

---

## Security and Configuration

### Environment Configuration

Each agent maintains independent `.env` files:

```
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY=your_api_key_here
```

**Why Independent Configuration?**
- Allows different API keys for different agents
- Enables separate quota management
- Supports different authentication methods (API key vs Vertex AI)

### API Key Management

```python
client = genai.Client(
    api_key=os.environ["GOOGLE_API_KEY"],
    http_options=types.HttpOptions(timeout=60000)
)
```

**Security Best Practices:**
- API keys stored in `.env` (gitignored)
- `.env_template` provided for setup guidance
- No hardcoded credentials in source code

---

## Testing Architecture

### Test Structure

```
iris/tests/
└── test_agent_tools.py

daedalus/tests/
└── test_agent_tools.py
```

### Test Configuration

```python
# requirements.txt
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

**Why pytest-asyncio?**
- Enables testing of async tools (`generate_prompts`, `generate_calendar`)
- Supports async fixtures and test functions

### Running Tests

```bash
pytest iris/tests/
pytest daedalus/tests/
```

---

## Performance Characteristics

### Iris Performance

- **Response Time**: ~1-2 seconds (Gemini 2.5 Flash)
- **Infographic Delivery**: ~500ms (local file read + artifact save)
- **Questionnaire Update**: ~100ms (state write)

### Daedalus Performance

- **Prompt Generation**: ~5-10 seconds (sub-agent call)
- **Calendar Generation (Sequential)**: ~120-240 seconds (12 images × 10-20s each)
- **Calendar Generation (Async)**: ~20-30 seconds (concurrent execution)

**Performance Improvement:**
- Async architecture provides **4-8x speedup** for calendar generation

### Bottlenecks and Optimizations

**Current Bottlenecks:**
1. Gemini 3 Pro Image API latency (~10-20s per image)
2. Network I/O for API calls

**Optimization Strategies:**
1. ✅ **Implemented**: Async concurrent image generation
2. ✅ **Implemented**: Retry logic with exponential backoff
3. 🔄 **Future**: Caching of common themes/prompts
4. 🔄 **Future**: Pre-generation of popular templates

---

## Future Enhancements

### Planned Improvements

1. **Payment Integration**: Replace mock payment link with real gateway (Stripe, Razorpay)
2. **User Authentication**: Add user accounts for order history
3. **Template Customization**: Allow users to upload custom templates
4. **Prompt Caching**: Cache frequently used themes to reduce sub-agent calls
5. **Analytics Dashboard**: Track conversion rates, popular themes, agent performance
6. **Multi-Language Support**: Extend personas to support multiple languages
7. **Image Editing**: Allow users to request edits to generated calendars

### Scalability Roadmap

1. **Database Integration**: Move from session state to persistent database (PostgreSQL, Firestore)
2. **Message Queue**: Use Pub/Sub for async task distribution
3. **CDN Integration**: Serve generated calendars via CDN
4. **Kubernetes Deployment**: Containerize agents for cloud-native scaling

---

## Core Technologies and Models Summary

### Frameworks and Libraries

| Technology | Version | Purpose |
|:-----------|:--------|:--------|
| **Google ADK** | ≥0.1.0 | Agent orchestration, tool management, session state |
| **Google GenAI** | ≥1.0.0 | Gemini model API client |
| **Pillow** | ≥10.0.0 | Image processing (template loading) |
| **asyncio** | Built-in | Asynchronous task orchestration |
| **pytest** | ≥7.4.0 | Testing framework |
| **pytest-asyncio** | ≥0.21.0 | Async test support |
| **requests** | ≥2.31.0 | HTTP requests (fallback image fetching) |

### AI Models

| Model | Usage | Rationale |
|:------|:------|:----------|
| **Gemini 2.5 Flash** | Iris agent, Daedalus agent, Prompt Generator sub-agent | Fast, cost-effective, sufficient for conversational AI and tool calling |
| **Gemini 3 Pro Image** | Calendar image generation | High-quality image synthesis, template editing, multi-resolution support |

### Architecture Patterns

| Pattern | Implementation | Benefit |
|:--------|:---------------|:--------|
| **Multi-Agent System** | Iris + Daedalus | Separation of concerns, independent scalability |
| **Sub-Agent Pattern** | Daedalus → Prompt Generator | Specialized task delegation, modularity |
| **Async/Await** | Tool functions, API calls | Concurrent execution, non-blocking I/O |
| **State Management** | ADK session state with `user:` prefix | Persistent data across conversation turns |
| **Retry with Exponential Backoff** | HTTP and API-level retries | Resilience to transient failures |
| **Artifact System** | Infographic and image delivery | Direct user delivery without LLM processing |
| **Template-Based Generation** | Calendar templates by aspect ratio | Consistent structure, design flexibility |

### Deployment Models

| Model | Command | Use Case |
|:------|:--------|:---------|
| **Standalone Iris** | `adk run iris` | Customer service only |
| **Standalone Daedalus** | `adk run daedalus` | Direct design requests |
| **Web UI (Both)** | `adk web` | Full customer journey |

---

## Conclusion

The Invysia Store architecture demonstrates a sophisticated application of Google ADK's multi-agent capabilities, combining:

1. **Persona-Driven Design**: Specialized agents with distinct roles and communication styles
2. **Async-First Architecture**: Concurrent image generation for 4-8x performance improvement
3. **State-Driven Workflows**: Persistent session state enables complex multi-turn interactions
4. **Independent Scalability**: Agents can be deployed and scaled independently
5. **Resilient Design**: Multi-level retry logic and partial failure handling
6. **Model Optimization**: Right-sized models for each task (Flash for orchestration, Pro for generation)

This architecture enables Invysia Store to deliver a premium, automated calendar creation experience while maintaining flexibility for future enhancements and scale.
