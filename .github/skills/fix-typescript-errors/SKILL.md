---
name: fix-typescript-errors
description: 'Fix common TypeScript errors in JavaScript files with TypeScript checks enabled, such as implicit any types on parameters. Use when encountering TypeScript compilation errors related to implicit any types in JavaScript files.'
argument-hint: 'Describe the error or file path'
user-invocable: true
---

# Fix TypeScript Errors

This skill helps resolve TypeScript errors in JavaScript files, particularly implicit any type errors.

## When to Use

- When you see "Parameter 'X' implicitly has an 'any' type" errors
- For adding type annotations to function parameters
- Converting JavaScript files to TypeScript or adding JSDoc comments

## Step-by-Step Procedure

1. Identify the error location in the file.
2. Determine the appropriate type for the parameter (e.g., string, number, object).
3. Add type annotation: either convert to .ts and add `: Type`, or add JSDoc `/** @param {Type} param */`.
4. Run TypeScript check to verify the fix.

## Examples

For a parameter `type` in a function:
- JSDoc: `/** @param {string} type */`
- TypeScript: `function foo(type: string) { ... }`