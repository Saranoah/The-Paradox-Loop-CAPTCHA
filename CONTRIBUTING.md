# Contributing to Paradox-Loop CAPTCHA

> **"I don't like CAPTCHA. You probably don't either. Let's fix that together."**

Welcome, fellow CAPTCHA-hater. If you've ever rage-clicked through blurry traffic lights or questioned your humanity while identifying fire hydrants, you're in the right place.

This project exists because one person got fed up and decided to build something better. Now it's your turn to make it even better.

---

## 🎯 The Mission

**We're not just building a CAPTCHA alternative.**

We're building:
- 🎨 **Art** - Making security beautiful, not frustrating
- 🧠 **Psychology** - Understanding how humans think differently from bots
- 🛡️ **Defense** - Staying one step ahead of adversaries
- 🌍 **Accessibility** - Technology that works for everyone
- 🔥 **Rebellion** - Against annoying, privacy-invading, user-hostile CAPTCHAs

**Our Philosophy:**
```
Traditional CAPTCHA: "Prove you're human by acting like a computer"
Paradox-Loop: "Prove you're human by being wonderfully, imperfectly human"
```

---

## 🚀 Quick Start for Contributors

### I Want To...

#### 🐛 **Report a Bug**
```bash
# 1. Check if it's already reported
https://github.com/Saranoah/The-Paradox-Loop-CAPTCHA/issues

# 2. Create new issue with:
- What you expected
- What actually happened  
- Steps to reproduce
- Your environment (OS, browser, Python version)
- Screenshots/logs if possible

# 3. Use the bug template
Click "New Issue" → "Bug Report"
```

#### 💡 **Suggest a Feature**
```bash
# Before suggesting, ask yourself:
□ Does this align with our philosophy?
□ Will it improve UX or security?
□ Is it feasible to implement?
□ Have I searched existing issues?

# Then create a Feature Request with:
- Problem it solves
- Proposed solution
- Alternative approaches considered
- Mockups/examples if relevant
```

#### 🎨 **Design a New Puzzle**
```bash
# The fun part! Create puzzles that:
✅ Humans solve intuitively (3-10 seconds)
✅ Bots struggle with (paradox, context, ambiguity)
✅ Work across cultures
✅ Are accessible

# Submit via Pull Request:
1. Add puzzle to puzzles/custom/
2. Include test cases
3. Explain the logic
4. Show bot resistance data
```

#### 💻 **Write Code**
```bash
# 1. Fork the repository
git clone https://github.com/YOUR-USERNAME/The-Paradox-Loop-CAPTCHA.git

# 2. Create a branch
git checkout -b feature/amazing-feature

# 3. Make your changes
# (See coding standards below)

# 4. Test thoroughly
python -m pytest tests/
python -m pytest tests/test_your_feature.py

# 5. Commit with clear message
git commit -m "feat: add quantum entanglement puzzle"

# 6. Push and create PR
git push origin feature/amazing-feature
```

#### 📖 **Improve Documentation**
```bash
# Documentation is CODE
# Bad docs = broken feature

Areas needing love:
- API reference (docs/api.md)
- Integration guides (docs/integrations/)
- Puzzle design guide (docs/puzzles.md)
- Accessibility guidelines (docs/accessibility.md)

# Even fixing typos matters!
```

#### 🧪 **Test and Break Things**
```bash
# We WANT you to break this

Try to bypass the system with:
- GPT-4/Claude API attacks
- Selenium/Puppeteer automation
- Behavioral spoofing
- Timing attacks
- Novel attack vectors

# Report findings responsibly:
security@[project-domain] or private issue
```

---

## 🎨 Puzzle Design Guidelines

### What Makes a Great Puzzle?

#### The Golden Rules

**1. Human Time: 3-10 seconds**
```
✅ "Check this box if you're NOT human"
   Human: 3 seconds (understands paradox)
   Bot: Fails (follows literal instruction)

❌ "Solve this Sudoku puzzle"
   Human: 5 minutes
   Bot: 2 seconds
   (Wrong direction!)
```

