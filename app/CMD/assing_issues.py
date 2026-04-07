"""Asigna issues existentes a miembros del equipo según su Historia de Usuario."""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path

REPO = "Lunaa001/NotebookUM"
ASSIGNEES = {
    "US1": "Catalan-Maximo",
    "US2": "Lunaa001",
    "US3": "DannyOkk",
    "US4": "vaninafuentes",
}
TASKS_MD = Path("specs/001-api-gestion-documentos/tasks.md")


def gh(*args: str) -> str:
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ⚠ {r.stderr.strip()}", file=sys.stderr)
        return ""
    return r.stdout.strip()


def main() -> None:
    text = TASKS_MD.read_text(encoding="utf-8")
    task_re = re.compile(r"T\d+\s+\[#(?P<num>\d+)\].+?\[(?P<story>US\d+)\]")

    assignments: dict[str, list[int]] = {user: [] for user in ASSIGNEES.values()}
    for m in task_re.finditer(text):
        story = m.group("story")
        if story in ASSIGNEES:
            assignments[ASSIGNEES[story]].append(int(m.group("num")))

    # Issues de fases padre (sin [USx]) — buscar por título
    phase_issues = json.loads(
        gh("issue", "list", "--repo", REPO, "--state", "all",
           "--limit", "500", "--json", "number,title") or "[]"
    )
    phase_story_map = {
        "Historia de Usuario 1": "US1", "Historia de Usuario 2": "US2",
        "Historia de Usuario 3": "US3", "Historia de Usuario 4": "US4",
    }
    for issue in phase_issues:
        for phrase, story in phase_story_map.items():
            if phrase in issue["title"] and "[Fase" in issue["title"]:
                assignments[ASSIGNEES[story]].append(issue["number"])

    total = sum(len(nums) for nums in assignments.values())
    print(f"Asignando {total} issues a {len(assignments)} personas...\n")

    for user, numbers in assignments.items():
        if not numbers:
            continue
        nums_str = " ".join(str(n) for n in sorted(set(numbers)))
        print(f"→ {user}: {len(set(numbers))} issues ({nums_str[:60]}...)")
        for num in sorted(set(numbers)):
            gh("issue", "edit", str(num), "--repo", REPO, "--add-assignee", user)
        print(f"  ✓ {user} asignado")

    print(f"\n✓ Asignación completada")


if __name__ == "_main_":
    main()