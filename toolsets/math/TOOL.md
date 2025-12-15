---
name: math
description: A specialized math engine for generating arithmetic problems, verifying calculations, and performing operations (add, subtract, multiply, factorial). Use this for ANY math-related content generation to ensure accuracy.
license: MIT
class_name: MathToolSet
keywords:
  - math
  - calculate
  - add
  - subtract
  - multiply
  - factorial
  - 计算
  - 加
  - 减
  - 乘
  - 阶乘
---

# Math Skill

## Overview
This skill uses the Model Context Protocol (MCP) to perform mathematical operations. It demonstrates how to integrate an MCP server as a skill.

## Usage
- Use when the user asks for math calculations.
- The skill will query the MCP server for available tools and ask the LLM to select the correct one.

## Example
- "Calculate 3 + 4"
- "What is the factorial of 5?"