**2. Bot Confusion: Multiple failure modes**
```python
# Good puzzle has several ways bots fail:

def analyze_puzzle_quality(puzzle):
    failure_modes = {
        'literal_interpretation': True,  # Bot follows rules literally
        'no_training_data': True,        # Can't learn from existing data
        'context_dependent': True,       # Requires understanding prior state
        'cultural_knowledge': False,     # Avoid this - not universal
        'temporal_logic': True           # Time-based reasoning
    }
    
    score = sum(failure_modes.values())
    return score >= 3  # Need at least 3 failure modes
```

**3. Cultural Neutrality**
```
✅ Universal concepts:
   - Basic logic (true/false)
   - Numbers (1, 2, 3)
   - Simple shapes (circle, square)
   - Common emotions (happy, sad)

❌ Culture-specific:
   - Idioms ("raining cats and dogs")
   - Historical references (requires specific education)
   - Local knowledge (US states, European capitals)
   - Religious concepts
```

**4. Accessibility First**
```
Every puzzle must work with:
✅ Keyboard only (no mouse required)
✅ Screen readers (ARIA labels)
✅ High contrast mode
✅ Cognitive disabilities (clear, simple language)
✅ Non-native speakers (avoid complex vocabulary)
```

### Puzzle Categories

#### Category 1: Logical Paradoxes
```javascript
// Template
{
  type: 'paradox',
  question: '[Statement that creates logical loop]',
  correctAnswer: '[Any valid response]',
  
  examples: [
    "Check this box if you are NOT human",
    "Select the option that makes this question invalid",
    "Click 'No' if you want to continue"
  ]
}

// Why it works:
// - Bots parse literally → fail
// - Humans understand meta-context → succeed
```

#### Category 2: Context-Dependent Logic
```javascript
// Template
{
  type: 'contextual',
  question: '[Depends on previous answer]',
  context: '[History of user responses]',
  
  example: {
    q1: "What's your favorite color?",
    q2: "Click the button that is NOT [previous answer]",
    // If user said "blue" → show blue, red, green
    // Correct answer: red or green (NOT blue)
  }
}

// Why it works:
// - Requires maintaining state
// - Bots struggle with pronoun resolution
// - Can't be pre-trained (infinite combinations)
```

#### Category 3: Temporal Impossibilities
```javascript
// Template
{
  type: 'temporal',
  question: '[References time/sequence]',
  timing: '[Requires specific timing]',
  
  examples: [
    "Click this button BEFORE reading this text",
    "Wait exactly 3 seconds, then click",
    "Click when the timer shows a prime number"
  ]
}

// Why it works:
// - Bots click instantly or with perfect timing
// - Humans have natural variation (2.8-3.4s for "3 seconds")
// - Temporal reasoning requires understanding causality
```

#### Category 4: Semantic Ambiguity
```javascript
// Template
{
  type: 'semantic',
  question: '[Multiple valid interpretations]',
  answers: '[All are "correct"]',
  
  examples: [
    "Type a word you don't know",
    "What's the opposite of a mirror?",
    "Select the color that isn't here"
  ]
}

// Why it works:
// - No training data exists (subjective/undefined)
// - Bots search for "correct" answer → freeze
// - Humans create/guess freely
```

#### Category 5: Meta-Cognitive Challenges
```javascript
// Template  
{
  type: 'meta',
  question: '[Self-referential or recursive]',
  logic: '[Requires theory of mind]',
  
  examples: [
    "Is this question a question?",
    "How many words are in this sentence?",
    "This statement is false. True or false?"
  ]
}

// Why it works:
// - Requires self-awareness
// - Creates infinite loops in deterministic systems
// - Humans handle with humor/intuition
```

### Puzzle Submission Template

