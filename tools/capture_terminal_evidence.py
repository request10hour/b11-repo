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
                "orb -m ubuntu-b11 sudo ss -tulnp | grep sshd",
                ["orb", "-m", "ubuntu-b11", "bash", "-lc", "sudo ss -tulnp | grep sshd"],
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
    (
        "06_directory_structure_check",
        [
            (
                "orb -m ubuntu-b11 sudo bash -lc 'AGENT_HOME=/home/agent-admin/agent-app; printf \"AGENT_HOME=%s\\n\" \"$AGENT_HOME\"; ls -ld \"$AGENT_HOME\" \"$AGENT_HOME/upload_files\" \"$AGENT_HOME/api_keys\" /var/log/agent-app'",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "bash",
                    "-lc",
                    'AGENT_HOME=/home/agent-admin/agent-app; printf "AGENT_HOME=%s\\n" "$AGENT_HOME"; ls -ld "$AGENT_HOME" "$AGENT_HOME/upload_files" "$AGENT_HOME/api_keys" /var/log/agent-app',
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo find /home/agent-admin/agent-app -maxdepth 2 -type d -printf '%M %u %g %p\\n'",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "find",
                    "/home/agent-admin/agent-app",
                    "-maxdepth",
                    "2",
                    "-type",
                    "d",
                    "-printf",
                    "%M %u %g %p\\n",
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo find /var/log/agent-app -maxdepth 0 -type d -printf '%M %u %g %p\\n'",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "find",
                    "/var/log/agent-app",
                    "-maxdepth",
                    "0",
                    "-type",
                    "d",
                    "-printf",
                    "%M %u %g %p\\n",
                ],
            ),
        ],
    ),
    (
        "07_access_permission_metadata_check",
        [
            (
                "orb -m ubuntu-b11 bash -lc 'id agent-admin && id agent-dev && id agent-test'",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "bash",
                    "-lc",
                    "id agent-admin && id agent-dev && id agent-test",
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo ls -ld /home/agent-admin /home/agent-admin/agent-app /home/agent-admin/agent-app/upload_files /home/agent-admin/agent-app/api_keys /var/log/agent-app",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "ls",
                    "-ld",
                    "/home/agent-admin",
                    "/home/agent-admin/agent-app",
                    "/home/agent-admin/agent-app/upload_files",
                    "/home/agent-admin/agent-app/api_keys",
                    "/var/log/agent-app",
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo getfacl -p /home/agent-admin /home/agent-admin/agent-app /home/agent-admin/agent-app/upload_files /home/agent-admin/agent-app/api_keys /var/log/agent-app",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "getfacl",
                    "-p",
                    "/home/agent-admin",
                    "/home/agent-admin/agent-app",
                    "/home/agent-admin/agent-app/upload_files",
                    "/home/agent-admin/agent-app/api_keys",
                    "/var/log/agent-app",
                ],
            ),
        ],
    ),
    (
        "08_access_permission_write_tests",
        [
            (
                "orb -m ubuntu-b11 sudo -u agent-admin bash -lc 'touch /home/agent-admin/agent-app/upload_files/admin_upload_test && rm /home/agent-admin/agent-app/upload_files/admin_upload_test && echo \"agent-admin upload_files write: OK\"'",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "-u",
                    "agent-admin",
                    "bash",
                    "-lc",
                    'touch /home/agent-admin/agent-app/upload_files/admin_upload_test && rm /home/agent-admin/agent-app/upload_files/admin_upload_test && echo "agent-admin upload_files write: OK"',
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo -u agent-dev bash -lc 'touch /home/agent-admin/agent-app/upload_files/dev_upload_test && rm /home/agent-admin/agent-app/upload_files/dev_upload_test && echo \"agent-dev upload_files write: OK\"'",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "-u",
                    "agent-dev",
                    "bash",
                    "-lc",
                    'touch /home/agent-admin/agent-app/upload_files/dev_upload_test && rm /home/agent-admin/agent-app/upload_files/dev_upload_test && echo "agent-dev upload_files write: OK"',
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo -u agent-test bash -lc 'touch /home/agent-admin/agent-app/upload_files/test_upload_test && rm /home/agent-admin/agent-app/upload_files/test_upload_test && echo \"agent-test upload_files write: OK\"'",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "-u",
                    "agent-test",
                    "bash",
                    "-lc",
                    'touch /home/agent-admin/agent-app/upload_files/test_upload_test && rm /home/agent-admin/agent-app/upload_files/test_upload_test && echo "agent-test upload_files write: OK"',
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo -u agent-admin bash -lc 'touch /home/agent-admin/agent-app/api_keys/admin_key_test && rm /home/agent-admin/agent-app/api_keys/admin_key_test && echo \"agent-admin api_keys write: OK\"'",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "-u",
                    "agent-admin",
                    "bash",
                    "-lc",
                    'touch /home/agent-admin/agent-app/api_keys/admin_key_test && rm /home/agent-admin/agent-app/api_keys/admin_key_test && echo "agent-admin api_keys write: OK"',
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo -u agent-dev bash -lc 'touch /home/agent-admin/agent-app/api_keys/dev_key_test && rm /home/agent-admin/agent-app/api_keys/dev_key_test && echo \"agent-dev api_keys write: OK\"'",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "-u",
                    "agent-dev",
                    "bash",
                    "-lc",
                    'touch /home/agent-admin/agent-app/api_keys/dev_key_test && rm /home/agent-admin/agent-app/api_keys/dev_key_test && echo "agent-dev api_keys write: OK"',
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo -u agent-test bash -lc 'if touch /home/agent-admin/agent-app/api_keys/test_key_denied 2>/dev/null; then rm -f /home/agent-admin/agent-app/api_keys/test_key_denied; echo \"agent-test api_keys write: UNEXPECTED_OK\"; exit 1; else echo \"agent-test api_keys write: DENIED (expected)\"; fi'",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "-u",
                    "agent-test",
                    "bash",
                    "-lc",
                    'if touch /home/agent-admin/agent-app/api_keys/test_key_denied 2>/dev/null; then rm -f /home/agent-admin/agent-app/api_keys/test_key_denied; echo "agent-test api_keys write: UNEXPECTED_OK"; exit 1; else echo "agent-test api_keys write: DENIED (expected)"; fi',
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo -u agent-admin bash -lc 'touch /var/log/agent-app/admin_log_test && rm /var/log/agent-app/admin_log_test && echo \"agent-admin log write: OK\"'",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "-u",
                    "agent-admin",
                    "bash",
                    "-lc",
                    'touch /var/log/agent-app/admin_log_test && rm /var/log/agent-app/admin_log_test && echo "agent-admin log write: OK"',
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo -u agent-dev bash -lc 'touch /var/log/agent-app/dev_log_test && rm /var/log/agent-app/dev_log_test && echo \"agent-dev log write: OK\"'",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "-u",
                    "agent-dev",
                    "bash",
                    "-lc",
                    'touch /var/log/agent-app/dev_log_test && rm /var/log/agent-app/dev_log_test && echo "agent-dev log write: OK"',
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo -u agent-test bash -lc 'if touch /var/log/agent-app/test_log_denied 2>/dev/null; then rm -f /var/log/agent-app/test_log_denied; echo \"agent-test log write: UNEXPECTED_OK\"; exit 1; else echo \"agent-test log write: DENIED (expected)\"; fi'",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "-u",
                    "agent-test",
                    "bash",
                    "-lc",
                    'if touch /var/log/agent-app/test_log_denied 2>/dev/null; then rm -f /var/log/agent-app/test_log_denied; echo "agent-test log write: UNEXPECTED_OK"; exit 1; else echo "agent-test log write: DENIED (expected)"; fi',
                ],
            ),
        ],
    ),
    (
        "09_agent_environment_variables_check",
        [
            (
                "orb -m ubuntu-b11 uname -m",
                ["orb", "-m", "ubuntu-b11", "uname", "-m"],
            ),
            (
                "orb -m ubuntu-b11 python3 -m zipfile -l /Users/10hour0574/Downloads/pjt7ec757e6-0e57-48e9-9805-e1587f441508_agent-app.zip",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "python3",
                    "-m",
                    "zipfile",
                    "-l",
                    "/Users/10hour0574/Downloads/pjt7ec757e6-0e57-48e9-9805-e1587f441508_agent-app.zip",
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo cat /etc/profile.d/agent-app.sh",
                ["orb", "-m", "ubuntu-b11", "sudo", "cat", "/etc/profile.d/agent-app.sh"],
            ),
            (
                "orb -m ubuntu-b11 sudo -u agent-admin bash -lc 'printf \"AGENT_HOME=%s\\nAGENT_PORT=%s\\nAGENT_UPLOAD_DIR=%s\\nAGENT_KEY_PATH=%s\\nAGENT_LOG_DIR=%s\\n\" \"$AGENT_HOME\" \"$AGENT_PORT\" \"$AGENT_UPLOAD_DIR\" \"$AGENT_KEY_PATH\" \"$AGENT_LOG_DIR\"'",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "-u",
                    "agent-admin",
                    "bash",
                    "-lc",
                    'printf "AGENT_HOME=%s\\nAGENT_PORT=%s\\nAGENT_UPLOAD_DIR=%s\\nAGENT_KEY_PATH=%s\\nAGENT_LOG_DIR=%s\\n" "$AGENT_HOME" "$AGENT_PORT" "$AGENT_UPLOAD_DIR" "$AGENT_KEY_PATH" "$AGENT_LOG_DIR"',
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo -u agent-admin bash -lc 'ls -l \"$AGENT_HOME/agent-app\" \"$AGENT_UPLOAD_DIR\" \"$(dirname \"$AGENT_KEY_PATH\")\" \"$AGENT_LOG_DIR\"'",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "-u",
                    "agent-admin",
                    "bash",
                    "-lc",
                    'ls -l "$AGENT_HOME/agent-app" "$AGENT_UPLOAD_DIR" "$(dirname "$AGENT_KEY_PATH")" "$AGENT_LOG_DIR"',
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo -u agent-admin bash -lc 'test -x \"$AGENT_HOME/agent-app\" && echo \"provided app executable: OK\"'",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "-u",
                    "agent-admin",
                    "bash",
                    "-lc",
                    'test -x "$AGENT_HOME/agent-app" && echo "provided app executable: OK"',
                ],
            ),
        ],
    ),
    (
        "10_key_file_check",
        [
            (
                "orb -m ubuntu-b11 sudo -u agent-admin bash -lc 'printf \"AGENT_KEY_PATH=%s\\n\" \"$AGENT_KEY_PATH\"'",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "-u",
                    "agent-admin",
                    "bash",
                    "-lc",
                    'printf "AGENT_KEY_PATH=%s\\n" "$AGENT_KEY_PATH"',
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo ls -l /home/agent-admin/agent-app/api_keys/t_secret.key",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "ls",
                    "-l",
                    "/home/agent-admin/agent-app/api_keys/t_secret.key",
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo wc -l /home/agent-admin/agent-app/api_keys/t_secret.key",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "wc",
                    "-l",
                    "/home/agent-admin/agent-app/api_keys/t_secret.key",
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo cat /home/agent-admin/agent-app/api_keys/t_secret.key",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "cat",
                    "/home/agent-admin/agent-app/api_keys/t_secret.key",
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo -u agent-admin bash -lc 'test \"$(cat \"$AGENT_KEY_PATH\")\" = \"agent_api_key_test\" && echo \"key content: OK\"'",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "-u",
                    "agent-admin",
                    "bash",
                    "-lc",
                    'test "$(cat "$AGENT_KEY_PATH")" = "agent_api_key_test" && echo "key content: OK"',
                ],
            ),
        ],
    ),
    (
        "11_agent_run_success_check",
        [
            (
                "orb -m ubuntu-b11 sudo -u agent-admin bash -lc 'sed -n \"1,14p\" \"$AGENT_LOG_DIR/agent-app-boot.log\"'",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "sudo",
                    "-u",
                    "agent-admin",
                    "bash",
                    "-lc",
                    'sed -n "1,14p" "$AGENT_LOG_DIR/agent-app-boot.log"',
                ],
            ),
            (
                "orb -m ubuntu-b11 pgrep -a -u agent-admin -f agent-app",
                ["orb", "-m", "ubuntu-b11", "pgrep", "-a", "-u", "agent-admin", "-f", "agent-app"],
            ),
            (
                "orb -m ubuntu-b11 bash -lc \"ps -o user:20,pid,ppid,comm,args -u agent-admin | grep '[a]gent-app'\"",
                [
                    "orb",
                    "-m",
                    "ubuntu-b11",
                    "bash",
                    "-lc",
                    "ps -o user:20,pid,ppid,comm,args -u agent-admin | grep '[a]gent-app'",
                ],
            ),
            (
                "orb -m ubuntu-b11 sudo ss -tulnp | grep ':15034'",
                ["orb", "-m", "ubuntu-b11", "bash", "-lc", "sudo ss -tulnp | grep ':15034'"],
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
