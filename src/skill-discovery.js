const fs = require("node:fs");
const path = require("node:path");

function parseSkillName(skillMdText, skillMdPath) {
  const match = skillMdText.match(/^---\n([\s\S]*?)\n---/);
  if (!match) {
    throw new Error(`Missing frontmatter: ${skillMdPath}`);
  }
  const nameMatch = match[1].match(/^name:\s*["']?([^"'\n]+)["']?\s*$/m);
  if (!nameMatch) {
    throw new Error(`Missing skill name: ${skillMdPath}`);
  }
  return nameMatch[1].trim();
}

function discoverSkills(repoRoot) {
  const skillsRoot = path.join(repoRoot, "skills");
  const skills = [];
  const seen = new Map();

  for (const groupName of fs.readdirSync(skillsRoot).sort()) {
    const groupDir = path.join(skillsRoot, groupName);
    if (!fs.statSync(groupDir).isDirectory()) {
      continue;
    }
    for (const skillDirName of fs.readdirSync(groupDir).sort()) {
      const sourceDir = path.join(groupDir, skillDirName);
      if (!fs.statSync(sourceDir).isDirectory()) {
        continue;
      }
      const skillMdPath = path.join(sourceDir, "SKILL.md");
      if (!fs.existsSync(skillMdPath)) {
        continue;
      }
      const name = parseSkillName(fs.readFileSync(skillMdPath, "utf8"), skillMdPath);
      if (seen.has(name)) {
        throw new Error(`Duplicate skill name: ${name}`);
      }
      seen.set(name, skillMdPath);
      skills.push({ name, sourceDir, skillMdPath });
    }
  }

  return skills;
}

module.exports = {
  discoverSkills,
  parseSkillName,
};
