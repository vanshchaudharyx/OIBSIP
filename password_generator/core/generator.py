"""
Core password generation engine with security rules.
"""
import secrets
import string
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PasswordConfig:
    length: int = 16
    use_uppercase: bool = True
    use_lowercase: bool = True
    use_digits: bool = True
    use_symbols: bool = True
    exclude_chars: str = ""
    exclude_ambiguous: bool = False  # Excludes l, 1, O, 0, I
    min_uppercase: int = 1
    min_lowercase: int = 1
    min_digits: int = 1
    min_symbols: int = 1

    AMBIGUOUS_CHARS: str = field(default="lL1Oo0I", init=False, repr=False)

    def __post_init__(self):
        object.__setattr__(self, 'AMBIGUOUS_CHARS', 'lL1Oo0I')


class PasswordStrength:
    VERY_WEAK = 0
    WEAK = 1
    FAIR = 2
    STRONG = 3
    VERY_STRONG = 4

    LABELS = {
        0: ("Very Weak", "#FF3B30"),
        1: ("Weak", "#FF9500"),
        2: ("Fair", "#FFCC00"),
        3: ("Strong", "#34C759"),
        4: ("Very Strong", "#30D158"),
    }


class PasswordGenerator:
    def __init__(self, config: Optional[PasswordConfig] = None):
        self.config = config or PasswordConfig()

    def _build_charset(self) -> str:
        charset = ""
        if self.config.use_uppercase:
            charset += string.ascii_uppercase
        if self.config.use_lowercase:
            charset += string.ascii_lowercase
        if self.config.use_digits:
            charset += string.digits
        if self.config.use_symbols:
            charset += string.punctuation

        # Remove excluded characters
        for ch in self.config.exclude_chars:
            charset = charset.replace(ch, "")

        # Remove ambiguous characters if requested
        if self.config.exclude_ambiguous:
            for ch in self.config.AMBIGUOUS_CHARS:
                charset = charset.replace(ch, "")

        return charset

    def _build_mandatory_chars(self) -> list:
        """Ensure minimum character type requirements are met."""
        mandatory = []

        def filtered(chars):
            result = chars
            for ch in self.config.exclude_chars:
                result = result.replace(ch, "")
            if self.config.exclude_ambiguous:
                for ch in self.config.AMBIGUOUS_CHARS:
                    result = result.replace(ch, "")
            return result

        if self.config.use_uppercase:
            pool = filtered(string.ascii_uppercase)
            for _ in range(self.config.min_uppercase):
                if pool:
                    mandatory.append(secrets.choice(pool))

        if self.config.use_lowercase:
            pool = filtered(string.ascii_lowercase)
            for _ in range(self.config.min_lowercase):
                if pool:
                    mandatory.append(secrets.choice(pool))

        if self.config.use_digits:
            pool = filtered(string.digits)
            for _ in range(self.config.min_digits):
                if pool:
                    mandatory.append(secrets.choice(pool))

        if self.config.use_symbols:
            pool = filtered(string.punctuation)
            for _ in range(self.config.min_symbols):
                if pool:
                    mandatory.append(secrets.choice(pool))

        return mandatory

    def generate(self) -> str:
        """Generate a cryptographically secure password."""
        if not any([
            self.config.use_uppercase,
            self.config.use_lowercase,
            self.config.use_digits,
            self.config.use_symbols,
        ]):
            raise ValueError("At least one character type must be selected.")

        charset = self._build_charset()
        if not charset:
            raise ValueError("Character set is empty after exclusions.")

        mandatory = self._build_mandatory_chars()
        remaining_length = max(0, self.config.length - len(mandatory))

        password_chars = mandatory + [secrets.choice(charset) for _ in range(remaining_length)]

        # Shuffle using secrets for cryptographic security
        for i in range(len(password_chars) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

        return "".join(password_chars)

    def generate_batch(self, count: int = 5) -> list[str]:
        """Generate multiple passwords at once."""
        return [self.generate() for _ in range(count)]

    @staticmethod
    def evaluate_strength(password: str) -> tuple[int, str, str]:
        """
        Returns (score 0-4, label, hex color).
        """
        score = 0
        feedback = []

        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1

        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_symbol = bool(re.search(r'[^a-zA-Z0-9]', password))

        variety = sum([has_upper, has_lower, has_digit, has_symbol])
        score += variety

        # Cap at max
        score = min(score, 4)

        # Generate feedback
        if not has_upper:
            feedback.append("Add uppercase letters")
        if not has_lower:
            feedback.append("Add lowercase letters")
        if not has_digit:
            feedback.append("Add numbers")
        if not has_symbol:
            feedback.append("Add symbols")
        if len(password) < 12:
            feedback.append("Use 12+ characters")

        label, color = PasswordStrength.LABELS[score]
        tip = " · ".join(feedback) if feedback else "Excellent password!"
        return score, label, color, tip