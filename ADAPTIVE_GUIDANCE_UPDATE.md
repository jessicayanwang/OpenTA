# Adaptive Guidance System - Major Update

## Overview

Removed rigid scaffolding levels and implemented truly adaptive, conceptual guidance that responds to student needs while maintaining strong academic integrity.

## Key Changes

### 1. ✅ **Removed Strict Scaffolding Levels**

**Before:**
- Hints 1-5: Forced high-level Socratic questions
- Hints 6-10: Forced medium-level guidance
- Hints 11-15: Forced low-level pseudo-code

**Problem:** Student asking for debugging help on hint #2 would get Socratic questions instead of debugging guidance.

**After:**
- **Adaptive responses** based on actual student needs
- LLM decides appropriate level based on:
  - Question type (debugging, implementation, conceptual)
  - Student knowledge level (zero-knowledge, stuck, exploring)
  - Actual question content
  - Chat history context

**Example:**
```
Hint #2: "My loop isn't working, it prints too many hashes"
Before: "What do you think a loop does?" (forced Socratic)
After: "Let's debug this. What did you expect vs what happened? 
       Can you trace through one iteration?" (appropriate debugging help)
```

### 2. ✅ **Truly Conceptual Pseudo-Code**

**Strict Rules - NO Code-Like Syntax:**

❌ **FORBIDDEN:**
- `for (int i = 0; i < height; i++)`
- `#include <stdio.h>`
- `int main(void) { }`
- `printf("...")`
- Any compilable code structure
- Semicolons, braces, angle brackets in code context
- Function signatures
- Variable declarations with types

✅ **ALLOWED - Conceptual Descriptions:**
- "Repeat a process for each row"
- "Check if the number is valid"
- "For each item, do something slightly different"
- "Keep asking until you get a valid answer"
- "The pattern: first row has 1 symbol, second has 2, third has 3..."

**Example Transformation:**

**Old (Too Code-Like):**
```
1. Include the standard input/output library
2. Create a main function
3. Declare an integer variable to store the height
4. Use a do-while loop to:
   - Prompt the user for a height
   - Keep asking until they give a number between 1 and 8
5. Use a for loop that counts from 1 to height (call this 'i')
```

**New (Truly Conceptual):**
```
Here's the thinking process:
- First, get a number from the user and make sure it's valid
- Think about each row as having two parts: empty space and symbols
- The empty space gets smaller as you go down (row 1: most spaces, last row: no spaces)
- The symbols get more numerous as you go down (row 1: one symbol, row 2: two symbols)
- After each row, move to a new line

Can you think about how the row number relates to how many spaces and symbols you need?
```

### 3. ✅ **Chat History Context**

**Implementation:**
- Frontend sends entire chat history for current problem
- Backend includes last 10 messages (5 exchanges) in LLM context
- LLM can reference previous conversation
- Avoids repetitive explanations
- Builds on previous understanding

**Example:**
```
Message 1:
Student: "How do I start the Mario problem?"
Assistant: "Think about the pattern. Each row has spaces and hashes..."

Message 2:
Student: "I still don't understand the spaces"
Assistant: "Remember we talked about the pattern? Let's focus on spaces specifically.
           For a height of 4:
           Row 1: 3 spaces, 1 hash
           Row 2: 2 spaces, 2 hashes
           Can you see the relationship?" [References previous conversation]
```

**Technical Details:**
```python
# Backend formats history
history_context = "\n\n**Previous Conversation:**\n"
for msg in recent_history[-10:]:
    if msg['role'] == 'user':
        history_context += f"Student: {msg['content']}\n"
    elif msg['role'] == 'assistant':
        history_context += f"Assistant: {msg['response']['guidance'][:200]}...\n"

# Adds to LLM context
guidance = await openai_tool.execute({
    'question': question,
    'context': context_text + history_context,  # Chat history included
    'system_prompt': system_prompt
})
```

## Updated System Prompt

### Core Principles

```
**Core Principle**: Be informative and helpful while guiding students to think. 
Adapt your response to what the student actually needs, not a rigid hint number.

**Response Style**:
- If they're debugging: Help them think through the problem, don't fix their code
- If they're stuck: Provide conceptual guidance to get them unstuck
- If they have specific questions: Answer directly but guide them to understand
- If they're exploring: Use Socratic questions that are informative, not empty
```

### Pseudo-Code Rules

```
**When Providing Algorithmic Guidance** (if needed):
Use PURELY CONCEPTUAL, NATURAL LANGUAGE descriptions. NO code-like syntax.

✅ GOOD - Conceptual thinking:
"Think about repeating a process for each row. For the first row, you need one hash. 
For the second row, two hashes. Can you see the pattern?"

"You'll want to repeat an action multiple times. Each time through, you do something 
slightly different based on which repetition you're on."

❌ BAD - Too code-like:
"for loop syntax with variables"
"include statements with angle brackets"
"main function with braces"
"printf with parentheses"
"Use a for loop"
"Declare an integer variable"

**Pseudo-Code Rules** (when absolutely necessary):
- NO actual code syntax
- NO include statements, main functions, braces, semicolons, or code parentheses
- NO compilable structures
- NO function signatures
- Focus on WHAT to do, not HOW to write it
- Use phrases like: "repeat this step", "check if", "for each item", "keep doing until"
```

