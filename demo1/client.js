import * as Y from 'yjs'
import { WebsocketProvider } from 'y-websocket'

// Create a Yjs document
const ydoc = new Y.Doc()

// Use the third command line argument as room name, or use a default
const roomName = process.argv[3] || 'my-shared-room-123'
console.log(`Using room: ${roomName}`)

// Use local websocket server
const provider = new WebsocketProvider('ws://localhost:1234', roomName, ydoc, {
  connect: true,
  maxBackoffTime: 10000
})

console.log(`Client ID: ${ydoc.clientID}`)

// Set up awareness
const awareness = provider.awareness
awareness.setLocalStateField('user', {
  name: process.argv[2] || 'Anonymous',
  color: process.argv[2] === 'client1' ? '#ffb61e' : '#0099ff'
})

// Improved connection status logging
provider.on('status', event => {
  console.log('Connection status:', event.status)
  // Log detailed connection information
  console.log('Connected:', provider.wsconnected)
  console.log('Should connect:', provider.shouldConnect)
})

awareness.on('change', changes => {
  console.log('Awareness changed. Connected clients:', Array.from(awareness.getStates().keys()))
})

// Create a Y.Map to hold the JSON data
const ymap = ydoc.getMap('shared-json')

// Load initial data from example_small.json
const initialData = {
  "name": "John Doe",
  "age": 30,
  "address": {
    "street": "123 Main St",
    "city": "Anytown"
  },
  "hobbies": ["reading", "gaming"]
}

// Wait for sync before initializing
provider.on('sync', isSynced => {
  console.log('Sync status:', isSynced)
  
  // Initialize the shared JSON data if it's not already set and we're synced
  if (isSynced && ymap.size === 0) {
    console.log('Initializing data')
    ymap.set('data', initialData)
  }
})

// Observe changes to the shared JSON data
ymap.observe(event => {
  console.log('Changes detected:', event.changes)
  console.log('Updated JSON data:', ymap.get('data'))
})

// Function to update the shared JSON data
function updateJsonData(updates) {
  console.log(`Updating with: ${JSON.stringify(updates)}`)
  ydoc.transact(() => {
    const data = ymap.get('data') || initialData
    if (updates.address && data.address) {
      // Handle nested objects properly
      data.address = { ...data.address, ...updates.address }
      delete updates.address
    }
    Object.assign(data, updates)
    ymap.set('data', data)
  })
}

// Function to wait for provider to be connected - FIX: only execute when truly connected
function waitForConnection(callback) {
  if (provider.wsconnected) {
    console.log('Already connected! Executing update.')
    callback()
    return
  }

  console.log('Waiting for connection before updating...')
  
  // Use one-time event listener for connection
  const statusHandler = (event) => {
    if (event.status === 'connected') {
      console.log('Connected to server! Executing update.')
      // Remove listener to avoid multiple calls
      provider.off('status', statusHandler)
      // Wait a bit for sync to complete
      setTimeout(callback, 1500)
    }
  }
  
  provider.on('status', statusHandler)
}

// Example updates from Client 1
if (process.argv[2] === 'client1') {
  waitForConnection(() => {
    updateJsonData({ name: 'Jane Doe', age: 25 })
    console.log('Client 1 made an update')
    console.log('Current JSON data:', ymap.get('data'))
  })
}

// Example updates from Client 2
if (process.argv[2] === 'client2') {
  waitForConnection(() => {
    updateJsonData({ address: { street: '456 Elm St', city: 'Othertown' } })
    console.log('Client 2 made an update')
    console.log('Current JSON data:', ymap.get('data'))
  })
}

// Force reconnection if not connected after 5 seconds
setTimeout(() => {
  if (!provider.wsconnected) {
    console.log('Not connected after 5 seconds, trying to reconnect...')
    provider.disconnect()
    provider.connect()
  }
}, 5000)

// Keep the script running
process.on('SIGINT', () => {
  provider.disconnect()
  process.exit(0)
})

console.log(`${process.argv[2]} started. Press Ctrl+C to exit.`)
