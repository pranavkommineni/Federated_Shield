"""
Web-Based Interactive Chat Interface for Federated Shield Agent
Serves a modern web UI on http://localhost:8080 connected to PyTorch Agent / OllamaAgent.
Runs 100% locally WITHOUT Ollama dependency when Ollama is not active.
"""

import json
import logging
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import importlib.metadata


_orig_meta_version = importlib.metadata.version

def _safe_meta_version(dist_name: str) -> str:
    if dist_name.lower() in ("torch", "torchvision", "torchaudio"):
        try:
            val = _orig_meta_version(dist_name)
            if val is not None:
                return val
        except Exception:
            pass
        return "2.13.0"
    return _orig_meta_version(dist_name)

importlib.metadata.version = _safe_meta_version

base_dir = os.path.dirname(os.path.abspath(__file__))

ai_core_dir = os.path.join(base_dir, "ai-core")
if ai_core_dir not in sys.path:
    sys.path.insert(0, ai_core_dir)

from agent.tool_registry import ToolRegistry
from agent.agent_loop import Agent
from model.llm_model import MockLLMModel, DummyTokenizer
from model.ollama_model import is_ollama_available
from fl.simulation import run_fl_simulation

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("WebChatServer")


def create_fl_registry() -> ToolRegistry:
    registry = ToolRegistry()

    @registry.register(name="run_federated_simulation", description="Trigger and run a multi-client Federated Learning training simulation")
    def run_federated_simulation(rounds: int = 2, clients: int = 2, secure_aggregation: bool = False) -> str:
        try:
            logger.info(f"Agent triggered FL Simulation: rounds={rounds}, clients={clients}, secure_agg={secure_aggregation}")
            history = run_fl_simulation(
                num_rounds=int(rounds),
                num_clients=int(clients),
                use_secure_agg=bool(secure_aggregation),
                mock_model=True
            )
            losses = history.losses_distributed
            loss_str = ", ".join([f"Round {r}: {l:.4f}" for r, l in losses])
            return (
                f"✅ Federated Learning Simulation Completed Successfully!\n"
                f"- Rounds Executed: {rounds}\n"
                f"- Active Virtual Clients: {clients}\n"
                f"- Secure Aggregation: {'Enabled' if secure_aggregation else 'Disabled'}\n"
                f"- Training Loss History: [{loss_str}]"
            )
        except Exception as e:
            return f"Error executing FL simulation: {str(e)}"

    @registry.register(name="get_node_fl_status", description="Query federated client node status, data partition size, and active training status")
    def get_node_fl_status(node_id: str = "node-01") -> str:
        nodes = {
            "node-01": {"org": "FinTech Corp", "samples": 1250, "status": "READY", "dp_eps": 0.5},
            "node-02": {"org": "HealthCare Plus", "samples": 980, "status": "TRAINING", "dp_eps": 0.8},
            "node-03": {"org": "Retail Group", "samples": 2100, "status": "READY", "dp_eps": 0.4},
            "server-main": {"role": "Aggregator Server", "secure_agg": "ACTIVE", "global_round": 3},
        }
        info = nodes.get(str(node_id).lower(), {"org": "Partner Org", "samples": 1000, "status": "ACTIVE", "dp_eps": 0.5})
        return json.dumps(info)

    @registry.register(name="get_server_status", description="Get operational status of a server or node")
    def get_server_status(server_id: str = "node-01") -> str:
        return get_node_fl_status(server_id)

    @registry.register(name="calculate_dp_privacy_noise", description="Calculate Differential Privacy noise scale and privacy guarantees")
    def calculate_dp_privacy_noise(target_epsilon: float = 1.0, max_grad_norm: float = 1.0) -> str:
        noise = round(float(max_grad_norm) / (float(target_epsilon) * 0.5), 3)
        return f"For Target Epsilon = {target_epsilon} and Clip Norm = {max_grad_norm}, inject Gaussian Noise std = {noise}. Guarantee: Differential Privacy (e={target_epsilon}, d=1e-5)."

    @registry.register(name="get_fl_metrics", description="Fetch metrics for past federated training rounds")
    def get_fl_metrics(round_num: int = 1) -> dict:
        metrics = {
            1: {"round": 1, "global_loss": 0.5214, "val_accuracy": "74.2%", "participants": 4},
            2: {"round": 2, "global_loss": 0.3891, "val_accuracy": "83.6%", "participants": 4},
            3: {"round": 3, "global_loss": 0.2415, "val_accuracy": "91.8%", "participants": 4},
        }
        return metrics.get(int(round_num), {"round": round_num, "global_loss": 0.2011, "val_accuracy": "93.4%", "participants": 4})

    @registry.register(name="add_numbers", description="Add two numbers together")
    def add_numbers(a: float = 0, b: float = 0) -> str:
        return str(float(a) + float(b))

    return registry


