
import fitz  # PyMuPDF:
from openai import OpenAI
import re
import argparse

# Set your OpenAI API key
# openai.api_key = os.getenv("OPENAI_API_KEY")  # or hardcode for testing

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
#model = "qwen3-8b-mlx"
#model = "qwen/qwen3-8b"
model = "nvidia_llama-3.1-nemotron-nano-4b-v1.1"
definition_store = {}

def get_important_terms(text, max_tokens=500):
    prompt = (
        "Extract the most important terms or key phrases from the following text. "
        "Only return a plain comma-separated list of terms without further explanation:\n\n"
        f"{text}"
    )

    response = client.chat.completions.create(
        model=model,  # or "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt}],
        #temperature=0.3,
        #max_tokens=max_tokens
    )
    terms = response.choices[0].message.content
    cleaned_text = re.sub(r"<think>.*?</think>", "", str(terms), flags=re.DOTALL)
    print(cleaned_text)
    return [term.strip() for term in cleaned_text.split(',') if term.strip()]

def get_summary(text, max_tokens=500):
    prompt = (
        "Summarize this text:\n\n"
        f"{text}"
    )

    response = client.chat.completions.create(
        model=model,  # or "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt}],
        #temperature=0.3,
        #max_tokens=max_tokens
    )
    terms = response.choices[0].message.content
    cleaned_text = re.sub(r"<think>.*?</think>", "", terms, flags=re.DOTALL)
    return cleaned_text

def get_definition(term, context, max_tokens=1000):
    if definition_store.get(term): return definition_store[term]
    prompt = (
        "Provided context: \n\n"
        f"{context}"
        "Explain this in details:\n\n"
        f"{term}"
    )

    response = client.chat.completions.create(
        model=model,  # or "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt}],
        #temperature=0.3,
        #max_tokens=max_tokens
    )
    terms = response.choices[0].message.content
    cleaned_text = re.sub(r"<think>.*?</think>", "", terms, flags=re.DOTALL)
    definition_store[term] = cleaned_text
    return cleaned_text

def highlight_terms_on_page(page, terms, context):
    for term in terms:
        if not term:
            continue
        instances = page.search_for(term)
        for inst in instances:
            highlight = page.add_highlight_annot(inst)
            highlight.set_info({
                "title": term,
                "content": get_definition(term, context)
            })
            highlight.update()

def min_ignore_none(*args):
    # Filter out None values
    filtered = [x for x in args if x is not None]
    if not filtered:
        return 0  # All values were None
    return min(filtered)

def max_ignore_none(*args):
    # Filter out None values
    filtered = [x for x in args if x is not None]
    if not filtered:
        return 0  # All values were None
    return max(filtered)

def highlight_pdf_page_by_page(input_path, output_path, max_pages=None, from_page=None, to_page=None):
    doc = fitz.open(input_path)
    end = min_ignore_none(max_pages, len(doc), to_page + 1 if to_page is not None else to_page)
    start = max_ignore_none(0, from_page)
    
    for i in range(start, end, 1):
        page = doc[i]
        text = page.get_text()
        if not text.strip():
            continue

        print(f"🔍 Analyzing Page {i+1-start}/{end-start}...")
        try:
            context = get_summary(text)
            terms = get_important_terms(text)
            print(f"📌 Page {i+1} terms: {terms}")
            highlight_terms_on_page(page, terms, context)
        except Exception as e:
            print(f"⚠️ Error processing page {i+1}: {e}")

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    print(f"✅ Highlighted PDF saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Highlight important terms in a PDF (page by page) using OpenAI.")
    parser.add_argument("input_pdf", help="Path to input PDF file")
    parser.add_argument("output_pdf", help="Path to output PDF file")
    parser.add_argument("--max-pages", type=int, default=None, help="Maximum number of pages to process")
    parser.add_argument("--from-page", type=int, default=None, help="From page index")
    parser.add_argument("--to-page", type=int, default=None, help="To page index")
    
    args = parser.parse_args()

    highlight_pdf_page_by_page(args.input_pdf, args.output_pdf, max_pages=args.max_pages, from_page=args.from_page, to_page=args.to_page)

if __name__ == "__main__":
    main()
