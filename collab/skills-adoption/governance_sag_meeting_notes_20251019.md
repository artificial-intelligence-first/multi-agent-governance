# GovernanceSAG Charter Confirmation — Meeting Notes

- **Date**: 2025-10-19
- **Participants**: GovernanceSAG (lead), MCPSAG (technical steward), Flow Runner maintainers, DocsSAG representative
- **Purpose**: Confirm Skills program charter, escalation paths, and steady-state review cadence prior to closing the ExecPlan.

## Agenda
1. Charter scope approval (ownership, decision rights, telemetry obligations)
2. Review of pilot outcomes (precision/recall, token削減, guardrailパフォーマンス)
3. Steady-state運用 (レビュー頻度、エスカレーション、メトリクス公開)
4. オープン課題とアクションアイテム整理

## Discussion Summary
- パイロット結果は受け入れ基準を満たし、DocsSAG/Flow Runner からのフィードバックも肯定的。
- Skills レジストリおよび allowlist の 30 日レビューと週次テレメトリ輸出を GovernanceSAG が主導し、MCPSAG が技術支援する体制を確定。
- `skills_exec` フラグはパイロット環境のみ有効化し、プロダクション適用には 2 回連続のレビューで問題なしを確認後とする。
- インシデント発生時は 1 営業日以内に GovernanceSAG へ報告し、Flow Runner テレメトリ (`skill_exec_*`) を添付する。
- DepsSAG は Skills 関連スクリプトで新規依存が追加された際、事前レビューを実施する。

## Decisions
1. Skills プログラムのチャーターを承認。Owner は GovernanceSAG、技術ステュワードは MCPSAG（`AGENTS.md` / `agents/SSOT.md` の記述と一致）。
2. Steady-state レビュー手順（30 日レジストリ監査・週次テレメトリ輸出・緊急エスカレーション）を Skills README と PLANS.md に反映済みの内容で正式運用する。
3. Flow Runner guardrails の allowlist 運用は deny-by-default 方針を継続し、追加スクリプトは GovernanceSAG + Flow Runner Maintainers のダブルサインオフが必要。

## Action Items
- GovernanceSAG: 2025-11-18 までに第 1 回 30 日レビューを実施し、結果を `collab/skills-adoption/notes.md` に追記。
- MCPSAG: `.mcp/cache/` の埋め込み管理 SOP を 2025-10-25 までにドラフト化し、Skills Decision Log にリンク。
- Flow Runner Maintainers: `skills_exec` 本番展開判断のための KPI トレンドを `telemetry/reports/skills_phase2_rolling.json` として整備（期限 2025-11-01）。
- DocsSAG: Draft Quality Skill の追加ヒント（共通フォーマット例）を 2025-10-24 までに `agents/sub-agents/docs-sag/skills/draft-quality/resources/` へ追加。

