import re
from typing import List

def is_heading(line: str) -> bool:
    line = line.strip()
    if not line:
        return False

    if len(line) > 80:
        return False

    # ALL CAPS headings
    if line.isupper():
        return True

    # Numbered headings (e.g. 14.1, 2.3.1)
    if re.match(r'^\d+(\.\d+)*\s+', line):
        return True

    # Title Case headings
    if line.istitle() and not line.endswith('.'):
        return True

    return False


def break_at_sentence_boundary(text: str, max_len: int) -> tuple[str, str]:
    """Break text at sentence boundary closest to max_len"""
    if len(text) <= max_len:
        return text, ""
    
    # Try to find sentence ending near max_len
    search_start = max_len - 200
    search_end = max_len + 200
    
    for i in range(min(search_end, len(text)), max(search_start, 0), -1):
        if text[i] in '.!?':
            return text[:i+1].strip(), text[i+1:].strip()
    
    # If no sentence boundary found, break at word boundary
    for i in range(max_len, max(0, max_len - 100), -1):
        if text[i] == ' ':
            return text[:i].strip(), text[i:].strip()
    
    # Last resort: break at max_len
    return text[:max_len].strip(), text[max_len:].strip()


def semantic_chunk(text: str, max_chars: int = 6000) -> List[str]:
    lines = text.split('\n')
    chunks = []

    current_chunk = ""
    current_heading = ""
    pending_line = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if is_heading(line):
            # Finish current chunk before starting new one
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            current_heading = line
            current_chunk = f"{line}\n"
            pending_line = ""
        else:
            # Process pending line first (from previous long line)
            if pending_line:
                line = pending_line + " " + line
                pending_line = ""
            
            # Check if adding this line would exceed max_chars
            potential_chunk = current_chunk + line + " "
            
            if len(potential_chunk) > max_chars and current_chunk:
                # Finish current chunk
                chunks.append(current_chunk.strip())
                current_chunk = current_heading + "\n"
            
            # Handle very long lines
            if len(line) > max_chars:
                # Break the long line at sentence boundary
                break_point = max_chars - len(current_chunk) - 100
                if break_point > 0:
                    first_part, remaining_part = break_at_sentence_boundary(line, break_point)
                    current_chunk += first_part + " "
                    chunks.append(current_chunk.strip())
                    current_chunk = current_heading + "\n"
                    pending_line = remaining_part
                else:
                    # Line is too long even for empty chunk, just break it
                    first_part, remaining_part = break_at_sentence_boundary(line, max_chars)
                    current_chunk += first_part + " "
                    chunks.append(current_chunk.strip())
                    current_chunk = current_heading + "\n"
                    pending_line = remaining_part
            else:
                # Normal case: add line to current chunk
                current_chunk += line + " "
                
                # If chunk is getting full, check if we should break here
                if len(current_chunk) >= max_chars - 500:  # Leave some buffer
                    # Look for a good break point in the current chunk
                    break_point = len(current_chunk)
                    for i in range(len(current_chunk) - 100, len(current_chunk)):
                        if current_chunk[i] in '.!?':
                            break_point = i + 1
                            break
                    
                    if break_point < len(current_chunk):
                        chunks.append(current_chunk[:break_point].strip())
                        current_chunk = current_heading + "\n" + current_chunk[break_point:].strip()
                        if not current_chunk.strip() == current_heading:
                            current_chunk += " "

    # Add final chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    # Handle any pending line
    if pending_line:
        chunks.append((current_heading + " " + pending_line).strip())

    return [chunk for chunk in chunks if chunk.strip()]
