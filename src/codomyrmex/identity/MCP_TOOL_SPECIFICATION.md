# Identity - MCP Tool Specification

This document specifies the Model Context Protocol (MCP) tools of the `identity` module. They are defined with `@mcp_tool` in `mcp_tools.py` and surfaced by the PAI MCP bridge as `codomyrmex.<name>`.

## General Considerations for Identity Tools

- **No shared state**: Every call creates a new `IdentityManager`. A persona created by `identity_create_persona` is not available to a later `identity_rotate_persona` call; pass `register_personas` to rotate within one call.
- **Verification levels**: `unverified`, `anonymous_verified`, `verified_anon`, `kyc_verified`.
- **Error Handling**: Tools catch exceptions and return `{"status": "error", "message": "<description>"}`.
- **Security**: Bio-cognitive samples are processed in memory and not persisted by the MCP layer.

---

## Tool: `identity_list_levels`

### 1. Tool Purpose and Description

Lists the supported verification levels.

### 2. Invocation Name

`identity_list_levels`

### 3. Input Schema (Parameters)

None.

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "levels": [
    {"name": "UNVERIFIED", "value": "unverified"},
    {"name": "ANON", "value": "anonymous_verified"},
    {"name": "VERIFIED_ANON", "value": "verified_anon"},
    {"name": "KYC", "value": "kyc_verified"}
  ]
}
```

---

## Tool: `identity_create_persona`

### 1. Tool Purpose and Description

Creates a persona and returns its metadata.

### 2. Invocation Name

`identity_create_persona`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `persona_id` | `string` | Yes | Unique persona identifier | `"p1"` |
| `name` | `string` | Yes | Display name | `"Alice"` |
| `level` | `string` | No | Verification level value (default `"unverified"`) | `"kyc_verified"` |
| `capabilities` | `array[string]` | No | Capability strings | `["read"]` |

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "persona": {
    "id": "p1",
    "name": "Alice",
    "level": "unverified",
    "created_at": "2026-10-07T23:35:46.502908+00:00",
    "attributes": {},
    "crumbs_count": 0,
    "capabilities": ["read"],
    "is_active": true
  }
}
```

An unknown `level` returns the error shape.

---

## Tool: `identity_check_capability`

### 1. Tool Purpose and Description

Checks whether a list of capabilities grants a required capability, using a temporary persona.

### 2. Invocation Name

`identity_check_capability`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `capabilities` | `array[string]` | Yes | Capabilities the persona holds | `["read"]` |
| `required_capability` | `string` | Yes | Capability to check for | `"write"` |

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "has_capability": false,
  "required": "write",
  "provided": ["read"]
}
```

---

## Tool: `identity_verify_biocognitive`

### 1. Tool Purpose and Description

Verifies a user with bio-cognitive signals: keystroke dynamics, heartbeat RR intervals and/or EEG band powers. Every modality that is supplied must pass.

### 2. Invocation Name

`identity_verify_biocognitive`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `user_id` | `string` | Yes | User being verified | `"u1"` |
| `keystroke_values` | `array[number]` | No | Baseline keystroke flight times for enrolment | `[0.12, 0.15, 0.11]` |
| `current_keystroke` | `number` | No | Current keystroke flight time to verify | `0.13` |
| `heartbeat_intervals` | `array[number]` | No | Current RR intervals (ms) to verify | `[810, 790, 805]` |
| `heartbeat_baseline` | `array[number]` | No | Baseline RR intervals (ms) for enrolment | `[800, 795, 810]` |
| `eeg_samples` | `array[number]` | No | Current EEG amplitude samples | `[0.1, -0.2, 0.05]` |
| `eeg_baseline` | `array[number]` | No | Baseline EEG samples for enrolment | `[0.1, -0.1, 0.02]` |
| `eeg_sampling_rate` | `number` | No | EEG sampling rate in Hz (default `256.0`) | `256.0` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` |
| `verified` | `boolean` | `true` when every supplied modality passed |
| `modalities` | `object` | Per-modality result (`keystroke`, `heartbeat`, `eeg`) with `verified` and details |
| `confidence` | `number` | Verifier confidence for `user_id` |

With no signal data the tool returns `{"status": "error", "message": "No bio-cognitive data provided for verification"}`.

---

## Tool: `identity_rotate_persona`

### 1. Tool Purpose and Description

Rotates the active persona: directly to a persona ID, round-robin to the next persona, or to the preferred persona. Personas can be registered inline first.

### 2. Invocation Name

`identity_rotate_persona`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `persona_id` | `string` | For `direct` | Target persona ID | `"p2"` |
| `mode` | `string` | No | `direct`, `next` or `preferred` (default `direct`) | `"direct"` |
| `reason` | `string` | No | Reason recorded in the rotation history (default `""`) | `"session start"` |
| `set_preferred` | `boolean` | No | Make `persona_id` the preferred persona before rotating (default `false`) | `true` |
| `clear_preferred` | `boolean` | No | Clear the preferred persona after rotating (default `false`) | `false` |
| `register_personas` | `array[object]` | No | Personas to register first: `{"id", "name", "level"?, "capabilities"?}` | `[{"id": "p2", "name": "Bob"}]` |

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "active_persona": {"id": "p2", "name": "Bob", "level": "unverified"},
  "rotation_history": [{"from": "none", "to": "p2", "timestamp": "...", "reason": ""}],
  "rotation_count": 1,
  "registered_count": 1
}
```

Errors: `"persona_id required for mode='direct'"`, `"No preferred persona set"`, `"Unknown rotation mode: <mode>. Use direct, next, or preferred."`, or `"Persona ID <id> not found"` when the persona was not registered in the same call.

### 5. Idempotency

- **Idempotent**: Yes, because nothing persists between calls.

<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->
