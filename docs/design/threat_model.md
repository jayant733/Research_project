# Threat model for the local demonstrator

This document describes what the running system does and what it does not prove.

## Trusted computing base

The Flower server, decryption authority, and dashboard run in one process for the local demo. A party who can read that process can read the CKKS secret key. The code keeps that key on `FHEAuthority` and performs addition in `ServerFHEEngine`, which is constructed from the public context only. That separation is a code boundary, not a separate-host guarantee.

## CKKS pool

Clients encrypt sample-scaled weights under a shared public context. The server sums those ciphertexts and multiplies by the inverse of the pool's sample count. `FHEAuthority.decrypt` is called on that aggregate only. Individual CKKS updates are not decrypted. Clients in this pool share the ability to decrypt the aggregate because they share the key ceremony's secret in the colocated demo. This is not a threshold or multi-key scheme.

## Secure-aggregation pool

Each client adds pairwise pseudorandom masks derived from a client-held secret and the peer list for that round. The server sums masked, sample-scaled updates and divides by the sample count. It does not load the mask secret. If any assigned peer is missing, aggregation raises `SecAggDropoutError` instead of inventing a dropout recovery. This is not the Bonawitz et al. secure-aggregation protocol: there is no key agreement, input validation, or malicious-client security proof.

## Differential-privacy pool

The client clips the model delta and adds Gaussian noise. An Opacus RDP accountant steps once per local update with `sample_rate=1.0` and reports epsilon at `delta=1e-5`. The displayed epsilon is that composed spend for the noisiest client in the round. It is not a centrally composed guarantee for the whole federation, and the noise multiplier is a demonstration setting rather than a tuned production budget.

## Telemetry

CPU, memory, bandwidth, and battery used for TOPSIS are generated from the client's declared profile and the round index, with a bounded blend of measured fit time. Threads on one host cannot honestly report different batteries or network links. The upload size and fit time shown in the UI are measured.

## Dropout recovery

When recovery is enabled, each secure-aggregation client uploads Shamir shares of the pair seeds it already knows. If one assigned peer is missing, the server reconstructs that peer's mask from a surviving endpoint and removes it from the sum. Two simultaneous dropouts are rejected when the missing pair has no surviving endpoint. The shares are visible to the colocated server on every round, so this does not hide masks from that server. There is still no production key agreement and no malicious-client proof.

## Trust and attacks

Scaled updates, near-zero updates, and telemetry that disagrees with the seeded profile lower a heuristic trust score. Low trust reduces the plaintext or local-DP aggregation weight and blocks assignment to local DP on the next round. Very low trust can also leave a CKKS ciphertext out of the sum. These checks are not a detection proof, and a client can still affect a masked pool during the round in which the anomaly is first observed.

## Out of scope

Malicious-server privacy against the colocated key holder, production secure aggregation, a proof of poisoning detection, formal convergence proofs, and energy measurement on physical devices are not provided.
