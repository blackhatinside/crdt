import y_py as Y

print("Demonstrating conflict resolution with concurrent edits...")

# Create two documents
charlie_doc = Y.YDoc()
diana_doc = Y.YDoc()

charlie_text = charlie_doc.get_text('conflict-demo')
diana_text = diana_doc.get_text('conflict-demo')

# Initialize with same content
with charlie_doc.begin_transaction() as txn:
    charlie_text.extend(txn, "This is a shared document.")

# Sync to Diana
update = Y.encode_state_as_update(charlie_doc)
Y.apply_update(diana_doc, update)

print("Starting with synchronized content:")
print(f"Charlie: '{str(charlie_text)}'")
print(f"Diana: '{str(diana_text)}'")

# Both make conflicting changes
print("\nBoth users edit the same part of the document:")

with charlie_doc.begin_transaction() as txn:
    # In y-py, delete takes the transaction and the length to delete
    # Delete first 7 characters ("This is")
    charlie_text.delete_range(txn, 0, 7)
    charlie_text.insert(txn, 0, "Charlie's")

with diana_doc.begin_transaction() as txn:
    # Delete first 7 characters
    diana_text.delete_range(txn, 0, 7)
    diana_text.insert(txn, 0, "Diana's amazing")

print(f"Charlie (local): '{str(charlie_text)}'")
print(f"Diana (local): '{str(diana_text)}'")

# Sync both ways
update_charlie = Y.encode_state_as_update(charlie_doc)
update_diana = Y.encode_state_as_update(diana_doc)

Y.apply_update(charlie_doc, update_diana)
Y.apply_update(diana_doc, update_charlie)

print("\nAfter synchronization (conflict resolution handled by CRDT):")
print(f"Charlie: '{str(charlie_text)}'")
print(f"Diana: '{str(diana_text)}'")
print("\nNote how both documents have identical content despite the conflict.")