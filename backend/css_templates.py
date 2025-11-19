"""CSS templates for consistent styling in generated HTML."""

# Base CSS template extracted from frontend globals.css
BASE_CSS_TEMPLATE = """
<style>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap");

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "Inter", sans-serif;
  background-color: #f8fafc;
  color: #1e293b;
  line-height: 1.6;
  padding: 20px;
  min-height: 100vh;
}

/* Container for content */
.content-container {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Custom animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}

.animate-slide-up {
  animation: slideUp 0.6s ease-out;
}

/* Card-like components */
.response-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.response-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Button styles */
.btn-primary {
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-block;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-block;
}

.btn-secondary:hover {
  background: #e2e8f0;
}

/* Grid layouts */
.grid {
  display: grid;
  gap: 1rem;
}

.grid-cols-1 { grid-template-columns: repeat(1, 1fr); }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }

@media (max-width: 768px) {
  .grid-cols-2, .grid-cols-3 {
    grid-template-columns: 1fr;
  }
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #1e293b;
}

h1 { font-size: 2rem; }
h2 { font-size: 1.5rem; }
h3 { font-size: 1.25rem; }
h4 { font-size: 1.125rem; }

p {
  margin-bottom: 1rem;
  color: #475569;
}

/* Images */
img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
}

/* Lists */
ul, ol {
  margin-bottom: 1rem;
  padding-left: 1.5rem;
}

li {
  margin-bottom: 0.25rem;
  color: #475569;
}

/* Interactive elements */
input, textarea, select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-family: inherit;
  transition: all 0.2s ease;
}

input:focus, textarea:focus, select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Utility classes */
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.mb-2 { margin-bottom: 0.5rem; }
.mb-4 { margin-bottom: 1rem; }
.mb-6 { margin-bottom: 1.5rem; }

.mt-2 { margin-top: 0.5rem; }
.mt-4 { margin-top: 1rem; }
.mt-6 { margin-top: 1.5rem; }

.p-2 { padding: 0.5rem; }
.p-4 { padding: 1rem; }
.p-6 { padding: 1.5rem; }

.rounded { border-radius: 8px; }
.rounded-lg { border-radius: 12px; }

.shadow { box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.shadow-lg { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); }

.bg-gray-50 { background-color: #f8fafc; }
.bg-white { background-color: white; }
.bg-blue-50 { background-color: #eff6ff; }
.bg-blue-100 { background-color: #dbeafe; }

.text-gray-600 { color: #475569; }
.text-gray-900 { color: #1e293b; }
.text-blue-600 { color: #2563eb; }

.border { border: 1px solid #e2e8f0; }
.border-gray-200 { border-color: #e5e7eb; }

/* Responsive design */
@media (max-width: 640px) {
  body {
    padding: 10px;
  }
  
  .content-container {
    padding: 1rem;
  }
  
  h1 { font-size: 1.5rem; }
  h2 { font-size: 1.25rem; }
}
</style>
"""


def inject_css_into_html(html_content) -> str:
    """Inject consistent CSS styling into HTML content."""

    if not html_content:
        html_content = "<div>No content available</div>"

    # Check if HTML already has a head tag
    if "<head>" in html_content.lower():
        # Insert CSS after the opening head tag
        head_pos = html_content.lower().find("<head>") + 6
        styled_html = (
            html_content[:head_pos]
            + "\n"
            + BASE_CSS_TEMPLATE
            + "\n"
            + html_content[head_pos:]
        )
    elif "<html>" in html_content.lower():
        # Add head section with CSS after html tag
        html_pos = html_content.lower().find("<html>") + 6
        head_section = f"\n<head>\n{BASE_CSS_TEMPLATE}\n</head>\n"
        styled_html = html_content[:html_pos] + head_section + html_content[html_pos:]
    else:
        # Wrap content in basic HTML structure with CSS
        styled_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MultiFlex</title>
    {BASE_CSS_TEMPLATE}
</head>
<body>
    <div class="content-container animate-fade-in">
        {html_content}
    </div>
</body>
</html>"""

    return styled_html


def ensure_interactive_elements_have_ids(html_content: str) -> str:
    """Ensure interactive elements have IDs for WebSocket interaction tracking."""
    import re

    # Add IDs to buttons without them
    button_pattern = r"<button(?![^>]*\bid=)[^>]*>"
    button_count = 0

    def add_button_id(match):
        nonlocal button_count
        button_count += 1
        button_tag = match.group(0)
        # Insert id before the closing >
        return button_tag[:-1] + f' id="btn-{button_count}">'

    html_content = re.sub(button_pattern, add_button_id, html_content)

    # Add IDs to form inputs without them
    input_pattern = r"<input(?![^>]*\bid=)[^>]*>"
    input_count = 0

    def add_input_id(match):
        nonlocal input_count
        input_count += 1
        input_tag = match.group(0)
        return input_tag[:-1] + f' id="input-{input_count}">'

    html_content = re.sub(input_pattern, add_input_id, html_content)

    # Add IDs to select elements without them
    select_pattern = r"<select(?![^>]*\bid=)[^>]*>"
    select_count = 0

    def add_select_id(match):
        nonlocal select_count
        select_count += 1
        select_tag = match.group(0)
        return select_tag[:-1] + f' id="select-{select_count}">'

    html_content = re.sub(select_pattern, add_select_id, html_content)

    return html_content
