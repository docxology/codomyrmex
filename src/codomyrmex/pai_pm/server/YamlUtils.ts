/**
 * YamlUtils.ts - Shared YAML Utilities for PAI System
 * 
 * Provides centralized YAML parsing and writing logic standardized across
 * all PAI CLI tools (Layer 1) and server components (Layer 2).
 */

import { writeFileSync } from "fs";

// ============================================================================
// Parsing
// ============================================================================

export function parseSimpleYaml(content: string): Record<string, any> {
    const result: Record<string, any> = {};
    let currentArrayKey: string | null = null;
    const currentArray: string[] = [];
    let multiLineKey: string | null = null;
    const multiLineValue: string[] = [];

    for (const line of content.split("\n")) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith("#")) {
            if (multiLineKey && line.startsWith("  ")) {
                multiLineValue.push(line.slice(2));
            }
            continue;
        }

        // Multi-line value continuation
        if (multiLineKey && (line.startsWith("  ") || line.startsWith("\t"))) {
            multiLineValue.push(trimmed);
            continue;
        }

        // End multi-line
        if (multiLineKey) {
            result[multiLineKey] = multiLineValue.join("\n");
            multiLineKey = null;
            multiLineValue.length = 0;
        }

        if (trimmed.startsWith("- ") && currentArrayKey) {
            let value = trimmed.slice(2).trim();
            // Handle quoted strings in array items
            if ((value.startsWith('"') && value.endsWith('"')) ||
                (value.startsWith("'") && value.endsWith("'"))) {
                value = value.slice(1, -1);
            }
            currentArray.push(value);
            continue;
        }

        // Save previous array
        if (currentArrayKey && currentArray.length > 0) {
            result[currentArrayKey] = [...currentArray];
            currentArray.length = 0;
            currentArrayKey = null;
        }

        // Key-value pair
        const colonIdx = trimmed.indexOf(":");
        if (colonIdx === -1) continue;

        const key = trimmed.slice(0, colonIdx).trim();
        let value = trimmed.slice(colonIdx + 1).trim();

        if (value === "|") {
            multiLineKey = key;
            continue;
        }

        if (!value) {
            currentArrayKey = key;
            continue;
        }

        // Remove quotes
        if ((value.startsWith('"') && value.endsWith('"')) ||
            (value.startsWith("'") && value.endsWith("'"))) {
            value = value.slice(1, -1);
        }

        result[key] = value;
    }

    // Save final array or multi-line
    if (currentArrayKey && currentArray.length > 0) {
        result[currentArrayKey] = [...currentArray];
    }
    if (multiLineKey) {
        result[multiLineKey] = multiLineValue.join("\n");
    }

    return result;
}

// ============================================================================
// Writing Helper
// ============================================================================

export function writeYamlFile(path: string, data: Record<string, any>, options: {
    title?: string;
    orderedKeys?: string[];
    multiLineKeys?: string[];
} = {}): void {
    const lines: string[] = [];

    if (options.title) lines.push(`# ${options.title}`);
    lines.push(``);

    // Write ordered keys first
    const handledKeys = new Set<string>();

    if (options.orderedKeys) {
        for (const key of options.orderedKeys) {
            if (data[key] !== undefined && data[key] !== null && data[key] !== "") {
                const val = data[key];
                // Quote strings unless it's a known non-quoted field
                const needsQuotes = typeof val === "string" &&
                    !["id", "status", "created", "completed", "priority", "target", "parent_goal", "parent_mission"].includes(key);

                if (needsQuotes) {
                    lines.push(`${key}: "${val}"`);
                } else {
                    lines.push(`${key}: ${val}`);
                }
                handledKeys.add(key);
            }
        }
    }

    // Handle multi-line keys
    if (options.multiLineKeys) {
        for (const key of options.multiLineKeys) {
            if (data[key]) {
                lines.push(``);
                lines.push(`${key}: |`);
                for (const line of String(data[key]).split("\n")) {
                    lines.push(`  ${line}`);
                }
                handledKeys.add(key);
            }
        }
    }

    // Handle remaining keys (arrays and others)
    for (const [key, val] of Object.entries(data)) {
        if (handledKeys.has(key)) continue;

        if (Array.isArray(val)) {
            if (val.length > 0) {
                lines.push(``);
                lines.push(`${key}:`);
                for (const item of val) {
                    // Ensure item is a string
                    const strItem = String(item);
                    // Check if it needs quotes (contains special chars or colons)
                    if (strItem.includes(":") || strItem.includes("#") || strItem.trim() !== strItem) {
                        lines.push(`  - "${strItem}"`);
                    } else {
                        lines.push(`  - ${strItem}`);
                    }
                }
            }
        } else if (val !== undefined && val !== null && val !== "") {
            // Simple key value
            if (typeof val === "string") {
                lines.push(`${key}: "${val}"`);
            } else {
                lines.push(`${key}: ${val}`);
            }
        }
    }

    lines.push(``);
    writeFileSync(path, lines.join("\n"));
}