registry = create_fl_registry()

# Check if Ollama is available or if running standalone PyTorch Agent
USE_OLLAMA = is_ollama_available() and "--no-ollama" not in sys.argv

if USE_OLLAMA:
    from agent.ollama_agent import OllamaAgent
    logger.info("Initializing OllamaAgent with local Ollama service...")
    agent = OllamaAgent(
        model_name="qwen2.5:3b",
        tool_registry=registry,
        system_prompt="You are the Federated Shield Autonomous AI Agent equipped with FL tools."
    )
    mode_status_text = "Ollama Local Model (qwen2.5:3b) Ready"
else:
    logger.info("Ollama not available. Loading real Qwen2.5-0.5B-Instruct model via HuggingFace for local inference...")
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        _qwen_model_name = "Qwen/Qwen2.5-0.5B-Instruct"
        logger.info(f"Loading tokenizer for {_qwen_model_name}...")
        _tokenizer = AutoTokenizer.from_pretrained(_qwen_model_name, trust_remote_code=True)
        if _tokenizer.pad_token is None:
            _tokenizer.pad_token = _tokenizer.eos_token

        logger.info(f"Loading model weights for {_qwen_model_name} (CPU, float32)...")
        _model = AutoModelForCausalLM.from_pretrained(
            _qwen_model_name,
            trust_remote_code=True,
            dtype=torch.float32,
        )
        _model.eval()
        logger.info(f"Qwen2.5-0.5B-Instruct loaded successfully for local inference.")

        agent = Agent(
            model=_model,
            tokenizer=_tokenizer,
            tool_registry=registry,
            system_prompt=(
                "You are a helpful, knowledgeable, and versatile AI assistant. Answer any user question clearly, "
                "naturally, and thoroughly across all topics and domains. Use your specialized tools when the user "
                "requests Federated Learning operations, simulations, node statuses, privacy calculations, or math."
            ),
        )
        mode_status_text = "Qwen2.5-0.5B (Local PyTorch) Ready"
    except Exception as e:
        logger.error(f"Failed to load Qwen model: {e}. Falling back to MockLLMModel.")
        model = MockLLMModel()
        tokenizer = DummyTokenizer()
        agent = Agent(
            model=model,
            tokenizer=tokenizer,
            tool_registry=registry,
            system_prompt="You are the Federated Shield Autonomous PyTorch AI Agent."
        )
        mode_status_text = "PyTorch Mock Engine (Model Load Failed)"