```python
# puzzles/custom/my_amazing_puzzle.py

from paradox_captcha.core import BasePuzzle

class MyAmazingPuzzle(BasePuzzle):
    """
    Brief description of the puzzle concept.
    
    Human solve time: X seconds (based on Y tests)
    Bot resistance: Z% (tested against GPT-4, Selenium)
    Accessibility: [WCAG level]
    """
    
    def __init__(self):
        self.category = 'paradox'  # or temporal, semantic, etc.
        self.difficulty = 'medium'  # easy, medium, hard
        self.language = 'en'        # ISO 639-1 code
        
    def generate(self, context=None):
        """Generate puzzle instance."""
        return {
            'question': 'Your puzzle text here',
            'options': ['Option A', 'Option B'],
            'correct_answer': self.validate_response,
            'metadata': {
                'expected_time': 5,  # seconds
                'accept_any': False  # or True for open-ended
            }
        }
    
    def validate_response(self, response, metadata):
        """
        Validate user response.
        
        Args:
            response: User's answer
            metadata: {response_time, mouse_entropy, etc}
        
        Returns:
            bool: True if human-like, False if bot-like
        """
        # Your validation logic
        if metadata['response_time'] < 500:  # Too fast
            return False
        
        # Add your specific checks
        return True
    
    def get_bot_resistance_score(self):
        """
        Self-assessment of bot resistance.
        
        Returns:
            dict: Breakdown of resistance factors
        """
        return {
            'gpt4_tested': True,
            'gpt4_success_rate': 0.35,  # 35% bypass rate
            'selenium_tested': True,
            'selenium_success_rate': 0.10,
            'training_data_exists': False,
            'cultural_neutral': True,
            'accessibility_score': 9.5
        }

# Tests (required!)
def test_my_amazing_puzzle():
    puzzle = MyAmazingPuzzle()
    
    # Test generation
    instance = puzzle.generate()
    assert 'question' in instance
    assert len(instance['options']) > 0
    
    # Test human-like response
    human_response = {
        'answer': 'Option A',
        'metadata': {
            'response_time': 3500,
            'mouse_entropy': 45
        }
    }
    assert puzzle.validate_response(human_response['answer'], 
                                    human_response['metadata']) == True
    
    # Test bot-like response
    bot_response = {
        'answer': 'Option A',
        'metadata': {
            'response_time': 100,  # Too fast
            'mouse_entropy': 0     # No movement
        }
    }
    assert puzzle.validate_response(bot_response['answer'],
                                    bot_response['metadata']) == False

if __name__ == '__main__':
    test_my_amazing_puzzle()
    print("✅ All tests passed!")
```

---

## 💻 Code Contribution Standards

### Setting Up Development Environment

```bash
# 1. Fork and clone
git clone https://github.com/YOUR-USERNAME/The-Paradox-Loop-CAPTCHA.git
cd The-Paradox-Loop-CAPTCHA

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dev dependencies
pip install -r requirements-dev.txt

# 4. Install pre-commit hooks
pre-commit install

# 5. Run tests to verify setup
python -m pytest tests/
```

### Code Style

**We use:**
- **Black** for Python formatting
- **ESLint** for JavaScript
- **Prettier** for everything else

```bash
# Format before committing
black src/
eslint js/ --fix
prettier --write "**/*.{json,md,yml}"

# Or use pre-commit (automatic)
pre-commit run --all-files
```

### Python Standards

```python
# Good code example

def validate_puzzle_response(
    response: str,
    metadata: Dict[str, Any],
    context: Optional[PuzzleContext] = None
) -> ValidationResult:
    """
    Validate a user's puzzle response.
    
    This function checks both the answer correctness and behavioral
    signals to distinguish humans from bots.
    
    Args:
        response: The user's submitted answer
        metadata: Behavioral data (timing, mouse movement, etc.)
        context: Optional puzzle history for contextual validation
        
    Returns:
        ValidationResult containing:
            - is_valid: bool
            - confidence: float (0.0-1.0)
            - flags: List[str] of suspicious signals
            
    Example:
        >>> result = validate_puzzle_response(
        ...     response="blue",
        ...     metadata={"response_time": 3500, "mouse_entropy": 45}
        ... )
        >>> result.is_valid
        True
        >>> result.confidence
        0.87
        
    Note:
        Response time thresholds are calibrated for desktop users.
        Mobile users may need adjusted thresholds (see config).
    """
    # Validation logic here
    pass


# Common patterns to follow

class PuzzleBase:
    """Base class for all puzzles."""
    
    def __init__(self):
        self.id: str = generate_unique_id()
        self.created_at: datetime = datetime.utcnow()
        self._cache: Optional[Dict] = None
    
    def generate(self) -> PuzzleInstance:
        """Generate a puzzle instance. Must be implemented by subclass."""
        raise NotImplementedError
    
    def validate(self, response: str) -> bool:
        """Validate response. Must be implemented by subclass."""
        raise NotImplementedError


# Type hints are required
def process_response(data: Dict[str, Any]) -> Tuple[bool, float]:
    result: bool = False
    confidence: float = 0.0
    return result, confidence


# Use descriptive variable names
def calculate_human_likelihood(behavioral_data: BehavioralMetrics) -> float:
    """
    Good: calculate_human_likelihood
    Bad: calc_hl, process_data, do_thing
    """
    pass
```

