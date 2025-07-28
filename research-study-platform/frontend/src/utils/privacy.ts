/**
 * Privacy utilities for anonymizing participant data in the admin dashboard
 */

/**
 * Generate a consistent hash for sensitive data
 * This provides a consistent, anonymized identifier while preserving uniqueness
 */
export const generateHash = (input: string): string => {
  // Simple hash function that generates consistent 8-character identifier
  let hash = 0;
  for (let i = 0; i < input.length; i++) {
    const char = input.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  
  // Convert to positive hex string and pad to 8 characters
  const hashStr = Math.abs(hash).toString(16).padStart(8, '0').slice(0, 8);
  return hashStr.toUpperCase();
};

/**
 * Anonymize email address - show hash instead of actual email
 */
export const anonymizeEmail = (email: string): string => {
  return `user_${generateHash(email)}`;
};

/**
 * Anonymize username - show hash instead of actual username
 */
export const anonymizeUsername = (username: string): string => {
  return `participant_${generateHash(username)}`;
};

/**
 * Get anonymized display name for participant
 * Uses participant_id if available, otherwise generates hash from username/email
 */
export const getAnonymizedDisplayName = (participant: {
  participant_id?: string;
  username?: string;
  email?: string;
}): string => {
  if (participant.participant_id) {
    return participant.participant_id;
  }
  
  const source = participant.username || participant.email || 'unknown';
  return `P_${generateHash(source)}`;
};

/**
 * Show partial hash for additional context while maintaining privacy
 */
export const getPartialHash = (input: string): string => {
  return generateHash(input).slice(0, 4);
};