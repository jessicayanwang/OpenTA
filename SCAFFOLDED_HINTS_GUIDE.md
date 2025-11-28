# Scaffolded Hints System - Complete Guide

## Overview

The Assignment Helper now uses a **progressive scaffolding system** with **10 hints** instead of 3, providing increasingly detailed help while maintaining academic integrity.

## Key Improvements

### 1. **Increased Hint Limit: 3 → 10**
- Students now get 10 hints per assignment
- Allows for genuine progressive learning
- Reduces frustration for students who are truly stuck

### 2. **Three-Level Scaffolding**

#### **Level 1: High-Level Guidance (Hints 1-3)**
- **Approach**: Socratic questions with informative content
- **Goal**: Help students think about the big picture
- **Example**:
  ```
  "A C program has two main parts: #include statements and a main() function. 
  Which part do you think is the entry point where execution begins?"
  ```
- **NOT**: "What do you think you need?" (too vague)

#### **Level 2: Medium-Level Guidance (Hints 4-7)**
- **Approach**: Structured guidance with examples, but hide implementation details
- **Goal**: Provide framework without giving away the solution
- **Example**:
  ```
  "You'll need a loop that runs from 1 to height. Inside that loop, you need to:
  1. Print some number of spaces
  2. Print some number of hashes
  
  Can you think about the relationship between the row number and how many 
  spaces vs hashes you need?"
  ```
- **Includes**: Pseudo-code structure with TODOs

#### **Level 3: Low-Level Guidance (Hints 8-10)**
- **Approach**: Detailed pseudo-code skeleton with specific guidance
- **Goal**: Maximum help without writing actual code
- **Example**:
  ```c
  #include <...>  // TODO: what library do you need for printf?
  
  int main(void)
  {
      // TODO: declare a variable to store the height
      
      // TODO: prompt the user and get input
      //       (look up get_int from CS50 library)
      
      // TODO: validate that height is between 1 and 8
      //       if not, re-prompt
      
      // TODO: use a loop from 1 to height
      //       for each row i:
      //         - print (height - i) spaces
      //         - print i hashes
      //         - print a newline
      
      return 0;
  }
  ```

### 3. **Zero-Knowledge Mode**

When students say things like:
- "I have no idea"
- "I don't know where to start"
- "I'm completely lost"
- "I don't understand anything"

The system activates **Zero-Knowledge Mode**:

**Instead of Socratic questions:**
```
❌ "What do you think a C program needs?"
```

**It provides foundational building:**
```
✅ "No problem! Let's start from the basics. A C program has two essential parts:

1. **Include statements** - These tell the compiler what tools you want to use
   Example: #include <stdio.h> gives you printf()

2. **main() function** - This is where your program starts running
   Every C program must have this

Would you like me to explain includes first, or the main function?"
```

### 4. **Problem-Specific Context**

The system now recognizes specific problems and provides targeted help:

**For "Hello" problem:**
- Focus: Basic C structure, printf, main function
- Key concepts: Includes, function syntax, string literals

**For "Mario" problem:**
- Focus: Nested loops, pattern printing, input validation
- Key concepts: Loop control, relationships between variables, formatting

**For "Credit" problem:**
- Focus: Luhn's algorithm, modulo operations, card validation
- Key concepts: Mathematical operations, conditionals, algorithm implementation

### 5. **Adaptive Resources and Next Steps**

Resources and next steps now adapt to the scaffolding level:

**High Level (Hints 1-3):**
- "Think about what you expected vs what happened"
- "Consider what steps are needed"

**Medium Level (Hints 4-7):**
- "Add print statements before the error line"
- "Write pseudocode for your approach"
- "Identify which C constructs you need (loops, conditionals)"

**Low Level (Hints 8-10):**
- "Set up the basic program structure (includes, main function)"
- "Add variable declarations for what you need to track"
- "Implement input validation first, then core logic"

## How It Works

### Hint Progression Example: Mario Problem

**Student asks: "How do I start the Mario problem?"**

**Hint #1 (High Level):**
```
Let's think about what the Mario problem is asking:

1. Get a height from the user (between 1-8)
2. Print a right-aligned pyramid of that height

Before writing any code, can you describe in your own words what pattern 
you see in the pyramid? For example, for height 4:
   #
  ##
 ###
####

What do you notice about spaces and hashes in each row?
```

**Hint #4 (Medium Level):**
```
Good! Now let's think about the structure you'll need:

1. **Input section**: Get and validate the height
   - Use get_int() to prompt the user
   - Check if it's between 1 and 8
   - If not, ask again

2. **Output section**: Print the pyramid
   - You'll need a loop from 1 to height
   - For each row, print:
     * Some spaces (how many?)
     * Some hashes (how many?)
   
Can you work out the relationship? If height is 4 and you're on row 2,
how many spaces and how many hashes?
```