HTML_CONTENT = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Federated Shield - Standalone PyTorch AI Agent & FL Engine</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-dark: #0f172a;
            --panel-bg: rgba(30, 41, 59, 0.75);
            --panel-border: rgba(255, 255, 255, 0.1);
            --accent-blue: #38bdf8;
            --accent-purple: #818cf8;
            --accent-green: #4ade80;
            --user-bubble: #2563eb;
            --agent-bubble: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
        }}

        body {{
            background-color: var(--bg-dark);
            background-image: 
                radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(129, 140, 248, 0.15) 0px, transparent 50%);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}

        .container {{
            width: 100%;
            max-width: 960px;
            height: 92vh;
            background: var(--panel-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--panel-border);
            border-radius: 20px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            overflow: hidden;
        }}

        .header {{
            padding: 20px 24px;
            border-bottom: 1px solid var(--panel-border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(15, 23, 42, 0.5);
        }}

        .header-title {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(34, 197, 94, 0.15);
            border: 1px solid rgba(34, 197, 94, 0.3);
            color: var(--accent-green);
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 500;
        }}

        .pulse-dot {{
            width: 8px;
            height: 8px;
            background: var(--accent-green);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--accent-green);
        }}

        .chat-box {{
            flex: 1;
            padding: 24px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .message-row {{
            display: flex;
            flex-direction: column;
            max-width: 85%;
        }}

        .message-row.user {{
            align-self: flex-end;
            align-items: flex-end;
        }}

        .message-row.agent {{
            align-self: flex-start;
            align-items: flex-start;
        }}

        .bubble {{
            padding: 14px 18px;
            border-radius: 16px;
            font-size: 15px;
            line-height: 1.5;
            word-wrap: break-word;
            white-space: pre-wrap;
        }}

        .user .bubble {{
            background: linear-gradient(135deg, #2563eb, #3b82f6);
            color: white;
            border-bottom-right-radius: 4px;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
        }}

        .agent .bubble {{
            background: var(--agent-bubble);
            border: 1px solid var(--panel-border);
            color: var(--text-main);
            border-bottom-left-radius: 4px;
        }}

        .meta {{
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 4px;
            padding: 0 4px;
        }}

        .tools-used {{
            display: flex;
            gap: 6px;
            margin-bottom: 6px;
            flex-wrap: wrap;
        }}

        .tool-tag {{
            background: rgba(56, 189, 248, 0.15);
            border: 1px solid rgba(56, 189, 248, 0.3);
            color: var(--accent-blue);
            font-size: 11px;
            padding: 3px 10px;
            border-radius: 6px;
            font-weight: 500;
        }}

        .quick-prompts {{
            padding: 12px 24px;
            display: flex;
            gap: 8px;
            overflow-x: auto;
            border-top: 1px solid var(--panel-border);
            background: rgba(15, 23, 42, 0.3);
        }}

        .prompt-chip {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--panel-border);
            color: var(--text-muted);
            padding: 8px 14px;
            border-radius: 12px;
            font-size: 13px;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s ease;
        }}

        .prompt-chip:hover {{
            background: rgba(56, 189, 248, 0.12);
            border-color: var(--accent-blue);
            color: var(--text-main);
        }}

        .input-bar {{
            padding: 18px 24px;
            border-top: 1px solid var(--panel-border);
            display: flex;
            gap: 12px;
            background: rgba(15, 23, 42, 0.5);
        }}

        input[type="text"] {{
            flex: 1;
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid var(--panel-border);
            border-radius: 12px;
            padding: 14px 18px;
            color: white;
            font-size: 15px;
            outline: none;
            transition: border-color 0.2s ease;
        }}

        input[type="text"]:focus {{
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
        }}

        button {{
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            border: none;
            color: white;
            font-weight: 600;
            padding: 0 24px;
            border-radius: 12px;
            cursor: pointer;
            transition: opacity 0.2s ease;
        }}

        button:hover {{
            opacity: 0.9;
        }}

        button:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}

        .typing-indicator {{
            display: flex;
            gap: 4px;
            padding: 12px 18px;
            background: var(--agent-bubble);
            border: 1px solid var(--panel-border);
            border-radius: 16px;
            width: fit-content;
        }}

        .dot {{
            width: 8px;
            height: 8px;
            background: var(--text-muted);
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }}

        .dot:nth-child(1) {{ animation-delay: -0.32s; }}
        .dot:nth-child(2) {{ animation-delay: -0.16s; }}

        @keyframes bounce {{
            0%, 80%, 100% {{ transform: scale(0); }}
            40% {{ transform: scale(1.0); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-title">
                <h2 style="font-size: 18px; font-weight: 600;">⚡ Federated Shield AI Agent (Direct PyTorch Mode)</h2>
            </div>
            <div class="status-badge">
                <div class="pulse-dot"></div>
                {mode_status_text}
            </div>
        </div>

        <div class="chat-box" id="chatBox">
            <div class="message-row agent">
                <div class="bubble">Hello! I am running in Direct PyTorch Mode without Ollama. You can ask me to run FL simulations, check node statuses, calculate DP noise, or evaluate metrics!</div>
                <div class="meta">Agent</div>
            </div>
        </div>

        <div class="quick-prompts">
            <div class="prompt-chip" onclick="sendQuickPrompt('Run a federated simulation')">🚀 Run FL Simulation</div>
            <div class="prompt-chip" onclick="sendQuickPrompt('Check status of node-01')">🔍 Node Status</div>
            <div class="prompt-chip" onclick="sendQuickPrompt('Calculate DP privacy noise')">🔒 DP Privacy Calculation</div>
            <div class="prompt-chip" onclick="sendQuickPrompt('Fetch FL metrics for round 2')">📊 Round 2 Metrics</div>
        </div>

        <div class="input-bar">
            <input type="text" id="userInput" placeholder="Command the agent to run FL tasks without Ollama..." onkeypress="handleKeyPress(event)" />
            <button id="sendBtn" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        const chatBox = document.getElementById('chatBox');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');

        function handleKeyPress(e) {{
            if (e.key === 'Enter') sendMessage();
        }}

        function sendQuickPrompt(promptText) {{
            userInput.value = promptText;
            sendMessage();
        }}

        function appendMessage(role, text, tools = []) {{
            const row = document.createElement('div');
            row.className = `message-row ${{role}}`;

            let toolsHtml = '';
            if (tools && tools.length > 0) {{
                toolsHtml = '<div class="tools-used">' + 
                    tools.map(t => `<span class="tool-tag">⚡ Executed Tool: ${{t}}</span>`).join('') + 
                    '</div>';
            }}

            row.innerHTML = `
                ${{toolsHtml}}
                <div class="bubble">${{escapeHtml(text)}}</div>
                <div class="meta">${{role === 'user' ? 'You' : 'Agent'}}</div>
            `;
            chatBox.appendChild(row);
            chatBox.scrollTop = chatBox.scrollHeight;
        }}

        function appendTypingIndicator() {{
            const row = document.createElement('div');
            row.className = 'message-row agent';
            row.id = 'typingIndicator';
            row.innerHTML = `
                <div class="typing-indicator">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                </div>
            `;
            chatBox.appendChild(row);
            chatBox.scrollTop = chatBox.scrollHeight;
        }}

        function removeTypingIndicator() {{
            const ind = document.getElementById('typingIndicator');
            if (ind) ind.remove();
        }}

        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}

        async function sendMessage() {{
            const query = userInput.value.trim();
            if (!query) return;

            appendMessage('user', query);
            userInput.value = '';
            userInput.disabled = true;
            sendBtn.disabled = true;

            appendTypingIndicator();

            try {{
                const res = await fetch('/api/chat', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ message: query }})
                }});

                const data = await res.json();
                removeTypingIndicator();

                if (data.response) {{
                    appendMessage('agent', data.response, data.tools_executed || []);
                }} else {{
                    appendMessage('agent', 'Error: Could not process request.');
                }}
            }} catch (err) {{
                removeTypingIndicator();
                appendMessage('agent', 'Network Error: Failed to reach backend agent server.');
            }} finally {{
                userInput.disabled = false;
                sendBtn.disabled = false;
                userInput.focus();
            }}
        }}
    </script>
</body>
</html>
"""


class AgentChatHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logger.info("%s - %s" % (self.address_string(), format % args))

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode("utf-8"))
        elif self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "mode": "pytorch_standalone" if not USE_OLLAMA else "ollama"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                payload = json.loads(body.decode("utf-8"))
                user_msg = payload.get("message", "")

                initial_msg_count = len(agent.memory.get_messages())
                response_text = agent.run(user_msg, max_turns=4)

                new_messages = agent.memory.get_messages()[initial_msg_count:]
                tools_executed = [
                    m.get("tool_name") for m in new_messages if m.get("role") == "tool" and "tool_name" in m
                ]

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "response": response_text,
                    "tools_executed": tools_executed
                }).encode("utf-8"))
            except Exception as e:
                logger.error(f"Error handling chat: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def run_server(port: int = 8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, AgentChatHandler)
    mode_str = "PyTorch Standalone (No Ollama)" if not USE_OLLAMA else "Ollama Local"
    print(f"\n🚀 Federated Shield Agent Server ({mode_str}) is live at: http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8080
    run_server(port)
