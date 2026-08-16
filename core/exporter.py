"""Progress export module for generating student report cards, certificates, and backups."""
import datetime
import os
from typing import Optional
from core.user_manager import UserProfile, LESSON_IDS
from core.gamification import ACHIEVEMENT_LIBRARY, get_achievement_by_id


def generate_student_report_markdown(user: UserProfile) -> str:
    """Generates a structured, beautiful Markdown student report card."""
    now_str = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")
    lvl = user.level_info

    md = []
    md.append(f"# 🎓 ChordMaster — Relatório de Progresso e Certificado de Estudo")
    md.append(f"**Aluno:** {user.avatar} {user.username}  |  **Data de Emissão:** {now_str}\n")
    md.append("---")

    # 1. Level & XP Summary
    md.append(f"## 🏆 Nível de Maestria Musical")
    md.append(f"- **Nível Atual:** Nível {lvl['level']} — {lvl['icon']} **{lvl['title']}**")
    md.append(f"- **Experiência Total (XP):** `{user.xp} XP`")
    if lvl['xp_needed'] > 0:
        md.append(f"- **Próximo Nível:** Faltam `{lvl['xp_needed']} XP` para o Nível {lvl['level'] + 1} ({lvl['progress_pct']:.0f}% concluído)")
    else:
        md.append(f"- **Estado:** 🌟 Nível Máximo de Maestria Atingido!")
    md.append("")

    # 2. Theory Chapters
    md.append(f"## 📖 Progresso nas Lições Teóricas ({len(user.completed_lessons)}/{len(LESSON_IDS)} Concluídas)")
    for lid, ltitle in LESSON_IDS:
        status = "✅ Concluído" if lid in user.completed_lessons else "⏳ Pendente"
        md.append(f"- {status} — **{ltitle}**")
    md.append("")

    # 3. Category Breakdown
    md.append(f"## 📊 Desempenho por Categoria de Treino")
    md.append(f"| Categoria | Tentativas | Acertos | Precisão | Maior Sequência |")
    md.append(f"| :--- | :---: | :---: | :---: | :---: |")

    from core.categories import CATEGORY_NAMES_PT
    
    for cat_key, st in user.categories.items():
        cat_name = CATEGORY_NAMES_PT.get(cat_key, cat_key.replace("_", " ").title())
        if st and st.total_attempts > 0:
            acc = (st.correct_count / float(st.total_attempts)) * 100.0
            md.append(f"| {cat_name} | {st.total_attempts} | {st.correct_count} | {acc:.1f}% | 🔥 {st.best_streak} |")
        else:
            md.append(f"| {cat_name} | 0 | 0 | 0.0% | 0 |")

    md.append(f"\n**Precisão Global:** `{user.accuracy_rate:.1f}%` ({user.total_correct} acertos em {user.total_attempts} exercícios)\n")

    # 4. Unlocked Achievements
    md.append(f"## 🏅 Medalhas e Conquistas ({len(user.unlocked_achievements)}/{len(ACHIEVEMENT_LIBRARY)})")
    if user.unlocked_achievements:
        for ach_id in user.unlocked_achievements:
            ach = get_achievement_by_id(ach_id)
            if ach:
                md.append(f"- {ach.icon} **{ach.title}** (+{ach.xp_reward} XP) — *{ach.description}*")
    else:
        md.append("*Nenhuma conquista desbloqueada ainda. Continua a praticar lições e músicas!*")
    md.append("")

    md.append("---")
    md.append("*Emitido automaticamente pela aplicação ChordMaster — Teoria & Prática Musical.*")

    return "\n".join(md)


def export_student_report_file(user: UserProfile, export_dir: Optional[str] = None) -> str:
    """Exports student report to a Markdown file in the target directory."""
    if export_dir is None:
        export_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    clean_name = "".join(c for c in user.username if c.isalnum() or c in ("-", "_")).lower()
    filename = f"relatorio_progresso_{clean_name}.md"
    filepath = os.path.join(export_dir, filename)

    content = generate_student_report_markdown(user)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath
