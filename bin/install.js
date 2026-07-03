#!/usr/bin/env node
const fs = require("fs");
const os = require("os");
const path = require("path");

const repoRoot = path.resolve(__dirname, "..");

const destinations = {
  claude: path.join(os.homedir(), ".claude", "skills"),
  agents: path.join(os.homedir(), ".agents", "skills"),
};

// ---------------------------------------------------------------------------
// Usage
// ---------------------------------------------------------------------------

function usage() {
  console.log(`Odoo Dev Skill installer

Commands:
  (default)   Install the skill globally into ~/.claude/skills/ and ~/.agents/skills/
  init        Initialize hooks in the current Odoo project (.claude/settings.json)

Usage:
  npx github:tatanaldana/odoo-dev-skill [install] [options]
  npx github:tatanaldana/odoo-dev-skill init [--dry-run]

Install options:
  --target <all|claude|agents>  Install target. Default: all
  --dry-run                     Show what would be copied without doing it
  --help                        Show this help

Init options:
  --dry-run                     Show what would be written without doing it

Examples:
  npx github:tatanaldana/odoo-dev-skill
  npx github:tatanaldana/odoo-dev-skill --target claude
  npx github:tatanaldana/odoo-dev-skill --dry-run

  cd /my-odoo-project
  npx github:tatanaldana/odoo-dev-skill init
  npx github:tatanaldana/odoo-dev-skill init --dry-run
`);
}

// ---------------------------------------------------------------------------
// Argument parsing
// ---------------------------------------------------------------------------

function parseArgs(argv) {
  const args = [...argv];
  const command = args[0] === "init" ? (args.shift(), "init")
                : args[0] === "install" ? (args.shift(), "install")
                : "install";

  const options = { command, target: "all", dryRun: false, help: false };

  for (let i = 0; i < args.length; i += 1) {
    const arg = args[i];
    if (arg === "--help" || arg === "-h") {
      options.help = true;
    } else if (arg === "--dry-run") {
      options.dryRun = true;
    } else if (arg === "--target") {
      const value = args[i + 1];
      if (!value) throw new Error("--target requires a value");
      options.target = value;
      i += 1;
    } else if (arg.startsWith("--target=")) {
      options.target = arg.slice("--target=".length);
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }

  if (options.command === "install" &&
      !["all", "claude", "agents"].includes(options.target)) {
    throw new Error(`Invalid target: ${options.target}. Valid values: all, claude, agents`);
  }

  return options;
}

// ---------------------------------------------------------------------------
// Install helpers
// ---------------------------------------------------------------------------

function timestamp() {
  const date = new Date();
  const pad = (v) => String(v).padStart(2, "0");
  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
    pad(date.getHours()),
    pad(date.getMinutes()),
    pad(date.getSeconds()),
  ].join("");
}

function ensureDir(dir, dryRun) {
  if (dryRun) { console.log(`[dry-run] mkdir -p ${dir}`); return; }
  fs.mkdirSync(dir, { recursive: true });
}

function copyItem(source, target, backupDir, dryRun) {
  const existing = fs.lstatSync(target, { throwIfNoEntry: false });
  if (existing) {
    const backupTarget = path.join(backupDir, path.basename(target));
    if (dryRun) {
      console.log(`[dry-run] backup ${target} -> ${backupTarget}`);
    } else {
      fs.mkdirSync(backupDir, { recursive: true });
      fs.rmSync(backupTarget, { recursive: true, force: true });
      fs.renameSync(target, backupTarget);
    }
  }
  if (dryRun) { console.log(`[dry-run] copy ${source} -> ${target}`); return; }
  fs.cpSync(source, target, { recursive: true, dereference: true });
}

function installTo(destName, destPath, dryRun) {
  const skillDest = path.join(destPath, "odoo-dev-skill");
  ensureDir(skillDest, dryRun);
  const backupDir = path.join(destPath, `.backup-odoo-dev-skill-${timestamp()}`);

  const items = [
    ["SKILL.md",    path.join(repoRoot, "SKILL.md"),    path.join(skillDest, "SKILL.md")],
    ["agents/",     path.join(repoRoot, "agents"),       path.join(skillDest, "agents")],
    ["skills/",     path.join(repoRoot, "skills"),       path.join(skillDest, "skills")],
    ["hooks/",      path.join(repoRoot, "hooks"),        path.join(skillDest, "hooks")],
    ["templates/",  path.join(repoRoot, "templates"),    path.join(skillDest, "templates")],
  ];

  for (const [label, src, dest] of items) {
    if (fs.existsSync(src)) {
      copyItem(src, dest, backupDir, dryRun);
      console.log(`${dryRun ? "would install" : "installed"} ${label} -> ${destName}`);
    }
  }

  if (!dryRun && fs.existsSync(backupDir)) {
    if (fs.readdirSync(backupDir).length === 0) fs.rmdirSync(backupDir);
  }

  console.log(`\nInstalled odoo-dev-skill to: ${skillDest}`);
}

// ---------------------------------------------------------------------------
// Init — write/merge .claude/settings.json in the current project
// ---------------------------------------------------------------------------

