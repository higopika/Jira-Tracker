# -----------------------------------------------------------------------------
# WHAT THIS FILE IS FOR
# -----------------------------------------------------------------------------
# This file holds the exact instructions sent to the model every time
# someone calls POST /api/refine. It's just one piece of text, kept in its
# own file so it's easy to find and change without touching endpoint code.
#
# WHAT'S DEFINED HERE
#   - NARRATIVE_REFINEMENT_SYSTEM_PROMPT: a single text value with the
#     instructions.
#
# WHO CALLS THIS FILE
#   - app/routers/narrative.py imports this text and sends it to the model
#     together with the user's brain dump.

# WHAT IS NARRATIVE_REFINEMENT_SYSTEM_PROMPT

# It's a string, specifically a module-level constant built from 
# several string literals that Python automatically joins into one.

# A few details worth noting:

# The ALL_CAPS name (NARRATIVE_REFINEMENT_SYSTEM_PROMPT) is a 
# Python convention meaning "treat this as a constant, don't "
# "change it after it's set." Python doesn't actually enforce '
# 'that, it's just a signal to anyone reading the code.
# 
# The parentheses around the whole thing aren't a tuple. 
# There are no commas between the strings, so Python just 
# sees several string literals sitting next to each other 
# and silently joins them into one single string. This is 
# called implicit string concatenation, a common way to split 
# one long string across multiple lines for readability.
# 
# It's a module-level variable, meaning it's created once, 
# when this file is first imported (by narrative.py), and 
# that one value is reused every time, not recreated per request.
# 
# So functionally, 
# it's equivalent to writing one long single-line string, 
# just formatted to be readable.
# -----------------------------------------------------------------------------
NARRATIVE_REFINEMENT_SYSTEM_PROMPT = (
    "You are a bug report formatter for a software defect tracker. Given a "
    "raw, unstructured bug observation from a user, produce a structured bug "
    "report. Respond with JSON only, matching exactly this schema: "
    '{"title": string, "steps_to_reproduce": [string], "expected_result": '
    'string, "actual_result": string, "environment_context": string}. Do not '
    "invent details that are not present in the input. If information for a "
    "field is missing, use an empty string or empty array."
)
