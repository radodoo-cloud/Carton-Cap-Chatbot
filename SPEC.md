Technical Specification — Carton Caps AI Chat Agent
Deliverable #1: Conversational AI Design + LLM Strategy


Table of Contents
Overview & Point of View
API Contract
System Diagrams
Mobile Integration
LLM Strategy & Reasoning
Conversation Design Principles
Privacy Considerations
Trade-offs & Alternatives Considered
Evolution Roadmap


1. Overview & Point of View
Capper is meant to do one job well, not everything. That single idea shaped every decision in this document.

When someone opens the Carton Caps chat, they almost always want one of two things: help finding products that support their school, or help understanding how the referral program works. They're not looking to chat for the sake of chatting. So Capper is built to be quick, to be right within those two areas, and to say plainly when something is outside what it can help with — rather than guessing and risking a wrong or off-brand answer.

The guiding rule behind the whole design is simple: the model is kept on a short leash. It's not trusted to know things on its own.

The AI model (GPT-4o-mini) is only used to turn real information into a natural-sounding reply — it's a communicator, not a source of truth. Anything Capper says about a product or the referral program comes from data the system actually looked up, never from what the model happens to "remember." That one choice is the backbone of the whole design.


2. API Contract
The API is a standard REST service — every request and response is JSON, and it follows a simple, resource-based URL pattern.

Base URL: http://localhost:8000 API Version: v1


2.1 Endpoints
POST /v1/chat/conversations
Starts a new chat session and returns Capper's opening message.

Request

{

  "entry_point": "home_widget"

}

Field
Type
Required
Default
What it's for
entry_point
string
No
home_widget
Where in the app the chat was opened from. Useful later for tailoring the greeting and for basic analytics.


Response 200

{

  "conversation_id": "c_3f9a1b2c",

  "greeting": "Hi! I am Capper. I can help you find products that support your school!"

}

Field
Type
What it's for
conversation_id
string
The session's ID — the app needs to send this with every message that follows.
greeting
string
Capper's first message.



POST /v1/chat/conversations/{conversation_id}/messages
Sends one user message and gets Capper's reply back.

Path Parameters | Parameter | Type | What it's for | |---|---|---| | conversation_id | string | The ID handed back when the conversation was created |

Request

{

  "content": "What snacks support my school?"

}

Field
Type
Required
Limits
What it's for
content
string
Yes
1–1000 characters
The user's message


Response 200

{

  "message_id": "m_7c4d2e1f",

  "role": "assistant",

  "intent": "PRODUCT_QUERY",

  "reply": "Here are some snacks from our catalog that support your school:\n- Granola Cereal Bars — $5.92\n- Frosted Flakes Cereal — $3.79",

  "retrieved_data": [

    { "id": 2, "name": "Granola Cereal Bars", "price": 5.92 },

    { "id": 1, "name": "Frosted Flakes Cereal", "price": 3.79 }

  ]

}

Field
Type
What it's for
message_id
string
ID of Capper's reply
role
string
Always "assistant"
intent
string
What kind of question this was: PRODUCT_QUERY, FAQ_QUERY, or GENERAL
reply
string
Capper's actual reply, in plain language
retrieved_data
array
The real data behind that reply — empty when the question was GENERAL (small talk)


Error Responses

Status
When it happens
Message
400
Empty message
"Message content cannot be empty."
400
Message too long
"Message exceeds maximum allowed length."
400
Question falls outside the referral topic
"I can only answer questions about the Carton Caps referral program..."
404
Conversation doesn't exist
"Conversation not found"


Every error looks like:

{ "detail": "<reason>" }


2.2 How a Message Gets Classified
Before anything else happens, every message is sorted into one of three buckets:

Type of question
How it's recognized
Where the answer comes from
What checks it before it's sent
PRODUCT_QUERY
Words like product, buy, snack, cereal, food, granola, etc.
The Products table
A check that catches obviously broken replies
FAQ_QUERY
Words like referral, invite, bonus, code, friend, reward, etc.
The referral FAQ document
A check that the answer actually matches what the FAQ says
GENERAL
Doesn't match either list
Nothing looked up — the model answers on its own
Same broken-reply check as above



