# Visualization Endpoint Debug Guide

## Overview
The `/isomorphism_visualization` endpoint now includes detailed logging to help identify where requests are hanging.

## Log Output Stages

When you submit a visualization prompt, you should see logs in this order:

### 1. Request Start
```
[VISUALIZATION] Starting visualization request: create a visual graph for the isomorphisms across a mechanical spring...
[VISUALIZATION] Extracting system names from prompt...
[VISUALIZATION] Systems identified: mechanical spring system <-> electric circuit model
```

### 2. Cache Check
```
[VISUALIZATION] Checking cache...
[VISUALIZATION] Cache miss - extracting system specifications...
```
or
```
[VISUALIZATION] Checking cache...
[VISUALIZATION] Using cached data
```

### 3. System Extraction (if not cached)
```
[VISUALIZATION] System 1 extracted in X.XXs
[VISUALIZATION] System 2 extracted in X.XXs
```
**Duration**: These LLM calls typically take 10-30 seconds each

### 4. Morphism Detection (if not cached)
```
[VISUALIZATION] Detecting morphisms...
[VISUALIZATION] Morphisms detected in X.XXs (6 morphisms)
```
**Duration**: This LLM call typically takes 15-40 seconds

### 5. Rendering
```
[VISUALIZATION] Rendering visualization...
[VISUALIZATION] Visualization rendered in X.XXs (18089 chars)
```
**Duration**: Usually < 1 second (fast)

### 6. Justification Generation
```
[VISUALIZATION] Generating justification...
[VISUALIZATION] Justification generated in X.XXs
```
**Duration**: This LLM call typically takes 10-20 seconds

### 7. Success
```
[VISUALIZATION] Preparing response: 5 ISO, 1 HOMO, avg=92.17%
[VISUALIZATION] Request completed successfully!
```

## Typical Timings
- **Cold (no cache)**: 60-150 seconds total
  - System 1 extraction: 15-30s
  - System 2 extraction: 15-30s
  - Morphism detection: 20-40s
  - Justification generation: 10-20s
  - Rendering: <1s

- **Warm (with cache)**: 10-30 seconds total
  - Cache lookup: <1s
  - Justification generation: 10-20s
  - Rendering: <1s

## Troubleshooting

### If request hangs after "Starting visualization request"
- **Check**: System names extraction
- **Cause**: Invalid system names in prompt
- **Fix**: Use format: "create a visual [system1] and [system2]"

### If request hangs at "System 1 extracted" or "System 2 extracted"
- **Check**: LLM API connection
- **Cause**: Gemini API timeout or rate limiting
- **Fix**: Wait a minute and retry, or check API key

### If request hangs at "Morphisms detected"
- **Check**: LLM API connection for morphism detection
- **Cause**: Complex system morphism analysis taking very long
- **Fix**: Wait longer or check API quota

### If request hangs at "Justification generated"
- **Check**: LLM API for justification generation
- **Cause**: Complex analysis or API slowness
- **Fix**: Wait or check API status

## Expected Behavior on First Request
1. First request will show `Cache miss` and take 60-150 seconds
2. Logs will show each extraction, detection, and generation step
3. Once complete, will receive full visualization
4. Subsequent requests for same systems will use cache and be much faster (10-30s)

## Performance Optimization
- First visualization: slow (60-150s) due to LLM calls
- Subsequent visualizations of same systems: fast (10-30s) due to caching
- Database caching is stored in `morphism_cache.db`

## Expected Log Pattern
```
[VISUALIZATION] Starting visualization request: ...
[VISUALIZATION] Extracting system names from prompt...
[VISUALIZATION] Systems identified: ...
[VISUALIZATION] Checking cache...
[VISUALIZATION] Cache miss - extracting system specifications...
[VISUALIZATION] System 1 extracted in X.XXs
[VISUALIZATION] System 2 extracted in X.XXs
[VISUALIZATION] Detecting morphisms...
[VISUALIZATION] Morphisms detected in X.XXs (N morphisms)
[VISUALIZATION] Rendering visualization...
[VISUALIZATION] Visualization rendered in X.XXs (XXXXX chars)
[VISUALIZATION] Generating justification...
[VISUALIZATION] Justification generated in X.XXs
[VISUALIZATION] Preparing response: N ISO, N HOMO, avg=XX.XX%
[VISUALIZATION] Request completed successfully!
```

If logs stop at any stage, check:
1. Network connection
2. Gemini API key validity
3. API rate limits
4. Browser network tab (frontend side)
