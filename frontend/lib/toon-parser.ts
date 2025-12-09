// TOON (Token-Oriented Object Notation) Parser
// Format: key1:value1|key2:value2|key3:value3

import { ParsedVulnerability } from '@/types/scan';

/**
 * Parse a TOON format string into a key-value object
 * @param toonString - String in format "key1:value1|key2:value2"
 * @returns Object with parsed key-value pairs
 */
export function parseTOON(toonString: string): Record<string, string> {
  if (!toonString || typeof toonString !== 'string') {
    return {};
  }

  const result: Record<string, string> = {};
  const fields = toonString.split('|');

  fields.forEach((field) => {
    const colonIndex = field.indexOf(':');
    if (colonIndex === -1) return;

    const key = field.substring(0, colonIndex).trim();
    const value = field.substring(colonIndex + 1).trim();

    if (key) {
      result[key] = value;
    }
  });

  return result;
}

/**
 * Parse a vulnerability patch TOON string into a ParsedVulnerability object
 * @param toonString - TOON formatted vulnerability string
 * @returns ParsedVulnerability object
 */
export function parseVulnerability(toonString: string): ParsedVulnerability {
  const data = parseTOON(toonString);

  // Extract line numbers if present
  let lineStart: number | undefined;
  let lineEnd: number | undefined;
  if (data.ln) {
    const lineParts = data.ln.split('-');
    lineStart = parseInt(lineParts[0], 10);
    lineEnd = lineParts.length > 1 ? parseInt(lineParts[1], 10) : lineStart;
  }

  // Generate deterministic ID based on content
  const idParts = [
    'vuln',
    data.file || 'unknown',
    lineStart || '0',
    data.category || 'unknown',
  ].join('-').replace(/[^a-zA-Z0-9-]/g, '_');
  const id = idParts;

  return {
    id,
    type: 'vulnerability',
    explanation: data.explanation || '',
    formattedCode: data.formatted_code || '',
    category: data.category || 'Unknown',
    severity: (data.sev || data.severity || 'MEDIUM').toUpperCase(),
    file: data.file,
    lineStart,
    lineEnd,

    // CVSS-like metrics
    attackVector: data.attack_vector,
    attackComplexity: data.attack_complexity,
    privilegesRequired: data.privileges_required,
    userInteraction: data.user_interaction,
    impactConfidentiality: data.impact_confidentiality,
    impactIntegrity: data.impact_integrity,
    impactAvailability: data.impact_availability,

    // Keep raw data for debugging
    raw: data,
  };
}

/**
 * Parse a secret patch TOON string into a ParsedVulnerability object
 * @param toonString - TOON formatted secret string
 * @returns ParsedVulnerability object (using same type for consistency)
 */
export function parseSecret(toonString: string): ParsedVulnerability {
  const data = parseTOON(toonString);

  // Extract line numbers if present
  let lineStart: number | undefined;
  let lineEnd: number | undefined;
  if (data.ln) {
    const lineParts = data.ln.split('-');
    lineStart = parseInt(lineParts[0], 10);
    lineEnd = lineParts.length > 1 ? parseInt(lineParts[1], 10) : lineStart;
  }

  // Generate deterministic ID based on content
  const idParts = [
    'secret',
    data.file || 'unknown',
    lineStart || '0',
    data.type || data.secret_type || 'unknown',
  ].join('-').replace(/[^a-zA-Z0-9-]/g, '_');
  const id = idParts;

  return {
    id,
    type: 'secret',
    explanation: data.explanation || '',
    formattedCode: data.formatted_code || '',
    file: data.file,
    lineStart,
    lineEnd,
    severity: (data.sev || data.severity || 'HIGH').toUpperCase(),

    // Secret-specific fields
    fixType: data.fix_type,
    recommendation: data.recommendation,
    secretType: data.type || data.secret_type,
    category: data.category || 'Hardcoded Secret',

    // Keep raw data for debugging
    raw: data,
  };
}

/**
 * Parse all vulnerabilities and secrets from scan data
 * @param vulnerabilities - Array of TOON formatted vulnerability strings
 * @param secrets - Array of TOON formatted secret strings
 * @returns Combined array of ParsedVulnerability objects
 */
export function parseAllFindings(
  vulnerabilities: string[],
  secrets: string[]
): ParsedVulnerability[] {
  const parsedVulns = vulnerabilities
    .filter((v) => v && v.trim())
    .map((v) => {
      try {
        return parseVulnerability(v);
      } catch (error) {
        console.warn('Failed to parse vulnerability:', v, error);
        return null;
      }
    })
    .filter((v): v is ParsedVulnerability => v !== null);

  const parsedSecrets = secrets
    .filter((s) => s && s.trim())
    .map((s) => {
      try {
        return parseSecret(s);
      } catch (error) {
        console.warn('Failed to parse secret:', s, error);
        return null;
      }
    })
    .filter((s): s is ParsedVulnerability => s !== null);

  return [...parsedVulns, ...parsedSecrets];
}

/**
 * Group vulnerabilities by file path
 * @param vulnerabilities - Array of ParsedVulnerability objects
 * @returns Map of file path to vulnerabilities
 */
export function groupVulnerabilitiesByFile(
  vulnerabilities: ParsedVulnerability[]
): Map<string, ParsedVulnerability[]> {
  const fileMap = new Map<string, ParsedVulnerability[]>();

  vulnerabilities.forEach((vuln) => {
    const filePath = vuln.file || 'unknown';
    if (!fileMap.has(filePath)) {
      fileMap.set(filePath, []);
    }
    fileMap.get(filePath)!.push(vuln);
  });

  // Sort vulnerabilities within each file by line number
  fileMap.forEach((vulns) => {
    vulns.sort((a, b) => {
      const lineA = a.lineStart || 0;
      const lineB = b.lineStart || 0;
      return lineA - lineB;
    });
  });

  return fileMap;
}

/**
 * Get vulnerability at a specific line number
 * @param vulnerabilities - Array of ParsedVulnerability objects
 * @param lineNumber - Line number to check
 * @returns Vulnerability at that line, or undefined
 */
export function getVulnerabilityAtLine(
  vulnerabilities: ParsedVulnerability[],
  lineNumber: number
): ParsedVulnerability | undefined {
  return vulnerabilities.find((vuln) => {
    if (!vuln.lineStart) return false;
    const start = vuln.lineStart;
    const end = vuln.lineEnd || start;
    return lineNumber >= start && lineNumber <= end;
  });
}