2.3 How a Conversation Flows
POST /v1/chat/conversations

        │

        ▼

  conversation_id comes back

        │

        ▼

POST /v1/chat/conversations/{id}/messages  ◄──┐

        │                                      │

        ▼                                      │

  reply comes back                             │

        │                                      │

        └──────── user sends next message ─────┘

Every message — from the user and from Capper — is saved, along with which of the three categories it fell into. That's what makes future features possible: pulling up chat history, looking at usage patterns, or eventually letting Capper remember earlier parts of the same conversation.


3. System Diagrams
3.1 How the Pieces Fit Together
flowchart TD

    subgraph Client["Mobile App / API Client"]

        APP["Carton Caps App"]

    end

    subgraph API["API Layer"]

        CONV["POST /v1/chat/conversations"]

        MSG["POST /{id}/messages"]

    end

    subgraph Pipeline["Message Pipeline"]

        IG["Input check\nclean up + validate the message"]

        RS["Intent classifier\nfigure out what kind of question it is"]

        AS["Orchestrator\nruns the whole pipeline"]

        CTX["Prompt builder\nassembles what the model sees"]

        LC["Model call\nGPT-4o-mini"]

        OG["Output check\ncatch broken or empty replies"]

    end

    subgraph Retrieval["Where facts come from"]

        SQL["Product lookup\nProducts table"]

        FAQ["FAQ lookup\nfaqs.txt"]

        FG["FAQ check\nkeeps referral answers grounded"]

    end

    subgraph Storage["Storage"]

        REPO["Database layer"]

        DB[("SQLite")]

    end

    APP -->|"create session"| CONV

    APP -->|"send message"| MSG

    MSG --> IG --> RS --> AS

    AS --> SQL

    AS --> FG --> FAQ

    AS --> CTX --> LC --> OG --> REPO --> DB

    CONV --> REPO


3.2 What Happens for One Message, Step by Step
sequenceDiagram

    actor User

    participant API as API

    participant IG as Input check

    participant RS as Intent classifier

    participant RET as Product or FAQ lookup

    participant FG as FAQ check

    participant CTX as Prompt builder

    participant LLM as Model call

    participant OG as Output check

    participant DB as Database

    User->>API: sends a message

    API->>IG: clean up + validate

    IG-->>API: sanitized text

    API->>RS: what kind of question is this?

    RS-->>API: PRODUCT_QUERY | FAQ_QUERY | GENERAL

    alt Referral question

        API->>FG: is this actually about the referral program?

        FG-->>API: yes, or a 400 error if not

        API->>RET: look up the relevant FAQ section

    else Product question

        API->>RET: look up matching products

    else Small talk

        Note over RET: nothing to look up

    end

    RET-->>API: the real facts, if any

    API->>CTX: build the prompt using those facts

    CTX-->>API: finished prompt

    API->>LLM: ask the model to reply

    LLM-->>API: draft reply

    alt Referral question

        API->>FG: does the reply actually match the FAQ?

        FG-->>API: clean reply, or a safe fallback

    else Product or small talk

        API->>OG: does the reply hold up?

        OG-->>API: clean reply, or a safe fallback

    end

    API->>DB: save the user's message

    API->>DB: save Capper's reply and its category

    API-->>User: final reply


