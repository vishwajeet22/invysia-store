# invysia-store

An intelligent multi-agent system that creates and delivers custom designed calendars through conversational AI.

**Instagram**: https://www.instagram.com/invysia.store/

## Overview

Invysia Store is a Google ADK-powered agentic team that automates the entire calendar creation process—from customer inquiry to design generation and payment. The system uses two specialized AI agents working together:

- **Iris** - Assistant Sales Manager: Handles customer interactions, gathers requirements, and provides product information
- **Daedalus** - Experienced Designer: Generates creative prompts and produces custom calendar designs

## Architecture

### Multi-Agent System

```
┌─────────────────────────────────────────────────┐
│                    Iris Agent                    │
│         (Assistant Sales Manager)                │
│                                                  │
│  • Customer interaction & requirements gathering │
│  • Product information & infographics           │
│  • Questionnaire management                     │
│  • Delegates design work to Daedalus            │
└──────────────────┬──────────────────────────────┘
                   │
                   │ Sub-agent
                   ▼
┌─────────────────────────────────────────────────┐
│                Daedalus Agent                    │
│            (Experienced Designer)                │
│                                                  │
│  • Theme-based prompt generation                │
│  • Calendar image generation (Gemini 3 Pro)     │
│  • Multi-resolution support (1K/2K/4K)          │
│  • Payment link generation                      │
└─────────────────────────────────────────────────┘
```

### Key Features

#### Iris Agent
- **Infographic Delivery**: Provides visual guides for buying process and product tiers
- **Questionnaire System**: Collects and stores user requirements in session state
- **Customer Service**: Answers questions about products, pricing, and delivery
- **Seamless Handoff**: Delegates design tasks to Daedalus when needed

#### Daedalus Agent
- **AI Prompt Generation**: Uses sub-agent to create 12 themed prompts for calendar months
- **Image Generation**: Leverages Gemini 3 Pro Image model for high-quality calendar designs
- **Async Processing**: Generates all 12 calendar images concurrently for efficiency
- **Template Support**: Works with multiple aspect ratios (9:16, etc.)
- **Resolution Options**: Supports 1K, 2K, and 4K output resolutions
- **Payment Integration**: Generates payment links for completed orders

### Technical Highlights

- **Google ADK Framework**: Built on Google's Agent Development Kit
- **Gemini Models**: Uses Gemini 2.5 Flash for agents and Gemini 3 Pro for image generation
- **Retry Logic**: Configured with exponential backoff for API resilience
- **Session State**: Persistent user data across conversation turns
- **Artifact System**: Delivers images and files directly to users

## Installation

### Prerequisites

- Python 3.8+
- Google API Key with access to Gemini models

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd invysia-store
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   For each agent (iris and daedalus), copy the `.env_template` to `.env`:
   ```bash
   cp iris/.env_template iris/.env
   cp daedalus/.env_template daedalus/.env
   ```
   
   Edit each `.env` file and add your Google API key:
   ```
   GOOGLE_GENAI_USE_VERTEXAI=0
   GOOGLE_API_KEY=your_api_key_here
   ```

## Usage

### Running Individual Agents

**Run Iris (Sales Manager)**
```bash
adk run iris
```

**Run Daedalus (Designer)**
```bash
adk run daedalus
```

### Web UI

Access both agents through the ADK web interface:
```bash
adk web
```

Then navigate to `http://localhost:8000` in your browser.

### Example Workflows

#### Customer Inquiry Flow
1. User starts conversation with Iris
2. Iris asks about requirements (resolution, delivery date, theme)
3. Iris shows product infographics if needed
4. User provides theme and preferences
5. Iris delegates to Daedalus for design generation
6. Daedalus generates 12 themed prompts
7. Daedalus creates calendar images asynchronously
8. Daedalus provides payment link
9. User receives completed calendar in output folder

#### Direct Design Request
1. User contacts Daedalus directly with a theme
2. Daedalus generates prompts using sub-agent
3. User specifies aspect ratio and resolution
4. Daedalus generates all 12 calendar images
5. Output saved to `output_XXX` folder with prompts.txt

## Project Structure

```
invysia-store/
├── iris/                      # Sales Manager Agent
│   ├── agent.py              # Agent configuration
│   ├── src/
│   │   ├── agent_tools.py    # Tools: infographics, questionnaire
│   │   └── agent_persona.py  # Agent instructions
│   ├── assets/               # Infographic images
│   └── .env                  # Environment configuration
├── daedalus/                 # Designer Agent
│   ├── agent.py              # Agent configuration
│   ├── src/
│   │   ├── agent_tools.py    # Tools: prompts, calendar generation
│   │   ├── agent_persona.py  # Agent instructions
│   │   └── sub_agents.py     # Prompt generator sub-agent
│   ├── templates/            # Calendar templates by aspect ratio
│   └── .env                  # Environment configuration
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Development

### Testing

Run tests for individual agents:
```bash
pytest iris/tests/
pytest daedalus/tests/
```

### Adding New Features

- **New Tools**: Add to respective `agent_tools.py` files
- **Agent Instructions**: Modify `agent_persona.py` files
- **Templates**: Add to `daedalus/templates/{aspect_ratio}/`

## License

All rights reserved.

## Contact

For business inquiries, visit our Instagram: [@invysia.store](https://www.instagram.com/invysia.store/)
