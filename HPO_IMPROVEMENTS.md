# Improvements to Encourage Hyperparameter Tuning in AIDE Agent

## Summary of Changes

The agent currently tracks HPO scores but doesn't strongly encourage hyperparameter tuning. Here are the key improvements:

## 1. **Add HPO-aware prompts in `_improve()` method** (lines 441-453)
   - Check parent node's HPO score
   - Add explicit guidance based on HPO status:
     - Score 0: CRITICAL message requiring HPO
     - Score 1: IMPORTANT message to improve HPO
     - Score 2: Suggestion to expand to score 3

## 2. **Add HPO-aware prompts in `_debug()` method** (lines 484-499)
   - Check parent node's HPO score
   - If score is 0, add message to include HPO after fixing bug

## 3. **Update `_draft()` method** (lines 395-405)
   - After 30% of steps, encourage basic HPO in initial drafts
   - Remove "without hyper-parameter optimization" restriction

## 4. **Strengthen HPO rewards** (lines 681-713)
   - Increase penalties for no HPO (especially late in search)
   - Increase rewards for good HPO
   - Adjust thresholds: 30%, 60% instead of 40%, 70%

## 5. **Include HPO in journal summary** (journal.py line 203)
   - Add HPO score and status to memory so agent sees it in context

## 6. **Increase HPO bias in node selection** (journal.py line 192)
   - Increase from 0.1 to 0.2 for stronger preference for HPO nodes
   - Increase scale factor from 0.01 to 0.02

## Implementation Notes

All changes maintain backward compatibility. The HPO scoring already exists and works correctly - these changes just make the agent more likely to actually implement HPO by:
1. Explicitly telling it when HPO is missing
2. Rewarding HPO more strongly
3. Making HPO status visible in memory
