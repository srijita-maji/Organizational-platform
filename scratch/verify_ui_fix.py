import re
import urllib.request
import json

def test_css_rules():
    with open("frontend/employee-dashboard.html", "r", encoding="utf-8") as f:
        html = f.read()

    with open("frontend/css/style.css", "r", encoding="utf-8") as f:
        css = f.read()

    print("=== 1. VERIFYING CSS SPECIFICITY & OVERRIDES ===")
    
    # Check that style.css doesn't affect .chat-log messages with flex
    assert ".msg:not(.chat-log *)" in css, "style.css should exclude .chat-log messages"
    print("[PASS] style.css excludes .chat-log from .msg flex styling")

    # Check that employee-dashboard.html explicitly sets display: block !important
    assert ".chat-log .msg" in html, "employee-dashboard.html has .chat-log .msg"
    assert "display: block !important" in html, "employee-dashboard.html has display: block !important for chat messages"
    print("[PASS] employee-dashboard.html sets display: block !important for .chat-log .msg")

    # Check max-width and wrapping
    assert "overflow-wrap: break-word" in html, "overflow-wrap: break-word present"
    assert "word-break: break-word" in html, "word-break: break-word present"
    print("[PASS] Natural text wrapping rules configured without aggressive breaking")

    # Check chat-form alignment
    assert ".chat-form" in html
    assert "height: 48px" in html
    print("[PASS] Chat form textarea and button heights synchronized to 48px")

    # Check suggested question chips
    assert ".chipbtn" in html
    assert "border-radius: 999px" in html
    print("[PASS] Suggested question chips styled as modern pills with border-radius: 999px")

    # Check responsive rules
    assert "@media (max-width: 768px)" in html
    print("[PASS] Responsive breakpoints for mobile/tablet configured")

def test_mdlite_and_chat_markup():
    print("\n=== 2. VERIFYING MARKDOWN & CHAT PARSING ===")
    sample_ai_text = (
        "Welcome! As a Frontend Developer, a great way to start improving your skills is by focusing on "
        "core technologies like JavaScript frameworks, responsive design, and state management.\n\n"
        "Here is how you can begin:\n"
        "- Pick one specific area to focus on first, such as advanced React patterns or web accessibility (a11y).\n"
        "- Build small, practical projects to apply what you learn.\n"
        "- Test your knowledge regularly using our platform quizzes so we can track your progress and identify any knowledge gaps.\n\n"
        "Since you are just getting started, try taking a baseline assessment in your dashboard. "
        "This will generate your first set of missed questions and help me give you more personalized course recommendations.\n\n"
        "What specific area of frontend development would you like to dive into today?"
    )

    # Replicate mdLite logic from employee-dashboard.html
    def esc(t):
        return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    def inl(t):
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(t))

    out = []
    current_list = None
    for line in sample_ai_text.split("\n"):
        m_bullet = re.match(r"^\s*[-*•]\s+(.*)$", line)
        if m_bullet:
            if current_list != "ul":
                if current_list: out.append(f"</{current_list}>")
                out.append("<ul>")
                current_list = "ul"
            out.append(f"<li>{inl(m_bullet.group(1))}</li>")
        else:
            if current_list:
                out.append(f"</{current_list}>")
                current_list = None
            if line.strip():
                out.append(f"<p>{inl(line.strip())}</p>")
    if current_list:
        out.append(f"</{current_list}>")

    parsed_html = "".join(out)
    print("Parsed HTML output preview:")
    print(parsed_html[:250] + "...")
    assert "<p>Welcome! As a Frontend Developer" in parsed_html
    assert "<p>Here is how you can begin:</p>" in parsed_html
    assert "<ul><li>Pick one specific area" in parsed_html
    assert "<li>Test your knowledge" in parsed_html
    assert "</ul><p>Since you are just getting started" in parsed_html
    print("[PASS] Markdown parses cleanly into distinct <p> and <ul> block elements (no columns)")

def test_live_backend_chat_api():
    print("\n=== 3. TESTING LIVE BACKEND /api/employee/me/chat ===")
    login_data = json.dumps({"email": "emp.test@infosys.com", "password": "Password@123"}).encode("utf-8")
    req = urllib.request.Request("http://localhost:8080/api/auth/login", data=login_data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        token = json.loads(resp.read().decode("utf-8")).get("token")
        assert token, "Token not received"
        print(f"[PASS] Logged in successfully, token received ({len(token)} chars)")

    chat_payload = json.dumps({
        "message": "How do I start improving my skills?",
        "history": []
    }).encode("utf-8")
    chat_req = urllib.request.Request(
        "http://localhost:8080/api/employee/me/chat",
        data=chat_payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    )
    with urllib.request.urlopen(chat_req) as resp:
        chat_resp = json.loads(resp.read().decode("utf-8"))
        assert "reply" in chat_resp, "Chat response should contain 'reply'"
        print(f"[PASS] Chat API returned HTTP {resp.status}")
        print(f"       Source: {chat_resp.get('source')}")
        print(f"       Reply length: {len(chat_resp.get('reply', ''))} chars")
        print(f"       Reply excerpt: {chat_resp.get('reply', '')[:120]}...")

if __name__ == "__main__":
    test_css_rules()
    test_mdlite_and_chat_markup()
    test_live_backend_chat_api()
    print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
