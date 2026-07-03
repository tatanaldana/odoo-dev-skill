#!/usr/bin/env node
const fs = require("fs");
const os = require("os");
const path = require("path");

const repoRoot = path.resolve(__dirname, "..");

const destinations = {
  claude: path.join(os.homedir(), ".claude", "skills"),
  agents: path.join(os.homedir(), ".agents", "skills"),
};

function usage() {
  console.log(`Odoo Dev Skill installer

Usage:
  npx github:tatanaldana/odoo-dev-skill [install] [options]

Options:
  --target <all|claude|agents>  Install target. Default: all
  --dry-run                     Show what would be copied
  --help                        Show this help

Examples:
  npx github:tatanaldana/odoo-dev-skill
  npx github:tatanaldana/odoo-dev-skill --target claude
  npx github:tatanaldana/odoo-dev-skill --dry-run
`);
}

function parseArgs(argv) {
  const args = [...argv];
  if (args[0] === "install") args.shift();

  const options = { target: "all", dryRun: false, help: false };

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

  if (!["all", "claude", "agents"].includes(options.target)) {
    throw new Error(`Invalid target: ${options.target}. Valid values: all, claude, agents`);
  }

  return options;
}

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
  if (dryRun) {
    console.log(`[dry-run] mkdir -p ${dir}`);
    return;
  }
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

  if (dryRun) {
    console.log(`[dry-run] copy ${source} -> ${target}`);
    return;
  }

  fs.cpSync(source, target, { recursive: true, dereference: true });
}

function installTo(destName, destPath, dryRun) {
  // Install into ~/.claude/skills/odoo-dev-skill/ (not ~/.claude/skills/)
  const skillDest = path.join(destPath, "odoo-dev-skill");
  ensureDir(skillDest, dryRun);

  const backupDir = path.join(destPath, `.backup-odoo-dev-skill-${timestamp()}`);

  // Copy SKILL.md
  const skillMd = path.join(repoRoot, "SKILL.md");
  if (fs.existsSync(skillMd)) {
    copyItem(skillMd, path.join(skillDest, "SKILL.md"), backupDir, dryRun);
    console.log(`${dryRun ? "would install" : "installed"} SKILL.md -> ${destName}`);
  }

  // Copy agents/ directory
  const agentsSrc = path.join(repoRoot, "agents");
  if (fs.existsSync(agentsSrc)) {
    copyItem(agentsSrc, path.join(skillDest, "agents"), backupDir, dryRun);
    console.log(`${dryRun ? "would install" : "installed"} agents/ -> ${destName}`);
  }

  // Copy skills/ directory
  const skillsSrc = path.join(repoRoot, "skills");
  if (fs.existsSync(skillsSrc)) {
    copyItem(skillsSrc, path.join(skillDest, "skills"), backupDir, dryRun);
    console.log(`${dryRun ? "would install" : "installed"} skills/ -> ${destName}`);
  }

  // Copy hooks/ directory
  const hooksSrc = path.join(repoRoot, "hooks");
  if (fs.existsSync(hooksSrc)) {
    copyItem(hooksSrc, path.join(skillDest, "hooks"), backupDir, dryRun);
    console.log(`${dryRun ? "would install" : "installed"} hooks/ -> ${destName}`);
  }

  // Copy templates/ directory
  const templatesSrc = path.join(repoRoot, "templates");
  if (fs.existsSync(templatesSrc)) {
    copyItem(templatesSrc, path.join(skillDest, "templates"), backupDir, dryRun);
    console.log(`${dryRun ? "would install" : "installed"} templates/ -> ${destName}`);
  }

  // Clean empty backup dir
  if (!dryRun && fs.existsSync(backupDir)) {
    const contents = fs.readdirSync(backupDir);
    if (contents.length === 0) fs.rmdirSync(backupDir);
  }

  console.log(`\nInstalled odoo-dev-skill to: ${skillDest}`);
}

function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    usage();
    return;
  }

  const targets =
    options.target === "all"
      ? Object.entries(destinations)
      : [[options.target, destinations[options.target]]];

  for (const [name, destPath] of targets) {
    installTo(name, destPath, options.dryRun);
  }

  console.log("\nRestart or reload Claude Code so it picks up the updated skill.");
}

try {
  main();
} catch (error) {
  console.error(`error: ${error.message}`);
  process.exitCode = 1;
}