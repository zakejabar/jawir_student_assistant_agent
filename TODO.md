# File Processing Limits Fix - TODO

## Problem
Large files are processed too quickly with minimal content extraction due to restrictive limits.

## Goals
- Remove all artificial limits on file processing
- Process entire files completely
- Maintain performance while maximizing content extraction

## Changes to Make

### 1. Increase Chunk Size Limit
- [ ] Update `semantic_chunker.py` to use larger chunk sizes (6000+ chars)
- [ ] Make chunking adaptive based on content structure

### 2. Remove Entity/Relationship Limits  
- [ ] Remove 20-entity limit in `kg_extractor.py`
- [ ] Remove 30-relationship limit in `kg_extractor.py`
- [ ] Allow unlimited extraction per chunk

### 3. Improve Text Processing
- [ ] Reduce aggressive text filtering in `upload_handler.py`
- [ ] Preserve more content during text cleaning
- [ ] Better handling of various document formats

### 4. Enhanced Progress Tracking
- [ ] Add better logging for large file processing
- [ ] Show detailed processing progress to user

## Status
- [x] Identified root causes
- [x] Implementing chunk size increases (800 → 6000 chars)
- [x] Removing entity/relationship limits (20 entities, 30 relationships → unlimited)
- [x] Improving text cleaning (3 chars → 2 chars threshold)
- [ ] Testing with large files

## Changes Made
✅ **semantic_chunker.py**: Increased `max_chars` from 800 to 6000
✅ **kg_extractor.py**: Removed `[:20]` and `[:30]` limits on entities and relationships
✅ **upload_handler.py**: Reduced text filtering threshold from 3 to 2 characters