### JavaScript Standards

```javascript
// Good code example

/**
 * Track user behavior during puzzle interaction.
 * 
 * @param {HTMLElement} container - The puzzle container element
 * @param {Object} options - Configuration options
 * @param {number} options.sampleRate - Mouse tracking sample rate (ms)
 * @returns {BehaviorTracker} Tracker instance
 * 
 * @example
 * const tracker = trackBehavior(puzzleElement, { sampleRate: 50 });
 * tracker.start();
 * // ... later ...
 * const data = tracker.getData();
 */
function trackBehavior(container, options = {}) {
    const { sampleRate = 50 } = options;
    
    const data = {
        mouseMovements: [],
        clickTimestamps: [],
        scrollEvents: [],
    };
    
    // Clear, single-responsibility functions
    const recordMouseMovement = (event) => {
        data.mouseMovements.push({
            x: event.clientX,
            y: event.clientY,
            timestamp: Date.now(),
        });
    };
    
    return {
        start: () => {
            container.addEventListener('mousemove', recordMouseMovement);
        },
        stop: () => {
            container.removeEventListener('mousemove', recordMouseMovement);
        },
        getData: () => ({ ...data }),
    };
}

// Use modern JavaScript
const humanBehavior = {
    // Use object destructuring
    analyzePattern: ({ movements, clicks, timing }) => {
        // Use arrow functions
        const entropy = movements.reduce((sum, m) => sum + m.variance, 0);
        
        // Use template literals
        console.log(`Calculated entropy: ${entropy}`);
        
        // Use spread operator
        return { ...timing, entropy, isHuman: entropy > 20 };
    },
};

// Avoid var, use const/let
const immutableData = Object.freeze({ config: 'value' });
let mutableCounter = 0;
```

### Testing Requirements

**All contributions MUST include tests.**

```python
# test_my_feature.py

import pytest
from paradox_captcha import MyFeature

class TestMyFeature:
    """Test suite for MyFeature."""
    
    def test_basic_functionality(self):
        """Test that basic feature works."""
        feature = MyFeature()
        result = feature.process()
        assert result is not None
    
    def test_edge_case_empty_input(self):
        """Test handling of empty input."""
        feature = MyFeature()
        result = feature.process("")
        assert result == feature.DEFAULT_VALUE
    
    def test_bot_detection(self):
        """Test that bots are detected."""
        feature = MyFeature()
        bot_data = {'response_time': 50, 'mouse_entropy': 0}
        assert feature.is_bot(bot_data) == True
    
    def test_human_detection(self):
        """Test that humans pass."""
        feature = MyFeature()
        human_data = {'response_time': 3500, 'mouse_entropy': 45}
        assert feature.is_bot(human_data) == False
    
    @pytest.mark.parametrize("input,expected", [
        ("normal", True),
        ("edge_case", True),
        ("invalid", False),
    ])
    def test_multiple_inputs(self, input, expected):
        """Test various inputs."""
        feature = MyFeature()
        assert feature.validate(input) == expected


# Run tests
# pytest tests/ -v --cov=src/
```

### Commit Message Standards

