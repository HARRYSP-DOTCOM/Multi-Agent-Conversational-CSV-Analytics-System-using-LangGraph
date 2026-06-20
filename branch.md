# Branching Implementation Notes

The chat branching logic isolates specific conversation paths, allowing users to spawn and toggle between independent conversation threads from any historical message.

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
Each node links to its predecessor via `parent_id`. The root message has `parent_id = None`. This structure allows a single message to act as a parent for multiple divergent branches.

## Session State Tracking

To handle rendering and context switching, we track four primary state variables:
- `current_message_id`: The node currently in focus. New user messages append to this node.
- `main_leaf_id`: Tracks the tail node of the primary/global conversation view.
- `view_mode`: Determines the active UI mode. Accepts `"all"` (global view) or `"branch"` (isolated thread view).
- `branch_root_id`: Stores the ID of the message where the active branch originated.

## Traversal Logic (`utils/tree_utils.py`)

Branch traversal is handled through backward path reconstruction:
- **Path Reconstruction** (`get_branch_path`): Walks backward from `current_node_id` following `parent_id` pointers until it hits the root, then reverses the list to return chronological order.
- **Leaf Discovery** (`get_leaf_node`): Used when returning to an existing branch. It traverses downward from a given node by fetching children and following the most recent timestamp until it hits a leaf.

## UI Components & State Management

The frontend uses two numeric toggles per assistant message to handle mode switching: `[1]` and `[2]`.

### Main View (`view_mode == "all"`)
Renders the full chronologically ordered path up to `main_leaf_id`.
Each assistant message displays a `[2]` button to spawn a branch.

**On clicking [2]**:
1. Switches `view_mode` to `"branch"`.
2. Sets `branch_root_id` to the selected message's ID.
3. Computes the active leaf for that branch using `get_leaf_node` and assigns it to `current_message_id`.
4. Triggers `st.rerun()` to execute the branch view render block.

### Branch View (`view_mode == "branch"`)
Renders only the isolated path starting from `branch_root_id` down to `current_message_id`.
The top message of the branch exposes a `[1]` button to exit the branch.

**On clicking [1]**:
1. Reverts `view_mode` back to `"all"`.
2. Nullifies `branch_root_id`.
3. Restores `current_message_id` to point back to `main_leaf_id`.
4. Triggers `st.rerun()`.

## Write Operations

When handling a new user prompt:
1. A user node is instantiated with `parent_id = current_message_id`.
2. `current_message_id` updates to the new user node.
3. The LLM processes the query and generates a response node linked to the user node.
4. `current_message_id` updates to the response node.
5. If operating in `"all"` mode, `main_leaf_id` synchronizes to the response node.
6. A final `st.rerun()` forces the display loop to pick up the new nodes and attach the navigation controls.
