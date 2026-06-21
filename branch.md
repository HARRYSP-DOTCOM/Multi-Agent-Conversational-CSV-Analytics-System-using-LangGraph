# Branching Implementation Notes

The chat branching logic replicates ChatGPT's versioning system. It allows users to edit previous questions, which seamlessly creates an alternate conversation branch from that specific point in history. Users can toggle between the original flow and the edited versions using inline navigation controls.

## Data Structure

Messages are stored as nodes in a dictionary mapping `id` to the message object, acting as an adjacency list. This structure is persisted in `st.session_state.messages`.

```python
{
    "id": str,
    "parent_id": str | None,
    "role": str,
    "content": any,
    "timestamp": str
}
```
Each node links to its predecessor via `parent_id`. The root message has `parent_id = None`. This tree structure naturally accommodates branching: when a user edits a message, the new message is assigned the exact same `parent_id` as the original, creating sibling nodes.

## Session State Tracking

State tracking is now drastically simplified to a single pointer:
- `current_message_id`: The leaf node currently in focus. The entire UI renders the chronological path leading up to this node.

*Note: Previous state variables like `view_mode`, `main_leaf_id`, and `branch_root_id` have been deprecated in favor of this simplified paradigm.*

## Traversal Logic (`utils/tree_utils.py`)

Branch traversal is handled through two core mechanisms:
- **Path Reconstruction** (`get_branch_path`): Walks backward from `current_message_id` following `parent_id` pointers until it hits the root, then reverses the list to return the chronological conversation thread.
- **Leaf Discovery** (`get_leaf_node`): Used when toggling between branch versions. It traverses downward from a given node by fetching children and following the most recent timestamp until it hits a terminal leaf.

## UI Components & State Management

The frontend renders the active branch and exposes version control directly on User messages.

### Edit Button
Every User message displays an Edit (`✏️`) button. 
**On submitting an edit:**
1. A new User message node is created with the exact same `parent_id` as the message being edited.
2. `current_message_id` is updated to this new node.
3. The LLM processes the new query using the historical context up to that point.
4. The system seamlessly transitions into the new branch.

### Version Navigation (`◀ 1/2 ▶`)
When rendering the chat, the UI dynamically checks if any User message has siblings (i.e., other nodes sharing the same `parent_id`). If siblings exist, version navigation arrows are rendered.

**On clicking `◀` or `▶`:**
1. The system identifies the target sibling node (e.g., toggling from Version 1 to Version 2).
2. It calls `get_leaf_node` to find the most recent message at the bottom of that sibling's branch.
3. `current_message_id` is updated to that leaf node.
4. `st.rerun()` is triggered, swapping the entire active view to the selected conversation timeline.

## Write Operations

When handling a new user prompt (non-edit):
1. A user node is instantiated with `parent_id = current_message_id`.
2. `current_message_id` updates to the new user node.
3. The LLM generates a response node linked to the new user node.
4. `current_message_id` updates to the response node.
5. A final `st.rerun()` forces the display loop to render the new nodes.

## Memory Accessibility and Isolation

The branching architecture inherently defines strict boundaries for what conversational memory is passed to the LLM (and thus what context the AI "remembers"). Memory is **strictly linear along the backward path** of the active branch.

### 1. Sequential Inheritance
When a new query is submitted, it inherits the complete, chronological lineage of its direct ancestors all the way back to the root node of the conversation. 
- Example: If the sequence is `Q1 -> A1 -> Q2 -> A2 -> Q3`, `Q3` has access to the memory of `Q1`, `A1`, `Q2`, and `A2`.

### 2. Sibling Isolation (Parallel Branches)
When a query is edited (creating a sibling node), the new branch splits off from that precise point in history. The new branch **does not** inherit any memory from the parallel branch it diverged from.
- Example: If `Q2` is edited to become `Q2 (v2)`, the new branch sequence is `Q1 -> A1 -> Q2 (v2)`. 
- `Q2 (v2)` **will** remember the context of `Q1` and `A1`.
- `Q2 (v2)` **will NOT** remember anything that was discussed in the original `Q2` or `A2`. 

### 3. Fetching from Conversational Memory
Before the system executes an external Web Search or CSV Analysis, the `history_agent` checks the active branch's inherited lineage. If the answer to the latest query can be deduced entirely from its direct ancestors in the active branch, it fetches that memory directly without performing redundant external searches. It cannot fetch answers that exist only in separate, isolated sibling branches.
