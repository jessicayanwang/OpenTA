# Multi-Chat System with Per-Problem Hint Tracking

## Overview

The Assignment Helper now supports **separate chat sessions for each problem** with **independent hint tracking** (15 hints per problem). This allows students to work on multiple problems without losing their progress.

## Key Features

### 1. **Per-Problem Chat Sessions** ✅
- Each problem (Hello, Mario, Credit) has its own independent chat
- Switching between problems preserves all chat history
- Up to 3 active chat sessions (one per problem)

### 2. **Session Persistence** ✅
- Chat sessions stored in React state (`chatSessions`)
- Persists across problem switches (until page refresh)
- No database required - in-memory storage

### 3. **15 Hints Per Problem** ✅
- Each problem has independent hint counter
- Hint count resets when switching problems
- Visual indicator shows X/15 hints used

### 4. **Improved Pseudo-Code** ✅
- **No code skeletons** - only natural language descriptions
- Progressive detail levels:
  - **Hints 1-5**: High-level Socratic questions
  - **Hints 6-10**: Natural language algorithm descriptions
  - **Hints 11-15**: Detailed step-by-step natural language

## Implementation Details

### Frontend Changes

#### Multi-Chat State Management
```typescript
// Store separate chat sessions for each problem
const [chatSessions, setChatSessions] = useState<{ [problemId: string]: Message[] }>({})
const [selectedProblem, setSelectedProblem] = useState('')

// Get current messages for selected problem
const messages = selectedProblem && chatSessions[selectedProblem] 
  ? chatSessions[selectedProblem] 
  : []
```

#### Auto-Initialize Chat Sessions
```typescript
useEffect(() => {
  if (selectedProblem && !chatSessions[selectedProblem]) {
    const problemName = PROBLEMS.find(p => p.id === selectedProblem)?.name || 'this problem'
    setChatSessions(prev => ({
      ...prev,
      [selectedProblem]: [getWelcomeMessage(problemName)]
    }))
  }
}, [selectedProblem])
```

#### Update Messages Per Problem
```typescript
// Add message to current problem's chat session
setChatSessions(prev => ({
  ...prev,
  [selectedProblem]: [...(prev[selectedProblem] || []), userMessage]
}))
```

#### Visual Indicators
- **Chat indicator**: Problems with active chats show 💬 emoji
- **Hint counter**: Shows "X/15 hints" for current problem
- **Placeholder**: Shows message when no problem selected

### Backend Changes

#### Updated Hint Limits
```python
# models.py
class GuardrailSettings(BaseModel):
    max_hints: int = 15  # 15 hints per problem
```

#### Updated Scaffolding Levels
```python
# assignment_helper_agent.py
# Hints 1-5: High level (Socratic questions, informative)
# Hints 6-10: Medium level (Structured guidance, natural language)
# Hints 11-15: Low level (Detailed natural language pseudo-code)
if hint_count < 5:
    scaffolding_level = "high"
elif hint_count < 10:
    scaffolding_level = "medium"
else:
    scaffolding_level = "low"
```

#### Natural Language Pseudo-Code
```python
# Medium level example
"""
First, get the height from the user and make sure it's between 1 and 8.
Then, for each row from 1 to height:
  - Print (height minus current row number) spaces
  - Print (current row number) hash symbols
  - Move to the next line
"""

# Low level example
"""
1. Include the standard input/output library
2. Create a main function
3. Declare an integer variable to store the height
4. Use a do-while loop to:
   - Prompt the user for a height
   - Keep asking until they give a number between 1 and 8
5. Use a for loop that counts from 1 to height (call this 'i')
6. Inside that loop, for each row:
   - Use another for loop to print (height - i) space characters
   - Use another for loop to print i hash characters
   - Print a newline character
7. Return 0 to indicate success
"""
```

**NO CODE SKELETONS** - Students must translate natural language to code themselves.

## User Experience

### Workflow Example

**Step 1: Select Problem 1 (Hello)**
- New chat session created
- Welcome message: "Welcome to the Assignment Helper for Problem 1: Hello!"
- Shows: "0/15 hints"

**Step 2: Ask Questions**
- Student: "How do I start?"
- System: Hint #1/15 (High level Socratic)
- Shows: "1/15 hints"

**Step 3: Switch to Problem 2 (Mario)**
- Problem 1 chat preserved
- New chat session for Problem 2
- Shows: "0/15 hints" (independent counter)
- Dropdown shows: "Problem 1: Hello 💬" (has active chat)

**Step 4: Switch Back to Problem 1**
- All previous messages still there
- Continues from where left off
- Shows: "1/15 hints"

**Step 5: Continue Until 15 Hints**
- Hints 1-5: High-level guidance
- Hints 6-10: Natural language algorithm descriptions
- Hints 11-15: Detailed step-by-step natural language
- At 15: "You've used all 15 hints. Contact instructor for additional help."

## Visual Indicators

### Problem Selector
```
Problem: [Problem 1: Hello 💬 ▼]  2/15 hints
         [Problem 2: Mario   ▼]
         [Problem 3: Credit  ▼]
```

- 💬 = Has active chat
- X/15 = Hints used for current problem

### No Problem Selected
```
┌─────────────────────────────────┐
│         📄                      │
│   Select a Problem to Start     │
│                                 │
│ Choose a problem from the       │
│ dropdown above to begin getting │
│ help. Each problem has its own  │
│ chat with up to 15 hints.       │
│                                 │
│ Active chats: Problem 1: Hello  │
└─────────────────────────────────┘
```