3.3 What's Stored
erDiagram

    CONVERSATIONS {

        string id PK "c_xxxxxxxx"

        string user_id

        string entry_point

        datetime created_at

    }

    MESSAGES {

        string id PK "m_xxxxxxxx"

        string conversation_id FK

        string role "user | assistant"

        string content

        string intent

        datetime created_at

    }

    PRODUCTS {

        int id PK

        string name

        string description

        float price

        string created_at

    }

    CONVERSATIONS ||--o{ MESSAGES : "has many"


4. Mobile Integration
4.1 How the App Talks to This Service
The Carton Caps app talks to Capper the same way it would talk to any other backend service — plain HTTP calls, no special SDK needed.

The basic flow:

App Launch / Chat Widget Opened

        │

        ▼

POST /v1/chat/conversations

{ "entry_point": "home_widget" }

        │

        ▼

Store conversation_id in local session state

        │

        ▼

User types message → POST /v1/chat/conversations/{id}/messages

        │

        ▼

Show the reply in the chat UI

If it was a product question, also show product cards using retrieved_data


4.2 Where the Chat Gets Opened From
The entry_point field just tells the API which screen the chat was opened from. Right now it's used loosely, but it opens the door to smarter greetings later.

Entry Point
Where it is in the app
home_widget
The chat bubble on the home screen
product_page
Opened from a product's detail page
referral_page
Opened from the referral/invite screen
onboarding
Opened during new-user onboarding


A later version could use this to skip straight to referral help when someone opens the chat from the referral page, instead of waiting for them to type a question first.


4.3 Turning Data Into Real UI
The retrieved_data field is kept separate from the reply text on purpose — it's the actual data behind what Capper said, meant for the app to turn into real UI rather than something to be parsed out of a sentence.

For a product question:

"retrieved_data": [

  { "id": 1, "name": "Frosted Flakes Cereal", "price": 3.79 },

  { "id": 2, "name": "Granola Cereal Bars", "price": 5.92 }

]

The app can turn this straight into tappable product cards — image, price, an "Add to Cart" button — while the reply text is just the friendly sentence that introduces them.

For a referral question:

"retrieved_data": [

  { "content": "Q: How do I refer a friend?\nA: Share your unique referral link..." }

]

Here it can back a small "this came from our official FAQ" note, which helps build trust that the answer isn't made up.


4.4 Who's Asking
Right now, every conversation is tied to one placeholder user (user_demo_123) — a stand-in for a real login. In the real app, the mobile client would send its normal login token, and the API would read the actual user from that token rather than trusting anything the app claims about who's asking.

Authorization: Bearer <jwt_token>

Once that's wired up, each conversation stays tied to a real person, which is what makes something like "show me my past conversations" possible down the line.


4.5 What the User Actually Sees, Step by Step
flowchart TD

    A(["User opens app"]) --> B["Chat widget visible on home screen"]

    B --> C["User taps widget"]

    C --> D["App calls POST /v1/chat/conversations\nentry_point: home_widget"]

    D --> E["Capper greeting displayed in chat UI"]

    E --> F["User types message"]

    F --> G["App calls POST /{id}/messages"]

    G --> H{intent in response?}

    H -->|"PRODUCT_QUERY"| I["Show reply text\n+ product cards"]

    H -->|"FAQ_QUERY"| J["Show reply text\n+ source note"]

    H -->|"GENERAL"| K["Show reply text only"]

    I --> F

    J --> F

    K --> F


5. LLM Strategy & Reasoning
5.1 Why GPT-4o-mini
Three reasons drove this choice over a bigger model like GPT-4o:

Speed — People notice lag in a chat window. The smaller model replies noticeably faster, which matters most on mobile where waiting feels worse.
Cost — At real scale, with potentially thousands of conversations a day, token costs add up fast. The smaller model runs at a fraction of the cost per reply.
The job doesn't need a bigger brain — Capper's actual work is turning a short list of products or an FAQ answer into a natural sentence. That's well within what a smaller model handles comfortably; it doesn't call for deep reasoning.

The trade-off is that this model is weaker at complex reasoning and holding long context. That's fine here, because the design never asks it to reason — only to phrase things clearly.


5.2 Why the Model Never Has to "Know" Anything
The single most important decision here: the model is never asked to answer from what it learned during training. Every real answer comes from one of two places:

The Products table, for anything about products
The referral FAQ document, for anything about the referral program

Before the model ever replies, the actual facts are handed to it directly. That one habit is what removes hallucination risk for the two question types that matter most — the model isn't guessing, it's paraphrasing something already known to be true.

For small talk (GENERAL), the model does answer on its own — but that's low-risk, since nothing factual is being claimed.


5.3 How the Prompt Is Built
Every prompt sent to the model has three parts:

Who it is — "You are Capper, a helpful assistant for the Carton Caps app."
What kind of question this is — so the model knows whether it's talking about products or referrals.
The actual facts — whatever was looked up for this specific question.

The model is never told "answer anything the user asks" — it's handed one specific, narrow task with the exact data it needs to do it.

Temperature: 0.7 — enough room for the phrasing to feel natural without becoming unpredictable. If this were something more sensitive to get exactly right every time, a lower value (0.3–0.5) would make more sense.

Max reply length: 300 tokens — plenty for a short answer with a product list or FAQ snippet, while keeping replies from running on and keeping costs predictable.


5.4 The Safety Checks
Four checks run at different points, each catching a different kind of problem:

Check
When it runs
What it catches
Input check
Before anything else
Malformed or abusive messages, stopped before they go any further
Referral topic check
Before looking anything up
Questions that aren't actually about the referral program, stopped before reaching the model
Referral answer check
After the model replies
Makes sure the reply actually matches what the FAQ says
General reply check
After the model replies
Catches obviously broken replies — empty, too short, nonsensical


The referral checks matter most. Capper is not allowed to guess about the referral program. If a reply doesn't clearly match what the FAQ actually says, it gets replaced with a safe, honest fallback instead. That's a deliberately cautious choice — a wrong answer about a bonus is the kind of mistake that costs real user trust, so it's worth being conservative here even at the cost of an occasional "I'm not sure" response.


6. Conversation Design Principles
6.1 Who Capper Is
Capper is meant to feel friendly, to the point, and clearly focused on one job — an approachable, mascot-style helper rather than a general-purpose chatbot, since the audience includes families and students.

A few rules shape every reply:

Answer the actual question first, then add context if useful
Never claim to know something outside the product catalog or the FAQ
Keep the language plain — no jargon, no markdown formatting in the reply itself
Keep it short — a sentence or two plus any data, since this is mostly read on a phone


6.2 When Capper Can't Help
If someone asks something totally outside scope — "what's the weather today?" — that falls into the small-talk category, and the model naturally steers the conversation back toward what it can actually help with.

If it's a referral-sounding question that doesn't match anything in the actual FAQ, Capper says so directly with a clear message about what it can help with, rather than trying to sound helpful and guessing. Being upfront about the boundary is better than a confident-sounding wrong answer.


6.3 Remembering the Conversation
Every message is saved along with which conversation it belongs to. Right now, though, each new message is handled on its own — Capper doesn't look back at earlier messages in the same conversation before replying. That's a deliberate simplification for this first version.

The groundwork for changing that is already there, since every message is stored with a link back to its conversation. Teaching Capper to actually read back over the last few turns before replying is a natural next step, not a rebuild.


6.4 Using Where the Chat Was Opened From
The entry_point field is a small but useful signal — someone opening the chat from the referral screen is very likely about to ask a referral question. Later on, this could be used to:

Guess the topic before the first message even arrives
Tailor the greeting to match
Skip the classification step entirely for that first message


7. Privacy Considerations
7.1 What Gets Saved
Every conversation and message is stored. Here's what that includes:

Data
Saved?
Notes
Who's asking
Yes
Currently a placeholder value; in production this would come from a verified login, never something the app just claims
Where the chat was opened from
Yes
Just tells you which screen — no personal information
The actual message text
Yes
Full text of everything the user and Capper say
What kind of question it was
Yes
The category each message was sorted into
When it happened
Yes
Timestamped in UTC


The message text itself is the sensitive part. Someone might mention something personal in passing — "I'm shopping for my daughter's school," for instance — and that should be treated with the same care as any other personal information in a real deployment.


7.2 What to Do Before This Goes to Production
Don't log the raw message text anywhere outside the main database — logs and monitoring tools should only ever see message IDs and categories, not the actual words.
Encrypt the database at rest, or move to a managed database service that handles this by default.
Set a retention limit — conversations shouldn't be kept forever. Something like 90 days is a reasonable starting point.
Be careful what reaches the AI provider — check OpenAI's data policy, and consider stripping obvious personal details out of a message before it's sent to the model at all.
Never trust a client-supplied identity — who's asking should always come from a verified login token, not something the app just states.
Always use HTTPS — the local setup used for building this is fine for development, but real traffic needs to be encrypted end to end.


7.3 What Happens to Data Sent to OpenAI
Messages sent to GPT-4o-mini fall under OpenAI's own data policies. As things stand, OpenAI doesn't use API traffic to train its models — but that's worth double-checking and writing down formally before shipping anything real. Given that Carton Caps' audience skews toward families and schools, it's also worth having a proper data agreement in place with OpenAI given the likelihood that some messages relate to minors, even indirectly.


8. Trade-offs & Alternatives Considered
8.1 Matching Keywords vs. Letting the Model Decide the Topic
What was built: the topic of a message is decided by matching against a list of keywords.

The alternative: ask the model itself to figure out the topic.

Why keyword matching won out:

No extra delay — there's no additional call involved
No extra cost — no extra tokens spent
Always predictable — the same message always lands in the same category
Simple to reason about and to extend

Where it falls short: paraphrasing breaks it. "What can I purchase?" won't trigger the product keywords the way "what snacks do you have" would. Having the model do this classification instead would handle that naturally — this is the most likely first thing to upgrade.


8.2 A Plain Text File vs. a Real Search Index for the FAQ
What was built: the FAQ lives in a plain text file, matched by keyword.

The alternative: put the FAQ into a proper search index that finds answers by meaning rather than exact wording.

Why the plain file won out:

There are only 11 FAQ entries — a search index would be overkill at this size
Nothing extra to set up or maintain
Keyword matching works fine when the content is this small and well organized

Where it falls short: once the FAQ grows past a few dozen entries, or covers more varied topics, keyword matching starts missing things — especially when someone phrases a question in words that don't overlap with the answer (like asking about "gaming the system" when the actual FAQ section is titled "abuse and restrictions"). That's when a real search index earns its keep.


8.3 A Simple Local Database vs. a Production Database
What was built: everything runs on a single SQLite file.

Why: no setup required, easy to move around, plenty for a small service running on one machine during development.

What changes in production: moving to something like PostgreSQL is essentially a one-line configuration change, not a rewrite, thanks to the way the database layer is built.


8.4 Answering Each Message on Its Own vs. Remembering the Conversation
What was built: each message is handled independently — Capper doesn't look back at what was said earlier in the same conversation.

The cost of that: if someone asks "what about the second one?" right after seeing a product list, Capper has no way to know what "the second one" refers to.

Why that was an acceptable trade-off for now: feeding the whole conversation history into every request adds cost, adds delay, and requires care to avoid overflowing what the model can handle at once. Since most questions Capper gets are self-contained, skipping this for now was a reasonable simplification — and because every message is already saved, adding this later is a contained change, not something that requires rebuilding the system.


9. Evolution Roadmap
Ordered roughly by how much value each change adds versus how much work it takes.
Near-term (v2)
Change
Why it matters
Let Capper see the last few messages in the conversation
Makes follow-up questions like "what about the second one?" actually answerable
Let the model decide the topic instead of keyword matching
Handles paraphrased questions the keyword list currently misses
Add a way to fetch past messages in a conversation
Lets the app restore chat history when someone reopens it
Real user logins
Replace the placeholder user ID with an actual verified identity

Medium-term (v3)
Change
Why it matters
Move to a production database
Handles real traffic, concurrent use, and encryption properly
Search the FAQ by meaning, not just keywords
Keeps working as the FAQ grows and covers more ground
Use where the chat was opened from to guess the topic upfront
Less friction for someone who's clearly there for one specific thing
Stream replies as they're generated
Feels faster on mobile — text appears as it's written instead of all at once

Longer-term
Change
Why it matters
Remember things about a specific user over time
"You asked about granola bars last week — we just got a new one"
A real recommendation engine
Move beyond keyword search toward genuinely personalized suggestions
Let users react to replies (thumbs up/down)
Gives a real signal for improving reply quality over time
Test different prompt versions against each other
Systematically improve tone, accuracy, and how often people act on Capper's suggestions
Hand off to a real person when Capper can't help
Gives users a way out when the agent genuinely can't answer