## Files Modified

### Backend
1. **`agents/assignment_helper_agent.py`**:
   - Removed rigid scaffolding levels (lines 207-216)
   - Replaced with adaptive scaffolding (line 209)
   - Rewrote scaffolding instructions (lines 373-422)
   - Added chat_history parameter (line 178)
   - Format and include chat history in LLM context (lines 225-240)
   - Pass chat_history through call chain (line 106)

### Frontend
2. **`app/assignment-help/page.tsx`**:
   - Send chat_history in API request (line 357)

## Benefits

### For Students
1. **More Relevant Help**: Get debugging help when debugging, not Socratic questions
2. **Less Frustration**: System adapts to actual needs
3. **Better Learning**: Conceptual understanding, not code copying
4. **Context Awareness**: LLM remembers previous conversation
5. **Natural Progression**: Help level adjusts to understanding, not hint count

### For Instructors
1. **Stronger Integrity**: NO code-like syntax at all
2. **Better Pedagogy**: Teaches algorithmic thinking
3. **Flexible System**: Adapts to different student needs
4. **Trackable**: Still logs all interactions
5. **Maintainable**: Simpler system, no rigid rules

## Testing

### Test Case 1: Adaptive Response
```
Hint #2: "My code has a bug, it prints too many hashes"
Expected: Debugging guidance, not Socratic questions
Should ask: "What did you expect vs what happened?"
Should NOT: "What do you think a loop does?"
```

### Test Case 2: Conceptual Pseudo-Code
```
Hint #12: "I really need detailed help"
Expected: Conceptual description, NO code
Should say: "Think about repeating for each row..."
Should NOT: "for (int i = 0; i < height; i++)"
```

### Test Case 3: Chat History Context
```
Hint #1: "How do I start Mario?"
Response: "Think about the pattern..."

Hint #2: "I still don't get it"
Expected: References previous conversation
Should say: "Remember we talked about the pattern? Let's break it down..."
Should NOT: Repeat the same explanation
```

### Test Case 4: Zero-Knowledge Mode
```
Hint #1: "I have no idea how to start"
Expected: Direct foundational explanation
Should: Build mental model from scratch
Should NOT: Ask empty Socratic questions
```

## Comparison: Before vs After

### Scenario: Student Debugging on Hint #3

**Before (Rigid Scaffolding):**
```
Student: "My loop prints 5 hashes instead of 4"
System: "What do you think causes this? Can you think about what a loop does?"
[Forced high-level Socratic because hint #3]
```

**After (Adaptive):**
```
Student: "My loop prints 5 hashes instead of 4"
System: "Let's debug this. You expected 4 but got 5 - that's an off-by-one error.
        Think about:
        - Where does your loop start counting?
        - Where does it stop?
        - Are you using < or <= in your condition?
        Can you check these in your code?"
[Appropriate debugging help based on question type]
```

### Scenario: Student Needs Detailed Help on Hint #14

**Before (Code-Like Pseudo-Code):**
```
System: "Here's the structure:
        1. Include the standard input/output library
        2. Create a main function
        3. Declare an integer variable to store the height
        4. Use a do-while loop to:
           - Prompt the user for a height
           - Keep asking until they give a number between 1 and 8
        5. Use a for loop that counts from 1 to height (call this 'i')"
[Too close to actual code]
```

**After (Conceptual Description):**
```
System: "Here's the thinking process:
        - First, get a number from the user and make sure it's valid
        - Keep asking until they give you something between 1 and 8
        - Then, think about each row as having two parts: empty space and symbols
        - The empty space gets smaller as you go down
        - The symbols get more numerous as you go down
        - After each row, move to a new line
        
        Can you think about how the row number relates to how many spaces 
        and symbols you need?"
[Conceptual, requires translation to code]
```

## Logging

Watch for these log messages:

```
📊 Hint #3/15, Knowledge: stuck
🤖 Calling OpenAI API for question type: debugging, with 4 history messages
✅ LLM response received (543 chars)
```

## Summary

The system now provides:
- ✅ **Adaptive responses** based on actual student needs
- ✅ **Truly conceptual** pseudo-code with NO code syntax
- ✅ **Chat history context** for coherent conversations
- ✅ **Stronger academic integrity** - impossible to copy code
- ✅ **Better learning outcomes** - teaches algorithmic thinking
- ✅ **More helpful** - responds to what students actually need

Students get genuinely helpful, context-aware guidance that teaches them to THINK algorithmically, not copy code! 🎉