## Hint Progression (15 Hints)

### Hints 1-5: High Level
**Goal**: Understand the problem
**Approach**: Informative Socratic questions
**Example**:
```
"Let's think about the Mario pyramid problem. Looking at the example:
   #
  ##
 ###
####

What pattern do you notice? Each row has spaces and hashes.
Can you describe the relationship between the row number and 
the number of spaces vs hashes?"
```

### Hints 6-10: Medium Level
**Goal**: Understand the algorithm
**Approach**: Natural language descriptions
**Example**:
```
"Here's the approach in plain English:

First, get the height from the user and make sure it's between 1 and 8.
If they give an invalid number, keep asking until they give a valid one.

Then, for each row from 1 to height:
  - Print (height minus current row number) spaces
  - Print (current row number) hash symbols
  - Move to the next line

Can you think about how to implement this?"
```

### Hints 11-15: Low Level
**Goal**: Detailed implementation guidance
**Approach**: Step-by-step natural language
**Example**:
```
"Here's the detailed step-by-step approach:

1. Include the standard input/output library (stdio.h)
2. Create a main function that returns an integer
3. Declare an integer variable called 'height'
4. Use a do-while loop to get valid input:
   - Inside the loop, prompt the user for a height
   - The loop should continue while height is less than 1 OR greater than 8
5. Create a for loop that counts from 1 to height (use variable 'i')
6. Inside that loop, for each row:
   - Create another for loop to print (height - i) space characters
   - Create another for loop to print i hash characters
   - Print a newline character to move to the next row
7. Return 0 to indicate the program finished successfully

Now try translating this into actual C code!"
```

**Still NO actual code** - student must write it themselves.

## Benefits

### For Students
1. **Work on multiple problems**: Can switch between problems without losing progress
2. **More hints**: 15 per problem instead of 3-10 total
3. **Better guidance**: Natural language descriptions instead of confusing code skeletons
4. **Clear progress**: See exactly how many hints used per problem
5. **Preserved context**: Chat history maintained when switching problems

### For Instructors
1. **Academic integrity**: Still no direct code solutions
2. **Better learning**: Students must translate natural language to code
3. **Flexible**: 15 hints allows genuine progressive learning
4. **Trackable**: Can see hint usage per problem
5. **Scalable**: Easy to add more problems

## Testing

### Test Case 1: Multi-Chat Persistence
```
1. Select Problem 1, ask "How do I start?"
2. Select Problem 2, ask "What algorithm should I use?"
3. Select Problem 1 again
Expected: Previous conversation with Problem 1 still visible
```

### Test Case 2: Independent Hint Counters
```
1. Select Problem 1, ask 3 questions (3/15 hints)
2. Select Problem 2, ask 1 question (1/15 hints)
3. Check counters
Expected: Problem 1 shows 3/15, Problem 2 shows 1/15
```

### Test Case 3: Natural Language Pseudo-Code
```
1. Select Problem 2 (Mario)
2. Ask 11 questions to reach low-level hints
Expected: Detailed natural language description, NO code skeletons
```

### Test Case 4: Visual Indicators
```
1. Start with no problems selected
Expected: Placeholder message shown
2. Select Problem 1, ask a question
Expected: Problem 1 shows 💬 in dropdown, shows "1/15 hints"
```

### Test Case 5: 15 Hint Limit
```
1. Ask 15 questions for Problem 1
Expected: After 15th, message says "Contact instructor for additional help"
2. Switch to Problem 2
Expected: Can still ask questions (independent counter)
```

## Files Modified

### Frontend
- `frontend/app/assignment-help/page.tsx`:
  - Changed from single `messages` state to `chatSessions` object
  - Added `useEffect` to initialize chat sessions
  - Updated all `setMessages` to `setChatSessions`
  - Added placeholder for no problem selected
  - Added visual indicators (💬, hint counter)

### Backend
- `backend/models.py`:
  - Changed `max_hints` from 20 to 15
- `backend/agents/assignment_helper_agent.py`:
  - Updated scaffolding levels: 1-5, 6-10, 11-15
  - Changed pseudo-code from code skeletons to natural language
  - Updated hint number display to show "/15"

## Migration Notes

### From Previous Version
- Old: Single chat for all problems, 10 hints total
- New: Separate chats per problem, 15 hints each

### Data Persistence
- Current: In-memory (lost on refresh)
- Future: Could add localStorage or database

### Hint Count Storage
- Backend tracks per `assignment_id` (problem_number)
- Frontend shows per `problemId` in chatSessions
- Counts are independent and correct

## Future Enhancements

1. **LocalStorage Persistence**: Save chatSessions to localStorage
2. **Export Chat**: Allow students to export chat history
3. **Hint Quality Feedback**: Let students rate hint helpfulness
4. **Smart Hint Skipping**: Jump levels based on student understanding
5. **Concept Mastery Tracking**: Remember what student already knows
6. **Multi-Assignment Support**: Extend to other assignments beyond Assignment 1

## Summary

The multi-chat system provides:
- ✅ **Separate chats** for each of 3 problems
- ✅ **15 hints per problem** with independent tracking
- ✅ **Session persistence** across problem switches
- ✅ **Natural language pseudo-code** instead of code skeletons
- ✅ **Visual indicators** for active chats and hint usage
- ✅ **Better UX** with clear progress tracking
- ✅ **Academic integrity** maintained (no direct code)

Students can now work on multiple problems effectively while getting genuinely helpful guidance that requires them to do the actual coding work! 🎉