We use [Conventional Commits](https://www.conventionalcommits.org/).

```bash
# Format: <type>(<scope>): <subject>

# Types:
feat:     New feature
fix:      Bug fix
docs:     Documentation only
style:    Code style (formatting, semicolons, etc.)
refactor: Code change that neither fixes a bug nor adds a feature
perf:     Performance improvement
test:     Adding missing tests
chore:    Maintenance (dependencies, build, etc.)

# Examples:
git commit -m "feat(puzzles): add quantum entanglement puzzle"
git commit -m "fix(validation): correct false positive rate"
git commit -m "docs(api): update authentication examples"
git commit -m "test(behavioral): add mouse tracking tests"

# Bad examples:
git commit -m "update stuff"
git commit -m "fix bug"
git commit -m "changes"
```

### Pull Request Process

```markdown
## PR Title
feat(scope): brief description

## Description
Clear explanation of what this PR does and why.

## Changes
- Added X feature
- Fixed Y bug
- Improved Z performance

## Testing
- [ ] All tests pass (`pytest tests/`)
- [ ] Added new tests for new features
- [ ] Manually tested in browser
- [ ] Tested with screen reader (if UI change)

## Screenshots (if applicable)
[Before/After images]

## Breaking Changes
None / [List any breaking changes]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No console errors/warnings
```

---

## 🎯 Focus Areas (Where We Need Help)

### 🔴 Critical Priority

**1. Security Research**
```
We need people to attack this system:
- GPT-4/Claude API bypass attempts
- Behavioral spoofing techniques
- Timing attack vectors
- Novel adversarial approaches

Report findings to: security@[domain]
```

**2. Accessibility**
```
Current status: Basic (7/10)
Target: WCAG 2.1 AA compliance (9/10)

Needed:
- Screen reader optimization
- Keyboard navigation improvements
- High contrast mode
- Cognitive load testing
```

**3. Performance Optimization**
```
Current: ~100 concurrent users tested
Target: 10,000+ concurrent users

Bottlenecks:
- Session state management
- Real-time behavioral analysis
- Puzzle generation caching
```

### 🟡 High Priority

**4. Puzzle Variety**
```
Current: ~10 puzzle types
Target: 50+ puzzle types

We need creative minds to design:
- New paradox categories
- Cross-cultural puzzles
- Time-based challenges
- Meta-cognitive tests
```

**5. Integration Libraries**
```
Needed:
- WordPress plugin
- Django package
- Rails gem
- React component
- Vue component
- Angular module
```

**6. Documentation**
```
Areas needing love:
- API reference
- Integration guides
- Deployment tutorials
- Video walkthroughs
- Translated docs (ES, FR, DE, JA)
```

### 🟢 Medium Priority

**7. Analytics Dashboard**
```
Build internal analytics to track:
- Success/failure rates
- Solve times by puzzle type
- Bot detection accuracy
- False positive trends
```

**8. Mobile Optimization**
```
Current solve times 2x desktop
Need to optimize for:
- Touch interfaces
- Small screens
- Slower processors
```

**9. Internationalization**
```
Translate puzzles to:
- Spanish
- French
- German
- Japanese
- Mandarin
```

---

## 🏆 Recognition & Rewards

### Hall of Fame

We celebrate contributors with:

**🥇 Gold Tier (Major contributions)**
- Name in README.md
- Custom "Core Contributor" badge
- Early access to new features
- Direct input on roadmap
- Free hosted plan (when available)

**🥈 Silver Tier (Significant contributions)**
- Name in CONTRIBUTORS.md
- "Valued Contributor" badge
- Recognition in release notes

**🥉 Bronze Tier (Any contribution)**
- Name in git history (forever!)
- Our eternal gratitude
- Warm fuzzy feeling

### What Counts as Major?

```
Major contributions:
- 10+ merged PRs
- New puzzle category with 5+ puzzles
- Complete integration library
- Security research with findings
- Accessibility improvements
- Performance optimization (>2x improvement)

Significant contributions:
- 3-9 merged PRs
- 3+ new puzzles
- Comprehensive documentation
- Bug fixes with tests

Any contribution:
- 1+ merged PR
- Bug report with reproduction
- Documentation fix
- Translation help
```

---

## 🤝 Community Guidelines

### Code of Conduct

**TL;DR: Don't be a jerk.**

**We value:**
- 🤝 Respect and kindness
- 💡 Constructive feedback
- 🌍 Diversity and inclusion
- 📚 Learning and teaching
- 🎉 Celebrating each other's wins

**We don't tolerate:**
- 🚫 Harassment or discrimination
- 🚫 Trolling or personal attacks
- 🚫 Spam or self-promotion
- 🚫 Sharing others' private info
- 🚫 Unethical or illegal activities

**Consequences:**
1. First offense: Warning
2. Second offense: Temporary ban
3. Third offense: Permanent ban

Report issues to: conduct@[domain]

### Getting Help

**Stuck? We've all been there.**

```bash
# Try these resources:

1. Documentation
   docs/README.md

2. Existing issues
   https://github.com/Saranoah/The-Paradox-Loop-CAPTCHA/issues

3. Discussions
   https://github.com/Saranoah/The-Paradox-Loop-CAPTCHA/discussions

4. Discord (coming soon)
   [Link when available]

5. Email
   help@[domain]
   (Response time: 24-48 hours)
```

### Communication Channels

**GitHub Issues: For bugs and features**
- Be specific
- Include reproduction steps
- Add relevant labels
- Search before posting

**GitHub Discussions: For questions and ideas**
- General questions
- Design discussions
- Feature brainstorming
- Show and tell

**Discord: For real-time chat (coming)**
- Quick questions
- Community hangout
- Pair programming
- Brainstorming sessions

**Email: For private matters**
- Security issues
- Code of conduct violations
- Partnership inquiries
- Press/media

---

## 🎓 Learning Resources

### New to Open Source?

**Start here:**
- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [First Contributions](https://github.com/firstcontributions/first-contributions)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

### New to Security?

**Learn the basics:**
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Web Security Academy](https://portswigger.net/web-security)
- [Cryptography 101](https://www.crypto101.io/)

### New to Accessibility?

**Essential reading:**
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [A11y Project](https://www.a11yproject.com/)
- [WebAIM](https://webaim.org/)

---

## 🚀 Your First Contribution

### Good First Issues

We label issues perfect for beginners:
- `good-first-issue` - Easy wins
- `help-wanted` - We need your skills
- `documentation` - Improve docs
- `beginner-friendly` - Learn as you go

**Find them here:**
[Good First Issues](https://github.com/Saranoah/The-Paradox-Loop-CAPTCHA/labels/good-first-issue)

### 5-Minute Contributions

**Yes, 5 minutes matters!**

```bash
# Quick wins:
- Fix a typo in docs
- Add a code comment
- Improve error message
- Add example to README
- Report a bug
- Star the repo (seriously, it helps!)
```

### Your First PR Checklist

```markdown
- [ ] Forked the repository
- [ ] Created a branch
- [ ] Made changes
- [ ] Added tests
- [ ] Run tests locally (`pytest tests/`)
- [ ] Formatted code (`black src/`)
- [ ] Written clear commit message
- [ ] Pushed to your fork
- [ ] Created pull request
- [ ] Filled out PR template
- [ ] Linked related issue
- [ ] Waited patiently for review 😊
```

---

## 💬 Questions?

**We're here to help.**

Remember:
- 🤔 No question is stupid
- 📚 We were all beginners once
- 🎓 Asking questions helps everyone learn
- 💡 Your fresh perspective is valuable

**Ways to ask:**
1. [Open a discussion](https://github.com/Saranoah/The-Paradox-Loop-CAPTCHA/discussions)


---

## 🎉 Thank You!

Every contribution, no matter how small, makes this project better.

You're not just writing code or docs. You're:
- 🛡️ Making the web more secure
- 🌍 Improving accessibility
- 🔒 Protecting privacy
- 😊 Reducing user frustration
- 🚀 Pushing technology forward

**Together, we're building something that doesn't suck.**

Welcome to the team. Let's make CAPTCHAs great (or at least tolerable).

---

<div align="center">

**[💻 Start Contributing](https://github.com/Saranoah/The-Paradox-Loop-CAPTCHA/issues)** • **[📖 Read Docs](docs/)** • **[💬 Join Discussion](https://github.com/Saranoah/The-Paradox-Loop-CAPTCHA/discussions)**

*"The best time to fix CAPTCHAs was 10 years ago. The second best time is now."*

</div>
