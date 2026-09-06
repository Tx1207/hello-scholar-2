function beginMarker(tool) {
  return `<!-- HELLO-SCHOLAR:BEGIN ${tool} -->`;
}

function endMarker(tool) {
  return `<!-- HELLO-SCHOLAR:END ${tool} -->`;
}

function wrapBlock(tool, content) {
  return `${beginMarker(tool)}\n${content.trimEnd()}\n${endMarker(tool)}`;
}

function blockRegex(tool) {
  const begin = beginMarker(tool).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const end = endMarker(tool).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const lineBreak = "\\r?\\n";
  return new RegExp(`${begin}${lineBreak}[\\s\\S]*?${lineBreak}${end}`);
}

function hasInstructionBlock(existingText, tool) {
  return blockRegex(tool).test(existingText);
}

function upsertInstructionBlock(existingText, tool, blockContent) {
  const regex = blockRegex(tool);
  if (regex.test(existingText)) {
    return existingText.replace(regex, wrapBlock(tool, blockContent));
  }
  return `${wrapBlock(tool, blockContent)}\n\n${existingText}`;
}

function removeInstructionBlock(existingText, tool) {
  return existingText.replace(blockRegex(tool), "");
}

module.exports = {
  beginMarker,
  endMarker,
  hasInstructionBlock,
  removeInstructionBlock,
  upsertInstructionBlock,
  wrapBlock,
};
