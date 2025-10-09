# Password Storage

Password storage in the database is done in compliance with [NIST SP 800-63B-4 (Digital Identity Guidelines Authentication and Authenticator Management)](https://doi.org/10.6028/NIST.SP.800-63b-4) with the following flow:

1. Plain password go through bcrypt_pbkdf with 16 bytes random salt and 1000 rounds to generate 32 key bytes.
2. The password key bytes encrypted using AES-CBC with 16 bytes random IV and an encryption key accessed only by the backend server (NOT the database).
3. The database stores "encrypted_pw_hash", "encrypted_pw_hash_iv", and "pw_hash_salt" in binary format in the user's document.

When verifying, the following steps are to be executed:

1. Retrieve "encrypted_pw_hash", "encrypted_pw_hash_iv", and "pw_hash_salt" from database.
2. Use bcrypt_pbkdf on the incoming password with "pw_hash_salt" to recompute the password key bytes.
3. Decrypt "encrypted_pw_hash" with "encrypted_pw_hash_iv" and the encryption key.
4. Compare the decrypted password key bytes in storage and the new password key bytes generated from the incoming password.
