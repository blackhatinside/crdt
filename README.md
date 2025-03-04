## CRDT
- Conflict Free Replicated Data Type
- Simplifies Distributed Systems with Collaborative Environment
- strongly consistent vs eventually consistent
- state based vs operation based


## Yjs Implementation

# y-doc

```javascript
const ydoc = new Y.Doc()
```

# [y-indexeddb](https://github.com/yjs/y-indexeddb):
offline persistent browser storage for multiple sessions

```bash
npm i --save y-indexeddb
```

```javascript
import { IndexeddbPersistence } from 'y-indexeddb'
const provider = new IndexeddbPersistence(docName, ydoc)
```

# [y-websocket](https://github.com/yjs/y-websocket):
client server model where clients connect to a single endpoint and server distributes awareness info and doc updates among clients

```bash
npm i y-websocket
```
