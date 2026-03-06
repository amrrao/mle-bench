# Code Changes to Improve Hyperparameter Tuning

## Summary
The agent tracks HPO scores correctly, but doesn't strongly encourage HPO. These changes add explicit prompts, stronger rewards, and better visibility.

## Changes Made (Already Applied)
✅ **journal.py line 203-213**: Added HPO score to journal summary  
✅ **journal.py line 192-199**: Increased HPO bias in node selection (0.1→0.2, 0.01→0.02)

## Changes Needed (Manual Application Required)

### 1. `_improve()` method (agent.py, lines 441-453)

**REPLACE:**
```python
                # Commented out: Hyperparameter tuning enforcement
                # "**IMPORTANT: If the previous solution does not include hyperparameter tuning, you MUST add it** (e.g., GridSearchCV, RandomizedSearchCV, Optuna, Hyperopt, or manual loops searching over ≥2 values for ≥1 hyperparameter).",
```

**WITH:**
```python
                # Check HPO status and add guidance
                parent_hpo_score = getattr(parent_node, 'hpo_score', 0)
                if parent_hpo_score == 0:
                    hpo_guideline = [
                        "**CRITICAL: The previous solution has NO hyperparameter tuning (HPO score: 0). "
                        "You MUST add hyperparameter tuning** using GridSearchCV, RandomizedSearchCV, Optuna, "
                        "Hyperopt, or manual loops searching over ≥3 values for ≥1 hyperparameter. "
                        "This is required to improve model performance."
                    ]
                elif parent_hpo_score == 1:
                    hpo_guideline = [
                        "**IMPORTANT: The previous solution has only superficial hyperparameter tuning (HPO score: 1). "
                        "You should improve it** by testing more hyperparameter values (≥5 iterations), "
                        "searching over multiple hyperparameters, or using a more systematic approach."
                    ]
                elif parent_hpo_score == 2:
                    hpo_guideline = [
                        "The previous solution has moderate hyperparameter tuning (HPO score: 2). "
                        "Consider expanding the search space or tuning additional hyperparameters to reach extensive tuning (score 3)."
                    ]
                else:
                    hpo_guideline = []
```

**AND UPDATE the list to include hpo_guideline:**
```python
            "Solution improvement sketch guideline": [
                "The solution sketch should be a brief natural language description of how the previous solution can be improved.",
                "You should be very specific and should only propose a single actionable improvement.",
                "This improvement should be atomic so that we can experimentally evaluate the effect of the proposed change.",
                "Take the Memory section into consideration when proposing the improvement.",
                *hpo_guideline,  # Add this line
                "The solution sketch should be 3-5 sentences.",
                "Don't suggest to do EDA.",
            ],
```

### 2. `_debug()` method (agent.py, lines 484-499)

**REPLACE:**
```python
        # Commented out: Hyperparameter tuning enforcement
        # # Check if the rejection was due to missing hyperparameter tuning
        # if parent_node.analysis and "missing hyperparameter tuning" in parent_node.analysis.lower():
        #     bugfix_guidelines.insert(1, 
        #         "**CRITICAL: The previous solution was rejected for missing hyperparameter tuning. You MUST add hyperparameter tuning** (e.g., GridSearchCV, RandomizedSearchCV, Optuna, Hyperopt, or manual loops searching over ≥2 values for ≥1 hyperparameter). This is required for the solution to be accepted."
        #     )
```

**WITH:**
```python
        # Check HPO status and add guidance if missing
        parent_hpo_score = getattr(parent_node, 'hpo_score', 0)
        if parent_hpo_score == 0:
            bugfix_guidelines.insert(1,
                "**IMPORTANT: The previous solution has NO hyperparameter tuning. "
                "After fixing the bug, you should also add hyperparameter tuning** "
                "(e.g., GridSearchCV, RandomizedSearchCV, Optuna, Hyperopt, or manual loops "
                "searching over ≥3 values for ≥1 hyperparameter) to improve performance."
            )
```

### 3. `_draft()` method (agent.py, line 397)

**REPLACE:**
```python
                "This first solution design should be relatively simple, without ensembling or hyper-parameter optimization.",
```

**WITH:**
```python
                "This first solution design should be relatively simple, without ensembling.",
                *([f"**Note: Since you're past the initial exploration phase, consider including basic hyperparameter tuning** (e.g., testing 3-5 values for key hyperparameters like learning_rate, n_estimators, or regularization strength) to establish a stronger baseline."] if (self.current_step / max(self.acfg.steps, 1)) > 0.3 else ["You may include basic hyperparameter tuning if appropriate."]),
```

### 4. `_get_hpo_reward()` method (agent.py, lines 689-713)

**REPLACE the entire method body:**
```python
        if progress_ratio < 0.4:  # Early search
            if hpo_score == 0:
                return -0.3
            elif hpo_score == 1:
                return -0.1
            else:
                return 0.0  # No penalty for moderate/extensive HPO early
        elif progress_ratio < 0.7:  # Mid search
            if hpo_score == 0:
                return -0.3
            elif hpo_score == 1:
                return -0.1
            elif hpo_score >= 2:
                return 0.15
            return 0.0
        else:  # Late search
            if hpo_score == 0:
                return -0.3
            elif hpo_score == 1:
                return -0.1
            elif hpo_score == 2:
                return 0.15
            elif hpo_score == 3:
                return 0.35
            return 0.0
```

**WITH:**
```python
        if progress_ratio < 0.3:  # Early search
            if hpo_score == 0:
                return -0.2  # Smaller penalty early
            elif hpo_score == 1:
                return -0.05
            elif hpo_score >= 2:
                return 0.1  # Small reward for good HPO early
            return 0.0
        elif progress_ratio < 0.6:  # Mid search
            if hpo_score == 0:
                return -0.5  # Stronger penalty
            elif hpo_score == 1:
                return -0.2
            elif hpo_score == 2:
                return 0.25
            elif hpo_score == 3:
                return 0.4
            return 0.0
        else:  # Late search
            if hpo_score == 0:
                return -0.8  # Very strong penalty for no HPO late
            elif hpo_score == 1:
                return -0.3
            elif hpo_score == 2:
                return 0.3
            elif hpo_score == 3:
                return 0.6  # Strong reward for extensive HPO
            return 0.0
```

**AND UPDATE the docstring:**
```python
        """
        Get HPO reward based on score and search progress (curriculum-style).
        
        Early search (0-30%): allow no/weak HPO, only apply small penalties
        Mid search (30-60%): reward score ≥2, stronger penalties for no HPO
        Late search (60-100%): strongly reward score ≥2, very strong penalties for no HPO
        """
```

## Expected Impact

1. **Explicit HPO prompts**: Agent will see clear messages when HPO is missing
2. **Stronger rewards**: Better HPO gets more reward, especially later in search
3. **HPO visibility**: HPO scores appear in memory/journal summaries
4. **Better node selection**: Nodes with HPO are slightly preferred

These changes should significantly increase the likelihood that the agent implements hyperparameter tuning.