function resolveSkillPath() {
  // The skill is always installed under ~/.claude/skills/odoo-dev-skill
  // os.homedir() returns the correct home on Linux, macOS, and Windows.
  return path.join(os.homedir(), ".claude", "skills", "odoo-dev-skill");
}

function buildHookEntry(scriptPath) {
  // Use forward slashes on all platforms for the command string —
  // python3 on Windows (via WSL or winget) handles them fine.
  const normalized = scriptPath.split(path.sep).join("/");
  return { type: "command", command: `python3 ${normalized}` };
}

function hooksAlreadyDeclared(settings, guardScript, editScript) {
  const hooks = settings.hooks || {};

  const stopHooks = (hooks.Stop || [])
    .flatMap((h) => h.hooks || [])
    .map((h) => h.command || "");

  const postHooks = (hooks.PostToolUse || [])
    .flatMap((h) => h.hooks || [])
    .map((h) => h.command || "");

  const hasStop = stopHooks.some((c) => c.includes("context_session_guard.py"));
  const hasPost = postHooks.some((c) => c.includes("odoo_edit_guard.py"));

  return hasStop && hasPost;
}

function mergeHooks(settings, guardScript, editScript) {
  if (!settings.hooks) settings.hooks = {};

  // Stop hook
  if (!settings.hooks.Stop) settings.hooks.Stop = [];
  const hasStop = settings.hooks.Stop
    .flatMap((h) => h.hooks || [])
    .some((h) => (h.command || "").includes("context_session_guard.py"));
  if (!hasStop) {
    settings.hooks.Stop.push({ hooks: [buildHookEntry(guardScript)] });
  }

  // PostToolUse hook
  if (!settings.hooks.PostToolUse) settings.hooks.PostToolUse = [];
  const hasPost = settings.hooks.PostToolUse
    .flatMap((h) => h.hooks || [])
    .some((h) => (h.command || "").includes("odoo_edit_guard.py"));
  if (!hasPost) {
    settings.hooks.PostToolUse.push({
      matcher: "Edit|Write",
      hooks: [buildHookEntry(editScript)],
    });
  }

  return settings;
}

function runInit(dryRun) {
  const projectRoot = process.cwd();
  const claudeDir   = path.join(projectRoot, ".claude");
  const settingsFile = path.join(claudeDir, "settings.json");
  const skillPath   = resolveSkillPath();
  const guardScript = path.join(skillPath, "hooks", "context_session_guard.py");
  const editScript  = path.join(skillPath, "hooks", "odoo_edit_guard.py");

  console.log(`\nodoo-dev-skill init`);
  console.log(`  project root : ${projectRoot}`);
  console.log(`  skill path   : ${skillPath}`);
  console.log(`  settings     : ${settingsFile}`);

  // Warn if hooks scripts are not installed yet
  if (!fs.existsSync(guardScript) || !fs.existsSync(editScript)) {
    console.warn(
      "\nWarning: hook scripts not found at the expected skill path.\n" +
      "Run the global install first:\n" +
      "  npx github:tatanaldana/odoo-dev-skill\n"
    );
  }

  let settings = {};

  if (fs.existsSync(settingsFile)) {
    try {
      settings = JSON.parse(fs.readFileSync(settingsFile, "utf-8"));
    } catch {
      console.error(`error: could not parse ${settingsFile} — fix JSON syntax and retry.`);
      process.exitCode = 1;
      return;
    }

    if (hooksAlreadyDeclared(settings, guardScript, editScript)) {
      console.log("\nodoo-dev-skill hooks already declared in settings.json — nothing to do.");
      return;
    }

    console.log("\nMerging odoo-dev-skill hooks into existing settings.json...");
  } else {
    console.log("\nCreating .claude/settings.json with odoo-dev-skill hooks...");
  }

  settings = mergeHooks(settings, guardScript, editScript);
  const output = JSON.stringify(settings, null, 2);

  if (dryRun) {
    console.log(`\n[dry-run] would write ${settingsFile}:\n${output}`);
    return;
  }

  fs.mkdirSync(claudeDir, { recursive: true });
  fs.writeFileSync(settingsFile, output + "\n", "utf-8");

  console.log(`\nDone. Restart Claude Code so it picks up the new hooks.`);
  console.log(
    "\nNote: run this command once per Odoo project from its root directory.\n" +
    "The global skill install only needs to be done once.\n"
  );
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------

function main() {
  const options = parseArgs(process.argv.slice(2));

  if (options.help) { usage(); return; }

  if (options.command === "init") {
    runInit(options.dryRun);
    return;
  }

  // Default: install globally
  const targets =
    options.target === "all"
      ? Object.entries(destinations)
      : [[options.target, destinations[options.target]]];

  for (const [name, destPath] of targets) {
    installTo(name, destPath, options.dryRun);
  }

  console.log("\nRestart or reload Claude Code so it picks up the updated skill.");
  console.log(
    "\nTo enable hooks in an Odoo project, run from its root directory:\n" +
    "  npx github:tatanaldana/odoo-dev-skill init\n"
  );
}

try {
  main();
} catch (error) {
  console.error(`error: ${error.message}`);
  process.exitCode = 1;
}