# Git Overview

## What is Git?
**Git** is a distributed **Version Control System (VCS)**. It tracks changes in source code during software development, allowing multiple developers to work on the same project simultaneously without overwriting each other's work.

Think of Git like a "Time Machine" for your code. Every time you make a "commit," you are taking a snapshot of your entire project at that specific moment. If something breaks later, you can always go back to a previous snapshot.

## Why do we need it?

### 1. Collaboration
Modern software is built by teams. Git allows dozens or even thousands of developers to contribute to the same codebase. It handles "merging" their changes together and alerts them if two people tried to change the same line of code (a "conflict").

### 2. Version History
Git keeps a complete history of every change ever made to the project. You can see *who* made a change, *when* they made it, and *why* (via commit messages). This is invaluable for debugging and auditing.

### 3. Branching & Experimentation
With Git, you can create a "branch"—a separate workspace where you can try out new ideas or fix bugs without affecting the main "master" code. If the experiment works, you merge it back; if it doesn't, you simply delete the branch.

### 4. Safety
Because Git is "distributed," every developer has a full copy of the entire project history on their own machine. If the central server (like GitHub) ever fails, the project can be restored from any developer's computer.

## Global Adoption
Git is the undisputed king of version control:
- **Market Share**: Over 90% of software developers worldwide use Git.
- **The Linux Legacy**: It was originally created by Linus Torvalds (the creator of Linux) to manage the Linux kernel development.
- **Standard Platform**: Platforms like **GitHub**, **GitLab**, and **Bitbucket** are built entirely around Git, hosting hundreds of millions of projects.

## Popular Git Commands
Here are the commands you will use in your daily workflow:

### Basic Workflow
| Command | Description |
| :--- | :--- |
| `git status` | Show the status of your changes (which files are modified/staged). |
| `git add <file>` | Stage a specific file for the next commit. |
| `git add .` | Stage **all** changes in the current directory. |
| `git commit -m "msg"` | Create a new snapshot (commit) with a descriptive message. |
| `git push` | Upload your local commits to a remote server (like GitHub). |
| `git pull` | Download latest changes from the remote server and merge them. |

### Branching & Exploration
| Command | Description |
| :--- | :--- |
| `git branch` | List all local branches. |
| `git checkout -b <name>` | Create a new branch and switch to it immediately. |
| `git checkout <name>` | Switch to an existing branch. |
| `git merge <name>` | Merge changes from another branch into your current one. |
| `git log --oneline` | Show a simplified history of recent commits. |
| `git diff` | Show the exact line-by-line changes in your files. |

## How we use it here
In this project, we follow a strict Git workflow:
- We never push directly to `master`.
- We use **Worktrees** to isolate different tasks.
- We use **Pull Requests (PRs)** to review code before it is merged.
- We use the **GitHub CLI (`gh`)** to manage our PRs directly from the terminal.
