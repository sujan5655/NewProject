from django.core.validators import RegexValidator
phone_regex = RegexValidator(
    regex=r'^(?:\+?977[- ]?)?(?:9[78]\d{8}|0\d{2}[- ]?\d{6}|01[- ]?\d{7})$',
    message="Phone number must be a valid Nepali mobile (10 digits starting with 97/98) or landline number. Country code (+977) is optional."
)