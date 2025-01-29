import numpy as np
import hashlib

def simulate_qkd_with_noise_reduction(N, noise_level):
    # Alice's preparation
    alice_bits = np.random.randint(2, size=N)
    alice_bases = np.random.randint(2, size=N)
    
    # Quantum channel simulation with noise
    bob_bases = np.random.randint(2, size=N)
    bob_bits = []
    
    for i in range(N):
        if alice_bases[i] == bob_bases[i]:
            # Apply noise with given probability
            if np.random.rand() < noise_level:
                bob_bits.append(1 - alice_bits[i])
            else:
                bob_bits.append(alice_bits[i])
        else:
            bob_bits.append(np.random.randint(2))
    
    # Sifting process
    matching_indices = np.where(alice_bases == bob_bases)[0]
    sifted_alice = alice_bits[matching_indices]
    sifted_bob = np.array(bob_bits)[matching_indices]
    
    if len(sifted_alice) < 20:
        raise ValueError("Insufficient matching bases for key establishment")
    
    # Error estimation (using 30% of sifted key)
    test_size = int(0.3 * len(sifted_alice))
    test_alice = sifted_alice[:test_size]
    test_bob = sifted_bob[:test_size]
    
    error_rate = np.mean(test_alice != test_bob)
    print(f"Initial error rate: {error_rate:.2%}")
    
    if error_rate > 0.15:
        raise ValueError("Error rate too high for secure key exchange")
    
    # Remove test bits from final key
    raw_alice = sifted_alice[test_size:]
    raw_bob = sifted_bob[test_size:]
    
    # Error correction
    corrected_bob = cascade_protocol(raw_alice, raw_bob)
    remaining_errors = np.sum(raw_alice != corrected_bob)
    print(f"Remaining errors after correction: {remaining_errors}")
    
    # Privacy amplification
    final_key = privacy_amplification(raw_alice)
    return final_key, error_rate, remaining_errors

def cascade_protocol(alice, bob, block_size=4):
    bob = bob.copy()
    max_iterations = 4
    
    for _ in range(max_iterations):
        for i in range(0, len(alice), block_size):
            block_end = min(i+block_size, len(alice))
            a_block = alice[i:block_end]
            b_block = bob[i:block_end]
            
            if sum(a_block) % 2 != sum(b_block) % 2:
                # Binary search for error
                for j in range(len(a_block)):
                    if a_block[j] != b_block[j]:
                        bob[i+j] = a_block[j]
                        break
        block_size *= 2
    
    return bob

def privacy_amplification(key_bits):
    # Convert bits to bytes
    byte_array = bytearray()
    for i in range(0, len(key_bits), 8):
        byte = sum(bit << (7 - j) for j, bit in enumerate(key_bits[i:i+8]))
        byte_array.append(byte)
    
    # Apply cryptographic hash
    hashed = hashlib.sha256(byte_array).digest()
    return hashed.hex()

# Example usage
try:
    final_key, error_rate, remaining_errors = simulate_qkd_with_noise_reduction(
        N=1000,       # Number of initial qubits
        noise_level=0.05  # 5% noise probability
    )
    print(f"\nFinal secret key: {final_key[:20]}... (length: {len(final_key)})")
    print(f"Key establishment successful with final error rate: {remaining_errors/len(final_key):.2%}")
except ValueError as e:
    print(f"Key exchange failed: {e}")
