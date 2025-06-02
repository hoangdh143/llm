#!/bin/bash

# Prompt can be passed as an argument or default
export PROMPT=${1:-"Explain the quadratic formula using markdown and include math formulas in LaTeX."}

PROMT_WITH_TEMPLATE=$(envsubst < template.txt)

# Use LLM to generate output (Markdown + LaTeX)
# MARKDOWN_OUTPUT=$(llm -m anthropic/claude-sonnet-4-0 "$PROMPT")
MARKDOWN_OUTPUT=$(python3 chat_client.py "$PROMT_WITH_TEMPLATE")
CLEANED_OUTPUT=$(echo $MARKDOWN_OUTPUT | sed -E 's|<think>.*</think>||g')

# echo $MARKDOWN_OUTPUT
# echo $CLEANED_OUTPUT

# Create temp files
HTML_FILE=$(mktemp --suffix=.html)
PDF_FILE=$(mktemp --suffix=.pdf)

# SANITIZED_MD=$(echo "$MARKDOWN_OUTPUT" | sed 's/\\/\\\\/g')

# Convert markdown to HTML and embed KaTeX
cat <<EOF > "$HTML_FILE"
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Rendered Markdown and Math</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.js" integrity="sha384-cMkvdD8LoxVzGF/RPUKAcvmm49FQ0oxwDF3BGKtDXcEc+T1b2N+teh/OJfpU0jr6" crossorigin="anonymous"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/contrib/auto-render.min.js" integrity="sha384-hCXGrW6PitJEwbkoStFjeJxv+fSOOQKOPbJxSfM6G5sWZjAyWhXiTIIAmQqnlLlh" crossorigin="anonymous"></script>
  <script>
      document.addEventListener("DOMContentLoaded", function() {
          renderMathInElement(document.body, {
            // customised options
            // auto-render specific keys, e.g.:
            delimiters: [
                {left: '$$', right: '$$', display: true},
                {left: '$', right: '$', display: false},
                {left: '\\(', right: '\\)', display: false},
                {left: '\\[', right: '\\]', display: true}
            ],
            // rendering keys, e.g.:
            throwOnError : false
          });
      });
  </script>
  <style>
    body { font-family: sans-serif; padding: 2em; font-size: 1.2em; line-height: 1.6; zoom: 0.5}
    code { background: #f4f4f4; padding: 0.2em 0.4em; border-radius: 4px; }
    pre { background: #f4f4f4; padding: 1em; overflow-x: auto; border-radius: 6px; }
  </style>
</head>
<body>
EOF

# Convert markdown to HTML and insert
# echo "$MARKDOWN_OUTPUT" | marked >> "$HTML_FILE"
# Render Markdown to HTML
echo "$PROMPT" >> "$HTML_FILE"
echo "$CLEANED_OUTPUT" | marked --gfm --breaks >> "$HTML_FILE"

# Close HTML
echo "</body></html>" >> "$HTML_FILE"

sed -i 's/\$\$/$/g' "$HTML_FILE"

# Convert to PDF using wkhtmltopdf
google-chrome-stable --headless --disable-gpu --print-to-pdf="$PDF_FILE" --print-to-pdf-no-header --virtual-time-budget=2000 --force-device-scale-factor=0.5 "$HTML_FILE"

#wkhtmltopdf "$HTML_FILE" "$PDF_FILE"

# 4. Print the PDF using CUPS
# lp -d Brother_HL-B2180DW -o media=A4 -o sides=two-sided-long-edge "$PDF_FILE"
vivaldi "$PDF_FILE"

echo "Sent to printer successfully."
