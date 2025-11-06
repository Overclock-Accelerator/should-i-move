# 03 - Agno Cooperation Strategy

## Overview

This example demonstrates a **cooperation-based** multi-agent system where specialized agents **debate and reach consensus** collaboratively. Unlike the coordination approach where a leader delegates tasks sequentially, this cooperation mode has all agents work on the same task simultaneously and discuss their findings.

## Key Differences from Coordination (01-agno-coordination.py)

| Feature | Coordination Mode (01) | Cooperation Mode (03) |
|---------|----------------------|----------------------|
| **Task Distribution** | Sequential delegation to individual agents | Simultaneous delegation to all agents |
| **Team Parameter** | `delegate_task_to_all_members=False` (default) | `delegate_task_to_all_members=True` |
| **Agent Interaction** | Agents work independently | Agents debate and discuss together |
| **Consensus** | Leader synthesizes separate reports | Team reaches consensus through discussion |
| **User Priority** | Considered in final synthesis | Central to the debate process |

## Cooperation Mode Architecture

```
┌─────────────────────────────────────────────────────┐
│         Team Leader (Discussion Moderator)          │
│  - Facilitates debate between all agents            │
│  - Ensures user's priority is central focus         │
│  - Guides team to consensus                         │
└─────────────────────────────────────────────────────┘
                          │
                          │ Delegates to ALL simultaneously
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Cost Analyst │  │  Sentiment   │  │  Migration   │
│              │  │   Analyst    │  │  Researcher  │
└──────────────┘  └──────────────┘  └──────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                          ▼
              Collaborative Discussion
                     (Debate)
                          │
                          ▼
                  Consensus Reached
```

## Key Features

### 1. **User Priority-Driven Debate**

The most important enhancement is that the user's **most important factor** (e.g., "affordability", "culture", "job opportunities") becomes the central consideration in the debate.

Each agent is instructed to:
- Consider the user's priority in their analysis
- **Defer to the user's priority** even if their data suggests a different conclusion
- Frame their recommendations around what the user values most

### 2. **Collaborative Discussion**

All agents:
- Present their findings simultaneously
- Listen to each other's perspectives
- Discuss areas of agreement and disagreement
- Work toward consensus

### 3. **Enhanced Pydantic Models**

Each agent's output schema includes a new field:
```python
perspective_on_user_priority: str = Field(
    ..., 
    description="How this analysis relates to the user's most important factor"
)
```

### 4. **Debate Summary**

The final recommendation includes a comprehensive `DebateSummary`:
```python
class DebateSummary(BaseModel):
    debate_rounds: int
    key_points_of_agreement: List[str]
    key_points_of_disagreement: List[str]
    how_user_priority_influenced_debate: str
    consensus_reached: str
    debate_highlights: List[str]
```

### 5. **Enhanced Final Report**

The generated markdown report includes:
- User's most important factor prominently displayed
- Full debate summary section
- Explanation of how the user's priority influenced the consensus
- Clear alignment between recommendation and user values

## Agent Instructions - Priority Deference

Each agent has updated instructions emphasizing priority deference:

```python
"CRITICAL: Always consider the user's MOST IMPORTANT FACTOR in your analysis"
"If the user prioritizes something other than [your domain], acknowledge this"
"Be willing to adjust your recommendation based on what the user values most"
"Even if [your data] suggests one decision, defer to user priorities if they conflict"
```

### Example Scenario:

**Cost Analyst** finds that moving is 30% more expensive, but the user's priority is **"career growth"**:

```
Cost Analyst in debate:
"While the cost of living is significantly higher (+30%), the user has stated 
that career growth is their primary concern. If the destination city offers 
superior job opportunities in their field, the financial premium may be 
justified given their stated priority."
```

## Usage

```bash
# Run the cooperation-based analysis
python 03-agno-cooperation.py

# With debug mode
python 03-agno-cooperation.py --debug
```

## Information Gathering

The system asks for:
1. Current city (specific)
2. Desired city (specific)
3. Financial situation (income & expenses)
4. City preferences
5. Likes/dislikes about current city
6. **Most important factor** (NEW!)

The most important factor question helps the system understand what to prioritize:
- "affordability" → Cost analysis weighted heavily
- "career growth" → Job market considerations prioritized
- "culture/lifestyle" → City vibe and cultural fit emphasized
- "family proximity" → Personal connections valued most

## Output

### Console Output
- Real-time debate between agents (with `show_members_responses=True`)
- Discussion moderation by team leader
- Consensus building process visible

### Report File
Saved as: `{current_city}_to_{desired_city}_cooperation_analysis.md`

Includes:
- Executive summary
- User's priority highlighted
- **Debate summary** (agreement/disagreement points)
- Individual agent analyses (with priority perspective)
- Final consensus recommendation
- Alignment with user's priority
- Next steps

## When to Use Cooperation Mode

**Use Cooperation Mode when:**
- The decision requires balancing multiple perspectives
- The user has a clear priority that should influence all analyses
- You want transparency in how the decision was reached
- Different expert opinions might conflict and need resolution

**Use Coordination Mode when:**
- Tasks are independent and don't require discussion
- Sequential analysis is more efficient
- The synthesis happens at the end without debate

## Technical Implementation

Key code change:

```python
move_decision_team = Team(
    name="City Move Decision Team",
    model=OpenAIChat("gpt-4o-mini"),
    members=[cost_analyst, sentiment_analyst, migration_researcher],
    delegate_task_to_all_members=True,  # ← COOPERATION MODE
    show_members_responses=True,         # ← Show the debate
    # ... other config
)
```

## Dependencies

Same as `01-agno-coordination.py`:
- `agno` (with OpenAI integration)
- `python-dotenv`
- `pydantic`
- Custom `brave_tools` for Reddit search
- City database from `nerdwallet-tools`

## Example Debate Flow

```
1. Team Leader: "Analyze this move with priority: 'career growth'"
   
2. Cost Analyst: "30% more expensive, but if jobs align with priority..."
   Sentiment Analyst: "Great culture scene, but priority is career..."
   Migration Researcher: "Redditors mention great job market for tech..."

3. Team Leader: "I see consensus forming around career opportunities..."

4. Final Consensus: "Recommend moving - career growth potential outweighs 
   cost increase, aligning with user's stated priority."
```

## Future Enhancements

Potential improvements:
- Add more debate rounds for complex decisions
- Include voting mechanism for stronger disagreements
- Allow user to interject during debate
- Add confidence levels per agent
- Track how often agents defer to user priority

---

**Related Files:**
- `01-agno-coordination.py` - Sequential coordination approach
- `03-agno-cooperation.py` - This cooperation approach
- `brave_tools/` - Reddit search integration
- `nerdwallet-tools/` - City database tools



