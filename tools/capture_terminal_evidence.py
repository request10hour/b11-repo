from pathlib import Path
import subprocess
import textwrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "evidence"
SCREENSHOT_DIR = ROOT / "screenshots"
EVIDENCE_DIR.mkdir(exist_ok=True)
SCREENSHOT_DIR.mkdir(exist_ok=True)


GROUPS = [
    (
        "01_ssh_config_check",
        [
            (
                "orb -m ubuntu-b11 sudo awk '/^(Port|PermitRootLogin)/ {print FILENAME \":\" FNR \":\" $0}' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/99-b11-hardening.conf",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "awk",
                    "/^(Port|PermitRootLogin)/ {print FILENAME \":\" FNR \":\" $0}",
                    "/etc/ssh/sshd_config",
                    "/etc/ssh/sshd_config.d/99-b11-hardening.conf",
                ],
            ),
            (
                "orb -m ubuntu-b11 bash -lc \"sudo sshd -T | grep -E '^(port|permitrootlogin) '\"",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "bash",
                    "-lc",
                    "sudo sshd -T | grep -E '^(port|permitrootlogin) '",
                ],
            ),
        ],
    ),
    (
        "02_ssh_port_listen_check",
        [
            (
                "orb -m ubuntu-b11 systemctl is-active ssh.service",
                ["orb", "-m", "ubuntu-b11", "systemctl", "is-active", "ssh.service"],
            ),
            (
                "orb -m ubuntu-b11 systemctl is-enabled ssh.service",
                ["orb", "-m", "ubuntu-b11", "systemctl", "is-enabled", "ssh.service"],
            ),
            (
                "orb -m ubuntu-b11 sudo ss -tulnp",
                ["orb", "-m", "ubuntu-b11", "sudo", "ss", "-tulnp"],
            ),
        ],
    ),
    (
        "03_ufw_firewall_status_check",
        [
            (
                "orb -m ubuntu-b11 sudo ufw status verbose",
                ["orb", "-m", "ubuntu-b11", "sudo", "ufw", "status", "verbose"],
            ),
            (
                "orb -m ubuntu-b11 sudo ufw status numbered",
                ["orb", "-m", "ubuntu-b11", "sudo", "ufw", "status", "numbered"],
            ),
        ],
    ),
    (
        "04_user_accounts_check",
        [
            (
                "orb -m ubuntu-b11 id agent-admin",
                ["orb", "-m", "ubuntu-b11", "id", "agent-admin"],
            ),
            (
                "orb -m ubuntu-b11 id agent-dev",
                ["orb", "-m", "ubuntu-b11", "id", "agent-dev"],
            ),
            (
                "orb -m ubuntu-b11 id agent-test",
                ["orb", "-m", "ubuntu-b11", "id", "agent-test"],
            ),
            (
                "orb -m ubuntu-b11 getent passwd agent-admin agent-dev agent-test",
                ["orb", "-m", "ubuntu-b11", "getent", "passwd", "agent-admin", "agent-dev", "agent-test"],
            ),
            (
                "orb -m ubuntu-b11 ls -ld /home/agent-admin /home/agent-dev /home/agent-test",
                ["orb", "-m", "ubuntu-b11", "ls", "-ld", "/home/agent-admin", "/home/agent-dev", "/home/agent-test"],
            ),
        ],
    ),
    (
        "05_user_groups_check",
        [
            (
                "orb -m ubuntu-b11 getent group agent-common agent-core",
                ["orb", "-m", "ubuntu-b11", "getent", "group", "agent-common", "agent-core"],
            ),
            (
                "orb -m ubuntu-b11 id agent-admin",
                ["orb", "-m", "ubuntu-b11", "id", "agent-admin"],
            ),
            (
                "orb -m ubuntu-b11 id agent-dev",
                ["orb", "-m", "ubuntu-b11", "id", "agent-dev"],
            ),
            (
                "orb -m ubuntu-b11 id agent-test",
                ["orb", "-m", "ubuntu-b11", "id", "agent-test"],
            ),
        ],
    ),
]


def run_command(command: list[str]) -> str:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    output = result.stdout
    if result.stderr:
        output += result.stderr
    if result.returncode != 0:
        output += f"\n[exit code: {result.returncode}]\n"
    return output.rstrip()


def command_to_text(display: str) -> str:
    return "$ " + display


def render_terminal(text: str, path: Path) -> None:
    font_candidates = [
        "/System/Library/Fonts/Menlo.ttc",
        "/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
    ]
    font = None
    for candidate in font_candidates:
        try:
            font = ImageFont.truetype(candidate, 18)
            break
        except OSError:
            pass
    if font is None:
        font = ImageFont.load_default()

    wrapped_lines = []
    for line in text.splitlines():
        if len(line) <= 118:
            wrapped_lines.append(line)
        else:
            wrapped_lines.extend(textwrap.wrap(line, width=118, subsequent_indent="  "))

    line_height = 24
    padding_x = 28
    padding_y = 28
    title_h = 34
    width = 1320
    height = padding_y * 2 + title_h + line_height * len(wrapped_lines)

    image = Image.new("RGB", (width, height), "#111827")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=16, fill="#111827")
    draw.ellipse((24, 18, 38, 32), fill="#ff5f56")
    draw.ellipse((46, 18, 60, 32), fill="#ffbd2e")
    draw.ellipse((68, 18, 82, 32), fill="#27c93f")

    y = padding_y + title_h
    for line in wrapped_lines:
        color = "#e5e7eb"
        if line.startswith("$ "):
            color = "#93c5fd"
        elif "20022" in line or "PermitRootLogin no" in line or "permitrootlogin no" in line:
            color = "#bbf7d0"
        draw.text((padding_x, y), line, font=font, fill=color)
        y += line_height

    image.save(path)


for name, commands in GROUPS:
    blocks = []
    for display, command in commands:
        blocks.append(command_to_text(display))
        blocks.append(run_command(command))
        blocks.append("")
    transcript = "\n".join(blocks).strip() + "\n"
    (EVIDENCE_DIR / f"{name}.txt").write_text(transcript)
    render_terminal(transcript, SCREENSHOT_DIR / f"{name}.png")
