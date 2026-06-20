import uuid
from datetime import datetime

def create_message(role: str, content: any, parent_id: str = None) -> dict:
    """Create a new message node."""
    return {
        "id": str(uuid.uuid4()),
        "parent_id": parent_id,
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow().isoformat()
    }

def add_message(messages_dict: dict, role: str, content: any, parent_id: str = None) -> str:
    """
    Creates a new message and adds it to the messages dictionary.
    Returns the new message's ID.
    """
    msg = create_message(role, content, parent_id)
    messages_dict[msg["id"]] = msg
    return msg["id"]

def get_branch_path(messages_dict: dict, current_node_id: str) -> list:
    """
    Reconstructs the active branch by traversing backwards from current_node_id.
    Returns a list of message objects from root to current.
    """
    path = []
    current_id = current_node_id

    while current_id and current_id in messages_dict:
        node = messages_dict[current_id]
        path.append(node)
        current_id = node.get("parent_id")

    # Reverse to get chronological order (root to leaf)
    path.reverse()
    return path

def get_root_id(messages_dict: dict, current_id: str) -> str:
    """Return the root message ID for the given node."""
    node_id = current_id
    while node_id and node_id in messages_dict:
        parent = messages_dict[node_id].get("parent_id")
        if not parent:
            return node_id
        node_id = parent
    return node_id

def get_children(messages_dict: dict, parent_id: str) -> list:
    """Returns a list of child messages sorted by timestamp."""
    children = [msg for msg in messages_dict.values() if msg.get("parent_id") == parent_id]
    return sorted(children, key=lambda x: x["timestamp"])

def get_leaf_node(messages_dict: dict, node_id: str) -> str:
    """Finds the most recent leaf node under the given node_id."""
    current = node_id
    while True:
        children = get_children(messages_dict, current)
        if not children:
            return current
        # Follow the most recently created child branch
        current = children[-1]["id"]


def get_descendants(messages_dict: dict, node_id: str) -> list:
    """Recursively collect all descendant messages of the given node."""
    descendants = []
    children = get_children(messages_dict, node_id)
    for child in children:
        descendants.append(child)
        descendants.extend(get_descendants(messages_dict, child["id"]))
    return descendants


def get_full_branch(messages_dict: dict, start_id: str) -> list:
    """Return the full subtree (including the start node) sorted chronologically."""
    root_msg = messages_dict.get(start_id)
    if not root_msg:
        return []
    all_msgs = [root_msg] + get_descendants(messages_dict, start_id)
    return sorted(all_msgs, key=lambda x: x["timestamp"])
