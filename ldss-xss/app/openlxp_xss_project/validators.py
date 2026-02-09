from django.core.exceptions import ValidationError

class MaximumLengthValidator:

    def __init__(self, max_length=20):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
            raise ValidationError(f"This password is too long, it must contain at most {self.max_length} characters.")

        return
