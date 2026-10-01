// Presentations-skill finalizer wrapper (validation + chart workbooks) so every build does not rewrite it.
// usage (run beside a node_modules link to the Codex runtime, with its node):
//   node finalize.mjs --draft /abs/draft.pptx --final /abs/FINAL.pptx --slides 9 --workspace /abs/round-dir \
//        [--tables 4,7] [--charts 3,5] [--family Pretendard] [--keep-workbooks] [--pair-ea "Apple SD Gothic Neo"] [--overwrite]
// The draft must live inside --workspace. Charts: materializeLiteralChartWorkbooks is on by default; without an embedded workbook Apple's renderer (QuickLook/Keynote preview) draws no chart.
process.env.RUNTIME_NODE_MODULES ??= '/Users/mseok/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
import fs from 'node:fs/promises';
import {existsSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL, fileURLToPath} from 'node:url';
const a = Object.fromEntries(process.argv.slice(2).reduce((acc, v, i, arr) => v.startsWith('--') ? [...acc, [v.slice(2), arr[i + 1] && !arr[i + 1].startsWith('--') ? arr[i + 1] : true]] : acc, []));
const list = s => (s && s !== true ? String(s).split(',').map(Number) : []);
const SKILL_DIR = '/Users/mseok/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.11814/skills/presentations';
const PY = '/Users/mseok/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3';
const {finalizePresentation} = await import(pathToFileURL(path.join(SKILL_DIR, 'container_tools/artifact_tool_utils.mjs')).href);
const tables = list(a.tables), charts = list(a.charts);
// Optional Latin+Hangul pairing (only when the user approved it): latin = --family (Helvetica Neue), east-asian slot = --pair-ea. The paired copy is what gets finalized.
let draftPath = a.draft;
const families = [a.family && a.family !== true ? a.family : 'Pretendard'];
if (a['pair-ea'] && a['pair-ea'] !== true) {
  const {execFileSync} = await import('node:child_process');
  draftPath = a.draft.replace(/\.pptx$/, '.paired.pptx');
  // pair_fonts.py: $RESEARCH_TALK_SKILL, else the skill folder this file was copied from (frozen snapshots), else the installed skill.
  const here = path.dirname(fileURLToPath(import.meta.url));
  const skillRoot = [process.env.RESEARCH_TALK_SKILL, path.resolve(here, '..'), '/Users/mseok/.codex/skills/research-talk'].filter(Boolean)
    .find(r => existsSync(path.join(r, 'scripts/pair_fonts.py')));
  if (!skillRoot) throw new Error('pair_fonts.py not found: set RESEARCH_TALK_SKILL to the skill folder');
  execFileSync(PY, [path.join(skillRoot, 'scripts/pair_fonts.py'), a.draft, draftPath, families[0], a['pair-ea']], {stdio: 'inherit'});
  families.push(a['pair-ea']);
}
// Make sure the deck font is installed (installs the bundled copy automatically when missing).
if (families[0] === 'Pretendard') {
  const {spawnSync} = await import('node:child_process');
  const hereF = path.dirname(fileURLToPath(import.meta.url));
  const rootF = [process.env.RESEARCH_TALK_SKILL, path.resolve(hereF, '..'), '/Users/mseok/.codex/skills/research-talk'].filter(Boolean).find(r => existsSync(path.join(r, 'scripts/ensure_font.py')));
  if (rootF) { const r = spawnSync(PY, [path.join(rootF, 'scripts/ensure_font.py')], {encoding: 'utf8'}); console.log((r.stdout || '').trim() || (r.stderr || '').trim()); }
}
// Theme fonts (heading/body) → the deck family, so text typed later in PowerPoint/Keynote matches (Artifact Tool's font scheme is read-only; the theme XML is rewritten).
{
  const {execFileSync} = await import('node:child_process');
  const here2 = path.dirname(fileURLToPath(import.meta.url));
  const root2 = [process.env.RESEARCH_TALK_SKILL, path.resolve(here2, '..'), '/Users/mseok/.codex/skills/research-talk'].filter(Boolean).find(r => existsSync(path.join(r, 'scripts/set_theme_fonts.py')));
  if (root2) {
    const themed = draftPath.replace(/\.pptx$/, '.themed.pptx');
    execFileSync(PY, [path.join(root2, 'scripts/set_theme_fonts.py'), draftPath, themed, families[0], families[1] ?? families[0]], {stdio: 'inherit'});
    draftPath = themed;
    // Charts: PowerPoint adds the series name as a title unless <c:autoTitleDeleted val="1"/> is present.
    if (existsSync(path.join(root2, 'scripts/chart_no_autotitle.py'))) {
      const notitle = draftPath.replace(/\.themed\.pptx$/, '.notitle.pptx');
      execFileSync(PY, [path.join(root2, 'scripts/chart_no_autotitle.py'), draftPath, notitle], {stdio: 'inherit'});
      draftPath = notitle;
    }
  }
}
const staging = path.join(a.workspace, '.codex-finalizer');
await fs.mkdir(staging, {recursive: true});
// Re-runs: drop the stale receipt; --overwrite also replaces an existing final file.
await fs.rm(path.join(staging, path.basename(a.final) + '.validation.json'), {force: true});
if (a.overwrite) await fs.rm(a.final, {force: true});
await fs.mkdir(path.dirname(a.final), {recursive: true});
const result = await finalizePresentation({
  explicitTotalSlideCount: Number(a.slides),
  requiredNativeTableOwnerSlides: tables,
  requiredNativeChartOwnerSlides: charts,
  materializeLiteralChartWorkbooks: !a['keep-workbooks'],
  workspaceDir: a.workspace, candidatePath: draftPath, finalPath: a.final,
  pythonExecutable: PY,
  integrityValidatorPath: path.join(SKILL_DIR, 'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath: path.join(SKILL_DIR, 'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs: ['--expected-slide-size-emu', '24384000,13716000', '--validate-bullet-geometry', '--validate-heading-fit', ...tables.flatMap(n => ['--require-native-table-slide', String(n)])],
  fontPolicy: {basis: 'design', families},
  verifyArtifactToolImport: true,
  receiptPath: path.join(staging, path.basename(a.final) + '.validation.json'),
});
console.log(JSON.stringify(result, null, 1).slice(0, 4000));
