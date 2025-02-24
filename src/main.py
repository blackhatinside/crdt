from fastapi import FastAPI, WebSocket
from ypy_websocket import WebsocketProvider
from ypy_websocket.ystore import SQLiteYStore
from y_py import YDoc
import json

app = FastAPI()

# Initialize Yjs document and store
ydoc = YDoc()
nodes = ydoc.get_array("nodes")
edges = ydoc.get_array("edges")
ystore = SQLiteYStore("ystore.db")

async def websocket_provider(websocket: WebSocket):
    provider = WebsocketProvider(ydoc, websocket, ystore=ystore)
    await provider.handle()

# WebSocket handler for CRDT sync
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        await websocket_provider(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")

# Get current state endpoint
@app.get("/state")
async def get_current_state():
    return {
        "nodes": [dict(node) for node in nodes],
        "edges": [dict(edge) for edge in edges]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        self.added_nodes = set()
        self.removed_nodes = set()
        self.added_edges = set()
        self.removed_edges = set()

    def add_node(self, node: Node):
        if node.id not in self.removed_nodes:
            self.nodes[node.id] = node
            self.added_nodes.add(node.id)

    def update_node(self, node_id: str, update_data: dict):
        if node_id in self.nodes:
            self.nodes[node_id] = self.nodes[node_id].copy(update=update_data)

    def remove_node(self, node_id: str):
        if node_id in self.added_nodes:
            self.added_nodes.remove(node_id)
        self.removed_nodes.add(node_id)
        self.nodes.pop(node_id, None)

    def add_edge(self, edge: Edge):
        edge_id = f"{edge.source}-{edge.target}"
        if edge_id not in self.removed_edges:
            self.edges[edge_id] = edge
            self.added_edges.add(edge_id)

    def remove_edge(self, edge_id: str):
        if edge_id in self.added_edges:
            self.added_edges.remove(edge_id)
        self.removed_edges.add(edge_id)
        self.edges.pop(edge_id, None)

    def merge(self, other: 'CRDT'):
        # Merge nodes
        for node_id in other.added_nodes - self.removed_nodes:
            if node_id in other.nodes:
                self.nodes[node_id] = other.nodes[node_id]
        self.removed_nodes.update(other.removed_nodes)

        # Merge edges
        for edge_id in other.added_edges - self.removed_edges:
            if edge_id in other.edges:
                self.edges[edge_id] = other.edges[edge_id]
        self.removed_edges.update(other.removed_edges)

# Global state
crdt = CRDT()

# WebSocket handler
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            operation = json.loads(data)
            
            # Process operation
            if operation['type'] == 'add_node':
                node = Node(**operation['data'])
                crdt.add_node(node)
            elif operation['type'] == 'update_node':
                crdt.update_node(operation['node_id'], operation['data'])
            elif operation['type'] == 'remove_node':
                crdt.remove_node(operation['node_id'])
            elif operation['type'] == 'add_edge':
                edge = Edge(**operation['data'])
                crdt.add_edge(edge)
            elif operation['type'] == 'remove_edge':
                crdt.remove_edge(operation['edge_id'])
            
            # Broadcast updated state
            state = {
                "nodes": list(crdt.nodes.values()),
                "edges": list(crdt.edges.values())
            }
            await websocket.send_json(state)
            
    except Exception as e:
        print(f"WebSocket error: {e}")

@app.get("/state")
async def get_current_state():
    return {
        "nodes": list(crdt.nodes.values()),
        "edges": list(crdt.edges.values())
    }

if __name__ == "__main__":
    import uvicorn