**Hint #8 (Low Level):**
```
Here's the structure you need to fill in:

#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int height;
    
    // TODO: Use a do-while loop to get valid input
    do
    {
        height = get_int("Height: ");
    }
    while (/* TODO: what condition makes height invalid? */);
    
    // TODO: Loop through each row (1 to height)
    for (int i = 1; i <= height; i++)
    {
        // TODO: Print (height - i) spaces
        for (/* TODO: loop condition */)
        {
            printf(" ");
        }
        
        // TODO: Print i hashes
        for (/* TODO: loop condition */)
        {
            printf("#");
        }
        
        // TODO: Print newline
        printf("\n");
    }
}

Now fill in the TODOs! Think about:
- What makes height invalid? (less than 1 or greater than 8)
- How many spaces for row i? (height - i)
- How many hashes for row i? (i)
```

## Backend Implementation

### Key Methods

#### `_detect_knowledge_level(question_lower)`
Detects if student has zero knowledge or is just stuck:
- Returns: `"zero_knowledge"`, `"stuck"`, or `"exploring"`

#### `_create_scaffolded_prompt(question_type, scaffolding_level, knowledge_level, problem_number, hint_number)`
Creates adaptive system prompt for the LLM based on:
- Question type (debugging, implementation, conceptual, etc.)
- Scaffolding level (high, medium, low)
- Knowledge level (zero_knowledge, stuck, exploring)
- Specific problem being worked on
- Current hint number

#### `_suggest_resources(question_type, scaffolding_level)`
Provides resources that adapt to scaffolding level:
- High: General resources
- Low: Specific function documentation, step-by-step examples

#### `_suggest_next_steps(question_type, scaffolding_level)`
Provides next steps that increase in specificity:
- High: "Think about what steps are needed"
- Medium: "Write pseudocode for your approach"
- Low: "Set up the basic program structure (includes, main function)"

## Configuration

### Max Hints Setting
In `models.py`:
```python
class GuardrailSettings(BaseModel):
    max_hints: int = 10  # Progressive scaffolding: 10 hints with increasing detail
```

Professors can adjust this in the professor console if needed.

## Testing the System

### Test Scenario 1: Zero Knowledge Student
```
Student: "I have no idea how to do the Hello problem"

Expected: Zero-knowledge mode activates, provides foundational explanation
without Socratic questions
```

### Test Scenario 2: Progressive Hints
```
Hint 1: High-level Socratic questions
Hint 2: More specific questions
Hint 3: Still high-level but more directed

Hint 4: Structured guidance appears
Hint 5: Pseudo-code structure introduced
Hint 6: More detailed structure
Hint 7: Specific components identified

Hint 8: Detailed pseudo-code skeleton
Hint 9: Very specific guidance with TODOs
Hint 10: Maximum help without actual code
```

### Test Scenario 3: Direct Answer Request
```
Student: "Can you just give me the code for Mario?"

Expected: Polite refusal with redirection to learning, regardless of hint count
```

## Guardrails Maintained

Despite providing more help, the system NEVER:
1. ❌ Provides complete code solutions
2. ❌ Writes actual implementation code
3. ❌ Gives direct answers to graded problems
4. ❌ Does the work for the student

It DOES:
1. ✅ Provide pseudo-code structure with TODOs
2. ✅ Explain concepts and approaches
3. ✅ Show program skeleton without implementation
4. ✅ Guide students to discover solutions themselves

## Benefits

### For Students
- **Less frustration**: 10 hints instead of 3
- **Progressive learning**: Help increases gradually
- **Better for beginners**: Zero-knowledge mode helps those truly lost
- **More helpful**: Pseudo-code and structure without giving away answers

### For Instructors
- **Maintains integrity**: Still no direct answers or code
- **Reduces office hours load**: Students can get unstuck independently
- **Better learning outcomes**: Scaffolding is proven pedagogical technique
- **Configurable**: Can adjust max hints per course needs

## Logging

Watch for these log messages:

```
📊 Hint #1, Scaffolding level: high, Knowledge: exploring
📊 Hint #4, Scaffolding level: medium, Knowledge: stuck
📊 Hint #8, Scaffolding level: low, Knowledge: zero_knowledge
```

This helps you understand what level of help is being provided.

## Future Enhancements

Potential improvements:
1. **Adaptive thresholds**: Adjust scaffolding levels based on student performance
2. **Concept mastery tracking**: Remember what student already knows
3. **Personalized hints**: Tailor to individual learning style
4. **Hint quality feedback**: Let students rate hint helpfulness
5. **Smart hint skipping**: Jump to medium level if student shows understanding

## Summary

The new scaffolded hints system provides:
- ✅ **10 hints** instead of 3
- ✅ **3 progressive levels** of detail
- ✅ **Zero-knowledge mode** for truly lost students
- ✅ **Problem-specific** guidance
- ✅ **Pseudo-code structures** without implementations
- ✅ **Adaptive resources** and next steps
- ✅ **Academic integrity** maintained throughout

Students get genuinely helpful guidance that adapts to their needs, while never receiving direct answers or code solutions.
