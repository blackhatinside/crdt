import y_py as Y

# Create documents for two users
alice_doc = Y.YDoc()
bob_doc = Y.YDoc()

# Both users access the same shared map
alice_map = alice_doc.get_map('user-profile')
bob_map = bob_doc.get_map('user-profile')

print("Initial state:")
print(f"Alice's map: {dict(alice_map)}")
print(f"Bob's map: {dict(bob_map)}")

# Alice adds some profile data
print("\n==================================================\n")
print("Alice adds profile data...")
with alice_doc.begin_transaction() as txn:
    alice_map.set(txn, "name", "Alice Smith")
    alice_map.set(txn, "email", "alice@example.com")
    alice_map.set(txn, "age", 28)

print(f"Alice's map: {dict(alice_map)}")
print(f"Bob's map (before sync): {dict(bob_map)}")

# Sync Alice's changes to Bob
print("\n==================================================\n")
print("Syncing Alice's changes to Bob...")
update_from_alice = Y.encode_state_as_update(alice_doc)
Y.apply_update(bob_doc, update_from_alice)

print(f"Bob's map (after sync): {dict(bob_map)}")

# Bob modifies some fields while adding new ones
print("\n==================================================\n")
print("Bob updates some fields and adds new ones...")
with bob_doc.begin_transaction() as txn:
    # Update existing field
    bob_map.set(txn, "email", "alice.smith@company.com")  # Updates email
    # Add new fields
    bob_map.set(txn, "department", "Engineering")
    bob_map.set(txn, "location", "New York")

print(f"Bob's map: {dict(bob_map)}")
print(f"Alice's map (before sync): {dict(alice_map)}")

# Meanwhile, Alice also makes changes
print("\n==================================================\n")
print("Meanwhile, Alice also updates her profile...")
with alice_doc.begin_transaction() as txn:
    # Update age
    alice_map.set(txn, "age", 29)  # Birthday update
    # Add skills as a nested data structure

    # Create a skills map within the document
    skills_map = alice_doc.get_map('skills')
    with alice_doc.begin_transaction() as skills_txn:
        skills_map.set(skills_txn, "programming", ["Python", "JavaScript", "Rust"])
        skills_map.set(skills_txn, "languages", ["English", "Spanish"])

    # Reference the skills map in the profile
    alice_map.set(txn, "skills_ref", "skills")

print(f"Alice's map: {dict(alice_map)}")
print(f"Alice's skills: {dict(alice_doc.get_map('skills'))}")

# Synchronize both ways
print("\n==================================================\n")
print("Synchronizing in both directions...")

# Bob to Alice
update_from_bob = Y.encode_state_as_update(bob_doc)
Y.apply_update(alice_doc, update_from_bob)

# Alice to Bob
update_from_alice = Y.encode_state_as_update(alice_doc)
Y.apply_update(bob_doc, update_from_alice)

print("\n==================================================\n")
print("Final synchronized state:")
print(f"Alice's map: {dict(alice_map)}")
print(f"Bob's map: {dict(bob_map)}")
print(f"Skills map in Alice's doc: {dict(alice_doc.get_map('skills'))}")
print(f"Skills map in Bob's doc: {dict(bob_doc.get_map('skills'))}")

# Demonstrate conflict resolution
print("\n==================================================\n")
print("Demonstrating concurrent edits of the same field...")

# Create new documents
charlie_doc = Y.YDoc()
diana_doc = Y.YDoc()

charlie_map = charlie_doc.get_map('settings')
diana_map = diana_doc.get_map('settings')

# Initialize with same content
with charlie_doc.begin_transaction() as txn:
    charlie_map.set(txn, "theme", "light")
    charlie_map.set(txn, "fontSize", 12)
    charlie_map.set(txn, "notifications", True)

# Sync to Diana
update = Y.encode_state_as_update(charlie_doc)
Y.apply_update(diana_doc, update)

print("Starting with synchronized settings:")
print(f"Charlie: {dict(charlie_map)}")
print(f"Diana: {dict(diana_map)}")

# Both modify the same fields concurrently
print("\nBoth users edit the same fields:")

with charlie_doc.begin_transaction() as txn:
    charlie_map.set(txn, "theme", "dark")
    charlie_map.set(txn, "fontSize", 14)

with diana_doc.begin_transaction() as txn:
    diana_map.set(txn, "theme", "blue")
    diana_map.set(txn, "fontSize", 16)
    # Diana also adds a new field
    diana_map.set(txn, "colorBlindMode", True)

print(f"Charlie (local): {dict(charlie_map)}")
print(f"Diana (local): {dict(diana_map)}")

# Sync both ways
update_charlie = Y.encode_state_as_update(charlie_doc)
update_diana = Y.encode_state_as_update(diana_doc)

Y.apply_update(charlie_doc, update_diana)
Y.apply_update(diana_doc, update_charlie)

print("\nAfter synchronization (last-write-wins for map fields):")
print(f"Charlie: {dict(charlie_map)}")
print(f"Diana: {dict(diana_map)}")