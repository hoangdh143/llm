#!/bin/bash

# Check if llm is installed
if ! command -v llm &> /dev/null; then
  echo "Error: llm is not installed."
  exit 1
fi

# Check if lp (CUPS print command) is installed
if ! command -v lp &> /dev/null; then
  echo "Error: CUPS (lp) is not installed."
  exit 1
fi

# Check required commands
for cmd in llm pandoc lp; do
    if ! command -v $cmd &> /dev/null; then
        echo "Error: '$cmd' is not installed."
        exit 1
    fi
done

# Prompt user for input query to llm
# read -rp "Enter your LLM prompt: " PROMPT
PROMPT=${1:-"Explain the quadratic formula in LaTeX format only."}

# Run llm and capture output
OUTPUT=$(llm -m anthropic/claude-sonnet-4-0 "$PROMPT")

# Create temporary files
MD_FILE=$(mktemp /tmp/llm_output_XXXX.md)
PDF_FILE="${MD_FILE%.md}.pdf"

# Write to markdown file
echo "$OUTPUT" > "$MD_FILE"

# Convert to PDF using pandoc (supports LaTeX math)
pandoc "$MD_FILE" -o "$PDF_FILE" --pdf-engine=pdflatex -V geometry:margin=2cm \
  -H <(echo '\usepackage[utf8]{inputenc}') \
  -H <(echo '\usepackage[T1]{fontenc}') \
  -H <(echo '\usepackage{tipa}') \
  -H <(echo '\DeclareUnicodeCharacter{02D0}{\textlengthmark}')
#-V header-includes="\\usepackage{amsmath,amssymb}\\documentclass{article}\\usepackage[utf8]{inputenc}\\usepackage[T1]{fontenc}\\usepackage{tipa}"

# Print the file using CUPS
lp -d Brother_HL-B2180DW -o media=A4 -o sides=two-sided-long-edge "$PDF_FILE"

# Clean up
rm "$MD_FILE" "$PDF_FILE"
